"""Battery B5 — the fast screen. Bets as pre-registered in Universe/docs/PREDICOES-CEREBRO.md (B5).

Arms, each changing ONE thing against the control `ctrl` (fixed path, no cost, same start,
track 8005, 32 beings, 12 000 ticks, 25 generations): `gate` (cost curriculum at 1 000 m),
`rot` (tracks 8005, 8100, 8150 rotated per generation), `rand` (random start), `long`
(20 000 ticks). Seeds 31, 77, 113, 137.

Rulers, declared before the run:
  primary   generation of discovery: first generation whose population MEDIAN progress
            reaches 1 000 m; censored (None) if it never does within 25 generations.
  secondary lap fraction of the final champion on held-out track 8200, from the
            one-generation evaluation `<run>_eval_t8200` (8 clones = one measurement).
  tertiary  impacts per km over the last 5 generations, as a ratio of sums.

Bets:
  (a) gate discovers at a generation <= ctrl in >= 3/4 seeds. Refuted if <= 2/4.
      Reported as NON-INFORMATIVE when gate and ctrl are identical in every generation
      (the gate never bound) -- a trivially satisfied bet is not a confirmation.
  (b) rot is the only arm that moves 8200: champion lap fraction rot > ctrl in >= 3/4, and
      no other arm reaches 3/4. Refuted if rot <= 2/4 or another arm also reaches 3/4.
  (c) rand does not change discovery (|delta gen| <= 3 in 3/4, censored treated as 25+)
      and does not move 8200 (rand > ctrl in <= 2/4).
  (d) long: median progress at generation 24 > 4 700 m in >= 3/4. Refuted if <= 2/4.

    python src/analyze_b5.py
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_db  # noqa: E402

BASE = '/media/llm-data/universe-runs/neuromod-lab-taxi'
LOGS = os.path.join(BASE, '_nmd', 'log')
ARMS = ('ctrl', 'gate', 'rot', 'rand', 'long')
SEEDS = (31, 77, 113, 137)
GENS = 25
DISCOVERY_M = 1000.0
LAP_M = {8005: 1639.0, 8200: 2377.0}
CEILING_LONG_M = 4700.0


def medians(run: str) -> list[float]:
    """Median progress per generation, from the run's own log line `gen N | med= X m`."""
    path = os.path.join(LOGS, f'{run}.log')
    if not os.path.exists(path):
        return []
    out = []
    with open(path, errors='replace') as f:
        for line in f:
            m = re.match(r'^gen +(\d+) \| med= *(\d+)m', line)
            if m:
                out.append(float(m.group(2)))
    return out


def discovery(meds: list[float], only_gens: set[int] | None = None) -> int | None:
    for gen, value in enumerate(meds):
        if only_gens is not None and gen not in only_gens:
            continue
        if value >= DISCOVERY_M:
            return gen
    return None


def tracks_per_generation(run: str) -> dict[int, int]:
    """Which track each generation ran on, from the log line `[pista] gen N usa seed=S`.
    Needed because in the rotation arm the discovery ruler is confounded by track difficulty
    (ledger B5d, declared before the result)."""
    path = os.path.join(LOGS, f'{run}.log')
    out: dict[int, int] = {}
    if not os.path.exists(path):
        return out
    with open(path, errors='replace') as f:
        for line in f:
            m = re.search(r'\[pista\] gen +(\d+) usa seed=(\d+)', line)
            if m:
                out[int(m.group(1))] = int(m.group(2))
    return out


def same_champion(run_a: str, run_b: str) -> bool:
    """True when two runs ended with byte-identical champion genomes. Then one evaluation
    serves both: re-running a deterministic simulator on the same bytes measures nothing new.
    Checked 16/09 for gate vs ctrl: identical md5 in all four seeds."""
    paths = [os.path.join(BASE, r, f'evolve_best_gen{GENS - 1:04d}.bin') for r in (run_a, run_b)]
    if not all(os.path.exists(p) for p in paths):
        return False
    with open(paths[0], 'rb') as fa, open(paths[1], 'rb') as fb:
        return fa.read() == fb.read()


def eval_laps(run: str, track: int) -> float | None:
    arm, seed = re.match(r'^b5_([a-z]+)_s(\d+)$', run).groups()
    if arm != 'ctrl' and same_champion(run, f'b5_ctrl_s{seed}'):
        run = f'b5_ctrl_s{seed}'
    path = os.path.join(BASE, f'{run}_eval_t{track}', 'population_gen0000.json')
    if not os.path.exists(path):
        return None
    with open(path) as f:
        beings = json.load(f)
    values = {round(float(b.get('progress_m') or 0.0), 3) for b in beings}
    if len(values) != 1:
        print(f'[warn] {run}_eval_t{track}: clones NOT identical ({len(values)} values)')
    return float(beings[0].get('progress_m') or 0.0) / LAP_M[track]


def fmt_gen(g: int | None) -> str:
    return '  cens' if g is None else f'{g:6d}'


