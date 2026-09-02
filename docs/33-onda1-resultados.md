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
