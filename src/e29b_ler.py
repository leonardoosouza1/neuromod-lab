"""Le os genes das reacoes (E29b) dos campeoes salvos no JSON do runner: tau_k, w_k, v_k, theta.
Uso: python src/e29b_ler.py <resultado.json>  — checa predicoes 29 (w<0) e 30 (tau divergem >=3x)."""
import sys, json, math
from lab import Reativo
sig = lambda g: 1./(1. + math.exp(-g))
for path in sys.argv[1:]:
    R = json.load(open(path))
    for r in (R if isinstance(R, list) else R.get('resultados', [R])):
        if 'reacoes' not in r.get('nome', ''): continue
        print(f"== {r['nome']} fit {r['fit']} mortos {r['mortos']}")
        o = Reativo.NP; n_w_neg = 0; n_div = 0
        for sd, W in r['W'].items():
            tau = [1. + 200.*sig(g - 4.) for g in W[o:o+2]]; w = W[o+2:o+4]; v = W[o+4:o+6]; th = sig(W[o+6])
            raz = max(tau)/min(tau); n_w_neg += (w[0] < 0); n_div += (raz >= 3.)
            print(f"  s{sd}: tau sede {tau[0]:6.1f} fome {tau[1]:6.1f} (razao {raz:4.1f})  w sede {w[0]:+.2f} fome {w[1]:+.2f}  v {v[0]:+.2f} {v[1]:+.2f}  portao {th:.2f}")
        n = len(r['W']); print(f"  pred 29 (w_sede<0): {n_w_neg}/{n}   pred 30 (tau razao>=3): {n_div}/{n}")
