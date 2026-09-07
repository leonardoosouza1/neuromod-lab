"""portao do E55: custo_gene 0 == identico (metab 1); custo > 0 muda so a fome; dof do Linear = 0; dof conta genes > gene_min."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *; from campo import dof_de; from completo import SerCompleto
os.environ['NM_COMPILE'] = '0'; mapas = [gerar_mapa(1000, L=200.)]
c0 = CfgCampo(L=200., fitness='bemestar'); c1 = CfgCampo(L=200., fitness='bemestar'); c1.custo_gene = 1.
W = torch.randn(16, SerCompleto.NP, device=DEV)*.8
m0 = rodar(SerCompleto, W, mapas, c0, T=200, seed=3, R=2); m1 = rodar(SerCompleto, W, mapas, c1, T=200, seed=3, R=2)
d = dof_de(W, c1); print('dof medio (genes > 0.5 alem da espinha):', round(float(d.mean()), 1), 'de', SerCompleto.NP - Linear.NP, '| metab medio', round(float(m1.metab.mean()), 2), flush=True)
print('custo 0: metab == 1:', bool((m0.metab == 1.).all()), '| custo 1: fome maior:', bool((m1.fome.mean() > m0.fome.mean())), f'({float(m0.fome.mean()):.1f} -> {float(m1.fome.mean()):.1f})', flush=True)
Wl = torch.randn(16, Linear.NP, device=DEV)*.8; ml = rodar(Linear, Wl, mapas, c1, T=50, seed=3, R=2); print('linear: dof', float(dof_de(Wl, c1).sum()), '== 0; metab', float(ml.metab.mean()), '== 1', flush=True)
c1.custo_gene = 0.; m2 = rodar(SerCompleto, W, mapas, c1, T=200, seed=3, R=2); print('custo 0 == baseline bit a bit:', float((m0.pos - m2.pos).abs().max()) == 0.0, flush=True)
