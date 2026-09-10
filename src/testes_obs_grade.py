"""[reprojeto CS docs/70 #2] PORTAO DE TOLERANCIA do servico-mais-perto pela grade: (1) nas MESMAS posicoes (2048 seres, 2 mapas), erro da
distancia por tipo vs a busca exata (o ponto escolhido no centro da celula pode nao ser o mais perto da posicao exata): media, p95, max e
fracao de posicoes onde o ponto escolhido difere; (2) juiz: campeao linear e64 (128 copias, semente 7777) com obs_rapido vs obs_grade —
fit, mortos, t_vida dentro de +-3 %; (3) ms/tique. Tolerancia declarada: erro medio <= .5 m, p95 <= 1.5 m, |dfit| <= 3 %. Exit 1 se passar."""
import sys, os, time, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('NM_COMPILE', '0')
import torch; from campo import *; from e43_campo import alinha_semente
mapas = [gerar_mapa(1000, L=200., distinto=True), gerar_mapa(1001, L=200., distinto=True)]
c = CfgCampo(L=200., fitness='vida'); c.obs_rapido = True; m = Campo(mapas, 1024, c, seed=3, R=1)
pos = torch.rand(m.B, 2, generator=torch.Generator(device=DEV).manual_seed(9), device=DEV)*200.; m.pos = pos
pe, de = m._perto_todos_r(pos); cig, iyg, ixg = m._cel(pos); m.campo_serv_pt = torch.stack([mp['campo_serv_pt'] for mp in mapas]); pg = m.campo_serv_pt[cig, :, iyg, ixg]; dg = (pos[:, None, :] - pg).norm(dim=-1)
err = (dg - de); dif_pt = ((pg - pe).abs().sum(-1) > 1e-6).float().mean(); ok1 = float(err.mean()) <= .5 and float(err.flatten().quantile(.95)) <= 1.5
print(f'  (1) distancia por grade vs exata em {m.B} posicoes: erro medio {float(err.mean()):.3f} m | p95 {float(err.flatten().quantile(.95)):.3f} m | max {float(err.max()):.2f} m | ponto escolhido difere em {100*float(dif_pt):.1f} % (celula = {200/GR:.2f} m)', 'OK' if ok1 else 'FALHOU', flush=True)
J = json.load(open('/media/llm-data/universe-runs/neuromod-lab-taxi/e64/e43_busca8x_L200.json')); Jw = J['bracos']['linear']['W']; W = torch.tensor(alinha_semente(Jw[sorted(Jw)[0]], J.get('nomes_f')), device=DEV)
res = {}
for rot, flag in (('rapido', dict(obs_rapido=True)), ('grade', dict(obs_grade=True))):
    cc = CfgCampo(L=200., fitness='vida'); cc.horizonte = 'aberto'; cc.T_max = 2400
    for k, v in flag.items(): setattr(cc, k, v)
    torch.cuda.synchronize(); t0 = time.time(); med = medidas(Linear, W, mapas[:1], cc, T=2400, seed=7777, R=1, copias=128); torch.cuda.synchronize(); res[rot] = (med, (time.time() - t0)/2400*1000.)
fr, fg = res['rapido'][0]['fit'], res['grade'][0]['fit']; d = abs(fg - fr)/max(abs(fr), 1e-9); ok2 = d <= .03
print(f"  (2) juiz do campeao linear (128 copias): fit rapido {fr:.3f} vs grade {fg:.3f} ({100*d:.1f} %) | t_vida {res['rapido'][0]['t_vida_media']:.2f} vs {res['grade'][0]['t_vida_media']:.2f} d | mortos {res['rapido'][0]['mortos']:.2f} vs {res['grade'][0]['mortos']:.2f}", 'OK' if ok2 else 'FALHOU', flush=True)
print(f"  (3) ms/tique (128 copias): rapido {res['rapido'][1]:.2f} -> grade {res['grade'][1]:.2f} ({res['rapido'][1]/max(res['grade'][1],1e-9):.2f}x)", flush=True)
print('PORTAO OBS GRADE', 'ok' if ok1 and ok2 else 'FALHOU', flush=True); sys.exit(0 if ok1 and ok2 else 1)
