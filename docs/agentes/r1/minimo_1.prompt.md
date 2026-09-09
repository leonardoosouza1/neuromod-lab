# CONTEXTO (neuromod-lab, taxi na GPU)
Seres = taxis com corpo (gasolina, agua, fome, fadiga, calor, vida, dinheiro, reserva) que precisam sobreviver 10 dias (2400 ticks; 1 tick = 6 min)
numa cidade continua 200x200 com distritos (perfis centro/industrial/residencial/periferia), ruas (custo 1 na rua, 3 fora), servicos (posto, comida,
agua, descanso, oficina) e passageiros. Cerebros evoluidos por selecao. Achados: (84) no Linear os sentidos do corpo sao invisiveis na direcao;
(E64-E67) o campeao linear e' um pico local da regua 'riqueza 10 dias' (busca x4, gradiente e ruido nao mudam; morre 0.82); (E68, pred 95) o campeao
anda 82% do tempo, 67% com passageiro, espera livre 3%: no mundo antigo o passageiro nascia perto do taxi, entao lugar nao tinha preco;
(E70, rodando) passageiro agora nasce NA CIDADE (pax_cidade). Regra da casa: negativo com mecanismo e' resultado; predicao ANTES de rodar; sem portao desenhado a mao no cerebro.
## Ultimas predicoes (ledger)
| 90 | E63 escada de NÉVOA (Claude Science, doc 49 §7, mundo ajustado: E56c, 10 d, riqueza, R=8, 5 sem., semeados do linear-com-luz): (a) névoa piora o linear monotonicamente inf → 40 → 25 → 15; (b) em névoa ≤ 25, só-camadas e/ou COMPLETO batem o linear por ≥ 10 pp PAREADO por semente com ent ≥ 15; (c) em névoa 25 com custo suave λ .3, dof sobrevivente ≥ 30 concentrado em hipocampo/córtex; (d) ablação do hipocampo no campeão de névoa 25 piora ≥ 10 pp. Cláusula: se todos ≥ 0.95 em névoa 15, refazer com 40/60. Aposta do CS: (a)(b)(c)(d) ✓; minha aposta: (a) ✓, (b) ✓ em névoa 25, (c) ✗ (custo ainda derruba), (d) ✓ | (a) ✗ névoa não piora (linear 0.80/0.77/0.81 em ∞/25/15); (b) ✗ em todos os níveis (só-camadas 0.81/0.78/0.81; completo 0.83/0.82/0.82; pareado ns, MDE 9 pp); (c) ✗ custo suave λ .3 em névoa 25: completo 0.85, só-camadas 0.85 (pior que sem custo); (d) sem objeto — escada inteira ✗ |
| 91 | Busca ×8 (q8: P=2048, 300 ger., paciência 60, 5 sementes, R=4, mundo E56c riqueza 10 d, semeados do linear-com-luz): se o gargalo era ORÇAMENTO, o bilinear-risco esc 3 fica ≥ 10 pp abaixo do linear (pareado) com ent ≥ 15 e M[risco,d_posto] < 0 em ≥ 3/5; aposta: ✗ (empate) — o gargalo é o sinal de aprendizado, não a busca | ✗ empate: linear 0.82 / 7.3 panes, bilinear-risco 0.85 / 6.3; ambos param na ger. 60 sem melhora sobre o semeado (ótimo local da régua); não é orçamento — é o sinal de aprendizado |
| 92 | E65 SINAL DE APRENDIZADO no táxi (q9: ES antitético com utilidade por posto, σ .1 e .3, lr .3, MESMO orçamento e sementes do q8: P=2048, 300 ger., paciência 60, 5 sem., R=4, semeados do linear-com-luz, régua riqueza 10 d, E56c): se a hipótese do fechamento ('falta sinal, não busca') está certa, o ES sobe ≥ 10 pp pareado sobre o GA (mortos 0.82 → ≤ 0.72) em ≥ 1 σ, com ent ≥ 15; aposta: ✗ (empate ±5 pp) — o platô 'não dirigir' é do PANORAMA de fitness (degrau), não do otimizador; se ✓, o gargalo era o otimizador e o Minecraft NÃO é necessário para prová-lo | ✗ empate: ES σ .1 mortos 0.77 (−5.3 pp, IC −14.5/+3.8, p .18), ES σ .3 0.80 (−2 pp); nenhum otimizador sobe a fitness de treino (GA −0.18→0.00, ES −0.28→+0.14) |
| 93 | E66 SINAL/RUÍDO da nota (diag_snr: 2048 mutantes σ .3 do campeão linear s0, mesma população em 3 sorteios de mundo, R=4, mundo/régua do q8): se a seleção é loteria, corr(nota_A, nota_B) entre indivíduos < 0.3 e a elite de 15 % de um mundo se mantém elite no outro em < 30 % (acaso 15 %); e a DP da nota do MESMO clone entre mundos (σ 0) é ≥ a DP entre mutantes num mundo; aposta: ✓ — é por isso que GA e ES travam no mesmo lugar (mecanismo do platô: nota cega, não panorama plano) | ✗ a nota NÃO é cega na escala do GA: σ .3 corr 0.81, elite mantida 43–46 % (acaso 15); σ .1 corr 0.45 (meio-cega na escala fina); clones: DP 0.49 = ruído puro; fitness média cai com σ (−2.14/−2.47/−3.23) = campeão é PICO local |
| 94 | E67 última brecha do fechamento (q11: ES σ .1 com R=16 — nota média em 16 mundos, ruído /2 — mesmo P=2048, sementes, mundos e paciência do q9b2): se o platô era só ruído na escala fina, o ES sobe ≥ 10 pp pareado sobre o GA (mortos ≤ 0.72); aposta: ✗ (fica em 0.75–0.80) — a curva fitness×σ diz que o campeão é pico local desta régua, não vítima de ruído | ✗ ES σ .1 R=16: mortos 0.78 [0.737, 0.826, 0.82, 0.737, 0.789] (−4 pp, dentro da faixa apostada 0.75–0.80); treino sobe −1.21→−0.93 até a ger 30 e para (ger 61); ruído /2 não abre subida nova — pico local confirmado por 3 lados (busca, otimizador, ruído) |
| 95 | E68 PONTO DE TÁXI (Leonardo 09-08: 'parar pode ser esperar passageiro'): táxi parado+livre recebe passageiro no lugar com espera ponto/demanda (ponto=30: centro ~15 ticks, periferia ~100) + sentidos e_demanda/e_espera; mundo E56c, riqueza 10 d, 5 sem., R=4, P=1024, 120 ger. paciência 40, semeados do linear q8 (alinhado): (a) o bilinear risco+demanda+espera bate o linear ≥ 10 pp em mortos OU ≥ +20 % de renda pareada (o linear não vê o lugar ao decidir 'ficar', achado 84); (b) o linear no mundo com ponto entrega mais que no mundo sem (ent ≥ 22 vs 18) porque parar passou a render; aposta: ✓ em (b) e ✓ em (a) — é o primeiro mundo onde a peça tem o que pagar | ✗ (a) bilinear risco+demanda+espera 0.80 vs linear 0.81 (−1 pp; entrega 15.1 vs 18.3, renda −18 %); COMPLETO 0.73 (−7 pp, p .15). ✗ (b) linear entrega 18.3 com ponto vs 18.1 sem. MECANISMO (diag_ponto): o linear NUNCA espera livre (3 % do tempo; 82 % andando, 67 % com passageiro; 2 % dos embarques via ponto) porque o mundo dá passageiro de graça rodando (12 privados a 8–45 u, renascendo perto em qualquer distrito) — sem escassez, esperar e escolher lugar não valem nada. Só o COMPLETO usou o ponto (11 % esperando, 20 % via ponto) |
| 96 | E69 ESCASSEZ de passageiro (npx 3, respawn 100: periferia ~333 ticks por slot, centro ~50) + ponto 30 + sentidos; mesmo protocolo do q13 (P1024, 120 ger, pac 40, 5 sem., riqueza 10 d, semeados do linear q8): (a) o linear cego ao lugar cai: ent ≤ 12 e mortos ≥ 0.85; (b) COMPLETO ou bilinear risco+demanda+espera batem o linear ≥ 10 pp em mortos OU ≥ +30 % renda pareada, com espera livre ≥ 10 % do tempo concentrada em demanda alta; aposta: ✓ (a) e ✓ (b) pelo COMPLETO (único que já usa o ponto) — é a primeira vez que ONDE trabalhar tem preço | CANCELADA (parada aos 12 min, sem resultado): Leonardo — 'eles deveriam buscar o passageiro, não o passageiro aparecer do nada'; escassez do pool privado ainda faz o passageiro nascer perto do táxi |
| 97 | E70 PASSAGEIRO NA CIDADE (pax_cidade: nasce onde há demanda, em volta do centro do distrito; táxi vai buscar; reposição ~ demanda do lugar; ponto OFF; 12 passageiros na cidade toda), mesmo protocolo do q13 (P1024, 120 ger, pac 40, 5 sem., riqueza 10 d, semeados do linear q8), controle pareado = linear do q13b (passageiro perto): (a) o linear entrega menos (ent ≤ 14 vs 18) e morre mais (≥ +5 pp) porque agora tem de viajar; (b) COMPLETO ou bilinear risco+demanda+espera batem o linear ≥ 10 pp em mortos OU ≥ +30 % renda pareada — pela primeira vez ONDE estar tem preço e o linear não lê lugar na direção; aposta: ✓ (a), ✓ (b) pelo COMPLETO (3 apostas ✓ perdidas hoje: o mundo é quem decide) | pendente |
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

# SUA TAREFA (grupo 'minimo', agente 1, rodada 1)
Desenhe o cenario MINIMO (menor desvio do base.json) que separa COMPLETO de linear por >= 10 pp de mortos. Mude o menor numero de parametros possivel e diga por que cada um. Bracos: linear, COMPLETO. Predicao obrigatoria com numeros e mecanismo.
Seja diferente dos outros agentes do grupo: agente 1 deve escolher uma abordagem distinta (variacao 1).
Responda com UM bloco ```json``` contendo o cenario.json completo (campo "predicao" obrigatorio, com numeros e mecanismo) e nada mais.