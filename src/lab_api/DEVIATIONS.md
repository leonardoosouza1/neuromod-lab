# Deviations between the PRD/contract and what S2's code actually does

Per the task rule: when the PRD (or the S0 contract it produced) and the code disagree,
the code wins, and the disagreement is written down here rather than silently "fixed"
without a trace. S0's own `lab-ui/contract/DEVIATIONS.md` is a separate, earlier file
(read-only from S2's worktree -- S2 has no `lab-ui` checkout) documenting S0's own
findings; this file is S2's continuation of the same practice, for `neuromod-lab`.

## 1. `check.py`'s tick-monotonicity check did not account for generation boundaries

`check_run` (`src/lab_api/trace/check.py`) asserted `tick > prev_tick` across the ENTIRE
`observation.jsonl` file, with no regard for the `generation` field. That is correct
within one generation but wrong across a boundary: `DrivingDiagnostics::reset`
(`Universe/src/bin/gpu_evolve/driving_diagnostics.rs`) sets `first_tick = 1` at the start
of every generation, so a real multi-generation run's tick counter legitimately drops
(e.g. from `12000` back to `16`) every time `generation` increments. S0's own fixture and
its `fake_run` test data never exercised this because both were single-generation.

Found running the S2 producer against a real finished multi-generation run
(`b5_ctrl_s31`, 25 generations, `observation.jsonl` has 18750 lines): `check_run` raised
`sample 750: tick 16 does not increase over the previous sample's tick 12000` on the very
first generation boundary -- a false positive, not a real data problem (verified:
`observation.jsonl` sample 749 has `generation:0, tick:12000`; sample 750 has
`generation:1, tick:16`).

Fixed (this task) by tracking `prev_tick`/`prev_generation` together and only asserting
monotonicity when `generation == prev_generation`. Covered by the pre-existing
`tests/test_trace_contract.py` (still green) plus the real multi-generation smoke in
`tests/test_trace_producer.py`.

## 2. `trace-v1.schema.json`'s `blocks` array required `minItems: 1`, which the PRD's own
   `summary` profile cannot satisfy

PRD §3 defines profile `summary` as "replay + events only" and §6/§5 by extension implies
`neural.trace` carries no blocks for it. The vendored schema copy
(`src/lab_api/trace/trace-v1.schema.json`, copied from `lab-ui/contract/` by S0) required
`blocks.length >= 1`, so a correctly-empty `summary` manifest fails schema validation --
found producing a real `summary`-profile trace end to end (`test_trace_producer.py`).

Fixed (this task) by relaxing `minItems` to `0` in the VENDORED copy only
(`src/lab_api/trace/trace-v1.schema.json`) -- this worktree has no `lab-ui` checkout, so
the canonical `lab-ui/contract/trace-v1.schema.json` was not touched. **Whoever merges S2
or next touches the canonical schema should apply the identical one-line change** (`
"blocks": {"type": "array", "minItems": 0, ...}`) there too, or every future `summary`
producer output will keep failing lab-ui's own loader. This is schema-widening only
(every manifest that validated before, with `blocks.length >= 1`, still validates) --
`schema_version` was not bumped, matching S0's own precedent for a non-breaking schema
fix (`lab-ui/contract/DEVIATIONS.md` #7 made the same call for a stricter addition).

## 3. `disabled_flags` covers FOUR P1.7 control-arm flags, not three

`trace-v1.schema.json`'s prose for `disabled_flags` names
`--no-neuron-memory, --no-neuron-threshold, --no-heterogeneous-activation`.
`Universe/src/bin/gpu_evolve/cli_flags.rs:100-103` defines a fourth, independent one:
`--no-neuron-period` ("freeze the per-neuron period of L1"). The producer
(`producer.py::DISABLED_FLAG_NAMES`) checks all four against the run's own
`manifest.json` `command` list; a manifest whose run passed `--no-neuron-period` alone
would otherwise silently lose that fact. Not a schema change (the field is a free-form
string array), just a correction to which flags this producer looks for.

## 4. `weights.json`'s `brain_flow` is the genome's ON-DISK block order, not the per-tick
   kernel dispatch order

The PRD (S2 task text) asks the Universe genome exporter for "`brain_flow` (the stage
names in order, from the code)". There is no literal `brain_flow` array anywhere in the
Rust code for the GENOME (there is a `brain_flow`-shaped concept for `neural.trace`'s
per-tick BLOCKS, i.e. sensor -> wave -> cfc -> raw_intent -> ... -> body, which
`producer.py`'s `_block_specs` order reproduces). For the genome's own stage list,
`genome_export`'s `brain_flow` is `universe::gpu::genome_io.rs`'s own on-disk block
order (l1, l2, kan_knots, slow_*, tau, sensors, neuron_*, gates_w, hip, fly) --
the one place that layout is documented as canonical ("DO NOT reorder"). This is
explicitly NOT the same as the per-tick dispatch order (tau feeds the CfC before L1
runs; kan_knots is applied on the HOST after L1+L2, to raw_intent; slow_* is a parallel
GPU kernel pair alongside brain.wgsl, not sequential with it) -- `weights.json` itself
carries a `brain_flow_note` field saying this in the same words, and
`Universe/src/bin/genome_export.rs`'s module doc says it too.

## 5. `brain_step` stops at `raw_intent`, not `final_command`

See `Universe/src/bin/brain_step.rs`'s module doc for the full reasoning: the chain from
`raw_intent` onward (`after_head`/`after_modulation`/`final_command`) is produced by
`map_native_action` (`Universe/src/bin/gpu_evolve/native_action.rs`), a pure, already-CPU,
already-tested function this task says to call rather than reimplement -- but it lives in
the `gpu_evolve` BINARY crate, not the `universe` LIBRARY crate, so a separate CPU-only
binary cannot `use` it without either moving it into the library (a real API change, not
done here without sign-off) or copying its logic (which "do NOT reimplement the brain in
a second place" forbids). `raw_intent` is also the PRD's own literal acceptance target
("the reference forward's motor intent must match the recorded `raw_intent` block"), so
this is not a scope cut against the spec.

## 6. `brain_step`'s forward pass has two documented, un-tuned approximations

Both are in `Universe/src/bin/brain_step.rs`'s module doc, repeated here because they
directly explain the S2 acceptance numbers (see `TESTING.md`):

- **No persistent output fatigue.** `src/engine.rs::execute_cycle`'s final combination
  step depends on `out_fatigue`, state accumulated over many prior ticks that a single
  offline sample does not carry. `brain_step` uses `out_fatigue=0` for every call
  (equivalent to `tanh(raw*2.0)` with no shrinkage).
- **P1.7 neuron mechanisms (memory/period/threshold/heterogeneous activation) are not
  applied.** `genome_export` exports `neuron_alpha_*`/`neuron_period_l1`/
  `neuron_threshold_l1`/`neuron_activation_*` as genome stages (so they are visible), but
  `brain_step`'s forward composes plain `BitLinear`/`FloatLinear`/`CfCCell` calls only --
  it does not gate L1's activation by these per-neuron mechanisms the way production
  `brain.wgsl` does when a run's `disabled_flags` is empty (i.e. when the mechanisms are
  ACTIVE, not disabled). For a run whose `disabled_flags` is non-empty for all four P1.7
  flags, this approximation does not apply; none of the runs tested here disabled all
  four.

Per the task's own instruction ("If it does not match, say so with the numbers and your
best diagnosis -- do NOT tune until it matches"), neither approximation was closed by
trial and error. See `TESTING.md`'s `brain_step --batch` section for the measured
max/mean absolute error and the third, independent candidate cause (being/genome identity
-- `lab-ui/contract/DEVIATIONS.md` #2, repeated below).

## 7. Being/genome identity is unverified for every non-`--resume` run (inherited from S0)

`lab-ui/contract/DEVIATIONS.md` #2 already documents this for the S0 fixture; it applies
identically to every trace this producer makes from a run that did not pass `--resume`
(all of the `b3_*`/`b5_*` runs tested here except `b3_fixed_s31_t8005`, which did). The
producer's `being_selection` text (`producer.py::_being_selection_text`) states this
honestly per-trace instead of writing "champion" -- see its three branches (explicit
`--being` override / `--resume` / no `--resume`).

## 9. `dist_wall_f`/`dist_wall_l`/`dist_wall_r`'s real cap is 50 m, not 30 m -- and the
   same recorded value means something different on the two wall-probe code paths

Found by S4 building the micro panels against real S2-produced traces: `dist_wall_f ==
50.0` cannot be told apart from "a real wall 50 m away" (continuous probe) vs "nothing
found -- the probe only reached 30 m" (legacy probe) without knowing which code path
recorded it. `lab-ui/contract/REPLAY-FORMAT.md`'s `ReplayFrame` field table documents
`dist_wall_f` as "front wall distance (m, cap 30)" -- inherited from a stale comment in
`Universe/src/replay.rs`, not verified against the actual probe code. The real cap
EVERY caller clamps to is 50 m (`Universe/src/bin/gpu_evolve/wall_probes.rs:91`,
`distance(grid, size, cell_size_m, position, forward, 50.0, true)`, called identically
whether `continuous_wall_probes()` (`statics.rs:101`) is true or false); only the LEGACY
probe's real reach is 30 m, below which its readings are genuine and above which
(including its own 50.0 "nothing found" sentinel) they are not.

Fixed (this task) by adding `recorder_config` to the manifest (see #10 below and
`SCHEMA-CHANGE-recorder_config.md`), carrying `wall_probe_kind`
(`"continuous"`/`"legacy"`), `wall_probe_max_m` (50.0, always), and
`wall_probe_reach_m` (30.0, only present when `wall_probe_kind=="legacy"`). The
`REPLAY-FORMAT.md` correction itself is proposed, not applied, in
`SCHEMA-CHANGE-recorder_config.md`'s "Also fix while touching this area" section --
`REPLAY-FORMAT.md` lives in `lab-ui/contract/`, not in this worktree.

## 10. `recorder_config`: a new, OPTIONAL top-level manifest object

PRD S5's manifest field list does not include a general "which code path recorded this"
object -- it has `disabled_flags` for the four P1.7 control-arm flags specifically, and
nothing broader. #9 above is the concrete motivating case, but the same ambiguity
applies to any of the several documented dual-code-path fields in `driving.meta.json`
(`slow_kinematics: legacy|canonical`, `motor_head: linear|spline`,
`throttle_arbitration: legacy|signed`, `reverse_controller: legacy|v2`,
`retina_geometry: legacy|physical-v1`, plus the retina/FOV/sampling constants a panel
needs to draw the retina and ray-fan correctly without hardcoding Universe's own
`config.rs`). `producer.py::_recorder_config` copies these verbatim out of
`driving.meta.json` (the recorder's own declaration, already trusted for validation --
`check.check_sample`) into one new manifest object, `recorder_config`. It is added to
the vendored schema copy's `properties` but deliberately NOT to `required`, because the
schema's `additionalProperties: false` makes this a real schema change, and an object
that predates it (including the S0 fixture, which this worktree cannot regenerate) must
stay valid. See `SCHEMA-CHANGE-recorder_config.md` for the exact patch to apply to the
canonical `lab-ui/contract/trace-v1.schema.json`, and
`tests/test_trace_contract.py::test_vendored_schema_diverges_from_lab_ui_contract_only_by_documented_s2_additions`
for the test that pins the gap until that patch lands.

## 11. `track.json` exports only the FIRST configured track seed for a run with track
   rotation

`producer.py::produce` reads `run_manifest['args']['tracks'][0]`. Every run tested here
(`b3_*`, `b5_ctrl_*`, `b5_gate_*`) has exactly one track seed, so this was never
exercised against a real rotating run (`b5_rot_*`, in flight during this task, explicitly
off-limits). A future rotating run needs a real per-generation seed lookup, not a single
fixed index; until then this is a known, narrow gap, not a silent wrong answer (single
-track runs -- the only ones this producer has been run against -- are unaffected).
