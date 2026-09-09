## 1) O que ainda mata

```tarefa
BASE = L3 p7 (0.66). UMA alavanca por politica; resto de p7 intacto. Prever mortos/corridas/refeicoes ANTES.
MEDIDO: p7 morre 50% fome / 48% dano. Campeao faz 41% das refeicoes entre 22h-5h (706/1734); p7 faz 7.4% (152/2047) e empilha 42% delas entre 6h-11h — passa a noite com fome e come quando o posto abre. Posto fecha 22h-6h (0 abastecidas nessa faixa nos dois). Pane sempre com tanque ~0.2 L, mediana 24.8 u do posto, p90 63.6 u.
A1 COMIDA NOTURNA FORTE: 22h-6h comer em ponto de comida com fome>35 (hoje dispara so em ~70); de dia nao comer com fome<30.
A2 PRE-NOITE: 19h-22h, se fome>25 ou tanque<40 L, ir ao servico mais perto — so sem passageiro; depois das 22h nunca desviar pra posto.
A3 PANE LONGE: pane continua transporte barato se dist_posto<25 u; se tanque<10 L E dist_posto>40 u, ir ao posto (nunca com passageiro).
A4 LITROS x CAIXA: no posto antes das 21h comprar 100 L se dinheiro>60, senao 50 L; nunca 100 L com dinheiro<40 (H7 quebrou assim).
A5 REFEICAO CARA: bloquear comer com fome<30 (p7 come com p10=21.1; campeao p10=38.4) e gastar o tick em corrida.
A6 AGUA MAGRA: beber so com agua<45 (p7 bebe em 54.9) e comprar agua sempre DEPOIS da comida.
A7 SAIR DO RAIO: p7 fica 42.8% do tempo livre dentro do raio de servico vs 26.2% do campeao — apos concluir as compras, alvo volta a ser passageiro.
A8 LIVRE: empilhar A1+A3 com limiares proprios, justificados por numero do campeao.
```

```hipoteses
| H16 | AGUA: beber/comprar mais cedo | ✓ 0.71 mas sede era so 7% das mortes — ganho veio de menos paradas, nao de sede | L3 p2 |
| H17 | REPARO mais cedo/mais barato (2o teste) | ✗ 0.82: reparo come caixa e ticks, corridas caem 16.4 → 12.7 | L1 p3, L3 p3 |
| H18 | GASOLINA: mais litros por parada | ✓ 0.73 (empata com a base) — menos paradas nao basta sozinho | L3 p4 |
| H19 | ORDEM das compras + ticks parado no posto (2o teste) | ✗ 0.99: uma acao por tick vira fila, 7.1 corridas | L3 p5 |
| H20 | NOITE = descansar/parar de rodar | ✗ 0.88: corta renda e nao evita fome (fome vira 73% das mortes) | L3 p6 |
| H21 | LIVRE: comida noturna + nao desviar com passageiro | ✓ 0.68, 2o melhor da serie | L3 p8 |
| H22 | limiar de fome baixo de DIA (3o teste) | ✗ 0.73: refeicoes sobem 7.3 → 8.2 e mortos nao cai — comer de dia nao cobre 22h-6h | L3 p1 |
```

Alavanca com mais chance é comida noturna, e o número é grande: o campeão tira 41% das refeições entre 22h e 5h, a explícita tira 7.4% — e ainda despeja 42% das refeições dela entre 6h e 11h, ou seja, sobrevive à noite com fome e só repõe quando o posto abre. H13 e H15 já colocaram "comer à noite", mas os dados provam que a cláusula quase não dispara (152 refeições noturnas em 2047): o limiar herdado (~70 de fome) chega tarde demais para a fome que se acumula em 8 horas sem posto. Baixar para 35 à noite e bloquear refeição barata de dia (<30) é a mesma quantidade de comida, redistribuída — deve levar fome de 50% para ~30% das mortes e mortos de 0.66 para ~0.58. A segunda alavanca é dano, e ali reparar mais já falhou duas vezes (0.84 e 0.82): o caminho é a fonte, não o conserto — pane acontece com 0.2 L e mediana 24.8 u do posto, mas o p90 é 63.6 u; pane perto é transporte barato (H2/H3), pane a 60 u é hora parada acumulando fome e dano. Restringir pane por DISTÂNCIA, não por precaução global, é o que separa A3 de H1 (que paralisou o táxi com desvio incondicional). Água (7% das mortes) e reparo estão saturados — só entram como variação magra para liberar caixa e ticks.