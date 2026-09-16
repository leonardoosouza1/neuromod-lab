"""Access control, exactly per lab-ui PRD S1 §8.

    | access | default 127.0.0.1, no login. --lan binds 0.0.0.0, REQUIRES the
    | password (/media/llm-data/lab-ui.env, created on first start, never in
    | repo/chat/docs), disables /api/sql, adds CSRF on write routes and an
    | audit line per launch/cancel/edit

Two modes, selected once at process start by `settings.lan`:

* **loopback** (`lan=False`, the default): every route is open, no session,
  no CSRF. This machine's owner is the only thing that can reach
  `127.0.0.1` -- the whole point of the default.
* **lan** (`lan=True`): every route requires a valid session cookie (set by
  `POST /api/login` with the shared password from the env file); every
  WRITE route additionally requires a CSRF token that matches the one
  minted at login (double-submit cookie: a non-HttpOnly `csrf_token`
  cookie the browser can read and echo back in the `X-CSRF-Token` header,
  compared against the same value stored server-side against the session).

The password is never logged, never echoed in a response body, and never
appears in `lab_db.audit` (which stores a payload hash, never the payload
-- see `lab_db.py`'s own `audit()` docstring).

Sessions live in a plain in-process dict. This is a single-process
`uvicorn` server serving one household's LAN (PRD §11 non-goals:
"multi-user accounts"), so a session store shared across workers or
surviving a restart is not a requirement this slice has to meet.
"""
from __future__ import annotations

import hmac
import secrets
import time
from dataclasses import dataclass

from fastapi import Cookie, Header, HTTPException, Request

from .settings import Settings

SESSION_COOKIE = "lab_ui_session"
CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "x-csrf-token"
SESSION_TTL_SECONDS = 8 * 3600  # PRD S1 §8: "cookie session (HttpOnly, 8 h)"


@dataclass
class Session:
    who: str
    csrf: str
    expires: float


class SessionStore:
    """In-memory session table. One instance lives on `app.state.sessions`."""

    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}

    def create(self, who: str) -> tuple[str, str]:
        """Returns (session_id, csrf_token)."""
        session_id = secrets.token_urlsafe(32)
        csrf = secrets.token_urlsafe(32)
        self._sessions[session_id] = Session(
            who=who, csrf=csrf, expires=time.time() + SESSION_TTL_SECONDS
        )
        return session_id, csrf

    def get(self, session_id: str | None) -> Session | None:
        if not session_id:
            return None
        session = self._sessions.get(session_id)
        if session is None:
            return None
        if session.expires < time.time():
            del self._sessions[session_id]
            return None
        return session

    def drop(self, session_id: str | None) -> None:
        if session_id:
            self._sessions.pop(session_id, None)


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_session_store(request: Request) -> SessionStore:
    return request.app.state.sessions


def check_password(settings: Settings, candidate: str) -> bool:
    """Constant-time compare -- a password check is exactly the kind of thing a
    naive `==` turns into a timing oracle."""
    if not settings.password:
        return False
    return hmac.compare_digest(settings.password, candidate)


def current_who(
    request: Request,
    lab_ui_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> str:
    """The identity to record in `lab_db.audit`. In loopback mode this never checks
    anything -- the machine's own login is the access control (PRD: "default
    127.0.0.1, no login"). Under `--lan`, requires a live session and returns its
    `who`; raises 401 otherwise. FastAPI dependency, use as
    `who: str = Depends(current_who)`.
    """
    settings: Settings = request.app.state.settings
    if not settings.lan:
        return "loopback"
    store: SessionStore = request.app.state.sessions
    session = store.get(lab_ui_session)
    if session is None:
        raise HTTPException(status_code=401, detail={"error": "login required under --lan"})
    return session.who


def require_csrf(
    request: Request,
    lab_ui_session: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    x_csrf_token: str | None = Header(default=None, alias=CSRF_HEADER),
) -> None:
    """Dependency for every WRITE route (PRD S1 §8: "CSRF token on every write
    route" under --lan). No-op in loopback mode. Under --lan: the session must
    exist (this doubles as the write-path's login check) and the `X-CSRF-Token`
    header must match the token minted for that session at login.
    """
    settings: Settings = request.app.state.settings
    if not settings.lan:
        return
    store: SessionStore = request.app.state.sessions
    session = store.get(lab_ui_session)
    if session is None:
        raise HTTPException(status_code=401, detail={"error": "login required under --lan"})
    if not x_csrf_token or not hmac.compare_digest(session.csrf, x_csrf_token):
        raise HTTPException(status_code=403, detail={"error": "missing or invalid CSRF token"})
