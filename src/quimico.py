"""E29a (Leonardo, cafe com leite): CEREBRO EM LOG — a politica linear sobre log(x) e uma LEI DE
POTENCIA: exp(score) = prod x_i^w_i. Com os MESMOS genes do Reativo ela expressa produtos e
razoes (tanque x distancia, necessidade / custo, L^2/D). Distancias e estados entram como
log(x + eps); sinais que ja sao sinal/limiar (semaforo, tem_pax, hora, bias) ficam lineares.
Puro em extra(): cancela o termo linear das features escolhidas e soma o termo em log."""
import torch
from lab import Reativo, NF, DEV, GMAX
from rodar import NOMES_F

# features que viram log: distancias (negativas em F: -d/6 -> usamos log(d+eps) com sinal) e estados 0..1
LOGAVEIS = ['d_alvo', 'custo_rua', 'congestao', 'd_posto', 'd_comida', 'd_descanso', 'd_oficina', 'd_loja',
            'e_fuel', 'e_fome', 'e_fadiga', 'e_pneu', 'e_temp', 'e_oleo', 'e_dinheiro', 'e_reserva', 'e_dano']
EPS = .05
import math
LOG_EPS = math.log(EPS)

class ReativoLog(Reativo):
    nome = 'reativo-log'; NP = Reativo.NP
    def reset(s, m, W):
        s.W = W; s.IDX = torch.tensor([i for i in range(NF) if NOMES_F[i] in LOGAVEIS], device=DEV, dtype=torch.long)
    def extra(s, m, W, viz):
        F, val = m.obs()                                   # (B,G,NF) — puro (recomputa)
        x = F[:, :, s.IDX]                                 # (B,G,k)
        # distancias vem como -d/6 (negativas): log da magnitude com o sinal preservado; estados 0..1: log direto
        xl = torch.sign(x)*(torch.log(x.abs() + EPS) - LOG_EPS)   # LOG_EPS e float de Python: sem tensor novo no laco (sync)
        w = W[:, None, s.IDX]
        return (xl*w).sum(-1) - (x*w).sum(-1)              # troca o termo linear pelo termo em log


# E29c: log so nos sinais do CORPO (distancias ficam lineares) — testa Weber-Fechner onde faz sentido.
CORPO_LOG = ['e_fuel', 'e_fome', 'e_fadiga', 'e_pneu', 'e_temp', 'e_oleo', 'e_dinheiro', 'e_reserva', 'e_dano']

class ReativoLogCorpo(ReativoLog):
    nome = 'reativo-log-corpo'
    def reset(s, m, W):
        super().reset(m, W)
        s.IDX = torch.tensor([i for i in range(NF) if NOMES_F[i] in CORPO_LOG], device=DEV, dtype=torch.long)
