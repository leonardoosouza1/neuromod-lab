import torch


def fabrica():
    class PoliticaL6Livre(object):
        def reset(self, m, W):
            self.reparando_vida = torch.zeros(m.B, dtype=torch.bool, device=DEV)
            self.comeu_ultimo_tick = torch.zeros(m.B, dtype=torch.bool, device=DEV)
            self.resfriando = torch.zeros(m.B, dtype=torch.bool, device=DEV)

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

            # ALAVANCA RUA (herdada de p7, intacta): score de mover ao alvo pondera d_alvo +
            # peso*custo_frente. peso pequeno de proposito: L1 p7 usou peso=5.0 e a penalidade
            # (5*2=10) dominou o d_alvo (diff maxima ~2), paralisando o taxi (0.99, 1.7 corridas).
            # Aqui peso=.15 da penalidade maxima .15*2=.3, so' desempata direcoes quase
            # equivalentes sem nunca virar a decisao principal de ir ao alvo.
            PESO_RUA = 0.15
            mover = torch.argmin(F[:, :, 0] + PESO_RUA * F[:, :, 6], dim=1)
            ir_oficina = torch.argmin(F[:, :, 4], dim=1)
            ir_comida_mov = torch.argmin(F[:, :, 2], dim=1)

            # ALAVANCA CALOR (herdada de L12 p8, intacta): parar pra esfriar assim que o calor
            # entra na zona de sangramento (D_RODAR .15/tick andando com raw>80, e_calor>.667),
            # com histerese soltando so' em e_calor<=.55 (raw 66) pra nao ligar/desligar a cada
            # tick. So' com ~tem_pax; quer_oficina sempre vence (reparar cura vida ALEM de
            # esfriar).
            entra_zona_sangramento = (e_calor > 0.667) & (~tem_pax)
            self.resfriando = (self.resfriando | entra_zona_sangramento) & (e_calor > 0.55) & (~tem_pax)

            score = torch.full((B, S), -1e9, device=device, dtype=dtype)

            quer_agua = e_agua < 0.50
            quer_comida = e_fome > 0.15
            quer_fuel = e_fuel < 0.95

            # ORDEM DE COMPRA NO POSTO: comida > agua > fuel (inalterado da base).
            score[:, 7] = torch.where(no_posto & quer_comida, 30.0 + (e_fome - 0.15), score[:, 7])

            # AGUA (inalterada da base): gatilho e_agua<0.50, tier 50L salvo e_agua<0.25 -> 100L.
            idx_pref_agua = torch.where(
                (e_agua < 0.25) & (dinh > 40.0),
                torch.full((B,), 6, device=device, dtype=torch.long),
                torch.full((B,), 5, device=device, dtype=torch.long),
            )
            disp_pref_agua = disp.gather(1, idx_pref_agua.unsqueeze(1)).squeeze(1)
            idx_agua = torch.where(disp_pref_agua, idx_pref_agua, torch.full_like(idx_pref_agua, 5))
            disp_agua = torch.where(disp_pref_agua, disp_pref_agua, disp[:, 5])
            val_agua = torch.where(
                no_posto & quer_agua & disp_agua,
                20.0 + (0.50 - e_agua),
                torch.full((B,), -1e9, device=device, dtype=dtype),
            )
            score.scatter_(1, idx_agua.unsqueeze(1), val_agua.unsqueeze(1))

            # GASOLINA (ALAVANCA DESTA POLITICA): tier = min(tier_por_caixa, tier_por_necessidade),
            # com UM degrau novo: G+4 (150 L) quando sobra caixa E o tanque esta genuinamente
            # baixo. FATO A do supervisor: a reserva nasce ZERO e NENHUMA das 87+ politicas
            # anteriores comprou o tier 150 L -- cada pane custa D_PANE 6 + (KCAL_PANE=8 -
            # reserva_gasta) de dano, entao sem reserva a parte variavel do dano de pane e'
            # sempre o teto (14 em vez de 6, ~7.5 panes/vida = ate' ~56 de dano evitavel).
            # 150 L custam 45*pmul*fase: ate' ~90 no distrito mais caro (centro) e so' ~13-27
            # no mais barato -- esta alavanca so' enxerga DINHEIRO (nao distrito), entao o
            # limiar dinh>90 e' o piso que cobre o PIOR caso (centro) sem arriscar ficar sem
            # caixa pra comida/agua em nenhum distrito. e_fuel<0.4 evita comprar o tier grande
            # com o tanque ainda >40% cheio (a maior parte dos 150 L iria pro tanque e nao pra
            # reserva -- desperdicaria o degrau extra numa parada que nao precisa dele).
            liters_falta = (1.0 - e_fuel) * 100.0
            idx_necessidade = torch.where(
                liters_falta <= 25.0,
                torch.full((B,), 0, device=device, dtype=torch.long),
                torch.where(
                    liters_falta <= 50.0,
                    torch.full((B,), 1, device=device, dtype=torch.long),
                    torch.where(
                        liters_falta <= 75.0,
                        torch.full((B,), 2, device=device, dtype=torch.long),
                        torch.full((B,), 3, device=device, dtype=torch.long),
                    ),
                ),
            )
            idx_caixa = torch.where(
                (dinh > 90) & (e_fuel < 0.4),
                torch.full((B,), 4, device=device, dtype=torch.long),
                torch.where(
                    dinh > 50,
                    torch.full((B,), 3, device=device, dtype=torch.long),
                    torch.where(
                        dinh > 25,
                        torch.full((B,), 1, device=device, dtype=torch.long),
                        torch.full((B,), 0, device=device, dtype=torch.long),
                    ),
                ),
            )
            # o min() classico (idx_necessidade tem teto 3) nunca deixaria o tier 4 passar --
            # a reserva e' comprada por OPORTUNIDADE de caixa, nao por necessidade imediata do
            # tanque, entao aplico o tier 4 por fora do min quando idx_caixa ja' sinalizou reserva.
            idx_pref_base = torch.minimum(idx_caixa, idx_necessidade)
            idx_desejado = torch.where(idx_caixa == 4, idx_caixa, idx_pref_base)
            disp_desejado = disp.gather(1, idx_desejado.unsqueeze(1)).squeeze(1)
            disp_base = disp.gather(1, idx_pref_base.unsqueeze(1)).squeeze(1)
            # fallback em cascata: sem 150 L disponivel/pago, tenta o tier normal
            # (min caixa/necessidade); sem esse, tenta 25 L (tier 0) -- mesma logica de
            # fallback da base, so' com um degrau a mais no topo.
            idx_fuel = torch.where(
                disp_desejado,
                idx_desejado,
                torch.where(disp_base, idx_pref_base, torch.zeros_like(idx_pref_base)),
            )
            disp_fuel = torch.where(
                disp_desejado,
                disp_desejado,
                torch.where(disp_base, disp_base, disp[:, 0]),
            )
            val_fuel = torch.where(
                no_posto & quer_fuel & disp_fuel,
                10.0 + (1.0 - e_fuel),
                torch.full((B,), -1e9, device=device, dtype=dtype),
            )
            score.scatter_(1, idx_fuel.unsqueeze(1), val_fuel.unsqueeze(1))

            melhor = torch.argmax(score, dim=1)
            comprar = no_posto & (score.gather(1, melhor.unsqueeze(1)).squeeze(1) > -1e8)

            segunda = no_posto & self.comeu_ultimo_tick & (e_fome > 0.15) & (dinh > 30) & disp[:, 7]

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
            acao = torch.where(comprar, G + melhor, acao)
            acao = torch.where(comprar_oficina, torch.full_like(acao, G + 9), acao)
            acao = torch.where(fora_agua, torch.full_like(acao, G + 5), acao)
            acao = torch.where(fora_comida, torch.full_like(acao, G + 7), acao)
            acao = torch.where(segunda, torch.full_like(acao, G + 7), acao)

            self.comeu_ultimo_tick = acao == (G + 7)

            return acao.long()

        def atualizar(self, m):
            pass

    return PoliticaL6Livre