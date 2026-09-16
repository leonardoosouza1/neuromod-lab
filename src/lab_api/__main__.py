"""`python -m lab_api --port 8130 [--lan] [--db PATH] [--spool PATH] [--runs-root PATH]`

Run from `src/` (or with `src/` on `PYTHONPATH`) so both `lab_api` (this
package) and `lab_db` (its sibling module) import cleanly -- the same
convention `lab_api.trace.check`'s own CLI already uses (see repo
`TESTING.md`).
"""
from __future__ import annotations

import uvicorn

from .app import create_app
from .settings import build_settings


def main() -> None:
    settings = build_settings()
    app = create_app(settings)
    mode = "LAN (password required)" if settings.lan else "loopback (no login)"
    print(f"lab-ui API on http://{settings.bind}:{settings.port}  [{mode}]  db={settings.db}")
    uvicorn.run(app, host=settings.bind, port=settings.port, log_level="info")


if __name__ == "__main__":
    main()
