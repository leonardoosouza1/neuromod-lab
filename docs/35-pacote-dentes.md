# 35 — Pacote de dentes (E19): parar não pode ser de graça — 2026-09-02

**Leonardo:** *"estou cheirando a bug; vale implementar mais coisas de uma vez e
ir tirando o que der errado."*

## O buraco
Um táxi que não faz nada por 5 dias terminava com **vida 100, fome 100 e
fitness 0**, com ou sem economia. Fome nunca feria; aluguel atrasado nunca
cobrava. Parar era de graça e seguro — o atrator dos três colapsos da onda 1
(muitos produtos com pena, reboque do tanque, "sempre"). Com pena por morte
no objetivo, uma população que espirala nas primeiras gerações cai em
"parar" e nunca sai (não há gradiente: qualquer movimento → pane → morte).

## O pacote (tudo atrás de flags; desligado = identidade bit-exata)
1. **Fome mata**: `fome_mata=0.5` de vida por passo com fome em 100 (escala
   a partir de 90). Parado sem comer: morre em ~1 dia. Verificado: 0 vivos.
2. **Dívida mata**: `divida_mata` — dinheiro abaixo de −60 = perde o carro.
   Com aluguel 8/dia dá 10 dias sem renda; sempre dá pra trabalhar pra sair.
3. **Reboque cobra gordura, resto na vida** (padrão novo do E15).
4. **Produto com limiar**: `relu(nec − 0.5)` — o produto só puxa pro serviço
   quando a necessidade passa da metade (onda 1: sem limiar, 5 produtos =
   −2.4 e "descanso" vira atrator).

## Predições (antes de rodar; R=16, 5 sementes, pena 5, cidades 1000+)
Âncora (corpo sem economia, Reativo): 8.54 / mortos 0.19.
1. `pacote`: ninguém para (entregas ≥ 9 em 5/5 sementes); fit ≥ 6.0 (a
   economia custa ~2), mortos ≤ 0.25.
2. `− fome`: com parar de graça de novo, ≥ 2 sementes desabam (entregas < 5)
   ou fit ≤ pacote − 0.5. Se ficar igual: a fome não era o dente decisivo.
3. `− dívida`: ≈ pacote (±0.5): o limite de −60 raramente é atingido em 5 dias.
4. `− limiar` (5 produtos crus): fit ≤ pacote − 1.5 (a órbita volta).
5. `− produto` (Reativo puro): mortos ≥ pacote + 4 pp (sem a alavanca do posto).
6. `− economia`: fit ≥ pacote + 1.5 (sem aluguel/imposto), mortos ≈.
Critério do pacote: se 1 vale e cada remoção piora ou empata, o pacote
fica inteiro; peça cuja remoção MELHORA sai.

## Resultado parcial (4 de 6 braços) — a fome a 0.5/passo é um deserto

| braço | fit | entregas | mortos | vida no fim | fome no fim |
|---|---|---|---|---|---|
| pacote | 3.42 | 6.1 | **0.96** | 2.5 | 99 |
| − fome | 1.79 | 4.1 | 0.14 | 70 | 98 (2 de 5 sementes desabaram: −0.1, 0.5, 0.5) |
| − dívida | 3.42 | 6.1 | 0.96 | 2.5 | 99 (idêntico ao pacote: a dívida nunca chega ao limite) |
| − limiar | 3.26 | 5.8 | 0.95 | 2.5 | 98 |

Leitura honesta: **96 % morrem de fome** mesmo trabalhando. Fome sobe 0.32
por passo (77 por dia) e a refeição tira 45: são 1.7 refeições por dia só pra
ficar no lugar. Com dano de 0.5 por passo a partir de 90, uma população
inicial aleatória morre inteira antes de a seleção conseguir subir o peso
da comida — deserto evolutivo (não há gradiente quando todo mundo morre).
Predição 2 ✓ (sem a fome, parar volta: 2 sementes desabam); predição 3 ✓
(dívida inerte em 5 dias); predições 1, 4, 5 não avaliáveis com todo mundo
morto de fome.

**Predição 7 (antes de rodar, e19b):** com `fome_mata` em 0.15 (100 de vida
em ~4 dias com fome no máximo; quem come uma vez por dia não sofre) a
população sobrevive (mortos ≤ 0.35, entregas ≥ 8) e os dentes ainda pegam o
parado (morre em ~5 dias). Com 0.10, mortos ≤ 0.30 mas o parado só morre
depois de 7 dias — dente fraco demais para vidas de 5 dias. Aposta: 0.15.

