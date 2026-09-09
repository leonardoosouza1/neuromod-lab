# Laço v2 — resumo por lote (juiz: simulador, 3 sementes; melhor confirmado em 5 sementes quando indicado)

| lote | políticas | melhor (3 s) | alavanca do melhor | 5 s | corridas/dia | causa de morte |
|---|---|---|---|---|---|---|
| L1 | 8 | **0.74** (p5) | ORDEM das compras no posto e quantos t | 0.7302083611488343 | 0.00 | fome 50 % / dano 48 % |
| L2 | 2 | **0.73** (p6) | NOITE: descanso/fadiga (hoje ignorado) | 0.7151041865348816 | 0.00 | fome 46 % / dano 53 % |
| L3 | 8 | **0.66** (p7) | RUA: penalizar sair da rua (custo_fren | 0.646875011920929 | 0.00 | fome 50 % / dano 48 % |
| L4 | 8 | **0.62** (p2) | AGUA: quando e quanto comprar | 0.634375 | 0.00 | fome 49 % / dano 45 % |
| L5 | 5 | **0.57** (p4) | GASOLINA: quantos litros por parada co | 0.584375011920929 | 0.00 | fome 48 % / dano 47 % |
| L6 | 8 | **0.56** (p4) | GASOLINA: quantos litros por parada co | 0.5703125238418579 | 0.00 | fome 47 % / dano 48 % |
| L7 | 8 | **0.56** (p6) | NOITE: descanso/fadiga (hoje ignorado) | 0.5723958492279053 | 0.00 | fome 47 % / dano 48 % |
| L8 | 8 | **0.57** (p7) | RUA: penalizar sair da rua (custo_fren | 0.5708333492279053 | 0.00 | fome 46 % / dano 48 % |
| L9 | 8 | **0.56** (p6) | NOITE: descanso/fadiga (hoje ignorado) | 0.5697916865348815 | 0.00 | fome 47 % / dano 48 % |
| L10 | 8 | **0.56** (p2) | AGUA: quando e quanto comprar | 0.565625011920929 | 2.48 | fome 47 % / dano 45 % |
| L11 | 7 | **0.56** (p3) | TRABALHO/LUGAR: quando LIVRE (sem pass | 0.5932291865348815 | 2.47 | fome 46 % / dano 46 % |
| L12 | 8 | **0.53** (p8) | LIVRE: qualquer coisa que os dados do  | 0.5536458492279053 | 2.38 | fome 51 % / dano 39 % |
| L13 | 7 | **0.53** (p7) | RUA: penalizar sair da rua (custo_fren | 0.5536458492279053 | 2.38 | fome 51 % / dano 39 % |
| L14 | 8 | **0.52** (p7) | RUA: penalizar sair da rua (custo_fren | 0.4958333432674408 | 2.32 | fome 49 % / dano 40 % |
| L15 | 8 | **0.49** (p8) | LIVRE: qualquer coisa que os dados do  | 0.4875000059604645 | 2.33 | fome 51 % / dano 38 % |
| L16 | 8 | **0.49** (p2) | AGUA: quando e quanto comprar | 0.4958333492279053 | 2.33 | fome 51 % / dano 39 % |

Total: 117 políticas julgadas em 16 lotes; evolução (campeão linear) = 0.85; teto explícito = 0.49 (L15 p8). Cadeia de ganhos: r5–r7 (pane como transporte, reparo, comida à noite) → L3 rua .15 → L4 água → L5/L6 litros → L12 esfriar → L14 rua .30 → L15 reserva. Refutadas: parada mínima (3×), custo_frente forte, top-up voluntário, reparo tardio, lugar/preço (2 sentidos), densidade de passageiro.

Erros do consolidador pagos: contrato de ações de memória (r1–r2), `s`=self no contrato (r3), parser do maior bloco (L4), hook do claude-mem (L2–L5), tarefa antiga no relançamento (L6), leitura do "ficar" (r8).
