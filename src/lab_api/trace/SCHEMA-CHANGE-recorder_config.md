# Proposed schema change: `recorder_config` (for `lab-ui/contract/trace-v1.schema.json`)

Found by S4 while building the micro panels against real S2-produced traces: a panel
cannot tell whether `physical.replay`'s `dist_wall_f == 50.0` means "a real wall 50 m
away" or "nothing found -- the legacy probe only reaches 30 m" without knowing which
code path (`Universe/src/bin/gpu_evolve/statics.rs::continuous_wall_probes()`) recorded
it. `lab-ui/contract/REPLAY-FORMAT.md` itself documents `dist_wall_f` as "cap 30m",
inherited from a stale comment in `Universe/src/replay.rs` -- the real cap the field is
clamped to is 50 m (`Universe/src/bin/gpu_evolve/wall_probes.rs:91`,
`distance(..., 50.0, true)`, called by BOTH probe kinds); only the LEGACY probe's real
reach is 30 m. See `src/lab_api/DEVIATIONS.md` #9 in this repo for the full writeup.

**This worktree (`neuromod-lab-s2-pack`) has no `lab-ui` checkout**, so the canonical
`lab-ui/contract/trace-v1.schema.json` could not be edited directly. This file is the
exact patch to apply there. The VENDORED copy in this repo
(`src/lab_api/trace/trace-v1.schema.json`) already has this change (plus the unrelated
`blocks.minItems` fix from `DEVIATIONS.md` #2) -- `tests/test_trace_contract.py`'s
`test_vendored_schema_diverges_from_lab_ui_contract_only_by_documented_s2_additions`
documents and pins the exact diff instead of asserting byte-identity, and says to delete
itself (restoring the plain byte-identity test) once the canonical copy is patched.

## The patch

Add ONE new property to the top-level `properties` object (schema has
`additionalProperties: false` at the top level, so a new field MUST be declared here to
be legal at all). **Do NOT add `recorder_config` to the top-level `required` array** --
it must stay optional, or every manifest produced before this schema version (including
the S0 fixture, `lab-ui/fixtures/trace-v1/universe-b2-gen0/manifest.json`, which this
worktree cannot regenerate) would fail validation retroactively.

Insert after `"disabled_flags": { ... }` (before the closing `},` of `properties`, i.e.
still inside `properties`, as a sibling of `disabled_flags`):

```json
    "recorder_config": {
      "type": "object",
      "description": "OPTIONAL. Copies the recorder's own code-path configuration out of driving.meta.json so a panel can tell apart two historically different behaviours that produce the SAME recorded number -- e.g. dist_wall_f == 50.0 means a real 50 m reading on the continuous wall probe but a 'nothing found within reach' sentinel on the legacy stepped probe, whose real reach is only 30 m. A manifest without this object predates this addition or was produced by a producer that has not adopted it yet; treat every field as unknown, not as a specific value, in that case.",
      "properties": {
        "wall_probes": { "type": "string", "enum": ["continuous", "legacy"] },
        "wall_probe_kind": { "type": "string", "enum": ["continuous", "legacy", "unknown"], "description": "Same value as 'wall_probes' when known; 'unknown' if driving.meta.json lacked it. Kept as a separate, always-present field so a consumer never has to fall back to a missing 'wall_probes'." },
        "wall_probe_max_m": { "type": "number", "description": "The cap ReplayFrame.dist_wall_f/l/r is clamped to either way (Universe/src/bin/gpu_evolve/wall_probes.rs, the distance(...) call every caller passes 50.0 to). 50.0 in every run measured so far." },
        "wall_probe_reach_m": { "type": "number", "description": "Present only when wall_probe_kind=='legacy': the legacy stepped probe's real reach (30 m). A recorded value >= this is the 'nothing found' sentinel (wall_probe_max_m), not a real distance between this and wall_probe_max_m." },
        "slow_kinematics": { "type": "string" },
        "motor_head": { "type": "string" },
        "throttle_arbitration": { "type": "string" },
        "reverse_controller": { "type": "string" },
        "retina_geometry": { "type": "string" },
        "retina_encoding": { "type": "string" },
        "fov_degrees": { "type": "number" },
        "retina_rows": { "type": "integer" },
        "retina_cols": { "type": "integer" },
        "retina_pitch_radians": { "type": "array", "items": { "type": "number" } },
        "sample_every": { "type": "integer" },
        "road_view_calibration_version": {}
      }
    }
```

Also apply the unrelated, already-shipped `blocks.minItems` fix (`DEVIATIONS.md` #2) in
the same commit if it has not landed yet, and the `disabled_flags` description wording
fix (`DEVIATIONS.md` #3: add `--no-neuron-period` to the flag list in that field's
`description`, a real 4th control-arm flag the original prose omitted). All three are
additive/non-breaking (the third is wording-only, no validation behaviour changes) --
S0's own precedent (`lab-ui/contract/DEVIATIONS.md` #7) is not to bump `schema_version`
for this class of change, so none of these three do either.

## Also fix while touching this area

`lab-ui/contract/REPLAY-FORMAT.md`'s `ReplayFrame` field table, `dist_wall_f` row, says
"front wall distance (m, cap 30)". Change to "front wall distance (m, cap 50; the LEGACY
wall-probe code path's real reach is only 30 m -- see trace-v1's `recorder_config.
wall_probe_reach_m` when `wall_probe_kind=='legacy'`, and `dist_wall_l`/`dist_wall_r`
rows should get the same correction, they share the same `distance(..., 50.0, true)`
call site)".

## Example: `recorder_config` as produced by this task's producer, real run

From `/media/llm-data/universe-runs/neuromod-lab-taxi/b5_ctrl_s31/trace/gen0024/being00/champion/manifest.json`:

```json
"recorder_config": {
  "slow_kinematics": "canonical",
  "motor_head": "spline",
  "throttle_arbitration": "signed",
  "reverse_controller": "v2",
  "retina_geometry": "legacy",
  "retina_encoding": "u32: material low byte, distance_mm upper 24 bits",
  "fov_degrees": 120.0,
  "retina_rows": 14,
  "retina_cols": 126,
  "retina_pitch_radians": [ -0.012, -0.0157, ... ],
  "sample_every": 16,
  "road_view_calibration_version": 2,
  "wall_probe_kind": "continuous",
  "wall_probe_max_m": 50.0
}
```

(`wall_probe_reach_m` is absent here because `wall_probe_kind` is `"continuous"`, not
`"legacy"` -- every run produced during this task used the continuous probe.)
