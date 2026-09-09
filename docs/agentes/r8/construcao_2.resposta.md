PREDICAO: mortos 0.60–0.68 (meta ≤0.68), corridas 19–21, renda 170–185, refeições 7–9, fração de "ficar" no traço ≈ 0% (mover/ir_oficina/ir_comida_mov agora argmin só nas 8 direções, nunca na coluna 8). Mecanismo esperado: eliminar ficar converte tempo morto em corrida → mais renda → mais comida (limiar de compra caiu pra .10, come mais cedo) → fome deixa de ser causa dominante; reparo só com caixa >25 guarda dinheiro pra comida mas pode deixar dano/calor crescer sem reparo em rodadas de caixa baixa — se piorar, é dano que mata, não fome.

```python
import torch


def fabrica():
    class PoliticaConstrucaoR8A2:
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
            dinh = e_dinh * 150.0
            tem_pax = e_pax > 0.5

            disp = tudo[:, G:G + S] > -1e8
            no_posto = disp[:, 0]
            no_oficina = disp[:, 9]

            # NUNCA ficar (indice 8): argmin restrito as 8 direcoes (0..7), excluindo a
            # coluna "ficar" do campo F. Na r7 o argmin incluia a opcao 8 e escolhia
            # "ficar" sempre que d_alvo=0 (ja no alvo) virava minimo -> 23% do traco parado.
            mover = torch.argmin(F[:, :8, 0], dim=1)
            ir_oficina = torch.argmin(F[:, :8, 4], dim=1)
            ir_comida_mov = torch.argmin(F[:, :8, 2], dim=1)

            score = torch.full((B, S), -1e9, device=device, dtype=dtype)

            LIMIAR_FOME_POSTO = 0.10  # agente 2: come mais cedo que r7 (.15) pra caixa nao virar fome
            quer_agua = e_agua < 0.8
            quer_comida = e_fome > LIMIAR_FOME_POSTO
            quer_fuel = e_fuel < 0.95

            # placar de compra no posto (agua > comida > gasolina) via argmax
            score[:, 5] = torch.where(no_posto & quer_agua, 30.0 + (0.8 - e_agua), score[:, 5])
            score[:, 7] = torch.where(no_posto & quer_comida, 20.0 + (e_fome - LIMIAR_FOME_POSTO), score[:, 7])

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
            segunda = no_posto & self.comeu_ultimo_tick & (e_fome > LIMIAR_FOME_POSTO) & (dinh > 30) & disp[:, 7]

            # fora do posto: ir a comida de longe (deslocamento planejado, nao emergencia)
            buscar_comida = (~no_posto) & (e_fome > 0.55) & (F[:, G - 1, 2] < 20)

            # emergencia fora do posto: so' se ja esta ao lado
            fora_agua = (~no_posto) & (e_agua < 0.15) & (F[:, G - 1, 3] < 8) & disp[:, 5]
            fora_comida = (~no_posto) & (e_fome > 0.85) & (F[:, G - 1, 2] < 8) & disp[:, 7]

            # REPARO: guarda caixa pra comida. So' inicia com dinheiro > 25 (era > 20 na r7);
            # mantem reparo ja iniciado com dinh > 15 (histerese, evita cancelar no meio do conserto).
            ini_vida = (e_vida < 0.5) & (dinh > 25)
            self.reparando_vida = (self.reparando_vida | ini_vida) & (e_vida < 0.8) & (dinh > 15)
            quer_calor = (e_calor > 0.75) & (~tem_pax) & (dinh > 25)
            quer_oficina = self.reparando_vida | quer_calor

            comprar_oficina = no_oficina & quer_oficina & (tudo[:, G + 9] > -1e8)
            ir_oficina_mov = quer_oficina & (~comprar_oficina)

            # prioridade (menor pra maior, ultima escrita vence):
            # mover base < buscar comida de longe < detour oficina < compra posto < compra oficina
            # < emergencia agua/comida < segunda refeicao
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

    return PoliticaConstrucaoR8A2
```