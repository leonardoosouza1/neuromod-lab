"""Tests for the S6 live relay (`src/lab_api/routes/live.py`) -- `GET /api/live/runs`
and `WS /ws/live`.

No GPU, no real `gpu_evolve`: a tiny stdlib HTTP server (`fake_panel` fixture) stands
in for `gpu_evolve --panel`'s own real server, serving canned JSON captured from
reading `Universe/src/bin/gpu_evolve/painel.rs`'s route handlers (`/api/status` ->
`PainelState`, `/api/beings` -> `Vec<BeingSnapshot>`). Every test uses a throwaway
spool under `tmp_path`, same convention as `tests/test_lab_api.py`.
"""
from __future__ import annotations

import json
import os
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

import lab_db
from lab_api.app import create_app
from lab_api.routes.live import MAX_PANEL_PORT, MIN_PANEL_PORT
from lab_api.settings import Settings
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

# ── fixtures ──────────────────────────────────────────────────────────────────────────


def _free_port_in_range(lo: int = MIN_PANEL_PORT, hi: int = MAX_PANEL_PORT) -> int:
    for p in range(lo, hi + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    raise RuntimeError(f"no free port in [{lo}, {hi}] for a test fixture")


# Captured from Universe/src/bin/gpu_evolve/painel.rs's own struct definitions
# (PainelState, BeingSnapshot), trimmed to real-shaped values.
FAKE_STATUS = {
    "geracao": 3, "mediana_m": 210.5, "elite_m": 340.2, "mortos_pct": 12.5,
    "obediencia_pct": 0.0, "setores": [1.0, 0.9, 0.5, 0.1],
    "slope": 4.2, "tick": 8192, "vivos": 7, "vel_mediana": 6.1,
    "life_mediana": 0.8, "fuel_mediana": 0.6, "activation_alarms": [],
    "dead_pct_l1": 2.0, "saturated_pct_l1": 1.0, "spectral_radius": 0.95,
    "snr_i8": 12.3, "waypoints": [[0.0, 0.0], [10.0, 2.0]],
}
FAKE_BEINGS = [
    {"id": 0, "x": 12.5, "z": 3.1, "vel": 6.0, "life": 0.9, "vivo": True},
    {"id": 1, "x": 8.0, "z": -1.2, "vel": 0.0, "life": 0.0, "vivo": False},
]


class _PanelHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args) -> None:  # silence stdlib access logging
        pass

    def do_GET(self) -> None:
        if self.path == "/api/status":
            body = json.dumps(FAKE_STATUS).encode()
        elif self.path == "/api/beings":
            body = json.dumps(FAKE_BEINGS).encode()
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


