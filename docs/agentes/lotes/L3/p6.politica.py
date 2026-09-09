import torch


def fabrica():
    class PoliticaConstrucaoR7A1OrdemPosto:
        def reset(self, m, W):
            self.reparando_vida = torch.zeros(m.B, dtype=torch.bool, device=DEV)
            self.comeu_ultimo_tick = torch.zeros(m.B, dtype=torch.bool, device=DEV)
            self.descansando = torch.zeros(m.B, dtype=torch.bool, device=DEV)

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
            e_fadiga = F[:, 0, 13]
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
            no_descanso = disp[:, 8]

            # trabalho continuo: sempre ao alvo. NUNCA argmin de d_posto.
            mover = torch.argmin(F[:, :, 0], dim=1)
            ir_oficina = torch.argmin(F[:, :, 4], dim=1)
            ir_comida_mov = torch.argmin(F[:, :, 2], dim=1)
            ir_descanso_mov = torch.argmin(F[:, :, 5], dim=1)

            score = torch.full((B, S), -1e9, device=device, dtype=dtype)

            quer_agua = e_agua < 0.8
            quer_comida = e_fome > 0.15
            quer_fuel = e_fuel < 0.95

            # ORDEM DE COMPRA NO POSTO: comida > agua > fuel (inalterado desta base).
            score[:, 7] = torch.where(no_posto & quer_comida, 30.0 + (e_fome - 0.15), score[:, 7])
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

            # segunda refeicao: se comeu no tick anterior e ainda ta com fome e tem grana, come de novo
            segunda = no_posto & self.comeu_ultimo_tick & (e_fome > 0.15) & (dinh > 30) & disp[:, 7]

            # comida a noite (inalterado desta base): posto fecha de noite, desvia pro ponto de
            # comida mais perto. Nunca com passageiro a bordo.
            buscar_comida = (~no_posto) & (~tem_pax) & ((e_noite > 0.5) | (e_fome > 0.6)) & (F[:, G - 1, 2] < 25)

            # emergencia fora do posto: so' se ja esta ao lado
            fora_agua = (~no_posto) & (e_agua < 0.15) & (F[:, G - 1, 3] < 8) & disp[:, 5]
            fora_comida = (~no_posto) & (e_fome > 0.85) & (F[:, G - 1, 2] < 8) & disp[:, 7]

            # REPARO: (1) vida baixa com histerese .5/.8, (2) calor alto sem passageiro
            ini_vida = (e_vida < 0.5) & (dinh > 20)
            self.reparando_vida = (self.reparando_vida | ini_vida) & (e_vida < 0.8) & (dinh > 10)
            quer_calor = (e_calor > 0.75) & (~tem_pax)
            quer_oficina = self.reparando_vida | quer_calor

            comprar_oficina = no_oficina & quer_oficina & (tudo[:, G + 9] > -1e8)
            ir_oficina_mov = quer_oficina & (~comprar_oficina)

            # ALAVANCA: fadiga/descanso (hoje ignorada — e_fadiga e d_descanso nunca lidos nesta
            # base). Histerese .6/.3 espelha a do reparo (.5/.8): entra a noite (posto fecha e
            # demanda cai — dados: 150-190 corridas/h de noite vs 230-250 de dia, e r7_1 ja tem
            # 42.8% do tempo livre dentro de raio de servico, sobra tempo pra isso) ou fadiga
            # extrema (>.85) a qualquer hora, como emergencia — mesma logica do calor (.75) pro
            # dano por pane. So descansa sem passageiro; corrida termina primeiro.
            ini_fad = (e_fadiga > 0.6) & (e_noite > 0.5) & (~tem_pax)
            emerg_fad = e_fadiga > 0.85
            self.descansando = (self.descansando | ini_fad | emerg_fad) & (e_fadiga > 0.3) & (~tem_pax)

            comprar_descanso = no_descanso & self.descansando & (tudo[:, G + 8] > -1e8)
            ir_descanso_final = self.descansando & (~comprar_descanso)

            # prioridade (menor pra maior, ultima escrita vence):
            # mover base < descanso (novo, mais fraco que comida) < buscar comida de longe <
            # detour oficina < compra posto < compra oficina < compra descanso < emergencia
            # agua/comida < segunda refeicao
            acao = mover.clone()
            acao = torch.where(ir_descanso_final, ir_descanso_mov, acao)
            acao = torch.where(buscar_comida, ir_comida_mov, acao)
            acao = torch.where(ir_oficina_mov, ir_oficina, acao)
            acao = torch.where(comprar, G + melhor, acao)
            acao = torch.where(comprar_oficina, torch.full_like(acao, G + 9), acao)
            acao = torch.where(comprar_descanso, torch.full_like(acao, G + 8), acao)
            acao = torch.where(fora_agua, torch.full_like(acao, G + 5), acao)
            acao = torch.where(fora_comida, torch.full_like(acao, G + 7), acao)
            acao = torch.where(segunda, torch.full_like(acao, G + 7), acao)

            self.comeu_ultimo_tick = acao == (G + 7)

            return acao.long()

        def atualizar(self, m):
            pass

    return PoliticaConstrucaoR7A1OrdemPosto