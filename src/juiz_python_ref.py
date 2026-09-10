"""[pred 174] referencia do JUIZ em Python nas MESMAS condicoes do juiz Rust (taxi_evolve --G 0): mundo v0 sem retina/regime/custo,
corpo/passageiros do cenario mundoA (dinh0 10, guincho 10, fuel_pos_pane 5, kcal_pane 8, respawn 20, ponto 0), regua vida, horizonte
aberto T_max 7200, mapa gerar_mapa(1000) (o do traco), 128 copias. [15:30] O GENOMA vem do JSON do Rust (`bracos.linear.W.0` = copia 0
semeada, campeao e64 + N(0, .05) do RNG do Rust): mesmo genoma dos dois lados, so o sorteio do mundo (berco/passageiros) difere. O Rust
tem semente de juiz FIXA (7777); aqui variamos a semente do juiz (--seeds) para ter a DISTRIBUICAO do Python e ver se o Rust cai dentro.
Veredito: fit e t_vida do Rust dentro de +-5 % da media do Python E dentro do [min, max] das sementes."""
import sys, os, json, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *
N = '/media/llm-data/universe-runs/neuromod-lab-taxi'
ap = argparse.ArgumentParser(); ap.add_argument('--rust', default=f'{N}/e82/rust_juiz_G0_P128.json'); ap.add_argument('--seeds', type=int, nargs='*', default=[7777, 7778, 7779, 7780, 7781]); ap.add_argument('--out', default=f'{N}/e72'); a = ap.parse_args()
cen = json.load(open('/home/leonardo/projects/LLM/neuromod-lab/cenarios/mundoA_seres.json'))
c = CfgCampo(L=200., fitness='vida'); co = cen['corpo']; c.dinh0 = co['dinh0']; c.fome_passo = co['fome_passo']; c.KCAL_PANE = co['kcal_pane']; c.GUINCHO = co['guincho']; c.FUEL_POS_PANE = co['fuel_pos_pane']
px = cen['passageiros']; c.NPX = px['npx']; c.respawn = px['respawn']; c.pax_cidade = px['pax_cidade']; c.ponto = px['ponto']; c.tarifa_base = px['tarifa_base']; c.tarifa_km = px['tarifa_km']; c.horizonte = 'aberto'; c.T_max = 7200; c.w_trab = 1.0
assert NF == 29 and Linear.NP == 40, (NF, Linear.NP)
R = json.load(open(a.rust)); b = R['bracos']['linear']; W = torch.tensor(b['W']['0'], device=DEV); assert W.numel() == 40, W.numel()
if R.get('nomes_f'): assert list(R['nomes_f']) == list(NOMES_F), 'layout de genes do Rust != NOMES_F daqui'
rust = dict(fit=b['fit'], t_vida=b['t_vida_media'], rec=b['rec'], ent=b['ent'], mortos=b['mortos'], mediana=b['t_vida_mediana'])
print(f"  Rust (128 copias, semente 7777): fit {rust['fit']:.3f} | mortos {rust['mortos']:.2f} | ent {rust['ent']:.2f} | t_vida {rust['t_vida']:.2f} d (mediana {rust['mediana']:.2f}) | rec {rust['rec']:.1f}", flush=True)
mapa = gerar_mapa(1000, L=200., distinto=True); res = []
for sd in a.seeds:
    med = medidas(Linear, W, [mapa], c, T=7200, seed=sd, R=1, copias=128); r = dict(seed=sd, fit=med['fit'], t_vida=med['t_vida']['media'], mediana=med['t_vida']['mediana'], rec=med['rec'], ent=med['ent'], mortos=med['mortos']); res.append(r)
    for k, v in med.items():   # [15:55] detalhe: TODAS as medias escalares que o Rust tambem grava (panes, n_posto, n_come, litros, dinh, fome/agua fim, oficina...) para achar ONDE a economia diverge
        if isinstance(v, (int, float)) and k not in r: r[k] = float(v)
    print(f"  Python (semente {sd}): fit {r['fit']:.3f} | mortos {r['mortos']:.2f} | ent {r['ent']:.2f} | t_vida {r['t_vida']:.2f} d (mediana {r['mediana']:.2f}) | rec {r['rec']:.1f}", flush=True)
ver = {}
for k in ('fit', 't_vida', 'rec', 'ent'):
    xs = [r[k] for r in res]; m = sum(xs)/len(xs); sd_ = (sum((x - m)**2 for x in xs)/max(1, len(xs) - 1))**.5
    ver[k] = dict(python_media=m, python_dp=sd_, python_min=min(xs), python_max=max(xs), rust=rust[k], desvio_pct=100*(rust[k] - m)/m, dentro_5pct=abs(rust[k] - m) <= .05*abs(m), dentro_faixa=min(xs) <= rust[k] <= max(xs))
    print(f"  {k:7s}: Python {m:.3f} +- {sd_:.3f} [{min(xs):.3f}, {max(xs):.3f}] | Rust {rust[k]:.3f} ({ver[k]['desvio_pct']:+.1f} %) | +-5 %: {ver[k]['dentro_5pct']} | na faixa: {ver[k]['dentro_faixa']}", flush=True)
alias = {'n_oficina': 'oficina', 'dinh_fim': 'dinh'}
print('  DETALHE (Python media de 5 sementes vs Rust):', flush=True)
for k in sorted(res[0]):
    kr = alias.get(k, k)
    if k in ('seed',) or kr not in b or not isinstance(b[kr], (int, float)): continue
    xs = [r[k] for r in res]; m = sum(xs)/len(xs); d = b[kr] - m; pct = (100*d/m) if abs(m) > 1e-9 else float('nan')
    print(f'    {k:18s} Python {m:9.3f}  Rust {b[kr]:9.3f}  dif {d:+8.3f} ({pct:+.1f} %)', flush=True)
ok = ver['fit']['dentro_5pct'] and ver['t_vida']['dentro_5pct'] and all(r['mortos'] == rust['mortos'] for r in res)
print(f"  VEREDITO pred 174: {'✓' if ok else '✗'} (fit e t_vida do Rust a +-5 % da media do Python com {len(res)} sementes; mortos iguais)", flush=True)
os.makedirs(a.out, exist_ok=True); json.dump(dict(rust=rust, python=res, veredito=ver, ok=ok, W=b['W']['0']), open(os.path.join(a.out, 'juiz_python_ref.json'), 'w'), indent=1); print('gravado', os.path.join(a.out, 'juiz_python_ref.json'), flush=True)
