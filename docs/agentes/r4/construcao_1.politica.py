import torch

G = 9  # 8 direcoes + ficar (index 8)
S = 10  # servicos


def fabrica():
    class Politica:
        def reset(self, m, W):
            self.W = W

        def extra(self, m, W, F):
            self.F = F
            return torch.zeros(m.B, G, device=F.device)

        def decidir(self, tudo, m):
            F = self.F
            B = F.shape[0]
            dev = F.device
            INF = float('inf')

            # linha g=8 (ficar) = distancias/estado SEM mover = leitura do "agora"
            cur = F[:, 8, :]
            e_fuel = cur[:, 10]
            e_agua = cur[:, 11]
            e_fome = cur[:, 12]
            e_fadiga = cur[:, 13]
            e_noite = cur[:, 21]
            e_risco = cur[:, 26]
            d_comida = cur[:, 2]
            d_descanso = cur[:, 5]

            at_posto = tudo[:, G + 0] > -1e8
            at_descanso = tudo[:, G + 8] > -1e8
            precisa_posto = (e_risco > 0) | (e_fuel < 0.15)

            def ir(col):
                d = F[:, :, col].clone()
                d[:, 8] = INF  # nunca devolver 8 (ficar)
                return torch.argmin(d, dim=1)

            mov_alvo = ir(0)
            mov_comida = ir(2)
            mov_descanso = ir(5)
            mov_posto = ir(1)

            # (1) default: trabalhar, ir ao alvo (passageiro/destino)
            acao = mov_alvo

            # (4) comida fora do posto so em emergencia e perto
            cond = (e_fome > 0.8) & (d_comida < 15) & (~at_posto)
            acao = torch.where(cond, mov_comida, acao)

            # (5) descanso so de madrugada, com fadiga alta e perto
            cond_desc = (e_noite > 0.5) & (e_fadiga > 0.8)
            cond = cond_desc & (d_descanso < 10) & (~at_descanso)
            acao = torch.where(cond, mov_descanso, acao)
            cond = cond_desc & at_descanso
            acao = torch.where(cond, torch.full_like(acao, G + 8), acao)

            # (2) luz de reserva acesa ou tanque < 15%: ir ao posto mais perto
            cond = precisa_posto & (~at_posto)
            acao = torch.where(cond, mov_posto, acao)

            # (3) no posto: abastecer aguas/comida ANTES de sair
            pode_50 = tudo[:, G + 1] > -1e8
            pode_100 = tudo[:, G + 3] > -1e8
            compra_fuel = torch.full((B,), G + 0, dtype=torch.long, device=dev)
            compra_fuel = torch.where(pode_50, torch.full_like(compra_fuel, G + 1), compra_fuel)
            compra_fuel = torch.where((m.dinh > 35) & pode_100, torch.full_like(compra_fuel, G + 3), compra_fuel)

            compra_comida_ok = (tudo[:, G + 7] > -1e8) & (e_fome > 0.25)
            compra_agua_ok = (tudo[:, G + 5] > -1e8) & (e_agua < 0.7)

            acao = torch.where(at_posto & compra_comida_ok, torch.full_like(acao, G + 7), acao)
            acao = torch.where(at_posto & compra_agua_ok, torch.full_like(acao, G + 5), acao)
            acao = torch.where(at_posto & precisa_posto, compra_fuel, acao)

            return acao

        def atualizar(self, m):
            pass

    return Politica