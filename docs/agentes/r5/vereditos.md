# Rodada 5 — vereditos (construção: política literal do campeão)

| item | previu | mediu | veredito | mecanismo |
|---|---|---|---|---|
| construcao_1 | ≤ .7 | crash (tensor CPU vs cuda) | — | juiz agora fixa o device padrão |
| construcao_2 | ≤ .7, ≥ 3 corridas/dia | **1.00**, mas 13.7 ent, renda 127, 3.7 refeições, 5.3 abastecidas, 3.7 panes; morre dia 4.1 por DANO 76 % | ✗ com progresso | reproduz o modo de morte do campeão (dano), sem sobreviventes; deixou de morrer de fome |

Leitura: a regra "pane como transporte + compra tudo no posto" fecha a fome. O que sobra é dano acumulado de pane/calor — reparável na
oficina por 10 (nem o campeão repara). r6 = esta política + reparo (pred 120, aposta ✓ 0.60–0.75).
