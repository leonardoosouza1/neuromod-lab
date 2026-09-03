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
