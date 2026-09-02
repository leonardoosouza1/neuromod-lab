# 27 — Corpo = carro: dano real, morte, gordura fácil, sono que come (E13, 2026-09-02)

**Leonardo:** *"Acho válido começar a realmente evoluir mais: colocar dano no
carro, dano real, fura o pneu demora mais, motor aquecido o carro desliga, o
reboque custa mais, pra que os seres realmente tentem deixar o carro o mais
vivo possível porque é o corpo deles. E mais gordura, ela entra mais fácil,
porque dormir e melhorar o cérebro custa caloria — deixar pro outro dia como
gordura às vezes não compensa."*

## 1. O que muda (tudo atrás de `cfg.corpo`, zero sem a flag — portão bit-exato)

| peça | antes (avaria = parada) | agora (avaria = FERIDA) |
|---|---|---|
| vida | não existia | 0–100, feature `e_dano = 1 − vida/100` |
| pane seca | 18 passos, reboque 12 | 18 passos, reboque **20**, **−6 vida** |
| furo | 15 passos, pneu→60 | **30 passos**, pneu→**40**, **−5 vida** |
| óleo | 22 passos | 22 passos, **−12 vida** |
| motor >92 °C | 14 passos, temp→40 | **desliga 20 passos**, temp fica 92 e esfria sozinho (1.6/passo), **−10 vida** |
| rodar machucado | nada | pneu<30 ou temp>80 ou óleo<20 andando: **−0.15/passo** |
| ferido | nada | tempo de viagem e consumo × (1 + 0.6·dano) |
| oficina | pneu/óleo/temp | + **vida +30** (mesmo preço 10) |
| morte | não existia | vida ≤ 0: para de entregar, para de agir |
| gordura fácil | só sobra da meia-noite | `reserva_posto`: posto também põe 20 na reserva |
| sono come | descanso grátis | `sono_come`: cada descanso custa 5 de fuel (tanque, depois gordura com perda) |

Mundo-base: o mundo honesto do E12-v8 (fuel×0.5, reboque, noite 22–6h).

## 2. Por quê assim

- **Morte é a seleção de verdade.** Até aqui o ser "sobrevivia" por definição:
  pane, furo e fervura eram paradas, não feridas. Agora o corpo acumula e o
  ser que não cuida DEIXA de existir — fitness congela. É a primeira vez que
  "deixar o carro vivo" vale mais que "entregar mais".
- **O motor quente desliga**: não é multa, é física — o carro para até esfriar.
- **Gordura entra fácil pela lei do E12** (doc 26 §7.2): com entrada só da
  meia-noite, I=10 ≪ f·S=45 e a reserva não paga; com o posto enchendo a
  reserva, I≈54 ≥ f·S e o regime vira "teto = buraco".
- **Sono que come** fecha o trade-off que o Leonardo descreveu: a caloria da
  noite vai pra recuperar/aprender OU pra gordura. Quem dorme muito engorda
  menos.

## 3. Teto medido antes (regra 1)

Perito (mesmo genoma à mão) no mundo corpo: **86% morrem em 5 dias**, vida
média no fim 9.7, dano 137 = fervura 81 + panes 44 + furos 7 + rodar 6. O
mundo é letal pra quem não muda de comportamento. Predições 14–18 em
PREDICOES.md §E13.

## 4. Resultados (2026-09-02)

### 4.1 Rápido (G=20, treino 2.5 dias) — a evolução nunca viu a morte

| braço | fit | mortos | t_vida | vida_fim | dano | panes | fervura | oficina |
|---|---|---|---|---|---|---|---|---|
| noite s+r (sem corpo) | 3.56 | 0 | – | 100 | 0 | 15.7 | 2.4 | 0 |
| corpo | 2.96 | **0.52** | 0.81 | 34 | 94 | 8.3 | 3.0 | 5.8 |
| corpo reserva | 2.23 | 0.55 | 0.80 | 29 | 104 | 9.1 | 3.5 | 5.6 |
| corpo res-posto | 2.99 | 0.44 | 0.84 | 39 | 97 | 6.6 | 4.2 | 6.2 |
| corpo res-posto sono | 2.01 | 0.37 | 0.85 | 47 | 77 | 6.5 | 2.9 | 4.7 |

Perito morre 86%; evoluído 52%. Mas as mortes caem no dia 4 (t_vida 0.81)
e o treino rápido vive 2.5 dias: **a seleção nunca viu ninguém morrer**. O
rápido é inválido pra morte por construção — regra nova (§5).

### 4.2 Longo (G=60, treino 5 dias, morte dentro do treino)

