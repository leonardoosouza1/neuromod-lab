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

## Triagem 2 (código herdado) — R=8, G=40, 3 sementes

| braço | fit | entregas | mortos | fome no fim | posto/vida |
|---|---|---|---|---|---|
| K=2 corpo nasce falando | 2.00 | 5.7 | 0.96 | 100 | 12.8 |
| K=2 corpo fala + cérebro ouve | 1.73 | 6.3 | 0.90 | 97 | 9.0 |
| K=2 só cérebro ouve | 1.64 | 5.1 | 0.98 | 100 | 14.6 |

Predições 6–8 ✗ — e o culpado é meu desenho, não a evolução: os hormônios
nasciam com τ ≈ 100 passos (gene 0 → sigmoide 0.5 → 101). A "sede de
gasolina" continua alta 100 passos depois de abastecer; como o posto agora
vende comida, no mesmo nó o serviço posto (h1·10) ganha da comida (h0·10) e
o táxi fica abastecendo em loop (9–15 visitas ao posto por vida, dinheiro
indo embora) sem comer. No cérebro direto a necessidade zera na hora do
abastecimento. Conserto: τ nasce rápido (gene 0 → ~5 passos) e a evolução
alonga se valer.

**Predição 9 (antes de rodar):** com τ rápido, `corpo fala + cérebro ouve`
≈ direto (fit ≥ 3.9, mortos ≤ 0.70, fome no fim < 90); `corpo nasce
falando` mortos ≤ 0.85. Se continuar ≥ 0.9: o problema é o empate posto ×
comida no mesmo nó (precisa de um "combo": abastecer também sacia).

## Triagem 3 (τ rápido) — R=8, G=40, 3 sementes

| braço | fit | entregas | mortos | fome no fim |
|---|---|---|---|---|
| direto (Reativo, triagem 1) | 4.85 | 9.4 | 0.60 | 85 |
| **K=2 corpo fala + cérebro ouve** | **4.38** | 9.3 | **0.58** | **80** |
| K=2 corpo nasce falando (cérebro tem de aprender a ouvir) | 2.16 | 6.5 | 0.89 | 97 |

Predição 9 ✓ no canal completo: **o gargalo de 2 hormônios transmite o
corpo sem perda** quando os dois lados nascem com o código (é o que a
biologia faz: cortisol e o receptor de cortisol vêm juntos). A evolução
com τ rápido não piorou nada e a fome terminou mais baixa que no direto.

O que NÃO aconteceu: aprender o código do zero. Com o corpo falando e o
cérebro surdo (um gene: comida ← h0), 89 % morrem de fome em 40 gerações —
não há gradiente enquanto todo mundo morre (o deserto, 3ª vez). Comunicação
não emerge num mundo que mata antes da primeira palavra.

**Próximo passo honesto (a decidir):** proteger a infância da população —
fome ferindo pouco nas primeiras gerações e subindo depois (currículo por
fração da população, como no E-currículo do Universe) — e medir se o cérebro
surdo aprende a ouvir. Alternativa: aceitar o código herdado como ponto de
partida e evoluir só o refinamento, que é o que a triagem 3 já mostra que
funciona.

**Predição 10 (antes de rodar — infância protegida, triagem):** com a fome
ferindo 0.03 na geração 0 e subindo até 0.15 em 60 % das gerações
(`--curriculo`), o cérebro surdo aprende a ouvir (`corpo nasce falando`:
mortos ≤ 0.70 na avaliação final com fome 0.15, fome no fim < 90) e o par
sem código nenhum (`corpo fala K=2`) sai do deserto (mortos ≤ 0.85). Se
nenhum sair: 40 gerações não bastam pra uma palavra — testar G=100 no
honesto antes de mudar o desenho.

## Honesto (R=16, 5 sementes) e currículo — fechamento do E20

| braço | fit | entregas | mortos | fome no fim |
|---|---|---|---|---|
| direto (Reativo) | 6.90 | 11.5 | 0.35 | 69 |
| K=2 corpo fala + cérebro ouve (código herdado) | 5.83 | 10.8 | 0.36 | 67 |
| corpo fala K=2, infância protegida (triagem) | 1.74 | 4.5 | 0.97 | 100 |
| corpo nasce falando + infância protegida (triagem) | 1.95 | 5.8 | 0.93 | 99 |

