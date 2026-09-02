# 31 — E17: cérebro com produtos (termos bilineares)

*(agente E17, 2026-09-02; plano em doc 28 §1. Código: `src/produtos.py`,
`src/e17_produtos.py`, `src/analise_produtos.py`, `src/testes_e17.py`.
Nada em `lab.py` foi tocado — portão de identidade `perito base ent 7.9740 /
av_fuel 25.1302` conferido.)*

## 1. Motivação: uma soma não expressa um "só quando"

O `Reativo` pontua cada vizinho com uma soma ponderada de features:

```
score(vizinho) = Σ_f w_f · F_f(vizinho)          F = [d_alvo, custo, congestão,
                                                      semáforo, d_posto…d_loja,
                                                      16 de estado, bias]
```

`e_fuel` e `d_posto` estão os dois lá dentro — mas SOMANDO. Com isso o ser
consegue dizer "gosto de nós perto do posto" (constante) e "meu tanque está
baixo" (desloca todos os vizinhos igualmente, porque o estado é o MESMO para
os 5 candidatos). O que ele não consegue dizer é **"puxa pro posto só quando
o tanque está baixo"** — isso é um produto `d_posto(vizinho) × (1−fuel/cap)`,
e produto não está no span de uma soma de features. Formalmente: o termo de
estado é constante ao longo de `g` (vizinho), então some do `argmax`; só o
produto faz o estado interno reordenar os vizinhos.

E14g (doc 27 §6.20) mostrou o tamanho disso com UM produto
(`ReativoNoite24`): mortos 0.17 → 0.12, panes −1/3, genes convergindo em 5/5
sementes (3.7 · 0.3) e ablação causal (zerar os dois: mortos → 0.35). O
diagnóstico de N2/N10 ("falta memória de rota") estava errado de nome: não era
memória, era um produto.

**Pergunta do E17:** os outros quatro serviços (comida, descanso, oficina,
loja) pedem a mesma alavanca? E se dermos ao cérebro TODOS os produtos
estado × distância, a evolução acha os poucos úteis — ou se perde na busca?

## 2. Desenho

### 2.1 `ReativoProduto` (NP = 44 + 7 = 51)

```
movimento(vizinho) += − W[B0+p] · d_p(vizinho) · nec_p          p = 0..4
serviço posto      += (W[B0+5]·sin h + W[B0+6]·cos h) · nec_posto
```

- `nec_p` é a necessidade do CORPO por serviço, a mesma fórmula de
  `Lote.serv_need()` sem `sv`/`paga` (necessidade guia a ROTA, disponibilidade
  guia a decisão de usar): `1−fuel/cap`, `fome/100`, `fad/100`,
  `max(1−pneu/100, temp/120)`, `min(dinh/90, 1)`.
- `d_p` vem de `m.dsa` — o mesmo oráculo da feature `d_*` de `obs()`; no mundo
  `semgps` ele já vem zerado, então o produto não fura a venda.
- Sinal: `W_p > 0` = "aproxime-se do serviço p quando precisar dele". O gene
  `pr_posto` é exatamente o gene `rota` do `ReativoNoite24`.
- Os 2 genes de hora entram no SERVIÇO posto (decidir abastecer cedo), não no
  movimento — o movimento já tem `pr_posto` e a hora sozinha não reordena
  vizinhos. Sem relógio (`m.RELOGIO` falso) `sin/cos` são zero: os genes ficam
  exatamente inertes e a identidade com o mundo sem relógio é preservada
  (testado).

### 2.2 `ReativoProdutoFull` (NP = 44 + 60 = 104)

```
movimento(vizinho) += − Σ_{k,p} W[B0 + 5k + p] · est_k · d_p(vizinho)
```

12 estados (`fuel, fome, fad, pneu, temp, oleo, dinh, tem_pax, reserva, h_sin,
h_cos, dano` — os 12 de `est` sem os 4 slots reservados de E15/E16) × 5
distâncias. **Cuidado com o sinal:** aqui os estados são as features de
`obs()` como elas são, e `e_fuel = fuel/cap` é ENCHIMENTO, não déficit. O
equivalente ao gene do Noite24 é portanto `W[fuel × posto] < 0` (a parte
linear `−W·d_posto` já é expressável pela própria feature). A análise traduz.

O Full é o controle de **busca vs expressividade**: contém o `ReativoProduto`
como subespaço (todo produto `nec_p × d_p` é combinação linear dos `est_k ×
d_p` mais a feature linear `d_p`), e mais 53 direções que não deveriam servir
pra nada.

