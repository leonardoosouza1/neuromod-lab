# 33 — Onda 1: resultados das baterias honestas (R=16, 5 sementes) — 2026-09-02/03

Regra da casa: efeito de mortalidade só conta com n ≥ 5 (regra 13) e com 64
vidas por genoma (regra 14). Tudo aqui segue isso. Cidades 1000+ (as fáceis;
2000+ vem depois). "mortos" = fração que morre em 5 dias; "fit" = entregas −
0.3·avarias, sem a pena.

## E17 — cérebro com produtos (pena 5)

| cérebro | genes | fit | mortos | panes | leitura |
|---|---|---|---|---|---|
| Reativo (soma sinais) | 44 | 8.54 | 0.19 | 7.9 | referência |
| ReativoNoite24 (1 produto: tanque × d_posto) | 44 | 8.40 | **0.15** | 6.5 | o produto certo, sozinho |
| ReativoProduto (5 produtos necessidade × distância + 2 de hora) | 51 | **6.10** | 0.21 | 4.9 | **pior**: −2.4 de fitness, mortos iguais |

**O que ajudou:** um produto só (tanque × distância ao posto) segue sendo o
que reduz mortes (−4 pp) sem custar entregas.
**O que piorou:** dar cinco produtos ao mesmo tempo. Mecanismo (apontado
pelo agente E17 e visível aqui: panes caem pra 4.9 mas entregas caem de 12.5
pra 9.6): fome, fadiga e pneu quase nunca são zero, então "necessidade ×
distância" vira atração CONSTANTE ao serviço — o táxi fica orbitando comida
e descanso em vez de trabalhar. O produto do tanque só funciona porque o
tanque cheio desliga o termo. Conserto proposto: limiar `relu(nec − θ)` com θ
gene (o produto só liga quando a necessidade passa de um ponto). Fica pra
onda 2. Predição 17.3 ✗.

Genes de produto evoluídos (5 sementes; posto · comida · descanso · oficina · loja):
posto 0.5–1.0 em **5/5** (redescobriu o do Noite24, mais fraco), **descanso 0.6–1.0
em 5/5** (o atrator: puxa pro descanso sempre, porque fadiga nunca é zero),
oficina 0–1.1, comida ≈ 0, loja pequeno; os dois genes de hora ficaram
dispersos (−3.7 a +1.7) — 6ª vez que hora não converge.

## E17 — cérebro com produtos, SEM pena (controle)

| cérebro | fit | mortos | panes |
|---|---|---|---|
| Reativo | 9.42 | 0.18 | 6.5 |
| **ReativoNoite24 (1 produto)** | **9.61** | **0.13** | 5.4 |
| ReativoProduto (5 produtos + hora) | 7.06 | 0.19 | 6.7 |

Sem pena a história é a mesma e mais limpa: **o produto certo, sozinho,
melhora os dois eixos** (+0.2 entregas, −5 mortos por 100, 4/5 sementes); os
cinco juntos custam 2.4 de entregas e não salvam ninguém. Com pena o
ReativoProduto tinha panes 4.9 e agora 6.7 — sem a pena ele não se esconde
tanto no descanso, mas continua orbitando. Veredito da onda 1 pro cérebro:
**produtos sim, mas um de cada vez e com limiar** (só ligam quando a
necessidade passa de um ponto). Predição 17.3 ✗ nos dois controles.

## E15 — economia real (pena 5, R=16) — parcial (faltam tanque / só gordura)

| mundo | fit | mortos | panes | renda bruta | imposto (receber+gastar) | aluguel+água | dívida máx | leitura |
|---|---|---|---|---|---|---|---|---|
| **âncora: corpo sem economia** | 8.54 | 0.19 | 7.9 | 239 | 0 | 0 | 0 | referência (bit-igual ao Reativo do E17: mesmo protocolo) |
| economia, reboque sem custo calórico (só −3 de vida) | 6.89 | **0.09** | 9.2 | 220 | 44 + 25 | 39 | 2.5 | menos mortos de toda a linha; mas pane volta a ser "posto grátis" (9.2/vida) |
| economia, reboque cobra 3 de gordura e o resto da VIDA | 6.11 | **0.28** | 5.7 | 179 | 36 + 22 | 36 | 1.5 | menos panes, muito mais mortos: cobrar da vida mata |

