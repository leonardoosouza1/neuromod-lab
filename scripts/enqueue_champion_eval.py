"""Freeze the final champion of finished runs and queue a one-generation evaluation of it.

Generalises the B3 recipe (`enqueue_b3_b2.py`): the champion genome is copied into the
evaluation directory as `evolve_best_gen0000.bin`, which is what `--resume` loads, and
`--resume-mix 1` makes the whole population clones of it. The clones are ONE measurement
and every analysis must treat them so.

The evaluation inherits the training run's control-path and cost flags from its request
file, so a legacy champion is never evaluated on the fixed path. Request files are
prefixed `2_` so the daemon, which takes the queue in filename order, runs these short
evaluations before any still-queued `3_` training runs.

    python scripts/enqueue_champion_eval.py --runs b5_ctrl_s31 b5_ctrl_s77 --tracks 8200 8005
    python scripts/enqueue_champion_eval.py --glob 'b5_rand_s*' --tracks 8200 8005
"""
from __future__ import annotations

import argparse
import fnmatch
import glob
import json
import os
import re
import shutil

BASE = '/media/llm-data/universe-runs/neuromod-lab-taxi'
SPOOL = os.path.join(BASE, '_nmd')
SNAPSHOTS = '/media/llm-data/snapshots'
EVAL_SUFFIX = re.compile(r'_eval_t\d+')

# Flags that describe HOW the champion was trained and must follow it into evaluation.
INHERITED = ('bin', 'width', 'wall-cost', 'impact-cost', 'throttle-arbitration', 'wall-probes',
             'slow-kinematics', 'legacy-reverse-controller', 'cost-gate-progress', 'retina-range')


def training_request(run: str) -> dict:
    for folder in ('feitos', 'pedidos'):
        for path in glob.glob(os.path.join(SPOOL, folder, f'*_{run}.json')):
            with open(path) as f:
                return json.load(f)
    raise SystemExit(f'no request file for {run} in {SPOOL}/feitos or pedidos')


def final_champion(run_dir: str, gens: int) -> str:
    path = os.path.join(run_dir, f'evolve_best_gen{gens - 1:04d}.bin')
    if not os.path.exists(path):
        raise SystemExit(f'{run_dir} is not finished: {os.path.basename(path)} missing')
    return path


def freeze_champion(run: str) -> tuple[str, dict]:
    """Copy the final champion of a finished training run to the snapshot store."""
    args = training_request(run)['args']
    champion = final_champion(os.path.join(BASE, run), int(args['gens']))
    frozen = os.path.join(SNAPSHOTS, 'champions', f'{run}.bin')
    os.makedirs(os.path.dirname(frozen), exist_ok=True)
    shutil.copy(champion, frozen)
    return frozen, args


def eval_request(run: str, track: int, frozen: str, args: dict, ticks: int = 20000,
                 beings: int = 8) -> dict:
    """Prepare the evaluation directory and return the nmd request for one track."""
    if EVAL_SUFFIX.search(run):
        raise SystemExit(f'{run} is itself an evaluation, not a training run')
    eval_id = f'{run}_eval_t{track}'
    out = os.path.join(BASE, eval_id)
    os.makedirs(out, exist_ok=True)
    shutil.copy(frozen, os.path.join(out, 'evolve_best_gen0000.bin'))
    eval_args = {k: args[k] for k in INHERITED if k in args}
    eval_args.update({'gens': 1, 'ticks': ticks, 'beings': beings, 'tracks': [track],
                      'seed': args['seed'], 'same-start': True, 'resume': True,
                      'resume-mix': 1, 'driving-diagnostics': True,
                      'vision-every': 2000, 'replay-every': 1})
    return {'id': eval_id, 'script': 'universe_run', 'out': eval_id, 'env': {},
            'args': eval_args, 'champion_of': run}


def write_request(request: dict, prefix: str) -> None:
    tmp = os.path.join(SPOOL, 'pedidos', f'{prefix}_{request["id"]}.json.tmp')
    with open(tmp, 'w') as f:
        json.dump(request, f)
    os.replace(tmp, tmp[:-4])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', nargs='*', default=[])
    ap.add_argument('--glob', default=None, help="run-name pattern, e.g. 'b5_rand_s*'")
    ap.add_argument('--tracks', nargs='+', type=int, required=True)
    ap.add_argument('--ticks', type=int, default=20000)
    ap.add_argument('--beings', type=int, default=8)
    ap.add_argument('--prefix', default='2')
    a = ap.parse_args()

    runs = list(a.runs)
    if a.glob:
        # An evaluation directory (`<run>_eval_t<track>`) also matches a pattern like
        # `b5_rot_s*`; on 16/09 that queued 16 evaluations of evaluations. Only training runs
        # are champions.
        runs += sorted(d for d in os.listdir(BASE) if fnmatch.fnmatch(d, a.glob)
                       and os.path.isdir(os.path.join(BASE, d)) and EVAL_SUFFIX.search(d) is None)
    for run in runs:
        if EVAL_SUFFIX.search(run):
            raise SystemExit(f'{run} is itself an evaluation, not a training run')
    queued = 0
    for run in runs:
        frozen, args = freeze_champion(run)
        for track in a.tracks:
            write_request(eval_request(run, track, frozen, args, a.ticks, a.beings), a.prefix)
            queued += 1
    print(f'queued {queued} evaluation(s) for {len(runs)} champion(s); frozen under {SNAPSHOTS}/champions')


if __name__ == '__main__':
    main()
