import torch


def fabrica():
    class PoliticaL13Comida(object):
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

            # ALAVANCA RUA (herdada, intacta): peso pequeno so' desempata direcoes quase
            # equivalentes, nunca vira a decisao principal de ir ao alvo.
            PESO_RUA = 0.15
            mover = torch.argmin(F[:, :, 0] + PESO_RUA * F[:, :, 6], dim=1)
            ir_oficina = torch.argmin(F[:, :, 4], dim=1)
            ir_comida_mov = torch.argmin(F[:, :, 2], dim=1)

            # ALAVANCA CALOR (herdada do L12 p8, intacta): para pra esfriar ao entrar na
            # zona de sangramento (D_RODAR .15/tick andando com e_calor>.667), histerese
            # soltando em e_calor<=.55. So' com ~tem_pax; quer_oficina sempre vence.
            entra_zona_sangramento = (e_calor > 0.667) & (~tem_pax)
            self.resfriando = (self.resfriando | entra_zona_sangramento) & (e_calor > 0.55) & (~tem_pax)

            score = torch.full((B, S), -1e9, device=device, dtype=dtype)

            # ALAVANCA DESTA POLITICA (unica mudanca vs a base): limiares de fome no posto
            # e fora. A base comprava comida oportunista no posto com fome>0.15 -- quase
            # sempre que parava, mesmo mal beliscando fome -- e so' desviava ativamente fora
            # do posto (buscar_comida) com fome>0.6. Os dados medidos mostram que quem come
            # bem (r7_1, a melhor politica explicita, mortos 0.74) come com fome mediana
            # 70.1 (p10 21.1, p90 85.3), e o campeao evoluido (pior, 0.85-0.88) come com
            # mediana 63.7. Testamos subir os dois limiares pra ficar mais perto dessa
            # mediana real: comida no posto so' com fome>0.35 (ainda bem antes do desvio
            # ativo, pra aproveitar a parada barata sem topar toda vez com fome baixa) e o
            # desvio ativo fora do posto so' com fome>0.70 (era 0.6), liberando mais ticks
            # de trabalho por vida. A emergencia (fora_comida, fome>0.85 com d_comida<8)
            # fica intocada -- e' a rede de seguranca, nao o gatilho normal, e ja' testada
            # em H5/H12/H22 como demasiado tarde pra mexer sem risco.
            LIMIAR_COMIDA_POSTO = 0.35
            LIMIAR_COMIDA_FORA = 0.70

            quer_agua = e_agua < 0.50
            quer_comida = e_fome > LIMIAR_COMIDA_POSTO
            quer_fuel = e_fuel < 0.95

            # ORDEM DE COMPRA NO POSTO: comida > agua > fuel (inalterado da base).
            score[:, 7] = torch.where(no_posto & quer_comida, 30.0 + (e_fome - LIMIAR_COMIDA_POSTO), score[:, 7])

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

            # GASOLINA (inalterada da base): tier = min(tier_por_caixa, tier_por_necessidade).
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
                dinh > 50,
                torch.full((B,), 3, device=device, dtype=torch.long),
                torch.where(
                    dinh > 25,
                    torch.full((B,), 1, device=device, dtype=torch.long),
                    torch.full((B,), 0, device=device, dtype=torch.long),
                ),
            )
            idx_pref = torch.minimum(idx_caixa, idx_necessidade)
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

            segunda = no_posto & self.comeu_ultimo_tick & (e_fome > LIMIAR_COMIDA_POSTO) & (dinh > 30) & disp[:, 7]

            # comida noturna (mantida): desvio quando e_noite>0.5 OU fome acima do novo
            # limiar fora do posto.
            buscar_comida = (~no_posto) & (~tem_pax) & ((e_noite > 0.5) | (e_fome > LIMIAR_COMIDA_FORA)) & (F[:, G - 1, 2] < 25)

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

    return PoliticaL13Comida