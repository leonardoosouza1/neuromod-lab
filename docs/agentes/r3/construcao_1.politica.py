import torch


class PoliticaUrgenciaMax:
    IDX = {
        'd_alvo': 0, 'd_posto': 1, 'd_comida': 2, 'd_agua': 3, 'd_oficina': 4, 'd_descanso': 5,
        'custo_frente': 6, 'preco_frente': 7, 'aliq_frente': 8, 'casa_frente': 9,
        'e_fuel': 10, 'e_agua': 11, 'e_fome': 12, 'e_fadiga': 13, 'e_calor': 14, 'e_vida': 15,
        'e_dinheiro': 16, 'e_reserva': 17, 'e_tem_pax': 18, 'h_sin': 19, 'h_cos': 20,
        'e_noite': 21, 'custo_aqui': 22, 'bias': 23, 'e_consumo': 24, 'e_autonomia': 25,
        'e_risco': 26, 'e_demanda': 27, 'e_espera': 28,
    }

    def reset(self, s, m, W):
        pass

    def extra(self, s, m, W, F):
        s.F = F
        return torch.zeros(m.B, F.shape[1], device=F.device, dtype=F.dtype)

    def decidir(self, s, tudo, m):
        F = s.F
        B, G = F.shape[0], F.shape[1]
        dev = F.device

        def corpo(nome):
            return F[:, 0, self.IDX[nome]]

        e_autonomia = corpo('e_autonomia')
        e_fome = corpo('e_fome')
        e_agua = corpo('e_agua')
        e_fadiga = corpo('e_fadiga')
        e_noite = corpo('e_noite')

        acao = torch.full((B,), 8, dtype=torch.long, device=dev)
        decidido = torch.zeros(B, dtype=torch.bool, device=dev)

        # ---------- (1) EMERGENCIA: severidade 0..1, age na pior por agente ----------
        urg_fuel = torch.clamp((0.3 - e_autonomia) / 0.3, min=0.0)
        urg_agua = torch.clamp((0.35 - e_agua) / 0.35, min=0.0)
        urg_fome = torch.clamp((e_fome - 0.6) / 0.4, min=0.0)

        urg = torch.stack([urg_fuel, urg_agua, urg_fome], dim=1)
        pior, qual = urg.max(dim=1)
        em_emergencia = pior > 0.0

        alvo_posto = F[:, :, self.IDX['d_posto']].argmin(dim=1)
        alvo_comida = F[:, :, self.IDX['d_comida']].argmin(dim=1)
        alvo_agua = F[:, :, self.IDX['d_agua']].argmin(dim=1)

        pode_posto25 = tudo[:, G + 0] > -1e8
        pode_posto50 = tudo[:, G + 1] > -1e8
        pode_posto75 = tudo[:, G + 2] > -1e8
        pode_posto100 = tudo[:, G + 3] > -1e8
        pode_agua50 = tudo[:, G + 5] > -1e8
        pode_agua100 = tudo[:, G + 6] > -1e8
        pode_comida = tudo[:, G + 7] > -1e8
        pode_descanso = tudo[:, G + 8] > -1e8

        m_fuel = em_emergencia & (qual == 0)
        acao_fuel = torch.where(
            pode_posto100, torch.full_like(acao, G + 3),
            torch.where(pode_posto75, torch.full_like(acao, G + 2),
            torch.where(pode_posto50, torch.full_like(acao, G + 1),
            torch.where(pode_posto25, torch.full_like(acao, G + 0), alvo_posto))))
        acao = torch.where(m_fuel, acao_fuel, acao)
        decidido = decidido | m_fuel

        m_agua = em_emergencia & (qual == 1) & ~decidido
        acao_agua = torch.where(
            pode_agua100, torch.full_like(acao, G + 6),
            torch.where(pode_agua50, torch.full_like(acao, G + 5), alvo_agua))
        acao = torch.where(m_agua, acao_agua, acao)
        decidido = decidido | m_agua

        m_fome = em_emergencia & (qual == 2) & ~decidido
        acao_fome = torch.where(pode_comida, torch.full_like(acao, G + 7), alvo_comida)
        acao = torch.where(m_fome, acao_fome, acao)
        decidido = decidido | m_fome

        # ---------- (2) OPORTUNISMO: ja no posto, abastece corpo antes de sair ----------
        no_posto = pode_posto25 & ~decidido
        quer_comida = no_posto & (e_fome > 0.3) & pode_comida
        acao = torch.where(quer_comida, torch.full_like(acao, G + 7), acao)
        decidido = decidido | quer_comida

        quer_agua = no_posto & ~decidido & (e_agua < 0.6) & (pode_agua100 | pode_agua50)
        acao_agua_op = torch.where(pode_agua100, torch.full_like(acao, G + 6), torch.full_like(acao, G + 5))
        acao = torch.where(quer_agua, acao_agua_op, acao)
        decidido = decidido | quer_agua

        # ---------- descanso de madrugada (parte do bom senso da camada 3) ----------
        alvo_descanso = F[:, :, self.IDX['d_descanso']].argmin(dim=1)
        quer_descanso = ~decidido & (e_noite > 0.5) & (e_fadiga > 0.7)
        acao_descanso = torch.where(pode_descanso, torch.full_like(acao, G + 8), alvo_descanso)
        acao = torch.where(quer_descanso, acao_descanso, acao)
        decidido = decidido | quer_descanso

        # ---------- (3) TRABALHO: default, rumo ao passageiro/destino ----------
        alvo_trabalho = F[:, :, self.IDX['d_alvo']].argmin(dim=1)
        acao = torch.where(~decidido, alvo_trabalho, acao)

        return acao

    def atualizar(self, s, m):
        pass


def fabrica():
    return PoliticaUrgenciaMax