"""Tests for the S1 FastAPI backend (`src/lab_api/`) -- lab-ui PRD S1.

Runs with pytest (present in the project venv, no install needed):

    /home/leonardo/projects/LLM/.venv-rocm/bin/python -m pytest tests/test_lab_api.py -v

Every test uses a throwaway database and a throwaway spool under `tmp_path`
(pytest's own per-test temp dir) -- NONE of them opens `/media/llm-data/lab.db`
or writes into the live nmd spool (`/media/llm-data/universe-runs/neuromod-lab-
taxi/_nmd/`), which a battery may be actively using. Track validation and
arm-flag-registry tests DO shell out to the real, already-built
`Universe/target/release/pista_check` and read the real
`Universe/src/bin/gpu_evolve/cli_flags.rs` -- both read-only, no GPU, per the
task's own instruction to validate against the real registry rather than a
hand-copied one. The trace-route tests read the real S0 fixture
(`lab-ui/fixtures/trace-v1/universe-b2-gen0/`), symlinked into a scratch
runs_root laid out per the PRD S5 path (`<run>/trace/gen<NNNN>/being<NN>/<profile>/`).
"""
from __future__ import annotations

import json
import os
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import lab_db  # noqa: E402
from lab_api.app import create_app  # noqa: E402
from lab_api.settings import Settings  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

def _llm_root() -> Path:
    """The workspace holding Universe/ and lab-ui/: one level above this repo on main
    (`LLM/neuromod-lab`), two levels above in a worktree (`LLM/.worktrees/<slice>`).
    A fixed `parents[3]` only worked in worktrees and broke the merged suite (16/09)."""
    if "LLM_ROOT" in os.environ:
        return Path(os.environ["LLM_ROOT"])
    repo_root = Path(__file__).resolve().parents[1]
    for candidate in (repo_root.parent, repo_root.parents[1]):
        if (candidate / "Universe").is_dir():
            return candidate
    return repo_root.parent


LLM_ROOT = _llm_root()
UNIVERSE_ROOT = str(LLM_ROOT / "Universe")
LAB_UI_REPO = Path(os.environ.get("LAB_UI_REPO", LLM_ROOT / "lab-ui"))
FIXTURE_DIR = LAB_UI_REPO / "fixtures" / "trace-v1" / "universe-b2-gen0"

REQUIRES_UNIVERSE = pytest.mark.skipif(
    not (Path(UNIVERSE_ROOT) / "target" / "release" / "pista_check").is_file(),
    reason="Universe/target/release/pista_check not built in this checkout",
)
REQUIRES_FIXTURE = pytest.mark.skipif(
    not FIXTURE_DIR.is_dir(), reason=f"fixture not found at {FIXTURE_DIR}"
)


# ── fixtures ──────────────────────────────────────────────────────────────────────────

def _seed_db(db_path: Path) -> None:
    """A small, hermetic dataset covering every table the routes read: two
    paired runs (same battery/seed, different arms, so `paired()`/`/api/compare`
    has something to compare), one prediction, one replay artifact."""
    db = lab_db.connect(str(db_path))
    now = "2026-09-16T00:00:00+00:00"
    for name, arm in (("r1_fixed_s31", "fixed"), ("r1_nocost_s31", "nocost")):
        db.execute(
            "INSERT INTO run (name, project, battery, arm, seed, out_dir, status, written,"
            " gens_requested, gens_complete, ticks, beings, ingested)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?, datetime('now'))",
            (name, "universe", "r1", arm, 31, f"/tmp/{name}", "finished", now, 1, 1, 1000, 4),
        )
        db.execute(
            "INSERT INTO generation (run_name, gen, beings, median_progress_m, mean_progress_m,"
            " max_progress_m, median_distance_m, mean_speed_mps, impacts, collision_energy_j,"
            " alive_ticks, dead) VALUES (?,0,4,10,10,10,10,10,0,0,4000,0)",
            (name,),
        )
        brake = 100.0 if arm == "fixed" else 40.0
        db.execute(
            "INSERT INTO driving (run_name, gen, alive_ticks, brake_ticks, overlap_ticks,"
            " impact_ticks, near_wall_ticks, stationary_ticks, reverse_ticks, contact_ticks,"
            " distance_m, collision_energy_j, throttle_sum, brake_sum, speed_sum, beings,"
            " min_last_tick) VALUES (?,0,1000,?,0,0,0,0,0,0,500,0,500,50,3000,4,1000)",
            (name, brake),
        )
    db.execute(
        "INSERT INTO artifact (run_name, kind, gen, path, bytes, sha256)"
        " VALUES ('r1_fixed_s31','replay',0,'/tmp/r1_fixed_s31/gen0000.replay',1024,'deadbeef')"
    )
    db.execute(
        "INSERT INTO prediction (code, doc, project, battery, kind, registered, status, summary)"
        " VALUES ('B1','/tmp/doc.md','universe','r1','prediction',NULL,NULL,'test prediction')"
    )
    db.commit()
    db.close()