Com 5 sementes e a morte visível, a leitura do agente (n=1) inverte: **cobrar
o reboque da vida é o que mata** (0.28), e cobrar nada mata pouco (0.09) mas
devolve a pane como posto grátis (N15). Falta o braço do meio — cobrar do
tanque (3 de gordura, resto do tanque) e só da gordura — que está na fila
(onda 1c), e a âncora sem economia. A carga tributária ficou em 49–53 % da
renda bruta e a dívida quase não aparece (máx 2.5 de 60): com aluguel 6+2 o
táxi não quebra, só fica magro de dinheiro (pobre 0.08).

**Com a âncora:** a economia (aluguel 6+2, imposto ~20 % ao receber e ao
gastar, preços por distrito) custa **1.7 a 2.4 de entregas** por vida — é a
saída fixa que o Leonardo pediu, e ela pesa: carga de ~50 % da renda bruta.
Sobre a morte, a economia em si não mata: o que decide é **como o reboque
cobra** — nada (0.09) < âncora (0.19) < da vida (0.28). O braço do tanque e
o só-gordura fecham a escada (onda 1c).

### A escada do reboque (economia ligada, pena 5, R=16, 5 sementes)

Como o guincho cobra, em ordem de dureza:

| o reboque cobra… | fit | mortos | panes | o que acontece |
|---|---|---|---|---|
| nada (só −3 de vida na pane) | 6.89 | **0.09** | 9.2 | pane vira "posto grátis lento" de novo (N15): pouca morte, muita pane |
| gordura primeiro; o que faltar vira VIDA (1 por caloria) | 6.36 | 0.17 | 8.7 | ≈ âncora: a gordura paga o guincho e a vida raramente entra |
| 3× isso, resto na vida | 6.11 | 0.28 | 5.7 | menos panes, muito mais mortos: a vida paga |
| gordura primeiro; o que faltar sai do TANQUE (3×) | **−0.74** | 0.11 | 2.4 | **paralisia**: renda 4.7, posto 1.1 — o táxi para de andar pra nunca precisar do guincho |
| âncora sem economia | 8.54 | 0.19 | 7.9 | referência |

**O que aprendemos:** o reboque tem que cobrar de algo que o táxi tem e
que não seja o remédio. Cobrar do **tanque** recria a espiral (a ração do
guincho é exata) e, com a morte visível, a evolução foge da espiral do
único jeito que sabe: **parando** — é o mesmo atrator da pena com muitos
produtos e do "sempre" das fases B. Cobrar da **vida** mata. Cobrar da
**gordura** (e só dela) é o meio-termo honesto: mortalidade igual à âncora,
pane ainda custa, e dá trabalho à poupança — exatamente o que o Leonardo
pediu ("cobrar calorias"). Falta o braço padrão do agente (gordura, resto
no tanque, 1×) pra saber se a paralisia é do 3× ou de qualquer cobrança no
tanque — está na fila.

## E16 — glândulas (sem pena, R=16, 5 sementes; regime = preço do combustível oscilando por dia)

| braço | fit | mortos | fervura | hormônio (h médio) | custo em fuel/vida | ganhos evoluídos (nec · expl · metab · sono · vel) |
|---|---|---|---|---|---|---|
| Reativo | 9.62 | 0.18 | 3.7 | – | – | – |
| glândula K=2 (κ=0.25) | 9.40 | 0.17 | 3.8 | 0.06 / 0.03 | 25 | ≈ 1 (quase desligada) |
| glândula K=1 (κ=0.25) | 8.69 | 0.18 | 3.6 | 0.0004 | 13 | 1 (desligada) |
| Reativo, regime | 9.05 | 0.13 | 4.3 | – | – | – |
| glândula K=2, regime (κ=0.25) | 9.49 | 0.20 | 2.4 | 0 / 0.10 | 55 | – |
| **glândula K=2, regime, κ=0.05** | **12.30** | 0.14 | **2.2** | 0.02 / **0.98** | 70 | **2.05 · 0.54 · 0.73 · 1.58 · –** |

