"""E29b (doc 37 §9): REACOES — lei de acao das massas com portao e especies lentas.
Especies c_k (K=2): sede = 1 - tanque, fome/100, ambas passadas por um integrador com tau proprio
(gene). Termos de reacao no MOVIMENTO: -w_kp * relu(c_k - theta) * d_p(vizinho), so nos pares
(sede -> posto, fome -> comida); e no SERVICO: +v_k * relu(c_k - theta) * sv_p*paga. Genes: tau_k (2),
w (2), v (2), theta (1) = 7, apendados ao Reativo. Genes zero == Reativo bit a bit (sem sync)."""
import torch
from lab import Reativo, NF, DEV

class ReativoReacoes(Reativo):
    nome = 'reativo-reacoes'; NP = Reativo.NP + 7
    def reset(s, m, W):
        B = m.B; o = Reativo.NP; s.W = W
        s.tau = 1. + 200.*torch.sigmoid(W[:, o:o+2] - 4.)      # gene 0 -> ~4.6 passos (rapido por padrao)
        s.w = W[:, o+2:o+4]; s.v = W[:, o+4:o+6]
        s.theta = torch.sigmoid(W[:, o+6:o+7])                  # portao 0..1 (gene 0 -> 0.5)
        s.c = torch.zeros(B, 2, device=DEV)
    def _ativ(s):
        return (s.c - s.theta).clamp(min=0.)                    # (B,2) especie acima do portao
    def extra(s, m, W, viz):
        a = s._ativ()                                           # (B,2)
        G = viz.shape[1]
        dpos = m.dsa[m.cidx[:, None].expand(-1, G), 0, viz]      # (B,G) distancia do vizinho ao posto
        dcom = m.dsa[m.cidx[:, None].expand(-1, G), 1, viz]      # ao comida
        return -(s.w[:, 0:1]*a[:, 0:1]*dpos + s.w[:, 1:2]*a[:, 1:2]*dcom)
    def extra_serv(s, m):
        a = s._ativ(); _, svpaga = m.serv_need(); z = torch.zeros_like(a[:, 0])
        return svpaga*torch.stack([s.v[:, 0]*a[:, 0], s.v[:, 1]*a[:, 1], z, z, z], 1)
    def atualizar(s, m):
        x = torch.stack([1. - m.fuel/m.capf(), m.fome/100.], 1)
        s.c = s.c + (x - s.c)/s.tau


# E29d — ablacoes do mecanismo (intervir, nao medir):
class ReativoReflexo(ReativoReacoes):
    """tau fixo em 1 (sem especie lenta): so o reflexo instantaneo com portao. Se == reacoes, a persistencia nao conta."""
    nome = 'reativo-reflexo'
    def reset(s, m, W):
        super().reset(m, W); s.tau = torch.ones_like(s.tau)

class ReativoReacoesSemPortao(ReativoReacoes):
    """portao fixo em 0 (reacao sempre ligada, proporcional): se cair pro nivel do noite24, o que paga e o JOELHO."""
    nome = 'reativo-reacoes-sem-portao'
    def reset(s, m, W):
        super().reset(m, W); s.theta = torch.zeros_like(s.theta)


# E29e — portao POR ESPECIE (8 genes): a fome pode ligar cedo (0.6) enquanto a sede liga tarde (0.9).
class ReativoReacoes2(ReativoReacoes):
    nome = 'reativo-reacoes-2portoes'; NP = Reativo.NP + 8
    def reset(s, m, W):
        super().reset(m, W)
        o = Reativo.NP; s.theta = torch.sigmoid(W[:, o+6:o+8])   # (B,2) um portao por especie


# E30 — VIES POR SERVICO: o Reativo tem UM vies pra 5 servicos (W[NF+5]); aqui cada servico ganha o seu
# (4 genes extras: posto, comida, descanso, oficina; loja fica no vies comum). Genes 0 == base bit a bit.
from lab import NF
class ReativoVies5(Reativo):
    nome = 'reativo-vies5'; NP = Reativo.NP + 4
    def reset(s, m, W):
        s.W = W; o = Reativo.NP
        s.vb = torch.cat([W[:, o:o+4], torch.zeros(W.shape[0], 1, device=W.device)], 1)   # (B,5)
    def extra_serv(s, m): return s.vb

class ReacoesVies5(ReativoReacoes):
    nome = 'reativo-reacoes-vies5'; NP = ReativoReacoes.NP + 4
    def reset(s, m, W):
        super().reset(m, W); o = ReativoReacoes.NP
        s.vb = torch.cat([W[:, o:o+4], torch.zeros(W.shape[0], 1, device=W.device)], 1)
    def extra_serv(s, m): return super().extra_serv(m) + s.vb


# E32 — PORTAO QUE ABRE MAIS CEDO QUANTO MAIS LONGE O POSTO: theta_ef = theta - beta * d_posto_atual/8.
# 1 gene extra (beta = softplus(gene), 0 quando gene -> -inf; gene 0 -> 0.69). Com beta=0 == reacoes bit a bit.
class ReativoReacoesDist(ReativoReacoes):
    nome = 'reativo-reacoes-dist'; NP = ReativoReacoes.NP + 1
    def reset(s, m, W):
        super().reset(m, W); o = ReativoReacoes.NP
        s.beta = torch.nn.functional.softplus(W[:, o:o+1] - 4.)       # (B,1); gene 0 -> 0.018 (nasce como reacoes; E32 v1 nascia em 0.69 e matou o reflexo)
    def _ativ(s):
        return (s.c - s.th_ef).clamp(min=0.)
    def extra(s, m, W, viz):
        dp = s._m_dposto(m)
        s.th_ef = torch.cat([s.theta - s.beta*dp, s.theta], 1)          # so a SEDE abre mais cedo; fome fica
        return super().extra(m, W, viz)
    @staticmethod
    def _m_dposto(m):
        return (m.dsa[m.cidx, 0, m.no]/8.)[:, None]                      # distancia do no atual ao posto, /8


# E35 — PORTAO SEPARADO PRA ABASTECER: o desvio pro posto usa theta; encher o tanque quando JA esta no posto usa
# theta_s = sigmoid(g_theta + g_extra). Gene extra 0 -> theta_s == theta (nasce igual ao pai, regra 17).
class ReativoReacoesTopUp(ReativoReacoes):
    nome = 'reativo-reacoes-topup'; NP = ReativoReacoes.NP + 1
    def reset(s, m, W):
        super().reset(m, W); o = Reativo.NP
        s.theta_s = torch.sigmoid(W[:, o+6:o+7] + W[:, ReativoReacoes.NP:ReativoReacoes.NP+1])
    def extra_serv(s, m):
        a = torch.cat([(s.c[:, 0:1] - s.theta_s).clamp(min=0.), (s.c[:, 1:2] - s.theta).clamp(min=0.)], 1)
        _, svpaga = m.serv_need(); z = torch.zeros_like(a[:, 0])
        return svpaga*torch.stack([s.v[:, 0]*a[:, 0], s.v[:, 1]*a[:, 1], z, z, z], 1)
