"""Python reference decoder for the trace-v1 contract (lab-ui PRD S5).

Twin of `lab-ui/contract/decoder.js` -- both must decode the fixture at
`lab-ui/fixtures/trace-v1/universe-b2-gen0/` byte-for-byte identically. See
`neuromod-lab/tests/test_trace_contract.py`.

`jsonschema` is not installed in `.venv-rocm` and this task forbids
`pip install` (see `lab-ui/contract/DEVIATIONS.md` #4), so `load_manifest`
validates against `trace-v1.schema.json` with a small, hand-written
validator (`_validate` below) covering exactly the subset of JSON Schema
draft 2020-12 that `trace-v1.schema.json` actually uses: `type`, `const`,
`enum`, `required`, `additionalProperties`, `properties`, `items`,
`minItems`, `pattern`, `minimum`, and one level of `$ref`/`$defs` (the
`block` definition). It is NOT a general-purpose JSON Schema validator.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
from pathlib import Path
from typing import Any

import numpy as np

_SCHEMA_PATH = Path(__file__).with_name("trace-v1.schema.json")

DTYPE_MAP = {
    "u8": "<u1", "i8": "<i1", "u16": "<u2", "i16": "<i2",
    "u32": "<u4", "i32": "<i4", "f32": "<f4", "f64": "<f8",
}


class ManifestValidationError(ValueError):
    """Raised when a manifest fails validation against trace-v1.schema.json."""


class AbsentBlockError(LookupError):
    """Raised by read_block() for a block manifest['absent'] lists as not recorded.

    Deliberately NOT a KeyError: "this block was never written, see 'reason'"
    is a different condition from "this key does not exist in a mapping",
    and callers that only catch KeyError (e.g. a generic dict-like access
    pattern) should not accidentally swallow it.
    """

    def __init__(self, name: str, reason: str):
        self.name = name
        self.reason = reason
        super().__init__(f"block {name!r} is absent: {reason}")


class BlockIntegrityError(ValueError):
    """Raised when a block's (or the whole file's) sha256 does not match the manifest.

    PRD S5, validation point 2: "the loader in lab-ui checks every block's
    bytes against the manifest's block table ... before drawing anything."
    """


def _validate_type(value: Any, type_spec, path: str) -> None:
    types = type_spec if isinstance(type_spec, list) else [type_spec]
    ok = False
    for t in types:
        if t == "object" and isinstance(value, dict):
            ok = True
        elif t == "array" and isinstance(value, list):
            ok = True
        elif t == "string" and isinstance(value, str):
            ok = True
        elif t == "integer" and isinstance(value, int) and not isinstance(value, bool):
            ok = True
        elif t == "number" and isinstance(value, (int, float)) and not isinstance(value, bool):
            ok = True
        elif t == "null" and value is None:
            ok = True
        elif t == "boolean" and isinstance(value, bool):
            ok = True
    if not ok:
        raise ManifestValidationError(f"{path}: expected type {type_spec}, got {type(value).__name__}: {value!r}")


def _validate(value: Any, schema: dict, defs: dict, path: str = "$") -> None:
    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            raise ManifestValidationError(f"{path}: unsupported $ref {ref!r} (only local #/$defs/ refs are handled)")
        schema = defs[ref[len("#/$defs/"):]]

    if "const" in schema and value != schema["const"]:
        raise ManifestValidationError(f"{path}: expected const {schema['const']!r}, got {value!r}")
    if "enum" in schema and value not in schema["enum"]:
        raise ManifestValidationError(f"{path}: {value!r} not in enum {schema['enum']}")
    if "type" in schema:
        _validate_type(value, schema["type"], path)
    if "pattern" in schema and isinstance(value, str) and not re.match(schema["pattern"], value):
        raise ManifestValidationError(f"{path}: {value!r} does not match pattern {schema['pattern']!r}")
    if "minimum" in schema and isinstance(value, (int, float)) and value < schema["minimum"]:
        raise ManifestValidationError(f"{path}: {value} < minimum {schema['minimum']}")
    if "minItems" in schema and isinstance(value, list) and len(value) < schema["minItems"]:
        raise ManifestValidationError(f"{path}: length {len(value)} < minItems {schema['minItems']}")

    if isinstance(value, dict) and schema.get("type") == "object":
        for key in schema.get("required", []):
            if key not in value:
                raise ManifestValidationError(f"{path}: missing required property {key!r}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(value) - set(props)
            if extra:
                raise ManifestValidationError(f"{path}: additional properties not allowed: {sorted(extra)}")
        for key, subschema in props.items():
            if key in value:
                _validate(value[key], subschema, defs, f"{path}.{key}")

    if isinstance(value, list) and schema.get("type") == "array" and "items" in schema:
        for i, item in enumerate(value):
            _validate(item, schema["items"], defs, f"{path}[{i}]")


def load_schema() -> dict:
    with open(_SCHEMA_PATH) as f:
        return json.load(f)


def validate_manifest(manifest: dict, schema: dict | None = None) -> None:
    """Raises ManifestValidationError on the first violation found."""
    schema = schema or load_schema()
    defs = schema.get("$defs", {})
    _validate(manifest, schema, defs)

    # Cross-field checks the JSON Schema subset above cannot express.
    if len(manifest["samples_tick"]) != manifest["count"]:
        raise ManifestValidationError(
            f"samples_tick has {len(manifest['samples_tick'])} entries, manifest.count is {manifest['count']}"
        )
    for block in manifest["blocks"]:
        if block["shape"][0] != manifest["count"]:
            raise ManifestValidationError(
                f"block {block['name']!r}: shape[0]={block['shape'][0]} != manifest.count={manifest['count']}"
            )
        n_elements = 1
        for dim in block["shape"]:
            n_elements *= dim
        itemsize = np.dtype(DTYPE_MAP[block["dtype"]]).itemsize
        expected_length = n_elements * itemsize
        if block["compression"] == "none" and block["length"] != expected_length:
            raise ManifestValidationError(
                f"block {block['name']!r}: length={block['length']} != "
                f"product(shape)*itemsize={expected_length}"
            )


def load_manifest(path: str | Path) -> dict:
    """Loads and validates manifest.json.

    `path` may be a trace-v1 directory (manifest.json is read from inside it)
    or the manifest.json file itself.
    """
    path = Path(path)
    manifest_path = path / "manifest.json" if path.is_dir() else path
    with open(manifest_path) as f:
        manifest = json.load(f)
    validate_manifest(manifest)
    return manifest


def _resolve(trace_dir: str | Path, manifest: dict | None):
    trace_dir = Path(trace_dir)
    if manifest is None:
        manifest = load_manifest(trace_dir)
    return trace_dir, manifest


def read_block(
    trace_dir: str | Path,
    name: str,
    t0: int | None = None,
    t1: int | None = None,
    manifest: dict | None = None,
    verify: bool = True,
) -> np.ndarray:
    """Reads block `name` from `<trace_dir>/neural.trace`, sliced to samples [t0, t1).

    `t0`/`t1` index into the sample axis (0..manifest['count']), NOT tick
    numbers -- use `manifest['samples_tick']` to translate a tick to a sample
    index. Returns a numpy array shaped `(t1-t0,) + shape[1:]` with the
    block's declared dtype (scaled by `block['scale']` when it is not 1.0,
    which promotes the result to float64).

    `verify` (default `True`, PRD S5 validation point 2): reads the block's
    ENTIRE byte range from disk and checks its sha256 against
    `block['sha256']` before slicing out [t0, t1) -- this costs a full read
    of the block even for a small tick range, but a corrupted byte anywhere
    in the block must not be silently returned just because it falls
    outside the requested slice. Raises `BlockIntegrityError` on mismatch,
    naming the block and both hashes. Pass `verify=False` for a fast,
    unchecked partial read (e.g. a range loader that has already verified
    the file once via `lab_api.trace.check`).

    Raises `AbsentBlockError` if the block is not in `manifest['blocks']`
    but IS listed in `manifest['absent']`; raises `KeyError` if it is in
    neither (a manifest inconsistency, not a normal "not recorded" case).
    """
    trace_dir, manifest = _resolve(trace_dir, manifest)
    block = next((b for b in manifest["blocks"] if b["name"] == name), None)
    if block is None:
        absent = {a["name"]: a["reason"] for a in manifest["absent"]}
        if name in absent:
            raise AbsentBlockError(name, absent[name])
        raise KeyError(f"block {name!r} not found in manifest and not listed as absent")
    if block["compression"] != "none":
        raise NotImplementedError(f"compression {block['compression']!r} not supported by this reference decoder")

    dtype = np.dtype(DTYPE_MAP[block["dtype"]])
    shape = tuple(block["shape"])
    count = shape[0]
    row_elements = 1
    for d in shape[1:]:
        row_elements *= d

    t0 = 0 if t0 is None else t0
    t1 = count if t1 is None else t1
    if not (0 <= t0 <= t1 <= count):
        raise ValueError(f"invalid sample range [{t0},{t1}) for block {name!r} with count {count}")

    if verify:
        with open(trace_dir / "neural.trace", "rb") as f:
            f.seek(block["offset"])
            whole_block_raw = f.read(block["length"])
        if len(whole_block_raw) != block["length"]:
            raise BlockIntegrityError(
                f"block {name!r}: expected {block['length']} bytes at offset {block['offset']}, "
                f"got {len(whole_block_raw)} (file truncated?)"
            )
        actual_sha256 = hashlib.sha256(whole_block_raw).hexdigest()
        if actual_sha256 != block["sha256"]:
            raise BlockIntegrityError(
                f"block {name!r}: sha256 mismatch -- manifest says {block['sha256']}, "
                f"actual bytes hash to {actual_sha256}"
            )
        row_bytes = row_elements * dtype.itemsize
        raw = whole_block_raw[t0 * row_bytes: t1 * row_bytes]
    else:
        n_elements = (t1 - t0) * row_elements
        with open(trace_dir / "neural.trace", "rb") as f:
            f.seek(block["offset"] + t0 * row_elements * dtype.itemsize)
            raw = f.read(n_elements * dtype.itemsize)
        if len(raw) != n_elements * dtype.itemsize:
            raise ValueError(
                f"block {name!r}: expected {n_elements * dtype.itemsize} bytes for range [{t0},{t1}), got {len(raw)}"
            )

    arr = np.frombuffer(raw, dtype=dtype).reshape((t1 - t0,) + shape[1:])
    if block["scale"] != 1.0:
        arr = arr.astype("<f8") * block["scale"]
    return arr


def verify_neural_trace_hash(trace_dir: str | Path, manifest: dict | None = None) -> None:
    """Checks manifest['hashes']['neural_trace'] against the whole neural.trace file.

    Raises BlockIntegrityError on mismatch. This is the cheap, whole-file
    check to run before trusting any per-block offset/length/sha256 in the
    block table (PRD S5 validation point 2) -- read_block() re-hashes only
    the block it is asked for, so a corruption outside every requested
    block's range would otherwise go unnoticed until (if ever) that part of
    the file is read.
    """
    trace_dir, manifest = _resolve(trace_dir, manifest)
    trace_path = trace_dir / "neural.trace"
    actual = hashlib.sha256(trace_path.read_bytes()).hexdigest()
    expected = manifest["hashes"]["neural_trace"]
    if actual != expected:
        raise BlockIntegrityError(
            f"{trace_path}: sha256 mismatch -- manifest says {expected}, actual file hashes to {actual}"
        )


# ---------------------------------------------------------------------------
# .replay decoder -- layout from Universe/src/replay.rs, byte offsets verified
# in lab-ui/contract/REPLAY-FORMAT.md. Independent of neural.trace: this is
# the `physical.replay` artifact, produced by Universe, not by the S2 trace
# producer.
# ---------------------------------------------------------------------------

REPLAY_HEADER_SIZE = 64
REPLAY_ENTRY_SIZE = 130
REPLAY_FRAME_SIZE = 128
REPLAY_MAGIC = b"IARARPLY"

# Little-endian struct format for one ReplayFrame (128 bytes). Field order and
# byte offsets verified against Universe/src/replay.rs -- see
# lab-ui/contract/REPLAY-FORMAT.md for the offset table this mirrors.
_FRAME_STRUCT = struct.Struct(
    "<"
    "3f"  # pos[3]           0..12
    "2f"  # fwd[2]           12..20
    "f"   # speed            20..24
    "f"   # yaw_rate         24..28
    "f"   # arc_prog         28..32
    "H"   # laps             32..34
    "B"   # gear             34..35
    "B"   # hp_norm          35..36
    "B"   # fuel_norm        36..37
    "3x"  # _alignment       37..40
    "I"   # tick             40..44
    "f"   # dist_wall_l      44..48
    "f"   # dist_wall_r      48..52
    "f"   # dist_wall_f      52..56
    "f"   # curv_40m         56..60
    "f"   # curv_70m         60..64
    "f"   # curv_120m        64..68
    "f"   # flow_align       68..72
    "f"   # line_offset      72..76
    "f"   # intent_thr       76..80
    "f"   # intent_str       80..84
    "f"   # intent_brk       84..88
    "f"   # final_thr        88..92
    "f"   # final_str        92..96
    "f"   # final_brk        96..100
    "B"   # dims_saturated   100..101
    "B"   # intent_mag_q     101..102
    "B"   # axiom_str_q      102..103
    "B"   # safety_flags     103..104
    "8b"  # retina_fov[8]    104..112
    "8b"  # retina_peri[8]   112..120
    "8x"  # _pad             120..128
)
assert _FRAME_STRUCT.size == REPLAY_FRAME_SIZE, _FRAME_STRUCT.size

_FLAT_FIELDS = (
    ["pos_x", "pos_y", "pos_z", "fwd_x", "fwd_z", "speed", "yaw_rate", "arc_prog",
     "laps", "gear", "hp_norm", "fuel_norm", "tick",
     "dist_wall_l", "dist_wall_r", "dist_wall_f",
     "curv_40m", "curv_70m", "curv_120m", "flow_align", "line_offset",
     "intent_thr", "intent_str", "intent_brk",
     "final_thr", "final_str", "final_brk",
     "dims_saturated", "intent_mag_q", "axiom_str_q", "safety_flags"]
    + [f"retina_fov_{i}" for i in range(8)]
    + [f"retina_peri_{i}" for i in range(8)]
)


def read_replay_header(path: str | Path) -> dict:
    with open(path, "rb") as f:
        header = f.read(REPLAY_HEADER_SIZE)
    if len(header) != REPLAY_HEADER_SIZE:
        raise ValueError(f"{path}: file shorter than the {REPLAY_HEADER_SIZE}-byte header")
    magic = header[0:8]
    if magic != REPLAY_MAGIC:
        raise ValueError(f"{path}: bad magic {magic!r}, expected {REPLAY_MAGIC!r}")
    version, source, n_beings = struct.unpack_from("<HBB", header, 8)
    if version != 1:
        raise ValueError(f"{path}: unsupported replay version {version} (expected 1)")
    tick_rate, = struct.unpack_from("<f", header, 12)
    world_seed, = struct.unpack_from("<Q", header, 16)
    return {
        "magic": magic.decode("ascii"),
        "version": version,
        "source": source,
        "n_beings": n_beings,
        "tick_rate": tick_rate,
        "world_seed": world_seed,
    }


def read_replay(path: str | Path, being: int | None = None) -> tuple[dict, list[dict]]:
    """Decodes a `.replay` file fully.

    Returns `(header, frames)`. `frames` is a list of dicts, one per recorded
    (being, tick) entry, in file order (grouped by tick, all beings per tick
    -- see REPLAY-FORMAT.md). Pass `being` to keep only that being's frames.
    """
    path = Path(path)
    data = path.read_bytes()
    header = read_replay_header(path)
    body = data[REPLAY_HEADER_SIZE:]
    if len(body) % REPLAY_ENTRY_SIZE != 0:
        raise ValueError(f"{path}: body length {len(body)} is not a multiple of {REPLAY_ENTRY_SIZE}")

    frames = []
    n_entries = len(body) // REPLAY_ENTRY_SIZE
    for i in range(n_entries):
        off = i * REPLAY_ENTRY_SIZE
        tag = body[off]
        idx = body[off + 1]
        if tag != 0xFE:
            raise ValueError(f"{path}: entry {i} has bad frame_tag 0x{tag:02x} (expected 0xFE)")
        if idx >= header["n_beings"]:
            raise ValueError(f"{path}: entry {i} has being_idx {idx} >= n_beings {header['n_beings']}")
        if being is not None and idx != being:
            continue
        frame_bytes = body[off + 2: off + 2 + REPLAY_FRAME_SIZE]
        values = _FRAME_STRUCT.unpack(frame_bytes)
        frame = dict(zip(_FLAT_FIELDS, values))
        frame["being_idx"] = idx
        frame["pos"] = [frame.pop("pos_x"), frame.pop("pos_y"), frame.pop("pos_z")]
        frame["fwd"] = [frame.pop("fwd_x"), frame.pop("fwd_z")]
        frame["retina_fov"] = [frame.pop(f"retina_fov_{i}") for i in range(8)]
        frame["retina_peri"] = [frame.pop(f"retina_peri_{i}") for i in range(8)]
        frames.append(frame)
    return header, frames