| braço | fit | por semente | mortos | vida_fim | dano | panes | fervura | oficina | res~ |
|---|---|---|---|---|---|---|---|---|---|
| noite s+r (sem corpo) | 6.45 | 7.2 / 6.1 / 6.0 | 0 | 100 | 0 | 15.5 | 1.9 | 0 | – |
| corpo | **7.20** | 6.9 / 7.3 / 7.4 | 0.39 | 47 | 83 | **8.0** | 2.4 | **7.5** | – |
| corpo reserva (meia-noite, peso) | 4.80 | 6.7 / 3.2 / 4.5 | 0.35 | 49 | 82 | 7.7 | 2.4 | 5.5 | 17.5 |
| corpo res-posto (peso) | 4.74 | 4.8 / 4.0 / 5.5 | 0.44 | 42 | 102 | 8.3 | **4.0** | 7.5 | 23.2 |
| corpo res-posto sono (peso) | 4.42 | 3.4 / 4.8 / 5.1 | 0.41 | 45 | 93 | 8.2 | 3.3 | 5.8 | 18.3 |

De onde vem o dano (evoluído, corpo): panes 48 (58%), fervura 24 (29%),
furos 6, óleo 3, rodar machucado 2. **A pane é a assassina** — não a fervura
que matava o perito (81). A evolução aprendeu a não ferver (8.1 → 2.4) e a
reparar (oficina 0 → 7.5 por vida, +225 de vida comprada); não aprendeu a
não secar.

### 4.3 Três achados

**1. A dor muda o comportamento — não o fitness (corrigido em §6.6).**
Com 3 sementes corpo > sem corpo (+0.75); com 5 sementes **−0.45** (3/5
positivas, média negativa): o ganho era ruído. O que replica 5/5: no mundo
sem corpo a evolução aceita 13–15 panes por vida e nunca vai à oficina; com
corpo, onde a pane FERE, faz 8 panes e vai à oficina 7 vezes. O ser cuida do
carro porque dói — mas os 38% que morrem comem exatamente o que os cuidados
rendem. Sinal denso muda a política; não sai de graça.

**2. Morte seleciona, mas só se está no treino.** 86% (perito) → 52% (G=20,
2.5 dias, sem morte no treino) → 39% (G=60, 5 dias, com morte). O que resta
morre de pane: vive no limite (vida_fim 47, N15 de novo: repara só o
suficiente).

**3. Gordura no mundo-corpo: pesa, esquenta, e é bimodal.** Perito
instrumentado: 0 panes com `res > 0` (sem bug). A reserva passa 30% do tempo
CHEIA (cap 60, entrada do posto desperdiçada) e 46–59% VAZIA: uma noite drena
os 60 em 2–3 mobilizações e o resto da noite vira pane; o posto só é visitado
4–7×/vida (pobre 0.35). E os braços com reserva carregam o peso (.10/.30):
no mundo-corpo o peso FERVE o motor (2.4 → 4.0 fervuras = +16 de dano) —
"gordo esquenta" apareceu sozinho, como o Leonardo descreveu. Resultado: as
reservas perdem 2.4–2.8 pra `corpo` sem reserva. Decomposição peso × reserva
× cap em §4.4 (E13b).

**Sono que come**: gordura −21%, fit −0.32 vs res-posto (predição 17 ✓);
o ser dormiu menos (sono 15 = 3 descansos/vida contra 7.6 no rápido) — trocou
sono por gordura, não gordura por sono.

### 4.4 E13b — decomposição peso × reserva × cap (longo, G=60)

| braço | fit | por semente | vs corpo (7.20) | mortos | vida_fim | dano | panes | fervura | res~ |
|---|---|---|---|---|---|---|---|---|---|
| corpo peso (só tanque pesa) | 5.48 | 4.8 / 4.6 / 7.1 | **−1.72** | 0.49 | 38 | 96 | 10.0 | 2.6 | – |
| corpo reserva s/peso (meia-noite) | 7.46 | 6.4 / 7.8 / 8.2 | +0.26 | 0.44 | 46 | 87 | 8.2 | 2.4 | 20.5 |
| corpo res-posto s/peso | 7.82 | 7.6 / 7.9 / 8.0 | +0.62 | 0.36 | 53 | 84 | 7.4 | 3.0 | 25.5 |
| **corpo res-posto s/peso, cap 120** | **9.57** | 10.4 / 8.3 / 10.0 | **+2.37 (3/3)** | **0.31** | 59 | **74** | **5.9** | 2.2 | 54.8 |
| corpo res-posto peso, cap 120 | 5.68 | 4.0 / 6.2 / 6.8 | −1.52 | 0.43 | 45 | 96 | 7.7 | 3.5 | 38.1 |

- **Cap mordia.** Com 120 de gordura a noite cabe: res~ 55, 2 mobilizações
  por vida, panes 8.0 → 5.9, dano −9, mortos −8 pp, e fitness +2.4 (3/3).
  Predição 19 ✓ na direção; ✗ nos limiares (panes 5.9 > 4, mortos 0.31 > 0.25).
- **Meia-noite sozinha ≈ 0** (+0.26, lei: I=10 ≪ f·S). Posto enchendo a
  reserva +0.62; posto + cap 120 +2.37. A cadeia inteira da lei do E12 vale
  aqui: entrada → estoque que cabe → cobre o buraco.
