"""`GET /api/live/runs` and `WS /ws/live` -- lab-ui S6: a live relay onto a running
`gpu_evolve --panel` process.

`gpu_evolve` itself already serves a tiny read-only HTTP panel when launched with
`--panel`/`--panel-port` (`Universe/src/bin/gpu_evolve/painel.rs`): `/api/status`
(`PainelState` -- per-generation + per-tick summary, updated ~every N ticks) and
`/api/beings` (`Vec<BeingSnapshot>` -- one row per being, every N ticks). This
router does two things over that:

1. `GET /api/live/runs` tells the browser WHICH ports currently have a panel to
   connect to, by reading the nmd spool's own heartbeat (`<spool>/estado/*.json`,
   written by `scripts/nmd.py::executa()`) rather than probing ports directly --
   a `fase != "rodando"` or dead-pid entry is exactly what nmd.py itself would
   consider gone, so this reuses that heartbeat instead of re-deriving liveness
   from a second signal (an HTTP probe) that could disagree with it.
2. `WS /ws/live?port=N&hz=H` is the actual relay: this process polls
   `http://127.0.0.1:<port>/api/status` and `/api/beings` at `H` Hz and forwards
   both as one JSON frame per tick. `/api/activation` is NEVER polled here --
   PRD/task: that endpoint is replay-only in the micro (S4) panels, not part of
   this live slice.

Security (this is a relay a browser controls the target `port` of, so it gets the
same attacker-mindset treatment as `/api/queue`'s `bin`/track validation):

* The HOST half of every outbound request is hardcoded to `127.0.0.1` -- there is
  no `host` query parameter anywhere in this module, so there is no way for a
  client to redirect this relay at a third machine (SSRF) no matter what it sends.
* The PORT half is restricted to `3200-3299` (`gpu_evolve`'s own panel default is
  3200; the range gives room for several concurrent `--panel-port` runs without
  opening this relay to arbitrary localhost services -- a database port, another
  API, etc). A request outside the range is refused before `accept()`, with
  WebSocket close code 1008 (Policy Violation).
* Under `--lan`, the websocket requires the same session cookie `/api/db/*` etc
  require (`auth.SESSION_COOKIE`, checked against `auth.SessionStore` directly --
  `current_who`'s own `Cookie(...)` dependency wants a `Request`, which a
  websocket connection does not have; `websocket.cookies` is the equivalent
  Starlette gives `WebSocket`). No session -> close 1008 before `accept()`, same
  as the port check, so an unauthenticated LAN client cannot even learn whether a
  given port is in range.
* No payload logging: this module never calls `print`/`logging` with `status`,
  `beings`, or any frame content -- an error frame carries only the exception's
  class name, not `str(exc)` (which could echo a URL or, in principle, a
  server-supplied error body).
"""
from __future__ import annotations

import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import APIRouter, Depends, Query, WebSocket

import lab_db
from ..auth import SESSION_COOKIE, SessionStore, current_who
from ..deps import get_settings
from ..settings import Settings

# `--panel`/`--painel` (switch) and `--panel-port`/`--painel-porta` (value, ALSO
# enables the panel per cli_flags.rs's own help text) -- see
# Universe/src/bin/gpu_evolve/cli_flags.rs.
PANEL_SWITCH_FLAGS = ("--panel", "--painel")
PANEL_PORT_FLAGS = ("--panel-port", "--painel-porta")
DEFAULT_PANEL_PORT = 3200

MIN_PANEL_PORT = 3200
MAX_PANEL_PORT = 3299

DEFAULT_HZ = 2.0
MIN_HZ = 1.0
MAX_HZ = 4.0
POLL_TIMEOUT_S = 2.0
ERROR_RETRY_INTERVAL_S = 1.0  # PRD: "when the port is down ... keep retrying at 1 Hz"

router = APIRouter(dependencies=[Depends(current_who)])  # GET /api/live/runs
ws_router = APIRouter()  # WS /ws/live -- does its own auth, see ws_live()'s docstring


# ── spool reading (no HTTP probe -- nmd's own heartbeat is the source of truth) ────────

def _pid_alive(pid: object) -> bool:
    """`os.kill(pid, 0)` -- sends no signal, just checks the pid exists. A pid owned by
    another user answers `PermissionError` (it exists, we just cannot signal it) --
    that still counts as alive."""
    if not isinstance(pid, int) or pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _extract_panel_port(argv: list[str]) -> int | None:
    """Reads an `estado/*.json` `argv` list (nmd.py's `argv[1:]`, i.e. script path
    then flags, e.g. `[".../universe_run.py", "--panel", "--panel-port", "3290", ...]`)
    and returns the panel port, or `None` if neither `--panel`/`--painel` nor
    `--panel-port`/`--painel-porta` is present. A bare `--panel` (no explicit port)
    returns `DEFAULT_PANEL_PORT` (3200), matching `gpu_evolve`'s own default.
    """
    panel_on = False
    port: int | None = None
    n = len(argv)
    i = 0
    while i < n:
        tok = argv[i]
        if tok in PANEL_SWITCH_FLAGS:
            panel_on = True
        elif tok in PANEL_PORT_FLAGS:
            panel_on = True
            if i + 1 < n:
                try:
                    port = int(argv[i + 1])
                except ValueError:
                    port = None
        i += 1
    if not panel_on:
        return None
    return port if port is not None else DEFAULT_PANEL_PORT


