```python
import torch


def fabrica():
    class PoliticaConstrucaoR7A2:
        def reset(self, m, W):
            self.reparando_vida = torch.zeros(m.B, dtype=torch.bool, device=DEV)
            self.ticks_no_posto = torch.zeros(m.B, dtype=torch.long, device=DEV)

        def extra(self, m, W, F):
            self.F = F
            return torch.zeros(m.B, F.shape[1], device=DEV, dtype=F.dtype)

        def decidir(self, tudo, m):
            F = self.F
            G = F.shape[1]
            S = tudo.shape[1] - G
            device = tudo.device
            dtype = tudo.dtype
            B = tudo.shape[0]

            e_fuel = F[:, 0, 10]
            e_agua = F[:, 0, 11]
            e_fome = F[:, 0, 12]
            e_calor = F[:, 0, 14]
            e_vida = F[:, 0, 15]
            e_dinh = F[:, 0, 16]
            e_pax = F[:, 0, 18]
            dinh = e_dinh * 150.0
            tem_pax = e_pax > 0.5

            disp = tudo[:, G:G + S] > -1e8
            no_posto = disp[:, 0]
            no_oficina = disp[:, 9]

            # contador de ticks seguidos no posto: 1a refeicao sempre livre, da 2a em
            # diante so' com folga de dinheiro (nao afunda o caixa comendo em loop)
            self.ticks_no_posto = torch.where(
                no_posto, self.ticks_no_posto + 1, torch.zeros_like(self.ticks_no_posto)
            )
            primeira_no_posto = self.ticks_no_posto == 1
            repetindo_no_posto = self.ticks_no_posto > 1

            # trabalho continuo: sempre ao alvo. NUNCA argmin de d_posto.
            mover = torch.argmin(F[:, :, 0], dim=1)
            ir_oficina = torch.argmin(F[:, :, 4], dim=1)
            ir_comida_mov = torch.argmin(F[:, :, 2], dim=1)

            score = torch.full((B, S), -1e9, device=device, dtype=dtype)

            # agua so' a .6 (nao .8): r6 gastava 6-8% das escolhas em agua, dinheiro
            # que faz falta pra comida/oficina
            quer_agua = e_agua < 0.6
            quer_comida = (e_fome > 0.15) & (primeira_no_posto | (repetindo_no_posto & (dinh > 30)))
            quer_fuel = e_fuel < 0.95

            # placar de compra no posto (agua > comida > gasolina) via argmax
            score[:, 5] = torch.where(no_posto & quer_agua, 30.0 + (0.6 - e_agua), score[:, 5])
            score[:, 7] = torch.where(no_posto & quer_comida, 20.0 + (e_fome - 0.15), score[:, 7])

            idx_pref = torch.where(
                dinh > 40,
                torch.full((B,), 3, device=device, dtype=torch.long),
                torch.full((B,), 1, device=device, dtype=torch.long),
            )
            disp_pref = disp.gather(1, idx_pref.unsqueeze(1)).squeeze(1)
            idx_fuel = torch.where(disp_pref, idx_pref, torch.zeros_like(idx_pref))
            disp_fuel = torch.where(disp_pref, disp_pref, disp[:, 0])
            val_fuel = torch.where(
                no_posto & quer_fuel & disp_fuel,
                10.0 + (1.0 - e_fuel),
                torch.full((B,), -1e9, device=device, dtype=dtype),
            )
            score.scatter_(1, idx_fuel.unsqueeze(1), val_fuel.unsqueeze(1))

            melhor = torch.argmax(score, dim=1)
            comprar = no_posto & (score.gather(1, melhor.unsqueeze(1)).squeeze(1) > -1e8)

            # fora do posto: ir a comida de longe, so' sem passageiro (desviar com pax
            # a bordo custa corrida — licao do r3_1: desviar demais mata por trabalhar
            # de menos, nao pela fome em si)
            buscar_comida = (~no_posto) & (~tem_pax) & (e_fome > 0.55) & (F[:, G - 1, 2] < 20)

            # emergencia fora do posto: so' se ja esta ao lado
            fora_agua = (~no_posto) & (e_agua < 0.15) & (F[:, G - 1, 3] < 8) & disp[:, 5]
            fora_comida = (~no_posto) & (e_fome > 0.85) & (F[:, G - 1, 2] < 8) & disp[:, 7]

            # REPARO mais cedo: histerese .65/.8 (era .5/.8) — dano mata metade das
            # mortes da r6, antecipar a oficina reduz o tempo com vida baixa
            ini_vida = (e_vida < 0.65) & (dinh > 20)
            self.reparando_vida = (self.reparando_vida | ini_vida) & (e_vida < 0.8) & (dinh > 10)
            quer_calor = (e_calor > 0.75) & (~tem_pax)
            quer_oficina = self.reparando_vida | quer_calor

            comprar_oficina = no_oficina & quer_oficina & (tudo[:, G + 9] > -1e8)
            ir_oficina_mov = quer_oficina & (~comprar_oficina)

            # prioridade (menor pra maior, ultima escrita vence):
            # mover base < buscar comida de longe < detour oficina < compra posto
            # < compra oficina < emergencia agua/comida
            acao = mover.clone()
            acao = torch.where(buscar_comida, ir_comida_mov, acao)
            acao = torch.where(ir_oficina_mov, ir_oficina, acao)
            acao = torch.where(comprar, G + melhor, acao)
            acao = torch.where(comprar_oficina, torch.full_like(acao, G + 9), acao)
            acao = torch.where(fora_agua, torch.full_like(acao, G + 5), acao)
            acao = torch.where(fora_comida, torch.full_like(acao, G + 7), acao)

            return acao.long()

        def atualizar(self, m):
            pass

    return PoliticaConstrucaoR7A2
```