### 2.3 Onde ficam os genes (regra 15: escala)

Apêndice ao genoma do `Reativo`, não nos 12 pesos mortos `NF+6..NF+17` —
aqueles já significam outra coisa em irmãos (`ReativoNoite` NF+6/7,
`ReativoHora` NF+6..NF+17, `BancoEMA` NF+6..NF+11) e o Full precisa de 60 de
qualquer jeito. Custo declarado: genoma 16% (Produto) e 136% (Full) maior que
o do `Reativo` — é exatamente o eixo que a predição 17.4 mede.

Escala (regra 15): distância crua é O(1..20), necessidade é O(0..1), então o
produto é O(10) e um gene O(1) já compete com os pesos de serviço O(10–20). É
o oposto do gene de timing do `ReativoNoite`, que era O(1)×O(1) e nasceu
inerte. Prova sem evolução (`testes_e17.py`): em 32 genomas ALEATÓRIOS, ligar
`pr_posto = 3.7` à mão leva panes de 7.75 → 4.02 e vida final de 20.5 → 31.0.

### 2.4 Mundo e avaliação

`cfg_corpo(continua=.02, reserva=True, RES_MAX=120, pane_dinh=0, massa=True,
peso=True, pena_morte=5)` — o recomendado do E13f com a morte visível ao
objetivo (E14b), que é onde E14g/h mediram a alavanca. Avaliação: 128
réplicas × 3 cidades de teste (1000+), T=1200. Regra 13/14: a bateria séria é
R=16, 5 sementes; aqui só cabe a validação rápida (§4).

## 3. Predições (ANTES de rodar)

Numeração local `17.x` (as globais 1–47 estão em `PREDICOES.md`; os quatro
agentes em paralelo renumeram no merge).

| # | predição | como cai |
|---|---|---|
| **17.1** | o produto `pr_posto` (fuel × d_posto) é redescoberto com sinal POSITIVO em ≥ 4/5 sementes e \|W\| ≈ 3–4, como no Noite24 (3.6–3.8) | sinal em ≤ 3/5, ou mediana fora de 2–6 |
| **17.2** | `pr_comida` (fome × d_comida) e `pr_oficina` — no Full, `dano × d_oficina` — também convergem (≥ 4/5, \|med\| > 0.5): o corpo pede | ficam ~0 ou trocam de sinal |
| **17.3** | `ReativoProduto` ≤ `ReativoNoite24` em mortos (≤ 0.12) e ≥ em fitness (mais alavancas, mesma avaliação) | mortos > 0.12 ou fit < Noite24 |
| **17.4** | `ReativoProdutoFull` fica PIOR que `ReativoProduto` em G=60 (fit e mortos) — genoma 8× maior no bloco novo, mesma pressão — a não ser que R seja grande | Full ≥ Produto |
| **17.5** | ablação: `pr_posto` é o produto mais causal — zerá-lo sozinho custa ≥ +10 pp de mortos; zerar TODOS custa ≥ +15 pp | outro gene domina, ou nenhum passa de +5 pp |
| **17.6** | `pr_loja` (dinheiro × d_loja) NÃO converge: dinheiro não tem "buraco" que a rota conserte (a loja é upgrade, não recuperação) | converge com \|med\| > 0.5 em ≥ 4/5 |
| **17.7** | os 2 genes de hora no serviço posto ficam INERTES (ablação < 2 pp) — 5ª vez que a família reativa não usa a hora (N17); a alavanca é o tanque, não o relógio | ablação da hora ≥ 5 pp |
| **17.8** | na geração 0 o Full tem fitness MENOR que o Produto: 60 genes × N(0, .8) × sinal O(10) afogam as features base no score (ruído bilinear), e a evolução gasta gerações só apagando produto | ger 0 empatada ou Full melhor |
| **17.9** | no Full, os produtos que sobrevivem são ESPARSOS: ≤ 8 dos 60 passam do limiar de convergência | > 15 convergem (então o cérebro virou "denso e funciona") |
| **17.10** | mecanismo esperado do ganho: menos panes (`av_fuel`) e mais visitas ao posto por vida (`n_posto`), não mais entregas — o produto é rota preventiva, não produtividade | fit sobe com `av_fuel` igual |

