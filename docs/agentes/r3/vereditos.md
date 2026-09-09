# Rodada 3 — vereditos (consolidador: Fable; juiz: simulador)

| item | previu | mediu | veredito | mecanismo |
|---|---|---|---|---|
| construcao_1 (contrato certo) | mortos ≤ .5 | 1.00; anda 95 %, 6.4 ent, 3 refeições, 1 pane, fome 93/água 24/dívida −4 | ✗ | desvia demais, trabalha de menos; campeão aceita 6.8 panes e entrega 17.7 |
| construcao_2 (contrato certo) | mortos ≤ .5 | 1.00; anda 93 %, 6.5 ent, 2.6 refeições, 0.2 pane | ✗ | idem |
| lugar_1 (npx 48, contraste de demanda 4×) | quem lê demanda ganha | linear **0.74**, COMPLETO 0.79, bilinear+dem 0.80 | ✗ invertido (válido) | primeiro cenário na banda com passageiro na cidade: ler lugar CUSTA e não paga |
| lugar_2 (npx 48, outro contraste) | ≥ 10 pp | 0.83 / 0.83 / 0.83 | ✗ empate | — |
| minimo_1, minimo_2 (eixo gasolina × lugar) | — | pendente | — | — |

## Decisão do consolidador (01:30)
- **Grupo "lugar" ENCERRADO** após 3 rodadas: 6 cenários, nenhum em que ler lugar/demanda/espera pague; no único cenário válido na cidade
  o linear é o melhor. É o mesmo invariante das baterias E54–E70 (peça não paga), agora com mundos desenhados por agentes.
- **Grupo "construção" DOBRA** (4 agentes na r4/r5): é o item mais informativo — se existe política explícita ≤ 0.6, o mundo é solúvel e
  a evolução é que não acha; se não existe, o mundo base é insolúvel a 10 dias e a régua/mundo precisa mudar (decisão do Leonardo).
- **Grupo "mínimo"** vive mais uma rodada só no eixo gasolina × lugar (resultado da r3 pendente).
