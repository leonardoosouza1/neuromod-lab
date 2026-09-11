# 89 — Portão de mundo: o piso do prêmio nos quatro mundos

Regra (CS docs/87 prop. 3, adotada como portão 11/09): cenário só ganha bateria se o prêmio acima de "ficar parado" for maior que 2× o ruído entre sementes. Medido com `julga_politica --politica parada.py` (3 mapas × 128 cópias × 5 sementes), campeão linear como referência; ruído = DP/média do fit do braço linear na bateria de 5 sementes.

| mundo | campeão (d) | parada (d) | prêmio (dias) | prêmio (fit = dias + renda/300) | ruído | veredito |
|---|---|---|---|---|---|---|
| A (`mundoA_seres`) | 3.865 | 3.664 | 5.2 % | 13 % | 8.7 % | **recusado** (prêmio < 2×ruído) |
| B (A + lei do B) | 3.865 | 3.664 | 5.2 % | 13 % | 8.7 % | **recusado** |
| C (`mundoC_cidade_da_vida`) | 5.088 | 3.667 | 27.9 % | 36 % | 9.6 % | passa |
| D (C + olho 27 m) | 5.14 | 3.67 | 28.6 % | 37 % | 8.5 % | passa |

Fontes: `e85/julga_parada_{A,B,C,D}.json`, `e79/e43_mundo{A5,B5,C5}.json`, `e87/e43_mundoD5.json`. O campeão COMPLETO fica ABAIXO da parada em A (3.39 d vs 3.66 d; `docs/88` adendo) — o cérebro que paga metabolismo 1.74 perde para quem não faz nada.

Consequência: todas as baterias de A/B mediram ruído; o programa da tese continua em C (ou D, equivalente). Bateria final da tese (plano META Parte 2.3): C, n = 8, depois de corte/paciência por população.
