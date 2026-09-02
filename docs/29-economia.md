# 29 — Economia real: dinheiro que compra tudo, distritos e reboque em calorias (E15, 2026-09-02)

**Leonardo (doc 28 / doc 27 §7):** *"dinheiro só faz sentido se compra tudo —
aluguel, água, imposto ao receber e ao gastar; distritos com preço e alíquota;
imposto pela ORIGEM da corrida; reboque cobrando CALORIAS em vez de dinheiro.
Regra de desenho: o ser sempre pode trabalhar pra sair do buraco (dívida com
juros, não morte instantânea)."*

Herança direta do **N16** (doc 27 §5): a multa da pane em dinheiro cobrava na
mesma moeda que compra o conserto (posto 2, oficina 10) e a 1ª pane virava
sentença — armadilha de pobreza, não seleção. A resposta não é tirar o custo
da pane: é **trocar a moeda**. O guincho queima caloria (gordura, depois
tanque); a carteira passa a servir pra coisa nenhuma-opcional: aluguel, água e
imposto, que ninguém escolhe pagar.

Tudo atrás de `cfg.economia` (desligado = identidade bit-exata, portão
`ent 7.9740 / av_fuel 25.1302` + `testes.py` + `testes_e15.py`).

## 1. O desenho

### 1.1 Distritos (D=3)

Cada cidade é particionada por **k-means determinístico** sobre as posições dos
nós (sementes por ponto-mais-distante + 8 iterações de Lloyd), calculado uma vez
por `Lote`, no host. A geografia é a mesma em todos os mundos daquela cidade.

Cada distrito tem uma **alíquota** e um **multiplicador de preço**, pareados:

| distrito | alíquota | multiplicador de preço | leitura |
|---|---|---|---|
| barato | 0.10 | 0.8 | periferia |
| médio | 0.20 | 1.0 | — |
| caro | 0.30 | 1.3 | centro |

**Qual distrito é qual é sorteado POR MUNDO** (`dist_sorteia=True`), do mesmo
jeito que `npc_base` (ruas) e `perda` (reserva). Justificativa: a geografia
econômica vira **lei oculta** — a evolução não pode decorar "na cidade 3 o
distrito 0 é caro", porque o distrito caro muda a cada mundo. Quem quiser usar
a informação tem que **ler a feature** `e_preco_local`. É a regra que os
negativos escreveram (N12: gatilho evoluído, nunca estatística fixa à mão) e o
padrão que N1 exige pra memória/leitura ter o que pagar. O braço de controle
`distritos fixos` (fase c) mede se essa escolha mudou alguma coisa.

Sorteio feito com **gerador próprio** (`seed+777771`), não com o `g` do mundo:
assim (a) desligado não desloca nenhum draw — identidade bit-exata — e (b)
ligado, o mundo físico (tráfego, perda, spawn) é o MESMO do braço sem economia.
Só a economia muda.

### 1.2 Imposto ao RECEBER, pela ORIGEM

A corrida paga a alíquota do distrito onde o passageiro **embarcou** (`po_`),
mesmo terminando noutro distrito. Implementação: o distrito de origem é gravado
no embarque (`e15_dorig`); na entrega, o imposto fixo `c.imposto` que a linha
comum já cobrou é **corrigido** para a alíquota da origem.

### 1.3 Imposto ao GASTAR

Toda compra paga `preço_base × multiplicador_do_nó_atual × (1 + alíquota)`.
Fator efetivo entre **0.88** (periferia barata) e **1.69** (centro caro) —
abastecer no lugar errado custa quase o dobro. O descanso (preço 0) não paga
imposto; posto (2), comida (3), oficina (10) e loja (26) pagam.

### 1.4 Aluguel e água

À meia-noite: `ALUGUEL (6) + ÁGUA (2) = 8/dia`, do dinheiro, sempre — é a
**despesa que não se escolhe**, o que faz o dinheiro valer alguma coisa. Morto
não paga.

### 1.5 Dívida com juros, nunca morte por dinheiro

`dinh` pode ficar negativo até `-LIMITE_DIVIDA` (60), com **5% de juros
diários** sobre o saldo negativo. Abaixo do piso o saldo trava (é o único
subsídio do desenho — declarado no §4).

