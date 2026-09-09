import torch


def fabrica():
    class PoliticaL15TrabalhoLugarP3(object):
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

            # ALAVANCA DESTE LOTE (TRABALHO/LUGAR): unica mudanca vs a base L14 p7 =
            # desempate de direcao por preco_frente/aliq_frente QUANDO LIVRE (sem
            # passageiro a bordo -- "sem compra pendente" ja e' garantido pela cadeia
            # de torch.where abaixo, que descarta o valor de `mover` sempre que
            # comprar/segunda/fora_agua/fora_comida/comprar_oficina disparam). Com
            # passageiro a bordo o alvo e' o destino da corrida: NAO desviar por
            # preco/aliq (jamais testado nem pedido -- manteria mover_ocupado puro).
            #
            # Dados: genes de movimento do campeao evoluido (5 sementes) mostram
            # aliq_frente negativo em 4/5 (-0.01 a -2.54: evita distrito de imposto
            # alto = centro) e preco_frente MISTO (-0.39 a +0.38: sem sentido
            # consistente). Os 3 testes anteriores deste eixo (H39, L13 p3, L14 p3)
            # usaram so' um sentido (rumo ao centro OU evitar aliq) e todos deram
            # empate exato com a base (0.53, 18.6 corridas, mesma causa de morte) --
            # ou seja, o platô nao discriminou entre os dois sentidos. Aqui combino
            # os dois sinais pedidos pela tarefa: penaliza aliq alta (imposto, ruim)
            # e premia preco alto (tarifa, bom), com peso pequeno (.15, o mesmo teto
            # seguro medido no eixo RUA em L1 p7/L13 p7) para so' desempatar direcoes
            # quase equidistantes em d_alvo (diff tipica ~2), sem competir com o
            # alvo real (passageiro/servico). Nao mudo mais nada: rua, calor, agua,
            # gasolina, comida e oficina ficam identicos a base L14 p7.
            PESO_RUA = 0.3
            PESO_LUGAR = 0.15
            custo_base = F[:, :, 0] + PESO_RUA * F[:, :, 6]
            desempate_lugar = PESO_LUGAR * (F[:, :, 8] - F[:, :, 7])
            custo_livre = custo_base + desempate_lugar
            mover = torch.argmin(torch.where(tem_pax.unsqueeze(1), custo_base, custo_livre), dim=1)
            ir_oficina = torch.argmin(F[:, :, 4], dim=1)
            ir_comida_mov = torch.argmin(F[:, :, 2], dim=1)

            # ALAVANCA LIVRE (herdada de L12 p8, intacta): calor tem DOIS canais de
            # dano -- D_RODAR=.15/tick ENQUANTO ANDA com calor>80 raw (e_calor>.667),
            # sangramento continuo que comeca ANTES do desligamento forcado a 92 raw
            # (e_calor>.767, D_QUENTE=6 fixo + 10 ticks travado, so' uma vez). Parar
            # (G-1) assim que entra na zona de sangramento e' barato porque calor_desce
            # (.6/tick) e' 3-4x mais rapido que a subida efetiva ao andar (~.15-.19/
            # tick). Histerese (self.resfriando) so' solta em e_calor<=.55 (raw 66)
            # pra evitar liga/desliga a cada tick; nunca desvia com passageiro a bordo.
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

    return PoliticaL15TrabalhoLugarP3