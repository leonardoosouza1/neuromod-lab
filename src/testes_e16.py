"""Testes do E16 — glandulas evolutivas (doc 30).

    NM_COMPILE=0 python src/testes_e16.py

1. identidade: cfg.glandulas=False nao muda NADA (portao do perito, bit a bit)
2. genes zero: h fica 0 e o Reativo e reproduzido BIT A BIT
3. h respeita [0, H_MAX] mesmo com genes extremos
4. custo calorico so quando h > 0
5. sono (descanso) reduz h pela metade
6. os ganhos respeitam o clamp por canal
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, GMAX, NF, Cfg, Lote, Reativo, gerar_cidade, rodar, passo
from glandulas import SerGlandular, ser_glandular, NG
from rodar import perito_W
from e16_glandulas import cfg_gl


def _cids(k=3, s0=1000):
    return [gerar_cidade(s0 + i) for i in range(k)]


def test_identidade_portao():
    """glandulas=False: o mundo tem de ser o mesmo do dia anterior, bit a bit."""
    W = perito_W(Reativo.NP)[None, :].repeat(64, 1)
    m = rodar(Reativo, W, _cids(), Cfg(1.0, mundo='base'), T=1200, seed=7777)
    ent, avf = float(m.ent.mean()), float(m.av_fuel.mean())
    assert abs(ent - 7.9740) < 1e-4 and abs(avf - 25.1302) < 1e-4, \
        f'PORTAO QUEBRADO: ent {ent:.4f} av_fuel {avf:.4f} (esperado 7.9740 / 25.1302)'
    print(f'  1. portao do perito intacto (ent {ent:.4f} av_fuel {avf:.4f})  OK')


def test_genes_zero_reproduz_reativo():
    """Genes das glandulas zerados => h=0, ganhos=1 => Reativo BIT A BIT."""
    cids = _cids()
    g = torch.Generator(device=DEV); g.manual_seed(11)
    Wr = torch.randn(32, Reativo.NP, generator=g, device=DEV)*.8
    A = ser_glandular(2)
    Wg = torch.zeros(32, A.NP, device=DEV); Wg[:, :Reativo.NP] = Wr
    for kw in ({}, dict(continua=.02)):
        c0 = cfg_gl(glandulas=False, **kw)
        c1 = cfg_gl(glandulas=True, K=2, **kw)
        m0 = rodar(Reativo, Wr, cids, c0, T=400, seed=99)
        m1 = rodar(A,       Wg, cids, c1, T=400, seed=99)
        assert torch.equal(m0.ent, m1.ent), 'entregas divergiram'
        assert torch.equal(m0.fuel, m1.fuel), 'tanque divergiu'
        assert torch.equal(m0.avar, m1.avar), 'avarias divergiram'
        assert torch.equal(m0.vida, m1.vida), 'vida divergiu'
        assert float(m1.h.abs().max()) == 0., 'h nao ficou em zero'
        assert float(m1.h_custo.sum()) == 0., 'cobrou caloria com h=0'
    print('  2. genes zero == Reativo bit a bit (2 mundos), h=0, custo 0  OK')


def _W_glandular(P, K, a_def=None, a_ev=None, b=None, tau_gene=0., seed=5):
    """Genoma do perito + genes de glandula escritos a mao."""
    A = ser_glandular(K)
    W = perito_W(Reativo.NP)[None, :].repeat(P, 1)
    W = torch.cat([W, torch.zeros(P, K*NG, device=DEV)], 1)
    for k in range(K):
        o = Reativo.NP + k*NG
        W[:, o] = tau_gene
        if a_def is not None: W[:, o+1:o+7] = torch.tensor(a_def[k], device=DEV)
        if a_ev is not None:  W[:, o+7:o+11] = torch.tensor(a_ev[k], device=DEV)
        if b is not None:     W[:, o+11:o+16] = torch.tensor(b[k], device=DEV)
    return A, W


def test_h_no_intervalo():
    """Genes extremos (todos os deficits com peso maximo) nao estouram H_MAX."""
    K = 2
    A, W = _W_glandular(64, K, a_def=[[5.]*6]*K, a_ev=[[5.]*4]*K,
                        b=[[5., 5., -5., 5., -5.]]*K, tau_gene=-5.)
    c = cfg_gl(glandulas=True, K=K, continua=.02)
    m = rodar(A, W, _cids(), c, T=400, seed=99)
    hi = float(m.h.max()); lo = float(m.h.min())
    assert lo >= 0. and hi <= c.H_MAX + 1e-6, f'h fora de [0,{c.H_MAX}]: {lo}..{hi}'
    # media ao longo da vida tambem
    hm = float((m.h_soma/m.h_n).max())
    assert 0. <= hm <= c.H_MAX + 1e-6, f'media de h fora do intervalo: {hm}'
    mu = m.mult_soma/m.h_n
    for j, (a, b_) in enumerate(c.GL_LIM):
        v = mu[:, j]
        assert float(v.min()) >= a - 1e-5 and float(v.max()) <= b_ + 1e-5, \
            f'canal {c.GL_CANAIS[j]} fora do clamp [{a},{b_}]: {float(v.min())}..{float(v.max())}'
    print(f'  3. h em [0,{c.H_MAX}] (max {hi:.3f}) e ganhos dentro do clamp por canal  OK')


def test_custo_so_com_h():
    """Custo calorico > 0 quando h > 0; exatamente 0 quando h = 0."""
    K = 1
    c = cfg_gl(glandulas=True, K=K, continua=.02)
    A, W1 = _W_glandular(64, K, a_def=[[3., 0., 0., 0., 0., 0.]], b=[[0.]*5])
    m1 = rodar(A, W1, _cids(), c, T=400, seed=99)
    A, W0 = _W_glandular(64, K, a_def=[[0.]*6], b=[[0.]*5])
    m0 = rodar(A, W0, _cids(), c, T=400, seed=99)
    h1 = float(m1.h_soma.mean()/m1.h_n); cu1 = float(m1.h_custo.mean())
    assert h1 > 0. and cu1 > 0., f'h {h1} custo {cu1}: hormonio ligado nao cobrou'
    assert float(m0.h_custo.abs().max()) == 0., 'cobrou com h=0'
    # a conta bate com KAPPA_H * soma de h ao longo da vida (so vivos)
    esperado = c.KAPPA_H*float(m1.h_soma.sum())
    assert abs(cu1*m1.B - esperado)/max(esperado, 1e-9) < .30, \
        f'custo {cu1*m1.B:.1f} vs KAPPA_H*sum(h) {esperado:.1f} (diferenca = passos de ser morto)'
    print(f'  4. custo calorico so com h>0 (h~ {h1:.3f}, custo {cu1:.1f} de fuel/vida)  OK')


def test_sono_limpa_h():
    """Descansar corta h pela metade — teste direto, um passo forcado."""
    K = 1
    cids = _cids(2)
    c = cfg_gl(glandulas=True, K=K, continua=.02)
    A, W = _W_glandular(16, K, a_def=[[3., 0., 0., 0., 0., 0.]], b=[[0.]*5])
    m = Lote(cids, 16, c, seed=3, R=1)
    a = A(); Wb = W[m.gidx]; a.reset(m, Wb)
    # poe todo mundo num no com DESCANSO aberto e h alto
    no_desc = []
    for ci in cids:
        idx = [i for i in range(ci['n']) if ci['serv'][i, 2] > 0]
        no_desc.append(idx[0])
    m.no = torch.tensor(no_desc, device=DEV)[m.cidx]
    m.h = torch.full_like(m.h, 1.5)
    antes = m.h.clone()
    esc = torch.full((m.B,), GMAX + 2, dtype=torch.long, device=DEV)
    passo(m, esc)
    # h_apos = (h_atualizado)*0.5 ; com deficit de fuel o drive e pequeno (1/tau)
    raz = float((m.h/antes).mean())
    assert 0.45 < raz < 0.56, f'sono nao cortou h pela metade (razao {raz:.3f})'
    assert float(m.h_sono.mean()) > 0., 'telemetria do sono ficou zerada'
    print(f'  5. descansar corta h pela metade (razao {raz:.3f})  OK')


def test_ganho_necessidade_multiplicativo():
    """extra_serv devolve (ganho-1)*svn*W: somado ao score da base da svn*W*ganho."""
    K = 1
    c = cfg_gl(glandulas=True, K=K, continua=.02)
    A, W = _W_glandular(8, K, a_def=[[3.]+[0.]*5], b=[[4., 0., 0., 0., 0.]])
    m = Lote(_cids(2), 8, c, seed=3, R=1)
    a = A(); Wb = W[m.gidx]; a.reset(m, Wb)
    m.h = torch.full_like(m.h, 1.)
    m.mult = torch.clamp(1. + (m.G_b*m.h[:, :, None]).sum(1), m.GL_LO, m.GL_HI)
    svn, _ = m.serv_need()
    base = svn*Wb[:, NF:NF+5]
    tot = base + a.extra_serv(m)
    alvo = base*m.mult[:, 0:1]
    assert float((tot - alvo).abs().max()) < 1e-4, 'ganho de necessidade nao ficou multiplicativo'
    print(f'  6. ganho de necessidade multiplicativo (ganho {float(m.mult[0,0]):.2f}x)  OK')


if __name__ == '__main__':
    print('--- testes E16 (glandulas) ---')
    test_identidade_portao()
    test_genes_zero_reproduz_reativo()
    test_h_no_intervalo()
    test_custo_so_com_h()
    test_sono_limpa_h()
    test_ganho_necessidade_multiplicativo()
    print('ok')