@pytest.fixture
def fake_panel():
    """A real HTTP server on 127.0.0.1, bound to a free port inside the panel range,
    serving the canned `painel.rs` shapes above. Yields the port."""
    port = _free_port_in_range()
    server = ThreadingHTTPServer(("127.0.0.1", port), _PanelHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.fixture
def down_port(fake_panel):
    """A free port in range with NOTHING listening -- `fake_panel` is requested first
    so its bind claims one port before this one scans, guaranteeing they differ."""
    return _free_port_in_range()


@pytest.fixture
def spool(tmp_path: Path) -> Path:
    root = tmp_path / "spool"
    for sub in ("pedidos", "estado", "feitos", "recusados"):
        (root / sub).mkdir(parents=True)
    return root


def _write_estado(spool: Path, run_id: str, **overrides) -> None:
    estado = {
        "id": run_id, "fase": "rodando", "inicio": "2026-09-16T00:00:00+00:00",
        "argv": [
            "/home/leonardo/projects/LLM/neuromod-lab/src/universe_run.py",
            "--bin", "/media/llm-data/snapshots/gpu_evolve-testbin",
            "--gens", "5", "--ticks", "1000", "--beings", "8",
        ],
        "out": f"/media/llm-data/universe-runs/neuromod-lab-taxi/{run_id}",
        "geracao": None, "melhor_por_semente": None, "bracos_prontos": [],
        "segundos": 10, "pid": os.getpid(),
    }
    estado.update(overrides)
    (spool / "estado" / f"{run_id}.json").write_text(json.dumps(estado))


@pytest.fixture
def settings(tmp_path: Path, spool: Path) -> Settings:
    return Settings(db=str(tmp_path / "lab.db"), spool=str(spool))


@pytest.fixture
def lan_settings(settings: Settings) -> Settings:
    return settings.model_copy(update={"lan": True, "password": "s3cret-test-pw"})


@pytest.fixture
def client(settings: Settings) -> TestClient:
    return TestClient(create_app(settings))


@pytest.fixture
def lan_client(lan_settings: Settings) -> TestClient:
    return TestClient(create_app(lan_settings))


# ── GET /api/live/runs ───────────────────────────────────────────────────────────────


class TestLiveRuns:
    def test_lists_a_rodando_run_with_panel_port_and_battery(self, client: TestClient, spool: Path):
        _write_estado(
            spool, "b7_range60_s31",
            argv=[
                "/home/leonardo/projects/LLM/neuromod-lab/src/universe_run.py",
                "--bin", "/media/llm-data/snapshots/gpu_evolve-testbin",
                "--gens", "5", "--panel", "--panel-port", "3290",
            ],
        )
        r = client.get("/api/live/runs")
        assert r.status_code == 200
        assert r.json() == [{"run": "b7_range60_s31", "port": 3290, "battery": "b7"}]

    def test_bare_panel_switch_defaults_to_port_3200(self, client: TestClient, spool: Path):
        _write_estado(
            spool, "z_smoke_s1",
            argv=["/tmp/universe_run.py", "--panel"],
        )
        r = client.get("/api/live/runs")
        # "z_smoke_s1" DOES match lab_db.RUN_NAME (battery=z, arm=smoke, seed=1) --
        # the regex only requires `<lowercase-alnum>_<anything>_s<digits>`, not a
        # real registered battery code. A genuinely non-matching id (no `_s<N>`
        # suffix) is covered by test_id_with_no_battery_shape_has_null_battery below.
        assert r.json() == [{"run": "z_smoke_s1", "port": 3200, "battery": "z"}]

    def test_id_with_no_battery_shape_has_null_battery(self, client: TestClient, spool: Path):
        _write_estado(
            spool, "adhoc-smoke-test",
            argv=["/tmp/universe_run.py", "--panel"],
        )
        r = client.get("/api/live/runs")
        assert r.json() == [{"run": "adhoc-smoke-test", "port": 3200, "battery": None}]

    def test_painel_porta_alias_recognised(self, client: TestClient, spool: Path):
        _write_estado(
            spool, "b7_range60_s77",
            argv=["/tmp/universe_run.py", "--painel", "--painel-porta", "3211"],
        )
        r = client.get("/api/live/runs")
        assert r.json() == [{"run": "b7_range60_s77", "port": 3211, "battery": "b7"}]

    def test_run_without_panel_flag_excluded(self, client: TestClient, spool: Path):
        _write_estado(spool, "b7_no_panel_s1")  # no --panel/--panel-port in default argv
        assert client.get("/api/live/runs").json() == []

    def test_finished_run_excluded_even_with_panel_flag(self, client: TestClient, spool: Path):
        _write_estado(
            spool, "b7_done_s1", fase="terminou",
            argv=["/tmp/universe_run.py", "--panel", "--panel-port", "3210"],
        )
        assert client.get("/api/live/runs").json() == []

    def test_dead_pid_excluded(self, client: TestClient, spool: Path):
        # A pid essentially guaranteed not to exist (max on Linux is well under this).
        _write_estado(
            spool, "b7_stale_s1", pid=2**30,
            argv=["/tmp/universe_run.py", "--panel", "--panel-port", "3220"],
        )
        assert client.get("/api/live/runs").json() == []

    def test_lan_requires_session(self, lan_client: TestClient):
        assert lan_client.get("/api/live/runs").status_code == 401


# ── WS /ws/live ──────────────────────────────────────────────────────────────────────


class TestWsLive:
    def test_snapshot_frame_shape_and_run_lookup(self, client: TestClient, spool: Path, fake_panel: int):
        _write_estado(
            spool, "b7_live_s1",
            argv=["/tmp/universe_run.py", "--panel", "--panel-port", str(fake_panel)],
        )
        with client.websocket_connect(f"/ws/live?port={fake_panel}&hz=4") as ws:
            frame = ws.receive_json()
        assert frame["type"] == "snapshot"
        assert frame["port"] == fake_panel
        assert frame["run"] == "b7_live_s1"
        assert isinstance(frame["t"], str) and frame["t"]
        assert frame["status"] == FAKE_STATUS
        assert frame["beings"] == FAKE_BEINGS

    def test_run_is_null_when_no_estado_entry_matches_the_port(self, client: TestClient, fake_panel: int):
        with client.websocket_connect(f"/ws/live?port={fake_panel}&hz=4") as ws:
            frame = ws.receive_json()
        assert frame["type"] == "snapshot"
        assert frame["run"] is None

    def test_never_polls_activation(self, client: TestClient, fake_panel: int):
        hits: list[str] = []
        real_do_get = _PanelHandler.do_GET

        def spy(self):
            hits.append(self.path)
            real_do_get(self)

        _PanelHandler.do_GET = spy
        try:
            with client.websocket_connect(f"/ws/live?port={fake_panel}&hz=4") as ws:
                ws.receive_json()
        finally:
            _PanelHandler.do_GET = real_do_get
        assert "/api/activation" not in hits
        assert set(hits) <= {"/api/status", "/api/beings"}

    def test_hz_clamped_to_max(self, client: TestClient, fake_panel: int):
        with client.websocket_connect(f"/ws/live?port={fake_panel}&hz=1000") as ws:
            ws.receive_json()
            t0 = time.monotonic()
            ws.receive_json()
            dt = time.monotonic() - t0
        # MAX_HZ=4 -> interval 0.25s; a raw hz=1000 would be near-0. Generous bounds
        # for CI/dev-machine scheduling jitter.
        assert 0.15 <= dt <= 1.0

    def test_hz_clamped_to_min(self, client: TestClient, fake_panel: int):
        with client.websocket_connect(f"/ws/live?port={fake_panel}&hz=0.01") as ws:
            ws.receive_json()
            t0 = time.monotonic()
            ws.receive_json()
            dt = time.monotonic() - t0
        # MIN_HZ=1 -> interval 1.0s; a raw hz=0.01 would be ~100s.
        assert dt >= 0.8

    def test_port_out_of_range_closes_with_policy_violation(self, client: TestClient):
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/ws/live?port=80&hz=2"):
                pass
        assert exc_info.value.code == 1008

    def test_port_above_range_closes_with_policy_violation(self, client: TestClient):
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect("/ws/live?port=4000&hz=2"):
                pass
        assert exc_info.value.code == 1008

    def test_down_port_sends_error_frame_and_keeps_retrying(self, client: TestClient, down_port: int):
        with client.websocket_connect(f"/ws/live?port={down_port}&hz=4") as ws:
            first = ws.receive_json()
            assert first["type"] == "error"
            assert first["port"] == down_port
            assert isinstance(first["error"], str) and first["error"]
            t0 = time.monotonic()
            second = ws.receive_json()
            dt = time.monotonic() - t0
        assert second["type"] == "error"
        # ERROR_RETRY_INTERVAL_S=1.0, independent of the (higher) requested hz.
        assert dt >= 0.8

    def test_lan_ws_without_session_closes_with_policy_violation(self, lan_client: TestClient, fake_panel: int):
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with lan_client.websocket_connect(f"/ws/live?port={fake_panel}&hz=2"):
                pass
        assert exc_info.value.code == 1008

    def test_lan_ws_with_session_cookie_connects(self, lan_client: TestClient, fake_panel: int):
        login = lan_client.post("/api/login", json={"password": "s3cret-test-pw", "name": "leo"})
        assert login.status_code == 200
        with lan_client.websocket_connect(f"/ws/live?port={fake_panel}&hz=4") as ws:
            frame = ws.receive_json()
        assert frame["type"] == "snapshot"