**O que aconteceu:** com o hormônio ao preço padrão (κ=0.25) a evolução
quase o desliga — empate. Com o hormônio barato (κ=0.05) e o preço do
combustível oscilando, a glândula **liga e fica ligada** (h ≈ 0.98, quase
constante) e o fitness sobe **+3.25 (5 de 5 sementes)**, a fervura cai pela
metade. O padrão que emergiu é coerente: dobra o peso das necessidades,
corta a exploração pela metade, reduz o metabolismo 27 %, melhora o sono
58 %. Um "modo economia".

**Por que não comemorar ainda:** o canal de metabolismo em 0.73 significa
**27 % menos combustível por passo**, pago com 0.05 de caloria por passo —
o táxi gasta ~1 a 2 de combustível por passo andando, então o hormônio
está **comprando eficiência abaixo do custo**: almoço grátis, não
inteligência (foi exatamente o alerta do agente ao recusar mexer no
`peso`). O h saturado confirma: virou um multiplicador fixo, não um
hormônio que sobe e desce. Teste decisivo (onda 1f, predição antes): o
mesmo braço com o metabolismo **proibido de ficar abaixo de 1** (eficiência
não se compra). Predição: se o ganho cair de +3.25 para ≤ +1.0, o grosso
era almoço grátis e o que sobra (necessidade ×2, exploração ×0.5, sono
×1.6) é o hormônio de verdade — ainda assim um resultado; se ficar ≥ +2.0
com 4/5 sementes, o modo economia paga por conta própria e é o maior
mecanismo do projeto. Controle extra: κ=0.05 sem regime (a glândula precisa
de um mundo que muda?).

**Braço padrão do agente (gordura primeiro, resto do tanque, 1×):** fit
**−0.49**, entregas 0.6, renda 9.8 — paralisia igual à do 3×. Não era a
escala: **qualquer cobrança no tanque** faz a população parar. O padrão do
runner passou a ser "gordura primeiro, resto na vida" (6.36 / 0.17), o único
dos cinco modos que mantém o mundo vivo E a pane custando. Escada final:

| reboque cobra… | fit | mortos |
|---|---|---|
| nada | 6.89 | 0.09 |
| **gordura → vida (padrão novo)** | **6.36** | **0.17** |
| gordura → vida, 3× | 6.11 | 0.28 |
| gordura → tanque (1× ou 3×) | −0.5 / −0.7 | paralisia |
| âncora sem economia | 8.54 | 0.19 |

### O controle "eficiência não se compra" (onda 1f)

| braço | fit | mortos | metabolismo | velocidade | leitura |
|---|---|---|---|---|---|
| κ=0.05 + regime (o +3.25) | 12.30 | 0.14 | 0.73 | – | o salto |
| **κ=0.05 + regime, metabolismo ≥ 1** | **9.02** | 0.19 | 1.00 | 0.93 | ganho SUMIU (Reativo regime: 9.05); glândulas quase desligadas |
| κ=0.05 **sem regime** | 13.05 | 0.15 | 0.74 | 0.75 | o salto nem precisava do mundo mudar |
| κ=0.25, metabolismo ≥ 1 | 8.62 | 0.23 | 1.00 | 1.01 | desligada, pior |

**Veredito:** os +3.25 eram **almoço grátis**. O canal de metabolismo podia
descer até 0.70 (30 % menos combustível por passo) e o hormônio custava
0.05 por passo — comprar eficiência abaixo do preço. Prova dupla: proibir o
desconto apaga o ganho; tirar o regime não apaga. O padrão "modo economia"
(necessidade ×2, exploração ×0.5, sono ×1.6) era o embrulho, não o
conteúdo. Predição registrada antes (doc 33, "se cair para ≤ +1.0, o grosso
era almoço grátis") ✓.

**O que fica de verdade:** (1) hormônio que mexe em PREÇO de física
(metabolismo, velocidade) tem que ser limitado a ≥ 1 ou custar mais que
economiza — senão a seleção o usa como desconto (regra 16); (2) com os canais
de decisão sozinhos (necessidade, exploração, sono) a evolução não achou
uso em G=60/R=16 — as glândulas ficaram inertes; (3) o que EMERGIU segue
válido como forma (uma glândula sobe com fome e freia; outra sobe com
abastecer e mantém), mas não paga neste mundo. Encerrado como N19.
