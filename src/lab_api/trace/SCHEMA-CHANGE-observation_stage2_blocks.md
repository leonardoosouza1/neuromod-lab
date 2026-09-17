# Proposed schema change: schema-2 stage blocks + `hashes.observed_genome[_file]`
(for `lab-ui/contract/trace-v1.schema.json`)

Coordinator task (2026-09-16): make the trace-v1 producer pack the new exact L1/L2
observation stages a new frozen `gpu_evolve` binary records (`observation_schema: 2` in
`driving.meta.json`; see `Universe/docs/KERNELS-OBSERVATION-L1L2.md`, especially §3 "the
nine exact stages" and §5 "metadata contract"). This is the schema patch for that, same
reason it could not be applied directly as the previous ones
(`SCHEMA-CHANGE-recorder_config.md`, `SCHEMA-CHANGE-counterfactual_valid.md`): this
worktree has no `lab-ui` checkout. **Do NOT edit the lab-ui repo from this worktree** --
this file is the exact patch to apply there; the vendored copy in this repo
(`src/lab_api/trace/trace-v1.schema.json`) already carries it, and an identical copy is
written to `/media/llm-data/scratch/obs2/trace-v1.schema.json` for the lab-ui side.

## The patch

### 1. `$defs.block.properties.name`: add an explicit `enum`

Additive in effect (every schema_version-1 manifest ever produced only ever used the
first nine names below, so nothing that validated before stops validating), but
**narrows** the schema going forward -- deliberately: the task's own requirement is
"contracts explicit and VALIDATED, mismatch must fail loudly," and an unconstrained
free-form block name silently accepts a typo. S0's own precedent
(`lab-ui/contract/DEVIATIONS.md` #7, repeated in this repo's `DEVIATIONS.md` #2) already
established that a stricter, non-widening addition does not need a `schema_version` bump
when it does not invalidate any real manifest -- confirmed here too (grep of every
`_BlockSpec(` call site in `producer.py`: only these 18 names have ever been written).

Replace:
```json
        "name": {
          "type": "string",
          "minLength": 1,
          "description": "Block identifier, stable across runs, e.g. 'retina', 'wave', 'cfc', 'raw_intent', 'after_head', 'after_modulation', 'final_command', 'pose', 'body'."
        },
```
with:
```json
        "name": {
          "type": "string",
          "minLength": 1,
          "enum": [
            "retina", "wave", "cfc", "raw_intent", "after_head", "after_modulation", "final_command", "pose", "body",
            "l1_matmul", "l1_effective", "l1_to_l2", "l2_matmul", "l2_effective", "l2_std", "l2_adapted", "bypass_adapted", "final_intent"
          ],
          "description": "Block identifier, stable across runs. The first nine are schema_version 1 (S0/S2). The last nine (added for observation_schema=2, see SCHEMA-CHANGE-observation_stage2_blocks.md) are the exact L1/L2 stage arrays Universe/docs/KERNELS-OBSERVATION-L1L2.md §3 names -- every value this producer has ever written into 'blocks[].name' is enumerated here on purpose (user requirement: an unlisted block name must fail schema validation loudly, not pass silently as an arbitrary string)."
        },
```

(`cfc_state`, one of the kernel doc's nine node names, is deliberately NOT one of the new
block names -- it duplicates the existing `cfc` block byte-for-byte; see the doc's §2 and
`producer.py::_STAGE2_BLOCK_NAMES`'s comment.)

### 2. `properties.hashes.properties`: add two OPTIONAL keys

`hashes` has `additionalProperties: false`, so (same situation as `recorder_config` and
`counterfactual_valid`) a new key MUST be declared here to be legal at all. **Do NOT**
add either to `hashes`' own `required` list -- every manifest produced before this change
(schema-1, and any schema-2 trace whose selected samples happen to lack `stages`) has
neither key.

Insert after `"neural_trace": { ... }` (before the closing `}` of `hashes.properties`):
```json
        "observed_genome": {
          "type": "string",
          "pattern": "^[0-9a-f]{64}$",
          "description": "OPTIONAL (added for observation_schema=2; see SCHEMA-CHANGE-observation_stage2_blocks.md in the neuromod-lab repo). sha256 (lowercase hex) of the exact genome file observation.jsonl's recorded samples name in their own 'genome_file' field (Universe/docs/KERNELS-OBSERVATION-L1L2.md §11) -- the genome that ACTUALLY produced the l1_matmul/l1_effective/l1_to_l2/l2_matmul/l2_effective/l2_std/l2_adapted/bypass_adapted/final_intent blocks below. Present only when this trace carries those schema-2 stage blocks; absent for every schema-1 trace, where weights.json keeps coming from 'checkpoint' (the generation's fitness champion) unchanged. May differ from 'checkpoint' -- the recorded being need not be the champion (see 'being_selection')."
        },
        "observed_genome_file": {
          "type": "string",
          "minLength": 1,
          "description": "OPTIONAL, present exactly when 'observed_genome' is present. The filename (relative to the run directory, e.g. 'observed_genome_gen0000.bin') that 'observed_genome' is the sha256 of."
        }
```

Neither change touches `schema_version` (top-level manifest field) -- `brain_schema_version`
(already an existing, versioned field for exactly this purpose, per its own description:
"Bumped whenever a stage's channel layout changes ... when the l1/l2/intent kernels
land") is bumped to `2` by `producer.py` instead, purely a code change, no schema.json
edit needed for that field (already `{"type":"integer","minimum":1}`, no enum).

## Why this exists (the evidence)

Real recording: `/media/llm-data/universe-runs/neuromod-lab-taxi/champ_nocost_s77_obs2_t8005/`
(binary `/media/llm-data/snapshots/gpu_evolve-bd5695f`), `driving.meta.json` declares
`"observation_schema": 2` and a `brain_graph` with the nine stage nodes; every one of its
3000 `observation.jsonl` rows carries a `stages` object with all nine arrays plus scalar
`l2_std`, and a `genome_file` field naming `observed_genome_gen0000.bin` (byte-identical,
99,184 bytes, to `evolve_best_gen0000.bin` in the same run -- confirmed by direct sha256
match, though the producer does NOT assume this in general; see `_stage_genome_info`'s
docstring for why it reads `genome_file` back out of the samples instead).
