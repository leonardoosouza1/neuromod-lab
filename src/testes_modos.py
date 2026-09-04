"""portao do E46 Modos: genes 0 == Linear; sem sync; responsabilidades. Roda SOZINHO na GPU (fila)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *
c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000, L=200.)]
W0 = torch.randn(16, Linear.NP, device=DEV)*.5; Wm = torch.zeros(16, Modos.NP, device=DEV); Wm[:, :Linear.NP] = W0
os.environ['NM_COMPILE'] = '0'; m1 = rodar(Linear, W0, mapas, c, T=150, seed=3, R=2); m2 = rodar(Modos, Wm, mapas, c, T=150, seed=3, R=2)
print('modos genes 0 == linear:', float((m1.pos-m2.pos).abs().max())==0.0, '| NP', Modos.NP, flush=True)
m = Campo(mapas, 32, c, seed=1, R=2); Wb = (torch.randn(32, Modos.NP, device=DEV)*.5)[m.gidx]; a = Modos(); a.reset(m, Wb)
for t in range(3): um_passo(m, a, Wb); a.atualizar(m)
torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode("error"); ok = True
try:
    for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
    r = a.ativacao(m)
except RuntimeError as e: ok = False
torch.cuda.set_sync_debug_mode("default"); print('SEM SYNC' if ok else 'SYNC!', '| responsabilidade media por modo', [round(float(x), 2) for x in r.mean(0)] if ok else '', flush=True)
os.environ['NM_COMPILE'] = '1'; m3 = rodar(Modos, Wm, mapas, c, T=150, seed=3, R=2); print('modos genes 0 == linear (compile):', float((m1.pos-m3.pos).abs().max()) < 1e-5, flush=True)
