# CONTEXTO (neuromod-lab, taxi na GPU)
Seres = taxis com corpo (gasolina, agua, fome, fadiga, calor, vida, dinheiro, reserva) que precisam sobreviver 10 dias (2400 ticks; 1 tick = 6 min)
numa cidade continua 200x200 com distritos (perfis centro/industrial/residencial/periferia), ruas (custo 1 na rua, 3 fora), servicos (posto, comida,
agua, descanso, oficina) e passageiros. Cerebros evoluidos por selecao. Achados: (84) no Linear os sentidos do corpo sao invisiveis na direcao;
(E64-E67) o campeao linear e' um pico local da regua 'riqueza 10 dias' (busca x4, gradiente e ruido nao mudam; morre 0.82); (E68, pred 95) o campeao
anda 82% do tempo, 67% com passageiro, espera livre 3%: no mundo antigo o passageiro nascia perto do taxi, entao lugar nao tinha preco;
(E70, rodando) passageiro agora nasce NA CIDADE (pax_cidade). Regra da casa: negativo com mecanismo e' resultado; predicao ANTES de rodar; sem portao desenhado a mao no cerebro.
## Ultimas predicoes (ledger)
| 92 | E65 SINAL DE APRENDIZADO no táxi (q9: ES antitético com utilidade por posto, σ .1 e .3, lr .3, MESMO orçamento e sementes do q8: P=2048, 300 ger., paciência 60, 5 sem., R=4, semeados do linear-com-luz, régua riqueza 10 d, E56c): se a hipótese do fechamento ('falta sinal, não busca') está certa, o ES sobe ≥ 10 pp pareado sobre o GA (mortos 0.82 → ≤ 0.72) em ≥ 1 σ, com ent ≥ 15; aposta: ✗ (empate ±5 pp) — o platô 'não dirigir' é do PANORAMA de fitness (degrau), não do otimizador; se ✓, o gargalo era o otimizador e o Minecraft NÃO é necessário para prová-lo | ✗ empate: ES σ .1 mortos 0.77 (−5.3 pp, IC −14.5/+3.8, p .18), ES σ .3 0.80 (−2 pp); nenhum otimizador sobe a fitness de treino (GA −0.18→0.00, ES −0.28→+0.14) |
| 93 | E66 SINAL/RUÍDO da nota (diag_snr: 2048 mutantes σ .3 do campeão linear s0, mesma população em 3 sorteios de mundo, R=4, mundo/régua do q8): se a seleção é loteria, corr(nota_A, nota_B) entre indivíduos < 0.3 e a elite de 15 % de um mundo se mantém elite no outro em < 30 % (acaso 15 %); e a DP da nota do MESMO clone entre mundos (σ 0) é ≥ a DP entre mutantes num mundo; aposta: ✓ — é por isso que GA e ES travam no mesmo lugar (mecanismo do platô: nota cega, não panorama plano) | ✗ a nota NÃO é cega na escala do GA: σ .3 corr 0.81, elite mantida 43–46 % (acaso 15); σ .1 corr 0.45 (meio-cega na escala fina); clones: DP 0.49 = ruído puro; fitness média cai com σ (−2.14/−2.47/−3.23) = campeão é PICO local |
| 94 | E67 última brecha do fechamento (q11: ES σ .1 com R=16 — nota média em 16 mundos, ruído /2 — mesmo P=2048, sementes, mundos e paciência do q9b2): se o platô era só ruído na escala fina, o ES sobe ≥ 10 pp pareado sobre o GA (mortos ≤ 0.72); aposta: ✗ (fica em 0.75–0.80) — a curva fitness×σ diz que o campeão é pico local desta régua, não vítima de ruído | ✗ ES σ .1 R=16: mortos 0.78 [0.737, 0.826, 0.82, 0.737, 0.789] (−4 pp, dentro da faixa apostada 0.75–0.80); treino sobe −1.21→−0.93 até a ger 30 e para (ger 61); ruído /2 não abre subida nova — pico local confirmado por 3 lados (busca, otimizador, ruído) |
| 95 | E68 PONTO DE TÁXI (Leonardo 09-08: 'parar pode ser esperar passageiro'): táxi parado+livre recebe passageiro no lugar com espera ponto/demanda (ponto=30: centro ~15 ticks, periferia ~100) + sentidos e_demanda/e_espera; mundo E56c, riqueza 10 d, 5 sem., R=4, P=1024, 120 ger. paciência 40, semeados do linear q8 (alinhado): (a) o bilinear risco+demanda+espera bate o linear ≥ 10 pp em mortos OU ≥ +20 % de renda pareada (o linear não vê o lugar ao decidir 'ficar', achado 84); (b) o linear no mundo com ponto entrega mais que no mundo sem (ent ≥ 22 vs 18) porque parar passou a render; aposta: ✓ em (b) e ✓ em (a) — é o primeiro mundo onde a peça tem o que pagar | ✗ (a) bilinear risco+demanda+espera 0.80 vs linear 0.81 (−1 pp; entrega 15.1 vs 18.3, renda −18 %); COMPLETO 0.73 (−7 pp, p .15). ✗ (b) linear entrega 18.3 com ponto vs 18.1 sem. MECANISMO (diag_ponto): o linear NUNCA espera livre (3 % do tempo; 82 % andando, 67 % com passageiro; 2 % dos embarques via ponto) porque o mundo dá passageiro de graça rodando (12 privados a 8–45 u, renascendo perto em qualquer distrito) — sem escassez, esperar e escolher lugar não valem nada. Só o COMPLETO usou o ponto (11 % esperando, 20 % via ponto) |
| 96 | E69 ESCASSEZ de passageiro (npx 3, respawn 100: periferia ~333 ticks por slot, centro ~50) + ponto 30 + sentidos; mesmo protocolo do q13 (P1024, 120 ger, pac 40, 5 sem., riqueza 10 d, semeados do linear q8): (a) o linear cego ao lugar cai: ent ≤ 12 e mortos ≥ 0.85; (b) COMPLETO ou bilinear risco+demanda+espera batem o linear ≥ 10 pp em mortos OU ≥ +30 % renda pareada, com espera livre ≥ 10 % do tempo concentrada em demanda alta; aposta: ✓ (a) e ✓ (b) pelo COMPLETO (único que já usa o ponto) — é a primeira vez que ONDE trabalhar tem preço | CANCELADA (parada aos 12 min, sem resultado): Leonardo — 'eles deveriam buscar o passageiro, não o passageiro aparecer do nada'; escassez do pool privado ainda faz o passageiro nascer perto do táxi |
| 97 | E70 PASSAGEIRO NA CIDADE (pax_cidade: nasce onde há demanda, em volta do centro do distrito; táxi vai buscar; reposição ~ demanda do lugar; ponto OFF; 12 passageiros na cidade toda), mesmo protocolo do q13 (P1024, 120 ger, pac 40, 5 sem., riqueza 10 d, semeados do linear q8), controle pareado = linear do q13b (passageiro perto): (a) o linear entrega menos (ent ≤ 14 vs 18) e morre mais (≥ +5 pp) porque agora tem de viajar; (b) COMPLETO ou bilinear risco+demanda+espera batem o linear ≥ 10 pp em mortos OU ≥ +30 % renda pareada — pela primeira vez ONDE estar tem preço e o linear não lê lugar na direção; aposta: ✓ (a), ✓ (b) pelo COMPLETO (3 apostas ✓ perdidas hoje: o mundo é quem decide) | ✓(a) linear 0.93 / ent 11.4 / dinh 11 (era 0.83 / 18 / 26); ✗(b) COMPLETO 0.91, bilinear+demanda 0.92, bilinear-risco 0.95: PISO — com 12 passageiros na cidade toda (mais perto a 31–56 u) todo mundo morre igual; a régua crava (degrau). Lugar passou a ter preço, mas ninguém consegue pagar: falta calibrar a densidade (npx 20–40) |
| 98 | R1 agentes — política explícita construcao_1 (Sonnet): PREDIÇÃO DO AGENTE mortos 0.30–0.40, 10–15 entregas | ✗ mortos 1.00, ent 3.7, renda 31, panes 0.2, fome_fim 100: estacionou e nunca comprou comida (morte por fome parado) |
| 99 | R1 agentes — política explícita construcao_2 (Sonnet): PREDIÇÃO DO AGENTE mortos 0.35–0.45, 10–14 entregas | ✗ mortos 1.00, ent 1.8, renda 15, panes 1.1, fome_fim 100: idem (fome, parado). Nenhuma política explícita jamais sobreviveu (oráculo 1.00, agentes 1.00 ×2) — candidata a achado: o mundo base pode ser insolúvel a 10 d com dinh0 10 |
## Contrato cenario.json e regras (doc 53)
# 53 — Agentes criam cenários e políticas; o simulador julga (receita Navier–Stokes, em casa, com Claude)

