"""Shared FastAPI dependencies: one `lab_db` connection per request.

A yield-dependency rather than a pooled connection: `lab_db.connect()` is cheap
(SQLite, WAL mode, no network round trip) and every route in this slice does at
most a handful of queries, so a fresh connection per request is simpler than a
pool and closes deterministically even if a route raises.
"""
from __future__ import annotations

import sqlite3
from collections.abc import Iterator

from fastapi import Request

import lab_db
from .settings import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_db(request: Request) -> Iterator[sqlite3.Connection]:
    settings: Settings = request.app.state.settings
    # FastAPI runs a sync yield-dependency and the sync route in different threadpool
    # threads; the default check raised `sqlite3.ProgrammingError` on ~1 in 10 requests under
    # the UI's parallel fetches (16/09). The connection is still private to this request.
    db = lab_db.connect(settings.db, check_same_thread=False)
    try:
        yield db
    finally:
        db.close()
