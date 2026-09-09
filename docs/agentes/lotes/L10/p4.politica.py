import torch


def fabrica():
    class PoliticaL10P4GasolinaPreco:
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
            custo_aqui = F[:, 0, 22]
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

            score = torch.full((B, S), -1e9, device=device, dtype=dtype)

            quer_agua = e_agua < 0.50
            quer_comida = e_fome > 0.15
            quer_fuel = e_fuel < 0.95

            # ORDEM DE COMPRA NO POSTO: comida > agua > fuel (inalterado da base).
            score[:, 7] = torch.where(no_posto & quer_comida, 30.0 + (e_fome - 0.15), score[:, 7])

            idx_pref_agua = torch.where(
                e_agua < 0.25,
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

            # ALAVANCA GASOLINA (unico ponto mudado vs L6 p4): a base L6 p4 ja tinha
            # idx_pref = min(tier_por_caixa, tier_por_necessidade), o que evita comprar mais
            # litro do que cabe no tanque. Mas o teto de dinheiro por tier (dinh>50->100L,
            # dinh>25->50L) era FIXO, como se o litro custasse sempre .3 (preco_L .3 x
            # pmul=1). O enunciado mede pmul ate' 4x entre distritos (100L = 60 no centro
            # contra 15 na periferia): com teto fixo, um abastecimento que calhe de cair num
            # distrito caro ainda libera o tier de 100L (~60 de custo) so' porque dinh>50,
            # estourando o caixa que falta pra comida/agua — foi exatamente a causa de morte
            # quando o gasolina foi mexido antes (L9 p4: sede subiu a 37% ao tocar um limiar
            # vizinho). Escalo o teto por custo_aqui (F[:,0,22], 0..1, ja' normalizado — nao
            # inverto constante de pmul que eu nao sei o valor exato): em posto barato
            # (custo_aqui~0) o teto fica IGUAL ao da base (50/25, comportamento inalterado —
            # a maioria dos postos, ja' que o campeao evoluido evita distrito caro por genes
            # de casa_frente/aliq_frente negativos); em posto caro (custo_aqui~1) o teto
            # dobra (100/50), empurrando pro tier de necessidade (idx_necessidade) em vez do
            # tier maximo. liters_falta e idx_necessidade ficam intocados — a autonomia
            # perseguida e' a mesma, so' o quanto o caixa aguenta pagar por ela muda.
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
            teto_100 = 50.0 * (1.0 + custo_aqui)
            teto_50 = 25.0 * (1.0 + custo_aqui)
            idx_caixa = torch.where(
                dinh > teto_100,
                torch.full((B,), 3, device=device, dtype=torch.long),
                torch.where(
                    dinh > teto_50,
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

    return PoliticaL10P4GasolinaPreco