**OK do Leonardo (2026-09-08 22:40):** "achei legal a ideia de agents criarem as coisas e devemos fazer o que você
pontuou; via parâmetro algo melhor para criar os cenários, cidade e entre outros."

## O que copiamos da OpenAI e o que não
| Peça deles | Aqui |
|---|---|
| 10.000 agentes em grupos isolados | 3–4 grupos × 2 agentes **Sonnet** (`claude -p`, assinatura), ≤ 10 por rodada (handbook 91; nunca Fable) |
| Codex consolida ideias entre grupos | 1 **Opus** por rodada lê resultados + diários, extrai 3 insights, realoca tarefas |
| Lean checa cada passo | simulador determinístico na fila `nmd` + régua pareada + **predição escrita pelo agente antes de rodar** |
| Euler antes de Navier–Stokes | escada: cenário base → cidade (E70) → escasso → competição |
| humano escolhe problema, realoca, confere o enunciado | Leonardo escolhe o degrau, veta, decide o que é "natureza" e o que é "muleta" |
| internet em cache | docs 44–53, PREDICOES.md, acervo, achados 84 e 95 |

Lição central: a tese é nossa, a moagem é dos agentes, o juiz é obrigatório. Sem juiz, N agentes = N rascunhos.

## Contrato: `cenario.json` (v0)
Tudo que hoje é constante espalhada vira parâmetro num arquivo que um agente consegue escrever e o simulador lê:
```json
{"nome": "centro-caro-periferia-vazia", "predicao": "linear morre >= .85; completo <= .70 porque ...",
 "mundo": {"L": 200, "dias": 10, "regua": "riqueza", "K": 6, "ruas": {"dentro": 1, "fora": 3}, "nevoa": null,
           "precos": {"amp": 0.5, "periodo": 3}},
 "distritos": {"centro":      {"pmul": 2.0, "aliq": .35, "alug": 2.5, "dem": 2.0, "dens": [1.0, 1.5, 1.0, 0.5, 1.0]},
               "industrial":  {"pmul": 0.6, "aliq": .10, "alug": 0.8, "dem": 0.7, "dens": [2.5, 0.0, 1.0, 0.0, 2.0]},
               "residencial": {"pmul": 1.0, "aliq": .15, "alug": 1.0, "dem": 1.0, "dens": [0.0, 2.0, 1.5, 2.0, 0.0]},
               "periferia":   {"pmul": 0.5, "aliq": .00, "alug": 0.8, "dem": 0.3, "dens": [0.5, 0.5, 0.5, 0.5, 0.0]}},
 "passageiros": {"npx": 12, "respawn": 20, "pax_cidade": true, "ponto": 0, "tarifa_base": 3, "tarifa_km": .25},
 "corpo": {"dinh0": 10, "fome_passo": .32, "kcal_pane": 8, "guincho": 0, "fuel_pos_pane": 15},
 "bracos": ["linear", "COMPLETO (talamo+cortex+hipocampo+reflexo+livre)"], "protocolo": {"P": 1024, "G": 120, "paciencia": 40, "R": 4, "seeds": [0,1,2,3,4]}}
```
`dens` = multiplicador de densidade por serviço (posto, comida, água, descanso, oficina). O loader (`e43_campo --cenario`)
aplica em `CfgCampo` e em `gerar_mapa(perfis=...)`; tudo que o cenário não define fica no default (identidade preservada).
Um cenário sem `predicao` é recusado pelo orquestrador.