def iter_live_runs(settings: Settings) -> list[dict[str, Any]]:
    """Every `<spool>/estado/*.json` entry that is `fase == "rodando"`, has a live
    `pid`, and whose `argv` carries a panel flag -- `[{"run", "port", "battery"}]`.
    `battery` reuses `lab_db.RUN_NAME` (the same regex `lab_db.ingest_run` derives a
    run's battery from), so this never grows a second, possibly-diverging parser for
    the `<battery>_<arm>_s<seed>[...]` naming convention.
    """
    estado_dir = Path(settings.spool) / "estado"
    if not estado_dir.is_dir():
        return []
    out: list[dict[str, Any]] = []
    for name in sorted(os.listdir(estado_dir)):
        if not name.endswith(".json"):
            continue
        try:
            with open(estado_dir / name, encoding="utf-8") as f:
                estado = json.load(f)
        except (OSError, ValueError):
            continue
        if not isinstance(estado, dict) or estado.get("fase") != "rodando":
            continue
        if not _pid_alive(estado.get("pid")):
            continue
        argv = estado.get("argv")
        if not isinstance(argv, list):
            continue
        port = _extract_panel_port([str(tok) for tok in argv])
        if port is None:
            continue
        run_id = str(estado.get("id") or name[:-5])
        m = lab_db.RUN_NAME.match(run_id)
        battery = m.group("battery") if m else None
        out.append({"run": run_id, "port": port, "battery": battery})
    return out


def find_run_for_port(settings: Settings, port: int) -> str | None:
    for r in iter_live_runs(settings):
        if r["port"] == port:
            return r["run"]
    return None


@router.get("/api/live/runs")
def get_live_runs(settings: Settings = Depends(get_settings)) -> list[dict[str, Any]]:
    return iter_live_runs(settings)


# ── the relay itself ────────────────────────────────────────────────────────────────

async def _fetch_json(client: httpx.AsyncClient, port: int, path: str) -> Any:
    resp = await client.get(f"http://127.0.0.1:{port}{path}", timeout=POLL_TIMEOUT_S)
    resp.raise_for_status()
    return resp.json()


@ws_router.websocket("/ws/live")
async def ws_live(
    websocket: WebSocket,
    port: int = Query(..., ge=1, le=65535),
    hz: float = Query(DEFAULT_HZ),
) -> None:
    """Relays `/api/status` + `/api/beings` from the `gpu_evolve --panel` process on
    `127.0.0.1:<port>` at `hz` Hz (clamped to `[MIN_HZ, MAX_HZ]`), as one
    `{"type": "snapshot", ...}` frame per poll. On a fetch failure (panel down, port
    refused, non-JSON body, non-2xx status) sends `{"type": "error", "port", "error"}`
    once and retries at `ERROR_RETRY_INTERVAL_S` (1 Hz) until the panel answers again --
    the connection itself is never dropped on a transient panel outage, only on the
    BROWSER disconnecting or an auth/port-range refusal at connect time.

    Auth and the port-range check both run BEFORE `websocket.accept()`, so a refused
    connection is a clean WebSocket close (code 1008, Policy Violation) during the
    handshake, not an accepted-then-immediately-closed connection.
    """
    settings: Settings = websocket.app.state.settings

    if settings.lan:
        store: SessionStore = websocket.app.state.sessions
        session_id = websocket.cookies.get(SESSION_COOKIE)
        if store.get(session_id) is None:
            await websocket.close(code=1008, reason="login required under --lan")
            return

    if not (MIN_PANEL_PORT <= port <= MAX_PANEL_PORT):
        await websocket.close(
            code=1008,
            reason=f"policy violation: port must be in [{MIN_PANEL_PORT}, {MAX_PANEL_PORT}]",
        )
        return

    await websocket.accept()
    clamped_hz = min(MAX_HZ, max(MIN_HZ, hz))
    interval = 1.0 / clamped_hz

    try:
        async with httpx.AsyncClient() as client:
            while True:
                run = find_run_for_port(settings, port)
                try:
                    status = await _fetch_json(client, port, "/api/status")
                    beings = await _fetch_json(client, port, "/api/beings")
                except (httpx.HTTPError, ValueError) as exc:
                    await websocket.send_json(
                        {"type": "error", "port": port, "error": type(exc).__name__}
                    )
                    await asyncio.sleep(ERROR_RETRY_INTERVAL_S)
                    continue
                await websocket.send_json({
                    "type": "snapshot",
                    "port": port,
                    "run": run,
                    "t": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "status": status,
                    "beings": beings,
                })
                await asyncio.sleep(interval)
    except asyncio.CancelledError:
        raise
    except Exception:
        # Browser disconnect (WebSocketDisconnect) or a transport-level error on an
        # already-torn-down connection -- either way, this coroutine's job is done.
        return
