"""portao do E50: genes 0 (largura ~0) == Reflexo bit a bit; sem sync; histerese ativa com largura > 0."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *
c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000, L=200.)]; os.environ['NM_COMPILE'] = '0'
Wr = torch.randn(16, Reflexo.NP, device=DEV)*.5; Wq = torch.zeros(16, ReflexoRaizes.NP, device=DEV); Wq[:, :Reflexo.NP] = Wr; Wq[:, -1] = -30.
m1 = rodar(Reflexo, Wr, mapas, c, T=300, seed=3, R=2); m2 = rodar(ReflexoRaizes, Wq, mapas, c, T=300, seed=3, R=2)
print('raizes largura 0 == reflexo:', float((m1.pos-m2.pos).abs().max())==0.0, '| NP', ReflexoRaizes.NP, flush=True)
Wq[:, -1] = 0.; m3 = rodar(ReflexoRaizes, Wq, mapas, c, T=300, seed=3, R=2); print('gene 0 (largura 0.018): max dif pos', round(float((m1.pos-m3.pos).abs().max()), 3), flush=True)
m = Campo(mapas, 32, c, seed=1, R=2); Wb = (torch.randn(32, ReflexoRaizes.NP, device=DEV)*.5)[m.gidx]; a = ReflexoRaizes(); a.reset(m, Wb)
for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode("error"); ok = True
try:
    for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
except RuntimeError as e: ok = False
torch.cuda.set_sync_debug_mode("default"); print('SEM SYNC' if ok else 'SYNC!', '| ligados', round(float(a.ligado.mean()), 2), flush=True)