- **O peso é o custo dominante do mundo-corpo.** Só o tanque pesando
  (.10): −1.72 e mortos 0.39 → 0.49. Gordura pesando (.30 do cap): a mesma
  configuração vencedora cai de 9.57 pra 5.68 (−3.9). Mecanismo: pesado
  anda mais devagar e ESQUENTA (fervura 2.2 → 3.5, +13 de dano), come mais,
  cansa mais — as quatro coisas que o Leonardo pediu, e todas cobram no
  mundo onde a margem é fina (pobre 0.3, tanque de 100 com noite fechada).
- Veredito da gordura no corpo: **vale, e muito, quando (a) entra fácil,
  (b) cabe, e (c) não pesa como calibrado.** Os números do peso (.10/.30)
  estão 3–5× fortes pra esta economia; a física está certa.

### 4.5 Quem morre: a armadilha de pobreza (E13c)

Campeão R120 (3 sementes × 128 réplicas), rodado com contadores:

| | vivos (69%) | mortos (31%) |
|---|---|---|
| panes por vida | **1.3** | **16** |
| dinheiro no fim | – | **0.6–1.0** |
| oficina | 6–12 | 4–7 |
| vida no fim | 83–90 | 0 |
| fit | 12–15 | – |
| causa (dano nos últimos ~50 passos) | – | pane 16, fervura 0.4, furo 0.4, óleo 0.6 |

Morte no dia 2–3, por volta do meio-dia. A perda oculta da conversão NÃO
importa (mortos 0.26–0.37 nos três terços). A cidade importa (1001: 17–23%;
1002: 30–47%). População BIMODAL com a mesma política: quem não pane nos
primeiros dias vive bem; quem pane uma vez paga o reboque de 20, fica sem os
2 do posto e os 10 da oficina, pane de novo, e morre quebrado. Gatilho
aleatório, espiral determinística.

Teste (mesma config vencedora, só a multa muda):

| reboque | fit | mortos | pobre | vida_fim | panes | dano |
|---|---|---|---|---|---|---|
| 20 | 9.57 | 0.31 | 0.28 | 59 | 5.9 | 74 |
| 8 | 9.35 | 0.27 | 0.22 | 61 | 5.7 | 80 |
| **0 (só o corpo paga)** | **10.67** | **0.17** | **0.07** | **72** | 6.5 | 84 |

Predição 20 ✓ na direção (mortos −45%, fit +1.1, pobreza 0.28 → 0.07), ✗
no limiar (0.17 > 0.12). Metade das mortes era dinheiro; a outra metade é
rota/noite — o ser roda de noite sem posto e seca onde está.

### 4.6 E13d — o peso, sem a armadilha (longo, config vencedora: res-posto, cap 120, reboque 0)

| peso (WF/WR) | fit | por semente | vs sem peso (10.67) | mortos | fervura | res~ | oficina |
|---|---|---|---|---|---|---|---|
| sem peso | 10.67 | 10.4 / 11.1 / 10.5 | — | 0.17 | 3.2 | 52.0 | 10.2 |
| .03/.10 | 9.78 | 10.4 / 9.8 / 9.1 | −0.89 | 0.18 | 3.4 | 53.4 | 10.1 |
| .05/.15 | 9.46 | 8.1 / 10.5 / 9.8 | −1.21 | 0.17 | 4.1 | 51.5 | 12.0 |
| **.10/.30 (Leonardo)** | **9.23** | 10.5 / 8.8 / 8.4 | **−1.44** | **0.16** | 3.8 | 49.7 | 8.1 |

- Predição 21 ✓ em mortos e fervura, ✗ por 0.1 no fit de .03/.10 e ✗ em
  "emagrece" (res~ 50–53 em todas: com cap 120 o peso não faz o ser encolher
  a gordura — a homeostase do E12 só apareceu com cap 60).
- **O achado é a interação.** Com reboque 20, o peso .10/.30 custava −3.9 e
  +12 pp de mortos; com reboque 0 custa −1.4 e 0 pp. O peso não matava — a
  armadilha matava e o peso era o empurrão (pesado → 1ª pane → quebrado). Os
  números do Leonardo são viáveis e SENTIDOS (fervura +20%, −1.4 de fitness)
  assim que a carteira deixa de pagar a pane duas vezes.
- Trajetória do design, mesma física, só calibração: cap 60 + reboque 20 +
  peso .10/.30 = **4.74, 44% mortos** → cap 120 + reboque 0 + peso .10/.30 =
  **9.23, 16% mortos**. Duas decisões de mundo, ×2 no fitness, ÷3 nas mortes.

### 4.7 E13e — os 17% que restam não são de hora nem de rota

Config vencedora com peso (.10/.30), três cérebros:

| arquitetura | fit | mortos | panes | fervura |
|---|---|---|---|---|
| Reativo | **9.23** | **0.16** | 6.5 | 3.8 |
| ReativoHora (serviço × hora) | 7.75 | 0.27 | 8.0 | 4.4 |
| Corpo (desvia pro serviço da maior necessidade) | 8.44 | 0.17 | 5.7 | 4.5 |

Predição 22 ✗ nas duas. A alavanca de hora piora (12 pesos a mais, G=60 não
acha "posto às 21h" — o mesmo resultado do E12b) e a de rota empata. Os 17%
são o teto da política reativa de 1 salto neste mundo: a cidade 1002 mata 2×
a 1001 com o mesmo genoma. Próxima alavanca é MECANISMO (sono em bloco à
noite com tanque baixo, doc 24; memória de posto), não peso a mais.

