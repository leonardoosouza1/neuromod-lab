"""Testes do E17 (produtos bilineares).

    NM_COMPILE=0 python src/testes_e17.py     # eager (rapido, obrigatorio)
    python src/testes_e17.py                  # deixa o torch.compile tentar

1. NP e layout dos genes.
2. IDENTIDADE: com os genes de produto ZERADOS, ReativoProduto e
   ReativoProdutoFull reproduzem o Reativo BIT A BIT (ent e av_fuel), com os
   mesmos pesos base e no mundo-corpo com relogio.
3. extra()/extra_serv() sao PURAS: nao mutam nada do Lote nem do proprio
   objeto, e o gradiente/valor nao depende de ordem de chamada (idempotentes).
4. Sem sync CPU<->GPU no caminho quente: nenhuma copia device->host durante
   os passos (checado por torch.cuda.set_sync_debug_mode quando ha GPU).
5. Um produto ligado a mao MUDA a politica (a alavanca nao e decorativa) e
   sem relogio os 2 genes de hora ficam inertes (identidade preservada).
6. Fumaca: rodar as duas arqs com pesos aleatorios, sem NaN.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, NF, Cfg, gerar_cidade, Reativo, rodar, modo_execucao
from e13_corpo import cfg_corpo, _R
from produtos import ReativoProduto, ReativoProdutoFull

CID = [gerar_cidade(s) for s in range(2)]
CFG = cfg_corpo(continua=.02, pena_morte=5., **_R)


def _W(B, NP, seed=11):
    g = torch.Generator(device=DEV); g.manual_seed(seed)
    return torch.randn(B, NP, generator=g, device=DEV)*.8


def test_np():
    assert ReativoProduto.NP == Reativo.NP + 7, ReativoProduto.NP
    assert ReativoProdutoFull.NP == Reativo.NP + 60, ReativoProdutoFull.NP
    assert ReativoProduto.B0 == Reativo.NP and ReativoProdutoFull.B0 == Reativo.NP
    assert len(ReativoProduto.NOMES) == 7 and len(ReativoProdutoFull.NOMES) == 60
    assert ReativoProdutoFull.NOMES[0] == 'fuelxposto'
    print(f'  NP: Reativo {Reativo.NP} | Produto {ReativoProduto.NP} | '
          f'Full {ReativoProdutoFull.NP}  OK')


def _corrida(A, W, cfg=CFG, T=300, seed=5, cids=CID):
    m = rodar(A, W, cids, cfg, T=T, seed=seed)
    return float(m.ent.mean()), float(m.av_fuel.mean()), float(m.vida.mean())


def test_identidade(cfg=CFG, rot='mundo-corpo'):
    """genes de produto zerados => a MESMA politica do Reativo, bit a bit."""
    B = 32
    Wr = _W(B, Reativo.NP)
    base = _corrida(Reativo, Wr, cfg)
    for A in (ReativoProduto, ReativoProdutoFull):
        Wp = torch.cat([Wr, torch.zeros(B, A.NP-Reativo.NP, device=DEV)], 1)
        got = _corrida(A, Wp, cfg)
        assert got == base, f'{A.nome} ({rot}) divergiu: {got} vs {base}'
    print(f'  identidade com produtos zerados ({rot}): ent {base[0]:.4f} '
          f'av_fuel {base[1]:.4f} vida {base[2]:.4f} em 3 arqs  OK')


def test_pureza():
    """extra()/extra_serv() nao podem mutar o Lote nem o objeto (contrato do
    torch.compile). Chamar 5x seguidas tem que dar sempre o MESMO tensor."""
    from lab import Lote
    B = 16
    for A in (ReativoProduto, ReativoProdutoFull):
        W = _W(B, A.NP)
        m = Lote(CID, B, CFG, seed=3, R=1)
        Wb = W[m.gidx]
        a = A(); a.reset(m, Wb)
        viz = m.A_().clamp(min=0)
        antes = {k: v.clone() for k, v in vars(m).items() if torch.is_tensor(v)}
        saidas = [a.extra(m, Wb, viz) for _ in range(5)]
        sv = [a.extra_serv(m) for _ in range(5)] if hasattr(a, 'extra_serv') else None
        for i in range(1, 5):
            assert torch.equal(saidas[0], saidas[i]), f'{A.nome}: extra nao e pura'
            if sv is not None:
                assert torch.equal(sv[0], sv[i]), f'{A.nome}: extra_serv nao e pura'
        for k, v in antes.items():
            atual = getattr(m, k)
            assert torch.equal(atual, v), f'{A.nome}: mutou m.{k}'
        assert saidas[0].shape == (m.B, viz.shape[1])
        assert torch.isfinite(saidas[0]).all()
        if sv is not None:
            assert sv[0].shape == (m.B, 5) and torch.isfinite(sv[0]).all()
    print('  extra/extra_serv puras (5 chamadas identicas, Lote intacto)  OK')


def test_sem_sync():
    """nenhuma copia device->host DENTRO do passo (zero sync, regra do lab).

    A construcao do Lote copia as cidades H2D (sync legitimo, 1x por rodada):
    o modo de debug so liga depois dela e depois de 1 passo de aquecimento.
    O `Reativo` entra como CONTROLE — se ele acusar, o sync nao e do E17."""
    if DEV != 'cuda':
        print('  (sem GPU: pulando teste de sync)'); return
    from lab import Lote, um_passo
    B = 8
    for A in (Reativo, ReativoProduto, ReativoProdutoFull):
        W = _W(B, A.NP)
        m = Lote(CID, B, CFG, seed=5, R=1)
        Wb = W[m.gidx]; a = A(); a.reset(m, Wb)
        um_passo(m, a, Wb); a.atualizar(m)          # aquecimento (fora do debug)
        torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode('error')
        try:
            for _ in range(30):
                um_passo(m, a, Wb); a.atualizar(m)
        finally:
            torch.cuda.set_sync_debug_mode('default')
    print('  zero sync CPU<->GPU em 30 passos (Reativo + 2 do E17)  OK')


def test_alavanca_viva():
    """ligar o produto do posto a mao TEM que mudar a politica (senao o gene e
    decorativo — foi o modo de falha do gene de timing, regra 15)."""
    B = 32
    Wr = _W(B, Reativo.NP)
    A = ReativoProduto
    W0 = torch.cat([Wr, torch.zeros(B, 7, device=DEV)], 1)
    W1 = W0.clone(); W1[:, A.B0] = 3.7            # o valor que a evolucao achou (E14g)
    e0, p0, v0 = _corrida(A, W0, T=600)
    e1, p1, v1 = _corrida(A, W1, T=600)
    assert (e0, p0) != (e1, p1), 'produto do posto nao mudou nada'
    print(f'  alavanca viva: pr_posto 0 -> 3.7 muda ent {e0:.2f}->{e1:.2f} '
          f'panes {p0:.2f}->{p1:.2f} vida {v0:.1f}->{v1:.1f}  OK')


def test_hora_inerte_sem_relogio():
    """sem relogio, os 2 genes de hora do ReativoProduto sao exatamente nulos."""
    cfg = Cfg(1.0, mundo='base'); cfg.pena_morte = 0.
    assert not cfg.relogio
    B = 24; A = ReativoProduto
    Wr = _W(B, Reativo.NP)
    W0 = torch.cat([Wr, torch.zeros(B, 7, device=DEV)], 1)
    W1 = W0.clone(); W1[:, A.B0+5] = 4.; W1[:, A.B0+6] = -3.
    assert _corrida(A, W0, cfg, T=300) == _corrida(A, W1, cfg, T=300), \
        'genes de hora agiram num mundo SEM relogio'
    print('  sem relogio: genes de hora exatamente inertes (identidade)  OK')


def test_fumaca():
    for A in (ReativoProduto, ReativoProdutoFull):
        W = _W(64, A.NP, seed=99)
        e, p, v = _corrida(A, W, T=400)
        assert e == e and v == v, f'{A.nome}: NaN'
        print(f'  {A.nome:<22} ent {e:6.2f} panes {p:5.2f} vida {v:6.2f}  OK')


if __name__ == '__main__':
    print(f'--- testes E17 (produtos) | modo {modo_execucao()} | {DEV} ---')
    test_np()
    test_identidade()
    cfg_sr = Cfg(1.0, mundo='base'); cfg_sr.pena_morte = 0.
    test_identidade(cfg_sr, 'base sem relogio')
    test_pureza()
    test_sem_sync()
    test_alavanca_viva()
    test_hora_inerte_sem_relogio()
    test_fumaca()
    print('ok')
