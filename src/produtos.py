"""E17 (doc 31): CEREBRO COM PRODUTOS — termos bilineares necessidade x distancia.

A politica do `Reativo` e LINEAR nas features: score(vizinho) = F . W. Ela tem
`e_fuel` e `d_posto` como features SEPARADAS, entao consegue dizer "gosto de
posto" e "estou com o tanque baixo", mas nunca "puxa pro posto SO QUANDO o
tanque esta baixo". Esse "so quando" e um PRODUTO, e produto nao esta no span
de uma soma ponderada de features.

E14g (doc 27 6.20) mostrou que UM produto — `-W * d_posto(vizinho) * (1-fuel/cap)`
— vale mortos 0.17 -> 0.12 e panes -1/3, com genes iguais em 5/5 sementes e
ablacao causal. Aqui a pergunta e: os outros quatro servicos pedem o mesmo?

    ReativoProduto      5 produtos necessidade_p x d_p (movimento)
                        + 2 produtos hora x necessidade_posto (servico posto)
    ReativoProdutoFull  TODOS os 12x5 = 60 produtos estado x distancia
                        (teste de BUSCA vs EXPRESSIVIDADE: a evolucao acha os
                        poucos uteis num genoma 8x maior, ou se perde?)

Contrato do lab.py: `extra()`/`extra_serv()` rodam DENTRO do torch.compile —
so tensores novos, nada in-place, nada de sync CPU<->GPU (sem .item()/.any()).
Escala (regra 15 dos NEGATIVOS): distancia crua e O(1..20) e necessidade e
O(0..1), entao o produto e O(10) — mesma ordem dos pesos de servico (O(10-20))
que ele disputa. Gene O(1) x sinal O(10) = alavanca viva; era exatamente o que
faltava ao gene de timing inerte do ReativoNoite.

Onde ficam os genes: APENDADOS depois do genoma do Reativo (NP = Reativo.NP+7
e +60), nao nos 12 pesos mortos NF+6..NF+17. Motivo: aqueles slots ja tem
significado em irmaos (ReativoNoite usa NF+6/NF+7, ReativoHora usa NF+6..NF+17,
BancoEMA usa NF+6..NF+11) e reusa-los tornaria a leitura do JSON ambigua; alem
disso o Full precisa de 60 e nao caberia. O custo e honesto e esta declarado
nas predicoes: genoma maior = busca maior (o Full existe justamente pra medir
esse custo). Zerar os genes novos reproduz o `Reativo` BIT A BIT (testes_e17).
"""
import torch
from lab import NF, DEV, Reativo

TAU = 2*3.14159265/24.

# nomes dos 60 produtos do Full (fora da classe: comprehension em corpo de
# classe nao enxerga os outros atributos da propria classe)
_EST_NOMES = ['fuel', 'fome', 'fad', 'pneu', 'temp', 'oleo', 'dinh', 'tem_pax',
              'reserva', 'h_sin', 'h_cos', 'dano']
_SERV_NOMES = ['posto', 'comida', 'descanso', 'oficina', 'loja']
_NOMES_FULL = [f'{e}x{sv}' for e in _EST_NOMES for sv in _SERV_NOMES]


