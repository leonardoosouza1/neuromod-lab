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
