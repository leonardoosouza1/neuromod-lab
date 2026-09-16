"""`/api/db/*` plus the two routes carried over from `lab_api.py` at parity
(`/api/compare`, `/api/sql`) -- lab-ui PRD S1/§7.

Every read route is a thin wrapper over `lab_db`; no route re-implements a
query `lab_db` already exposes. The two write routes (`verdict`, `annotation`)
each log one `lab_db.audit` row, per PRD §7: "Write routes: pydantic schema,
CSRF token under --lan, one audit line in lab.db."
"""
from __future__ import annotations

import sqlite3

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

import lab_db
from ..auth import current_who, require_csrf
from ..deps import get_db

# `dependencies=[Depends(current_who)]` at the router level gates EVERY route
# below (reads included) behind a live session under --lan (PRD S1 §8: under
# --lan the whole app requires the password, not just the write routes; in
# loopback mode `current_who` is a no-op that always succeeds). Write routes
# add `require_csrf` individually since that check only applies to them.
router = APIRouter(dependencies=[Depends(current_who)])


@router.get("/api/db/batteries")
def get_batteries(db: sqlite3.Connection = Depends(get_db)) -> list[dict]:
    return [dict(r) for r in lab_db.batteries(db)]


@router.get("/api/db/runs")
def get_runs(
    battery: str | None = None, arm: str | None = None, status: str | None = None,
    db: sqlite3.Connection = Depends(get_db),
) -> list[dict]:
    rows = [dict(r) for r in lab_db.runs(db, battery=battery, arm=arm, status=status)]
    for row in rows:
        row["replays"] = db.execute(
            "SELECT COUNT(*) FROM artifact WHERE run_name = ? AND kind = 'replay'",
            (row["name"],),
        ).fetchone()[0]
    return rows


@router.get("/api/db/run/{name}")
def get_run(name: str, db: sqlite3.Connection = Depends(get_db)) -> dict:
    run = db.execute("SELECT * FROM run WHERE name = ?", (name,)).fetchone()
    if run is None:
        raise HTTPException(status_code=404, detail={"error": f"no such run: {name}"})
    return {
        "run": dict(run),
        "generations": [
            dict(r) for r in db.execute(
                "SELECT * FROM generation WHERE run_name = ? ORDER BY gen", (name,)
            )
        ],
        "driving": [
            dict(r) for r in db.execute(
                "SELECT * FROM driving WHERE run_name = ? ORDER BY gen", (name,)
            )
        ],
        "artifacts": [
            dict(r) for r in db.execute(
                "SELECT kind, gen, path, bytes FROM artifact WHERE run_name = ?"
                " ORDER BY kind, gen", (name,)
            )
        ],
    }


@router.get("/api/db/predictions")
def get_predictions(
    battery: str | None = None, status: str | None = None,
    db: sqlite3.Connection = Depends(get_db),
) -> list[dict]:
    return [dict(r) for r in lab_db.predictions(db, battery=battery, status=status)]


@router.get("/api/db/annotations")
def get_annotations(
    run: str | None = None, gen: int | None = None, db: sqlite3.Connection = Depends(get_db)
) -> list[dict]:
    return [dict(r) for r in lab_db.annotations(db, run=run, gen=gen)]


class VerdictBody(BaseModel):
    code: str = Field(min_length=1, max_length=16)
    status: str
    doc: str | None = None


@router.post("/api/db/verdict")
def post_verdict(
    body: VerdictBody,
    db: sqlite3.Connection = Depends(get_db),
    who: str = Depends(current_who),
    _csrf: None = Depends(require_csrf),
) -> dict:
    try:
        changed = lab_db.set_verdict(db, body.code, body.status, doc=body.doc)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail={"error": str(exc)}) from exc
    lab_db.audit(db, who, "verdict", body.model_dump())
    return {"changed": changed}


class AnnotationBody(BaseModel):
    run: str = Field(min_length=1)
    text: str = Field(min_length=1, max_length=4000)
    gen: int | None = None
    tick: int | None = None
    author: str = ""


@router.post("/api/db/annotation")
def post_annotation(
    body: AnnotationBody,
    db: sqlite3.Connection = Depends(get_db),
    who: str = Depends(current_who),
    _csrf: None = Depends(require_csrf),
) -> dict:
    try:
        row_id = lab_db.add_annotation(
            db, body.run, body.text, gen=body.gen, tick=body.tick,
            author=body.author or who,
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=404, detail={"error": f"no such run: {body.run}"}) from exc
    lab_db.audit(db, who, "annotation", body.model_dump())
    return {"id": row_id}


@router.get("/api/compare")
def get_compare(
    battery: str = "", left: str = "", right: str = "",
    metric: str = "brake_pct_alive", include_running: str | None = None,
    db: sqlite3.Connection = Depends(get_db),
) -> dict:
    try:
        return lab_db.paired(db, battery, left, right, metric, include_running == "1")
    except sqlite3.Error as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc


# A SEPARATE router, included by app.py only when NOT running under --lan (PRD
# S1 §8: "/api/sql disabled entirely under --lan"). Keeping it as its own router
# means the route does not exist at all under --lan -- a 404, not a 403 -- which
# is the strongest reading of "disabled entirely": no code path in this process
# can reach a raw-SQL execution once --lan is set.
sql_router = APIRouter()


@sql_router.get("/api/sql")
def get_sql(q: str = "", db: sqlite3.Connection = Depends(get_db)) -> list[dict]:
    lowered = q.strip().lower()
    if not (lowered.startswith("select") or lowered.startswith("with")):
        raise HTTPException(status_code=400, detail={"error": "only SELECT/WITH are served here"})
    try:
        return [dict(r) for r in db.execute(q).fetchall()]
    except sqlite3.Error as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
