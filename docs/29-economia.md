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

## 5. Validação rápida

*(preenchido depois de rodar — números honestos, 1 semente)*
