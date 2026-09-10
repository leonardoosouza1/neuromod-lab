"""linear_sem_ficar.py — [10/09 Astra plano-terceiro-olho passo 1] o CAMPEAO LINEAR (W de --campeao, semente 0) com a opcao
FICAR (acao 8) proibida: `tudo` que chega ao decidir ja e a nota do campeao para as 9 direcoes + 10 servicos
(politica_util.rodar); aqui so se apaga a coluna 8 e toma o argmax. REQUER `--W-politica campeao` no julga_politica: sem isso o W e zero, o `tudo` chega zerado e apagar a coluna 8 vira 'direcao 0 sempre' (pred 179b, artefato de 10/09). Mede o que o FICAR (5-10 % dos tiques nos
mundos A/B, docs/78) vale de verdade para o campeao — se cair pouco, o FICAR nao sustenta o fit."""
import torch


def fabrica():
    class LinearSemFicar:
        def reset(self, m, W):
            pass

        def extra(self, m, W, F):
            return torch.zeros(m.B, F.shape[1], device=DEV, dtype=F.dtype)

        def decidir(self, tudo, m):
            t = tudo.clone()
            t[:, 8] = -1e9
            return t.argmax(1)

        def atualizar(self, m):
            pass

    return LinearSemFicar
