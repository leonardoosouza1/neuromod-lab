# 38 — E22: o cérebro aprende a ouvir EM VIDA (plasticidade gateada por recompensa)

O E20 mostrou que hormônio + receptor herdados funcionam, e que o receptor
não nasce por seleção em 40 gerações. A biologia tem outro caminho, que a
linha de Najarro & Risi (regras hebbianas evoluídas, 2020) e o nosso
cérebro-por-órgãos (dopamina como portão de plasticidade) já usaram: **o
receptor se ajusta durante a vida**, guiado por um sinal de recompensa.

## Desenho (arquivo novo, sem tocar no `lab.py`)
- Corpo: as glândulas do E20 com código herdado só do lado do corpo (h0 =
  fome, h1 = sede), τ rápido.
- Cérebro: `Gserv` (K×5, hormônio → serviço) começa em ZERO e muda em vida:
  `ΔG[k,p] = η · h_k · [usou o serviço p] · r`, onde `r` = recompensa do
  passo (entregou +1, comeu/abasteceu +0.5 se a necessidade caiu, pane −1,
  dano −0.1·Δvida). Gene: η (taxa) e um decaimento. Tudo em `atualizar()`
  (in-place, fora do grafo).
- Controles: η=0 (surdo, = E20 "corpo nasce falando"), código herdado dos
  dois lados (teto), plasticidade sem gate (r=1 sempre: Hebb puro).

## Predições (antes de rodar; triagem)
13. Com η > 0 e gate por recompensa, o cérebro surdo passa a comer: mortos
    ≤ 0.70 e fome no fim < 90 (E20: 0.89–0.93 / 97–100); com η evoluída,
    ≥ 2/3 sementes escolhem η > 0.
14. Hebb puro (sem gate) NÃO aprende o certo (mortos ≈ surdo): sem a
    recompensa, "fome alta + serviço posto" também é reforçado (é onde ele
    está) — o gate é o que separa correlação de causa (o mesmo que a dopamina
    fez no cérebro-por-órgãos: sem ela, acaso).
15. Código herdado dos dois lados continua sendo o teto (≈ direto); a
    plasticidade chega a ≥ 70 % do teto.

## Triagem (R=8, G=40, 3 sementes) — negativa com mecanismo

| braço | fit | entregas | mortos | fome no fim |
|---|---|---|---|---|
| direto (Reativo) | 4.85 | 9.4 | 0.60 | 85 |
| surdo (corpo fala, η=0) | 1.31 | 5.0 | 0.95 | 98 |
| curioso sem aprender (Gserv aleatório por vida, η=0) | 0.39 | 4.3 | 0.96 | 99 |
| aprende a ouvir (η evolui) | 0.68 | 4.1 | 0.95 | 99 |
| aprende a ouvir (η=.1 fixa) | 0.82 | 4.3 | 0.95 | 99 |
| Hebb puro (sem recompensa) | 0.64 | 4.4 | 0.97 | 99 |
| teto: código herdado dos 2 lados | 4.38 | 9.3 | 0.58 | 80 |

Predição 13 ✗ (a plasticidade não salva: 0.95 = surdo), 14 ✓ (Hebb puro não
aprende — mas trivialmente, ninguém aprendeu), 15 ✓ (o teto continua sendo o
código herdado). Mecanismo: a regra `ΔG = η·h·usou·r` só dispara depois da
PRIMEIRA refeição, e a primeira refeição depende de escolher "comida" num nó
com comida por acaso — com a fome matando em ~2 dias, o táxi morre antes do
acaso. A curiosidade aleatória (Gserv ~ N(0,3)) não bastou. Quarta aparição
do deserto: seleção (E19), currículo (E20), receptor (E20), plasticidade (E22).

**O que o deserto pede:** tempo de explorar SEM morrer — infância individual
(E8): a fome não fere nos primeiros 2 dias de cada vida (`fome_gracia`),
depois fere normal. Não muda o objetivo nem o mundo adulto.

**Predição 18 (antes de rodar, triagem, mesma bateria com `fome_gracia`=480):**
`aprende a ouvir η=.1` ≤ surdo − 0.15 em mortos e ≥ 2/3 sementes com
Gserv[fome→comida] > 0 no fim da vida; `direto` melhora (mortos ≤ 0.50);
teto ≈ direto. Se `aprende` continuar = surdo mesmo com 2 dias de graça: a
primeira refeição não acontece por acaso nem sem pressão — o gargalo é o
número de nós com comida (6 de 26), não o tempo.

## E25 (infância individual, triagem) — parcial

| braço | fit | mortos | fome no fim |
|---|---|---|---|
| direto (Reativo), com 2 dias de graça | 5.27 | 0.47 | 79 |
| surdo (η=0) | 1.27 | 0.89 | 97 |
| aprende a ouvir η=.1 | 0.45 | 0.93 | 98 |

A graça ajuda o cérebro direto (0.60 → 0.47) e não ajuda o aprendiz
(predição 18 ✗): a curiosidade nos PESOS (Gserv aleatório) não faz a
primeira refeição acontecer — o viés de serviço evoluído esconde qualquer
serviço. Curiosidade de verdade é tentar serviços: **E25b, ε-exploração na
infância** — com probabilidade ε o táxi usa um serviço disponível ao acaso
(só enquanto a fome não fere). Predição 25: com ε=.2, o surdo curioso come
≥ 2 vezes na infância e o aprendiz η=.1 sai do deserto (mortos ≤ 0.75,
Gserv[fome→comida] > 0 em ≥ 2/3 sementes); η=.3 + ε=.4 melhor ainda. Se o
aprendiz continuar = surdo curioso: a regra de recompensa está errada (não
é falta de tentativa).
