import torch


def fabrica():
    class PoliticaConstrucao2R6(PoliticaConstrucao2R5 if False else object):
        def reset(self, m, W):
            self.reparando = torch.zeros(m.B, dtype=torch.bool, device=m.vida.device)

        def extra(self, m, W, F):
            self.F = F
            return torch.zeros(m.B, F.shape[1], device=F.device, dtype=F.dtype)

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
            e_tem_pax = F[:, 0, 18]
            dinh = e_dinh * 150.0

            disp = tudo[:, G:G + S] > -1e8
            no_posto = disp[:, 0]
            no_oficina = disp[:, 9]
            carregando = e_tem_pax > 0.5

            mover_alvo = torch.argmin(F[:, :, 0], dim=1)
            mover_oficina_dir = torch.argmin(F[:, :, 4], dim=1)

            # (1) reparo: entra com e_vida<.5 e dinheiro>20; so' sai do modo quando e_vida>.8 (latch, precisa varias visitas)
            comeca_reparo = (e_vida < 0.5) & (dinh > 20)
            self.reparando = self.reparando | comeca_reparo
            sai_reparo = e_vida > 0.8
            self.reparando = self.reparando & (~sai_reparo)
            quer_reparo = self.reparando & (dinh > 20)

            # (2) resfriar: calor alto e sem passageiro (oficina zera calor)
            quer_resfriar = (e_calor > 0.75) & (~carregando)

            quer_oficina = quer_reparo | quer_resfriar
            comprar_oficina = quer_oficina & no_oficina

            # trabalho continuo (NUNCA argmin de d_posto); desvia so' pra oficina quando precisa e nao esta nela
            mover = torch.where(quer_oficina & (~no_oficina), mover_oficina_dir, mover_alvo)

            score = torch.full((B, S), -1e9, device=device, dtype=dtype)

            quer_agua = e_agua < 0.8
            quer_comida = e_fome > 0.2
            # agente 2: abastece 100L SEMPRE que houver $>40 no posto (nao so' quando e_fuel baixo) -> menos panes
            quer_fuel = (dinh > 40) | (e_fuel < 0.95)

            score[:, 5] = torch.where(no_posto & quer_agua, 30.0 + (0.8 - e_agua), score[:, 5])
            score[:, 7] = torch.where(no_posto & quer_comida, 20.0 + (e_fome - 0.2), score[:, 7])

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

            # oficina tem prioridade sobre compras de posto (dano mata mais rapido que fome/sede)
            score[:, 9] = torch.where(comprar_oficina, 50.0 + (1.0 - e_vida), score[:, 9])

            melhor = torch.argmax(score, dim=1)
            comprar = score.gather(1, melhor.unsqueeze(1)).squeeze(1) > -1e8

            # emergencia fora do posto: so' se ja esta ao lado (nao desvia por vontade)
            fora_agua = (~no_posto) & (e_agua < 0.15) & (F[:, G - 1, 3] < 8) & disp[:, 5]
            fora_comida = (~no_posto) & (e_fome > 0.85) & (F[:, G - 1, 2] < 8) & disp[:, 7]

            acao = mover.clone()
            acao = torch.where(fora_agua, torch.full_like(acao, G + 5), acao)
            acao = torch.where(fora_comida, torch.full_like(acao, G + 7), acao)
            acao = torch.where(comprar, G + melhor, acao)

            return acao.long()

        def atualizar(self, m):
            pass

    return PoliticaConstrucao2R6