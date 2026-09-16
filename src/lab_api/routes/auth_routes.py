"""`POST /api/login` / `POST /api/logout` -- lab-ui PRD S1 §7: "(only meaningful
under --lan)". In loopback mode there is nothing to log into (PRD §8: "default
127.0.0.1, no login"), so `/api/login` refuses with 400 rather than pretending
to establish a session that no route will ever check.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

from ..auth import (
    CSRF_COOKIE,
    SESSION_COOKIE,
    SESSION_TTL_SECONDS,
    SessionStore,
    check_password,
    get_session_store,
    get_settings,
)
from ..settings import Settings

router = APIRouter()


class LoginBody(BaseModel):
    password: str = Field(min_length=1)
    name: str = Field(default="lan", max_length=40)


@router.post("/api/login")
def login(
    body: LoginBody, response: Response,
    settings: Settings = Depends(get_settings), store: SessionStore = Depends(get_session_store),
) -> dict:
    if not settings.lan:
        raise HTTPException(status_code=400, detail={"error": "login is only meaningful under --lan"})
    if not check_password(settings, body.password):
        raise HTTPException(status_code=401, detail={"error": "wrong password"})

    session_id, csrf = store.create(who=body.name or "lan")
    response.set_cookie(
        SESSION_COOKIE, session_id, max_age=SESSION_TTL_SECONDS,
        httponly=True, samesite="lax", secure=False, path="/",
    )
    # NOT HttpOnly: the double-submit CSRF pattern requires the browser's own JS
    # to read this cookie and echo it back in the X-CSRF-Token header.
    response.set_cookie(
        CSRF_COOKIE, csrf, max_age=SESSION_TTL_SECONDS,
        httponly=False, samesite="lax", secure=False, path="/",
    )
    return {"ok": True, "who": body.name or "lan"}


@router.post("/api/logout")
def logout(
    request: Request, response: Response, store: SessionStore = Depends(get_session_store)
) -> dict:
    store.drop(request.cookies.get(SESSION_COOKIE))
    response.delete_cookie(SESSION_COOKIE, path="/")
    response.delete_cookie(CSRF_COOKIE, path="/")
    return {"ok": True}
