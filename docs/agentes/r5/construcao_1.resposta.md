PREDICAO: mortos ~0.78–0.85 (não bate meta .70 — fadiga/calor ignorados acumulam igual ao campeão, que também morre .85), entregas 15–18 (~3.5–4/dia, bate meta ≥3), refeições 5–6, abastecidas 4 (sempre tanque cheio quando no posto), panes 7–8 (aceita pane como transporte, nunca desvia por vontade), fome/sede quase não matam (emergência fora do posto cobre: come se e_fome>.85 e já está do lado, bebe se e_agua<.15 e já está do lado); morte majoritária dia 8–9 por vida baixa acumulada (fadiga/calor não tratados) ou dívida se gastar tudo em gasolina 100L toda vez que rico.

```python
import torch


def fabrica():
    class PoliticaConstrucao5v1:
        def reset(self, m, W):
            pass

        def extra(self, m, W, F):
            self.F = F
            self.G = F.shape[1]
            return torch.zeros(m.B, self.G)

        def decidir(self, tudo, m):
            F = self.F
            G = self.G

            e_agua = F[:, 0, 11]
            e_fome = F[:, 0, 12]
            d_comida_parado = F[:, G - 1, 2]
            d_agua_parado = F[:, G - 1, 3]

            esta_no_posto = tudo[:, G + 0] > -1e8
            tem_agua = tudo[:, G + 5] > -1e8
            tem_comida = tudo[:, G + 7] > -1e8
            tem_g100 = tudo[:, G + 3] > -1e8
            tem_g50 = tudo[:, G + 1] > -1e8

            rico = m.dinh > 40

            # (a) trabalho continuo: sempre ir ao alvo, nunca argmin de d_posto
            acao = torch.argmin(F[:, :, 0], dim=1)

            # (c) comida fora do posto so em emergencia, ja do lado
            emerg_comida = (~esta_no_posto) & (e_fome > 0.85) & (d_comida_parado < 8) & tem_comida
            acao = torch.where(emerg_comida, torch.full_like(acao, G + 7), acao)

            # (d) agua fora do posto so em emergencia, ja do lado
            emerg_agua = (~esta_no_posto) & (e_agua < 0.15) & (d_agua_parado < 8) & tem_agua
            acao = torch.where(emerg_agua, torch.full_like(acao, G + 5), acao)

            # (b) no posto: agua, senao comida, senao gasolina (100 se rico, senao 50, senao 25)
            acao_gas = torch.where(
                rico & tem_g100, torch.full_like(acao, G + 3),
                torch.where(tem_g50, torch.full_like(acao, G + 1), torch.full_like(acao, G + 0)),
            )
            acao_posto = torch.where(
                (e_agua < 0.8) & tem_agua, torch.full_like(acao, G + 5),
                torch.where((e_fome > 0.2) & tem_comida, torch.full_like(acao, G + 7), acao_gas),
            )

            acao = torch.where(esta_no_posto, acao_posto, acao)

            return acao.long()

        def atualizar(self, m):
            pass

    return PoliticaConstrucao5v1
```