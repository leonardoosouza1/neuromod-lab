# Rodada 1 — vereditos (consolidador: Fable, sessão principal; juiz: simulador via nmd)

## Referência da rodada: E70 cidade (q16, protocolo cheio)
```
=== metrica=mortos  ref=linear  n=5 ===
linear                                       0.930    0.020
COMPLETO (talamo+cortex+hipocampo+reflexo+livre)   0.905    0.039   -0.025 [ -0.067, +0.018]   0.181
bilinear risco (esc 3)                       0.951    0.028   +0.022 [ +0.009, +0.035]   0.0100
bilinear risco+demanda+espera (esc 1)        0.921    0.026   -0.009 [ -0.064, +0.047]   0.6819
linear @ passageiro perto (q13b)                         0.825    0.030   -0.104 [ -0.156, -0.052]  
=== metrica=ent  ref=linear  n=5 ===
linear                                      11.403    0.824
COMPLETO (talamo+cortex+hipocampo+reflexo+livre)  12.246    1.209   +0.843 [ -0.595, +2.281]   0.178
bilinear risco (esc 3)                      10.361    0.880   -1.042 [ -1.232, -0.852]   0.0001  BIM
bilinear risco+demanda+espera (esc 1)        9.719    0.772   -1.684 [ -3.029, -0.340]   0.0254  BIM
linear @ passageiro perto (q13b)                        18.093    0.418   +6.689 [ +5.402, +7.977]  
=== metrica=dinh  ref=linear  n=5 ===
linear                                      10.700    2.332
COMPLETO (talamo+cortex+hipocampo+reflexo+livre)  10.886    1.776   +0.186 [ -0.725, +1.096]   0.601
bilinear risco (esc 3)                      10.773    2.052   +0.072 [ -5.072, +5.217]   0.9707  BIM
bilinear risco+demanda+espera (esc 1)       11.002    3.420   +0.302 [ -6.443, +7.047]   0.9071  BIM
linear @ passageiro perto (q13b)                        26.494    7.134  +15.794 [ +5.077,+26.511]  
```
Piso: com 12 passageiros na cidade toda, todo mundo morre 0.91–0.95. Lugar passou a ter preço, ninguém consegue pagar.

| item | previu | mediu | veredito | mecanismo |
|---|---|---|---|---|
| construcao_1 (política) | mortos .30–.40, 10–15 ent | **1.00**, 3.7 ent, fome_fim 100, panes .2 | ✗ | estacionou, nunca comprou comida (refeições 0); previsão ignorou que comida só existe em alguns distritos e que o passageiro está longe |
| construcao_2 (política) | mortos .35–.45, 10–14 ent | **1.00**, 1.8 ent, fome_fim 100 | ✗ | idem |
| lugar_1 (cenário ímã) | linear ≥ .60, ent ≤ 8 | linear 1.00/3.8 ent; COMPLETO (talamo+cor 1.00/3.6 ent; bilinear risco (esc  1.00/3.2 ent; bilinear risco+deman 1.00/2.9 ent | ✗ (escala) | escassez total (npx 5, respawn 80, periferia .05) = letal para todos; régua crava |
| lugar_2, minimo_1, minimo_2 | — | pendente | — | — |

## Ajustes para a rodada 2 (feitos)
1. Contrato: **banda do controle** — linear entre 0.40 e 0.80 ou o cenário é inválido; tabela de calibração medida vai no prompt.
2. Juiz de política ganha AUTÓPSIA (refeições, abastecidas, fome/água/dinheiro no fim) para o agente ver o mecanismo, não só o número.
3. Tarefas r2 (`grupos_r2.json`): lugar → calibrar densidade (npx 20–40) e usar CONTRASTE de demanda, não escassez; construcao → 3 camadas
   (emergência / oportunismo no posto-loja / trabalho) e "vá buscar, não pare"; minimo → achar a densidade mínima em que o linear volta a 0.5–0.7.
## O que não repetir
Escassez total; predição sem olhar a tabela de calibração; política que espera o serviço "aparecer" (o táxi tem de ir).