## 5. Veredito e regras

**O corpo funciona como o Leonardo pediu:** a dor ensina (corpo > sem corpo,
metade das panes, oficina 0 → 7.5), a morte seleciona (86% → 52% → 39% → 31%
→ 17% conforme o treino vê a morte, a gordura cabe e a multa some), "gordo
esquenta" apareceu sozinho, e o ser vive no limite (repara o suficiente).

**Três decisões de calibração pro Leonardo — REVISADAS com 5 sementes
(E13p, §6.10): a 2ª sobrevive, a 3ª cai.**
1. **Peso .10/.30 é viável — desde que a multa em dinheiro suma** (§4.6):
   com reboque 20 custava −3.9 e +12 pp de mortos; com reboque 0 custa −1.4
   e 0 pp. Manter os números do Leonardo; o peso é sentido (fervura +20%).
2. **Reboque caro em DINHEIRO cria armadilha de pobreza** — a multa cobra na
   mesma moeda que compra o conserto (posto, oficina), então a 1ª pane vira
   espiral. Eco da lei da moeda cruzada (doc EXP10): o corpo já paga a pane
   (−6 vida); a carteira não devia pagar de novo. Reboque 0 = −45% de mortes.
3. ~~Cap da gordura ≥ buraco da noite (120, não 60): +2.4 e −8 pp.~~ **Caiu
   com 5 sementes**: +0.4 (2/5) e mortos +1 pp. A gordura acumula mais (51
   vs 27) e não muda panes nem mortes. Cap é indiferente.

**Regra 11 (00-NEGATIVOS):** morte só seleciona se cabe no treino — o
rápido (2.5 dias) viu 0 mortes e "evoluiu" 52% de mortalidade; o longo (5
dias) viu a morte e caiu pra 39%. Antes de rodar seleção por morte, medir o
dia em que o perito morre e treinar mais longo que isso.

**Regra 12:** penalidade na moeda que compra a recuperação = armadilha. Ao
adicionar multa, perguntar "com que o ser paga o conserto?" — se for a mesma
coisa, a multa mata por espiral, não por seleção.

**Fica pra depois (declarado):** os 17% que ainda morrem — hora e rota
não resolvem (§4.7); candidatos: sono em bloco à noite com tanque baixo
(doc 24), memória de posto. Também: dano permanente por idade, oficina com
preço por HP, greve no mundo-corpo.

## 6. Mundo recomendado (E13f): massa como cálculo base + gordura contínua

**Leonardo:** *"não sei o que é melhor, faça o recomendado; gordura mais ao
longo do tempo, acumulável; peso influenciando; precisa ter um cálculo base
geral e o peso extra afeta."*

### 6.1 Cálculo base: massa

Uma fórmula, tudo deriva dela:

```
massa  = 1000 kg (chassi) + 0.75·fuel + 2.5·res + 80·(carregando passageiro)
peso   = massa / 1000
```

| carga | kg | efeito no peso |
|---|---|---|
| tanque cheio (100) | 75 | +7.5% |
| gordura cheia (120) | 300 | +30% |
| passageiro | 80 | +8% |

O `peso` multiplica tempo de viagem, consumo (fuel/água/calor/pneu), fome e
fadiga, e divide a recuperação do descanso — os mesmos canais de antes, agora
com uma massa física por trás. Gordura pesa 3.3× mais por unidade que
gasolina (o "combustível rápido pesa pouco, a poupança pesa" do doc 26). O
passageiro pesando é novo: carregar custa.

### 6.2 Gordura acumulável ao longo do tempo

A cada passo, 2% da sobra do tanque acima de NIVEL=50 vira gordura (perda de
10%). Sem lote da meia-noite, sem compra no posto: quem anda com o tanque
acima da metade engorda devagar, quem vive no reserva não engorda. Metade
da sobra se converte em ~35 passos (3.5 h); um tanque cheio parado rende
~45 de gordura num dia.

Mundo: corpo + cap 120 + reboque só no corpo (as duas decisões do §5).
Predição 23 em PREDICOES.md.

### 6.3 Resultados (longo, G=60, 3 sementes)

| braço | fit | por semente | mortos | res~ | mob | panes | fervura | dano |
|---|---|---|---|---|---|---|---|---|
| **recomendado** (taxa .02) | **8.16** | 8.7 / 8.6 / 7.2 | **0.21** | 45 | 3.2 | 7.3 | 4.7 | 104 |
| taxa .05 | 7.68 | 7.5 / 7.9 / 7.6 | 0.20 | 50 | 4.2 | 8.2 | 4.3 | 106 |
| sem peso | 10.42 | 11.0 / 9.6 / 10.7 | 0.17 | 51 | 2.9 | 7.3 | 2.7 | 80 |
| sem gordura | 7.34 | 7.8 / 6.3 / 7.9 | 0.27 | – | – | 9.2 | 3.4 | 103 |

