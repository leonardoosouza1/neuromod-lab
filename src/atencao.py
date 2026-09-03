"""E21: ATENCAO INTEROCEPTIVA — so a necessidade mais urgente decide o servico.
Inspirado em "Interoceptive Attention as Dynamic Homeostatic Prioritization" (2026,
AffectWorld): redirecionar um orcamento fixo de precisao para a necessidade mais urgente
dobrou a sobrevivencia. Aqui: o score de servicos do Reativo (svn = sv*nec*paga, somado
sobre os 5) vira winner-take-all na necessidade: so o servico da MAIOR necessidade
(entre os disponiveis e pagaveis) mantem seu termo; os outros sao cancelados.
Puro em extra_serv (sem tocar no lab.py); com `wta=False` e identico ao Reativo."""
import torch
from lab import Reativo, NF

def fabrica(wta=True, suave=0.):
    class ReativoAtencao(Reativo):
        NP = Reativo.NP
        nome = 'reativo-atencao' if wta else 'reativo-atencao-off'
        def reset(s, m, W): s.W = W
        def extra_serv(s, m):
            if not wta: return torch.zeros(m.B, 5, device=m.fuel.device)
            svn, _ = m.serv_need()                      # (B,5) sv*nec*paga
            top = torch.nn.functional.one_hot(svn.argmax(1), 5).float()
            keep = top if suave == 0. else (top + suave*(1. - top))
            return svn*s.W[:, NF:NF+5]*(keep - 1.)      # cancela os que nao sao o mais urgente
    return ReativoAtencao
