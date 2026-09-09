# Dados tick a tick (gerados por dados_campeao.py) — o que o campeao evoluido FAZ, medido, nao imaginado

## CAMPEAO evoluido (linear q8, semente 0): mortos 0.88, vida media 5.8 dias, 17.9 corridas, 6.0 refeicoes, 4.3 abastecidas, 6.6 panes, 1.4 oficinas (B=96, 3 mapas de teste)
- ABASTECE quando o tanque esta em: mediana 15.0 (p10 13.8, p90 95.5, n=1237) L (de 100); com dinheiro mediana 37.1 (p10 18.0, p90 71.6, n=1237); compra mediana 100.0 (p10 100.0, p90 100.0, n=1237) L; a mediana 1.0 (p10 0.0, p90 5.7, n=1237) u do posto no tick anterior
- COME quando a fome esta em: mediana 63.7 (p10 38.4, p90 100.0, n=1734) (de 100; morre a 90+)
- BEBE quando a agua esta em: mediana 54.5 (p10 31.2, p90 68.4, n=1266) (de 100; morre abaixo de 10)
- PANE acontece com tanque mediana 0.2 (p10 0.0, p90 0.5, n=1899) L e a mediana 25.9 (p10 12.4, p90 61.4, n=1899) u do posto mais perto
- OFICINA com vida mediana 42.2 (p10 15.7, p90 64.4, n=394)
- Intervalo entre corridas entregues: mediana 57.0 (p10 14.0, p90 139.0, n=5145) ticks (1 tick = 6 min)
- Tempo LIVRE (sem passageiro, nao preso) dentro do raio de algum servico: 26.2 %
- Por hora do dia (0-23): movimentos | abastecidas | refeicoes | corridas: 0:15240/0/83/181 1:16083/0/71/158 2:16127/0/70/187 3:16119/0/85/173 4:15992/0/72/164 5:15839/0/103/150 6:15258/119/46/233 7:15054/98/57/240 8:14831/83/51/232 9:15477/103/67/211 10:15515/80/56/260 11:15502/85/60/255 12:15478/61/58/251 13:15258/58/61/245 14:15090/65/73/247 15:15062/79/64/249 16:14822/56/62/229 17:14606/80/78/229 18:15524/83/72/236 19:15399/60/74/238 20:15243/56/73/236 21:15158/71/76/208 22:14858/0/125/164 23:15064/0/97/169

## POLITICA campeao_explicito_r7_1.py: mortos 0.74, vida media 6.8 dias, 16.3 corridas, 7.1 refeicoes, 7.5 abastecidas, 7.1 panes, 1.9 oficinas (B=96, 3 mapas de teste)
- ABASTECE quando o tanque esta em: mediana 35.3 (p10 14.9, p90 88.2, n=2154) L (de 100); com dinheiro mediana 20.8 (p10 7.4, p90 47.0, n=2154); compra mediana 50.0 (p10 25.0, p90 100.0, n=2154) L; a mediana 0.0 (p10 0.0, p90 5.8, n=2154) u do posto no tick anterior
- COME quando a fome esta em: mediana 70.1 (p10 21.1, p90 85.3, n=2047) (de 100; morre a 90+)
- BEBE quando a agua esta em: mediana 54.9 (p10 38.4, p90 75.2, n=1270) (de 100; morre abaixo de 10)
- PANE acontece com tanque mediana 0.2 (p10 0.0, p90 0.5, n=2042) L e a mediana 24.8 (p10 11.4, p90 63.6, n=2042) u do posto mais perto
- OFICINA com vida mediana 47.9 (p10 30.7, p90 72.6, n=560)
- Intervalo entre corridas entregues: mediana 61.0 (p10 14.0, p90 182.7, n=4694) ticks (1 tick = 6 min)
- Tempo LIVRE (sem passageiro, nao preso) dentro do raio de algum servico: 42.8 %
- Por hora do dia (0-23): movimentos | abastecidas | refeicoes | corridas: 0:17161/0/79/151 1:18012/0/9/154 2:17572/0/7/166 3:17117/0/4/167 4:16703/0/2/169 5:16269/0/5/142 6:13556/287/224/197 7:13449/168/111/198 8:13188/172/177/190 9:14042/152/114/194 10:14115/143/122/224 11:14192/144/119/208 12:14080/91/100/240 13:13963/124/108/198 14:14098/119/105/201 15:13985/111/88/208 16:13693/113/114/212 17:13686/108/132/214 18:15074/116/100/220 19:15162/103/93/247 20:15276/119/106/242 21:15185/84/82/218 22:16621/0/24/161 23:16757/0/22/173
