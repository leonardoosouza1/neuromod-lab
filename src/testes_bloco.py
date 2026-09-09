"""[spec Mundo Vivo I1a] test_dof_bloco_soma: a decomposicao por bloco nao perde nem inventa gene — soma dos blocos == dof_de, nos dois modos
(degrau e custo_suave), para SerCompleto e partes; nomes cobrem exatamente NP - Linear.NP; Linear devolve {}."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *; from completo import SerCompleto, SoCamadas, SemTalamo, nomes_genes_completos
def test_dof_bloco_soma():
    n = nomes_genes_completos(); assert len(n) == SerCompleto.NP - Linear.NP, (len(n), SerCompleto.NP - Linear.NP)
    assert len(set(n)) == len(n), 'nomes repetidos'
    pre = {b: sum(x.startswith(b) for x in n) for b in BLOCOS}; assert sum(pre.values()) == len(n), pre
    g = torch.Generator(device=DEV); g.manual_seed(3); W = torch.randn(64, SerCompleto.NP, generator=g, device=DEV)*.8
    for suave in (False, True):
        for gm in (.5, .2, 1.):
            c = CfgCampo(L=200.); c.gene_min = gm; c.custo_suave = suave
            db = dof_por_bloco(W, c, SerCompleto); tot = float(dof_de(W, c).mean())
            assert abs(sum(db.values()) - tot) < 1e-3, (suave, gm, sum(db.values()), tot)
    assert dof_por_bloco(torch.randn(8, Linear.NP, device=DEV), CfgCampo(L=200.), Linear) == {}
    for A in (SoCamadas, SemTalamo): assert set(dof_por_bloco(W, CfgCampo(L=200.), A)) == set(pre) - {b for b in pre if pre[b] == 0}
    print('test_dof_bloco_soma: OK |', {b: pre[b] for b in BLOCOS}, '| exemplo dof_bloco:', {k: round(v, 1) for k, v in dof_por_bloco(W, CfgCampo(L=200.), SerCompleto).items()}, flush=True)
if __name__ == '__main__': test_dof_bloco_soma()

def test_grupos_por_nome():
    """[pre-F3] GRUPOS por nome == os indices cravados de antes (0..23 + extras no corpo), para o layout de hoje (NM_RISCO=1 NM_PONTO=1: NF 29)."""
    from completo import GRUPOS
    antigo = {'rota': [0, 6, 9, 18], 'servicos': [1, 2, 3, 4, 5], 'corpo': sorted([10, 11, 12, 13, 14, 15, 24, 25] + list(range(26, NF))), 'economia': [7, 8, 16, 17], 'tempo': [19, 20, 21, 22, 23]}
    novo = dict(GRUPOS); assert novo == antigo, (novo, antigo)
    assert sorted(i for _, ids in GRUPOS for i in ids) == list(range(NF)); print('test_grupos_por_nome: OK (indices identicos aos cravados; cobrem NF =', NF, ')', flush=True)
if __name__ == '__main__': test_grupos_por_nome()

def test_alinha_semente_nome():
    """[pre-F3] alinhamento por nome reproduz o alinhamento antigo (zeros no fim do corpo) para os layouts conhecidos, e mapeia certo com nomes_f."""
    from e43_campo import alinha_semente, _LAYOUTS
    for np_old, nf_old in _LAYOUTS.items():
        if np_old >= Linear.NP: continue
        v = [float(i + 1) for i in range(np_old)]; a = alinha_semente(v)
        assert len(a) == Linear.NP and all(a[NOMES_F.index(n)] == v[i] for i, n in enumerate(nf_old)), np_old
        assert all(a[i] == 0. for i, n in enumerate(NOMES_F) if n not in nf_old)
    perm = list(reversed(NOMES_F)); v = [float(i) for i in range(len(perm))]; a = alinha_semente(v, perm); assert all(a[NOMES_F.index(n)] == v[i] for i, n in enumerate(perm))
    print('test_alinha_semente_nome: OK (layouts', sorted(_LAYOUTS), '-> NP', Linear.NP, ')', flush=True)
if __name__ == '__main__': test_alinha_semente_nome()
