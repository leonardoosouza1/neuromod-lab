# Deviations between the PRD and what this slice (S1, the API) actually does

Per the task rule: when the PRD and the code disagree, the code wins, and the
disagreement is written down here rather than silently "fixed" in the PRD.

## 1. `pista_check` never prints "AVISO"

PRD S1 task brief: "tracks must pass `GET /api/tracks/validate` = run
`pista_check --seed N` and treat any line containing `AVISO` as invalid."

Read `Universe/src/bin/pista_check.rs` in full (228 lines) and ran it against
several seeds (`8005`, `9001`, `1`, `2`, `3`, `42`, `100`, `7000`, `8200`,
widths `28` and `60`): the string `"AVISO"` does not appear anywhere in the
binary's source, and none of these runs printed it. This is consistent with
the project's 12/09 "English-only code" rule (`CLAUDE.md` memory
`feedback_english_only_code`) -- `pista_check.rs` was rewritten in English at
some point after the PRD prose was drafted, and the PRD's "AVISO" line is
stale.

What the binary actually prints per examined point, on a defect: `"  ←
AXIS OFF THE TRACK"` (axis lands off `VoxelType::Road`) or `"  ← BOTTLENECK"`
(free width `< width * 0.5`), plus a separate diagnostic block that prints
`"→ NULL VARIANCE: ..."` when the frontal-vision sensor is constant. The
closing summary line is either `"No defects: ..."` (drivable) or `"<N> points
with defects in the examined stretch."` (not drivable). The binary's own exit
code is always `0` either way -- it never signals failure through the process
exit status, only through stdout text.

`routes/queue.py`'s `_parse_pista_check()` therefore classifies a track as
valid when the output contains `"No defects:"` AND none of
`("AXIS OFF THE TRACK", "BOTTLENECK", "NULL VARIANCE", "AVISO")` appear on any
line. `"AVISO"` is kept in that tuple as a harmless, currently-dead extra
match -- if some future or alternate build of `pista_check` reintroduces
Portuguese wording, this code keeps working without a change; it is not load-
bearing for any seed exercised in this slice's tests.

**Consequence for testing:** every seed this session sampled (see above,
including the fixture's own `8005`) came back "No defects" -- track
generation in the current `VoxelWorld` appears robust for these seeds/widths,
so no naturally-failing seed was found to exercise the "queue POST refuses an
invalid track" path end-to-end against the real binary. `tests/test_lab_api.py`
covers this two ways instead: (a) a pure unit test of `_parse_pista_check()`
against synthetic output text containing each defect marker, and (b) an
integration test of `POST /api/queue` that monkeypatches
`routes.queue.validate_track` to return `{"valid": False, ...}`, proving the
route actually consults the validator's verdict and refuses the request
before writing anything to the spool.

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
