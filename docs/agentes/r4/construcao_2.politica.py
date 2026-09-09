import torch

G = 9  # 8 direcoes + ficar (index 8)
S = 10  # servicos


def fabrica():
    class Politica:
        def reset(self, m, W):
            self.W = W
            # 0 trabalhar, 1 abastecer, 2 emerg-comida, 3 descanso — maquina de estado com histerese
            self.modo = torch.zeros(m.B, dtype=torch.long, device=W.device)

        def extra(self, m, W, F):
            self.F = F
            dev = F.device
            cur = F[:, 8, :]  # linha 'ficar' = leitura do agora, sem mover
            e_fuel = cur[:, 10]; e_agua = cur[:, 11]; e_fome = cur[:, 12]; e_fadiga = cur[:, 13]
            e_noite = cur[:, 21]; e_risco = cur[:, 26]
            d_comida = cur[:, 2]; d_descanso = cur[:, 5]

            m1, m2, m3 = self.modo.eq(1), self.modo.eq(2), self.modo.eq(3)

            precisa_abastecer = (e_risco > 0) | (e_fuel < .15)
            sai_abastecer = m1 & (e_fuel > .6) & (e_risco <= 0)   # so sai depois de topar (evita ping-pong perto do gatilho)

            emerg_comida = (e_fome > .8) & (d_comida < 15)
            sai_emerg = m2 & (e_fome < .3)

            quer_descanso = (e_noite > .5) & (e_fadiga > .8) & (d_descanso < 10)
            sai_descanso = m3 & ((e_fadiga < .3) | (e_noite <= .5))

            fica_abastecer = m1 & ~sai_abastecer
            fica_emerg = m2 & ~sai_emerg
            fica_descanso = m3 & ~sai_descanso

            p_abastecer = precisa_abastecer | fica_abastecer
            p_emerg = (emerg_comida | fica_emerg) & ~p_abastecer
            p_descanso = (quer_descanso | fica_descanso) & ~p_abastecer & ~p_emerg

            novo = torch.zeros_like(self.modo)
            novo = torch.where(p_descanso, torch.full_like(novo, 3), novo)
            novo = torch.where(p_emerg, torch.full_like(novo, 2), novo)
            novo = torch.where(p_abastecer, torch.full_like(novo, 1), novo)
            self.modo = novo

            return torch.zeros(m.B, G, device=dev)

        def _compra(self, tudo, cur):
            B = cur.shape[0]
            dev = cur.device
            e_fuel = cur[:, 10]; e_agua = cur[:, 11]; e_fome = cur[:, 12]; e_risco = cur[:, 26]

            compra = torch.full((B,), -1, dtype=torch.long, device=dev)
            precisa_fuel = (e_risco > 0) | (e_fuel < .6)
            for k in (4, 3, 2, 1, 0):  # 150,100,75,50,25 — o maior que o dinheiro paga primeiro
                avail = tudo[:, G + k] > -1e8
                compra = torch.where(precisa_fuel & avail & (compra < 0),
                                      torch.full((B,), G + k, dtype=torch.long, device=dev), compra)

            falta_fuel = precisa_fuel & (compra < 0)  # queria mas nao deu (sem dinheiro/fora do raio): usa a parada p/ agua/comida
            pode_outro = (~precisa_fuel) | falta_fuel

            quer_agua = pode_outro & (e_agua < .7)
            for k in (6, 5):  # agua 100 antes de 50, mesma logica "o maior que paga"
                avail = tudo[:, G + k] > -1e8
                compra = torch.where(quer_agua & avail & (compra < 0),
                                      torch.full((B,), G + k, dtype=torch.long, device=dev), compra)

            quer_comida = pode_outro & (e_fome > .25)
            avail_comida = tudo[:, G + 7] > -1e8
            compra = torch.where(quer_comida & avail_comida & (compra < 0),
                                  torch.full((B,), G + 7, dtype=torch.long, device=dev), compra)

            return compra

        def decidir(self, tudo, m):
            F = self.F
            dev = F.device
            INF = float('inf')

            def ir(col):
                d = F[:, :, col].clone()
                d[:, 8] = INF  # nunca devolver 8 (ficar)
                return torch.argmin(d, dim=1)

            mov_alvo = ir(0)
            mov_posto = ir(1)
            mov_comida = ir(2)
            mov_descanso = ir(5)

            m1, m2, m3 = self.modo.eq(1), self.modo.eq(2), self.modo.eq(3)

            # (1) default: trabalhar, ir ao alvo (passageiro/destino) — nunca ficar parado esperando
            acao = mov_alvo.clone()

            # (5) modo descanso: so entrou de madrugada com fadiga alta e descanso perto
            at_descanso = tudo[:, G + 8] > -1e8
            acao = torch.where(m3 & at_descanso, torch.full_like(acao, G + 8), acao)
            acao = torch.where(m3 & ~at_descanso, mov_descanso, acao)

            # (4) modo emergencia de fome fora do posto
            at_comida = tudo[:, G + 7] > -1e8
            acao = torch.where(m2 & at_comida, torch.full_like(acao, G + 7), acao)
            acao = torch.where(m2 & ~at_comida, mov_comida, acao)

            # (2)+(3) modo abastecer: vai ao posto mais perto e, la, topa combustivel/agua/comida numa so parada
            at_posto = tudo[:, G + 0] > -1e8
            compra = self._compra(tudo, F[:, 8, :])
            tem_compra = compra >= 0
            acao = torch.where(m1 & at_posto & tem_compra, compra, acao)
            acao = torch.where(m1 & at_posto & ~tem_compra, mov_alvo, acao)  # ja topou tudo: volta a trabalhar nesta parada
            acao = torch.where(m1 & ~at_posto, mov_posto, acao)

            return acao.long()

        def atualizar(self, m):
            pass

    return Politica