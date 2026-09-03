# 36 — O corpo fala: dois sistemas que aprendem a se comunicar (E20, 2026-09-03)

**Leonardo:** *"o ser precisa de mais incentivo pra procurar comida; toma ações
singulares, o foco fica na corrida e só pensa em comer quando a fome está
alta. Aplicar de verdade o cortisol e outros hormônios, o cérebro perceber
que o corpo se comunica com ele com essa força; uma rede pro próprio corpo,
treinada pra modular hormônios — cérebro e corpo como dois sistemas
complexos que com o tempo acham uma forma de se comunicar."*

## O que muda (sem tocar no `lab.py`)
- O cérebro **deixa de ver o corpo cru**. As features do corpo (tanque, fome,
  cansaço, pneu, calor, óleo, dinheiro, gordura, dano, dívida) são canceladas
  no score de movimento, e a necessidade crua sai do score de serviços.
- Uma **rede do corpo** (8 sinais → 6 neurônios tanh → K hormônios sigmoide),
  cada hormônio com lentidão τ (1–200 passos), produz o que o cérebro vê.
- O cérebro decide serviços por `sv · paga · (h @ G)` e ganha um viés de
  movimento por hormônio. Tudo no genoma; co-evolução no mesmo fitness.
- Controles: `direto` (Reativo, vê tudo), `K=1`, `K=4`, `redundante` (vê o
  corpo cru E os hormônios — com genes zero é bit-igual ao Reativo).

Por que gargalo: no E16 os hormônios eram redundantes com as features cruas
e a seleção os desligou. Com gargalo, a comunicação passa a ser obrigatória.

Verificado antes de rodar: portão bit-exato; redundante com genes 0 ==
Reativo (bit); gargalo muda o comportamento do perito (1.97 vs 2.41); zero
sync no laço quente; 5.6 ms/passo (GPU livre).

## Predições (antes de rodar; triagem R=8, G=40, 3 sementes; mundo = pacote final do E19)
Referência da triagem: `direto` mede a si mesmo na mesma rodada.
1. `K=2` recupera ≥ 80 % do fitness do `direto` e tem mortos ≤ direto: o
   corpo aprende a codificar tanque e fome em 2 canais.
2. `K=1` desaba (fit < 60 % do direto): um canal não separa "sem gasolina"
   de "com fome".
3. `K=4` ≈ `K=2` (canais sobrando ficam inertes).
4. `redundante` ≈ `direto`, com hormônios inertes (G ≈ 0): a redundância
   mata a comunicação (o mesmo do E16).
5. Fome no fim: `K=2` < `direto` em ≥ 2/3 sementes — o corpo consegue fazer a
   fome soar mais alto e por mais tempo (τ evoluído > 20 passos).
Se `K=2` ficar < 60 % do direto: 82 genes em G=40 não convergem (busca), e
a próxima é co-evolução em duas populações ou τ fixo.

## Triagem 1 (sem código herdado) — R=8, G=40, 3 sementes

| braço | genes | fit | entregas | mortos | fome no fim |
|---|---|---|---|---|---|
| direto (Reativo) | 44 | 4.85 | 9.4 | 0.60 | 85 |
| corpo fala K=2 | 126 | 1.64 | 5.3 | **0.97** | 100 |
| corpo fala K=1 | 112 | 2.03 | 5.5 | 0.96 | 100 |
| corpo fala K=4 | 154 | 2.23 | 5.9 | 0.97 | 100 |
| redundante K=2 | 126 | 4.98 | 9.3 | 0.66 | 90 |

Predição 4 ✓ (redundante = direto, hormônios inertes). Predições 1, 2, 3, 5
✗: com o gargalo **97 % morrem de fome** — corpo e cérebro não acham o
código "fome → comida" em 40 gerações com 82–110 genes, e como todo mundo
morre não há gradiente (deserto, o mesmo do E19). Mecanismo, não ruído:
fome em 100 nas 9 sementes.

Diagnóstico com o perito (não serve de teste — ele se exaure e quebra:
dinheiro −2, 1.2 refeições/vida): quando está num nó com comida, a comida
GANHA do movimento (4.5–5.9 vs < 0); ele não come porque está em descanso
forçado (fadiga 95) ou sem 3 dinheiros. A decisão é argmax puro, sem ruído.

**Triagem 2 — código herdado (predições 6–8, antes de rodar):**
6. `corpo nasce falando` (h0 = fome, h1 = sede de gasolina, fixos; o cérebro
   tem de aprender a ouvir): mortos ≤ 0.70 e fome no fim < 100 em ≥ 2/3 —
   metade do código pronto basta pra sair do deserto.
7. `corpo fala + cérebro ouve` (os dois priors): ≈ direto (fit ≥ 80 %,
   mortos ≤ direto + 0.1) — o canal funciona de ponta a ponta; a evolução
   só refina.
8. `só cérebro ouve` (o corpo tem de aprender a falar): pior que 6 — falar é
   mais difícil que ouvir (a rede do corpo tem 68 genes, o ouvido tem 10).
