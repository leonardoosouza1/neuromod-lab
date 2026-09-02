# 26 — Calorias, reserva e peso: energia em DOIS compartimentos (E12, 2026-09-01)

**Leonardo:** *"água é ponto central. Precisamos de outra coisa como calorias —
o combustível. Gordura e caloria são complexas, mas em carros temos a reserva:
o táxi pode ter mais gasolina e no fim do dia isso vira reserva se não for
usado por outros processos como crescer, desenvolver o cérebro. A perda de
conversão pode variar — talvez o cérebro desvende. E a reserva PESA no chassi:
perde performance, gasta mais água, tem mais fome, não dorme tão bem. Copiando
um ser humano. Rode validações para ver se vale a pena."*

## 1. Por que isto não é "mais um recurso"

Até aqui o preço da eficiência (κ) era um número subtraído do fitness — uma
penalidade macia, abstrata, artesanal. Com calorias o cérebro passa a **comer
do mesmo tanque que salva a noite**. A tese-mãe ("eficiência é o ponto inicial
de tudo") deixa de ser fórmula e vira restrição DURA da física do mundo:

- cérebro caro = menos sobra à meia-noite = menos gordura = morre na noite magra;
- infância cara (E8) ganha conta de verdade — é o Kuzawa (bebê gasta 2× glicose,
  crescimento desacelera pra pagar o cérebro);
- crescer (upgrade/órgão) compete com sobreviver pela MESMA poupança.

## 2. Design (UMA energia, DOIS estados — como glicose × gordura)

| peça | regra | análogo |
|---|---|---|
| tanque (`fuel`) | como antes; posto enche (eco2) | glicose/glicogênio |
| reserva (`res`, teto 60) | à MEIA-NOITE, sobra do tanque acima de 50 vira reserva (perde 10%); só converte o que cabe | gordura |
| mobilizar | tanque não paga o salto e `res>0` → para 3 passos, converte 25 com perda `perda` | lipólise: lenta e com perda |
| `perda` | sorteada POR MUNDO (15–45%) — lei oculta como `k_agua`; só se descobre vivendo | metabolismo individual |
| pane | só quando a reserva zerou | inanição |
| peso | `1 + .10·fuel/cap + .30·res/60` multiplica tempo de viagem, fuel/água/calor, fome, fadiga; DIVIDE a recuperação do descanso | obesidade: lento, quente, faminto, dorme mal |
| cérebro come | `cerebro_come`: custo neural sai do TANQUE (`KAPPA_F`=.05/consulta), não do fitness | 20% da energia humana vai pro cérebro |

Sensores novos (NF 18→21, zero nos mundos antigos): `e_reserva`, `h_sin`,
`h_cos`. O ser SENTE a gordura pelo chassi (efeitos) E lê o nível (feature) —
igual a nós: pesa no corpo e sabemos que estamos gordos.

## 3. Onde a energia MORDE (sem isto, teto zero — regra 1)

N13 provou: no base ninguém fica sem gasolina (posto barato e onipresente).
Reserva num mundo assim é pura taxa. Então o mundo ganhou NOITE (22h–6h):
posto FECHADO, 1 dos 6 passageiros acordado. Perito à mão: 18 panes/3 dias,
parado 74% da noite. A noite magra é a fome que dá trabalho à gordura.

## 4. O que a validação decide (predições em PREDICOES.md §E12)

Braços (reativo, mesmo genoma): `dia` → `noite` → `reserva` (sem peso) →
`reserva+peso`; fase B: `talamo` × `sempre` com o cérebro comendo calorias.
Decisões que os números tomam:
- teto (panes evitáveis × custo) < 0.5 → reserva sem trabalho neste mundo;
- `reserva+peso` ≥ `noite` → vale a pena; < → peso caro OU gordura nunca se forma;
- comportamento emergente esperado: encher antes das 22h; gordura baixa quando
  pesa; mobilizações à noite > 0.

## 5. Sugestões pra depois (não rodadas — declaradas)

1. **Crescer com gordura**: upgrade da loja custa reserva (não só dinheiro) —
   fecha "crescer consome a sobra".
2. **Infância paga pelos pais → pela reserva**: o bebê nasce com reserva cheia
   (leite) e o cérebro infantil drena dela; subsídio vira conta.
3. **Perda desvendável**: SerSono aprende `perda` como aprendeu `k_agua`
   (regressão no sono: quanto rendeu cada mobilização) → decide se vale
   engordar neste mundo.
4. **Água × gordura**: pesado esquenta mais → água como recurso central (N13)
   acopla direto: gordo bebe mais água. Já está no design (cuf×peso).

## 6. Resultados (2026-09-01, 7 baterias, 26 braços, 78 sementes, 3 arquiteturas)

Predições em PREDICOES.md §E12 (1–11). Fitness = entregas − 0.3·avarias,
5 dias em 3 cidades novas, 128 réplicas por campeão, média de 3 sementes.

### 6.1 No mundo E12 padrão a gordura NUNCA se forma

| bateria | noite | reserva | reserva+peso | res~/60 | panes/vida |
|---|---|---|---|---|---|
| rápido (G=20) | 2.74 | 2.54 | 2.88 | 4 | 16–17 |
| longo (G=60) | 4.83 | **5.34** | 4.50 | 4.5 | 18 |
| longo, ReativoHora (lê a hora) | 4.42 | **5.13** | 4.42 | 4.3 | 17–19 |
| longo, RICO (pane sem multa) | **8.21** | 7.85 | 7.09 | 3–5 | 16.5–17.7 |
| longo, Corpo (desvia pro posto) | **4.97** | 4.71 | 4.42 | 4.5 | 15–17 |

- Reserva grátis vale de −0.4 a +0.7 sobre `noite`; com peso, de −1.1 a +0.1.
  Dentro do ruído entre sementes (±0.7). **Não paga.**
- Mecanismo: o tanque às 22h fica em 32–39 (< NIVEL=50) em TODOS os braços,
  então a meia-noite converte 6–9 de fuel por dia e a gordura oscila em 3–5.
  Só 1.4–3 mobilizações por vida contra 15–19 panes. A reserva mobiliza 25 e
  a pane devolve 15 por 18 passos parado: sem estoque, a gordura é o mesmo
  seguro da pane, só que menor.
- Por que ninguém enche antes da noite? Testei 4 hipóteses, todas nulas:
  (a) tempo de evolução (G=60 ✗), (b) alavanca neural pra hora (ReativoHora
  usa `fuel22` 37–39, igual ✗), (c) pobreza (rico: pobre_frac 0.09 e panes
  IGUAIS 16.5 ✗), (d) previdência de rota (Corpo desvia pro posto e pane
  igual ✗). Sobrou: **a pane é escolha da evolução** — "posto grátis lento".
- Prova da escolha (v6): tirar o fuel da pane (`reboque`: ração só até o posto)
  mata o mundo em qualquer multa — perito ent 3.1; evolução `dia` fit −4.3
  (multa 12), −1.3 (multa 4), +0.2 (multa 0), com 22–26 panes/vida. **A pane
  que devolve 15 de fuel SUSTENTA a economia**: 17 panes × 15 = 2.5 tanques
  grátis por vida. Sem ela não há mundo; com ela não há sobra.
- Emergente (rico): com reserva o ser vai MENOS ao posto (6.3 vs 10.2/vida) —
  a gordura substitui o posto, não a noite.
- Fase B (cérebro come do tanque): `sempre` colapsa (ent 4.0, tanque às 22h
  = 14, fit −0.11); `talamo` 1.62. O gap absoluto (1.7) é menor que no E6
  (~6.5) porque aqui o custo aparece como pane (cai na avaria), não como κ.
  A física "cérebro caro morre na noite magra" funciona — só não havia gordura
  pra ele comer.

### 6.2 Num mundo COM sobra (fuel × 0.5) a gordura forma — e o peso come o ganho

Rápido, 3 sementes (longo abaixo quando terminar):

| braço | fit | res~/60 | mob/vida | posto/vida | panes |
|---|---|---|---|---|---|
| dia | 13.16 | – | – | 12.4 | 5.1 |
| noite | 8.80 | 0 | 0 | 10.5 | 4.6 |
| reserva (grátis) | **10.06** | **17.7** | 1.8 | 16.7 | 5.4 |
| noite+peso (só tanque, WF=.10) | 7.92 | 0 | 0 | 8.9 | 7.7 |
| reserva+peso (.10/.30) | 7.51 | 8.9 | 1.7 | 9.0 | 8.5 |
| reserva+peso N30 | 7.71 | 17.1 | 3.0 | 15.8 | 7.1 |
| reserva, só peso da gordura (WF=0, WR=.30) | 8.61 | 16.0 | 2.0 | 12.7 | 5.6 |
| reserva+peso meio (.05/.15) | 8.93 | 14.6 | 1.7 | 10.0 | 5.6 |
| noite+peso meio (.05/0) | 9.31 | 0 | 0 | 9.0 | 7.5 |

Longo (G=60, T_evo=1200, 3 sementes, 459 s) — os pares justos:

| braço | fit | por semente | res~/60 | posto/vida | panes |
|---|---|---|---|---|---|
| noite | 13.03 | 12.4 / 14.1 / 12.5 | 0 | 6.8 | 5.6 |
| reserva (grátis) | **13.37** | 13.6 / 13.0 / 13.5 | 20.6 | 13.9 | 5.3 |
| noite+peso (.10) | 12.72 | 13.7 / 12.6 / 11.9 | 0 | 7.9 | 5.6 |
| reserva+peso (.10/.30) | **11.06** | 11.3 / 11.9 / 10.0 | 17.8 | 9.1 | 5.9 |
| noite+peso meio (.05) | 13.24 | 13.4 / 12.6 / 13.7 | 0 | 6.4 | 5.6 |
| reserva+peso meio (.05/.15) | 12.86 | 13.4 / 12.9 / 12.3 | 22.2 | 10.7 | 4.6 |

- Predição 11 ✓ (gordura forma: res~ 17.7 rápido / 20.6 longo, conv/dia
  13–15, panes < 8, fuel22 56–66).
- Longo: seguro grátis **+0.34** (11% do teto de 3.1; rápido dava +1.26 —
  com mais gerações a `noite` sozinha melhora e a folga da reserva encolhe).
  Peso cheio: **−1.66** contra o par justo `noite+peso` (3 de 3 sementes
  abaixo). Metade do peso: −0.38 (ruído). Gordura sob peso cheio 17.8 vs
  20.6 — emagreceu 14%, não os 50% do rápido: o "fica magro" é real mas
  fraco quando a evolução tem tempo.
- Rápido: seguro grátis **+1.26** sobre noite (sementes +4.2 / −1.5 / +1.0)
  = 57% do teto (2.2). Paga, mas 1 de 3 sementes perdeu.
- Peso do TANQUE sozinho: −0.88 (é imposto do mundo, igual pra todos).
- Par justo `reserva+peso` vs `noite+peso`: **−0.41**. Só gordura pesando:
  −0.19 sobre noite. Metade do peso: −0.38 sobre o par. Todos dentro do ruído
  (o `noite+peso meio` deu +0.5 acima de `noite` sem poder — é o tamanho do
  ruído). **Com qualquer peso testado a reserva vira empate.**
- **Emergente e não roteirizado**: com peso o ser fica MAGRO — gordura 8.9
  contra 17.7 sem peso, vai ao posto 9 vezes em vez de 17, e aceita mais panes
  (8.5 vs 5.4). Sob WR=.30 a evolução escolheu "leve e às vezes parado" em vez
  de "gordo e garantido". É a homeostase de peso que o design pedia (§4:
  "gordura baixa quando pesa") — apareceu sozinha.

### 6.3 Veredito: vale a pena?

**Como física, sim — como vantagem, não (ainda).** A cadeia toda funciona
(sobra → gordura → mobiliza com perda → pesa → o ser emagrece), mas o
fitness não sai do ruído:

1. No mundo padrão não há sobra: a pane subsidiada (15 de fuel grátis) é o
   que mantém o táxi vivo, e ela deixa a gordura sem trabalho. Isto é
   calibração do MUNDO, não da reserva.
2. Onde há sobra, o seguro grátis rende +1.3 (rápido) / +0.34 (longo) e o
   peso, com os números do Leonardo (.10/.30), custa −1.7 contra o par justo;
   a metade do peso dá empate (−0.4, ruído). Gordura de graça = pequeno
   ganho; gordura que pesa = prejuízo ou empate.
3. O teto é pequeno por construção: no mundo com sobra a noite custa 4.4 e só
   2.2 são panes evitáveis; o resto é o posto fechado e 5 de 6 passageiros
   dormindo — coisa que gordura nenhuma resolve.

O que decidiria a favor (não rodado, declarado): (a) mundo sem pane
subsidiada MAS com renda que sustente o posto (hoje não existe: reboque com
multa 0 dá fit 0.2); (b) noite mais longa/cidade maior onde uma vida sem
gordura não fecha a noite; (c) gordura com uso além de seguro — crescer,
infância, cérebro (§5.1–5.2) — aí ela vira poupança, não só airbag.

### 6.4 Placar das predições 1–11

| # | predição | resultado |
|---|---|---|
| 1 | noite custa ≥ 1.5 | ✓ −2.9 (rápido), −4.4 (sobra) |
| 2 | teto da reserva ≥ 0.5 | ✓ 6.9–8.4 (mas irrealizável: 15 de 18 panes são escolha) |
| 3 | reserva > noite | ✗/~ (−0.2 a +0.7; +1.3 só com sobra) |
| 4 | reserva+peso ≥ noite | ✗ (−1.3 a +0.1) |
| 5 | fuel22 sobe com reserva | ✗ (32–39 sempre) |
| 6 | talamo > sempre com cérebro comendo | ✓ 1.62 vs −0.11 |
| 7 | G=60/N30 fazem gordura formar | ✗ (res~ 3.7–4.5) |
| 8 | ReativoHora enche antes da noite | ✗ (fuel22 igual) |
| 9 | rico: pobreza era o gargalo | ✗ (pobre 0.09, panes iguais) |
| 10 | Corpo: previdência era o gargalo | ✗ → pane é ESCOLHA (confirmado no v6) |
| 11 | com sobra a gordura forma e o peso morde | ✓ (17.7–20.6/60; peso cheio −1.7, meio −0.4) |
