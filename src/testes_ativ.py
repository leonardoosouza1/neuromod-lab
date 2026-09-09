"""[spec Mundo Vivo F2] test_custo_identidade: (a) existencia == caminho de antes; (b) modo ativacao com lambda 0 == existencia bit a bit (os caches
nao mudam a matematica). test_custo_ativacao_gene_morto: hipocampo com pesos ENORMES mas ganho 0 (sinal sempre zero) custa cheio em
'existencia' e ~0 em 'ativacao'. test_metab_monotono: dobrar lambda dobra (metab-1)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from completo import SerCompleto, nomes_genes_completos
mapas = [gerar_mapa(1000, L=200., distinto=True)]; g = torch.Generator(device=DEV); g.manual_seed(5)
W = torch.randn(32, SerCompleto.NP, generator=g, device=DEV)*.3; W[:, :Linear.NP] = torch.randn(32, Linear.NP, generator=g, device=DEV)*.5
def cfg(modo, lam):
    c = CfgCampo(L=200., fitness='riqueza'); c.custo_modo = modo; c.custo_gene = lam; return c
def test_custo_identidade():
    m0 = rodar(SerCompleto, W, mapas, cfg('existencia', 0.), T=200, seed=3, R=1); m1 = rodar(SerCompleto, W, mapas, cfg('ativacao', 0.), T=200, seed=3, R=1)
    ok = torch.equal(m0.pos, m1.pos) and torch.equal(m0.vida, m1.vida) and torch.equal(m0.fome, m1.fome); print('test_custo_identidade (ativacao lam 0 == existencia lam 0, bit a bit):', ok, flush=True); assert ok
    m2 = rodar(SerCompleto, W, mapas, cfg('existencia', .3), T=200, seed=3, R=1); print('  existencia lam .3: metab medio', round(float(m2.metab.mean()), 3), '(> 1 = custo cobrado como antes)', flush=True); assert float(m2.metab.mean()) > 1.
def test_custo_ativacao_gene_morto():
    nomes = nomes_genes_completos(); Wd = torch.zeros(32, SerCompleto.NP, device=DEV); Wd[:, :Linear.NP] = W[:, :Linear.NP]
    o = SerCompleto.O_HIP; Wd[:, o+1] = 0.   # hip_ganho = 0 -> tanh(0) = 0: memoria SEMPRE zero
    ih = [i for i, n in enumerate(nomes) if n.startswith('hipM')]; Wd[:, Linear.NP + torch.tensor(ih, device=DEV)] = 3.   # 87 genes de M_h com peso 3 (bem acima de gene_min) mas sinal morto
    me = rodar(SerCompleto, Wd, mapas, cfg('existencia', .3), T=200, seed=3, R=1); ma = rodar(SerCompleto, Wd, mapas, cfg('ativacao', .3), T=200, seed=3, R=1)
    e, a = float(me.metab.mean()), float(ma.metab.mean()); print(f'test_custo_ativacao_gene_morto: metab existencia {e:.3f} (cobra os 87 genes mortos) vs ativacao {a:.3f} (~1.0)', 'OK' if e > 1.2 and a < 1.02 else 'FALHOU', '| ativacao_bloco hip', round(float((ma.ativ_soma['hip']/ma.ativ_n).mean()), 4), flush=True)
    assert e > 1.2 and a < 1.02
def test_metab_monotono():
    m1 = rodar(SerCompleto, W, mapas, cfg('ativacao', .3), T=200, seed=3, R=1); m2 = rodar(SerCompleto, W, mapas, cfg('ativacao', .6), T=200, seed=3, R=1)
    r = float((m2.metab - 1.).mean())/max(float((m1.metab - 1.).mean()), 1e-9); print(f'test_metab_monotono: (metab-1) lam .6 / lam .3 = {r:.3f} (esperado 2.0)', 'OK' if abs(r - 2.) < .05 else 'FALHOU', '| ativacao_bloco:', {b: round(float((v/m1.ativ_n).mean()), 3) for b, v in m1.ativ_soma.items()}, flush=True); assert abs(r - 2.) < .05
if __name__ == '__main__':
    test_custo_identidade(); test_custo_ativacao_gene_morto(); test_metab_monotono()
