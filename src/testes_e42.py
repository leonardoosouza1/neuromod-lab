"""Testes do E42 cerebro em camadas (src/camadas.py).

    NM_COMPILE=0 python src/testes_e42.py     # eager (obrigatorio)
    python src/testes_e42.py                  # deixa o torch.compile tentar

1. NP e layout dos genes das 3 camadas.
2. IDENTIDADE BIT A BIT com os genes novos zerados vs ReativoReacoes — com o W do
   PERITO (+ reflexo ligado) e tambem com genomas ALEATORIOS (que tem peso nao-nulo
   em mem_0..2: e o ganho mestre do hipocampo que garante a regra 17 tambem ai).
3. extra()/extra_serv() PURAS: 5 chamadas dao o mesmo tensor e o Lote fica intacto.
4. Sem sync CPU<->GPU no laco quente (set_sync_debug_mode('error')).
5. ALAVANCA VIVA: cada camada ligada a mao MUDA a politica (gene nao e decorativo).
6. ativacao() devolve so tensores, com gate == 1 no nascimento.
7. Fumaca: genomas aleatorios, sem NaN.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, NF, Lote, um_passo, rodar, modo_execucao
from reacoes import ReativoReacoes
from e19_pacote import cfg_pacote
from rodar import perito_W
from camadas import SerCamadas, nomes_genes, NG, DMAX, IDX_CORTEX

CID_KW = dict(fome=.15, refeicao=90., comida_no_posto=True)
CFG = cfg_pacote(**CID_KW)
from lab import gerar_cidade
CID = [gerar_cidade(s) for s in range(2)]
NOVOS = SerCamadas.NP - ReativoReacoes.NP


def _W(B, NP, seed=11):
    g = torch.Generator(device=DEV); g.manual_seed(seed)
    return torch.randn(B, NP, generator=g, device=DEV)*.8


def _perito(B, NP):
    """W do perito + o reflexo do E29b ligado, como nos runners de reacoes."""
    w = perito_W(NP)
    w[ReativoReacoes.NP-7+2] = 3.      # w_sede  (W[:,44+2])
    w[ReativoReacoes.NP-7+6] = 1.      # portao  (W[:,44+6])
    return w[None, :].repeat(B, 1)


def _corrida(A, W, cfg=CFG, T=300, seed=5):
    m = rodar(A, W, CID, cfg, T=T, seed=seed)
    return (float(m.ent.sum()), float(m.av_fuel.sum()), float(m.vida.sum()),
            float(m.dinh.sum()), float(m.fome.sum()))


def test_np():
    assert SerCamadas.O_TAL == ReativoReacoes.NP == 51, SerCamadas.O_TAL
    assert SerCamadas.N_TAL == 15 and SerCamadas.O_COR == 66
    assert SerCamadas.N_COR == 24 and SerCamadas.O_HIP == 90
    assert SerCamadas.NP == 92, SerCamadas.NP
    assert len(nomes_genes()) == NOVOS == 41
    assert NG == 5 and DMAX == 6 and IDX_CORTEX == [0, 4, 1, 22]
    print(f'  layout: pai {ReativoReacoes.NP} | talamo 51..65 | cortex 66..89 | '
          f'hipocampo 90..91 | NP {SerCamadas.NP}  OK')


def test_identidade_perito():
    """o portao do doc 41: perito + reflexo, genes novos em ZERO, diferenca EXATA 0."""
    B = 16
    Wp = _perito(B, ReativoReacoes.NP)
    Wc = torch.cat([Wp, torch.zeros(B, NOVOS, device=DEV)], 1)
    m1 = rodar(ReativoReacoes, Wp, CID, CFG, T=400, seed=5)
    m2 = rodar(SerCamadas,     Wc, CID, CFG, T=400, seed=5)
    d = float((m1.ent - m2.ent).abs().max())
    assert d == 0., f'(m1.ent - m2.ent).abs().max() = {d}'
    for k in ('av_fuel', 'vida', 'dinh', 'fome', 'res', 'avar'):
        dk = float((getattr(m1, k) - getattr(m2, k)).abs().max())
        assert dk == 0., f'{k} divergiu: {dk}'
    print(f'  IDENTIDADE perito+reflexo: (m1.ent - m2.ent).abs().max() == {d:.1f} '
          f'(ent {float(m1.ent.mean()):.2f}) e 6 campos do corpo  OK')


def test_identidade_aleatoria():
    """genoma ALEATORIO: mem_0..2 tem peso nao-nulo — so o ganho mestre do
    hipocampo (gene 91 = 0) e que segura a identidade."""
    B = 32
    for sd in (11, 23):
        Wr = _W(B, ReativoReacoes.NP, seed=sd)
        assert float(Wr[:, NF+6:NF+9].abs().max()) > 0.1, 'mem_0..2 zerado: teste vazio'
        Wc = torch.cat([Wr, torch.zeros(B, NOVOS, device=DEV)], 1)
        a = _corrida(ReativoReacoes, Wr); b = _corrida(SerCamadas, Wc)
        assert a == b, f'seed {sd}: {a} vs {b}'
    print('  IDENTIDADE com 2 populacoes aleatorias (mem_* nao-nulo)  OK')


def test_pureza():
    B = 16
    W = _W(B, SerCamadas.NP)
    m = Lote(CID, B, CFG, seed=3, R=1); Wb = W[m.gidx]
    a = SerCamadas(); a.reset(m, Wb)
    viz = m.A_().clamp(min=0)
    antes_m = {k: v.clone() for k, v in vars(m).items() if torch.is_tensor(v)}
    antes_a = {k: v.clone() for k, v in vars(a).items() if torch.is_tensor(v)}
    saidas = [a.extra(m, Wb, viz) for _ in range(5)]
    svs = [a.extra_serv(m) for _ in range(5)]
    for i in range(1, 5):
        assert torch.equal(saidas[0], saidas[i]), 'extra nao e pura'
        assert torch.equal(svs[0], svs[i]), 'extra_serv nao e pura'
    for k, v in antes_m.items():
        assert torch.equal(getattr(m, k), v), f'extra mutou m.{k}'
    for k, v in antes_a.items():
        assert torch.equal(getattr(a, k), v), f'extra mutou s.{k}'
    assert saidas[0].shape == (m.B, viz.shape[1]) and torch.isfinite(saidas[0]).all()
    print('  extra/extra_serv puras (5 chamadas iguais; Lote e o proprio ser intactos)  OK')


def test_sem_sync():
    if DEV != 'cuda':
        print('  (sem GPU: pulando teste de sync)'); return
    B = 8
    W = _W(B, SerCamadas.NP)
    m = Lote(CID, B, CFG, seed=5, R=1); Wb = W[m.gidx]
    a = SerCamadas(); a.reset(m, Wb)
    for _ in range(5):
        um_passo(m, a, Wb); a.atualizar(m)        # aquecimento fora do debug
    torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode('error')
    try:
        for _ in range(10):
            um_passo(m, a, Wb); a.atualizar(m)
        _ = a.ativacao()
    finally:
        torch.cuda.set_sync_debug_mode('default')
    print('  zero sync CPU<->GPU em 10 passos + ativacao()  OK')


def test_alavancas_vivas():
    """cada camada, ligada a mao, tem que MUDAR a politica (regra 15)."""
    B = 24
    Wp = _perito(B, ReativoReacoes.NP)
    W0 = torch.cat([Wp, torch.zeros(B, NOVOS, device=DEV)], 1)
    # `pre`: peso-base que a camada precisa ter o que modular (o perito zera as
    # features do corpo e a memoria — gatear um peso ZERO nao muda nada e o teste
    # nao provaria a alavanca, so o zero).
    casos = [
        ('talamo (fecha o grupo rota: a=-3)',  SerCamadas.O_TAL + 0,       -3., {}),
        ('talamo (b do grupo corpo: +3)',      SerCamadas.O_TAL + 3*2 + 1,  3., {9: 2.}),
        ('cortex (delta d0 x d_alvo: +3)',     SerCamadas.O_COR + 0,        3., {}),
        ('hipocampo (ganho: +3)',              SerCamadas.O_HIP + 1,        3., {NF+6: 2.}),
    ]
    for nome, i, v, pre in casos:
        ref = W0.clone()
        for j, x in pre.items(): ref[:, j] = x
        W1 = ref.clone(); W1[:, i] = v
        b = _corrida(SerCamadas, ref, T=500); got = _corrida(SerCamadas, W1, T=500)
        assert got != b, f'{nome}: alavanca DECORATIVA (nada mudou)'
        print(f'    {nome:<38} ent {b[0]:9.1f} -> {got[0]:9.1f}')
    print('  4 alavancas vivas (talamo x2, cortex, hipocampo)  OK')


def test_ativacao():
    B = 12
    Wp = _perito(B, ReativoReacoes.NP)
    W0 = torch.cat([Wp, torch.zeros(B, NOVOS, device=DEV)], 1)
    m = Lote(CID, B, CFG, seed=2, R=1); Wb = W0[m.gidx]
    a = SerCamadas(); a.reset(m, Wb)
    for _ in range(60):
        um_passo(m, a, Wb); a.atualizar(m)
    at = a.ativacao()
    for k, v in at.items():
        assert torch.is_tensor(v), f'{k} nao e tensor'
        assert v.shape == (m.B,), f'{k} tem shape {tuple(v.shape)}'
        assert torch.isfinite(v).all(), f'{k} tem NaN/inf'
    for g in ('rota', 'servicos', 'corpo', 'economia', 'tempo'):
        d = float((at[f'talamo_gate_{g}'] - 1.).abs().max())
        assert d == 0., f'gate do grupo {g} nasceu != 1 ({d})'
    assert float(at['cortex_delta_abs'].max()) == 0.
    print(f'  ativacao(): {len(at)} chaves, todas tensores (B,), gate==1 e delta==0 '
          f'no nascimento  OK')


def test_fumaca():
    for sd in (99, 100):
        W = _W(64, SerCamadas.NP, seed=sd)
        e, p, v, d, f = _corrida(SerCamadas, W, T=400)
        assert e == e and v == v and d == d, 'NaN'
        print(f'    seed {sd}: ent {e/64:6.2f} panes {p/64:5.2f} vida {v/64:6.1f}')
    print('  fumaca com genomas aleatorios, sem NaN  OK')


if __name__ == '__main__':
    print(f'--- testes E42 (cerebro em camadas) | modo {modo_execucao()} | {DEV} ---')
    test_np()
    test_identidade_perito()
    test_identidade_aleatoria()
    test_pureza()
    test_sem_sync()
    test_alavancas_vivas()
    test_ativacao()
    test_fumaca()
    print('ok')
