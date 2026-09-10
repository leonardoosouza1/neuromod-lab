# 86 — O piso do prêmio: parado leva 87 % do campeão (Mundo A) — 10/09 20:05

Controle pedido pelo CS (docs/78 §4) e pelo Astra (plano, passo 1): uma política que **só fica parada** (`politicas/parada.py`, ação 8 sempre), julgada no mundo de cada cenário com 128 cópias × 5 sementes, contra o campeão linear do mesmo mundo (W da semente 0). Fit da régua vida ≈ dia da morte + renda/300.

| mundo | parado: dia, renda, fit | campeão linear: dia, renda, fit | parado/campeão |
|---|---|---|---|
| A | 3.66, 0, **3.66** (100 % fome) | 3.87, 98, **4.19** (78 % dano, 5.2 panes, $ −19) | **.87** |
| B | idem A (o linear não paga conta de cérebro: campeão bit a bit igual) | idem | .87 |
| C | 3.67, 0, **3.67** | 5.09, 196, **5.74** (18 % vivos no dia 10, $ +17) | **.64** |

## O que isso diz
1. **O prêmio tem piso alto.** Em A, não fazer nada vale 87 % do melhor genoma que 30 gerações acharam. A evolução disputa os 13 % de cima; os cérebros perdem ~20 % desse pedaço para a espinha — a "lacuna" de .86 d é grande dentro da faixa que se disputa, pequena dentro do fit.
2. **A é armadilha de dívida.** O campeão trabalha (11 entregas, renda 98) e termina com −19: aluguel 4/d + guincho 10 por pane (5.2 panes) > renda. Ele vive 0.2 d a mais que o parado porque come 4 vezes, e morre de dano (78 %). Nada que o cérebro faça em A escapa disso — o que explica por que "mais gerações compram genes, não aptidão" (pred 177).
3. **C escapa do piso** (.64): renda 196, dinheiro positivo, 18 % chegam ao dia 10. É o mundo onde a régua discrimina — e onde a lacuna espinha–cérebro é a maior (2.32). Ou seja: quando o prêmio passa a distinguir, quem se distingue é a espinha.
4. **O FICAR é carga, não vício** — mas o teste que ia provar isso (campeão sem a opção FICAR) saiu inválido: `julga_politica` mede políticas com W = zeros, então o `tudo` do `decidir` não era a nota do campeão; a coluna 8 apagada virou "direção 0 sempre" (anda reto, seca o tanque, guincho, sem dinheiro, morre no dia 1.46). Refeito como `o3g_julga_semficar_{A,C}` com o W do campeão. Checklist item 13.

## Propostas (para Leonardo/CS decidirem; nada disso está na fila)
- **Controle padrão**: todo mundo novo registra `piso_parado` (uma chamada de `julga_politica parada`, segundos) e os resultados passam a reportar `fit − piso`. Não muda seleção (constante), muda a leitura.
- **Régua**: uma constante não muda o argmax; o que muda é o PESO da renda. Hoje `w_trab` = 1 → renda/300 ≈ .33 de 4.19 (8 % do fit). Candidato a Mundo E: `w_trab` 3 (renda vira ~20 % do fit) — predição a registrar antes: a lacuna espinha–COMPLETO em A cresce (a espinha entrega mais por dia) e o parado cai para ≤ .75.
- **Economia**: o piso alto de A vem do mundo matar todo mundo em ~4 d por dívida+dano. Uma lei só (ex.: guincho 10 → 0 com pane custando calorias, como no v1) tiraria a armadilha; mas isso é o Mundo A' e compete com o D do Opus. Escolha do Leonardo.
