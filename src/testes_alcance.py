"""portao do E52: gene k = -30 (k ~ 0) == Reflexo bit a bit; gene 0 (k 0.018) ~ Reflexo; sem sync; ativacao cresce com d_posto quando k > 0."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *
c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000, L=200.)]; os.environ['NM_COMPILE'] = '0'
Wr = torch.randn(16, Reflexo.NP, device=DEV)*.5; Wq = torch.zeros(16, ReflexoAlcance.NP, device=DEV); Wq[:, :Reflexo.NP] = Wr; Wq[:, -1] = -30.
m1 = rodar(Reflexo, Wr, mapas, c, T=300, seed=3, R=2); m2 = rodar(ReflexoAlcance, Wq, mapas, c, T=300, seed=3, R=2)
print('alcance k~0 == reflexo:', float((m1.pos-m2.pos).abs().max())==0.0, '| NP', ReflexoAlcance.NP, flush=True)
Wq[:, -1] = 0.; m3 = rodar(ReflexoAlcance, Wq, mapas, c, T=300, seed=3, R=2); print('gene 0 (k 0.018): max dif pos', round(float((m1.pos-m3.pos).abs().max()), 3), flush=True)
m = Campo(mapas, 32, c, seed=1, R=2); Wb = (torch.randn(32, ReflexoAlcance.NP, device=DEV)*.5)[m.gidx]; Wb[:, -1] = 6.; a = ReflexoAlcance(); a.reset(m, Wb)
for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode("error"); ok = True
try:
    for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
except RuntimeError as e: ok = False
torch.cuda.set_sync_debug_mode("default")
at = a._ativ(); dp = a.d_posto; cor = float(torch.corrcoef(torch.stack([at, dp]))[0, 1]) if float(at.std()) > 0 else 0.
print('SEM SYNC' if ok else 'SYNC!', '| k medio', round(float(a.k.mean()), 2), '| corr(ativacao, d_posto)', round(cor, 2), '(tem de ser > 0 com k > 0)', flush=True)
