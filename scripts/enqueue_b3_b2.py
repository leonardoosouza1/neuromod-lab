"""Enqueue batteries B3 (frozen champions, train vs held-out track) and B2 (cost curriculum).

Both run on a FROZEN binary so that agents rebuilding the Universe checkout cannot swap the
executable under the queue mid-battery (`universe_run.py` joins `--bin` onto target/release,
and an absolute path survives that join). Request files are prefixed `1_`/`2_` because the
daemon takes the queue in filename order and B3 (48 x 1 generation) must precede B2.

B3 recipe, per champion: the run directory is pre-seeded with the champion genome as
`evolve_best_gen0000.bin`, which is what `--resume` loads; `--resume-mix 1` makes the whole
population clones of it. The eight clones are one measurement and the analysis treats them so.
"""
import json, os, shutil

BASE = '/media/llm-data/universe-runs/neuromod-lab-taxi'
PEDIDOS = os.path.join(BASE, '_nmd', 'pedidos')
BIN = '/media/llm-data/snapshots/gpu_evolve-f5d203b'
CHAMPIONS = '/media/llm-data/snapshots/b1-champions'
SEEDS = (31, 77, 113, 137, 191, 233)
LEGACY = {'throttle-arbitration': 'legacy', 'wall-probes': 'legacy', 'slow-kinematics': 'legacy',
          'legacy-reverse-controller': True}
COST = {'wall-cost': 2, 'impact-cost': 1}
NOCOST = {'wall-cost': 0, 'impact-cost': 0}
ARMS_B1 = {'legacy': {**LEGACY, **COST}, 'fixed': COST,
           'legacy_nocost': {**LEGACY, **NOCOST}, 'nocost': NOCOST}

def write(prefix, run_id, args):
    ped = {'id': run_id, 'script': 'universe_run', 'out': run_id, 'env': {}, 'args': args}
    with open(os.path.join(PEDIDOS, f'{prefix}_{run_id}.json'), 'w') as f:
        json.dump(ped, f)

n3 = 0
for arm, flags in ARMS_B1.items():
    for seed in SEEDS:
        champion = os.path.join(CHAMPIONS, f'b1_{arm}_s{seed}.bin')
        assert os.path.exists(champion), champion
        for track in (8005, 8200):
            run_id = f'b3_{arm}_s{seed}_t{track}'
            out = os.path.join(BASE, run_id)
            os.makedirs(out, exist_ok=True)
            shutil.copy(champion, os.path.join(out, 'evolve_best_gen0000.bin'))
            write('1', run_id, {'bin': BIN, 'gens': 1, 'ticks': 20000, 'beings': 8, 'width': 28,
                                'tracks': [track], 'seed': seed, 'same-start': True,
                                'resume': True, 'resume-mix': 1, 'driving-diagnostics': True,
                                'vision-every': 2000, 'replay-every': 1, **flags})
            n3 += 1

n2 = 0
ARMS_B2 = {'cost': COST, 'nocost': NOCOST, 'gate': {**COST, 'cost-gate-progress': 1000}}
for arm, flags in ARMS_B2.items():
    for seed in SEEDS:
        run_id = f'b2_{arm}_s{seed}'
        write('2', run_id, {'bin': BIN, 'gens': 30, 'ticks': 20000, 'beings': 48, 'width': 28,
                            'tracks': [8005], 'seed': seed, 'same-start': True,
                            'driving-diagnostics': True, 'replay-every': 29, **flags})
        n2 += 1
print(f'queued B3 {n3} runs, B2 {n2} runs -> {PEDIDOS}')
