"""FastAPI app factory -- lab-ui PRD S1.

`create_app(settings)` wires every router; `/api/sql` is the one route NOT
always present -- it is only included when `settings.lan` is `False` (PRD
S1 §8: "`/api/sql` disabled entirely under `--lan`"), so under `--lan` the
route does not exist (404), rather than existing but refusing (403).
"""
from __future__ import annotations

from fastapi import FastAPI

from .auth import SessionStore
from .routes import auth_routes, counterfactual, db, queue, trace
from .settings import Settings


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="lab-ui API", description="lab-ui PRD S1 -- see neuromod-lab/src/lab_api/")
    app.state.settings = settings
    app.state.sessions = SessionStore()

    app.include_router(db.router)
    if not settings.lan:
        app.include_router(db.sql_router)
    app.include_router(queue.router)
    app.include_router(trace.router)
    app.include_router(counterfactual.router)
    app.include_router(auth_routes.router)

    @app.get("/api/health")
    def health() -> dict:
        return {"ok": True, "lan": settings.lan}

    return app
