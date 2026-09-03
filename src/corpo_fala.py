"""E20 (doc 36): O CORPO FALA — o cerebro deixa de ver o corpo cru e so recebe hormonios.

Uma rede pequena do CORPO (8 sinais -> 6 tanh -> K sigmoides, com lentidao tau por
hormonio) produz K hormonios; o cerebro (Reativo) tem os pesos das features do corpo
CANCELADOS (gargalo) e decide servicos so pelos hormonios: ss = sv*paga*(h @ Gserv) + bias,
e o movimento ganha um vies por hormonio (h @ Gmov). Tudo no genoma (co-evolucao no mesmo
fitness). `redundante=True` = o cerebro ve o corpo cru E os hormonios (controle).
Nada de lab.py: cancelamento feito em extra()/extra_serv() (puras); estado h atualizado em
atualizar() (in-place, fora do grafo). Hormonio atrasa 1 passo por construcao.
"""
import torch
from lab import Reativo, NF, DEV

# indices das features do CORPO em F (ver Lote.obs / NOMES_F): fuel, fome, fad, pneu, temp,
# oleo, dinh, res, dano, e_divida  (tem_pax, hora e preco local NAO sao corpo)
IDX_CORPO = [9, 10, 11, 12, 13, 14, 15, 17, 20, 21]
NX, NH = 8, 6

def _sinais(m):
    """(B,8) o que o CORPO sente (mesma escala das features de obs)."""
    return torch.stack([1. - m.fuel/m.capf(), m.fome/100., m.fad/100., 1. - m.vida/100.,
                        m.temp/120., 1. - m.pneu/100., (m.dinh/90.).clamp(-1., 1.),
                        m.res/m.cfg.RES_MAX], -1)

def _feat_corpo(m):
    """(B,10) as features do corpo EXATAMENTE como obs() as monta (pra cancelar)."""
    c = m.cfg
    div = ((-m.dinh/c.LIMITE_DIVIDA).clamp(0., 1.) if c.economia else torch.zeros_like(m.fuel))
    return torch.stack([m.fuel/m.capf(), m.fome/100., m.fad/100., m.pneu/100., m.temp/120.,
                        m.oleo/100., (m.dinh/120.).clamp(max=1.), m.res/c.RES_MAX,
                        1. - m.vida/100., div], -1)

def fabrica(K=2, redundante=False, nome=None, prior_corpo=False, prior_cerebro=False):
    """prior_corpo: o corpo NASCE sabendo dizer fome (h0) e sede de gasolina (h1) — codigo herdado
    que a evolucao refina (u = sigmoid(rede(x) + 8*(x_k - 0.55))). prior_cerebro: o cerebro nasce
    ouvindo (Gserv += 10 em comida<-h0 e posto<-h1). Triagem 1 (sem prior): 97 % morrem de fome —
    82-110 genes em G=40 nao acham o codigo e o deserto tira o gradiente."""
    n_body = NX*NH + NH + NH*K + K + K + K*5 + K
    class SerCorpoFala(Reativo):
        NP = Reativo.NP + n_body
        def reset(s, m, W):
            B = m.B; s.W = W; s.K = K; s.red = redundante
            o = Reativo.NP
            s.W1 = W[:, o:o+NX*NH].reshape(B, NX, NH); o += NX*NH
            s.b1 = W[:, o:o+NH]; o += NH
            s.W2 = W[:, o:o+NH*K].reshape(B, NH, K); o += NH*K
            s.b2 = W[:, o:o+K]; o += K
            # tau: gene 0 -> ~4.6 passos (RAPIDO por padrao; a evolucao alonga se quiser). Triagem 2:
            # com gene 0 -> ~101 passos a "sede" ficava alta 100 passos depois de abastecer e o posto
            # (que vende comida) ganhava da comida no mesmo no -> loop de abastecer, 90-98 % de fome.
            s.tau = 1. + 200.*torch.sigmoid(W[:, o:o+K] - 4.); o += K   # 1..201 passos
            s.Gserv = W[:, o:o+K*5].reshape(B, K, 5); o += K*5
            s.Gmov = W[:, o:o+K]; o += K
            s.h = torch.zeros(B, K, device=DEV)
            s.h_soma = torch.zeros(B, K, device=DEV); s.n = torch.zeros((), device=DEV)
            s.IDX = torch.tensor(IDX_CORPO, device=DEV)
            s.Pc = None; s.Pb = None
            if prior_corpo:   # (K,8): h0 <- fome (x[1]), h1 <- sede de gasolina (x[0]); resto 0
                Pc = torch.zeros(K, NX, device=DEV); Pc[0, 1] = 8.
                if K > 1: Pc[1, 0] = 8.
                s.Pc = Pc
            if prior_cerebro:  # (K,5): comida <- h0, posto <- h1
                Pb = torch.zeros(K, 5, device=DEV); Pb[0, 1] = 10.
                if K > 1: Pb[1, 0] = 10.
                s.Pb = Pb
        def extra(s, m, W, viz):
            mov = (s.h*s.Gmov).sum(1, keepdim=True)                       # (B,1) vies por hormonio
            if s.red: return mov
            fc = _feat_corpo(m)                                            # (B,10)
            cancel = (fc*W[:, s.IDX]).sum(1, keepdim=True)                 # o que o corpo cru somava
            return mov - cancel
        def extra_serv(s, m):
            svn, svpaga = m.serv_need()
            G = s.Gserv if s.Pb is None else s.Gserv + s.Pb[None]
            ss_h = svpaga*torch.einsum('bk,bkp->bp', s.h, G)
            if s.red: return ss_h
            return ss_h - svn*s.W[:, NF:NF+5]                              # cancela a necessidade crua
        def atualizar(s, m):
            x = _sinais(m)
            z = torch.tanh(torch.einsum('bx,bxh->bh', x, s.W1) + s.b1)
            pre = torch.einsum('bh,bhk->bk', z, s.W2) + s.b2
            if s.Pc is not None: pre = pre + torch.einsum('bx,kx->bk', x - 0.55, s.Pc)
            u = torch.sigmoid(pre)
            s.h = s.h + (u - s.h)/s.tau
            s.h_soma += s.h; s.n = s.n + 1
    SerCorpoFala.nome = nome or (f'corpo-fala-K{K}' + ('-red' if redundante else '') + ('-pc' if prior_corpo else '') + ('-pb' if prior_cerebro else ''))
    SerCorpoFala.K = K
    return SerCorpoFala
