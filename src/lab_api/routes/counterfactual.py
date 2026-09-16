"""`POST /api/counterfactual` -- lab-ui PRD S1 §7.

Route shape only. The actual computation ("ablate at tick t, recompute
through the reference forward", PRD §3 "contribution vs causality") needs
Universe's `brain_step` reference forward (state + genome -> outputs),
which is S2's deliverable (PRD §4: "Universe ONLY: ... a `brain_step`
reference forward ... for the counterfactual"). Until that lands, this
route always answers 501 -- never a fabricated `{outputs, delta}`.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..auth import current_who, require_csrf

router = APIRouter(dependencies=[Depends(current_who)])


class CounterfactualRequest(BaseModel):
    trace: str  # "<run>/<gen>/<being>/<profile>", same shape the trace routes take apart
    tick: int
    remove: list[str] = []


@router.post("/api/counterfactual")
def post_counterfactual(
    body: CounterfactualRequest, _csrf: None = Depends(require_csrf)
) -> None:
    raise HTTPException(
        status_code=501,
        detail={"error": "needs the brain_step reference forward from S2"},
    )