class ReativoProduto(Reativo):
    """5 genes de produto no movimento + 2 de hora no servico posto.

    movimento(vizinho) += - W[B0+p] * d_p(vizinho) * nec_p      p = 0..4
    servico posto      += (W[B0+5]*sin(h) + W[B0+6]*cos(h)) * nec_posto

    Sinal: W_p POSITIVO = "aproxime-se do servico p quando precisar dele"
    (a distancia entra negada, igual ao gene `rota` do ReativoNoite24).
    Sem relogio (m.RELOGIO falso) sin/cos sao zero: os 2 genes de hora somem
    e a identidade com o mundo sem relogio fica preservada.
    """
    nome = 'reativo-produto'
    NP = Reativo.NP + 7
    B0 = Reativo.NP          # primeiro gene de produto
    NOMES = ['pr_posto', 'pr_comida', 'pr_descanso', 'pr_oficina', 'pr_loja',
             'sv_posto_hsin', 'sv_posto_hcos']

    def reset(s, m, W):
        s.W = W

    # ---- pecas puras (sem estado, sem in-place) ----
    @staticmethod
    def _nec(m):
        """(B,5) necessidade do CORPO por servico — mesma formula de
        Lote.serv_need(), SEM `sv` (disponivel no no) e SEM `paga`: aqui a
        necessidade modula a ROTA (querer ir ate la), nao a decisao de usar."""
        return torch.stack([1. - m.fuel/m.capf(), m.fome/100., m.fad/100.,
                            torch.maximum(1. - m.pneu/100., m.temp/120.),
                            (m.dinh/90.).clamp(max=1.)], -1)

    @staticmethod
    def _ds(m, viz):
        """(B,5,G) distancia de cada vizinho ate o servico mais proximo.
        Usa m.dsa (o mesmo oraculo da feature `d_*` de obs()): no mundo
        `semgps` ele ja vem zerado, entao o produto nao fura a venda."""
        G = viz.shape[1]
        return m.dsa[m.cidx[:, None, None].expand(-1, 5, G),
                     m.AR5[None, :, None].expand(m.B, -1, G),
                     viz[:, None, :].expand(-1, 5, -1)]

    @staticmethod
    def _hora(m):
        if not m.RELOGIO:
            z = torch.zeros_like(m.fuel)
            return z, z
        ang = m.hora()*TAU
        return torch.sin(ang), torch.cos(ang)

    def extra(s, m, W, viz):
        ds = s._ds(m, viz)                     # (B,5,G)
        nec = s._nec(m)                        # (B,5)
        return -torch.einsum('bp,bp,bpg->bg', W[:, s.B0:s.B0+5], nec, ds)

    def extra_serv(s, m):
        hs, hc = s._hora(m)
        nec_p = 1. - m.fuel/m.capf()
        p = (s.W[:, s.B0+5]*hs + s.W[:, s.B0+6]*hc)*nec_p
        z = torch.zeros_like(p)
        return torch.stack([p, z, z, z, z], 1)


class ReativoProdutoFull(Reativo):
    """TODOS os produtos estado x distancia: 12 estados x 5 servicos = 60 genes.

    movimento(vizinho) += - sum_{k,p} W[B0 + 5k + p] * est_k * d_p(vizinho)

    ATENCAO AO SINAL: aqui os estados sao as features de obs() como elas sao —
    e_fuel e fuel/cap (ENCHIMENTO), nao deficit. O produto equivalente ao gene
    `rota` do ReativoNoite24 (`-W*(1-fuel/cap)*d_posto`) e portanto
    W[fuel,posto] NEGATIVO (a parte linear -W*d_posto ja e expressavel pela
    feature d_posto do proprio Reativo). A analise traduz o sinal.

    So faz sentido comparado ao ReativoProduto: mesma expressividade + 53 genes
    que nao deveriam ser usados. Se a evolucao encontrar os mesmos poucos
    produtos, expressividade e de graca; se afundar, o custo e de BUSCA.
    """
    nome = 'reativo-produto-full'
    NE = 12
    NP = Reativo.NP + 60
    B0 = Reativo.NP
    EST = _EST_NOMES
    SERV = _SERV_NOMES
    NOMES = _NOMES_FULL

    def reset(s, m, W):
        s.W = W

    @staticmethod
    def _est(m):
        """(B,12) as 12 features de estado de obs() (sem os 4 slots reservados
        de E15/E16). Recalculadas aqui na mesma ordem e escala."""
        hs, hc = ReativoProduto._hora(m)
        return torch.stack([m.fuel/m.capf(), m.fome/100., m.fad/100.,
                            m.pneu/100., m.temp/120., m.oleo/100.,
                            (m.dinh/120.).clamp(max=1.),
                            (m.pd_ >= 0).float(),
                            m.res/m.cfg.RES_MAX, hs, hc,
                            1. - m.vida/100.], -1)

    def extra(s, m, W, viz):
        ds = ReativoProduto._ds(m, viz)                       # (B,5,G)
        est = s._est(m)                                       # (B,12)
        Wm = W[:, s.B0:s.B0+60].reshape(-1, s.NE, 5)          # (B,12,5) copia
        return -torch.einsum('bkp,bk,bpg->bg', Wm, est, ds)


ARQS_E17 = {'produto': ReativoProduto, 'produto_full': ReativoProdutoFull}
