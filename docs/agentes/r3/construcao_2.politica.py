import torch


def fabrica():
    NOMES_OP = ['d_alvo', 'd_posto', 'd_comida', 'd_agua', 'd_oficina', 'd_descanso',
                'custo_frente', 'preco_frente', 'aliq_frente', 'casa_frente']
    IDX = {n: i for i, n in enumerate(NOMES_OP)}
    NOMES_CORPO = ['e_fuel', 'e_agua', 'e_fome', 'e_fadiga', 'e_calor', 'e_vida', 'e_dinheiro',
                   'e_reserva', 'e_tem_pax', 'h_sin', 'h_cos', 'e_noite', 'custo_aqui', 'bias',
                   'e_consumo', 'e_autonomia', 'e_risco', 'e_demanda', 'e_espera']
    OFF = len(NOMES_OP)
    CIDX = {n: OFF + i for i, n in enumerate(NOMES_CORPO)}

    class Politica:
        def reset(self, s, m, W):
            s.modo = torch.zeros(m.B, dtype=torch.long, device=m.dinh.device)

        def extra(self, s, m, W, F):
            s.F = F
            return torch.zeros(m.B, F.shape[1], device=F.device)

        def decidir(self, s, tudo, m):
            F = s.F
            G = F.shape[1]
            c = F[:, 0, :]  # corpo e' igual nas 9 opcoes

            autonomia = c[:, CIDX['e_autonomia']]
            fome = c[:, CIDX['e_fome']]
            agua = c[:, CIDX['e_agua']]
            fadiga = c[:, CIDX['e_fadiga']]
            noite = c[:, CIDX['e_noite']] > 0.5

            modo = s.modo
            entra_fuel = autonomia < 0.30
            sai_fuel = autonomia > 0.50
            entra_fome = fome > 0.60
            sai_fome = fome < 0.40
            entra_agua = agua < 0.35
            sai_agua = agua > 0.55

            novo = modo.clone()
            novo = torch.where(entra_fuel, torch.full_like(novo, 1), novo)
            novo = torch.where((modo == 1) & sai_fuel & ~entra_fuel, torch.zeros_like(novo), novo)
            novo = torch.where(entra_fome & (novo != 1), torch.full_like(novo, 2), novo)
            novo = torch.where((modo == 2) & sai_fome & ~entra_fome & (novo != 1), torch.zeros_like(novo), novo)
            novo = torch.where(entra_agua & (novo != 1) & (novo != 2), torch.full_like(novo, 3), novo)
            novo = torch.where((modo == 3) & sai_agua & ~entra_agua & (novo != 1) & (novo != 2), torch.zeros_like(novo), novo)
            s.modo = novo
            modo = novo

            acao = torch.full((m.B,), 8, dtype=torch.long, device=m.dinh.device)

            # ---------- 1. EMERGENCIA ----------
            alvo_posto = torch.argmin(F[:, :, IDX['d_posto']], dim=1)
            alvo_comida = torch.argmin(F[:, :, IDX['d_comida']], dim=1)
            alvo_agua = torch.argmin(F[:, :, IDX['d_agua']], dim=1)

            em_fuel = modo == 1
            comprar_100 = tudo[:, G + 3] > -1e8
            comprar_75 = tudo[:, G + 2] > -1e8
            comprar_50 = tudo[:, G + 1] > -1e8
            comprar_25 = tudo[:, G + 0] > -1e8
            acao_fuel = torch.where(comprar_100, torch.full_like(acao, G + 3),
                        torch.where(comprar_75, torch.full_like(acao, G + 2),
                        torch.where(comprar_50, torch.full_like(acao, G + 1),
                        torch.where(comprar_25, torch.full_like(acao, G + 0), alvo_posto))))
            acao = torch.where(em_fuel, acao_fuel, acao)

            em_fome = modo == 2
            comprar_comida = tudo[:, G + 7] > -1e8
            acao_fome = torch.where(comprar_comida, torch.full_like(acao, G + 7), alvo_comida)
            acao = torch.where(em_fome, acao_fome, acao)

            em_agua = modo == 3
            comprar_agua100 = tudo[:, G + 6] > -1e8
            comprar_agua50 = tudo[:, G + 5] > -1e8
            acao_agua = torch.where(comprar_agua100, torch.full_like(acao, G + 6),
                        torch.where(comprar_agua50, torch.full_like(acao, G + 5), alvo_agua))
            acao = torch.where(em_agua, acao_agua, acao)

            # ---------- 2. OPORTUNISMO (so' fora de emergencia) ----------
            sem_emergencia = modo == 0
            no_posto = tudo[:, G + 0] > -1e8
            oport_comida = no_posto & (fome > 0.30) & comprar_comida
            oport_agua = no_posto & (agua < 0.60) & (comprar_agua100 | comprar_agua50)
            acao_oport = torch.where(oport_comida, torch.full_like(acao, G + 7),
                         torch.where(comprar_agua100, torch.full_like(acao, G + 6),
                         torch.full_like(acao, G + 5)))
            usa_oport = sem_emergencia & (oport_comida | oport_agua)
            acao = torch.where(usa_oport, acao_oport, acao)

            # ---------- 3. TRABALHO ----------
            trabalho = sem_emergencia & ~usa_oport
            descansar = trabalho & noite & (fadiga > 0.70)
            pode_descansar = tudo[:, G + 8] > -1e8
            alvo_descanso = torch.argmin(F[:, :, IDX['d_descanso']], dim=1)
            acao_descanso = torch.where(pode_descansar, torch.full_like(acao, G + 8), alvo_descanso)
            alvo_trabalho = torch.argmin(F[:, :, IDX['d_alvo']], dim=1)
            acao_trabalho = torch.where(descansar, acao_descanso, alvo_trabalho)
            acao = torch.where(trabalho, acao_trabalho, acao)

            return acao

        def atualizar(self, s, m):
            pass

    return Politica