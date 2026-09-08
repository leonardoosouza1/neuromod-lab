# O mundo não é viável a 15 dias — e não é o guincho

Medido em 2026-09-08, oráculo (política escrita à mão, sem genes), mundo distinto
L=200, 15 dias, 64 cópias, variante `poup_oport`. Régua da casa, escrita no próprio
`oraculo_campo.py`: *"se o oráculo também morre, o mundo é duro demais e tem de ser
recalibrado ANTES de qualquer arquitetura."*

## O oráculo morre — e as duas alavancas óbvias não salvam

| guincho | dinh0 | mortos | entregas (15 d) |
|---|---|---|---|
| 10 | 10 | 1.00 | 6.0 |
| 0 | 10 | 1.00 | 6.1 |
| 10 | 40 | 1.00 | 7.7 |
| 0 | 40 | 1.00 | 7.9 |

Também morrem as variantes `base` (5.6 entregas) e `poupador` (5.1) na célula
guincho 10 / dinh0 10. **Recalibrar o guincho de 10 para 4 não resolve** — e seria
subsídio, o negativo N15 (subsídio vira renda).

## Por que morre: a esteira das necessidades, não a pane

Orçamento de dano do oráculo (célula guincho 10 / dinh0 10):

| canal | dano |
|---|---|
| **fome** | **56.8** |
| dívida | 521 ticks em dívida |
| calor | 11.1 |
| pane | 7.3–16.9 (só **1.2 panes** em 15 dias) |
| sede | 0.3 |
| total | 109.4 |

E o tempo: o oráculo fica **62 % do tempo travado em comida e 33 % em posto** — 95 %
do tempo de alvo em necessidade, ~5 % trabalhando — e anda só **31–40 %** do tempo.

## A conta de renda fecha; a de tempo não

Medido de `campo.py` (4096 amostras do próprio mundo):

- passageiro → destino: média **35.4 m** (quartis 14 / 28 / 52); buscar o mais perto: **10.1 m**
- tarifa líquida por entrega **9.02**, gasolina **2.04** (45 passos) → **líquido +6.97**
- custo fixo **5.55/dia** (aluguel 4 + comida 1.54 + água 0.01)
- teto geométrico: 240 ticks / 45 passos = **5.3 entregas/dia** → +31/dia no teto

Uma entrega por dia pagaria a conta. O oráculo faz **0.37/dia**. O gargalo é
`fome_passo = 0.32/tick` = **77 de fome por dia** (dia de 240 ticks): a esteira
consome o dia útil antes de a economia poder fechar.

## Próxima calibração (unidimensional, sem evolução)

Varrer `fome_passo` — ou o valor da refeição — até o oráculo viver 15 dias com
margem, e só então comparar arquiteturas. Critério: `vivos ≥ 0.5` **e**
`entregas ≥ 15` (senão é pedra). Seis células de oráculo, sem evolução.

**Só depois disso** a escada de névoa (E63) mede cérebro em vez de teto de mundo:
com `mortos` em 0.99–1.00 em todos os braços (E62 15 d, e também guincho4_bem10
0.93/0.94 e guincho4_riqueza10 0.95/0.96), nenhuma diferença entre arquiteturas é
observável — é o degrau do N14.

## Ressalvas

64 cópias, uma variante nas células da grade, `mortos` no teto em todas — dá para
afirmar que nenhuma das duas alavancas sai do teto; não dá para ordená-las entre si.
Os números de tempo e dano são do oráculo, não de um ser evoluído.
