# 27 — Corpo = carro: dano real, morte, gordura fácil, sono que come (E13, 2026-09-02)

**Leonardo:** *"Acho válido começar a realmente evoluir mais: colocar dano no
carro, dano real, fura o pneu demora mais, motor aquecido o carro desliga, o
reboque custa mais, pra que os seres realmente tentem deixar o carro o mais
vivo possível porque é o corpo deles. E mais gordura, ela entra mais fácil,
porque dormir e melhorar o cérebro custa caloria — deixar pro outro dia como
gordura às vezes não compensa."*

## 1. O que muda (tudo atrás de `cfg.corpo`, zero sem a flag — portão bit-exato)

| peça | antes (avaria = parada) | agora (avaria = FERIDA) |
|---|---|---|
| vida | não existia | 0–100, feature `e_dano = 1 − vida/100` |
| pane seca | 18 passos, reboque 12 | 18 passos, reboque **20**, **−6 vida** |
| furo | 15 passos, pneu→60 | **30 passos**, pneu→**40**, **−5 vida** |
| óleo | 22 passos | 22 passos, **−12 vida** |
| motor >92 °C | 14 passos, temp→40 | **desliga 20 passos**, temp fica 92 e esfria sozinho (1.6/passo), **−10 vida** |
| rodar machucado | nada | pneu<30 ou temp>80 ou óleo<20 andando: **−0.15/passo** |
| ferido | nada | tempo de viagem e consumo × (1 + 0.6·dano) |
| oficina | pneu/óleo/temp | + **vida +30** (mesmo preço 10) |
| morte | não existia | vida ≤ 0: para de entregar, para de agir |
| gordura fácil | só sobra da meia-noite | `reserva_posto`: posto também põe 20 na reserva |
| sono come | descanso grátis | `sono_come`: cada descanso custa 5 de fuel (tanque, depois gordura com perda) |

Mundo-base: o mundo honesto do E12-v8 (fuel×0.5, reboque, noite 22–6h).

## 2. Por quê assim

- **Morte é a seleção de verdade.** Até aqui o ser "sobrevivia" por definição:
  pane, furo e fervura eram paradas, não feridas. Agora o corpo acumula e o
  ser que não cuida DEIXA de existir — fitness congela. É a primeira vez que
  "deixar o carro vivo" vale mais que "entregar mais".
- **O motor quente desliga**: não é multa, é física — o carro para até esfriar.
- **Gordura entra fácil pela lei do E12** (doc 26 §7.2): com entrada só da
  meia-noite, I=10 ≪ f·S=45 e a reserva não paga; com o posto enchendo a
  reserva, I≈54 ≥ f·S e o regime vira "teto = buraco".
- **Sono que come** fecha o trade-off que o Leonardo descreveu: a caloria da
  noite vai pra recuperar/aprender OU pra gordura. Quem dorme muito engorda
  menos.

## 3. Teto medido antes (regra 1)

Perito (mesmo genoma à mão) no mundo corpo: **86% morrem em 5 dias**, vida
média no fim 9.7, dano 137 = fervura 81 + panes 44 + furos 7 + rodar 6. O
mundo é letal pra quem não muda de comportamento. Predições 14–18 em
PREDICOES.md §E13.