## Rodada (3–5 por noite)
1. **Grupos** (isolados, cada um com uma tarefa imposta): G1 "cenário em que ESPERAR/ESCOLHER LUGAR vale mais que rodar"; G2 "política explícita
   (Python vetorizado, `politica(obs) -> esc`) que sobrevive 10 dias no cenário base" — a prova por construção; G3 "cenário MÍNIMO que
   separa completo de linear por ≥ 10 pp". Cada agente recebe o contexto, a API e devolve `cenario.json` / `politica.py` + predição.
2. **Juiz**: fila `nmd`, um item por vez (~10 min por cenário de 4 braços; ~1 min por política). Régua pareada; controle linear sempre.
3. **Consolidação** (Opus): o que matou cada tentativa, que truque de um grupo serve para outro, 3 insights, realocação.
4. **Diário** por grupo em `docs/agentes/<rodada>/<grupo>.md`; ledger PREDICOES recebe uma linha por item julgado.

## Guardas
- **Banda do controle (regra desde a rodada 1):** um cenário só é válido se o linear (controle) ficar com mortos entre **0.40 e 0.80**. Abaixo
  disso o mundo é fácil demais; acima, a régua crava no teto e não separa nada (na rodada 1, 'ímã no centro' deu 1.00 em todos e a
  cidade com 12 passageiros deu 0.91–0.95 em todos). Tabela de calibração medida: passageiro perto (npx 12) → linear 0.83 / 18 entregas;
  cidade npx 12 → 0.93 / 11; cidade npx 5 + respawn 80 + periferia .05 → 1.00 / 3. Calibração limpa (só npx, 00:55): 24 → 0.82 / 16.5 ent; 36 → 0.81 / 19.3; 48 → 0.78 / 20.9. **Densidade não é a alavanca**: com 48 a cidade ≈ mundo
  antigo; o que mata é o corpo. Ponto de trabalho: npx 48, respawn 20; um parâmetro por vez.
