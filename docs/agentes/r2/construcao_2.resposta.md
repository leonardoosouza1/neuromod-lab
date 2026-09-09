PREDICAO: mortos 0.15–0.30 (vs 1.00 na rodada 1); entregas 12–16; refeicoes>=8 e abastecidas>=10 em 10 dias (fome_fim longe de 100, dinheiro_fim positivo ou dívida controlada); mecanismo distinto de rodada1: compra comida/agua tambem NO POSTO (loja_no_posto) e vai atras de passageiro mesmo a 30-60u (score contínuo, não corta d_alvo grande). Morte residual esperada, se houver: pane de combustível em corrida longa até passageiro distante, não fome parado.

```python
import torch

G = 9  # 8 direcoes + ficar (g=8)

# offsets em F[:, :, idx] (corpo = colunas 10..28, iguais nas 9 opcoes)
I_D_ALVO, I_D_POSTO, I_D_COMIDA, I_D_AGUA, I_D_OFICINA, I_D_DESCANSO = 0, 1, 2, 3, 4, 5
I_CUSTO_FRENTE, I_CASA_FRENTE = 6, 9
I_FUEL, I_AGUA, I_FOME, I_FAD, I_CALOR, I_VIDA, I_DINHEIRO = 10, 11, 12, 13, 14, 15, 16
I_NOITE, I_AUTONOMIA = 21, 25

# offsets em tudo[:, G:] (ACOES)
S_POSTO25, S_POSTO50, S_ENCHER, S_COMIDA, S_AGUA, S_HOTEL, S_OFICINA = 0, 1, 2, 3, 4, 5, 6


def _urg_low(x, thresh):
    # urgente quando x cai ABAIXO de thresh (niveis: combustivel, agua, vida, autonomia)
    return torch.clamp((thresh - x) / thresh, 0.0, 1.0) ** 3


def _urg_high(x, thresh):
    # urgente quando x sobe ACIMA de thresh (acumulos: fome, fadiga, calor)
    return torch.clamp((x - thresh) / (1.0 - thresh), 0.0, 1.0) ** 3


class PoliticaConstrucao2:
    """
    Variacao 2 (utilidade continua, sem cascata rigida if/elif):
    cada necessidade vira uma URGENCIA 0..1 (cubica, escala suave perto do limiar)
    que PESA a distancia ate o servico correspondente; as 9 opcoes de movimento
    sao pontuadas por uma soma ponderada de TODAS as necessidades ao mesmo tempo
    (nao so a mais critica) e o argmax escolhe. Compra so acontece quando ja se
    esta no servico (mascara tudo[:,G:] > -1e8), em 3 faixas de urgencia
    (oportunismo > 0.3, emergencia por limiar duro) aplicadas em ordem de
    prioridade crescente via torch.where (a ultima condicao verdadeira vence).
    """

    def reset(self, s, m, W):
        s.G = G

    def extra(self, s, m, W, F):
        s.F = F
        return torch.zeros(m.B, s.G, device=F.device)

    def decidir(self, s, tudo, m):
        F = s.F
        B = m.B
        dev = F.device
        corpo = F[:, 0, :]  # colunas 10.. sao iguais nas 9 opcoes

        e_fuel = corpo[:, I_FUEL]
        e_agua = corpo[:, I_AGUA]
        e_fome = corpo[:, I_FOME]
        e_fad = corpo[:, I_FAD]
        e_calor = corpo[:, I_CALOR]
        e_vida = corpo[:, I_VIDA]
        e_dinh = corpo[:, I_DINHEIRO]
        e_noite = corpo[:, I_NOITE]
        autonomia = corpo[:, I_AUTONOMIA]

        # ---- urgencias continuas (0..1) ----
        u_fuel = _urg_low(autonomia, 0.35)   # margem de alcance ate o posto
        u_agua = _urg_low(e_agua, 0.35)
        u_fome = _urg_high(e_fome, 0.55)
        u_fad = _urg_high(e_fad, 0.75)
        u_calor = _urg_high(e_calor, 0.80)
        u_vida = _urg_low(e_vida, 0.40)

        # ---- distancias por opcao de movimento (B, G) ----
        d_alvo = F[:, :, I_D_ALVO]
        d_posto = F[:, :, I_D_POSTO]
        d_comida = F[:, :, I_D_COMIDA]
        d_agua = F[:, :, I_D_AGUA]
        d_oficina = F[:, :, I_D_OFICINA]
        d_descanso = F[:, :, I_D_DESCANSO]
        custo_frente = F[:, :, I_CUSTO_FRENTE]

        # comida/agua tambem se compram no posto (loja_no_posto) -> usa o mais perto
        d_food_alvo = torch.minimum(d_posto, d_comida)
        d_water_alvo = torch.minimum(d_posto, d_agua)

        W_WORK, W_FUEL, W_AGUA, W_FOME, W_FAD, W_VIDA, W_CUSTO = 1.0, 3.0, 2.5, 2.5, 1.5, 3.0, 0.3

        score = (
            W_WORK * (-d_alvo)
            + W_FUEL * u_fuel.unsqueeze(1) * (-d_posto)
            + W_AGUA * u_agua.unsqueeze(1) * (-d_water_alvo)
            + W_FOME * u_fome.unsqueeze(1) * (-d_food_alvo)
            + W_FAD * u_fad.unsqueeze(1) * (-d_descanso)
            + W_VIDA * u_vida.unsqueeze(1) * (-d_oficina)
            - W_CUSTO * custo_frente
        )

        # calor: nao tem "lugar", esfria FICANDO PARADO (g=8) -> reforca ficar
        score[:, G - 1] = score[:, G - 1] + 4.0 * u_calor
        # de madrugada com fadiga, reforca ir descansar
        night_rest = (e_noite * torch.clamp(e_fad, 0.0, 1.0)).unsqueeze(1)
        score = score + 1.5 * night_rest * (-d_descanso)

        acao = torch.argmax(score, dim=1)

        # ---- compras: so valem se ja se esta no servico (mascara do ambiente) ----
        avail = tudo[:, G:] > -1e8
        casa_aqui = F[:, G - 1, I_CASA_FRENTE] > 0.5

        def buy(mask, idx_servico):
            nonlocal acao
            alvo = torch.full_like(acao, G + idx_servico)
            acao = torch.where(mask, alvo, acao)

        # camada oportunismo (prioridade baixa): topar tanque/agua/comida se ja parado ali e sobra dinheiro
        buy(avail[:, S_ENCHER] & ((1.0 - e_fuel) > 0.3) & (e_dinh > 0.02), S_ENCHER)
        buy(avail[:, S_AGUA] & ((1.0 - e_agua) > 0.3) & (e_dinh > 0.02), S_AGUA)
        buy(avail[:, S_COMIDA] & (e_fome > 0.3) & (e_dinh > 0.02), S_COMIDA)

        # camada emergencia (prioridade alta, sobrescreve oportunismo): limiar duro, quase sem checar dinheiro
        buy(avail[:, S_HOTEL] & (e_fad > 0.85) & (~casa_aqui) & (e_dinh > 0.05), S_HOTEL)
        buy(avail[:, S_OFICINA] & (e_vida < 0.35) & (e_dinh > 0.05), S_OFICINA)
        buy(avail[:, S_AGUA] & (e_agua < 0.20), S_AGUA)
        buy(avail[:, S_COMIDA] & (e_fome > 0.70), S_COMIDA)
        buy(avail[:, S_ENCHER] & (autonomia < 0.20), S_ENCHER)

        return acao.long()

    def atualizar(self, s, m):
        pass


def fabrica():
    return PoliticaConstrucao2
```