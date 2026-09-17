"""`/api/queue`, `/api/tracks/validate`, `/api/snapshots` -- lab-ui PRD S1 §7.

The queue routes never run anything: they write (or edit, or remove) a
declarative request file in `<spool>/pedidos/`, exactly the format
`neuromod-lab/scripts/nmd.py` already consumes (see that file's own
`PEDIDO` docstring and `valida()`) -- the daemon on the host is what turns
a pedido into a `universe_run.py` invocation. Writes are temp-file +
`os.replace` (atomic rename), per PRD S1 §7 / this task's own instruction,
so the daemon's `os.listdir(pedidos/)` scan never observes a half-written
file.

Every field the browser can set is validated here BEFORE the file is
written: `bin` must be a frozen snapshot, every track seed must pass
`pista_check`, and every arm flag must be a real `gpu_evolve` flag from the
allow-list `flags.py` derives from `cli_flags.rs`. nmd.py's own `valida()`
is a second, independent gate on the host side -- this router's job is to
make sure a well-formed, launchable request is the ONLY thing that can
reach that gate from the browser.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import time
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator

import lab_db
from ..auth import current_who, require_csrf
from ..deps import get_db, get_settings
from ..flags import FlagRegistryError, arm_flag_allow_list
from ..settings import Settings

router = APIRouter(dependencies=[Depends(current_who)])

# nmd.py's PEDIDO id / arg-flag regexes (scripts/nmd.py: `re.fullmatch(r'[\w-]{1,40}', pid)`,
# `FLAG = re.compile(r'^[A-Za-z][A-Za-z0-9-]{0,24}$')`) -- mirrored here so a request this
# router accepts is guaranteed to also pass the daemon's own whitelist gate.
_ID_RE = re.compile(r"^[\w-]{1,40}$")
_FLAG_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9-]{0,24}$")

TRACE_PROFILES = ("summary", "champion", "event", "full")


# ── request schema ───────────────────────────────────────────────────────────────────

class ArmFlag(BaseModel):
    """One `gpu_evolve` CLI flag. `flag` is stored WITHOUT leading dashes (the
    browser may send either `--no-fuel` or `no-fuel`); `value=None` means a
    switch (presence = on); any other value means a VALUE flag."""

    flag: str
    value: str | int | float | bool | None = None

    @field_validator("flag")
    @classmethod
    def _strip_dashes_and_check_shape(cls, v: str) -> str:
        v = v.lstrip("-")
        if not _FLAG_NAME_RE.match(v):
            raise ValueError(f"not a valid flag name: {v!r}")
        return v


class ExperimentRequest(BaseModel):
    """The validated experiment schema PRD S1 names: never a shell command, always
    typed fields the API checks before anything touches the spool."""

    id: str = Field(min_length=1, max_length=40)
    out: str | None = None
    bin: str
    gens: int = Field(ge=1, le=500)
    ticks: int = Field(ge=1, le=200_000)
    beings: int = Field(ge=1, le=128)
    width: float = Field(default=28.0, ge=10.0, le=60.0)
    seed: int = Field(ge=0, le=2**31 - 1)
    tracks: list[int] = Field(min_length=1, max_length=12)
    same_start: bool = False
    wall_cost: float | None = Field(default=None, ge=0.0, le=1000.0)
    impact_cost: float | None = Field(default=None, ge=0.0, le=1000.0)
    cost_gate_progress: float | None = Field(default=None, ge=0.0, le=100_000.0)
    trace_profile: Literal["summary", "champion", "event", "full"] = "summary"
    trace_cadence: int | None = Field(default=None, ge=1, le=10_000)
    vision_being: int = Field(default=0, ge=0, le=127)
    arm_flags: list[ArmFlag] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def _id_matches_daemon_whitelist(cls, v: str) -> str:
        if not _ID_RE.match(v):
            raise ValueError("id must match nmd.py's own pattern: [\\w-]{1,40}")
        return v

    @field_validator("tracks")
    @classmethod
    def _tracks_bounded(cls, v: list[int]) -> list[int]:
        for seed in v:
            if not (0 <= seed <= 2**31 - 1):
                raise ValueError(f"track seed out of range: {seed}")
        return v


# ── validation helpers (bin, tracks, arm flags) ──────────────────────────────────────

def validate_bin(settings: Settings, bin_path: str) -> Path:
    """`bin` must be a file directly under `settings.snapshots_root` (PRD S1: "bin
    (frozen snapshots only)") -- never a subdirectory (that's where `b1-champions/`
    genome WEIGHT files live, not executables) and never a path elsewhere on disk.
    """
    snapshots_root = Path(settings.snapshots_root).resolve()
    resolved = Path(bin_path).resolve()
    if resolved.parent != snapshots_root:
        raise ValueError(
            f"bin must be a file directly under {snapshots_root} (frozen snapshots only), "
            f"got {resolved}"
        )
    if not resolved.is_file():
        raise ValueError(f"bin does not exist: {resolved}")
    if not os.access(resolved, os.X_OK):
        raise ValueError(f"bin is not executable: {resolved}")
    return resolved


# Cache: (universe_root, seed, width, ate) -> {"valid": bool, "issues": [...]}. Process-
# lifetime, per PRD S1: "tracks must pass ... (validated by pista_check, cached)".
_track_cache: dict[tuple[str, int, float, float], dict] = {}

# Substrings `pista_check`'s current (English) output uses to mark a defect at one
# examined point. "AVISO" is kept as a harmless extra match on stdout in case some
# build ever prints it there too -- see DEVIATIONS.md #1 for where it ACTUALLY
# comes from (stderr, via `world.rs::procedural_waypoints`'s fallback, not
# `pista_check.rs` itself) and why it needs its own stderr check below.
_DEFECT_MARKERS = ("AXIS OFF THE TRACK", "BOTTLENECK", "NULL VARIANCE", "AVISO")

_LAP_RE = re.compile(r"lap\s+(\d+(?:\.\d+)?)\s*m")


def _parse_pista_check(output: str) -> tuple[bool, list[str]]:
    issues = [line.strip() for line in output.splitlines()
              if any(marker in line for marker in _DEFECT_MARKERS)]
    valid = ("No defects:" in output) and not issues
    return valid, issues


def _pista_check_binary(settings: Settings) -> Path:
    binary = Path(settings.universe_root) / "target" / "release" / "pista_check"
    if not binary.is_file():
        raise FileNotFoundError(f"pista_check binary not found at {binary} (cargo build --release)")
    return binary


def _lap_distance(binary: Path, seed: int, width: float) -> float:
    """Cheap probe (`--ate 1`, walks almost nothing) that still prints the FULL lap
    length in `pista_check`'s header line ("... lap N m ..."). Used so track
    validation always covers the whole lap, not just the first 600 m the binary's
    own `--ate` default stops at -- the cold tester's finding: seed 8215's only
    defects sit at 1152 m, past that default window, and `gpu_evolve` itself
    refuses a track like that at launch no matter where the defect sits.
    """
    try:
        result = subprocess.run(
            [str(binary), "--seed", str(seed), "--width", str(width), "--ate", "1"],
            capture_output=True, text=True, timeout=20,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(f"pista_check --seed {seed} (lap probe) timed out after 20s") from exc
    m = _LAP_RE.search(result.stdout)
    if not m:
        raise ValueError(f"pista_check --seed {seed}: could not read lap distance from --ate 1 probe output")
    return float(m.group(1))


def validate_track(settings: Settings, seed: int, width: float = 28.0, ate: float | None = None) -> dict:
    """Runs `pista_check --seed <seed> --width <width> --ate <ate>` (CPU-only, no
    GPU, no `gpu_evolve`) and classifies the track as drivable or not. `ate=None`
    (the default, used by `validate_experiment`) resolves to the FULL lap via
    `_lap_distance()` first -- an explicit `ate` is still honoured as-is for
    callers that want a cheap partial peek. Refuses (valid=False) on any of:
    `pista_check` exiting non-zero, a defect line in stdout (`_parse_pista_check`),
    or `[AVISO]` on stderr -- `world.rs::procedural_waypoints` prints that when its
    generator fell back to an UNVALIDATED reserve candidate after 96 failed
    attempts (seed 8300: exit 0, "No defects" in the examined stretch, AVISO on
    stderr regardless) -- see DEVIATIONS.md #1. Cached by `(seed, width, resolved
    ate)` for the life of the process.
    """
    binary = _pista_check_binary(settings)
    resolved_ate = ate if ate is not None else _lap_distance(binary, seed, width)

    key = (settings.universe_root, seed, width, resolved_ate)
    if key in _track_cache:
        return _track_cache[key]

    try:
        result = subprocess.run(
            [str(binary), "--seed", str(seed), "--width", str(width), "--ate", str(resolved_ate)],
            capture_output=True, text=True, timeout=20,
        )
    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(f"pista_check --seed {seed} timed out after 20s") from exc

    valid, issues = _parse_pista_check(result.stdout)
    if "[AVISO]" in result.stderr:
        valid = False
        issues = issues + [f"pista_check stderr: {result.stderr.strip()[:300]}"]
    if result.returncode != 0:
        valid = False
        issues = issues + [f"pista_check exited {result.returncode}: {result.stderr.strip()[:300]}"]
    report = {"seed": seed, "width": width, "ate": resolved_ate, "valid": valid, "issues": issues}
    _track_cache[key] = report
    return report


def validate_arm_flags(settings: Settings, arm_flags: list[ArmFlag]) -> dict[str, object]:
    """Returns the `args` fragment for the pedido (flag-without-dashes -> True or
    value), or raises `ValueError` naming the first offending flag.
    """
    cli_flags_path = str(Path(settings.universe_root) / "src" / "bin" / "gpu_evolve" / "cli_flags.rs")
    try:
        allow_list = arm_flag_allow_list(cli_flags_path)
    except FlagRegistryError as exc:
        raise ValueError(str(exc)) from exc

    args: dict[str, object] = {}
    for af in arm_flags:
        spec = allow_list.get(af.flag)
        if spec is None:
            raise ValueError(f"unknown or reserved arm flag: --{af.flag}")
        if spec.takes_value:
            if af.value is None:
                raise ValueError(f"--{af.flag} requires a value")
            if isinstance(af.value, bool):
                raise ValueError(f"--{af.flag} requires a non-boolean value")
            args[af.flag] = af.value
        else:
            if af.value not in (None, True):
                # nmd.py's own valida() raises ValueError('bool em lista') for a
                # False/other value on a flag it treats as boolean -- a switch is
                # either present (True) or absent, never False. Caught here so a
                # request that would be silently refused by the daemon is instead
                # refused, with a reason, before it ever reaches the spool.
                raise ValueError(f"--{af.flag} is a switch: pass value=true or omit it, never false")
            args[af.flag] = True
    return args


def build_pedido_args(settings: Settings, req: ExperimentRequest) -> dict[str, object]:
    args: dict[str, object] = {
        "bin": str(validate_bin(settings, req.bin)),
        "gens": req.gens,
        "ticks": req.ticks,
        "beings": req.beings,
        "width": req.width,
        "seed": req.seed,
        "tracks": list(req.tracks),
    }
    if req.same_start:
        args["same-start"] = True
    if req.wall_cost is not None:
        args["wall-cost"] = req.wall_cost
    if req.impact_cost is not None:
        args["impact-cost"] = req.impact_cost
    if req.cost_gate_progress is not None:
        args["cost-gate-progress"] = req.cost_gate_progress
    if req.trace_profile != "summary":
        args["driving-diagnostics"] = True
        args["vision-being"] = req.vision_being
        if req.trace_cadence is not None:
            args["vision-every"] = req.trace_cadence
    args.update(validate_arm_flags(settings, req.arm_flags))
    return args


def validate_experiment(settings: Settings, req: ExperimentRequest) -> dict:
    """Runs every cross-cutting check (bin, tracks, arm flags) and returns the
    pedido's `args` dict on success. Raises `ValueError` with a message naming
    exactly what failed -- callers turn this into a 422.
    """
    track_reports = [validate_track(settings, seed, req.width) for seed in req.tracks]
    bad = [r for r in track_reports if not r["valid"]]
    if bad:
        raise ValueError(
            "unvalidated track(s): "
            + "; ".join(f"seed {r['seed']}: {r['issues'] or ['pista_check reported defects']}" for r in bad)
        )
    return build_pedido_args(settings, req)


# ── spool I/O (atomic writes; PRD S1 §7) ─────────────────────────────────────────────

FILENAME_PREFIX = "lab-ui"  # <prefix>_<id>.json, written via <prefix>_<id>.json.tmp + os.replace


def _pedidos_dir(settings: Settings) -> Path:
    d = Path(settings.spool) / "pedidos"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _find_pedido_file(pedidos_dir: Path, request_id: str) -> Path | None:
    """Finds the file for `request_id` by its JSON "id" field, not by filename --
    mirrors `lab_db.mirror_queue`'s own approach (a pedido's filename may carry an
    arbitrary ordering prefix, e.g. the real spool's `3_b5_ctrl_s113.json`)."""
    if not pedidos_dir.is_dir():
        return None
    for name in sorted(os.listdir(pedidos_dir)):
        if not name.endswith(".json"):
            continue
        path = pedidos_dir / name
        try:
            with open(path, encoding="utf-8") as f:
                payload = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(payload, dict) and str(payload.get("id")) == request_id:
            return path
    return None


def _is_running(settings: Settings, request_id: str) -> bool:
    estado_path = Path(settings.spool) / "estado" / f"{request_id}.json"
    if not estado_path.is_file():
        return False
    try:
        with open(estado_path, encoding="utf-8") as f:
            estado = json.load(f)
    except (OSError, ValueError):
        return False
    return isinstance(estado, dict) and estado.get("fase") == "rodando"


def _write_pedido_atomic(pedidos_dir: Path, filename: str, pedido: dict) -> Path:
    final_path = pedidos_dir / filename
    tmp_path = pedidos_dir / (filename + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(pedido, f, ensure_ascii=False, indent=1)
    os.replace(tmp_path, final_path)  # atomic on the same filesystem
    return final_path


def _to_pedido(req: ExperimentRequest, args: dict[str, object]) -> dict:
    return {
        "id": req.id,
        "script": "universe_run",
        "out": req.out or req.id,
        "env": {},
        "args": args,
    }


# ── routes ────────────────────────────────────────────────────────────────────────────

@router.get("/api/queue")
def get_queue(db: sqlite3.Connection = Depends(get_db), settings: Settings = Depends(get_settings)) -> list[dict]:
    lab_db.mirror_queue(db, spool=settings.spool)
    return [dict(r) for r in db.execute("SELECT * FROM queue_mirror ORDER BY id")]


@router.post("/api/queue", status_code=201)
def post_queue(
    body: ExperimentRequest,
    db: sqlite3.Connection = Depends(get_db),
    settings: Settings = Depends(get_settings),
    who: str = Depends(current_who),
    _csrf: None = Depends(require_csrf),
) -> dict:
    pedidos_dir = _pedidos_dir(settings)
    if _find_pedido_file(pedidos_dir, body.id) is not None:
        raise HTTPException(status_code=409, detail={"error": f"a request with id {body.id!r} already exists"})
    try:
        args = validate_experiment(settings, body)
    except (ValueError, FileNotFoundError, TimeoutError) as exc:
        raise HTTPException(status_code=422, detail={"error": str(exc)}) from exc

    pedido = _to_pedido(body, args)
    filename = f"{FILENAME_PREFIX}_{body.id}.json"
    path = _write_pedido_atomic(pedidos_dir, filename, pedido)
    lab_db.audit(db, who, "launch", body.model_dump())
    return {"id": body.id, "path": str(path), "pedido": pedido}


@router.put("/api/queue/{request_id}")
def put_queue(
    request_id: str,
    body: ExperimentRequest,
    db: sqlite3.Connection = Depends(get_db),
    settings: Settings = Depends(get_settings),
    who: str = Depends(current_who),
    _csrf: None = Depends(require_csrf),
) -> dict:
    pedidos_dir = _pedidos_dir(settings)
    existing = _find_pedido_file(pedidos_dir, request_id)
    if existing is None:
        raise HTTPException(status_code=404, detail={"error": f"no pending request with id {request_id!r}"})
    if _is_running(settings, request_id):
        raise HTTPException(status_code=409, detail={"error": f"request {request_id!r} is running, cannot edit"})

    try:
        args = validate_experiment(settings, body)
    except (ValueError, FileNotFoundError, TimeoutError) as exc:
        raise HTTPException(status_code=422, detail={"error": str(exc)}) from exc

    pedido = _to_pedido(body, args)
    pedido["id"] = request_id  # the path id is authoritative, not whatever the body carries
    tmp_path = existing.with_name(existing.name + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(pedido, f, ensure_ascii=False, indent=1)
    os.replace(tmp_path, existing)
    lab_db.audit(db, who, "edit", body.model_dump())
    return {"id": request_id, "path": str(existing), "pedido": pedido}


@router.delete("/api/queue/{request_id}")
def delete_queue(
    request_id: str,
    db: sqlite3.Connection = Depends(get_db),
    settings: Settings = Depends(get_settings),
    who: str = Depends(current_who),
    _csrf: None = Depends(require_csrf),
) -> dict:
    pedidos_dir = _pedidos_dir(settings)
    existing = _find_pedido_file(pedidos_dir, request_id)
    if existing is None:
        raise HTTPException(status_code=404, detail={"error": f"no pending request with id {request_id!r}"})
    if _is_running(settings, request_id):
        raise HTTPException(status_code=409, detail={"error": f"request {request_id!r} is running, cannot cancel"})
    os.remove(existing)
    lab_db.audit(db, who, "cancel", {"id": request_id})
    return {"removed": True, "id": request_id}


@router.get("/api/tracks/validate")
def get_tracks_validate(
    seed: int, width: float = 28.0, ate: float | None = None,
    settings: Settings = Depends(get_settings),
) -> dict:
    try:
        return validate_track(settings, seed, width, ate)
    except (FileNotFoundError, TimeoutError) as exc:
        raise HTTPException(status_code=422, detail={"error": str(exc)}) from exc


@router.get("/api/snapshots")
def get_snapshots(settings: Settings = Depends(get_settings)) -> dict:
    root = Path(settings.snapshots_root)
    binaries: list[dict] = []
    if root.is_dir():
        for entry in sorted(root.iterdir()):
            if entry.is_file():
                st = entry.stat()
                binaries.append({
                    "name": entry.name, "path": str(entry), "bytes": st.st_size,
                    "mtime": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(st.st_mtime)),
                    "executable": os.access(entry, os.X_OK),
                })
    champions: list[dict] = []
    # `champions/` is where every battery since B3 freezes its final champions
    # (enqueue_champion_eval.py); `b1-champions/` predates it. Newest first, so a
    # battery that just finished is at the top of the panel's list (17/09).
    for champ_dir in (root / "champions", root / "b1-champions"):
        if champ_dir.is_dir():
            for entry in champ_dir.iterdir():
                if entry.is_file():
                    st = entry.stat()
                    champions.append({
                        "name": entry.name, "path": str(entry), "bytes": st.st_size,
                        "mtime": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(st.st_mtime)),
                    })
    champions.sort(key=lambda c: c["mtime"], reverse=True)
    return {"binaries": binaries, "champions": champions}
