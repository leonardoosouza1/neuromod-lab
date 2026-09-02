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

## E15 — economia real (pena 5, R=16) — parcial, falta a âncora "sem economia"

| mundo | fit | mortos | panes | renda bruta | imposto (receber+gastar) | aluguel+água | dívida máx | leitura |
|---|---|---|---|---|---|---|---|---|
| economia, reboque sem custo calórico (só −3 de vida) | 6.89 | **0.09** | 9.2 | 220 | 44 + 25 | 39 | 2.5 | menos mortos de toda a linha; mas pane volta a ser "posto grátis" (9.2/vida) |
| economia, reboque cobra 3 de gordura e o resto da VIDA | 6.11 | **0.28** | 5.7 | 179 | 36 + 22 | 36 | 1.5 | menos panes, muito mais mortos: cobrar da vida mata |

Com 5 sementes e a morte visível, a leitura do agente (n=1) inverte: **cobrar
o reboque da vida é o que mata** (0.28), e cobrar nada mata pouco (0.09) mas
devolve a pane como posto grátis (N15). Falta o braço do meio — cobrar do
tanque (3 de gordura, resto do tanque) e só da gordura — que está na fila
(onda 1c), e a âncora sem economia. A carga tributária ficou em 49–53 % da
renda bruta e a dívida quase não aparece (máx 2.5 de 60): com aluguel 6+2 o
táxi não quebra, só fica magro de dinheiro (pobre 0.08).
