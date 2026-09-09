# Rodada 6 — ACHADO: a primeira política explícita que bate a evolução

| item | previu | mediu | veredito |
|---|---|---|---|
| construcao_1 (r5_2 + reparo na oficina) | ≤ .7 | **0.76** [0.779, 0.773, 0.745, 0.747, 0.734] vs campeão 0.85 [0.87, 0.818, 0.875, 0.836, 0.828]; 18.2 ent; renda 168; 6 refeições; 8.1 abastecidas; 7.9 panes; dia 5.3 (fome 50 %, dano 50 %) | ✓ parcial: bate o campeão em 5/5 sementes (−9 pp), não chegou a ≤ .70 |
| construcao_2 (+ 100 L no posto) | ≤ .7 | 0.80 (−4 pp), 17.9 ent | ✗ parcial: abastecer 100 L come o dinheiro do reparo/comida |

Cópia estável da política vencedora: `src/politicas/campeao_explicito_r6_1.py` (juiz: `julga_politica.py --politica ...`).
Caminho até aqui (6 rodadas): r1–r2 morreram por erro MEU de contrato; r3 (contrato certo) morreu de fome por desviar demais; r4 idem;
r5 (literal do campeão: pane como transporte) chegou ao modo de morte do campeão; r6 (+ reparo) passou o campeão.
O que isso diz: o mundo base É solúvel abaixo de 0.85 — a evolução (300 gerações, 4 otimizadores) não achou o que existe.
