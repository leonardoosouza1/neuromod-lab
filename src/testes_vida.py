"""[spec Mundo Vivo F1] test_horizonte_identidade (fixo == antes: rodar/medidas nao mudam), test_vida_sem_teto (mundo brutal: CV de t_vida >= .15
— a regua ainda ordena onde 'mortos em 10 dias' crava em 1.00), test_teto_avisa (T_max pequeno -> frac_teto > .05)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from campo import _fit   # _fit nao vem no import *: nome com underscore
mapas = [gerar_mapa(1000, L=200., distinto=True)]; g = torch.Generator(device=DEV); g.manual_seed(5); W = torch.randn(64, Linear.NP, generator=g, device=DEV)*.5
def test_horizonte_identidade():
    c1 = CfgCampo(L=200., fitness='riqueza'); c2 = CfgCampo(L=200., fitness='riqueza'); c2.horizonte = 'fixo'; c2.T_max = 300
    m1 = rodar(Linear, W, mapas, c1, T=300, seed=3, R=2); m2 = rodar(Linear, W, mapas, c2, T=300, seed=3, R=2)
    assert torch.equal(m1.pos, m2.pos) and torch.equal(m1.vida, m2.vida) and torch.equal(m1.dinh, m2.dinh), 'horizonte fixo mudou o mundo'
    f1 = _fit(m1, c1, 300); f2 = _fit(m2, c2, 300); assert torch.equal(f1, f2); print('test_horizonte_identidade: OK (pos/vida/dinh/fit bit-iguais)', flush=True)
def test_vida_sem_teto():
    c = CfgCampo(L=200., fitness='vida'); c.horizonte = 'aberto'; c.GUINCHO = 10.; c.FUEL_POS_PANE = 5.; c.dinh0 = 5.; c.KCAL_PANE = 8.; c.T_max = 240*30
    m = rodar(Linear, W, mapas, c, T=c.T_max, seed=3, R=2); tv = m.t_vida/240.; cv = float(tv.std()/tv.mean()); mortos = float((m.vida <= 0).float().mean())
    f = _fit(m, c, c.T_max); assert f.shape == (m.B,) and bool(torch.isfinite(f).all())
    print(f'test_vida_sem_teto: mortos {mortos:.2f} (regua antiga cravaria), t_vida media {float(tv.mean()):.2f} d, CV {cv:.2f} (>= .15?)', 'OK' if cv >= .15 else 'FALHOU', '| ticks rodados <= T_max:', int(m.t), flush=True)
    assert cv >= .15
def test_teto_avisa():
    c = CfgCampo(L=200., fitness='vida'); c.horizonte = 'aberto'; c.T_max = 240
    m = rodar(Linear, W, mapas, c, T=c.T_max, seed=3, R=2); med = medidas(Linear, W[0], mapas, c, T=c.T_max, seed=3, R=1, copias=32)
    print(f"test_teto_avisa: frac_teto {med['t_vida']['frac_teto']:.2f} (> .05 esperado com 1 dia)", 'OK' if med['t_vida']['frac_teto'] > .05 else 'FALHOU', flush=True); assert med['t_vida']['frac_teto'] > .05
if __name__ == '__main__':
    test_horizonte_identidade(); test_vida_sem_teto(); test_teto_avisa()