@pytest.fixture
def snapshots_root(tmp_path: Path) -> Path:
    root = tmp_path / "snapshots"
    champions = root / "b1-champions"
    champions.mkdir(parents=True)
    binary = root / "gpu_evolve-testbin"
    binary.write_bytes(b"not a real binary, just needs to exist and be +x")
    binary.chmod(binary.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    (champions / "r1_fixed_s31.bin").write_bytes(b"fake genome bytes")
    return root


@pytest.fixture
def runs_root(tmp_path: Path) -> Path:
    root = tmp_path / "runs_root"
    root.mkdir()
    if FIXTURE_DIR.is_dir():
        # PRD S5 path layout: <run_dir>/trace/gen<NNNN>/being<NN>/<profile>/
        being_dir = root / "b2_cost_s113" / "trace" / "gen0000" / "being00"
        being_dir.mkdir(parents=True)
        (being_dir / "champion").symlink_to(FIXTURE_DIR, target_is_directory=True)
    return root


@pytest.fixture
def spool(tmp_path: Path) -> Path:
    root = tmp_path / "spool"
    for sub in ("pedidos", "estado", "feitos", "recusados"):
        (root / sub).mkdir(parents=True)
    return root


@pytest.fixture
def settings(tmp_path: Path, snapshots_root: Path, runs_root: Path, spool: Path) -> Settings:
    db_path = tmp_path / "lab.db"
    _seed_db(db_path)
    return Settings(
        db=str(db_path), runs_root=str(runs_root), spool=str(spool),
        snapshots_root=str(snapshots_root), universe_root=UNIVERSE_ROOT,
    )


@pytest.fixture
def lan_settings(settings: Settings) -> Settings:
    return settings.model_copy(update={"lan": True, "password": "s3cret-test-pw"})


@pytest.fixture
def client(settings: Settings) -> TestClient:
    return TestClient(create_app(settings))


@pytest.fixture
def lan_client(lan_settings: Settings) -> TestClient:
    return TestClient(create_app(lan_settings))


def _valid_experiment_body(bin_path: Path, **overrides) -> dict:
    body = {
        "id": "t1", "bin": str(bin_path), "gens": 2, "ticks": 100, "beings": 4,
        "seed": 1, "tracks": [8005],
    }
    body.update(overrides)
    return body


# ── auth ──────────────────────────────────────────────────────────────────────────────

class TestAuth:
    def test_loopback_reads_and_writes_need_no_session(self, client: TestClient):
        assert client.get("/api/db/batteries").status_code == 200
        r = client.post("/api/db/annotation", json={"run": "r1_fixed_s31", "text": "note"})
        assert r.status_code == 200

    def test_lan_read_without_session_is_401(self, lan_client: TestClient):
        r = lan_client.get("/api/db/batteries")
        assert r.status_code == 401

    def test_lan_login_wrong_password_is_401(self, lan_client: TestClient):
        r = lan_client.post("/api/login", json={"password": "nope"})
        assert r.status_code == 401

    def test_login_refused_in_loopback_mode(self, client: TestClient):
        r = client.post("/api/login", json={"password": "anything"})
        assert r.status_code == 400

    def test_lan_login_then_read_succeeds(self, lan_client: TestClient):
        r = lan_client.post("/api/login", json={"password": "s3cret-test-pw", "name": "leo"})
        assert r.status_code == 200
        assert r.json() == {"ok": True, "who": "leo"}
        assert lan_client.get("/api/db/batteries").status_code == 200

    def test_lan_write_without_csrf_header_is_403(self, lan_client: TestClient):
        lan_client.post("/api/login", json={"password": "s3cret-test-pw"})
        r = lan_client.post("/api/db/annotation", json={"run": "r1_fixed_s31", "text": "x"})
        assert r.status_code == 403

    def test_lan_write_with_csrf_header_succeeds_and_audits(
        self, lan_client: TestClient, lan_settings: Settings
    ):
        login = lan_client.post("/api/login", json={"password": "s3cret-test-pw", "name": "leo"})
        csrf = login.cookies.get("csrf_token")
        assert csrf
        r = lan_client.post(
            "/api/db/annotation", json={"run": "r1_fixed_s31", "text": "brake fires late"},
            headers={"X-CSRF-Token": csrf},
        )
        assert r.status_code == 200
        db = lab_db.connect(lan_settings.db)
        rows = lab_db.audits(db, action="annotation")
        assert len(rows) == 1
        assert rows[0]["who"] == "leo"
        db.close()

    def test_sql_route_absent_under_lan(self, lan_client: TestClient):
        lan_client.post("/api/login", json={"password": "s3cret-test-pw"})
        r = lan_client.get("/api/sql", params={"q": "select 1"})
        assert r.status_code == 404

    def test_sql_route_present_in_loopback(self, client: TestClient):
        r = client.get("/api/sql", params={"q": "select 1 as one"})
        assert r.status_code == 200
        assert r.json() == [{"one": 1}]

    def test_sql_rejects_non_select(self, client: TestClient):
        r = client.get("/api/sql", params={"q": "delete from run"})
        assert r.status_code == 400


# ── db routes ─────────────────────────────────────────────────────────────────────────

class TestDbRoutes:
    def test_batteries(self, client: TestClient):
        r = client.get("/api/db/batteries")
        assert r.status_code == 200
        batteries = {b["battery"]: b for b in r.json()}
        assert batteries["r1"]["runs"] == 2

    def test_runs_filtered_by_battery_and_replays_count(self, client: TestClient):
        r = client.get("/api/db/runs", params={"battery": "r1"})
        assert r.status_code == 200
        rows = {row["name"]: row for row in r.json()}
        assert rows["r1_fixed_s31"]["replays"] == 1
        assert rows["r1_nocost_s31"]["replays"] == 0

    def test_run_detail(self, client: TestClient):
        r = client.get("/api/db/run/r1_fixed_s31")
        assert r.status_code == 200
        body = r.json()
        assert body["run"]["name"] == "r1_fixed_s31"
        assert len(body["generations"]) == 1
        assert len(body["driving"]) == 1
        assert len(body["artifacts"]) == 1

    def test_run_detail_404(self, client: TestClient):
        r = client.get("/api/db/run/does-not-exist")
        assert r.status_code == 404

    def test_predictions(self, client: TestClient):
        r = client.get("/api/db/predictions", params={"battery": "r1"})
        assert r.status_code == 200
        assert r.json()[0]["code"] == "B1"

    def test_annotations_round_trip(self, client: TestClient):
        post = client.post(
            "/api/db/annotation", json={"run": "r1_fixed_s31", "text": "note", "gen": 0}
        )
        assert post.status_code == 200
        r = client.get("/api/db/annotations", params={"run": "r1_fixed_s31"})
        assert r.status_code == 200
        assert any(a["text"] == "note" for a in r.json())

    def test_annotation_unknown_run_is_404(self, client: TestClient):
        r = client.post("/api/db/annotation", json={"run": "nope", "text": "x"})
        assert r.status_code == 404

    def test_verdict_writes_and_audits(self, client: TestClient, settings: Settings):
        r = client.post("/api/db/verdict", json={"code": "B1", "status": "confirmed"})
        assert r.status_code == 200
        assert r.json() == {"changed": 1}
        db = lab_db.connect(settings.db)
        row = db.execute("SELECT status FROM prediction WHERE code='B1'").fetchone()
        assert row["status"] == "confirmed"
        assert len(lab_db.audits(db, action="verdict")) == 1
        db.close()

    def test_verdict_bad_status_is_422(self, client: TestClient):
        r = client.post("/api/db/verdict", json={"code": "B1", "status": "bogus"})
        assert r.status_code == 422

    def test_compare(self, client: TestClient):
        r = client.get(
            "/api/compare",
            params={"battery": "r1", "left": "fixed", "right": "nocost", "metric": "brake_pct_alive"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["n"] == 1
        assert body["mean"] == pytest.approx(6.0)  # (100/1000*100) - (40/1000*100) = 10 - 4


# ── queue routes ──────────────────────────────────────────────────────────────────────

class TestQueueRoutes:
    def test_post_writes_atomically_and_no_tmp_file_left(
        self, client: TestClient, settings: Settings, snapshots_root: Path
    ):
        bin_path = snapshots_root / "gpu_evolve-testbin"
        r = client.post("/api/queue", json=_valid_experiment_body(bin_path))
        assert r.status_code == 201, r.text
        pedidos_dir = Path(settings.spool) / "pedidos"
        names = sorted(p.name for p in pedidos_dir.iterdir())
        assert names == ["lab-ui_t1.json"]  # no .tmp left behind
        pedido = json.loads((pedidos_dir / "lab-ui_t1.json").read_text())
        assert pedido["id"] == "t1"
        assert pedido["script"] == "universe_run"
        assert pedido["args"]["bin"] == str(bin_path)
        assert pedido["args"]["tracks"] == [8005]

    def test_post_audits_launch(self, client: TestClient, settings: Settings, snapshots_root: Path):
        client.post("/api/queue", json=_valid_experiment_body(snapshots_root / "gpu_evolve-testbin"))
        db = lab_db.connect(settings.db)
        assert len(lab_db.audits(db, action="launch")) == 1
        db.close()

    def test_post_rejects_duplicate_id(self, client: TestClient, snapshots_root: Path):
        body = _valid_experiment_body(snapshots_root / "gpu_evolve-testbin")
        assert client.post("/api/queue", json=body).status_code == 201
        r = client.post("/api/queue", json=body)
        assert r.status_code == 409

    def test_post_rejects_bin_outside_snapshots(self, client: TestClient, tmp_path: Path):
        outside = tmp_path / "not-a-snapshot"
        outside.write_bytes(b"x")
        outside.chmod(0o755)
        r = client.post("/api/queue", json=_valid_experiment_body(outside, id="t2"))
        assert r.status_code == 422
        assert "snapshots" in r.json()["detail"]["error"]

    def test_post_rejects_bin_in_champions_subdir(self, client: TestClient, snapshots_root: Path):
        champ = snapshots_root / "b1-champions" / "r1_fixed_s31.bin"
        r = client.post("/api/queue", json=_valid_experiment_body(champ, id="t3"))
        assert r.status_code == 422

    def test_post_rejects_unknown_arm_flag(self, client: TestClient, snapshots_root: Path):
        body = _valid_experiment_body(
            snapshots_root / "gpu_evolve-testbin", id="t4",
            arm_flags=[{"flag": "totally-not-a-real-flag"}],
        )
        r = client.post("/api/queue", json=body)
        assert r.status_code == 422
        assert "unknown" in r.json()["detail"]["error"]

    @REQUIRES_UNIVERSE
    def test_post_accepts_real_arm_flag_and_value_flag(self, client: TestClient, snapshots_root: Path):
        body = _valid_experiment_body(
            snapshots_root / "gpu_evolve-testbin", id="t5",
            arm_flags=[{"flag": "--no-neuron-memory"}, {"flag": "sigma", "value": 0.1}],
        )
        r = client.post("/api/queue", json=body)
        assert r.status_code == 201, r.text
        assert r.json()["pedido"]["args"]["no-neuron-memory"] is True
        assert r.json()["pedido"]["args"]["sigma"] == 0.1

    def test_post_rejects_switch_flag_with_false_value(self, client: TestClient, snapshots_root: Path):
        body = _valid_experiment_body(
            snapshots_root / "gpu_evolve-testbin", id="t6",
            arm_flags=[{"flag": "no-neuron-memory", "value": False}],
        )
        r = client.post("/api/queue", json=body)
        assert r.status_code == 422

    def test_post_rejects_value_flag_without_value(self, client: TestClient, snapshots_root: Path):
        body = _valid_experiment_body(
            snapshots_root / "gpu_evolve-testbin", id="t7", arm_flags=[{"flag": "sigma"}],
        )
        r = client.post("/api/queue", json=body)
        assert r.status_code == 422

    def test_post_rejects_reserved_flag_name(self, client: TestClient, snapshots_root: Path):
        # "seed" is a dedicated top-level field, not an arm flag -- see flags.RESERVED_FLAG_NAMES.
        body = _valid_experiment_body(
            snapshots_root / "gpu_evolve-testbin", id="t8", arm_flags=[{"flag": "seed", "value": 5}],
        )
        r = client.post("/api/queue", json=body)
        assert r.status_code == 422

    def test_post_rejects_invalid_track(self, client: TestClient, snapshots_root: Path, monkeypatch):
        # Unit-level: proves the route actually consults validate_track's verdict
        # and refuses before writing anything to the spool. The real-binary
        # equivalents (seed 8215, 8300) live in TestTracksAndSnapshots below --
        # see DEVIATIONS.md #1, no longer "no naturally-failing seed found".
        import lab_api.routes.queue as queue_mod

        def fake_invalid(settings, seed, width=28.0, ate=None):
            return {"seed": seed, "width": width, "ate": ate, "valid": False,
                    "issues": ["  270    Road    3.0m    2.0m    99999m  ← BOTTLENECK"]}

        monkeypatch.setattr(queue_mod, "validate_track", fake_invalid)
        body = _valid_experiment_body(snapshots_root / "gpu_evolve-testbin", id="t9")
        r = client.post("/api/queue", json=body)
        assert r.status_code == 422
        assert "unvalidated track" in r.json()["detail"]["error"]

    @REQUIRES_UNIVERSE
    def test_get_queue_mirrors_pending_request(
        self, client: TestClient, snapshots_root: Path
    ):
        client.post("/api/queue", json=_valid_experiment_body(snapshots_root / "gpu_evolve-testbin", id="tq"))
        r = client.get("/api/queue")
        assert r.status_code == 200
        rows = {row["id"]: row for row in r.json()}
        assert rows["tq"]["state"] == "pending"
        assert rows["tq"]["script"] == "universe_run"

    def test_put_edits_pending_request_in_place(
        self, client: TestClient, settings: Settings, snapshots_root: Path
    ):
        bin_path = snapshots_root / "gpu_evolve-testbin"
        client.post("/api/queue", json=_valid_experiment_body(bin_path, id="tp"))
        body = _valid_experiment_body(bin_path, id="tp", gens=99)
        r = client.put("/api/queue/tp", json=body)
        assert r.status_code == 200
        assert r.json()["pedido"]["args"]["gens"] == 99
        # still exactly one file, same name (PUT edits IN PLACE, does not rename)
        pedidos_dir = Path(settings.spool) / "pedidos"
        assert [p.name for p in pedidos_dir.iterdir()] == ["lab-ui_tp.json"]

    def test_put_refuses_running_request(
        self, client: TestClient, settings: Settings, snapshots_root: Path
    ):
        bin_path = snapshots_root / "gpu_evolve-testbin"
        client.post("/api/queue", json=_valid_experiment_body(bin_path, id="tr"))
        estado_dir = Path(settings.spool) / "estado"
        (estado_dir / "tr.json").write_text(json.dumps({"id": "tr", "fase": "rodando"}))
        r = client.put("/api/queue/tr", json=_valid_experiment_body(bin_path, id="tr", gens=3))
        assert r.status_code == 409

    def test_put_unknown_id_is_404(self, client: TestClient, snapshots_root: Path):
        r = client.put("/api/queue/nope", json=_valid_experiment_body(snapshots_root / "gpu_evolve-testbin"))
        assert r.status_code == 404

    def test_delete_removes_pending_request(
        self, client: TestClient, settings: Settings, snapshots_root: Path
    ):
        bin_path = snapshots_root / "gpu_evolve-testbin"
        client.post("/api/queue", json=_valid_experiment_body(bin_path, id="td"))
        r = client.delete("/api/queue/td")
        assert r.status_code == 200
        pedidos_dir = Path(settings.spool) / "pedidos"
        assert list(pedidos_dir.iterdir()) == []

    def test_delete_refuses_running_request(
        self, client: TestClient, settings: Settings, snapshots_root: Path
    ):
        bin_path = snapshots_root / "gpu_evolve-testbin"
        client.post("/api/queue", json=_valid_experiment_body(bin_path, id="tdr"))
        estado_dir = Path(settings.spool) / "estado"
        (estado_dir / "tdr.json").write_text(json.dumps({"id": "tdr", "fase": "rodando"}))
        r = client.delete("/api/queue/tdr")
        assert r.status_code == 409

    def test_delete_unknown_id_is_404(self, client: TestClient):
        r = client.delete("/api/queue/nope")
        assert r.status_code == 404


# ── tracks/validate, snapshots ───────────────────────────────────────────────────────

class TestTracksAndSnapshots:
    @REQUIRES_UNIVERSE
    def test_tracks_validate_real_seed(self, client: TestClient):
        r = client.get("/api/tracks/validate", params={"seed": 8005})
        assert r.status_code == 200
        body = r.json()
        assert body["seed"] == 8005
        assert body["valid"] is True
        assert body["issues"] == []

    # Cold tester's finding: `pista_check` exits 0 for seed 8300 but prints
    # "[AVISO] ... falling back to unvalidated reserve candidate" on STDERR, which
    # validate_track used to read only when returncode != 0 -- so POST /api/queue
    # returned 201 instead of 422. Also, without a full-lap `--ate`, seed 8215's 4
    # defects (at 1152 m) sit past the binary's own 600 m default and were never
    # seen. `validate_track`'s default `ate=None` now walks the FULL lap and always
    # checks stderr for `[AVISO]`, regardless of exit code.
    @REQUIRES_UNIVERSE
    def test_tracks_validate_refuses_aviso_fallback_seed(self, client: TestClient):
        r = client.get("/api/tracks/validate", params={"seed": 8300})
        assert r.status_code == 200
        body = r.json()
        assert body["valid"] is False
        assert any("AVISO" in i for i in body["issues"])

    @REQUIRES_UNIVERSE
    def test_tracks_validate_refuses_defect_past_600m(self, client: TestClient):
        r = client.get("/api/tracks/validate", params={"seed": 8215})
        assert r.status_code == 200
        body = r.json()
        assert body["valid"] is False
        assert body["ate"] > 600.0
        assert any("AXIS OFF THE TRACK" in i for i in body["issues"])

    @REQUIRES_UNIVERSE
    def test_tracks_validate_accepts_clean_seed_8200(self, client: TestClient):
        r = client.get("/api/tracks/validate", params={"seed": 8200})
        assert r.status_code == 200
        body = r.json()
        assert body["valid"] is True
        assert body["issues"] == []

    @REQUIRES_UNIVERSE
    def test_post_queue_refuses_aviso_fallback_track(self, client: TestClient, snapshots_root: Path):
        body = _valid_experiment_body(snapshots_root / "gpu_evolve-testbin", id="t-8300", tracks=[8300])
        r = client.post("/api/queue", json=body)
        assert r.status_code == 422
        assert "AVISO" in r.json()["detail"]["error"]

    @REQUIRES_UNIVERSE
    def test_post_queue_refuses_out_of_window_defect_track(self, client: TestClient, snapshots_root: Path):
        body = _valid_experiment_body(snapshots_root / "gpu_evolve-testbin", id="t-8215", tracks=[8215])
        r = client.post("/api/queue", json=body)
        assert r.status_code == 422

    @REQUIRES_UNIVERSE
    def test_post_queue_accepts_clean_track_8200(self, client: TestClient, snapshots_root: Path):
        body = _valid_experiment_body(snapshots_root / "gpu_evolve-testbin", id="t-8200", tracks=[8200])
        r = client.post("/api/queue", json=body)
        assert r.status_code == 201, r.text

    def test_snapshots_lists_binaries_and_champions(self, client: TestClient):
        r = client.get("/api/snapshots")
        assert r.status_code == 200
        body = r.json()
        names = {b["name"] for b in body["binaries"]}
        assert "gpu_evolve-testbin" in names
        champ_names = {c["name"] for c in body["champions"]}
        assert "r1_fixed_s31.bin" in champ_names


# ── track output parsing (unit-level, no subprocess) ────────────────────────────────

class TestParsePistaCheck:
    def test_no_defects_is_valid(self):
        from lab_api.routes.queue import _parse_pista_check

        valid, issues = _parse_pista_check(
            "TRACK seed 8005\n...\nNo defects: the axis is on asphalt...\n"
        )
        assert valid is True
        assert issues == []

    def test_axis_off_track_is_invalid(self):
        from lab_api.routes.queue import _parse_pista_check

        text = "  270     Grass    0.0m    0.0m  99999m  ← AXIS OFF THE TRACK\n270 points with defects"
        valid, issues = _parse_pista_check(text)
        assert valid is False
        assert any("AXIS OFF THE TRACK" in i for i in issues)

    def test_bottleneck_is_invalid(self):
        from lab_api.routes.queue import _parse_pista_check

        text = "  480     Road    2.0m    1.0m     13m  ← BOTTLENECK\n1 points with defects"
        valid, issues = _parse_pista_check(text)
        assert valid is False

    def test_null_variance_is_invalid(self):
        from lab_api.routes.queue import _parse_pista_check

        text = (
            "  saturated at 60.0 m: 0.0%\n"
            "  mean 60.0 m . standard deviation 0.00 m\n"
            "  -> NULL VARIANCE: the channel is constant.\n"
            "No defects: the axis is on asphalt...\n"  # even if the walk found no point defect
        )
        valid, issues = _parse_pista_check(text)
        assert valid is False


# ── flag registry ─────────────────────────────────────────────────────────────────────

class TestFlagRegistry:
    @REQUIRES_UNIVERSE
    def test_loads_real_registry_and_excludes_reserved(self):
        from lab_api.flags import arm_flag_allow_list

        cli_flags_path = str(Path(UNIVERSE_ROOT) / "src" / "bin" / "gpu_evolve" / "cli_flags.rs")
        allow = arm_flag_allow_list(cli_flags_path)
        assert "no-neuron-memory" in allow
        assert allow["no-neuron-memory"].takes_value is False
        assert "sigma" in allow and allow["sigma"].takes_value is True
        assert "seed" not in allow  # reserved: dedicated schema field
        assert "out" not in allow  # reserved: process plumbing

    def test_missing_file_raises(self, tmp_path: Path):
        from lab_api.flags import FlagRegistryError, load_flag_registry

        load_flag_registry.cache_clear()
        with pytest.raises(FlagRegistryError):
            load_flag_registry(str(tmp_path / "does-not-exist.rs"))


# ── trace routes ──────────────────────────────────────────────────────────────────────

class TestTraceRoutes:
    @REQUIRES_FIXTURE
    def test_manifest_200(self, client: TestClient):
        r = client.get("/api/trace/b2_cost_s113/0/0/champion")
        assert r.status_code == 200
        body = r.json()
        assert body["magic"] == "trace-v1"
        assert body["run"] == "b2_cost_s113"
        assert body["count"] == 300

    def test_manifest_404_when_not_produced(self, client: TestClient):
        r = client.get("/api/trace/no-such-run/0/0/champion")
        assert r.status_code == 404
        assert r.json()["detail"]["error"] == "not produced"

    @REQUIRES_FIXTURE
    def test_block_range_exact_byte_length(self, client: TestClient):
        r = client.get("/api/trace/b2_cost_s113/0/0/champion/block/cfc", params={"t0": 0, "t1": 10})
        assert r.status_code == 200
        assert len(r.content) == 10 * 96 * 4  # T=10, 96 channels, f32

    @REQUIRES_FIXTURE
    def test_block_full_range_matches_manifest_length(self, client: TestClient):
        manifest = client.get("/api/trace/b2_cost_s113/0/0/champion").json()
        block = next(b for b in manifest["blocks"] if b["name"] == "cfc")
        r = client.get("/api/trace/b2_cost_s113/0/0/champion/block/cfc")
        assert len(r.content) == block["length"]

    @REQUIRES_FIXTURE
    def test_block_hash_is_verified_and_cached(self, client: TestClient):
        import lab_api.routes.trace as trace_mod

        trace_mod._verified_blocks.clear()
        r1 = client.get("/api/trace/b2_cost_s113/0/0/champion/block/cfc", params={"t0": 0, "t1": 5})
        assert r1.status_code == 200
        assert len(trace_mod._verified_blocks) == 1
        r2 = client.get("/api/trace/b2_cost_s113/0/0/champion/block/cfc", params={"t0": 5, "t1": 10})
        assert r2.status_code == 200
        assert len(trace_mod._verified_blocks) == 1  # same key, not re-added

    @REQUIRES_FIXTURE
    def test_unknown_block_is_404(self, client: TestClient):
        r = client.get("/api/trace/b2_cost_s113/0/0/champion/block/nope")
        assert r.status_code == 404

    @REQUIRES_FIXTURE
    def test_absent_block_names_reason(self, client: TestClient):
        r = client.get("/api/trace/b2_cost_s113/0/0/champion/block/l1")
        assert r.status_code == 404
        assert r.json()["detail"]["reason"] == "not recorded by this binary"

    @REQUIRES_FIXTURE
    def test_replay_served_as_octet_stream(self, client: TestClient):
        r = client.get("/api/trace/b2_cost_s113/0/0/champion/replay")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("application/octet-stream")
        assert r.content[:8] == b"IARARPLY"

    @REQUIRES_FIXTURE
    def test_genome_served(self, client: TestClient):
        r = client.get("/api/trace/b2_cost_s113/0/0/champion/genome")
        assert r.status_code == 200
        assert len(r.content) == 99_184

    @REQUIRES_FIXTURE
    def test_events_served_as_json(self, client: TestClient):
        r = client.get("/api/trace/b2_cost_s113/0/0/champion/events")
        assert r.status_code == 200
        assert isinstance(r.json(), list)
        assert r.json()[0]["kind"]

    @REQUIRES_FIXTURE
    def test_weights_absent_with_reason(self, client: TestClient):
        r = client.get("/api/trace/b2_cost_s113/0/0/champion/weights")
        assert r.status_code == 404
        assert r.json()["detail"]["reason"] == "produced by S2"

    @REQUIRES_FIXTURE
    def test_track_absent_with_reason(self, client: TestClient):
        r = client.get("/api/trace/b2_cost_s113/0/0/champion/track")
        assert r.status_code == 404
        assert r.json()["detail"]["reason"] == "produced by S2"


# ── counterfactual stub ───────────────────────────────────────────────────────────────

class TestCounterfactual:
    def test_returns_501(self, client: TestClient):
        r = client.post("/api/counterfactual", json={"trace": "b2_cost_s113/0/0/champion", "tick": 16, "remove": []})
        assert r.status_code == 501
        assert "S2" in r.json()["detail"]["error"]


def test_db_dependency_connection_is_usable_from_another_thread(settings: Settings) -> None:
    """FastAPI opens a sync yield-dependency in one threadpool thread and runs the sync route
    in another; with sqlite3's default thread check 182 of 200 parallel requests failed with
    500 (16/09). The per-request connection must work across threads."""
    import threading
    from types import SimpleNamespace

    from lab_api.deps import get_db

    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(settings=settings)))
    gen = get_db(request)
    db = next(gen)
    errors: list[BaseException] = []

    def use() -> None:
        try:
            db.execute('SELECT 1').fetchone()
        except BaseException as exc:  # noqa: BLE001 - the assertion reports it
            errors.append(exc)

    worker = threading.Thread(target=use)
    worker.start()
    worker.join()
    gen.close()
    assert errors == []