- **Gordura contínua vale**: +0.82 e −6 pp de mortos sobre o mesmo mundo sem
  gordura; forma devagar (45/120 em média, 3.2 mobilizações por vida contra
  2 lotes/vida do modelo antigo).
- **Mais rápido não é melhor**: taxa .05 perde 0.5 — converter depressa tira
  fuel do tanque e vira pane (8.2 vs 7.3). A poupança boa é lenta.
- **O peso por massa custa −2.3** (previa −1.0) e o canal é o calor: fervura
  2.7 → 4.7 = +20 de dano. Tanque cheio +7.5%, gordura média +11%, passageiro
  +8% quase sempre — E13g separa os três.
- Comparado ao vencedor anterior (posto enche a reserva, peso .10/.30): 9.23 /
  0.16. O recomendado é 1 ponto pior e 5 pp mais mortal — porque acumula
  devagar (o que o Leonardo pediu) e porque o passageiro agora pesa. Física
  mais honesta, número um pouco menor; ambos declarados.

### 6.4 E13g — de onde vem o custo do peso (longo)

| braço | fit | mortos | res~ | panes | fervura |
|---|---|---|---|---|---|
| recomendado (.02, pax 80 kg, gordura 2.5 kg/u) | 8.16 | 0.21 | 45 | 7.3 | 4.7 |
| taxa .01 | 7.58 | 0.22 | 35 | 8.7 | 3.8 |
| passageiro 0 kg | 8.79 | 0.17 | 42 | 7.7 | 4.0 |
| gordura 1.5 kg/u | 7.77 | 0.20 | 49 | 7.1 | 4.3 |
| sem peso (§6.3) | 10.42 | 0.17 | 51 | 7.3 | 2.7 |

- **Taxa .02 é o vale**: .01 acumula pouco (35) e pane mais; .05 drena o
  tanque e pane mais. A poupança boa é lenta mas não lenta demais — o ótimo
  é a taxa em que a gordura chega ao buraco da noite sem esvaziar o dia.
- **Passageiro pesando** explica ¼ do custo (+0.63 sem ele). Gordura mais
  leve não muda nada (o ser carrega 45 em média = 112 kg → 68 kg, ruído).
- **O canal é o limiar de fervura.** Todo braço com peso ferve 4.0–4.7×/vida
  contra 2.7 sem peso, inclusive com passageiro 0 kg. Um tanque cheio pesa
  só +7.5%, mas o ser evoluído roda com o motor encostado nos 92 °C — um
  empurrão de 7% vira +50% de fervuras (20 passos + 10 de vida cada). O peso
  custa pouco em linha reta e muito no limiar. É a mesma lição do N15 (vive
  no limite) vista pelo lado do calor.

### 6.5 E13h — vida longa e cidades nunca vistas (mesmo campeão)

| avaliação | fit | fit/dia | mortos | panes/dia | fervura/dia | res~ |
|---|---|---|---|---|---|---|
| 5 dias, cidades 1000+ (padrão) | 8.16 | 1.63 | 0.21 | 1.46 | 0.94 | 45 |
| **10 dias**, cidades 1000+ | 14.66 | 1.47 | **0.39** | 1.09 | 0.67 | 51 |
| 5 dias, **cidades 2000+** | 4.71 | 0.94 | 0.35 | 2.02 | 0.88 | 28 |

- **Risco de morte é constante (~4%/dia), não "morte cedo"**: 0.21 nos 5
  primeiros dias, 0.18 nos 5 seguintes. Meia-vida ~17 dias. Quem sobrevive
  melhora com a idade (panes/dia −25%, fervura/dia −29%): a gordura acumula
  (51) e o corpo é mantido — mas o azar de uma noite ruim continua matando.
- **Cidade manda.** Perito (sem política) rende ent 4.6 em 1000+ e 3.3 em
  2000+: o conjunto de teste padrão é o mais fácil dos quatro. O campeão cai
  −42% em 2000+ — ⅔ dificuldade, ⅓ possível overfit. **Todos os números em
  1000+ estão ~30% otimistas.** Decisão: avaliar em 6 cidades daqui pra
  frente (predição 25 ✗ na cláusula de generalização).

### 6.6 E13i — replicação com 5 sementes: "a dor ensina" não paga

| braço | fit (5 sementes) | por semente | mortos | panes | oficina |
|---|---|---|---|---|---|
| noite s+r (sem corpo) | 7.33 | 5.9 / 8.0 / 8.5 / 6.7 / 7.6 | 0 | 13.3 | 0 |
| corpo | 6.88 | 6.8 / 8.5 / 5.9 / 7.3 / 5.9 | 0.38 | 8.3 | 6.9 |

Diferença **−0.45** (n=3 dava +0.75). Regra da replicação (feedback
"replicação > σ"): o efeito seguiu o n e trocou de sinal — era ruído. O que
sobrevive: o corpo muda o COMPORTAMENTO em 5/5 sementes (metade das panes,
oficina de 0 pra 7), e a morte cobra o que o cuidado rende. Predição 26 ✗.

### 6.7 E13j/k — sono que come, cérebro que come, fome rara (longo)

