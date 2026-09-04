"""portao do E48: comite com genes 0 (dW=0) == Linear; W0_comite reproduz a media dos campeoes; inercia move r; sem sync. Roda sozinho na GPU."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *
c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000, L=200.)]; os.environ['NM_COMPILE'] = '0'
W0 = torch.randn(16, Linear.NP, device=DEV)*.5; Wc = torch.zeros(16, Comite.NP, device=DEV); Wc[:, :Linear.NP] = W0
m1 = rodar(Linear, W0, mapas, c, T=150, seed=3, R=2); m2 = rodar(Comite, Wc, mapas, c, T=150, seed=3, R=2)
print('comite genes 0 == linear:', float((m1.pos-m2.pos).abs().max())==0.0, '| NP', Comite.NP, flush=True)
J = json.load(open('/media/llm-data/universe-runs/neuromod-lab-taxi/e43/e43_triagem_L200_10d.json'))['bracos']
Wk = W0_comite([J[n]['W']['0'] for n in ('linear', 'reflexo', 'produto (need x dist, portao)', 'minimo 3 (d_alvo, d_posto, e_fuel)')])
m = Campo(mapas, 32, c, seed=1, R=2); Wb = (Wk[None, :] + torch.randn(32, Comite.NP, device=DEV)*.2)[m.gidx]; a = Comite(); a.reset(m, Wb)
for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode("error"); ok = True
try:
    for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
    r = a.ativacao(m)
except RuntimeError as e: ok = False
torch.cuda.set_sync_debug_mode("default"); print('SEM SYNC' if ok else 'SYNC!', '| responsabilidade media', [round(float(x), 2) for x in r.mean(0)] if ok else '', '| tau medio', round(float(a.tau.mean()), 1), flush=True)
med = medidas(Comite, Wk, mapas, c, T=2400, seed=7777, R=1, copias=64); print(f"comite W0 (media dos campeoes, sem evoluir): mortos {med['mortos']:.2f} ent {med['ent']:.1f}", flush=True)
