#!/usr/bin/env python3
"""[11/09 PRD-CEREBRO C4] wrapper da fila `nmd` para binarios do Universe (regra 21: UM processo na GPU, tudo pela fila).
Sem torch, sem CUDA: so subprocess. O binario tem de estar compilado antes (`cargo build --release`, CPU, fora da fila).
Uso (pedido): {"script": "universe_run", "out": "universe-cerebro/u0", "args": {"bin": "gpu_evolve", "args-json": "[\"--gens\",\"1\",...]"}}
`--out` do pedido vira `--saida <dir>` do binario (se o binario nao aceitar --saida, passe "saida": false)."""
import sys, os, json, argparse, subprocess, time
ap = argparse.ArgumentParser(); ap.add_argument('--out', required=True); ap.add_argument('--bin', required=True); ap.add_argument('--args-json', default='[]')
ap.add_argument('--saida', default='true', help='true = acrescenta --saida <out> aos args do binario'); ap.add_argument('--nice', type=int, default=5)
a = ap.parse_args()
UNI = os.path.expanduser('~/projects/LLM/Universe'); exe = os.path.join(UNI, 'target', 'release', a.bin)
if not os.path.isfile(exe): raise SystemExit(f'binario nao existe: {exe} (cargo build --release antes, fora da fila)')
os.makedirs(a.out, exist_ok=True); args = json.loads(a.args_json)
if a.saida == 'true': args += ['--saida', a.out]
cmd = ['nice', '-n', str(a.nice), exe] + [str(x) for x in args]
print('universe_run:', ' '.join(cmd), flush=True); t0 = time.time()
env = dict(os.environ); env.setdefault('HSA_OVERRIDE_GFX_VERSION', '10.3.0')
rc = subprocess.call(cmd, cwd=UNI, env=env)
print(f'universe_run: exit {rc} em {time.time()-t0:.0f}s', flush=True); sys.exit(rc)
