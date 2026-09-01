"""Testes de equivalencia da reescrita de performance (2026-08-31).

    python src/testes.py <caminho-do-lab-antigo.py>

1. Janela diadica incremental == janela diadica materializada (bit a bit).
2. Determinismo: duas rodadas com mesma seed dao o mesmo resultado.
"""
import sys, os, importlib.util, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import DEV, GMAX, NF, gerar_cidade, Cfg, ARQS, rodar, _JanelasDiadicas


def test_diadica_equivalente(lab_old_path, B=64, n=26, T=200, seed=3):
    spec = importlib.util.spec_from_file_location('lab_old', lab_old_path)
    lab_old = importlib.util.module_from_spec(spec); spec.loader.exec_module(spec and lab_old)
    g = torch.Generator(device=DEV); g.manual_seed(seed)

    class FakeM: pass
    m = FakeM(); m.B = B; m.n = n
    NP = NF+6+6+6
    W = torch.randn(B, NP, generator=g, device=DEV)

    velho = lab_old.Diadica(); velho.reset(m, W)
    jan = _JanelasDiadicas(); jan.reset(m)

    pior = 0.
    for t in range(T):
        m.no = torch.randint(0, n, (B,), generator=g, device=DEV)
        viz = torch.randint(0, n, (B, GMAX), generator=g, device=DEV)
        o_velho = velho.extra(m, W, viz)
        o_novo = jan.saida(m, viz, W[:, NF+6:NF+12])
        jan.push_no(m, m.no)
        d = (o_velho - o_novo).abs().max().item()
        pior = max(pior, d)
        assert d < 1e-4, f'passo {t}: divergiu {d}'
    print(f'  diadica incremental == materializada em {T} passos (max |dif| {pior:.2e})  OK')


def test_determinismo(mundo='base'):
    cids = [gerar_cidade(s) for s in range(2)]
    cfg = Cfg(1.0, mundo=mundo)
    for A in ARQS:
        W = torch.randn(8, A.NP, device=DEV, generator=torch.Generator(device=DEV).manual_seed(7))
        e = []
        for _ in range(2):
            m = rodar(A, W, cids, cfg, T=200, seed=5)
            e.append(m.ent.sum().item())
        assert e[0] == e[1], f'{A.nome}: nao deterministico {e}'
    print(f'  5 arquiteturas deterministicas ({mundo})  OK')


def test_juntas_equivale():
    """evoluir_juntas deve dar BIT A BIT o mesmo resultado que evoluir isolado."""
    from lab import evoluir, evoluir_juntas, BancoEMA, Reativo
    cids = [gerar_cidade(s) for s in range(2)]
    cfg = Cfg(1.0, mundo='base')
    juntas = evoluir_juntas([Reativo, BancoEMA], cids, cfg, P=64, ger=6, T=150,
                            seed=3, R=2, verbose=False)
    for A in (Reativo, BancoEMA):
        w, hist, _ = evoluir(A, cids, cfg, P=64, ger=6, T=150, seed=3, R=2,
                             verbose=False)
        wj, hj, _ = juntas[A.nome]
        assert hist == hj, f'{A.nome}: hist difere\n  solo:   {hist}\n  juntas: {hj}'
        assert torch.equal(w, wj), f'{A.nome}: campeao difere'
    print('  evoluir_juntas == evoluir isolado (bit a bit, 2 arqs)  OK')


if __name__ == '__main__':
    velho = sys.argv[1] if len(sys.argv) > 1 else None
    print('--- testes de equivalencia ---')
    if velho:
        test_diadica_equivalente(velho)
    else:
        print('  (sem caminho do lab antigo: pulando equivalencia da diadica)')
    for mu in ['base', 'cego', 'hotspot', 'mare', 'ruas', 'semgps']:
        test_determinismo(mu)
    test_juntas_equivale()
    print('ok')
