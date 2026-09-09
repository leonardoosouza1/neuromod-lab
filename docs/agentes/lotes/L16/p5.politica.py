import torch


def fabrica():
    class PoliticaL16ParadaMinima(object):
        def reset(self, m, W):
            self.reparando_vida = torch.zeros(m.B, dtype=torch.bool, device=DEV)
            self.resfriando = torch.zeros(m.B, dtype=torch.bool, device=DEV)
            self.abasteceu_parada = torch.zeros(m.B, dtype=torch.bool, device=DEV)
            self.comeu_parada = torch.zeros(m.B, dtype=torch.bool, device=DEV)

        def extra(self, m, W, F):
            self.F = F
            return torch.zeros(m.B, F.shape[1], device=DEV, dtype=F.dtype)

        def decidir(self, tudo, m):
            F = self.F
            G = F.shape[1]
            S = tudo.shape[1] - G
            device = tudo.device
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

            # RUA (herdada de L14 p7, intacta): peso pequeno de custo_frente na
            # escolha de direcao ao alvo.
            PESO_RUA = 0.3
            mover = torch.argmin(F[:, :, 0] + PESO_RUA * F[:, :, 6], dim=1)
            ir_oficina = torch.argmin(F[:, :, 4], dim=1)
            ir_comida_mov = torch.argmin(F[:, :, 2], dim=1)

            # CALOR (herdada de L12 p8, intacta): parar pra esfriar na zona de
            # sangramento, histerese solta em raw 66.
            entra_zona_sangramento = (e_calor > 0.667) & (~tem_pax)
            self.resfriando = (self.resfriando | entra_zona_sangramento) & (e_calor > 0.55) & (~tem_pax)

            # ALAVANCA DESTE LOTE (PARADA MINIMA, 4a rodada da mesma hipotese:
            # H54/L13 p5 = 0.95, H55/L14 p5 = 0.96, L15 p5 = 0.75). Regra fixa
            # do enunciado: no raio do posto so' existem 2 decisoes possiveis
            # (gasolina por tier de caixa, comida por limiar de fome), SEM agua
            # e SEM reavaliacao — "nada mais". As flags abaixo (resetadas so'
            # quando o taxi sai do raio) fazem valer o teto de <= 2 ticks pedido:
            # 1 compra de combustivel + 1 de comida por visita, no maximo, mesmo
            # que a necessidade continue depois disso — quem tira o taxi do raio
            # e' o mover() da RUA, ja' existente, nao uma acao "ficar" nova.
            self.abasteceu_parada = self.abasteceu_parada & no_posto
            self.comeu_parada = self.comeu_parada & no_posto

            idx_fuel = torch.where(
                dinh >= 35.0,
                torch.full((B,), 3, device=device, dtype=torch.long),  # 100 L
                torch.full((B,), 1, device=device, dtype=torch.long),  # 50 L
            )
            disp_fuel = disp.gather(1, idx_fuel.unsqueeze(1)).squeeze(1)
            quer_fuel = e_fuel < 0.95
            comprar_fuel = no_posto & quer_fuel & disp_fuel & (~self.abasteceu_parada)

            quer_comida = e_fome > 0.30
            comprar_comida = no_posto & quer_comida & disp[:, 7] & (~self.comeu_parada) & (~comprar_fuel)

            comprar = comprar_fuel | comprar_comida
            acao_compra = torch.where(
                comprar_fuel,
                G + idx_fuel,
                torch.full((B,), G + 7, device=device, dtype=torch.long),
            )

            # emergencias FORA do posto (herdadas intactas, "compras que ja
            # funcionam"): agua/comida em ponto de comida e busca noturna.
            buscar_comida = (~no_posto) & (~tem_pax) & ((e_noite > 0.5) | (e_fome > 0.6)) & (F[:, G - 1, 2] < 25)

            fora_agua = (~no_posto) & (e_agua < 0.15) & (F[:, G - 1, 3] < 8) & disp[:, 5]
            fora_comida = (~no_posto) & (e_fome > 0.85) & (F[:, G - 1, 2] < 8) & disp[:, 7]

            ini_vida = (e_vida < 0.5) & (dinh > 20)
            self.reparando_vida = (self.reparando_vida | ini_vida) & (e_vida < 0.8) & (dinh > 10)
            quer_calor = (e_calor > 0.75) & (~tem_pax)
            quer_oficina = self.reparando_vida | quer_calor

            comprar_oficina = no_oficina & quer_oficina & (tudo[:, G + 9] > -1e8)
            ir_oficina_mov = quer_oficina & (~comprar_oficina)

            parar_resfriar = self.resfriando & (~quer_oficina)

            acao = mover.clone()
            acao = torch.where(buscar_comida, ir_comida_mov, acao)
            acao = torch.where(parar_resfriar, torch.full_like(acao, G - 1), acao)
            acao = torch.where(ir_oficina_mov, ir_oficina, acao)
            acao = torch.where(comprar, acao_compra, acao)
            acao = torch.where(comprar_oficina, torch.full_like(acao, G + 9), acao)
            acao = torch.where(fora_agua, torch.full_like(acao, G + 5), acao)
            acao = torch.where(fora_comida, torch.full_like(acao, G + 7), acao)

            self.abasteceu_parada = self.abasteceu_parada | (acao == (G + idx_fuel))
            self.comeu_parada = self.comeu_parada | (acao == (G + 7))

            return acao.long()

        def atualizar(self, m):
            pass

    return PoliticaL16ParadaMinima