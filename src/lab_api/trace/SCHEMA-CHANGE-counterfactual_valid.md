# Proposed schema change: `counterfactual_valid` (for `lab-ui/contract/trace-v1.schema.json`)

Coordinator follow-up to the S2 brain_step acceptance check (2026-09-16): "make the
producer refuse (or mark `counterfactual_valid: false` in the manifest) for traces whose
`being_selection` is not guaranteed to be the genome's owner." This is the schema patch
for that field, analogous to `SCHEMA-CHANGE-recorder_config.md` (same reason it could not
be applied directly: this worktree has no `lab-ui` checkout).

## The patch

Add ONE new property to the top-level `properties` object (as a sibling of
`recorder_config`, still inside `properties`, before the closing `},` of `properties`).
**Do NOT add it to the top-level `required` array** -- it must stay optional, for the
same reason as `recorder_config` (every manifest produced before this change, including
the S0 fixture, must stay valid).

```json
    "counterfactual_valid": {
      "type": "boolean",
      "description": "OPTIONAL. True only when 'being' is VERIFIED to own genome.bin's exact weights, so a Counterfactual / brain_step recomputation over weights.json + neural.trace is comparing the same individual to itself. Verified condition (2026-09-16): --resume --resume-mix 1 with being==the recorder's own selected_being==0 -- population slot 0 is unconditionally an exact, unmutated clone of the loaded checkpoint (Universe/src/bin/gpu_evolve/main.rs), confirmed by direct sha256 match against the source checkpoint for 4 real runs. A manifest without this field predates the check; treat as unverified (not necessarily invalid), same as false. IMPORTANT: true here says nothing about whether brain_step's reference forward currently reproduces the recorded raw_intent -- it does not yet, even for a verified-valid trace (Universe/docs/LAB-UI-S2-GENOME-EXPORT.md); this field is about genome OWNERSHIP, not about brain_step's own accuracy."
    }
```

## Why this exists (the evidence)

`Universe/src/bin/gpu_evolve/main.rs`, the `--resume` population seeding:

```rust
pop.push(best.clone()); // elite exato
// ... only AFTER this, for the REMAINING slots:
while pop.len() < n_seres {
    let mut filho = best.clone();
    for w in filho.l1.iter_mut() { *w *= mix; }
    for w in filho.l2.iter_mut() { *w *= mix; }
    pop.push(filho);
}
```

Population slot 0 is `best.clone()` with **no scaling applied at all** -- unconditionally,
regardless of `--resume-mix`'s value. Confirmed by direct `sha256sum` of
`<run>/evolve_best_gen0000.bin` against its source checkpoint
(`/media/llm-data/snapshots/b1-champions/<arm>_s<seed>.bin`, per
`neuromod-lab/scripts/enqueue_b3_b2.py`'s own B3 recipe) for 4 real `--resume
--resume-mix 1` runs:

| run | source champion | match |
|---|---|---|
| `b3_fixed_s31_t8005` | `b1_fixed_s31.bin` | `3417a549...c117045` -- byte-identical |
| `b3_legacy_s31_t8005` | `b1_legacy_s31.bin` | `7ba04537...aa36dc775` -- byte-identical |
| `b3_fixed_s113_t8200` | `b1_fixed_s113.bin` | `77e3a0c5...ab2e7fda45` -- byte-identical |
| `b3_legacy_nocost_s77_t8005` | `b1_legacy_nocost_s77.bin` | `ed72e4d3...985b1f3770` -- byte-identical |

(hashes truncated for width; exact commands in `Universe/docs/LAB-UI-S2-GENOME-EXPORT.md`)

`--resume-mix < 1` is deliberately NOT marked valid: the code path is the same
unconditional `pop.push(best.clone())` for slot 0, so it is very likely also exact, but
this producer only claims what it directly verified, and mix<1 was not tested.

## Also proposed: producer refusal vs. marking

The coordinator offered either "refuse" or "mark false" as acceptable. This
implementation chose MARKING (`counterfactual_valid: false`), not refusing production,
because a trace with unverified genome ownership is still fully useful for every OTHER
panel (Track 2D, retina, Stages, Pedals+chain, Sensor coverage, Ghost, ...) -- only the
Counterfactual panel (PRD S6) and any `brain_step`-backed computation need to gate on
this field. Refusing production of the entire trace over one panel's precondition would
throw away real, valid data for no benefit to the other panels.
