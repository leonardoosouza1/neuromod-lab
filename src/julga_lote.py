"""JUIZ EM LOTE: N politicas num processo, campeao medido UMA vez (cache), 3 sementes na triagem; --confirma re-mede o top-k com 5.
Saida: uma linha por politica + JSON com tudo (placar). Politica que falha vira linha 'ERRO' (nao derruba o lote)."""
import sys, os, json, glob, time, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from politica_util import *
ap = argparse.ArgumentParser(); ap.add_argument('--politicas', nargs='+', required=True, help='arquivos .py ou globs'); ap.add_argument('--cenario', default=None)
ap.add_argument('--campeao', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e64/e43_busca8x_L200.json'); ap.add_argument('--seeds', type=int, nargs='*', default=[7777, 7778, 7779])
ap.add_argument('--copias', type=int, default=128); ap.add_argument('--confirma', type=int, default=0, help='re-mede as k melhores com 5 sementes'); ap.add_argument('--sem-traco', action='store_true')
ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/agentes'); ap.add_argument('--tag', default='')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
arqs = sorted(set(f for p in a.politicas for f in (glob.glob(p) if any(c in p for c in '*?[') else [p])))
cfg, teste, T, chave = mundo(a.cenario); J = json.load(open(a.campeao))['bracos']['linear']['W']; Wc = torch.tensor(alinha_semente(J['0']), device=DEV); Wz = torch.zeros(Linear.NP, device=DEV)
cache = os.path.join(a.out, f'baseline_{chave}_{"-".join(map(str, a.seeds))}_{a.copias}.json')
if os.path.exists(cache): base = json.load(open(cache))
else: base = mede(Linear, Wc, cfg, teste, T, a.seeds, a.copias); json.dump(base, open(cache, 'w'))
print(f'== juiz em lote | {len(arqs)} politicas | cenario {a.cenario or "base"} | {len(a.seeds)} sementes x {a.copias} copias x 3 mapas ==', flush=True)
print('  ' + linha('CAMPEAO evoluido (referencia)', base), flush=True)
res = []
for f in arqs:
    t0 = time.time(); nome = os.path.basename(f).replace('.politica.py', '').replace('.py', ''); POL, erro = carrega(f)
    if erro: print(f'  {nome[:34]:<34} ERRO {erro}', flush=True); res.append(dict(politica=f, nome=nome, erro=erro)); continue
    try:
        med = mede(POL, Wz, cfg, teste, T, a.seeds, a.copias); tr = None if a.sem_traco else traco(POL, Wz, cfg, teste)
        med['dif_mortos'] = med['mortos'] - base['mortos']; print('  ' + linha(nome, med, tr) + f' ({time.time()-t0:.0f}s)', flush=True); res.append(dict(politica=f, nome=nome, med=med, traco=tr))
    except Exception as e: print(f'  {nome[:34]:<34} ERRO exec {type(e).__name__}: {str(e)[:140]}', flush=True); res.append(dict(politica=f, nome=nome, erro=f'{type(e).__name__}: {str(e)[:140]}'))
ok = sorted([r for r in res if 'med' in r], key=lambda r: r['med']['mortos'])
if a.confirma and ok:
    print(f'== confirmacao: top {a.confirma} com 5 sementes ==', flush=True); s5 = [7777, 7778, 7779, 7780, 7781]
    c5 = os.path.join(a.out, f'baseline_{chave}_5s_{a.copias}.json'); b5 = json.load(open(c5)) if os.path.exists(c5) else mede(Linear, Wc, cfg, teste, T, s5, a.copias); json.dump(b5, open(c5, 'w'))
    print('  ' + linha('CAMPEAO (5 sementes)', b5), flush=True)
    for r in ok[:a.confirma]:
        POL, _ = carrega(r['politica']); m5 = mede(POL, Wz, cfg, teste, T, s5, a.copias); m5['dif_mortos'] = m5['mortos'] - b5['mortos']; r['med5'] = m5; print('  ' + linha(r['nome'] + ' (5s)', m5), flush=True)
json.dump(dict(cenario=a.cenario, seeds=a.seeds, copias=a.copias, baseline=base, res=res), open(os.path.join(a.out, f'lote{a.tag}.json'), 'w'), indent=1)
print(f'== fim: {len(ok)}/{len(arqs)} medidas; melhor {ok[0]["nome"] if ok else "-"} {ok[0]["med"]["mortos"] if ok else ""} ==', flush=True)