Braços restantes com fome 0.5: `− produto` (Reativo) 4.97 / mortos 0.87;
`− economia` 4.91 / 0.85 — todos no deserto da fome (fome no fim 94–96). O
Reativo morre um pouco menos que o cérebro com produtos (0.87 vs 0.96): o
produto de comida com limiar 0.5 não faz o ser comer mais cedo. Nada do
pacote é legível com esta fome; e19b decide a calibração.

## e19b — calibração da fome (R=16, 5 sementes)

| braço | fit | entregas | mortos | fome no fim | leitura |
|---|---|---|---|---|---|
| pacote, fome .15 | 4.79 | 8.9 | 0.66 | 96 | ainda morre de fome |
| pacote, fome .10 | 1.85 | 3.8 | 0.31 | 99 | dente fraco: 3 de 5 sementes voltam a PARAR |
| Reativo, fome .15 | 6.16 | 10.5 | 0.52 | 88 | idem, um pouco melhor |

Predição 7 ✗: a força do dente não resolve sozinha. O ser **não consegue
comer o bastante**: fome sobe 0.32/passo (77/dia), refeição tira 45 → 1.7
refeições/dia só pra empatar, cada uma com desvio e 3 dinheiros. Antes dos
dentes a fome em 100 era grátis, então a evolução nunca precisou comer.
Conserto do lado da COMIDA: `REFEICAO` vira parâmetro (45 = identidade) e o
pacote usa 90 (uma refeição por dia basta), com fome .15.

**Predição 8 (antes de rodar, e19c):** com refeição 90 + fome .15: mortos
≤ 0.35, entregas ≥ 9 em 5/5 sementes (ninguém para), fome no fim ≤ 70;
`− economia` ≥ pacote + 1.5 de fitness; cérebro com produtos ≤ Reativo em
mortos (o produto de comida com limiar agora tem trabalho). Se mortos
ficarem ≥ 0.5: o gargalo é a DISTÂNCIA até a comida (poucos nós têm) e o
conserto é densidade de serviço, não corpo.

## e19c — refeição 90 (R=16, 5 sementes) e o diagnóstico

| braço | fit | entregas | mortos | fome no fim |
|---|---|---|---|---|
| pacote ref90 fome .15 (cérebro com produtos) | 5.27 | 9.4 | 0.59 | 91 |
| pacote ref90 fome .15 (Reativo) | 6.44 | 10.8 | 0.49 | 86 |

Predição 8 ✗. Olhando o campeão (Reativo, 128 réplicas): **2.2 refeições em 5
dias**, 34 de 1200 passos num nó com comida, e quando está num nó com comida
com fome ≥ 60 come só **13 %** das vezes (13 oportunidades por vida). Peso
evoluído da feature "distância até comida" ≈ 0 em 5/5 sementes; peso do
serviço comida (1.4–3.5) menor que posto/oficina (4–5). Só **3 dos 26 nós**
têm comida. O cérebro reativo não aprende a rotear pra comida — o mesmo
limite que teve com o posto à noite — e dois recursos letais com 3 nós cada
é demais pra política de 1 salto.

**Conserto de mundo (e19d):** `comida_no_posto` — o posto vende comida
(nós com comida 3 → ~6, e o ser já sabe ir ao posto). Predição 9 (antes de
rodar): refeições/vida ≥ 5, fome no fim ≤ 60, mortos ≤ 0.35, entregas ≥ 9,
ninguém parado; com refeição 45 (`ref45`) mortos ≤ 0.45 (o tamanho da
refeição importa menos que o acesso). Se mortos continuarem ≥ 0.45 mesmo
com comida no posto: o gargalo é a DECISÃO de comer (13 %), e o conserto é
acoplar comer ao abastecer ("combo": abasteceu → comeu) ou dar ao cérebro o
produto fome × distância com limiar alto.

> Operacional (2026-09-03 08:36): a máquina foi DESLIGADA às 00:57 e ligada
> às 07:30 (`last -x`); o 3º braço da e19c (ref90 − economia) e a fila e19d
> morreram com o desligamento — não foi o harness (a fila roda sob
> `systemd --user`, sobrevive ao reinício da sessão). Relançados juntos como
> e19e (4 braços, ~50 min). Lição: ao acordar, conferir `last -x` antes de
> culpar a fila; filas não sobrevivem a desligamento — retomar por `.done`.
