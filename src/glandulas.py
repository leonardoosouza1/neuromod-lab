"""E16 (doc 30): GLANDULAS EVOLUTIVAS — hormonios sem nome.

    "hormonio nao e controlado pelo cerebro, o corpo ajuda; precisa do reverso
     (dopamina). E estresse deve EMERGIR, nao ser roteirizado." (Leonardo)

O hormonio e do CORPO: `h` (K integradores com vazamento) vive no `Lote` e e
atualizado dentro de `passo()` — o cerebro so SENTE `h` (features e16_a/e16_b)
e e modulado por ele. Esta classe carrega apenas os GENES (tau, entradas,
saidas), que o `reset()` copia para o corpo, e aplica os dois ganhos que sao
do cerebro: necessidade (multiplicativo) e exploracao (opcional).

Genoma: NP = Reativo.NP + K*16, com 16 genes por glandula:
    [0]      log-tau  -> tau = TAU_MIN*(TAU_MAX/TAU_MIN)^sigmoide(gene), 10..2000 passos
    [1:11]   a_i      -> 6 deficits (fuel, fome, fadiga, dano, calor, pobre)
                        + 4 eventos (entregou, abasteceu, consertou, descansou)
    [11:16]  b_j      -> 5 canais (necessidade, exploracao, metabolismo, sono, velocidade)

Genes zero => h fica 0 => ganhos 1 => o Reativo e reproduzido BIT A BIT
(src/testes_e16.py). Ninguem da nome as glandulas: a analise (src/analise_
glandulas.py) le a correlacao e o sinal DEPOIS de evoluir.
"""
import math, torch
from lab import DEV, NF, Reativo

NG = 16          # genes por glandula: 1 tau + 10 entradas + 5 saidas


class SerGlandular(Reativo):
    """Reativo + K glandulas. Os genes das glandulas vao DEPOIS dos NP=44 do
    Reativo, entao os 44 primeiros pesos tem o mesmo significado (comparacao
    justa com o braco de referencia)."""
    nome = 'glandula-K2'
    K = 2
    NP = Reativo.NP + 2*NG
    expl_on = False      # ruido de exploracao modulado (opt-in; default = argmax puro)
    EXPL_ESC = .5        # escala do Gumbel quando expl_on (score de servico e O(20))

    def reset(s, m, W):
        c = m.cfg
        if not c.glandulas:
            raise ValueError('SerGlandular exige cfg.glandulas=True')
        if c.GL_K != s.K:
            raise ValueError(f'cfg.GL_K={c.GL_K} != arquitetura K={s.K}')
        s.W = W
        base = Reativo.NP
        g = W[:, base:base + s.K*NG].view(-1, s.K, NG)
        # tau LOG-UNIFORME entre TAU_MIN e TAU_MAX via sigmoide: gene ~N(0,.8)
        # nasce no meio (~141 passos) e o clamp +-5 da mutacao alcanca as pontas.
        lo, hi = math.log(c.GL_TAU_MIN), math.log(c.GL_TAU_MAX)
        m.tau = torch.exp(lo + torch.sigmoid(g[:, :, 0])*(hi - lo)).contiguous()
        m.G_a = g[:, :, 1:11].contiguous()
        m.G_b = (g[:, :, 11:16]*c.GL_ESCALA_B).contiguous()
        m.h = torch.zeros_like(m.h)
        # gerador PROPRIO do ruido: nao consome m.gsim, entao o mundo sorteado
        # e identico ao dos outros bracos (comparacao pareada)
        s.gexp = torch.Generator(device=DEV); s.gexp.manual_seed(20260902)

    def extra_serv(s, m):
        """GANHO DE NECESSIDADE, multiplicativo (EXP10: multiplicativo > aditivo,
        16/16). O score de servico e svn*W; aqui entra (ganho-1)*svn*W, de modo
        que o total vira svn*W*ganho — o hormonio ESCALA a fome do cerebro por
        servico, nao soma um empurrao cego."""
        svn, _ = m.serv_need()
        return (m.mult[:, 0:1] - 1.)*svn*s.W[:, NF:NF+5]

    def decidir(s, tudo, m):
        if not s.expl_on:
            return tudo.argmax(1)
        u = torch.rand(tudo.shape, generator=s.gexp, device=DEV).clamp(min=1e-20)
        gum = -torch.log(-torch.log(u))
        return (tudo + (s.EXPL_ESC*m.mult[:, 1:2])*gum).argmax(1)


def ser_glandular(K=2, expl=False):
    """Fabrica: SerGlandular com K glandulas (NP acompanha K)."""
    return type(f'SerGlandularK{K}', (SerGlandular,),
                dict(K=K, NP=Reativo.NP + K*NG, expl_on=expl,
                     nome=f'glandula-K{K}' + ('-expl' if expl else '')))


def genes_zero(P, K=2, base_W=None):
    """(P, NP) com os genes das glandulas zerados — reproduz o Reativo."""
    NP = Reativo.NP + K*NG
    W = torch.zeros(P, NP, device=DEV)
    if base_W is not None:
        W[:, :Reativo.NP] = base_W[:, :Reativo.NP]
    return W


def ler_genes(w, K=2, cfg=None):
    """Le os genes de UM campeao (1-D) e devolve tau, a, b em unidades fisicas."""
    from lab import Cfg
    c = cfg or Cfg()
    g = w[Reativo.NP:Reativo.NP + K*NG].reshape(K, NG)
    lo, hi = math.log(c.GL_TAU_MIN), math.log(c.GL_TAU_MAX)
    tau = torch.exp(lo + torch.sigmoid(g[:, 0])*(hi - lo))
    return tau, g[:, 1:11], g[:, 11:16]*c.GL_ESCALA_B


NOMES_X = ['def_fuel', 'def_fome', 'def_fadiga', 'def_dano', 'def_calor', 'def_pobre',
           'ev_entregou', 'ev_abasteceu', 'ev_consertou', 'ev_descansou']
