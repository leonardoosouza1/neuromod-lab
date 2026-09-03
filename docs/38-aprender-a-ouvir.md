# 38 — E22: o cérebro aprende a ouvir EM VIDA (plasticidade gateada por recompensa)

O E20 mostrou que hormônio + receptor herdados funcionam, e que o receptor
não nasce por seleção em 40 gerações. A biologia tem outro caminho, que a
linha de Najarro & Risi (regras hebbianas evoluídas, 2020) e o nosso
cérebro-por-órgãos (dopamina como portão de plasticidade) já usaram: **o
receptor se ajusta durante a vida**, guiado por um sinal de recompensa.

## Desenho (arquivo novo, sem tocar no `lab.py`)
- Corpo: as glândulas do E20 com código herdado só do lado do corpo (h0 =
  fome, h1 = sede), τ rápido.
- Cérebro: `Gserv` (K×5, hormônio → serviço) começa em ZERO e muda em vida:
  `ΔG[k,p] = η · h_k · [usou o serviço p] · r`, onde `r` = recompensa do
  passo (entregou +1, comeu/abasteceu +0.5 se a necessidade caiu, pane −1,
  dano −0.1·Δvida). Gene: η (taxa) e um decaimento. Tudo em `atualizar()`
  (in-place, fora do grafo).
- Controles: η=0 (surdo, = E20 "corpo nasce falando"), código herdado dos
  dois lados (teto), plasticidade sem gate (r=1 sempre: Hebb puro).

## Predições (antes de rodar; triagem)
13. Com η > 0 e gate por recompensa, o cérebro surdo passa a comer: mortos
    ≤ 0.70 e fome no fim < 90 (E20: 0.89–0.93 / 97–100); com η evoluída,
    ≥ 2/3 sementes escolhem η > 0.
14. Hebb puro (sem gate) NÃO aprende o certo (mortos ≈ surdo): sem a
    recompensa, "fome alta + serviço posto" também é reforçado (é onde ele
    está) — o gate é o que separa correlação de causa (o mesmo que a dopamina
    fez no cérebro-por-órgãos: sem ela, acaso).
15. Código herdado dos dois lados continua sendo o teto (≈ direto); a
    plasticidade chega a ≥ 70 % do teto.
