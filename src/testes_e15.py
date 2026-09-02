"""Testes do E15 (economia real). Rodar com NM_COMPILE=0.

    NM_COMPILE=0 python src/testes_e15.py

1. fumaca: o mundo com economia roda nas 3 arquiteturas, sem NaN.
2. IDENTIDADE: economia=False nao muda nada (portao bit-exato do perito) e
   economia LIGADA com todas as constantes neutras (aliquota 0, preco 1,
   aluguel 0, juros 0, kcal 0) da bit a bit o mesmo que economia desligada.
3. divida: dinh nunca abaixo de -LIMITE_DIVIDA, e a divida realmente acontece.
4. imposto pela ORIGEM: caso construido a mao — uma entrega paga a aliquota do
   distrito onde o passageiro EMBARCOU, mesmo terminando noutro distrito.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import (DEV, GMAX, NF, gerar_cidade, Cfg, Lote, passo, Reativo,
                 ReativoNoite, ReativoNoite24, rodar)
from rodar import perito_W
from e13_corpo import cfg_corpo, _R
from e15_economia import cfg_e15


def test_fumaca():
    cids = [gerar_cidade(s) for s in range(2)]
    cfg = cfg_e15()
    for A in (Reativo, ReativoNoite, ReativoNoite24):
        W = torch.randn(4, A.NP, device=DEV,
                        generator=torch.Generator(device=DEV).manual_seed(3))*.8
        m = rodar(A, W, cids, cfg, T=200, seed=0)
        for k in ('ent', 'dinh', 'fuel', 'res', 'vida', 'imp_orig', 'imp_gastar',
                  'aluguel_pago', 'div_max', 'kcal_reb'):
            v = getattr(m, k)
            assert torch.isfinite(v).all(), f'{A.nome}: {k} nao-finito'
        assert m.t_dist.sum(1).max() <= 200 + 1e-3
    print('  fumaca economia (3 arqs, sem NaN)  OK')


def test_portao_identidade():
    """economia desligada = HEAD bit a bit (numeros do doc 28)."""
    teste = [gerar_cidade(1000+s) for s in range(3)]
    W = perito_W(Reativo.NP)[None, :].repeat(64, 1)
    m = rodar(Reativo, W, teste, Cfg(1.0, mundo='base'), T=1200, seed=7777)
    ent, avf = float(m.ent.mean()), float(m.av_fuel.mean())
    assert abs(ent - 7.9740) < 1e-4 and abs(avf - 25.1302) < 1e-4, \
        f'PORTAO QUEBRADO: ent {ent:.4f} av_fuel {avf:.4f} (esperado 7.9740 / 25.1302)'
    print(f'  portao perito base: ent {ent:.4f} av_fuel {avf:.4f}  OK')


def test_economia_neutra_e_identidade():
    """economia LIGADA com constantes neutras == economia DESLIGADA, bit a bit.
    (exercita os 4 blocos E15; o portao acima so prova que o codigo nao roda)"""
    teste = [gerar_cidade(1000+s) for s in range(3)]
    W = perito_W(Reativo.NP)[None, :].repeat(32, 1)
    off = cfg_corpo(continua=.02, **_R); off.imposto = 0.
    on = cfg_e15(aluguel=0., agua=0., juros=0., kcal=0., limite=1e9, imposto=0.,
                 aliq=(0., 0., 0.), pmul=(1., 1., 1.), D_pane=off.D_PANE)
    a = rodar(Reativo, W, teste, off, T=600, seed=7777)
    b = rodar(Reativo, W, teste, on,  T=600, seed=7777)
    for k in ('ent', 'av_fuel', 'avar', 'dinh', 'fuel', 'res', 'vida', 'rec'):
        x, y = getattr(a, k), getattr(b, k)
        assert torch.equal(x, y), (f'economia neutra divergiu em {k}: '
                                   f'{float(x.mean()):.6f} vs {float(y.mean()):.6f}')
    print('  economia neutra == economia desligada (8 tensores, bit a bit)  OK')


def test_divida_no_limite():
    """dinh nunca abaixo de -LIMITE, e a divida existe de verdade (nao vacuo)."""
    teste = [gerar_cidade(1000+s) for s in range(3)]
    W = perito_W(Reativo.NP)[None, :].repeat(32, 1)
    cfg = cfg_e15(aluguel=30., limite=40.)     # aluguel brutal: quebra na certa
    m = rodar(Reativo, W, teste, cfg, T=1200, seed=7777)
    mn = float(m.dinh.min())
    assert mn >= -cfg.LIMITE_DIVIDA - 1e-3, f'divida furou o piso: {mn:.3f} < {-cfg.LIMITE_DIVIDA}'
    assert float(m.div_max.max()) > 1., 'teste vacuo: ninguem se endividou'
    assert float(m.t_divida.max()) > 0.
    print(f'  divida no piso: min(dinh) {mn:.2f} >= -{cfg.LIMITE_DIVIDA:.0f}, '
          f'div_max medio {float(m.div_max.mean()):.1f}  OK')


def test_imposto_pela_origem():
    """caso construido: entrega que COMECOU noutro distrito paga a aliquota de la."""
    cfg = cfg_e15(sorteia=False, aluguel=0., agua=0.)   # distrito k tem ALIQ[k]
    cids = [gerar_cidade(0)]
    m = Lote(cids, 8, cfg, seed=1, R=1)
    B = m.B
    n = m.n
    # escolhe pares (origem, destino) em DISTRITOS DIFERENTES sempre que der
    dist = m.e15_dist[0]                                  # (n,) distrito de cada no
    orig = torch.arange(B, device=DEV) % n
    dest = torch.tensor([int((torch.nonzero(dist != dist[int(o)])[0, 0]).item())
                         for o in orig], device=DEV)
    m.no = dest.clone(); m.po_ = orig.clone(); m.pd_ = dest.clone()
    m.e15_dorig = m.e15_dist[m.cidx, orig]                # gravado no embarque
    m.rest = torch.zeros(B, device=DEV); m.tpar = torch.zeros(B, device=DEV)
    m.fad = torch.full((B,), 10., device=DEV)
    m.fuel = torch.full((B,), 100., device=DEV)
    m.vida = torch.full((B,), 100., device=DEV)
    m.fase_dia = torch.zeros(B, device=DEV)               # t=1 nao e meia-noite
    d0 = m.dinh.clone()
    dd = m.DIa[m.cidx, orig, dest]
    br = (cfg.base + cfg.km*dd)*m.tar()
    aliq_o = m.e15_aliq.gather(1, m.e15_dorig[:, None]).squeeze(1)
    aliq_d = m.e15_aliq.gather(1, m.e15_dist[m.cidx, dest][:, None]).squeeze(1)
    passo(m, torch.zeros(B, dtype=torch.long, device=DEV))   # acao = mover (nao gasta dinheiro)
    got = m.dinh - d0
    esp_o = br*(1. - aliq_o)                              # o correto: aliquota da ORIGEM
    esp_d = br*(1. - aliq_d)                              # o errado: aliquota do destino
    assert torch.allclose(got, esp_o, atol=1e-3), \
        f'imposto errado:\n  obtido  {got}\n  origem  {esp_o}\n  destino {esp_d}'
    dif = (dist[orig] != dist[dest])
    assert bool(dif.any()), 'teste vacuo: nenhum par cruzou distrito'
    assert not torch.allclose(got[dif], esp_d[dif], atol=1e-3), \
        'teste vacuo: origem e destino cobrariam o mesmo'
    assert torch.allclose(m.imp_orig, br*aliq_o, atol=1e-3), 'telemetria imp_receber errada'
    print(f'  imposto pela ORIGEM: {int(dif.sum())}/{B} corridas cruzaram distrito, '
          f'todas pagaram a aliquota da origem  OK')


if __name__ == '__main__':
    print('--- testes E15 (economia) ---')
    test_portao_identidade()
    test_economia_neutra_e_identidade()
    test_fumaca()
    test_divida_no_limite()
    test_imposto_pela_origem()
    print('ok')