| braço | fit | mortos | res~ | panes | notas |
|---|---|---|---|---|---|
| recomendado | 8.16 | 0.21 | 45 | 7.3 | referência |
| + sono come (5 fuel/descanso) | 6.91 | 0.26 | 40 | 8.9 | dorme 3×/vida; queima tanque → pane |
| + cérebro come, Reativo | 8.16 | 0.21 | 45 | 7.3 | controle: bit-igual (sem custo neural) |
| + cérebro come, **Tálamo** | 7.45 | 0.22 | 46 | 7.2 | paga o cérebro em caloria e vive |
| + cérebro come, **Sempre** | −0.52 | 0.28 | 19 | 4.2 | ent 1.0, pobre 0.47: PARALISIA |
| greve 1 em 4, com gordura | 6.49 | 0.30 | 39 | 9.4 | greve custa −1.67 |
| greve 1 em 4, sem gordura | 5.45 | 0.28 | – | 11.2 | gordura vale +1.04 na fome |

- **Dormir custa mais do que engordar rende.** Com sono comendo 5 de fuel, o
  ser dorme só 3 vezes por vida e mesmo assim perde 1.25 e +5 pp de mortos —
  ele não troca gordura por sono (gordura −11%), troca sono por vida e paga
  em panes. O trade-off que o Leonardo descreveu existe; nesta economia o
  sono perde.
- **Cérebro que come, com morte no mundo: tálamo 7.45 × sempre −0.52** — gap
  de 8.0, o maior de todas as fases B (E6: 6.3 no fitness; E12: 1.7). Ligar
  tudo não mata: PARALISA — o cérebro come o tanque antes de o ser andar, e
  ele fica parado, pobre e magro. O tálamo (10% dos órgãos ligados) paga
  0.7 de fitness pelo cérebro e vive igual.
- **Fome rara no mundo-corpo: a gordura já foi gasta na noite.** A greve
  custa só −1.67 (E12 sem noite: −4.5) e a gordura acrescenta +0.2 sobre o
  que já valia sem greve. Res~ 39 e 4 mobilizações/vida: a noite diária
  consome a poupança antes de o dia de greve chegar. Duas escassezes
  competem pelo mesmo estoque e a mais frequente ganha (lei do E12 §7: o
  estoque na greve é I/f_noite, não I/f_greve).

### 6.8 E13l — sono em bloco à noite (longo)

Mecanismo: à noite, escolher `descanso` vira dormir até as 6h (fadiga zera,
não roda de madrugada). Decisão do ser; nenhum roteiro.

| arquitetura | fit | mortos | bloco (noites de 5) | par_noite | panes |
|---|---|---|---|---|---|
| Reativo, sem bloco | 8.16 | 0.21 | – | – | 7.3 |
| Reativo + bloco | 8.30 | **0.18** | 1.1 | 0.69 | 7.5 |
| ReativoHora + bloco | 8.17 | 0.19 | 1.2 | 0.70 | 7.2 |

O bloco existe e quase ninguém entra: uma noite por vida, nas duas
arquiteturas. −3 pp de mortos (n=3, replicação em E13n), fitness igual. A
hora como feature não faz o ser ir dormir — terceira vez que o ReativoHora
não usa a hora (E12b, E13e, E13l): 12 pesos a mais que a evolução de G=60
não aprende a apontar. Predição 29 ✗. O piso de ~18% de mortes é da família
reativa de 1 salto; a próxima alavanca teria de ser um órgão com sinal de
noite no portão (tálamo), não a física do sono.

### 6.9 E13m — números honestos e vida longa

**Seis cidades (1000+ e 2000+):** recomendado **6.44 / mortos 0.28**; com
sono em bloco 6.52 / 0.25. O bloco rende −3 pp de mortos nos dois conjuntos
de cidades e nada de fitness.

**Treino com vida de 10 dias (G=100, T_evo=2400), avaliado em 10 dias:**

| braço | fit | fit/dia | mortos | vida_fim | bloco (noites de 10) |
|---|---|---|---|---|---|
| campeão de 5 dias, vivendo 10 (§6.5) | 14.66 | 1.47 | 0.39 | 52 | – |
| treinado 10 dias | 16.98 | 1.70 | **0.39** | 53 | – |
| treinado 10 dias + **sono em bloco** | **18.02** | 1.80 | **0.29** | 63 | 1.9 |

- **O risco de 4%/dia é piso do mundo**, não falta de treino: dobrar a vida
  no treino melhora o fitness/dia (+16%) e não move a mortalidade (0.39 =
  0.39). Predição 30b ✗.
- **O sono em bloco cresce com a vida.** −3 pp em 5 dias, **−10 pp em 10
  dias** (3/3 sementes), +1.0 de fitness. Dormir uma noite inteira a cada
  5 evita as mortes tardias — é a primeira alavanca que mexe no piso.
  Replicação com 5 sementes em E13o.