Negativo possível (declarado): com 5 produtos em vez de 1, a evolução pode
co-adaptar (regra 5 dos NEGATIVOS: mecanismo novo × peso evoluído) e piorar —
por exemplo `pr_descanso` puxando pro descanso o tempo todo (fadiga nunca é
zero) e roubando a rota do passageiro. Se `ReativoProduto` < `Noite24`, a
leitura é "um produto basta; cinco brigam entre si", que é um resultado tão
útil quanto o positivo.

## 4. Validação rápida (1 semente, G=10 — NÃO é a bateria)

Orçamento de GPU do agente: **uma** evolução curta (P=512, G=10, T_evo=600,
1 semente, R=4) + avaliação em 128 réplicas × 3 cidades (1000+), T=1200.
Levou 71 s no total (modo `compile`). **Regra 13: com 1 semente e 10 gerações
nada aqui é evidência** — é fumaça com número. A referência do E14g/h (G=60,
R=16, 5 sementes) é fit 8.17/mortos 0.17 (Reativo) e 8.58/0.12 (Noite24);
tudo abaixo está 4× abaixo disso porque a busca mal começou.

| braço | NP | fit | mortos | ent | panes | posto | t_vida | melhor ger 0 → 9 |
|---|---|---|---|---|---|---|---|---|
| reativo | 44 | **2.20** | 0.250 | 5.24 | 5.39 | 10.0 | 0.91 | −0.18 → 3.16 |
| noite24 | 44 | 1.56 | 0.208 | 4.10 | 4.13 | 5.6 | 0.92 | +0.17 → 1.72 |
| produto | 51 | 0.63 | 0.148 | 1.93 | 1.65 | 7.3 | 0.94 | +0.01 → 0.94 |
| produto_full | 104 | −0.09 | **0.010** | 0.13 | 0.14 | 4.4 | 0.99 | −0.34 → 0.28 |

### 4.1 O achado que muda a leitura: mortalidade é métrica de degrau aqui

A ordem de `mortos` é o INVERSO exata da ordem de `fit`: quem entrega menos
morre menos, e o `produto_full` chega a **0.010 de mortos com 0.13 entregas**
— o melhor número de mortalidade do laboratório inteiro, produzido por um ser
que praticamente não sai do lugar. Com `pena_morte=5` e 10 gerações, "parar"
é o pico local mais barato, e o produto é justamente a alavanca que permite
parar de forma barata (puxar sempre pro serviço mais perto). Consequência
metodológica, válida para a bateria séria e para os outros agentes:
**nenhuma conclusão do E17 pode ser lida em `mortos` sozinho** — a comparação
tem que ser conjunta (`fit` E `mortos`, com `ent` do lado). É a mesma armadilha
do feedback "métrica de degrau" (zero cravado = métrica batendo no limite).

### 4.2 A alavanca à mão (regra 15) — 128 réplicas, sem evolução nenhuma

`analise_produtos.py --perito` liga cada produto à mão sobre um genoma base.
Base 1 = perito escrito à mão (não é deste mundo: 0.773 de mortos);
base 2 = campeão `reativo` desta corrida (fit 2.20).

| produto ligado à mão (=3.7) sobre o **reativo evoluído** | fit | mortos | ent | panes |
|---|---|---|---|---|
| (nenhum: campeão intacto) | 2.20 | 0.250 | 5.24 | 5.39 |
| pr_posto | −2.30 | 0.604 | 0.62 | 5.28 |
| pr_comida | −2.06 | 0.646 | 0.98 | 6.29 |
| pr_descanso | 0.63 | **0.016** | 1.13 | **0.59** |
| pr_oficina | −3.70 | 0.812 | 0.22 | 9.11 |
| pr_loja | 0.91 | 0.268 | 3.33 | 4.58 |
| os 5 juntos | −1.06 | 0.221 | 0.22 | 2.22 |

Três leituras, todas com mecanismo:

- **A alavanca não é decorativa** (o modo de falha do gene de timing, regra
  15): mexer um único gene move mortalidade de 0.25 para 0.02 ou para 0.81,
  panes de 5.4 para 0.6 ou 9.1. Escala certa, efeito enorme.
- **Enxertar produto em genoma que não co-adaptou SEMPRE custa fitness**
  (13/13 variantes, nas duas bases). Faz sentido: os pesos lineares foram
  selecionados sem o produto, e o produto reordena os vizinhos justamente
  quando a necessidade aparece — que é quando o peso linear já estava
  decidindo. **O produto precisa co-evoluir com o resto**; o mesmo gene que
  no E14g valia −5 pp de mortos, ligado à mão no campeão errado vale +35 pp.
  É a regra 5 dos NEGATIVOS (co-adaptação) com o sinal invertido: aqui a
  co-adaptação não é o risco, é a condição.
