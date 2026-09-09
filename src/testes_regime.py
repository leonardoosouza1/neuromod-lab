"""[spec Mundo Vivo F4] test_regime_identidade: regime None -> multiplicadores exatamente 1 e noite_ igual a formula antiga em 2400 horas;
test_regime_ciclo: media de cada multiplicador num ciclo inteiro = 1.0 +- .01 e a noite dura em media 8 h (o regime muda o QUANDO, nao o
QUANTO); sentidos est_sin/est_cos presentes e coerentes com a fase. (Identidade com NM_REGIME=0: testes_cidade/testes_campo.)"""
import sys, os, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'; assert os.environ.get('NM_REGIME') == '1', 'rodar com NM_REGIME=1'
import torch; from campo import *
mapas = [gerar_mapa(1000, L=200., distinto=True)]
def test_regime_identidade():
    c = CfgCampo(L=200.); m = Campo(mapas, 4, c, seed=3, R=1); assert m.cfg.regime is None
    for canal in ('consumo', 'preco', 'demanda', 'dia_curto'): assert float(m._mult_regime(canal)) == 1.
    ok = True
    for t in range(0, 2400, 7):
        m.t = torch.tensor(t, device=DEV); h = m.hora(); antigo = (h >= 22.) | (h < 6.); ok &= bool(torch.equal(m.noite_(), antigo))
    print('test_regime_identidade: multiplicadores == 1 e noite_ == formula antiga:', ok, flush=True); assert ok
def test_regime_ciclo():
    c = CfgCampo(L=200.); c.regime = dict(REGIME_PADRAO); m = Campo(mapas, 4, c, seed=3, R=1); T = int(240*c.regime['periodo_dias'])
    med = {k: 0. for k in ('consumo', 'preco', 'demanda')}; noite = 0.; F0 = None
    for t in range(T):
        m.t = torch.tensor(t, device=DEV)
        for k in med: med[k] += float(m._mult_regime(k))/T
        noite += float(m.noite_()[0])/T
    ok = all(abs(v - 1.) < .01 for v in med.values()) and abs(noite*24. - 8.) < .15
    m.t = torch.tensor(int(T/4), device=DEV); F, _ = m.obs(); es = float(F[0, G - 1, len(NOMES_OP) + NOMES_CORPO.index('est_sin')]); ec = float(F[0, G - 1, len(NOMES_OP) + NOMES_CORPO.index('est_cos')])
    print(f'test_regime_ciclo: medias {dict((k, round(v, 3)) for k, v in med.items())} (1.0), noite media {noite*24.:.2f} h (8), est_sin/cos em T/4 = {es:.2f}/{ec:.2f} (1/0)', 'OK' if ok and abs(es - 1.) < .05 and abs(ec) < .05 else 'FALHOU', flush=True)
    assert ok and abs(es - 1.) < .05 and abs(ec) < .05
    m.t = torch.tensor(0, device=DEV); m.passo(torch.full((m.B,), G - 1, dtype=torch.long, device=DEV)); print('  passo com regime ligado roda; pmul/demanda vem das bases:', bool(torch.allclose(m.demanda, m.demanda0*m._mult_regime('demanda'))), flush=True)
if __name__ == '__main__':
    print(f'NF {NF} sentidos {NOMES_CORPO[-2:]}', flush=True); test_regime_identidade(); test_regime_ciclo()
