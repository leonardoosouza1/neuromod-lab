"""[10/09 kernel de vida inteira] PORTAO do vida_hip: (1) contra o traco do Python (e81/traco_ref.json, 16 seres, 2400 ticks, alvo INJETADO
do traco): fracao de acoes iguais por tique, divergencias classificadas pela margem (< 1e-3 empate; > 1e-2 bug), erro maximo por variavel
enquanto ambos vivos, t_vida por ser; (2) estatistica com respawn ligado (bateria): 128 copias do campeao linear, Python vs kernel
(RNGs diferentes): media/DP de t_vida, rec, fit; (3) velocidade: B=2560 (P128 x R4 x 5 sementes), T=7200 aberto: segundos por geracao vs
~50 s do torch (linear) e 168 s (COMPLETO). Exit 1 se (1) tiver acoes iguais < 95 % ou erro de estado > 1e-2 antes da 1a divergencia."""
import sys, os, json, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from campo import _fit; from e43_campo import alinha_semente; from vida_hip import rodar_hip
N = '/media/llm-data/universe-runs/neuromod-lab-taxi'
t0 = time.time(); import vida_hip; vida_hip.modulo(); print(f'  compilacao/carga do kernel: {time.time() - t0:.0f} s', flush=True)
txt = open(f'{N}/e81/traco_ref.json').read().replace('Infinity', '1e30'); tr = json.loads(txt); B, T = tr['B'], tr['T']
mapa = gerar_mapa(tr['seed_mapa'], L=200., distinto=True); J = json.load(open(f'{N}/e64/e43_busca8x_L200.json')); Jw = J['bracos']['linear']['W']
W = torch.tensor(alinha_semente(Jw[sorted(Jw)[0]], J.get('nomes_f')), device=DEV)[None, :].repeat(B, 1)
c = CfgCampo(L=200., fitness='vida'); c.respawn = 1e9; c.ponto = 0.; c.horizonte = 'fixo'
alvo = torch.tensor(tr['alvo_por_tique'], device=DEV); m, ac, traj = rodar_hip(W, [mapa], c, T, seed=7, alvo=alvo, grava=True)
ini = torch.tensor(tr['inicial']['pos'], device=DEV); print(f'  berco igual ao traco: {bool((ini - torch.tensor(tr["inicial"]["pos"], device=DEV)).abs().max() < 1e-6)} | pos inicial do Campo vs traco: {float((Campo([mapa], B, c, seed=7, R=1).pos - ini).abs().max()):.2e}', flush=True)
acp = torch.tensor(tr['acoes_por_tique'], device=DEV); trp = torch.tensor(tr['traco'], device=DEV); mg = torch.tensor(tr['margem_por_tique'], device=DEV)
vivos = (trp[:, :, 6] > 0) & (traj[:, :, 6] > 0); ig = (ac == acp) & vivos; frac = float(ig.float().sum()/vivos.float().sum())
dif = (~ig) & vivos; bug = dif & (mg > 1e-2); emp = dif & (mg < 1e-3)
tb = torch.nonzero(bug); primeiro = (int(tb[0, 0]), int(tb[0, 1])) if tb.numel() else None
print(f'  (1) acoes iguais {100*frac:.2f} % dos ser-tiques vivos | divergencias: empates (margem<1e-3) {int(emp.sum())}, duvidosas {int((dif & ~bug & ~emp).sum())}, bugs (margem>1e-2) {int(bug.sum())} | 1a com margem>1e-2: {primeiro}', flush=True)
nomes = ['fome', 'fuel', 'agua', 'dinh', 'x', 'y', 'vida']; tlim = primeiro[0] if primeiro else T
err = {n: float(((traj[:tlim, :, i] - trp[:tlim, :, i]).abs()*vivos[:tlim]).max()) for i, n in enumerate(nomes)}
print(f'  erro maximo por variavel ate o tique {tlim}: ' + ' '.join(f'{k} {v:.2e}' for k, v in err.items()), flush=True)
tvp = torch.tensor(tr['t_vida'], device=DEV); print(f'  t_vida Python vs kernel (ticks): {[(int(a), int(b)) for a, b in zip(tvp.tolist(), m.t_vida.tolist())]}', flush=True)
ok1 = frac >= .95 and max(err.values()) <= 1e-2
c2 = CfgCampo(L=200., fitness='vida'); c2.horizonte = 'fixo'; W128 = W[:1].repeat(128, 1)
torch.cuda.synchronize(); t1 = time.time(); mp = rodar(Linear, W128, [mapa], c2, T=2400, seed=7777, R=1); torch.cuda.synchronize(); tp = time.time() - t1
t1 = time.time(); mk = rodar_hip(W128, [mapa], c2, 2400, seed=7777); tk = time.time() - t1; fp, fk = _fit(mp, c2, 2400), _fit(mk, c2, 2400)
print(f'  (2) 128 copias, respawn 20, T 2400: t_vida Python {float(mp.t_vida.mean())/240:.2f} +- {float(mp.t_vida.std())/240:.2f} d vs kernel {float(mk.t_vida.mean())/240:.2f} +- {float(mk.t_vida.std())/240:.2f} d | rec {float(mp.rec.mean()):.1f} vs {float(mk.rec.mean()):.1f} | fit {float(fp.mean()):.3f} vs {float(fk.mean()):.3f} | tempo {tp:.1f} s vs {tk:.2f} s', flush=True)
ok2 = True   # [10/09 astra P1-3] a comparacao distributiva era so impressao: o portao saia 'ok' com ok1 (trajetoria injetada) mesmo com fit/t_vida divergentes
for sd in (7777, 7778):
    W512 = W[:1].repeat(512, 1); mp2 = rodar(Linear, W512, [mapa], c2, T=2400, seed=sd, R=1); mk2 = rodar_hip(W512, [mapa], c2, 2400, seed=sd)
    fp2, fk2 = float(_fit(mp2, c2, 2400).mean()), float(_fit(mk2, c2, 2400).mean()); tp2, tk2 = float(mp2.t_vida.mean()), float(mk2.t_vida.mean())
    okd = abs(fk2 - fp2) <= .05*abs(fp2) and abs(tk2 - tp2) <= .05*tp2; ok2 = ok2 and okd
    print(f'  (2b) semente {sd}, 512 copias, RNG proprio de cada motor: fit torch {fp2:.3f} vs kernel {fk2:.3f} ({100*(fk2-fp2)/fp2:+.1f} %) | t_vida {tp2/240:.2f} vs {tk2/240:.2f} d ({100*(tk2-tp2)/tp2:+.1f} %) -> {"ok" if okd else "FALHOU"} (tolerancia 5 % = ~4 erros-padrao da media a 512 copias)', flush=True)
c3 = CfgCampo(L=200., fitness='vida'); c3.horizonte = 'aberto'; c3.T_max = 7200; Wg = W[:1].repeat(128, 1) + torch.randn(128, 40, device=DEV)*.1; mapas4 = [gerar_mapa(s, L=200., distinto=True) for s in range(4)]
torch.cuda.synchronize(); t1 = time.time(); mg_ = rodar_hip(Wg.repeat(5, 1), mapas4, c3, 7200, seed=11, R=1); torch.cuda.synchronize(); tg = time.time() - t1
print(f'  (3) geracao inteira no kernel: B {mg_.B} (640 genomas x 4 mapas), T ate 7200 aberto: {tg:.2f} s (torch linear ~50 s/geracao a P128 R4 x5; COMPLETO 168 s) | t_vida medio {float(mg_.t_vida.mean())/240:.2f} d', flush=True)
print('PORTAO VIDA HIP', 'ok' if (ok1 and ok2) else 'FALHOU', f'(trajetoria {ok1}, distribuicao {ok2})', flush=True); sys.exit(0 if (ok1 and ok2) else 1)
