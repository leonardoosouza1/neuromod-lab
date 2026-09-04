"""portao do E44 v2: sem prefeito == rodar() bit a bit; prefeito genes 0 == rodar(); sem sync; caixa per capita e subsidio existem."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *; from prefeito import Prefeito
c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000+s, L=200.) for s in range(3)]; W = torch.randn(16, Produto.NP, device=DEV)*.5
os.environ['NM_COMPILE'] = '0'
m1 = rodar(Produto, W, mapas, c, T=500, seed=3, R=2); m2, _ = rodar_com_prefeito(Produto, W, mapas, c, T=500, seed=3, R=2)
print('sem prefeito == rodar():', float((m1.pos-m2.pos).abs().max())==0.0 and float((m1.dinh-m2.dinh).abs().max())==0.0, flush=True)
m3, p3 = rodar_com_prefeito(Produto, W, mapas, c, T=500, seed=3, R=2, Wp=torch.zeros(3, Prefeito.NP, device=DEV), prefeito_cls=Prefeito)
print('prefeito genes 0 == rodar():', float((m1.pos-m3.pos).abs().max())==0.0, '| caixa per capita', [round(float(x),1) for x in p3.caixa], flush=True)
Wp = torch.randn(3, Prefeito.NP, device=DEV)*.5; m4, p4 = rodar_com_prefeito(Produto, W, mapas, c, T=2400, seed=3, R=2, Wp=Wp, prefeito_cls=Prefeito)
print('prefeito aleatorio 10 dias: mult', [[round(float(x),2) for x in p4.mult[i]] for i in range(3)], 'obras', p4.obras.tolist(), 'caixa', [round(float(x),1) for x in p4.caixa], 'subsidio medio/ser', round(float(m4.subs.mean()),1), 'px_ok medio', round(float(m4.px_ok.float().mean()),2), flush=True)
m = Campo(mapas, 64, c, seed=1, R=2); Wb = (torch.randn(64, Produto.NP, device=DEV)*.5)[m.gidx]; a = Produto(); a.reset(m, Wb); pref = Prefeito(m, Wp)
for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode("error"); ok = True
try:
    pref.receita(m.imp); pref.agir(1)
    for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
except RuntimeError as e: ok = False
torch.cuda.set_sync_debug_mode("default"); print('SEM SYNC (prefeito v2)' if ok else 'SYNC!', flush=True)
