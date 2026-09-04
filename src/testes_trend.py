"""portao do E49: ProdutoTrend genes 0 == Produto (que com genes 0 == Linear); sem sync. Roda sozinho na GPU."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *
c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000, L=200.)]; os.environ['NM_COMPILE'] = '0'
Wp = torch.randn(16, Produto.NP, device=DEV)*.5; Wt = torch.zeros(16, ProdutoTrend.NP, device=DEV); Wt[:, :Produto.NP] = Wp
m1 = rodar(Produto, Wp, mapas, c, T=300, seed=3, R=2); m2 = rodar(ProdutoTrend, Wt, mapas, c, T=300, seed=3, R=2)
print('trend genes 0 == produto:', float((m1.pos-m2.pos).abs().max())==0.0, '| NP', ProdutoTrend.NP, flush=True)
m = Campo(mapas, 32, c, seed=1, R=2); Wb = (torch.randn(32, ProdutoTrend.NP, device=DEV)*.5)[m.gidx]; a = ProdutoTrend(); a.reset(m, Wb)
for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode("error"); ok = True
try:
    for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
    r = a.ativacao(m)
except RuntimeError as e: ok = False
torch.cuda.set_sync_debug_mode("default"); print('SEM SYNC' if ok else 'SYNC!', flush=True)
os.environ['NM_COMPILE'] = '1'; m3 = rodar(ProdutoTrend, Wt, mapas, c, T=300, seed=3, R=2); print('trend genes 0 == produto (compile):', float((m1.pos-m3.pos).abs().max()) < 1e-5, flush=True)