O bloqueio dos serviços **não precisou de código novo**: os portões que já
existem (`dinh >= preço` na compra e `paga` no `serv_need`) fecham o comércio
assim que o saldo fica abaixo do preço. Ou seja: **no vermelho ninguém fia**.
O ser continua rodando, pegando passageiro e entregando — trabalhar é sempre
possível, e é a única saída. É exatamente a regra do Leonardo, e o mecanismo é
a lei da moeda cruzada: a dívida é em dinheiro, a saída é em trabalho.

### 1.6 Reboque em CALORIAS

Na pane seca, o guincho cobra `KCAL_REBOQUE (1.0) × d_posto` — **da gordura
primeiro** (com a perda de mobilização `m.perda`), do tanque depois. Zero em
dinheiro (`pane_dinh=0`; o `Lote` levanta erro se não for). E como a pane agora
cobra caloria, o dano de vida cai de `D_PANE=6` para **3**: senão a mesma pane
puniria três vezes (vida + caloria + tempo parado).

Calibração medida com o perito (5 dias, 3 cidades, 32 réplicas): `d_posto`
médio 2.8 → o guincho custa ~2.8 kcal por pane, ~25 por vida. Com `kcal=3` o
perito perde 0.7 de entregas e ganha 1.4 panes; com `kcal=1` fica no ruído.
Ficou 1.0.

**`KCAL_VIDA` (adicionado depois de medir, §5.1):** com `>0`, o que a gordura
não cobre vira **dano de vida** (tanto por kcal) em vez de sair do tanque. O
default continua sendo o que o Leonardo pediu (`0`, tanque), mas a medição diz
que o tanque é a moeda errada — ver §5.1 e a decisão 1 do §6.

### 1.7 Features (2 slots, `e15_a`/`e15_b` → `e_divida`/`e_preco_local`)

- `e_divida` = `clamp(-dinh/LIMITE, 0, 1)` — quão fundo está o buraco.
- `e_preco_local` = fator de preço do distrito atual normalizado em 0..1.

**Limitação declarada:** os dois slots ficam no bloco `est`, que é **por ser**,
não por vizinho — a mesma constante entra nos G candidatos de movimento. Logo o
ser pode aprender *"não compre aqui, ande mais"* (o fator desloca o placar
movimento × serviço), mas **não pode rotear para o distrito barato**: isso
exigiria uma feature por vizinho, como `d_posto`. Consequência direta: o
imposto pela origem, nesta versão, é variância de renda — não é alavanca
comportamental. Vira alavanca no E17 (produtos) ou com um slot por vizinho.

## 2. Telemetria nova (por vida)

`renda_bruta` (m.rec), `imp_receber`, `imp_gastar`, `aluguel_agua`, `juros`,
`carga_fiscal` (soma / renda bruta), `div_max` (+ percentis), `div_frac`
(fração dos passos vivo e no vermelho), `kcal_reboque`, `t_dist` e `ent_dist`
(passos e entregas por distrito).

## 3. Predições (antes de rodar)

Numeradas a partir de 46 (o doc 27 fecha em 45). Os braços são
`corpo (sem economia)` · `economia` · `economia rico` (aluguel 3) ·
`economia pobre` (aluguel 10) · `economia sem juros`, arquitetura Reativo.

46. **Identidade.** `economia=False` = HEAD bit a bit; economia ligada com
    constantes neutras (alíquota 0, preço 1, aluguel 0, juros 0, kcal 0) = economia
    desligada bit a bit. *(já verificado nos testes, antes da evolução)*
47. **O mundo não morre (N14).** `ent` do braço `economia` ≥ 60% do braço sem
    economia e `fit` cai entre 1 e 3 pontos. A economia é custo puro: ela não
    dá alavanca nova nenhuma ao Reativo, só tira recurso.
48. **Com aluguel, `pobre_frac` sobe** (mais passos com `dinh < 2`) em todos os
    braços com economia, e `div_frac > 0.05` no braço padrão.
49. **`div_max` bimodal.** Os percentis de `div_max` separam a população: p25 ≈ 0
    (quem nunca deve) e p100 encostando no piso (60). Desigualdade emerge de um
    mundo homogêneo — só pelo acaso das primeiras panes.
