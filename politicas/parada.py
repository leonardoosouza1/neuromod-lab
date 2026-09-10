"""parada.py — [10/09 CS docs/78 + Astra plano-terceiro-olho passo 1] CONTROLE COMPORTAMENTAL: fica parada SEMPRE.
Acao 8 = FICAR (DIRS[8] = (0, 0) em campo.py). Piso do premio: quanto do fit 'vida' (dias + renda/300) se ganha sem
sair do lugar (nao gasta gasolina, nao esquenta, nao bate; mas nao compra nem ganha renda). Comparar com o campeao
linear do MESMO mundo (julga_politica imprime os dois) e com linear_sem_ficar.py."""
import torch


def fabrica():
    class Parada:
        def reset(self, m, W):
            pass

        def extra(self, m, W, F):
            return torch.zeros(m.B, F.shape[1], device=DEV, dtype=F.dtype)

        def decidir(self, tudo, m):
            return torch.full((tudo.shape[0],), 8, device=tudo.device, dtype=torch.long)

        def atualizar(self, m):
            pass

    return Parada
