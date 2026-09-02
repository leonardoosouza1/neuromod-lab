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

*(preenchido depois de rodar; regra 13 diz que efeito de mortalidade só conta
com n ≥ 5 sementes — o que está aqui é fumaça com número, não evidência.)*

## 5. O que a bateria séria precisa rodar (depois do merge)

`--preset longo` (G=60, T_evo=1200, R=16, 5 sementes) × 4 braços × 2 conjuntos
de cidades (1000+ e 2000+), + `analise_produtos.py` com ablação em 128
réplicas. É o mesmo custo do E14g/h.