50. **`economia pobre` mata mais que `economia rico`, SEM multa em dinheiro.**
    Mortos(aluguel 10) − mortos(aluguel 3) ≥ +5 pp. O mecanismo previsto é
    novo e não é o N16: dívida → comércio fechado → não abastece → pane →
    dano. É a espiral de pobreza reaparecendo pela porta do combustível.
    Ressalva registrada: `panes` pode NÃO subir junto, porque quem quebra cedo
    anda menos (foi o que o perito fez: 11.4 panes no pobre contra 13.3 no
    rico). O sinal a olhar é **mortos** e `div_frac`, não panes.
51. **Juros são segunda ordem.** `economia sem juros` difere do padrão por
    ≤ 1 ponto de fit e ≤ 2 pp de mortos (5%/dia sobre ~20 de dívida = 1/dia
    contra 8/dia de aluguel). Se der efeito grande, é sintoma de que a
    população vive encostada no piso — e aí o piso é que está errado.
52. **Reboque em caloria não cria espiral de dinheiro** (por construção,
    `pane_dinh=0`) **mas pode criar espiral de combustível**: se a gordura está
    vazia, a caloria sai do tanque, que é a mesma moeda que leva ao posto —
    regra 12 na moeda calórica. Previsão: efeito monotônico e pequeno em
    `kcal=1`, visível em `kcal=3` (fase b).
53. **Carga fiscal é regressiva.** O campeão evoluído deve ficar em 20–40% da
    renda bruta; o perito (que entrega 3× menos) ficou em ~84%. O aluguel é
    custo fixo: quanto pior o ser, maior a fatia. Previsão dura: a `carga_fiscal`
    do braço `economia rico` é menor que a do `economia pobre` por ≥ 10 pp.
54. **`e_preco_local` ganha peso POSITIVO** (adiar compra em distrito caro
    favorece mover) em ≥ 3/5 sementes numa bateria séria. Na validação rápida
    (1 semente) só dá pra reportar o sinal.
55. **`e_divida` fica inerte** (|peso| na faixa do ruído): saber que está
    endividado não muda o que dá pra fazer — a única ação disponível já é
    trabalhar, e o ser já trabalha. Se ele NÃO for inerte, é achado.
56. **O imposto pela origem não é explorável nesta versão** (§1.7): `ent_dist`
    fica proporcional a `t_dist` (sem preferência por distrito de embarque) e o
    braço `distritos fixos` empata com o sorteado (fase c). Se der diferença,
    a lei oculta está vazando por algum canal que eu não previ.

**Regra 13 aplicada a mim mesmo:** a validação abaixo tem **1 semente** e 3
cidades. Nada dela vale como afirmação — é anti-mundo-morto (N14) e anti-bug.
Efeito de mortalidade só conta com n ≥ 5 e 6 cidades, depois do merge.

## 4. O subsídio declarado (regra 9)

O piso da dívida em −60 **é um subsídio**: encostado nele, o aluguel do dia é
perdoado. Vale, no máximo, `8 + juros`/dia. Não é lugar confortável — no
vermelho o comércio fecha, então quem está no piso não abastece, não come, não
repara: o corpo cobra o resto. Mas está declarado, é mensurável (`div_frac` no
piso) e a alternativa (dívida sem piso) faria a dívida crescer sem que nada
mudasse, o que é pior porque é invisível.

## 5. Validação rápida (1 semente — nada aqui é afirmação)

`Reativo, P=512, G=10, T_evo=600, R=4, 1 semente, avaliação 1200 passos ×
128 réplicas × 3 cidades (1000+)`. JSONs em
`/media/llm-data/universe-runs/neuromod-lab-taxi/e15/`. Modo: compile.
**Ruído de referência (regra 13): ±1.5 de fit e ±8 pp de mortos entre
sementes.** Só efeito ≫ isso merece uma frase.

| braço | fit | ent | mortos | panes | posto | oficina | res~ | carga fiscal | div_frac | div_max |
|---|---|---|---|---|---|---|---|---|---|---|
| corpo (sem economia) | **2.79** | 6.4 | 0.28 | **5.9** | **12.2** | 4.9 | 35.8 | – | – | – |
| economia | −1.76 | 5.3 | 0.58 | 18.2 | 4.2 | 4.0 | 23.5 | 0.78 | 0.31 | 12.4 |
| economia rico (aluguel 3) | −1.58 | 4.0 | 0.45 | 14.1 | 7.8 | 3.4 | 25.2 | 0.70 | 0.22 | 5.8 |
| economia pobre (aluguel 10) | −2.25 | 4.2 | 0.67 | 16.0 | 7.9 | 2.4 | 25.9 | 0.99 | 0.32 | 17.2 |
| economia sem juros | −2.04 | 3.6 | 0.54 | 14.3 | 7.1 | 2.5 | 23.2 | 0.92 | 0.28 | 9.9 |

