# Hipóteses já testadas (não repetir) — atualizado pelo consolidador
| # | hipótese | resultado | onde |
|---|---|---|---|
| H1 | ir ao posto por precaução (autonomia < .3) evita morte | ✗ morre de fome no dia 3: desvio demais, 6 corridas em vez de 17 | r3, r4 |
| H2 | evitar pane a todo custo | ✗ o campeão tem 6.8 panes/vida e vive mais: pane + guincho (15 L) é transporte barato ao posto | r5 |
| H3 | política que nunca vai ao posto por vontade e compra tudo lá (pane como transporte) | ✓ chega ao modo de morte do campeão (dano), 13.7 corridas | r5 |
| H4 | + reparo na oficina quando vida < .5 | ✓ 0.76 (bate o campeão 0.85); o campeão TAMBÉM repara (1,5 oficinas/vida, medido 09/09) | r6 |
| H5 | + comer mais no posto (fome > .15) e comida perto | ✓ 0.73 | r7 |
| H6 | tirar o 'ficar' (23 % das escolhas) | ✗ 0.88: o 'ficar' era no raio do serviço, completando compras (uma ação por tick) | r8 |
| H7 | abastecer 100 L sempre que no posto com dinheiro > 40 | ✗ 0.80: come o dinheiro do reparo/comida | r6_2 |
| H8 | reparo só com caixa > 25 | ✗ 0.90 (junto com H6) | r8_2 |
| H9 | densidade de passageiro na cidade muda mortalidade | ✗ npx 24/36/48 → 0.82/0.81/0.78 | q17 |
| H10 | ler lugar/demanda/espera paga (cérebro em camadas) | ✗ em 10 cenários; no válido da cidade o linear é o melhor | r1–r3 |
| H11 | penalizar sair da rua (custo_frente) ao escolher direção | ✗ 0.99: paralisa o táxi (1.7 corridas) — a penalidade domina a distância ao alvo | L1 p7 |
| H12 | comer mais no posto (limiar de fome mais baixo) sem mudar onde come | ✗ 0.78, fome 74 % das mortes: o posto fecha à noite; comer mais de dia não cobre a noite | L1 p1 |
| H13 | comer à noite em pontos de comida (posto fecha) | ✓ leve: 0.74 → 0.72 (5 sementes), fome ainda 47 % das mortes | L2 p6 |
| H14 | lote 2: 6/8 respostas sem bloco ```python → recusadas | bug de formato do orquestrador (parser agora aceita ```py / ``` com def fabrica) | L2 |
| H15 | rua como DESEMPATE (peso .15 em custo_frente, não 5.0) + comida à noite em ponto de comida + nunca desviar com passageiro a bordo + comida antes de água no posto | ✓ 0.66 (3 sementes): melhor da série; o agente calibrou o peso pelos dados do L1 p7 (que paralisou com peso 5) | L3 p7 |