- Agente não avalia o próprio resultado; só o simulador. Cenário "fácil demais" é pego pelo controle linear (se o linear já
  resolve, o cenário não separa nada). Política que lê estado proibido (posição do passageiro além do sentido) é recusada pela API.
- Sem GPU fora da fila. Sem Fable. Contar agentes antes de disparar.

## Ordem de implementação
1. `gerar_mapa(perfis=...)` + `--cenario` no e43 (identidade: cenário = defaults → bit-igual). **(em andamento)**
2. `scripts/agentes/rodada.py`: monta prompts, chama `claude -p --model sonnet`, coleta JSON/py, enfileira, espera, chama Opus.
3. Primeiro degrau (pred 98): "existe política explícita com mortos ≤ 0.50 em 10 dias no cenário base?" Se ✗ com mecanismo, o
   mundo é insolúvel e o farol vira prioridade; se ✓, a política vira semente da evolução (o Euler do nosso N–S).

## cenarios/base.json (mundo de hoje; tudo que voce nao mudar fica assim)
{
 "nome": "base",
 "predicao": "referencia: mundo de hoje (q13b); nenhuma aposta",
 "mundo": {
  "L": 200,
  "dias": 10,
  "regua": "riqueza",
  "K": 6,
  "ruas": {
   "dentro": 1,
   "fora": 3
  },
  "precos": {
   "amp": 0.5,
   "periodo": 3
  }
 },
 "distritos": {
  "centro": {
   "pmul": 2.0,
   "aliq": 0.35,
   "alug": 2.5,
   "dem": 2.0,
   "dens": [
    1.0,
    1.5,
    1.0,
    0.5,
    1.0
   ]
  },
  "industrial": {
   "pmul": 0.6,
   "aliq": 0.1,
   "alug": 0.8,
   "dem": 0.7,
   "dens": [
    2.5,
    0.0,
    1.0,
    0.0,
    2.0
   ]
  },
  "residencial": {
   "pmul": 1.0,
   "aliq": 0.15,
   "alug": 1.0,
   "dem": 1.0,
   "dens": [
    0.0,
    2.0,
    1.5,
    2.0,
    0.0
   ]
  },
  "periferia": {
   "pmul": 0.5,
   "aliq": 0.0,
   "alug": 0.8,
   "dem": 0.3,
   "dens": [
    0.5,
    0.5,
    0.5,
    0.5,
    0.0
   ]
  }
 },
 "passageiros": {
  "npx": 12,
  "respawn": 20,
  "pax_cidade": false,
  "ponto": 0,
  "tarifa_base": 3,
  "tarifa_km": 0.25
 },
 "corpo": {
  "dinh0": 10,
  "fome_passo": 0.32,
  "kcal_pane": 8,
  "guincho": 0,
  "fuel_pos_pane": 15
 },
 "bracos": [
  "linear"
 ],
 "protocolo": {
  "P": 1024,
  "G": 120,
  "paciencia": 40,
  "R": 4,
  "seeds": [
   0,
   1,
   2,
   3,
   4
  ]
 }
}
## Constantes do corpo (CfgCampo): fuel_passo .15/tick andando (tanque 100, posto vende a preco_L .3/L x pmul do distrito), agua_passo .08, fome_passo .32 (REFEICAO 90 por 2 x pmul),
fad_passo .15, calor sobe .15 andando e desce .6 parado (CALOR_MAX 92 = pane de calor), pane de gasolina = KCAL_PANE 8 de reserva + reboque ate o posto com 15 L,
tarifa 3 + .25 por unidade x pmul do distrito de origem, aluguel 4 x alug do distrito-casa por dia, LIMITE_DIVIDA 60, HOTEL 8, oficina 10 (REPARO 25 de vida), dinh0 10.
## Bracos disponiveis: ['linear', 'COMPLETO (talamo+cortex+hipocampo+reflexo+livre)', 'bilinear risco+demanda+espera (esc 1)', 'bilinear risco (esc 3)', 'bilinear (corpo x opcao)', 'reflexo', 'minimo 3 (d_alvo, d_posto, e_fuel)']
## CALIBRACAO MEDIDA (rodada 1) — leia antes de escolher numeros
linear e' o controle e TEM de ficar com mortos entre 0.40 e 0.80, senao a regua crava e o cenario e' recusado. Medidas: passageiro perto do taxi (pax_cidade false, npx 12) -> linear 0.83, 18 entregas, renda 165;
cidade (pax_cidade true, npx 12, respawn 20) -> linear 0.93, 11 entregas, renda ~110, COMPLETO 0.91 (piso: todos morrem igual); cidade + npx 5 + respawn 80 + periferia dem .05 -> 1.00 e 3 entregas (letal).
CALIBRACAO LIMPA (so npx varia, cidade): npx 24 -> linear 0.82 / 16.5 entregas; 36 -> 0.81 / 19.3; 48 -> 0.78 / 20.9. DENSIDADE NAO E' A ALAVANCA: com 48 a cidade vira o mundo antigo. O que mata e' o corpo (pane/fome/divida), nao a falta de passageiro. Ponto de trabalho para cenarios na cidade: npx 48, respawn 20; mude UM parametro por vez.
O CAMPEAO EVOLUIDO (medido pelo juiz): 17.7 entregas, 6 refeicoes, 4.2 abastecidas, 6.8 PANES por vida, dinheiro final 27, morre 0.85. Ele ACEITA a pane (guincho leva ao posto com 15 L e cobra 8 kcal de reserva) em vez de desviar por precaucao; come toda vez que abastece. A politica r3_1 (contrato certo) andou 95% do tempo, entregou 6, comeu 3x, 1 pane, e morreu 1.00 de fome/sede/divida: desviar demais e trabalhar de menos mata.
Politicas explicitas da rodada 1 (2 agentes) morreram 1.00 de FOME com 2-4 entregas: estacionaram e nunca compraram comida (refeicoes 0). O oraculo a mao tambem morre 1.00. O campeao evoluido, medido pelo mesmo juiz: 0.85, 17.7 entregas, 6.8 panes.