Decomposição (fase b, mesmas condições):

| braço | fit | ent | mortos | panes | posto | res~ | carga |
|---|---|---|---|---|---|---|---|
| economia só imposto (aluguel 0) | −2.91 | 4.6 | 0.64 | 20.1 | 6.1 | 19.6 | 0.44 |
| economia só aluguel (alíquota plana .18, preço 1.0) | −3.05 | 4.1 | 0.59 | 19.7 | 6.6 | 17.1 | 0.84 |
| **economia kcal 0** (reboque não cobra caloria) | **0.89** | 6.6 | 0.40 | **12.2** | 8.7 | 26.0 | 0.66 |
| economia kcal 3 | −2.47 | 4.1 | 0.61 | 17.9 | 4.6 | 20.0 | 0.80 |
| **economia só gordura** (kcal 1, resto em VIDA) | **0.92** | 6.8 | 0.65 | **12.5** | 8.1 | 24.2 | 0.63 |
| **economia só gordura, kcal 3** | **3.37** | 7.7 | 0.64 | **6.0** | 10.2 | 36.6 | 0.57 |

### 5.1 O achado: o guincho calórico cobra na moeda errada (regra 12, de novo)

O que mais custa neste mundo **não é o dinheiro — é a caloria do guincho, e
por um mecanismo que os próprios negativos do lab previam**:

- Ligar a economia inteira leva as panes de **5.9 → 18.2** (3×) e derruba as
  visitas ao posto de **12.2 → 4.2** (−66%).
- Tirar só o dinheiro (braço `só imposto`: aluguel 0, dívida praticamente
  inexistente — `div_max` 1.6, `div_frac` 0.11) **não conserta nada**: 20.1
  panes. Logo o colapso do posto **não** é falta de dinheiro.
- Tirar só a caloria do guincho (`kcal 0`) leva as panes a 12.2 e o fit a
  +0.89 (de −1.76).
- Mandar o que a gordura não cobre para a **VIDA** em vez do tanque
  (`KCAL_VIDA=1`) dá o mesmo resultado com kcal=1 (12.5 panes) e, com kcal=3,
  **volta ao patamar do mundo sem economia** (6.0 panes, posto 10.2,
  gordura 36.6, fit 3.37).

**Mecanismo:** o guincho entrega a ração exata pra rastejar até o posto
(`pf = 1.31·d_posto + 2`, ~13% de margem). Cobrar caloria do **tanque** logo
depois come essa margem: o ser não chega ao posto e pane de novo. É a
**regra 12 na moeda calórica** — a multa cobrada na mesma moeda que compra a
recuperação vira espiral, não seleção. É a terceira aparição da lei da moeda
cruzada (EXP10 → N16 dinheiro → aqui, combustível). A gordura é moeda
diferente; o tanque não é.

O corolário desagradável: com a gordura vazia, "gordura primeiro, tanque
depois" **é** cobrar do tanque. Só a versão que nunca toca no tanque
(gordura → vida) respeita a regra.

### 5.2 Placar das predições

| # | veredito | número |
|---|---|---|
| 46 identidade | ✓ | portão 7.9740/25.1302; economia neutra == desligada bit a bit (8 tensores) |
| 47 mundo não morre / fit cai 1–3 | ✓ ent (5.3/6.4 = 83%; 5.8/6.1 = 95% em G=20) · **✗ fit** | cai 4.6, não 1–3 |
| 48 pobre_frac sobe, div_frac > .05 | ✓ | 0.33 → 0.55; div_frac 0.21–0.32 |
| 49 div_max bimodal | **✗** | percentis 0 / 7 / 11 / 17 / 42: espalhado, não bimodal. p0=0 e p100=42 no MESMO genoma: a desigualdade vem do acaso das primeiras panes |
| 50 pobre mata mais que rico | ✓ | 0.67 vs 0.45 = **+22 pp** (previsto ≥ +5). Ressalva registrada valeu: panes NÃO acompanharam (16.0 vs 14.1) |
| 51 juros são segunda ordem | ~ | fit −0.28, mortos −4 pp — dentro do ruído de 1 semente, não dá pra separar de zero |
| 52 espiral de combustível do guincho calórico | **✓ e maior que o previsto** | já em kcal=1 (18.2 panes vs 12.2 sem); §5.1 |
| 53 carga fiscal 20–40% / regressiva | **✗ nível** · ✓ direção | 78% no padrão (não 20–40%); regressiva 2×: rico 0.70 vs pobre 0.99 (+29 pp, previsto ≥10) e cai 0.78 → 0.68 quando o campeão melhora (G=10 → G=20) |
| 54 `e_preco_local` com peso positivo | **não decidível** | ver 5.3 |
| 55 `e_divida` inerte | **não decidível** | ver 5.3 |
| 56 origem não é explorável | ✓ | entregas por faixa de preço: 0.342 / 0.346 / 0.312 (barato/médio/caro) — uniforme; tempo por faixa idem (0.30–0.35) |

