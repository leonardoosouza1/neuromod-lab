"""E23 (doc 37 §4): a EQUACAO MINIMA que sobrevive — destilacao por re-ajuste, nao por poda.
`ReativoMinimo(k)`: o Reativo so pode usar as k features de movimento da lista `permitidas`
(as outras sao CANCELADAS em extra(), puro) + os 6 pesos de servico. A evolucao ajusta so o
que sobra -> a politica de k termos e verificada por construcao (e o fitness dela). Com todas
as features permitidas e identico ao Reativo."""
import torch
from lab import Reativo, NF, DEV
from rodar import NOMES_F

def fabrica(permitidas, nome=None):
    idx_bloq = [i for i in range(NF) if NOMES_F[i] not in permitidas and NOMES_F[i] != 'bias']
    class ReativoMinimo(Reativo):
        NP = Reativo.NP
        def reset(s, m, W):
            s.W = W; s.IDX = torch.tensor(idx_bloq, device=DEV, dtype=torch.long) if idx_bloq else None
        def extra(s, m, W, viz):
            if s.IDX is None: return 0.
            F, val = m.obs()                                   # (B,G,NF) — recomputa (puro)
            return -(F[:, :, s.IDX]*W[:, None, s.IDX]).sum(-1)  # cancela os termos bloqueados
    ReativoMinimo.nome = nome or f'minimo-{len(permitidas)}'
    ReativoMinimo.permitidas = list(permitidas)
    return ReativoMinimo
