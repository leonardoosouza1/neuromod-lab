"""Portoes do CAMPO (E43): identidade eager x compile por campo, genes 0 == pai, sem sync, tempo por passo. Roda SOZINHO na GPU (fila)."""
import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, campo as C
from campo import *
c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000+s, L=200.) for s in range(3)]
for A, nome in ((Linear, 'Linear'), (Produto, 'Produto'), (Reflexo, 'Reflexo')):
    W = torch.randn(64, A.NP, device=DEV)*.5
    for T in (60, 300):
        os.environ['NM_COMPILE'] = '0'; me = rodar(A, W, mapas, c, T=T, seed=3, R=2)
        os.environ['NM_COMPILE'] = '1'; mc = rodar(A, W, mapas, c, T=T, seed=3, R=2)
        d = {k: float((getattr(me, k) - getattr(mc, k)).abs().max()) for k in ('pos', 'fuel', 'agua', 'fome', 'dinh', 'ent', 'vida', 'res')}
        nd = int(((me.pos - mc.pos).abs().sum(1) > 0).sum())
        print(f'{nome} T={T}: seres com pos diferente {nd}/{me.B} | max dif', {k: (f'{v:.1e}' if v else '0') for k, v in d.items()}, flush=True)
os.environ['NM_COMPILE'] = '1'
W0 = torch.randn(64, Linear.NP, device=DEV)*.5
for A in (Produto, Reflexo):
    Wx = torch.zeros(64, A.NP, device=DEV); Wx[:, :Linear.NP] = W0
    m1 = rodar(Linear, W0, mapas, c, T=200, seed=3, R=2); m2 = rodar(A, Wx, mapas, c, T=200, seed=3, R=2)
    print(f'{A.__name__} genes 0 == Linear (compile):', float((m1.pos - m2.pos).abs().max()) == 0.0, flush=True)
m = Campo(mapas, 1024, c, seed=0, R=16); Wb = (torch.randn(1024, Produto.NP, device=DEV)*.5)[m.gidx]; a = Produto(); a.reset(m, Wb); fn = C._passo_fn()
for t in range(3): fn(m, a, Wb); a.atualizar(m)
torch.cuda.synchronize(); t0 = time.time()
for t in range(30): fn(m, a, Wb); a.atualizar(m)
torch.cuda.synchronize(); print(f'B={m.B} compilado: {(time.time()-t0)/30*1000:.2f} ms/passo', flush=True)
torch.cuda.set_sync_debug_mode("error"); ok = True
try:
    for t in range(5): fn(m, a, Wb); a.atualizar(m)
except RuntimeError as e: ok = False
torch.cuda.set_sync_debug_mode("default"); print('SEM SYNC (compilado)' if ok else 'SYNC!', flush=True)
import sys; sys.exit(0 if ok else 1)   # [revisao 09-09] exit code (ok = sem sync no passo compilado)
