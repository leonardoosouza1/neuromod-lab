import torch


def fabrica():
    class PoliticaL3A1LimiarComida:
        def reset(self, m, W):
            self.reparando_vida = torch.zeros(m.B, dtype=torch.bool, device=DEV)
            self.comeu_ultimo_tick = torch.zeros(m.B, dtype=torch.bool, device=DEV)

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
            e_noite = F[:, 0, 21]
            dinh = e_dinh * 150.0
            tem_pax = e_pax > 0.5

            disp = tudo[:, G:G + S] > -1e8
            no_posto = disp[:, 0]
            no_oficina = disp[:, 9]

            # trabalho continuo: sempre ao alvo. NUNCA argmin de d_posto.
            mover = torch.argmin(F[:, :, 0], dim=1)
            ir_oficina = torch.argmin(F[:, :, 4], dim=1)
            ir_comida_mov = torch.argmin(F[:, :, 2], dim=1)

            score = torch.full((B, S), -1e9, device=device, dtype=dtype)

            quer_agua = e_agua < 0.8
            # ALAVANCA COMIDA: limiar no posto desce 0.15 -> 0.10 (comida custa 2 x pmul,
            # quase gratis; nao ha razao pra esperar ficar mais faminto se ja estou parado
            # no posto por outro motivo). Ordem de compra (comida > agua > fuel) inalterada.
            quer_comida = e_fome > 0.10
            quer_fuel = e_fuel < 0.95

            score[:, 7] = torch.where(no_posto & quer_comida, 30.0 + (e_fome - 0.10), score[:, 7])
            score[:, 5] = torch.where(no_posto & quer_agua, 20.0 + (0.8 - e_agua), score[:, 5])

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

            # segunda refeicao: inalterada (nao e o foco desta alavanca)
            segunda = no_posto & self.comeu_ultimo_tick & (e_fome > 0.15) & (dinh > 30) & disp[:, 7]

            # ALAVANCA COMIDA (fora do posto): detour proativo desce 0.6 -> 0.45 de fome
            # (dia OU noite, mesmo knob) e emergencia adjacente desce 0.85 -> 0.70. Motivo:
            # mesmo com o fix de noite (ponto de comida) ja embutido nesta base, o lote
            # anterior ainda morre 46-53% de fome com fome final 62-67 — ou seja o gatilho
            # atual dispara tarde demais pra cobrir o trajeto ate o ponto de comida antes do
            # 90 fatal. Cada 0.15 de folga = ~47 ticks (fome_passo .32/tick) a mais de
            # antecedencia. Raio (25) e condicao de noite inalterados (nao e minha alavanca).
            buscar_comida = (~no_posto) & (~tem_pax) & ((e_noite > 0.5) | (e_fome > 0.45)) & (F[:, G - 1, 2] < 25)

            fora_agua = (~no_posto) & (e_agua < 0.15) & (F[:, G - 1, 3] < 8) & disp[:, 5]
            fora_comida = (~no_posto) & (e_fome > 0.70) & (F[:, G - 1, 2] < 8) & disp[:, 7]

            # REPARO: inalterado (nao e minha alavanca)
            ini_vida = (e_vida < 0.5) & (dinh > 20)
            self.reparando_vida = (self.reparando_vida | ini_vida) & (e_vida < 0.8) & (dinh > 10)
            quer_calor = (e_calor > 0.75) & (~tem_pax)
            quer_oficina = self.reparando_vida | quer_calor

            comprar_oficina = no_oficina & quer_oficina & (tudo[:, G + 9] > -1e8)
            ir_oficina_mov = quer_oficina & (~comprar_oficina)

            # prioridade (menor pra maior, ultima escrita vence):
            # mover base < buscar comida de longe < detour oficina < compra posto < compra oficina
            # < emergencia agua/comida < segunda refeicao
            acao = mover.clone()
            acao = torch.where(buscar_comida, ir_comida_mov, acao)
            acao = torch.where(ir_oficina_mov, ir_oficina, acao)
            acao = torch.where(comprar, G + melhor, acao)
            acao = torch.where(comprar_oficina, torch.full_like(acao, G + 9), acao)
            acao = torch.where(fora_agua, torch.full_like(acao, G + 5), acao)
            acao = torch.where(fora_comida, torch.full_like(acao, G + 7), acao)
            acao = torch.where(segunda, torch.full_like(acao, G + 7), acao)

            self.comeu_ultimo_tick = acao == (G + 7)

            return acao.long()

        def atualizar(self, m):
            pass

    return PoliticaL3A1LimiarComida