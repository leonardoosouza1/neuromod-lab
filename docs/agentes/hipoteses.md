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

| H16 | AGUA: beber/comprar mais cedo | ✓ 0.71 mas sede era so 7% das mortes — ganho veio de menos paradas, nao de sede | L3 p2 |
| H17 | REPARO mais cedo/mais barato (2o teste) | ✗ 0.82: reparo come caixa e ticks, corridas caem 16.4 → 12.7 | L1 p3, L3 p3 |
| H18 | GASOLINA: mais litros por parada | ✓ 0.73 (empata com a base) — menos paradas nao basta sozinho | L3 p4 |
| H19 | ORDEM das compras + ticks parado no posto (2o teste) | ✗ 0.99: uma acao por tick vira fila, 7.1 corridas | L3 p5 |
| H20 | NOITE = descansar/parar de rodar | ✗ 0.88: corta renda e nao evita fome (fome vira 73% das mortes) | L3 p6 |
| H21 | LIVRE: comida noturna + nao desviar com passageiro | ✓ 0.68, 2o melhor da serie | L3 p8 |
| H22 | limiar de fome baixo de DIA (3o teste) | ✗ 0.73: refeicoes sobem 7.3 → 8.2 e mortos nao cai — comer de dia nao cobre 22h-6h | L3 p1 |
| H16 | ÁGUA: comprar menos/na hora certa sobre a base p7 | ✓ 0.66 → 0.62 (5 s 0.63): sede sobe para 19 % das mortes mas fome/dano caem; renda 172 | L4 p2 |
| H17 | (bug) parser pegava o maior bloco python: em respostas sujas pelo hook, era o código-base ecoado → 6/8 do lote 4 idênticos à base | corrigido: último bloco + recusa 'igual à base' | L4 |
| H18 | GASOLINA: paradas mais frequentes com menos litros (abast 11.4 vs 8) sobre L4 p2 | ✓ 0.62 → 0.57 (5 s 0.58): o agente previu empate (0.65–0.68) e errou para MELHOR | L5 p4 |
| H19 | (bug do laço) relançamento usava tarefa_L1 e lote 6 rodou com tarefa vazia (fallback para arquivo inexistente) | corrigido: tarefa mais recente existente | L5–L6 |
