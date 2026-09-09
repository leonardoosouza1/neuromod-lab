PREDICAO: mortos ≈ 0.30–0.40 (abaixo do campeão 0.82 e do oráculo 1.00); entregas médias ≈ 10–15 por sobrevivente em 10 dias (menos que um campeão otimizado, pois só vai ao alvo mais próximo, sem otimizar rota/receita). O que mata quem sobrar: dívida (LIMITE_DIVIDA 60) por aluguel+imposto batendo antes da primeira renda acumular (dinh0=10 é pouco) e pane de calor residual (a cascata só esfria taxi parado por fadiga/hotel, não trata calor como gatilho direto).

Abordagem (variação 1 — cascata de prioridade explícita, sem scoring/pesos): pilha de regras booleanas com limiar fixo, sobrevivência antes de economia, cada regra de prioridade mais alta sobrescreve a de baixo via `torch.where`. Difere de abordagem por utilidade/soma-ponderada.

```python
import torch

# NOMES_OP (colunas 0..9, por opção de movimento g)
D_ALVO, D_POSTO, D_COMIDA, D_AGUA, D_OFICINA, D_DESCANSO, CUSTO_FRENTE, PRECO_FRENTE, ALIQ_FRENTE, CASA_FRENTE = range(10)

# NOMES_CORPO (colunas 10.., iguais nas 9 opções)
_OFF = 10
(E_FUEL, E_AGUA, E_FOME, E_FADIGA, E_CALOR, E_VIDA, E_DINHEIRO, E_RESERVA, E_TEM_PAX,
 H_SIN, H_COS, E_NOITE, CUSTO_AQUI, BIAS, E_CONSUMO, E_AUTONOMIA, E_RISCO, E_DEMANDA, E_ESPERA) = range(_OFF, _OFF + 19)

# ACOES (colunas de serviço em 'tudo', após as G opções de movimento)
AC_POSTO25, AC_POSTO50, AC_POSTO_ENCHER, AC_COMIDA, AC_AGUA, AC_HOTEL, AC_OFICINA = range(7)

G = 9  # 8 direções + ficar


def fabrica():
    class PoliticaCascata:
        def reset(self, m, W):
            self.F = None

        def extra(self, m, W, F):
            self.F = F
            return torch.zeros(m.B, G, device=F.device, dtype=F.dtype)

        def decidir(self, tudo, m):
            F = self.F
            corpo = F[:, 0, :]  # colunas de corpo são iguais em todas as 9 opções

            e_fuel = corpo[:, E_FUEL]
            e_agua = corpo[:, E_AGUA]
            e_fome = corpo[:, E_FOME]
            e_fad = corpo[:, E_FADIGA]
            e_vida = corpo[:, E_VIDA]
            e_dinheiro = corpo[:, E_DINHEIRO]
            e_autonomia = corpo[:, E_AUTONOMIA]
            e_noite = corpo[:, E_NOITE]
            sem_pax = corpo[:, E_TEM_PAX] < 0.5

            d_alvo = F[:, :, D_ALVO]          # (B, 9)
            d_posto = F[:, :, D_POSTO]        # (B, 9)
            preco_frente = F[:, :, PRECO_FRENTE]

            serv = tudo[:, G:]                # disponível E pago
            tem_posto_encher = serv[:, AC_POSTO_ENCHER] > -1e8
            tem_comida = serv[:, AC_COMIDA] > -1e8
            tem_agua = serv[:, AC_AGUA] > -1e8
            tem_hotel = serv[:, AC_HOTEL] > -1e8
            tem_oficina = serv[:, AC_OFICINA] > -1e8

            # base: vai ao alvo, evitando direção cara quando pobre
            pobre = (e_dinheiro < 0.15).unsqueeze(1)
            caro = preco_frente > preco_frente.mean(dim=1, keepdim=True)
            penal = torch.where(pobre & caro, torch.full_like(d_alvo, 50.0), torch.zeros_like(d_alvo))
            acao = torch.argmin(d_alvo + penal, dim=1)

            # prioridade 1: descansar de madrugada se fadiga alta, sem passageiro, hotel aqui
            quer_descansar = (e_fad > 0.7) & (e_noite > 0.5) & tem_hotel & sem_pax
            acao = torch.where(quer_descansar, torch.full_like(acao, G + AC_HOTEL), acao)

            # prioridade 2: comer se fome alta e comida aqui
            quer_comer = (e_fome > 0.7) & tem_comida
            acao = torch.where(quer_comer, torch.full_like(acao, G + AC_COMIDA), acao)

            # prioridade 3: beber se água baixa e disponível aqui
            quer_beber = (e_agua < 0.3) & tem_agua
            acao = torch.where(quer_beber, torch.full_like(acao, G + AC_AGUA), acao)

            # prioridade 4: reparar se vida baixa e oficina aqui
            quer_reparo = (e_vida < 0.5) & tem_oficina
            acao = torch.where(quer_reparo, torch.full_like(acao, G + AC_OFICINA), acao)

            # prioridade 5: ir ao posto se combustível crítico ou margem de alcance curta
            fuel_critico = (e_fuel < 0.30) | (e_autonomia < 0.15)
            acao_ir_posto = torch.argmin(d_posto, dim=1)
            acao = torch.where(fuel_critico, acao_ir_posto, acao)

            # prioridade 6 (máxima): encher tanque se já está no posto e não está cheio
            quer_encher = (e_fuel < 0.90) & tem_posto_encher
            acao = torch.where(quer_encher, torch.full_like(acao, G + AC_POSTO_ENCHER), acao)

            return acao.long()

        def atualizar(self, m):
            pass

    return PoliticaCascata
```