# SUA TAREFA (grupo 'construcao', agente 2, rodada 8)
PONTO DE PARTIDA (nao reinvente): a politica abaixo (rodada 7) e' a melhor ate agora: mortos 0.73 (campeao evoluido 0.85), 7.3 refeicoes, 16.5 corridas, renda 150, morre dia 5.7 (fome 52%, dano 47%), dinheiro final 7. DEFEITO MEDIDO NO TRACO: 23% das escolhas sao 'ficar' (indice 8) — tempo parado que seria corrida (a r6, com 4% de ficar, rendia 168). Fome com 7 refeicoes e caixa 7 = falta RENDA. Agente 1: elimine todo caminho que devolve 8: quando nao ha compra a fazer, SEMPRE argmin(F[:,:,0]) (ir ao passageiro/destino); revise cada torch.where para garantir que o default e' mover; nada mais muda. Agente 2: idem + reparo na oficina so se dinheiro > 25 (guardar caixa para comida) e comida no posto tambem quando e_fome > .10. FORMATO OBRIGATORIO: uma linha `PREDICAO: ...` e depois UM bloco ```python``` com o arquivo completo (a irma da r7 foi recusada por nao seguir o formato). Use device=DEV em todo tensor novo. Predicao com numeros: mortos, corridas, renda, refeicoes, fracao de ficar no traco (meta < 5%). Meta: mortos <= 0.68.

