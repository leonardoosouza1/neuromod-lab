import torch


def fabrica():
    class PoliticaL10Lugar(object):
        def reset(self, m, W):
            self.reparando_vida = torch.zeros(m.B, dtype=torch.bool, device=DEV)
            self.comeu_ultimo_tick = torch.zeros(m.B, dtype=torch.bool, device=DEV)
            # ALAVANCA LUGAR: contador de ticks restantes segurando o rumo por preco/aliq
            # (>= 20 ticks, como pedido, pra nao trocar de direcao a cada tick e cancelar
            # o proprio deslocamento).
            self.lugar_ticks = torch.zeros(m.B, dtype=torch.long, device=DEV)

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
            e_demanda = F[:, 0, 27]
            e_espera = F[:, 0, 28]
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

            # ALAVANCA LUGAR (unica mudanca deste lote): quando LIVRE (sem passageiro),
            # sem NENHUMA compra pendente (agua/comida/gasolina/oficina — reusa os gates
            # ja calculados acima + vida/calor) e o gatilho de renda dispara (e_espera>.6,
            # mediana medida = .57, ou e_demanda<.5, que cobre industrial/periferia), o
            # taxi desempata a direcao por receita esperada a frente (preco_frente x
            # (1-aliq_frente)) em vez de so' d_alvo+custo_frente. W=.7 (meio da faixa
            # .5-1.0 pedida). Segura o rumo por 20 ticks (contador) pra nao cancelar o
            # proprio deslocamento a cada tick, e larga assim que pega passageiro
            # (tem_pax zera o contador). Com tanque < 30% inverte pro sentido de preco
            # BAIXO (fica mais barato abastecer 100L perto da pane, puxado pelos genes
            # do campeao que evitam aliq alta). NADA MAIS muda: compra, comida, agua,
            # gasolina, oficina seguem identicos a L6 p4.
            quer_oficina_now = (e_vida < 0.5) | (e_calor > 0.75)
            sem_pendente = (~quer_agua) & (~quer_comida) & (~quer_fuel) & (~quer_oficina_now)
            gatilho_lugar = (e_espera > 0.6) | (e_demanda < 0.5)
            ativa_lugar = (~tem_pax) & sem_pendente & gatilho_lugar

            self.lugar_ticks = torch.where(
                tem_pax,
                torch.zeros_like(self.lugar_ticks),
                torch.where(
                    ativa_lugar & (self.lugar_ticks <= 0),
                    torch.full_like(self.lugar_ticks, 20),
                    torch.clamp(self.lugar_ticks - 1, min=0),
                ),
            )
            usar_lugar = (~tem_pax) & (self.lugar_ticks > 0)

            W_LUGAR = 0.7
            preco_frente = F[:, :, 7]
            aliq_frente = F[:, :, 8]
            receita_frente = preco_frente * (1.0 - aliq_frente)
            score_rumo_caro = F[:, :, 0] + PESO_RUA * F[:, :, 6] - W_LUGAR * receita_frente
            score_rumo_barato = F[:, :, 0] + PESO_RUA * F[:, :, 6] + W_LUGAR * receita_frente
            mover_lugar_caro = torch.argmin(score_rumo_caro, dim=1)
            mover_lugar_barato = torch.argmin(score_rumo_barato, dim=1)
            mover_lugar = torch.where(e_fuel < 0.3, mover_lugar_barato, mover_lugar_caro)

            mover = torch.where(usar_lugar, mover_lugar, mover)

            # ORDEM DE COMPRA NO POSTO: comida > agua > fuel (inalterado da base).
            score[:, 7] = torch.where(no_posto & quer_comida, 30.0 + (e_fome - 0.15), score[:, 7])

            # ALAVANCA AGUA (herdada de L6 p4, intacta).
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

            # ALAVANCA GASOLINA (herdada de L6 p4, intacta).
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

    return PoliticaL10Lugar