def main() -> None:
    db = lab_db.connect()
    rows = {}
    for arm in ARMS:
        for seed in SEEDS:
            run = f'b5_{arm}_s{seed}'
            meds = medians(run)
            last5 = db.execute('SELECT impacts_per_km FROM v_last5 WHERE run_name = ?', (run,)).fetchone()
            tracks = tracks_per_generation(run)
            on_8005 = {g for g, t in tracks.items() if t == 8005} if tracks else None
            rows[(arm, seed)] = {
                'gens': len(meds), 'discovery': discovery(meds),
                # B5d: the comparable ruler holds the track fixed at 8005
                'discovery_8005': discovery(meds, on_8005),
                'tracks_seen': sorted(set(tracks.values())),
                'median_last': meds[-1] if meds else None,
                'laps_8200': eval_laps(run, 8200), 'laps_8005': eval_laps(run, 8005),
                'impacts_per_km': float(last5[0]) if last5 and last5[0] is not None else None,
                'medians': meds,
            }

    print(f"{'run':16s}{'gens':>5s}{'disc':>6s}{'d8005':>6s}{'med@last':>9s}{'laps8005':>9s}{'laps8200':>9s}{'imp/km':>8s}")
    for arm in ARMS:
        for seed in SEEDS:
            r = rows[(arm, seed)]
            print(f"{arm + '_s' + str(seed):16s}{r['gens']:5d}{fmt_gen(r['discovery'])}{fmt_gen(r['discovery_8005'])}"
                  f"{(r['median_last'] or 0):9.0f}"
                  f"{(r['laps_8005'] if r['laps_8005'] is not None else float('nan')):9.2f}"
                  f"{(r['laps_8200'] if r['laps_8200'] is not None else float('nan')):9.2f}"
                  f"{(r['impacts_per_km'] if r['impacts_per_km'] is not None else float('nan')):8.2f}")

    complete = {arm: all(rows[(arm, s)]['gens'] == GENS for s in SEEDS) for arm in ARMS}
    print('\ncomplete arms:', [a for a in ARMS if complete[a]], ' incomplete:', [a for a in ARMS if not complete[a]])

    def gen_or_cens(g):
        return GENS if g is None else g

    if complete['rot'] and complete['ctrl']:
        literal = sum(1 for s in SEEDS if gen_or_cens(rows[('rot', s)]['discovery']) < gen_or_cens(rows[('ctrl', s)]['discovery']))
        fixed = sum(1 for s in SEEDS if gen_or_cens(rows[('rot', s)]['discovery_8005']) < gen_or_cens(rows[('ctrl', s)]['discovery_8005']))
        print(f"[B5d] rot discovers earlier than ctrl: literal ruler {literal}/4 (CONFOUNDED by track), "
              f"8005-only ruler {fixed}/4 (comparable; 9 generations of resolution)")

    print('\n=== bets (pre-registered) ===')
    # (a)
    if complete['gate'] and complete['ctrl']:
        identical = all(rows[('gate', s)]['medians'] == rows[('ctrl', s)]['medians'] for s in SEEDS)
        if identical:
            print('(a) NON-INFORMATIVE: gate identical to ctrl in every generation of every seed (the gate never bound)')
        else:
            ok = sum(1 for s in SEEDS if gen_or_cens(rows[('gate', s)]['discovery']) <= gen_or_cens(rows[('ctrl', s)]['discovery']))
            print(f"(a) gate discovers <= ctrl in {ok}/4 -> {'holds' if ok >= 3 else 'REFUTED'}")
    # (b)
    def beats_ctrl_8200(arm):
        pairs = [(rows[(arm, s)]['laps_8200'], rows[('ctrl', s)]['laps_8200']) for s in SEEDS]
        if any(x is None or y is None for x, y in pairs):
            return None
        return sum(1 for x, y in pairs if x > y)
    b = {arm: beats_ctrl_8200(arm) for arm in ARMS if arm != 'ctrl'}
    print('(b) champion laps on 8200 > ctrl, per arm:', {k: (f'{v}/4' if v is not None else 'pending') for k, v in b.items()})
    if b.get('rot') is not None and all(v is not None for v in b.values()):
        others = [a for a, v in b.items() if a != 'rot' and v >= 3]
        verdict = 'holds' if b['rot'] >= 3 and not others else 'REFUTED'
        print(f"    rot {b['rot']}/4, other arms at >= 3/4: {others} -> {verdict}")
    # (c)
    if complete['rand'] and complete['ctrl']:
        close = sum(1 for s in SEEDS if abs(gen_or_cens(rows[('rand', s)]['discovery']) - gen_or_cens(rows[('ctrl', s)]['discovery'])) <= 3)
        moves = b.get('rand')
        print(f"(c) rand |delta discovery| <= 3 in {close}/4; rand > ctrl on 8200 in {moves if moves is not None else 'pending'}/4 -> "
              f"{'holds' if close >= 3 and moves is not None and moves <= 2 else ('pending' if moves is None else 'REFUTED')}")
    # (d)
    if complete['long']:
        over = sum(1 for s in SEEDS if (rows[('long', s)]['median_last'] or 0) > CEILING_LONG_M)
        print(f"(d) long median at gen 24 > {CEILING_LONG_M:.0f} m in {over}/4 -> {'holds' if over >= 3 else 'REFUTED'}")

    out = os.path.join(BASE, 'b5-analise')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'b5.json'), 'w') as f:
        json.dump({f'{a}_s{s}': v for (a, s), v in rows.items()}, f, indent=1)
    print(f'\nwrote {out}/b5.json')


if __name__ == '__main__':
    main()
