"""[E66] Sinal/ruido da NOTA de fitness: a mesma populacao avaliada em dois sorteios de mundo.
Se corr(nota_A, nota_B) entre individuos e baixa, a selecao (GA ou ES) escolhe sorte, nao genoma.
Clones (sigma 0) medem o ruido puro de avaliacao; mutantes (sigma .1/.3) medem a variancia genetica visivel."""
import sys, os, json, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *
ap = argparse.ArgumentParser(); ap.add_argument('--init-from', nargs=2, required=True); ap.add_argument('--seed-campeao', type=int, default=0)
ap.add_argument('--P', type=int, default=2048); ap.add_argument('--R', type=int, default=4); ap.add_argument('--sigmas', type=float, nargs='*', default=[0., .1, .3])
ap.add_argument('--L', type=float, default=200.); ap.add_argument('--dias', type=float, default=10.); ap.add_argument('--fitness', default='riqueza'); ap.add_argument('--mundo', default='distinto')
ap.add_argument('--kcal-pane', type=float, default=8.); ap.add_argument('--dinh0', type=float, default=10.); ap.add_argument('--guincho', type=float, default=0.); ap.add_argument('--fuel-pane', type=float, default=15.)
ap.add_argument('--seeds-mundo', type=int, nargs='*', default=[777000, 777013, 777026]); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e66'); ap.add_argument('--tag', default='')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
cfg = CfgCampo(L=a.L, fitness=a.fitness); cfg.KCAL_PANE = a.kcal_pane; cfg.dinh0 = a.dinh0; cfg.GUINCHO = a.guincho; cfg.FUEL_POS_PANE = a.fuel_pane
treino = [gerar_mapa(s, L=a.L, distinto=a.mundo == 'distinto') for s in range(4)]; T = int(240*a.dias)
J = json.load(open(a.init_from[0]))['bracos'][a.init_from[1]]['W']; W0 = torch.tensor(J[str(a.seed_campeao)], device=DEV)
assert W0.numel() == Linear.NP, f'campeao {W0.numel()} genes != Linear.NP {Linear.NP} (NM_RISCO?)'
g = torch.Generator(device=DEV); g.manual_seed(123); res = dict(P=a.P, R=a.R, T=T, seeds_mundo=a.seeds_mundo, sigmas={})
print(f'== E66 SNR da nota | P={a.P} R={a.R} T={T} campeao {a.init_from[1]} s{a.seed_campeao} | mundos {a.seeds_mundo} ==', flush=True)
for sg in a.sigmas:
    W = (W0[None, :] + torch.randn(a.P, Linear.NP, generator=g, device=DEV)*sg).clamp(-5, 5)
    F = torch.stack([avaliar(Linear, W, treino, cfg, T, seed=s, R=a.R) for s in a.seeds_mundo])      # (n_mundos, P)
    C = torch.corrcoef(F); cors = [float(C[i, j]) for i in range(len(a.seeds_mundo)) for j in range(i+1, len(a.seeds_mundo))]
    dp_ind = float(F.std(1).mean()); dp_mundo = float(F.std(0).mean())      # dispersao entre individuos (num mundo) vs entre mundos (mesmo individuo)
    top = F[0].argsort(descending=True)[:int(.15*a.P)]; sobre = [float((F[k].argsort(descending=True)[:int(.15*a.P)].unsqueeze(1) == top.unsqueeze(0)).any(1).float().mean()) for k in range(1, len(a.seeds_mundo))]
    r = dict(corr=cors, corr_media=sum(cors)/len(cors), dp_entre_individuos=dp_ind, dp_entre_mundos=dp_mundo, fit_media=float(F.mean()), elite_15pct_mantida=sobre)
    res['sigmas'][str(sg)] = r
    print(f'  sigma {sg:.2f} | corr entre mundos {r["corr_media"]:+.3f} {[round(c,3) for c in cors]} | DP entre individuos {dp_ind:.3f} vs DP do MESMO individuo entre mundos {dp_mundo:.3f} | elite 15% que continua elite noutro mundo {[round(x,2) for x in sobre]} (acaso = 0.15) | fit media {r["fit_media"]:+.2f}', flush=True)
    res['sigmas'][str(sg)]['F'] = F.cpu().tolist()   # [painel] matriz (n_mundos, P) de notas, para o grafico mundo A x mundo B
json.dump(res, open(os.path.join(a.out, f'diag_snr{a.tag}.json'), 'w'), indent=1)
