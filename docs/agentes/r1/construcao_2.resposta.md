PREDICAO: mortos ~0.35–0.45 (bate a barra ≤0.50); entregas ~10–14 em 10 dias (abaixo do campeão 0.82 porque desvia pra serviço antes de virar emergência). O que mata o resto: espiral de dívida — repor combustível/água/comida com frequência alta (fome_passo .32) consome caixa mais rápido que a tarifa recompõe quando passageiro fica longe (LIMITE_DIVIDA 60 estoura → aluguel não pago → vida cai por hotel/despejo), não pane física direta (autonomia com margem .15 e vida <.30 cobertas antes do limite).

Abordagem (var. 2, diferente de cascata simples): prioridade por "pior necessidade vence" — score econômico na busca de passageiro (penaliza custo/tarifa da via quando dinheiro baixo) + cascata de sobrevivência aplicada em ordem crescente de urgência (descanso leve→fome→água→fadiga forte→combustível com margem de autonomia→vida→calor, cada uma sobrescrevendo a anterior), tudo vetorizado em torch sem loop por ser.

```python
import torch

IDX_D_ALVO = 0
IDX_D_POSTO = 1
IDX_D_COMIDA = 2
IDX_D_AGUA = 3
IDX_D_OFICINA = 4
IDX_D_DESCANSO = 5
IDX_CUSTO_FRENTE = 6
IDX_PRECO_FRENTE = 7
IDX_ALIQ_FRENTE = 8

IDX_E_FUEL = 10
IDX_E_AGUA = 11
IDX_E_FOME = 12
IDX_E_FADIGA = 13
IDX_E_CALOR = 14
IDX_E_VIDA = 15
IDX_E_DINHEIRO = 16
IDX_E_TEM_PAX = 18
IDX_E_NOITE = 21
IDX_E_AUTONOMIA = 25

AC_POSTO25 = 0
AC_POSTO_ENCHER = 2
AC_COMIDA = 3
AC_AGUA = 4
AC_HOTEL = 5
AC_OFICINA = 6

FICAR = 8
EPS = 1e-4
KAPPA_CUSTO = 0.6


def fabrica():
    class PoliticaPrioridadeSobrevivencia:
        def reset(s, m, W):
            s.W = W

        def extra(s, m, W, F):
            s.F = F
            return torch.zeros(m.B, F.shape[1], device=F.device)

        def _melhor_direcao(s, col):
            return torch.argmin(s.F[:, :, col], dim=1)

        def _chegou(s, col, g):
            F = s.F
            d = F.gather(1, g.view(-1, 1, 1).expand(-1, 1, F.shape[2]))[:, 0, col]
            return d < EPS

        def decidir(s, tudo, m):
            F = s.F
            G = F.shape[1]
            corpo = F[:, 0, :]

            e_fome = corpo[:, IDX_E_FOME]
            e_agua = corpo[:, IDX_E_AGUA]
            e_fadiga = corpo[:, IDX_E_FADIGA]
            e_calor = corpo[:, IDX_E_CALOR]
            e_vida = corpo[:, IDX_E_VIDA]
            e_dinheiro = corpo[:, IDX_E_DINHEIRO]
            e_noite = corpo[:, IDX_E_NOITE]
            e_autonomia = corpo[:, IDX_E_AUTONOMIA]
            tem_pax = corpo[:, IDX_E_TEM_PAX] > 0.5
            pobre = e_dinheiro < 0.10

            custo_via = F[:, :, IDX_CUSTO_FRENTE] + F[:, :, IDX_PRECO_FRENTE] * F[:, :, IDX_ALIQ_FRENTE]
            score_base = F[:, :, IDX_D_ALVO] + torch.where(
                pobre.unsqueeze(1), KAPPA_CUSTO * custo_via, torch.zeros_like(custo_via)
            )
            acao = torch.argmin(score_base, dim=1)

            def aplicar(mask, col, acao_idx):
                nonlocal acao
                if not mask.any():
                    return
                g_alt = s._melhor_direcao(col)
                chegou = s._chegou(col, g_alt)
                disponivel = tudo[:, G + acao_idx] > -1e8
                comprar = mask & chegou & disponivel
                mover = mask & ~comprar
                acao = torch.where(comprar, torch.full_like(acao, G + acao_idx), acao)
                acao = torch.where(mover, g_alt, acao)

            aplicar(e_noite.bool() & (e_fadiga > 0.40) & ~tem_pax, IDX_D_DESCANSO, AC_HOTEL)
            aplicar(e_fome > 0.70, IDX_D_COMIDA, AC_COMIDA)
            aplicar(e_agua < 0.30, IDX_D_AGUA, AC_AGUA)
            aplicar(e_fadiga > 0.80, IDX_D_DESCANSO, AC_HOTEL)

            mask_fuel = e_autonomia < 0.15
            if mask_fuel.any():
                usa_encher = tudo[:, G + AC_POSTO_ENCHER] > -1e8
                acao_posto = torch.where(
                    usa_encher, torch.full_like(acao, AC_POSTO_ENCHER), torch.full_like(acao, AC_POSTO25)
                )
                g_alt = s._melhor_direcao(IDX_D_POSTO)
                chegou = s._chegou(IDX_D_POSTO, g_alt)
                disponivel = torch.where(
                    usa_encher, tudo[:, G + AC_POSTO_ENCHER], tudo[:, G + AC_POSTO25]
                ) > -1e8
                comprar = mask_fuel & chegou & disponivel
                mover = mask_fuel & ~comprar
                acao = torch.where(comprar, G + acao_posto, acao)
                acao = torch.where(mover, g_alt, acao)

            aplicar(e_vida < 0.30, IDX_D_OFICINA, AC_OFICINA)

            acao = torch.where(e_calor > 0.85, torch.full_like(acao, FICAR), acao)

            return acao.long()

        def atualizar(s, m):
            pass

    return PoliticaPrioridadeSobrevivencia
```