**Replicação (E13n, 5 sementes, vida de 5 dias):** recomendado 8.76 / mortos
0.18; com bloco 7.55 / 0.21. O bloco **perde** 1.2 de fitness e não reduz
mortes (2/5 sementes abaixo). O −3 pp de n=3 — repetido em 2000+ — era
ruído. Em vidas de 5 dias o bloco é inerte. O −10 pp em 10 dias (n=3) só
vale se sobreviver ao E13o (5 sementes). Quarta vez que n=3 enganou hoje:
regra de casa a partir daqui, **efeito de mortalidade só conta com n ≥ 5**.

**Replicação em vida de 10 dias (E13o, 5 sementes):** recomendado 18.70 /
mortos 0.29; com bloco 17.68 / 0.31 — 1/5 sementes com menos mortos. O
−10 pp de n=3 era ruído. **Sono em bloco: encerrado** (inerte a nocivo em 5
e 10 dias). O piso de mortalidade não cedeu a nenhuma das cinco alavancas
testadas (treino longo, hora, rota, sono em bloco, cérebro por tálamo): é o
teto da política reativa de 1 salto neste mundo.

### 6.10 E13p — as duas decisões recomendadas, com 5 sementes

| decisão | n=3 | n=5 | veredito |
|---|---|---|---|
| cap 120 vs 60 (res-posto, sem peso, reboque 20) | +2.37 (3/3), −8 pp | **+0.40 (2/5), +1 pp** | ruído — cai |
| reboque 0 vs 20 (res-posto, sem peso, cap 120) | +1.10, −14 pp | **+1.32 (4/5), −11 pp (5/5)** | **replica** |

Mortos por semente, reboque 20 → 0: 0.38→0.26, 0.31→0.23, 0.42→0.21,
0.27→0.23, 0.33→0.23. A armadilha de pobreza (§4.5) é o achado mais robusto
do E13: multa em dinheiro na moeda que compra o conserto mata por espiral.
O cap era o que parecia mais óbvio pela lei do E12 e era ruído: a noite
gasta a gordura antes de o cap importar (§6.7).

### 6.11 Números finais e o que sobreviveu ao n=5 (E13q)

**Mundo recomendado** (corpo + massa como cálculo base + gordura contínua 2%
+ reboque só no corpo + noite; cap 120 indiferente), Reativo, G=60, 5 dias:

| cidades | fit (5 sementes) | mortos |
|---|---|---|
| 1000+ (fáceis) | 8.76 | 0.18 |
| 2000+ (duras) | 5.39 | 0.30 |
| **média honesta (6 cidades)** | **7.08** | **0.24** |

Afirmações do E13, replicadas com 5 sementes (1000+):

| afirmação | n=3 | n=5 | veredito |
|---|---|---|---|
| gordura contínua vale | +0.82, −6 pp | **+0.79 (4/5), −7 pp (4/5)** | ✓ |
| peso por massa custa, via fervura | −2.26, fervura +2.0 | **−2.34 (5/5), fervura +1.2** | ✓ |
| reboque só no corpo (sem multa) | −14 pp | **−11 pp (5/5), +1.3** | ✓ |
| cap 120 > 60 | +2.37 (3/3), −8 pp | +0.40 (2/5), +1 pp | ✗ ruído |
| sono em bloco (5 d) | −3 pp | +3 pp, −1.2 | ✗ ruído |
| sono em bloco (10 d) | −10 pp (3/3), +1.0 | +2 pp, −1.0 | ✗ ruído |
| "a dor ensina" (fitness) | +0.75 | −0.45 | ✗ ruído |

Três de sete sobreviveram — as três que têm mecanismo físico direto
(gordura cobre pane; peso esquenta; multa quebra). As quatro que caíram
eram efeitos de MORTALIDADE ou ganhos sem mecanismo próprio. Regra 13.

### 6.12 E13r — o portão do tálamo lendo a noite (5 sementes)

| arquitetura (cérebro come do tanque) | fit | mortos | por semente (mortos) |
|---|---|---|---|
| Tálamo | 7.26 | 0.24 | 0.26 / 0.11 / 0.21 / 0.37 / 0.24 |
| Tálamo + noite no portão | 7.01 | 0.23 | 0.15 / 0.21 / 0.19 / 0.24 / 0.35 |

Efeito zero, como previsto (predição 35 — a primeira predição honestamente
negativa que acertou). O sinal de noite no órgão não abre o posto. Placar
das alavancas contra o piso de mortalidade: treino de 10 dias, hora, rota,
sono em bloco, tálamo, tálamo-noite — **seis, nenhuma move**. O piso é do
mundo (posto fechado + tanque vazio) cruzado com a política de 1 salto; a
única saída declarada é memória de rota ou replanejamento (N2/N10), que a
família linear não tem.

### 6.13 E13s — as últimas afirmações do recomendado, com 5 sementes

| afirmação | n=3 | n=5 | veredito |
|---|---|---|---|
| taxa .05 pior que .02 | −0.48 | **−1.37 (5/5)** | ✓ |
| taxa .01 pior que .02 | −0.58 | −0.60 (2/5), mortos +4 pp | marginal |
| sono come custa | −1.25, +5 pp | **−2.01 (5/5), +9 pp (5/5)** | ✓ |