- **Canal de 2 hormônios com código herdado: mesma mortalidade, −1.1 de
  entregas** (4/5 sementes). Dois canais carregam o que mata (fome, gasolina)
  e perdem o resto (dinheiro, pneu, calor, dano) — o cérebro direto vê dez
  sinais. É o preço do gargalo, não um bug.
- **Aprender o código do zero não emergiu**, nem com a fome ferindo pouco nas
  primeiras gerações (predição 10 ✗). Com 126 genes, 40 gerações e um evento
  raro dos dois lados (o corpo tem de produzir um canal que sobe com fome E o
  cérebro tem de pesá-lo em comida), a seleção não acha a primeira palavra.
  Bate com a literatura de comunicação emergente: gargalo sozinho não
  produz código; precisa de pressão específica (aprendizado iterado,
  jogos de sinalização) — e a biologia resolve herdando receptor e hormônio
  juntos.

**Veredito E20:** hormônios como canal funcionam quando nascem com o código
(biologia); como linguagem que emerge, não nestes orçamentos. O que o
Leonardo descreveu — "o corpo grita e o cérebro ouve" — vira, na prática,
**priorização**: escolher a necessidade mais urgente e deixar só ela falar.
É exatamente o achado de 2026 em "interoceptive attention" (AffectWorld):
atenção dinâmica à necessidade mais urgente dobrou a sobrevivência. Próximo
teste: E21, atenção interoceptiva (só a maior necessidade decide o serviço).

## E21 — atenção interoceptiva (predição 11, antes de rodar)
`ReativoAtencao`: no score de serviços, só a necessidade mais urgente (entre
as disponíveis e pagáveis) mantém seu termo; as outras são canceladas
(winner-take-all). `atencao off` é bit-igual ao Reativo. Variante `suave .3`
mantém 30 % das outras.
11. Triagem: `atencao` tem mortos ≤ direto − 0.10 e fome no fim ≤ 60 (a fome,
    quando é a maior necessidade, decide sozinha), com fit ≥ direto − 0.5;
    `suave .3` entre os dois. Se mortos não caírem: a fome raramente é a
    MAIOR necessidade no momento em que há comida — e o conserto é a
    persistência (uma vez eleita, a necessidade segue mandando por N passos).

### E21 triagem (R=8, G=40, 3 sementes)

| braço | fit | entregas | mortos | fome no fim |
|---|---|---|---|---|
| direto (Reativo) | 4.85 | 9.4 | 0.60 | 85 |
| **atenção interoceptiva** (só a maior necessidade decide) | **5.00** | 10.0 | **0.49** | 77 |
| atenção suave .3 | 4.82 | 9.5 | 0.56 | 80 |

Predição 11: mortos −11 pp ✓ (2/3 sementes abaixo), fit ≥ direto ✓, fome no
fim ≤ 60 ✗ (77). Primeira alavanca de DECISÃO que reduz a morte por fome sem
custar entregas — e é o achado de 2026 (AffectWorld) reproduzido no táxi.
Ruído da triagem ±8 pp: decide no honesto.

**Predição 12 (antes de rodar, honesto R=16, 5 sementes):** atenção
interoceptiva vs direto (6.90 / 0.35): mortos ≤ 0.28 com ≥ 4/5 sementes
abaixo, fit ≥ 6.4, fome no fim ≤ 65. Se mortos ficarem ≥ 0.33: a triagem
era ruído e a atenção só reorganiza sem salvar — a próxima é persistência
(a necessidade eleita segue mandando N passos).

### E21 honesto (R=16, 5 sementes)

| braço | fit | mortos | por semente (mortos) | fome no fim |
|---|---|---|---|---|
| direto | 6.90 | 0.35 | .30 .38 .38 .39 .32 | 69 |
| atenção interoceptiva | 6.55 | 0.36 | .57 .34 .33 .30 .25 | 66 |

Predição 12 ✗: o −11 pp da triagem era ruído (sexta vez que n=3 engana;
regra 13 vale também pra triagem). Mecanismo do empate: no táxi as
necessidades raramente competem no mesmo instante — o Reativo com pesos
evoluídos já age como "uma de cada vez"; o achado de 2026 (AffectWorld)
supõe várias necessidades simultâneas disputando um orçamento de precisão,
que aqui não existe. A morte por fome não é competição entre necessidades:
é estar no nó certo com dinheiro e escolher comer. Atenção interoceptiva
encerrada como neutra.
