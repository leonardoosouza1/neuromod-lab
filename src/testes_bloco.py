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
