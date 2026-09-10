"""[CS BRAINSTORM-FORMULAS 1,2,4] (1) talamo_norm: com portoes todos ~2.0 a soma cai para NG (padrao off = soma 2*NG); (2) cortex_amp 2.0
permite (1+delta) < 0 (inverte o sinal do sentido), .5 nao; (3) temp_decisao: 0 == padrao bit a bit; .3 muda decisoes, e determinista (mesma
semente = mesma trajetoria) e NAO mexe no sorteio do mundo (passageiros iguais). Sai com exit 1 se algo falhar."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from campo import um_passo; from completo import SerCompleto, NG
mapas = [gerar_mapa(1000, L=200., distinto=True)]; g = torch.Generator(device=DEV); g.manual_seed(5)
W = torch.randn(32, SerCompleto.NP, generator=g, device=DEV)*.3; W[:, :Linear.NP] = torch.randn(32, Linear.NP, generator=g, device=DEV)*.5
def cfg(**kw):
    c = CfgCampo(L=200., fitness='riqueza')
    for k, v in kw.items(): setattr(c, k, v)
    return c
def monta(Wg, c):
    m = Campo(mapas, Wg.shape[0], c, seed=3, R=1); Wb = Wg[m.gidx]; a = SerCompleto(); a.reset(m, Wb)
    for _ in range(5): um_passo(m, a, Wb)
    return m, a
def test_talamo_norm():
    Wg = W.clone(); o = SerCompleto.O_TAL; Wg[:, o:o+SerCompleto.N_TAL:3] = 5.
    m0, a0 = monta(Wg, cfg(talamo_norm=False)); m1, a1 = monta(Wg, cfg(talamo_norm=True)); s0 = a0._gate(m0).sum(1); s1 = a1._gate(m1).sum(1)
    ok = float(s0.min()) > 1.5*NG and float((s1 - NG).abs().max()) < 1e-3
    print(f'test_talamo_norm: NG {NG} | soma dos portoes sem denominador {float(s0.mean()):.2f} (~2*NG) | com denominador {float(s1.mean()):.3f} (== NG)', 'OK' if ok else 'FALHOU', flush=True); return ok
def test_cortex_amp():
    Wg = W.clone(); o = SerCompleto.O_COR; Wg[:, o:o+SerCompleto.N_COR] = -5.
    _, a5 = monta(Wg, cfg(cortex_amp=.5)); _, a2 = monta(Wg, cfg(cortex_amp=2.)); f5 = float((1. + a5.DLT).min()); f2 = float((1. + a2.DLT).min())
    ok = f5 > 0. and f2 < 0.
    print(f'test_cortex_amp: min(1+delta) amp .5 = {f5:.2f} (nunca inverte) | amp 2.0 = {f2:.2f} (inverte o sinal do sentido)', 'OK' if ok else 'FALHOU', flush=True); return ok
def test_temp_decisao():
    m0 = rodar(SerCompleto, W, mapas, cfg(), T=200, seed=3, R=1); mz = rodar(SerCompleto, W, mapas, cfg(temp_decisao=0.), T=200, seed=3, R=1)
    ma = rodar(SerCompleto, W, mapas, cfg(temp_decisao=.3), T=200, seed=3, R=1); mb = rodar(SerCompleto, W, mapas, cfg(temp_decisao=.3), T=200, seed=3, R=1)
    ident = torch.equal(m0.pos, mz.pos) and torch.equal(m0.vida, mz.vida); muda = not torch.equal(m0.pos, ma.pos); det = torch.equal(ma.pos, mb.pos) and torch.equal(ma.vida, mb.vida)
    ok = ident and muda and det
    print(f'test_temp_decisao: T=0 == padrao {ident} | T=.3 muda a trajetoria {muda} | T=.3 determinista (2 corridas iguais) {det}', 'OK' if ok else 'FALHOU', flush=True); return ok
if __name__ == '__main__':
    r = [test_talamo_norm(), test_cortex_amp(), test_temp_decisao()]; print('PORTAO BRAINSTORM', 'ok' if all(r) else 'FALHOU', flush=True); sys.exit(0 if all(r) else 1)
