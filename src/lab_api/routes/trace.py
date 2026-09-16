"""`/api/trace/*` -- lab-ui PRD S1 §7, serving the trace-v1 contract (S0) over HTTP.

This router only READS a trace-v1 directory that already exists on disk
(`<runs_root>/<run>/trace/gen<NNNN>/being<NN>/<profile>/`, PRD S5). Producing
one from `observation.jsonl` is S2's job -- a missing trace here is reported
as `404 {"error": "not produced"}`, never built on demand.

Validation point 2 of PRD S5 ("the loader ... checks every block's bytes
against the manifest's block table ... before drawing anything") is done by
`lab_api.trace.reference_decoder` and `lab_api.trace.check`, both S0 modules
this router calls rather than reimplements. The block-range route verifies a
block's whole-file hash once per process and caches the verdict (this
module's own `_verified_blocks`), so a scrub that requests many small tick
ranges from the same block does not re-hash the whole block on every request.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Response

from ..auth import current_who
from ..deps import get_settings
from ..settings import Settings
from ..trace import reference_decoder as rd

router = APIRouter(dependencies=[Depends(current_who)])

_CONTENT_TYPE = {
    "replay": "application/octet-stream",
    "genome": "application/octet-stream",
    "events": "application/json",
    "track": "application/json",
    "weights": "application/json",
}
_FILENAME = {
    "replay": "physical.replay",
    "genome": "genome.bin",
    "events": "events.json",
    "track": "track.json",
    "weights": "weights.json",
}


def _trace_dir(settings: Settings, run: str, gen: int, being: int, profile: str) -> Path:
    return Path(settings.runs_root) / run / "trace" / f"gen{gen:04d}" / f"being{being:02d}" / profile


def _load_manifest_or_404(trace_dir: Path) -> dict:
    if not (trace_dir / "manifest.json").is_file():
        raise HTTPException(status_code=404, detail={"error": "not produced"})
    try:
        return rd.load_manifest(trace_dir)
    except rd.ManifestValidationError as exc:
        raise HTTPException(
            status_code=500, detail={"error": f"manifest.json failed schema validation: {exc}"}
        ) from exc


# (neural.trace path, size, mtime_ns, block name) -> True once its bytes have been
# checked against manifest['blocks'][*]['sha256'] in this process. PRD S5: "the
# loader ... checks every block's bytes ... before drawing anything" -- done once,
# not on every tick-range request.
_verified_blocks: dict[tuple, bool] = {}


def _verify_block_once(trace_dir: Path, block: dict) -> None:
    neural_trace = trace_dir / "neural.trace"
    try:
        st = neural_trace.stat()
    except OSError as exc:
        raise HTTPException(status_code=404, detail={"error": f"neural.trace missing: {exc}"}) from exc
    key = (str(neural_trace), st.st_size, st.st_mtime_ns, block["name"])
    if _verified_blocks.get(key):
        return
    with open(neural_trace, "rb") as f:
        f.seek(block["offset"])
        raw = f.read(block["length"])
    if len(raw) != block["length"]:
        raise HTTPException(
            status_code=500,
            detail={"error": f"block {block['name']!r}: truncated neural.trace "
                              f"(expected {block['length']} bytes, got {len(raw)})"},
        )
    actual = hashlib.sha256(raw).hexdigest()
    if actual != block["sha256"]:
        raise HTTPException(
            status_code=500,
            detail={"error": f"block {block['name']!r}: sha256 mismatch -- manifest says "
                              f"{block['sha256']}, actual {actual}"},
        )
    _verified_blocks[key] = True


def _read_raw_slice(trace_dir: Path, block: dict, t0: int, t1: int) -> bytes:
    itemsize = np.dtype(rd.DTYPE_MAP[block["dtype"]]).itemsize
    row_elements = 1
    for d in block["shape"][1:]:
        row_elements *= d
    row_bytes = row_elements * itemsize
    with open(trace_dir / "neural.trace", "rb") as f:
        f.seek(block["offset"] + t0 * row_bytes)
        return f.read((t1 - t0) * row_bytes)


@router.get("/api/trace/{run}/{gen}/{being}/{profile}")
def get_manifest(run: str, gen: int, being: int, profile: str, settings: Settings = Depends(get_settings)) -> dict:
    trace_dir = _trace_dir(settings, run, gen, being, profile)
    return _load_manifest_or_404(trace_dir)


@router.get("/api/trace/{run}/{gen}/{being}/{profile}/block/{name}")
def get_block(
    run: str, gen: int, being: int, profile: str, name: str,
    t0: int | None = None, t1: int | None = None,
    settings: Settings = Depends(get_settings),
) -> Response:
    trace_dir = _trace_dir(settings, run, gen, being, profile)
    manifest = _load_manifest_or_404(trace_dir)

    block = next((b for b in manifest["blocks"] if b["name"] == name), None)
    if block is None:
        absent = {a["name"]: a["reason"] for a in manifest["absent"]}
        if name in absent:
            raise HTTPException(status_code=404, detail={"error": "not produced", "reason": absent[name]})
        raise HTTPException(status_code=404, detail={"error": f"no such block: {name}"})
    if block["compression"] != "none":
        raise HTTPException(
            status_code=500,
            detail={"error": f"compression {block['compression']!r} not supported by this server"},
        )

    count = block["shape"][0]
    lo = 0 if t0 is None else t0
    hi = count if t1 is None else t1
    if not (0 <= lo <= hi <= count):
        raise HTTPException(
            status_code=400,
            detail={"error": f"invalid sample range [{lo},{hi}) for block {name!r} with count {count}"},
        )

    _verify_block_once(trace_dir, block)
    raw = _read_raw_slice(trace_dir, block, lo, hi)
    return Response(content=raw, media_type="application/octet-stream")


@router.get("/api/trace/{run}/{gen}/{being}/{profile}/{artifact}")
def get_artifact(
    run: str, gen: int, being: int, profile: str, artifact: str,
    settings: Settings = Depends(get_settings),
) -> Response:
    if artifact not in _FILENAME:
        raise HTTPException(status_code=404, detail={"error": f"no such artifact: {artifact}"})
    trace_dir = _trace_dir(settings, run, gen, being, profile)
    manifest = _load_manifest_or_404(trace_dir)

    filename = _FILENAME[artifact]
    path = trace_dir / filename
    if not path.is_file():
        absent = {a["name"]: a["reason"] for a in manifest["absent"]}
        reason = absent.get(filename) or absent.get(artifact) or "file not present in this trace"
        raise HTTPException(status_code=404, detail={"error": "not produced", "reason": reason})

    return Response(content=path.read_bytes(), media_type=_CONTENT_TYPE[artifact])
