"""[spec Mundo Vivo F5] test_reproducao_identidade: cfg.reproducao None -> filhos 0, res_filhos 0 (nenhum caminho novo executa; identidade
de posicao coberta por testes_cidade/campo). test_reproducao_conserva: energia gasta em filhos == energia removida da reserva (res_filhos ==
filhos*custo_kcal), reserva nunca negativa, e com reserva cheia nascem filhos (fitness 'filhos' finito)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from campo import _fit
mapas = [gerar_mapa(1000, L=200., distinto=True)]; g = torch.Generator(device=DEV); g.manual_seed(5); W = torch.randn(64, Linear.NP, generator=g, device=DEV)*.5
def test_reproducao_identidade():
    c = CfgCampo(L=200., fitness='riqueza'); m = rodar(Linear, W, mapas, c, T=300, seed=3, R=2)
    ok = float(m.filhos.sum()) == 0. and float(m.res_filhos.sum()) == 0.; print('test_reproducao_identidade: reproducao None -> filhos 0 e res_filhos 0:', ok, flush=True); assert ok
def test_reproducao_conserva():
    c = CfgCampo(L=200., fitness='filhos'); c.reproducao = dict(REPRODUCAO_PADRAO); m = Campo(mapas, 64, c, seed=3, R=2); Wb = W[m.gidx]; a = Linear(); a.reset(m, Wb)
    m.res[:] = 120.; res_min = 1e9; T = 300
    for t in range(T):
        um_passo(m, a, Wb); a.atualizar(m); res_min = min(res_min, float(m.res.min()))
    custo = c.reproducao['custo_kcal']; cons = bool(torch.allclose(m.res_filhos, m.filhos*custo)); f = _fit(m, c, T)
    ok = cons and res_min >= 0. and float(m.filhos.mean()) >= 1. and bool(torch.isfinite(f).all())
    print(f'test_reproducao_conserva: res_filhos == filhos*{custo:.0f}: {cons} | reserva minima {res_min:.1f} (>= 0) | filhos por ser {float(m.filhos.mean()):.2f} (>= 1 com reserva cheia) | fit finito', 'OK' if ok else 'FALHOU', flush=True); assert ok
if __name__ == '__main__':
    test_reproducao_identidade(); test_reproducao_conserva()
