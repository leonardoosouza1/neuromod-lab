"""[CS §E] ORCAMENTO DE ATIVIDADE: (1) identidade: orcamento None == antes, bit a bit; (2) a projecao segura: com B pequeno, soma_blocos |saida| <= B
em todo tick amostrado; (3) B enorme == sem orcamento (fator 1) bit a bit; (4) nao premia parar: o orcamento nao mexe no metab (custo 0 ->
metab 1.0 com ou sem orcamento) e um genoma com blocos zerados decide igual ao Linear (fator 1, nada a redistribuir)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from completo import SerCompleto
mapas = [gerar_mapa(1000, L=200., distinto=True)]; g = torch.Generator(device=DEV); g.manual_seed(5)
W = torch.randn(32, SerCompleto.NP, generator=g, device=DEV)*.3; W[:, :Linear.NP] = torch.randn(32, Linear.NP, generator=g, device=DEV)*.5
def cfg(orc):
    c = CfgCampo(L=200., fitness='riqueza'); c.orcamento_ativ = orc; return c
def test_identidade_e_teto():
    m0 = rodar(SerCompleto, W, mapas, cfg(None), T=200, seed=3, R=1); m1 = rodar(SerCompleto, W, mapas, cfg(1e9), T=200, seed=3, R=1)
    ok = torch.equal(m0.pos, m1.pos) and torch.equal(m0.vida, m1.vida); print('test_identidade: orcamento enorme == None (bit a bit):', ok, flush=True); assert ok
def test_projecao_segura():
    c = cfg(0.05); m = Campo(mapas, 32, c, seed=1, R=1); Wb = W[m.gidx]; a = SerCompleto(); a.reset(m, Wb); pior = 0.
    for t in range(60):
        F, val = m.obs(); out = a.extra(m, Wb, F); soma = sum(v.abs().mean(1) for v in a._blk.values()); fator = a._fator_orc()[:, 0]
        pior = max(pior, float((soma*fator).max())); esc = (torch.einsum('bgf,bf->bg', F, Wb[:, :NF]) + out).argmax(1); m.passo(esc); a.atualizar(m)
    ok = pior <= 0.05 + 1e-4; print(f'test_projecao_segura: max soma_blocos apos projecao {pior:.4f} <= B 0.05:', 'OK' if ok else 'FALHOU', flush=True); assert ok
def test_nao_premia_parar():
    c = cfg(0.05); m = rodar(SerCompleto, W, mapas, c, T=200, seed=3, R=1); ok1 = float((m.metab - 1.).abs().max()) == 0.
    Wz = W.clone(); Wz[:, Linear.NP:] = 0.; mz = rodar(SerCompleto, Wz, mapas, c, T=200, seed=3, R=1); ml = rodar(Linear, W[:, :Linear.NP], mapas, cfg(None), T=200, seed=3, R=1)
    ok2 = torch.equal(mz.pos, ml.pos); print('test_nao_premia_parar: metab intacto (orcamento nao e custo):', ok1, '| blocos zerados sob orcamento == Linear:', ok2, flush=True); assert ok1 and ok2
if __name__ == '__main__':
    test_identidade_e_teto(); test_projecao_segura(); test_nao_premia_parar()