- **`nec` sem portão vira atração constante.** `1−fuel/cap` é ~0 com o tanque
  cheio (o gene do Noite24 se desliga sozinho), mas `fome/100`, `fad/100` e
  `1−pneu/100` quase nunca são zero: `pr_comida`/`pr_oficina`/`pr_descanso`
  puxam pro serviço o tempo todo e o táxi para de trabalhar. Se a bateria
  séria confirmar, a correção não é tirar o produto, é dar-lhe LIMIAR
  (`relu(nec − θ)`, θ gene) — a alavanca do posto funciona porque o
  denominador já a desliga.

### 4.3 Ablação dos campeões desta corrida (128 réplicas)

| campeão (G=10) | zerar TODOS os produtos | gene mais causal |
|---|---|---|
| noite24 (fit 1.56 / 0.208) | fit 0.20 / **mortos 0.383** | `rota_posto`: +19 pp de mortos, −1.39 de fit |
| produto (0.63 / 0.148) | −2.47 / **0.758** | `pr_oficina` +9.6 pp; `pr_posto` +6.5 pp |
| produto_full (−0.09 / 0.010) | −4.06 / **0.927** | `fome×descanso` +10 pp; `tem_pax×descanso` +7 pp |

Os produtos são causais nos três: sem eles a política inteira cai. Mas nos dois
campeões do E17 eles sustentam uma política de *não trabalhar*, então a
causalidade aqui não valida a alavanca — valida que o gene tem força.

### 4.4 Placar das predições até onde a fumaça alcança

| # | status | número |
|---|---|---|
| 17.1 | **não avaliável** (1 semente; regra 13 pede 5) | `pr_posto` = +0.51 (E14g dá 3.7 em 5/5 — G=10 é 1/6 da busca) |
| 17.2 | não avaliável | `pr_comida` −0.18, `pr_oficina` +0.41 |
| 17.3 | **✗ nesta escala** | produto 0.63/0.148 vs noite24 1.56/0.208: mortos menor mas fitness menor — vitória por não trabalhar, não conta |
| 17.4 | **✓ (fraco)** | full −0.09 < produto 0.63 < noite24 1.56 em fit |
| 17.5 | parcial | zerar todos: +61 pp (produto). `pr_posto` sozinho +6.5 pp (< 10 pp); o mais causal foi `pr_oficina` |
| 17.6 | ✗ (fraco) | `pr_loja` foi o MAIOR gene de movimento (+1.06) e à mão é o único benigno (fit −0.22) |
| 17.7 | ✓ (fraco) | genes de hora: ablação +0.8 pp e −2.1 pp = ruído. 5ª vez que a família reativa não usa a hora |
| 17.8 | **✓ (fraco)** | melhor da geração 0: full −0.34 < produto +0.01 < noite24 +0.17 |
| 17.9 | não avaliável | (precisa de sementes) |
| 17.10 | ✓ na direção | produto faz 1.65 panes vs 5.39 do reativo, com 1/3 das entregas |

**O que ficou provado sem depender de evolução:** `pr_posto` é bit a bit o
gene `rota` do `ReativoNoite24` (`testes_e17.py`: max \|dif\| 9.5e-07 em 40
passos), os genes zerados reproduzem o `Reativo` exatamente em dois mundos, e
`extra()` roda em `compile` e em `eager` sem sync.

### 4.5 O que a bateria séria tem de responder (ordem)

1. G=60 / R=16 / 5 sementes: `produto` bate `noite24` em fitness *e* mortos?
   Sem isso, 17.3 fica aberta — G=10 só mostrou o atrator "parar".
2. O atrator "parar" é do orçamento de busca ou dos 5 produtos? Controle
   barato: mesma corrida com `pena_morte=0` (se o standstill sumir, era a
   pena; se ficar, é a atração constante do `nec`).
3. Variante com LIMIAR (`relu(nec − θ)`) contra a versão crua — é a correção
   que §4.2 prevê.
4. `produto_full` com R=16 e G=60: 17.4 e 17.9 (esparsidade) só existem lá.

## 5. O que a bateria séria precisa rodar (depois do merge)

`--preset longo` (G=60, T_evo=1200, R=16, 5 sementes) × 4 braços × 2 conjuntos
de cidades (1000+ e 2000+), + `analise_produtos.py` com ablação em 128
réplicas. É o mesmo custo do E14g/h.
