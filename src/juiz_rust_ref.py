"""[pred 174] juiz RUST (Universe taxi_evolve --G 0) com as MESMAS copias do juiz Python (P 128, R 1, semente 0, mapa 1000 do traco):
a corrida anterior usou P 8 = 8 seres (erro-padrao ~18 % em t_vida, inconclusiva). Chama o binario ja compilado (CPU, < 1 s) e
grava em e82. Compara com e72/juiz_python_ref (campeao + N(0, .05), 128 copias): fit e t_vida dentro de +-5 % fecham a 174."""
import sys, os, json, subprocess, argparse
N = '/media/llm-data/universe-runs/neuromod-lab-taxi'; BIN = '/home/leonardo/projects/LLM/Universe/target/release/taxi_evolve'
ap = argparse.ArgumentParser(); ap.add_argument('--out', default=f'{N}/e82'); ap.add_argument('--P', type=int, default=128); ap.add_argument('--G', type=int, default=0); a = ap.parse_args()
os.makedirs(a.out, exist_ok=True); saida = os.path.join(a.out, f'rust_juiz_G{a.G}_P{a.P}.json')
cmd = [BIN, '--G', str(a.G), '--P', str(a.P), '--R', '1', '--seeds', '0', '--mapa', f'{N}/e81/traco_ref.json', '--campeao', f'{N}/e82/campeao_e64_linear_40.json', '--saida', saida]
print(' '.join(cmd), flush=True); r = subprocess.run(cmd, capture_output=True, text=True); print(r.stdout[-4000:], flush=True); print(r.stderr[-2000:], file=sys.stderr, flush=True)
assert r.returncode == 0, f'taxi_evolve exit {r.returncode}'
J = json.load(open(saida)); print('chaves do JSON:', list(J.keys())[:30], flush=True)
ref = f'{N}/e72/juiz_python_ref.json'
if os.path.exists(ref): print('python ref:', json.dumps(json.load(open(ref)))[:600], flush=True)