### 5.3 O controle que o próprio experimento entregou (54/55)

O braço `corpo (sem economia)` é o **controle de deriva perfeito** para as duas
features novas: lá elas valem exatamente zero, então o peso que a evolução lhes
dá é ruído puro. Em G=10 esse ruído foi `e_divida +0.33` e `e_preco_local
+0.27`. Os pesos do braço com economia (−0.68 / −0.73; no `pobre`, +1.74) estão
na mesma faixa. **Com 1 semente e 10 gerações não dá para distinguir uso de
deriva** — é a regra 15 (gene novo precisa de escala) somada à regra 13.
Medir de verdade: 5 sementes, G=60, e comparar |peso| contra o mesmo peso no
braço sem economia (o gene inerte é o próprio controle).

### 5.4 O que NÃO foi validado

- Nada com n ≥ 5 sementes nem 6 cidades: **nenhuma linha acima é afirmação**
  (regra 13). Mortalidade, em especial, é bimodal e ±8 pp.
- `R=4` e `pena_morte=0` ⇒ **a morte é invisível à seleção** (N18/regra 14).
  Isso contamina justamente a leitura de `mortos` do §5.1: o braço
  `só gordura kcal 3` tem o melhor fit (3.37) e 0.64 de mortos — ele
  converte vida em entrega porque o fitness não vê a vida. A bateria séria
  tem que ser R=16 + pena, ou o veredito do guincho calórico sai invertido.
- Fase c (distritos fixos × sorteados × cidade plana) não rodou.
- 10 dias, cidades 2000+, ReativoNoite24: não rodaram.
- Um travamento de GPU (`Memory access fault`) ocorreu uma vez ao iniciar uma
  rodada compilada, com 3 outros agentes na mesma placa; o mesmo comando
  passou na repetição e o caminho novo foi verificado em eager. Não achei
  causa no código — registrado, não explicado.

## 6. Decisões pro Leonardo

1. **Trocar a moeda do guincho (o único item urgente).** `gordura → tanque`
   (o que foi pedido) recria a espiral: 18.2 panes contra 6.0 de
   `gordura → vida`. Deixei o pedido como **default** (`KCAL_VIDA=0`) porque
   1 semente não muda default (regra 13), e o modo moeda-cruzada atrás de
   `cfg.KCAL_VIDA`. Recomendo `kcal_vida=1` (e aí `kcal` pode subir pra 3)
   assim que a bateria de 5 sementes confirmar.
2. **Aluguel 6+2/dia é pesado**: 42% da renda bruta de um campeão fraco. Não é
   arbitrário — é o que faz a economia ser regressiva e separar competente de
   incompetente (predição 53) — mas se a bateria séria mostrar carga > 60% no
   campeão de G=60, baixar para 4+1.
3. **Crédito.** Hoje "no vermelho ninguém fia" sai de graça dos portões que já
   existiam. É mais duro do que o pedido ("bloqueado abaixo do limite"): o
   comércio fecha abaixo de ZERO, não abaixo de −60. Se o objetivo for
   *sempre poder trabalhar pra sair do buraco*, o posto tem que fiar até o
   limite — e isso exige mexer em `serv_need`, que está fora dos blocos E15.
   Não mexi. É o item nº 1 do E19.
4. **Feature por vizinho.** Sem um slot por candidato de movimento, imposto
   pela origem e preço por distrito não viram comportamento (predição 56 ✓).
   Casa com o achado do E14 (a alavanca que faltava era um PRODUTO de dois
   sinais, não mais um escalar): o E17 é o lugar.