```python
import torch


def fabrica():
    class PoliticaConstrucaoR7A1:
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

            # trabalho continuo: sempre ao alvo. NUNCA argmin de d_posto.
            mover = torch.argmin(F[:, :, 0], dim=1)
            ir_oficina = torch.argmin(F[:, :, 4], dim=1)
            ir_comida_mov = torch.argmin(F[:, :, 2], dim=1)

            score = torch.full((B, S), -1e9, device=device, dtype=dtype)

            quer_agua = e_agua < 0.8
            quer_comida = e_fome > 0.15
            quer_fuel = e_fuel < 0.95

            # placar de compra no posto (agua > comida > gasolina) via argmax
            score[:, 5] = torch.where(no_posto & quer_agua, 30.0 + (0.8 - e_agua), score[:, 5])
            score[:, 7] = torch.where(no_posto & quer_comida, 20.0 + (e_fome - 0.15), score[:, 7])

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
            segunda = no_posto & self.comeu_ultimo_tick & (e_fome > 0.15) & (dinh > 30) & disp[:, 7]

            # fora do posto: ir a comida de longe (deslocamento planejado, nao emergencia)
            buscar_comida = (~no_posto) & (e_fome > 0.55) & (F[:, G - 1, 2] < 20)

            # emergencia fora do posto: so' se ja esta ao lado
            fora_agua = (~no_posto) & (e_agua < 0.15) & (F[:, G - 1, 3] < 8) & disp[:, 5]
            fora_comida = (~no_posto) & (e_fome > 0.85) & (F[:, G - 1, 2] < 8) & disp[:, 7]

            # REPARO: (1) vida baixa com histerese .5/.8, (2) calor alto sem passageiro
            ini_vida = (e_vida < 0.5) & (dinh > 20)
            self.reparando_vida = (self.reparando_vida | ini_vida) & (e_vida < 0.8) & (dinh > 10)
            quer_calor = (e_calor > 0.75) & (~tem_pax)
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

    return PoliticaConstrucaoR7A1
```
Seja diferente dos outros agentes do grupo: agente 2 deve escolher uma abordagem distinta (variacao 2).
## Contrato politica.py (agente escreve; o juiz executa em GPU com 3 mundos de teste x 128 copias x 5 sementes)
Defina `fabrica()` que devolve uma CLASSE (nao instancia) com EXATAMENTE estes metodos e assinaturas Python (self e' o objeto, como sempre): `def reset(self, m, W)`, `def extra(self, m, W, F)` -> devolve torch.zeros(m.B, G) e guarda self.F = F, `def decidir(self, tudo, m)` -> LongTensor (m.B,), `def atualizar(self, m)`. NAO acrescente parametros extras (na rodada 3 os agentes escreveram `def reset(self, s, m, W)` e crasharam).
- F (B, G=9, NF) = observacao: para cada opcao de movimento g (8 direcoes + ficar = g 8), colunas 0..9 = NOMES_OP = ['d_alvo','d_posto','d_comida','d_agua','d_oficina','d_descanso','custo_frente','preco_frente','aliq_frente','casa_frente']
  (distancias em unidades andadas APOS a opcao; d_alvo = passageiro mais perto ou destino se carrega) e colunas 10.. = NOMES_CORPO (iguais nas 9 opcoes):
  ['e_fuel','e_agua','e_fome','e_fadiga','e_calor','e_vida','e_dinheiro','e_reserva','e_tem_pax','h_sin','h_cos','e_noite','custo_aqui','bias','e_consumo','e_autonomia','e_risco','e_demanda','e_espera'] (escalas 0..1; dinheiro /150; autonomia = (tanque/consumo - d_posto)/100).
- tudo (B, G+S): colunas 0..G-1 = notas de movimento (ignore), G+k = servico k DISPONIVEL e pago (> -1e8). ORDEM EXATA (S=10), indice k -> acao: ['0: posto 25', '1: posto 50', '2: posto 75', '3: posto 100', '4: posto 150', '5: agua 50', '6: agua 100', '7: comida', '8: descanso', '9: oficina']. Ex.: comprar 'comida' = devolver G + 7; 'posto 100' = G + 3. Use `tudo[:, G+k] > -1e8` para saber se a acao k pode ser comprada AQUI e AGORA (esta no raio 6 do servico e tem dinheiro). A LOJA do posto vende comida e agua (loja_no_posto): no posto, comida/agua tambem ficam disponiveis. Distancias F[:, :, 1..5] sao ate posto/comida/agua/oficina/descanso; servico 'disponivel' exige d < 6.
- Corpo em m (tensores (B,)): m.fuel, m.agua, m.fome, m.fad, m.calor, m.vida, m.dinh, m.res, m.pd_ (>=0 carregando), m.hora() (0..24), m.noite_(), m.B.
- Devolva por ser: um indice de movimento 0..8 (use argmin de uma coluna de F para 'ir ao alvo'), ou G + indice do servico para comprar.
- Proibido: importar alem de torch/math, ler m.px/m.pxd/m.serv/m.g/m.dest, chamar os/sys/open/exec. Tudo vetorizado em torch (sem loop por ser).
- RODADAS 1-2 MORRERAM POR CULPA DO CONTRATO: a ordem de ACOES estava errada no prompt (comida era indexada como posto 100 L). Agora a ordem acima e' a do codigo. Nao invente indices: use a tabela.
- Exemplo minimo (o oraculo que morreu 1.00): ir ao passageiro; se e_fuel < .4 ir ao posto e encher quando disponivel; se fome > .8 comer. Faca melhor: margem de alcance (autonomia), comer quando ja esta no posto, evitar centro caro sem dinheiro, descansar de madrugada.
Responda com UM bloco ```python``` com o politica.py completo, e antes dele UMA linha `PREDICAO: ...` com mortos, entregas e o que mata.