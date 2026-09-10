"""[CS JARDIM-COMUM] (1) jardim_comum=False == hoje bit a bit (mesma sequencia de sorteios); (2) no jardim, o MESMO genoma replicado P
vezes da variancia EXATAMENTE zero dentro de cada bloco (pos, vida, t_vida iguais) e blocos diferentes diferem; (3) genomas diferentes
no mesmo bloco diferem (o jardim iguala o mundo, nao o ser); (4) medidas() fica fora do jardim (128 copias com bercos distintos)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from completo import SerCompleto
mapas = [gerar_mapa(1000, L=200., distinto=True), gerar_mapa(1001, L=200., distinto=True)]; g = torch.Generator(device=DEV); g.manual_seed(5)
W = torch.randn(8, Linear.NP, generator=g, device=DEV)*.5
def cfg(jc):
    c = CfgCampo(L=200., fitness='riqueza'); c.jardim_comum = jc; return c
def test_identidade():
    m0 = rodar(Linear, W, mapas, CfgCampo(L=200., fitness='riqueza'), T=300, seed=3, R=3); m1 = rodar(Linear, W, mapas, cfg(False), T=300, seed=3, R=3)
    ok = torch.equal(m0.pos, m1.pos) and torch.equal(m0.vida, m1.vida); print('test_identidade (jardim False == padrao bit a bit):', ok, flush=True); return ok
def test_mesmo_genoma_variancia_zero():
    Wr = W[:1].repeat(8, 1); m = rodar(Linear, Wr, mapas, cfg(True), T=300, seed=3, R=3); NB = m.NB
    pos = m.pos.view(8, NB, 2); tv = m.t_vida.view(8, NB); vida = m.vida.view(8, NB)
    dentro = float((pos - pos[:1]).abs().max()) + float((tv - tv[:1]).abs().max()) + float((vida - vida[:1]).abs().max())
    entre = float(pos[0].std(0).sum()); ok = dentro == 0. and entre > 1.
    print(f'test_mesmo_genoma_variancia_zero: NB {NB} blocos | diferenca maxima entre copias do MESMO genoma no mesmo bloco {dentro:.1e} (deve ser 0) | desvio entre blocos {entre:.1f} (>1)', 'OK' if ok else 'FALHOU', flush=True); return ok
def test_genomas_diferentes():
    m = rodar(Linear, W, mapas, cfg(True), T=300, seed=3, R=3); pos = m.pos.view(8, m.NB, 2); d = float((pos - pos[:1]).abs().max()); ok = d > 1.
    print(f'test_genomas_diferentes: no mesmo bloco, genomas diferentes divergem {d:.1f} (>1)', 'OK' if ok else 'FALHOU', flush=True); return ok
def test_medidas_fora_do_jardim():
    med = medidas(Linear, W[0], mapas[:1], cfg(True), T=300, seed=7777, R=1, copias=32); ok = med['t_vida']['p10'] < med['t_vida']['p90'] or med['mortos'] in (0., 1.)
    print(f"test_medidas_fora_do_jardim: t_vida p10 {med['t_vida']['p10']:.2f} p90 {med['t_vida']['p90']:.2f} (copias com bercos distintos)", 'OK' if ok else 'FALHOU', flush=True); return ok
if __name__ == '__main__':
    r = [test_identidade(), test_mesmo_genoma_variancia_zero(), test_genomas_diferentes(), test_medidas_fora_do_jardim()]; print('PORTAO JARDIM', 'ok' if all(r) else 'FALHOU', flush=True); sys.exit(0 if all(r) else 1)