O vale da taxa é assimétrico: acumular depressa custa com certeza; devagar
demais custa pouco. Dormir queimando caloria é nocivo em todas as sementes —
nesta economia o sono perde pra gordura, sempre.

### 6.14 E13t — o teto da alavanca "encher antes da noite" (regra à mão nos campeões)

Regra 1 antes de gastar mais evolução: injetar a regra no campeão de 5
sementes (mesma cidade, mesma semente) e medir o teto.

| política | fit | mortos | por semente (mortos) | panes | tanque às 22h |
|---|---|---|---|---|---|
| campeão | 8.75 | 0.181 | .15 .18 .23 .17 .17 | 7.6 | 46 |
| + bônus no serviço posto às 20–22h (sem rota) | 8.79 | 0.178 | — | 7.4 | 48 |
| + **rota puxada pro posto às 20–22h com tanque < 70** | 8.75 | **0.134** | .12 .15 .17 .11 .12 | 5.5 | 61 |
| + rota 18–22h com tanque < 90 | 8.13 | 0.135 | — | 3.1 | 74 |
| "sempre encher" (24h, tanque < 40) | 4.65 | 0.319 | — | 3.1 | 56 |

- **A alavanca existe e vale 5 pp** (5/5 sementes, fitness intacto). O
  ReativoHora tinha 12 pesos pra achá-la e não achou — evolvabilidade.
- **Os 13% restantes são físicos.** Com o tanque a 74 às 22h ainda há 3
  panes por vida e 13% de mortos. O campeão já compra o tanque grande
  (3.6 upgrades/vida, capacidade 130): mesmo com 135 de tanque a noite +
  manhã não fecha em toda cidade. Forçar a compra não acrescenta.
- "Sempre encher" mata mais: vive no posto, entrega pouco, e morre de
  fervura no vai-e-vem. Timing certo > cautela constante.
- Teste de evolvabilidade em E14a: 2 genes de timing nos pesos mortos do
  Reativo (predição 38) — a evolução acha 2 números onde não achou 12?

### 6.15 E14a — dois genes de timing, e o mecanismo do piso

`ReativoNoite`: os 12 pesos mortos do Reativo viram 2 — um empurra o serviço
posto e outro puxa a rota pro posto, ambos só entre 20h e 22h e proporcional
ao tanque vazio. A regra à mão com esses dois números tirou 5 pp de mortos.

| | fit | mortos | genes (posto, rota) por semente |
|---|---|---|---|
| Reativo | 8.76 | 0.18 | – |
| ReativoNoite | 7.25 | 0.23 | (0.96, .40) (−1.96, .43) (−1.20, −.24) (0.96, .32) (−1.81, .65) |

A evolução achou o gene — com o **sinal errado** em 3 de 5 sementes. Não
é evolvabilidade. Olhe o teto (§6.14): a regra tirou 5 pp de mortos e o
fitness ficou **idêntico** (8.75 = 8.75). Quem morre no dia 4 já entregou
quase tudo que entregaria no dia 5. **A morte não custa fitness — logo não
é selecionada.** É o mecanismo por trás das seis alavancas nulas: nenhuma
podia ser achada porque o objetivo não contém a vida. Os genes derivaram ao
acaso e 3/5 caíram do lado que atrapalha.

Conserto proposto e testado em E14b: pena por morrer no fitness da evolução
(`pena_morte`, 0 = identidade). Se a evolução achar os dois genes com a
pena, o piso era do objetivo — e "seres que tentam deixar o carro vivo"
exige que viver valha pontos, não só entregar.

### 6.16 E14b — a vida no fitness (pena por morrer)

| arquitetura | pena | fit (sem pena) | mortos | genes posto por semente |
|---|---|---|---|---|
| Reativo | 0 | 8.76 | 0.18 | – |
| Reativo | 5 | 7.18 | 0.22 | – |
| ReativoNoite | 0 | 7.25 | 0.23 | 0.96 −1.96 −1.20 0.96 −1.81 |
| **ReativoNoite** | **5** | 7.51 | **0.16** | **1.73 1.13 4.03 1.58 4.40** |

- **Com a vida no objetivo, o gene aponta pro lado certo em 5/5 sementes**
  (sem pena: 3/5 pro lado errado). É o resultado categórico do dia: não era
  falta de alavanca nem de gerações — era o fitness que não via a morte.
- A mortalidade cai de 0.23 pra 0.16 (abaixo do Reativo, 0.18); o tamanho
  ainda está dentro do ruído de ±8 pp e não chega ao teto da regra à mão
  (0.134). E14c testa se o limite é o ruído de avaliação (16 vidas por
  genoma → 64).
- Pena no Reativo puro não ajuda (0.22): sem alavanca no genoma, o gradiente
  não tem onde agir. Pena custa fitness (−1.2 a −1.6): viver mais devagar.
- **Pro Leonardo:** "seres que tentam deixar o carro vivo" exige que viver
  valha pontos. Entregas − avarias não basta: quem morre no dia 4 entregou
  quase tudo. Candidatos a objetivo: pena fixa por morte (testado), ou
  fitness por dia vivido (entregas/dia × dias), ou vida como moeda do
  torneio (arena).
