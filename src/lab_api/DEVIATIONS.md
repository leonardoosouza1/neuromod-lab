# Deviations between the PRD and what this slice (S1, the API) actually does

Per the task rule: when the PRD and the code disagree, the code wins, and the
disagreement is written down here rather than silently "fixed" in the PRD.

## 1. `pista_check` DOES print "[AVISO]" -- from `world.rs`, on stderr, not from `pista_check.rs` itself (CORRECTED, see below)

**This item originally said "AVISO" never appears and no naturally-failing
seed existed. Both claims were wrong; the cold tester found the gap this
caused (`POST /api/queue` returned 201 for seed 8300 instead of 422) and it
is fixed as of this commit.** Kept below (struck out) for the record, then
the correction.

~~Read `Universe/src/bin/pista_check.rs` in full (228 lines) [...] the string
`"AVISO"` does not appear anywhere in the binary's source [...] no naturally-
failing seed was found.~~ The miss: `"AVISO"` was grepped only in
`pista_check.rs` itself. It actually lives in `Universe/src/world.rs`
(`procedural_waypoints()`'s fallback path, `eprintln!`, not `println!`) --
printed when the track generator's 96 candidate attempts all fail
`validate_track` and it falls back to an UNVALIDATED reserve candidate. That
code path runs from `VoxelWorld::new()`, which `pista_check` calls too, so
`pista_check --seed 8300` prints `"[AVISO] procedural_waypoints(seed=8300):
96 tentativas de geração falharam ... caindo no candidato de reserva SEM
validação geométrica"` **to stderr**, exits `0`, and its own point-by-point
walk (within whatever `--ate` window was examined) may still report "No
defects" -- the fallback candidate's defect, if any, need not fall inside
that window.

What the binary prints on **stdout** per examined point, on a defect: `"  ←
AXIS OFF THE TRACK"` (axis lands off `VoxelType::Road`) or `"  ← BOTTLENECK"`
(free width `< width * 0.5`), plus a diagnostic block that prints `"→ NULL
VARIANCE: ..."` when the frontal-vision sensor is constant, closing with
either `"No defects: ..."` (drivable) or `"<N> points with defects in the
examined stretch."`. The process exit code is always `0` regardless of
stdout content -- only the `[AVISO]` line (stderr) and the stdout defect
markers carry a refusal signal; there is no non-zero exit to lean on.

Two real, independent gaps this closed, both now covered by
`tests/test_lab_api.py::TestTracksAndSnapshots` against the REAL binary:

1. **stderr was only read when `returncode != 0`** (`validate_track` in
   `routes/queue.py`), and `pista_check` always exits `0` -- so the `[AVISO]`
   line was invisible no matter what it said. Fixed: stderr is now checked
   for `"[AVISO]"` unconditionally. Seed `8300` (exit 0, "No defects" in the
   examined stretch, `[AVISO]` on stderr) is the naturally-failing seed that
   was missing before.
2. **`--ate` defaulted to `pista_check`'s own 600 m**, examining only the
   first 600 m of a lap that can run past 2 km. Seed `8215`'s only defects (4
   × `AXIS OFF THE TRACK`) sit at ~1152 m -- past that window, so the old
   default silently missed them. Fixed: `validate_track(ate=None)` (the
   default `validate_experiment` uses) now probes the full lap length first
   (`--ate 1`, whose header line prints `"lap N m"` regardless of the window
   requested) and validates that whole distance. An explicit `ate` is still
   honoured as a deliberate partial check.

Seeds sampled at full-lap resolution for this fix: `8300` (AVISO fallback,
refused), `8215` (4 defects @ ~1152 m, refused), `8230` (1 defect @ 224 m,
refused -- was already inside the old 600 m window), `8107` and `8200`
(clean, accepted), `8005` (the existing fixture seed, still clean at its
full ~1639 m lap).

## 2. `--bin` validated against `/media/llm-data/snapshots/`, matching real usage exactly

Initially worried this might be a deviation: `universe_run.py` (the script
`nmd.py` invokes for a `"script": "universe_run"` pedido) resolves its own
`--bin` argument as `os.path.join(UNI, 'target', 'release', a.bin)`. Read a
REAL pending request from the live spool
(`/media/llm-data/universe-runs/neuromod-lab-taxi/_nmd/pedidos/`, e.g.
`args.bin = "/media/llm-data/snapshots/gpu_evolve-f5d203b"`) and confirmed:
because `a.bin` is an ABSOLUTE path, Python's `os.path.join` discards every
component before it -- the `target/release` prefix is silently dropped, and
the binary that actually runs is exactly the absolute path handed in `args`.
So "bin must be a file under `/media/llm-data/snapshots/`" (this task's
instruction) is not a deviation from how the daemon behaves; it is exactly
what a real, currently-queued pedido does. `routes/queue.py:validate_bin()`
requires `bin` to resolve to a file whose PARENT is exactly
`settings.snapshots_root` (not a subdirectory -- `b1-champions/` holds genome
weight files, not executables) and to be executable.

## 3. Arm-flag values: a switch never accepts `value: false`

`scripts/nmd.py`'s own `valida()` special-cases `v is True` for a boolean arg
(emits `--flag` with no value) but has NO corresponding case for `v is False`:
a `False` value falls into the general value loop, which raises
`ValueError('bool em lista')` for any boolean it did not already special-case.
In other words, the daemon has no way to express "off" for a switch flag
other than omitting it entirely -- there is no such thing as `--no-fuel
false` in this system.

`routes/queue.py`'s `ArmFlag`/`validate_arm_flags()` therefore reject
`value: false` (and any non-`{None, True}` value) for a switch flag with a
422 naming the flag, rather than writing a pedido the daemon would refuse
downstream with a much less specific `"bool em lista"`. Not a deviation from
the daemon's behaviour -- a stricter, earlier rejection of exactly the same
case, with a reason attached.

## 4. `/api/queue` write endpoints authenticate identically to reads under `--lan`

PRD S1 §8's prose singles out write routes ("CSRF token on every write
route"), which could be read as "only writes need a session." The API section
(§7) is broader: "Write routes: pydantic schema, CSRF token under --lan, one
audit line." Read routes under `--lan` still need to not be wide open to
anyone on the LAN without the password -- the PRD's own stated goal ("the
owner wants LAN access with a password") would not hold if `GET
/api/db/batteries` answered without a session. This slice requires a live
session for EVERY route under `--lan` (`current_who` as a router-level
`dependencies=[...]`, so both reads and writes are gated) and additionally
requires the CSRF header only on the five write routes (`require_csrf`).
Not a contradiction of the PRD text, just resolving an ambiguity the PRD
prose left open, in the direction its own stated goal points.

## 5. `GET /api/snapshots` "binaries" is every top-level FILE under `snapshots_root`

The task brief says `/api/snapshots` "lists `/media/llm-data/snapshots/`
binaries and `b1-champions/`." The snapshots root currently also holds a
non-binary file (`universe_pos_E1_20260813_1517.tar.gz`, a tarball) and other
subdirectories (`cerebro-campeao-2026-08-13/`) besides `b1-champions/`. This
route lists every regular file directly under `snapshots_root` as a
"binary" (including that tarball -- it is not this route's job to guess
which top-level files are executables the launcher can point `bin` at; the
launcher already gets `"executable": true/false` per entry from `os.access`)
and, separately, every regular file inside `b1-champions/` as a "champion" --
other subdirectories (like `cerebro-campeao-2026-08-13/`) are not listed
under either key, matching the brief's literal "binaries and `b1-champions/`"
rather than guessing at a third category.
