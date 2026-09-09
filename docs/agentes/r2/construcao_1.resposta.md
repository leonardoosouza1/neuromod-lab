Escrevendo política, abordagem distinta (variação 1): histerese de emergência + navegação custo-aware (penaliza sair da rua) + combo comida/posto (loja no posto).

PREDICAO: mortos 0.40–0.55, entregas 8–12, refeições ≥15 (nunca mais 0 como rodada 1), abastecidas 4–6, fome_fim ≤40, dinheiro_fim 5–30 (aluguel/imposto comem margem); se morrer, causa provável vira fadiga/calor (não mapeados em camada própria) ou dívida por aluguel em distrito caro, não mais fome pura.

```python
import torch

G = 9  # 8 direcoes + ficar
OFF = 10  # offset onde comecam as colunas de corpo em F

# indices NOMES_OP
D_ALVO, D_POSTO, D_COMIDA, D_AGUA, D_OFICINA, D_DESCANSO, CUSTO_FRENTE = 0, 1, 2, 3, 4, 5, 6

# indices corpo (OFF + local)
E_FUEL, E_AGUA, E_FOME, E_FADIGA, E_CALOR, E_VIDA = OFF+0, OFF+1, OFF+2, OFF+3, OFF+4, OFF+5
E_DINHEIRO, E_NOITE, E_AUTONOMIA = OFF+6, OFF+11, OFF+15

# indices ACOES (servicos)
S_25L, S_50L, S_ENCHER, S_COMIDA, S_AGUA, S_HOTEL, S_OFICINA = 0, 1, 2, 3, 4, 5, 6


class PoliticaConstrucao1:
    def reset(s, m, W):
        dev = m.fuel.device
        B = m.B
        s.emerg_fuel = torch.zeros(B, dtype=torch.bool, device=dev)
        s.emerg_fome = torch.zeros(B, dtype=torch.bool, device=dev)
        s.emerg_vida = torch.zeros(B, dtype=torch.bool, device=dev)
        s.F = None

    def extra(s, m, W, F):
        s.F = F
        return torch.zeros(m.B, F.shape[1], device=F.device)

    def decidir(s, tudo, m):
        F = s.F
        B = m.B
        dev = F.device

        corpo = F[:, G - 1, :]  # opcao 'ficar' carrega os campos de corpo (iguais nas 9 opcoes)
        e_fuel = corpo[:, E_FUEL]
        e_agua = corpo[:, E_AGUA]
        e_fome = corpo[:, E_FOME]
        e_fadiga = corpo[:, E_FADIGA]
        e_vida = corpo[:, E_VIDA]
        e_noite = corpo[:, E_NOITE]
        e_autonomia = corpo[:, E_AUTONOMIA]

        d_alvo = F[:, :, D_ALVO]
        d_posto = F[:, :, D_POSTO]
        d_comida = F[:, :, D_COMIDA]
        d_agua = F[:, :, D_AGUA]
        d_oficina = F[:, :, D_OFICINA]
        d_descanso = F[:, :, D_DESCANSO]
        custo_frente = F[:, :, CUSTO_FRENTE]

        disp = tudo[:, G:] > -1e8
        n_serv = disp.shape[1]

        def disp_col(i):
            if i < n_serv:
                return disp[:, i]
            return torch.zeros(B, dtype=torch.bool, device=dev)

        esta_no_posto = d_posto[:, G - 1] < 0.5
        esta_na_comida = d_comida[:, G - 1] < 0.5
        esta_na_agua = d_agua[:, G - 1] < 0.5
        esta_na_oficina = d_oficina[:, G - 1] < 0.5

        # histerese: entra em emergencia num limiar, so sai num limiar mais folgado (evita oscilar)
        s.emerg_fuel = torch.where(e_autonomia < 0.15, torch.ones_like(s.emerg_fuel),
                        torch.where(e_autonomia > 0.35, torch.zeros_like(s.emerg_fuel), s.emerg_fuel))
        s.emerg_fome = torch.where(e_fome > 0.75, torch.ones_like(s.emerg_fome),
                        torch.where(e_fome < 0.30, torch.zeros_like(s.emerg_fome), s.emerg_fome))
        s.emerg_vida = torch.where(e_vida < 0.30, torch.ones_like(s.emerg_vida),
                        torch.where(e_vida > 0.55, torch.zeros_like(s.emerg_vida), s.emerg_vida))

        # navegacao custo-aware: penaliza opcao que sai da rua (custo_frente maior fora dela)
        pen = 0.5 * custo_frente
        ir_alvo = torch.argmin(d_alvo + pen, dim=1)
        ir_posto = torch.argmin(d_posto + pen, dim=1)
        ir_oficina = torch.argmin(d_oficina + pen, dim=1)
        ir_descanso = torch.argmin(d_descanso + pen, dim=1)
        # comida efetiva: posto tambem vende comida/agua (loja_no_posto) -> vai pro mais perto dos dois
        d_comida_ef = torch.minimum(d_comida, d_posto)
        ir_comida_ef = torch.argmin(d_comida_ef + pen, dim=1)

        acao = ir_alvo.clone()

        # camada 3: trabalho — madrugada + fadiga alta = descansar
        noite_cansado = (e_noite > 0.5) & (e_fadiga > 0.6)
        acao = torch.where(noite_cansado, ir_descanso, acao)

        # camada 2: oportunismo — ja no servico, compra o que precisa (tudo[:,G:] ja filtra por pagavel)
        pode_agua = disp_col(S_AGUA) & (e_agua < 0.7) & esta_na_agua
        acao = torch.where(pode_agua, torch.full_like(acao, G + S_AGUA), acao)
        pode_comida = disp_col(S_COMIDA) & (e_fome > 0.3) & (esta_na_comida | esta_no_posto)
        acao = torch.where(pode_comida, torch.full_like(acao, G + S_COMIDA), acao)
        pode_encher = disp_col(S_ENCHER) & (e_fuel < 0.7) & esta_no_posto
        acao = torch.where(pode_encher, torch.full_like(acao, G + S_ENCHER), acao)
        pode_oficina = disp_col(S_OFICINA) & (e_vida < 0.7) & esta_na_oficina
        acao = torch.where(pode_oficina, torch.full_like(acao, G + S_OFICINA), acao)

        # camada 1: emergencia — prioridade fuel > fome > vida (aplica por ultimo = mais prioridade)
        acao_vida = torch.where(disp_col(S_OFICINA) & esta_na_oficina, torch.full_like(acao, G + S_OFICINA), ir_oficina)
        acao = torch.where(s.emerg_vida, acao_vida, acao)

        acao_fome = torch.where(disp_col(S_COMIDA) & (esta_na_comida | esta_no_posto),
                                 torch.full_like(acao, G + S_COMIDA), ir_comida_ef)
        acao = torch.where(s.emerg_fome, acao_fome, acao)

        acao_fuel = torch.where(disp_col(S_ENCHER) & esta_no_posto, torch.full_like(acao, G + S_ENCHER), ir_posto)
        acao = torch.where(s.emerg_fuel, acao_fuel, acao)

        return acao.long()

    def atualizar(s, m):
        pass


def fabrica():
    return PoliticaConstrucao1
```