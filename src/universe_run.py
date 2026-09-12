#!/usr/bin/env python3
"""[11/09 PRD-CEREBRO C4] wrapper da fila `nmd` para binarios do Universe (regra 21: UM processo na GPU, tudo pela fila).
Sem torch, sem CUDA: so subprocess. O binario tem de estar compilado antes (`cargo build --release`, CPU, fora da fila).
Pedido: {"script": "universe_run", "out": "u0_smoke", "args": {"bin": "gpu_evolve", "gens": 1, "ticks": 20000, "retomar": true,
         "pistas": [8005, 8200, 9001], "seed": 77}}  -> gpu_evolve --gens 1 --ticks 20000 --retomar --pistas 8005,8200,9001 --seed 77 --out <dir>
Tudo que nao e flag do wrapper passa direto ao binario (parse_known_args); `--pistas` com varios valores vira lista separada por virgula
(a fila nao aceita virgula em valor). `--out` do pedido vira `<flag-de-saida> <dir>` (gpu_evolve: `--out`; "saida": "false" desliga)."""
import sys, os, json, argparse, subprocess, time
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--bin', required=True)
ap.add_argument('--saida', default='--out', help='nome do flag de saida do binario (gpu_evolve: --out); "false" = nao acrescenta'); ap.add_argument('--nice', type=int, default=5)
ap.add_argument('--pistas', nargs='*', default=None)
a, resto = ap.parse_known_args()
UNI = os.path.expanduser('~/projects/LLM/Universe'); exe = os.path.join(UNI, 'target', 'release', a.bin)
if not os.path.isfile(exe): raise SystemExit(f'binario nao existe: {exe} (cargo build --release antes, fora da fila)')
os.makedirs(a.out, exist_ok=True); args = list(resto)
if a.pistas: args += ['--pistas', ','.join(a.pistas)]
if a.saida != 'false': args += [a.saida, a.out]
cmd = ['nice', '-n', str(a.nice), exe] + [str(x) for x in args]
print('universe_run:', ' '.join(cmd), flush=True); t0 = time.time()
env = dict(os.environ); env.setdefault('HSA_OVERRIDE_GFX_VERSION', '10.3.0')
rc = subprocess.call(cmd, cwd=UNI, env=env)
print(f'universe_run: exit {rc} em {time.time()-t0:.0f}s', flush=True); sys.exit(rc)
