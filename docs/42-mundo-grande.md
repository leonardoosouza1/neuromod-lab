# 42 — E42 MUNDO: a cidade grande (agente MUNDO da spec 41 §2)

**Spec:** `docs/41-cidade-grande.md` §1 (contratos) e §2 (agente MUNDO).
**Código:** `src/cidade_grande.py`, `src/e42_mundo.py`, blocos `[E42 mundo]` em
`src/lab.py`, nomes em `src/rodar.py`/`src/destilar.py`.
**Saídas:** `/media/llm-data/universe-runs/neuromod-lab-taxi/e42/`.

Pedido do Leonardo no meio do caminho (2026-09-03): *"cidades MUITO maiores,
~500 nós — vamos pôr o modelo pra suar"*. Então `n` virou parâmetro (104 / 250 /
500) e a fumaça rodou nas duas pontas (104 e 500).

---

## 1. O que foi feito

### 1.1 Cidade grande (`src/cidade_grande.py`)
`gerar_cidade_grande(seed, n=104, max_saltos=6)` = `lab.gerar_cidade(seed, n)`
(que já escala serviços com `esc_n = n/26`) + duas garantias que a cidade grande
exige e a de 26 nós não exigia:

- **conexo**: `conectar()` liga componentes separadas pelo par de nós mais
  próximo (respeitando `GMAX=5`) e refaz `A/W/DI/grp/tem` pela mesma regra do
  gerador. Em 60 sementes de n=104 e 7 de n=250/500 **nunca foi preciso** — a
  verificação fica porque `DI` entre componentes vale `1e6` e isso envenenaria
  em silêncio toda feature de distância.
- **d_posto ≤ 6 SALTOS**: `postos_ate()` acrescenta posto no nó mais longe (BFS
  em saltos, ideia do E34) até o máximo cair a 6. **Foi preciso**: em 60
  sementes de n=104, 7 passavam de 6 saltos (máx 11, seed 1026). Sem isso a
  cidade grande mataria por geometria, não por mérito (é o negativo do E34).

Custo: numpy no host, **fora do laço** — 0,02 s (n=104) e 0,31 s (n=500) por
cidade, uma vez por rodada.

### 1.2 Distritos (D escala com n)
`D = round(6·√(n/104))` → **6** (n=104), **9** (n=250), **13** (n=500):
densidade de distritos por área constante. A partição continua sendo o k-means
determinístico que o `Lote` já fazia (semente por ponto-mais-distante + 8
Lloyd); o que mudou no `lab.py` foi só passar a **exigir tabela com D linhas**
(antes D=3 estava embutido nas tuplas `ALIQ`/`PMUL`).

Tabela por distrito, determinística pela seed (`tabela_distritos(D, seed)`),
**estratificada** (uma amostra por faixa de 1/D, embaralhada):

| grandeza | faixa (spec) | média com D=6 / 9 / 13 |
|---|---|---|
| alíquota | .05 – .35 | 0,195 / 0,196 / 0,199 |
| multiplicador de preço | ×0,70 – ×1,60 | 1,172 / 1,165 / 1,152 |
| multiplicador de aluguel | ×0,50 – ×2,00 | 1,260 / 1,244 / 1,249 |

> **Por que estratificado:** a 1ª versão sorteava uniforme e, com D=6, saiu
> aluguel médio **1,55 e nenhum distrito barato** — o custo MÉDIO da cidade
> virava sorte da semente e contaminaria qualquer comparação com o mundo do
> E20, além de mudar de nível entre n=104 e n=500. Estratificado, a média é o
> meio da faixa em qualquer D e a **heterogeneidade** (que é o ponto dos
> distritos) fica garantida.

**Decisão declarada (desvio da spec §2.2):** a tabela é por **rodada** (fica na
`cfg`), não por cidade. A mesma `cfg` serve as 4 cidades de treino e as 3 de
teste (listas de tamanhos diferentes), então uma tabela `(NC,D)` não caberia
num `cfg` único sem quebrar `rodar(A, W, teste, cfg)`. O que varia por
cidade/mundo é **qual distrito recebe cada linha** — e isso o E15 já sorteia
POR MUNDO (`dist_sorteia`), que é a lei oculta: a geografia do preço não se
decora entre episódios.

### 1.3 Passageiro que cruza distrito (`cfg.pax_cruza`, default 0)
`Lote._spawn_destino(origem)`: destino ~ **1/(1+d)**, nunca o próprio nó, com no
mínimo `pax_cruza` (=0,30 no preset) da massa em **outro distrito**. Reescala
exata: se a massa que já cruza é ≥ f não mexe; senão multiplica o lado de fora
por `f/P_fora` e o de dentro por `(1−f)/(1−P_fora)` — a fração fora fica
exatamente f sem deformar o 1/(1+d) dentro de cada lado. Sorteio por
Gumbel-argmax em `(B,n)` na GPU (multinomial faz sync).

Dois cuidados que valem citar:
- **excluir o próprio nó** é obrigatório: com peso 1/(1+d), d=0 é o MAIOR peso —
  o passageiro que "vai pra lugar nenhum" pagaria a tarifa base na hora, de
  graça. Era uma bomba de dinheiro grátis.
- o `randint` antigo **continua sendo consumido** mesmo com a flag ligada: o
  stream do mundo (congestão, spawn de origem, avarias) fica idêntico ao do
  braço sem a flag; só o destino muda.

### 1.4 Tarifa pelo distrito de ORIGEM (`cfg.tarifa_distrito`)
`tarifa = base × distância × multiplicador de preço do distrito de origem`,
aplicado em `br` **antes** do imposto. O imposto pela origem já era do E15 (a
correção `corr`), então nada foi duplicado: quem embarca no distrito caro paga
mais e o fisco leva a alíquota de lá.

### 1.5 Moradia (`cfg.moradia`)
- `m.casa` = distrito do nó onde **nasceu** (v1, não muda na vida).
- **aluguel** cobrado à meia-noite passa a ser `ALUGUEL × ALUGUEL_D[casa]`
  (0,5–2,0): morar no distrito caro custa até 4× o do barato. Cobrado pela
  CASA, não por onde o ser está.
- **descanso**: dentro do distrito-casa é como hoje (grátis — o aluguel já foi
  pago); fora custa **`HOTEL` (=8) × fator de preço do distrito**, entrando no
  mesmo `gasto` do E15, logo pagando o imposto local como qualquer compra.
- **dormir na rua não repõe** (`cfg.rua_nao_dorme`): a parada por fadiga
  (fad ≥ 95 → 40) só devolve o corpo **de dia ou dentro do distrito-casa**. À
  noite e fora de casa o ser perde os 12 passos e acorda cansado; o descanso
  pago (casa ou hotel) vira a única forma de zerar fadiga à noite.
- **sentidos novos** nos slots reservados: `e_em_casa` (1 se está no
  distrito-casa) em `h_gl0` e `e_aliq_local` (alíquota do distrito atual,
  **normalizada 0..1** pela faixa da tabela — regra 15: escala do gene) em
  `h_gl1`. Os slots são compartilhados com as glândulas (E16) e nunca rodam
  juntos: `cfg.glandulas` tem prioridade, `cfg.moradia` preenche quando as
  glândulas estão desligadas, e sem nenhum dos dois continuam zero.

> **Limite conhecido dos dois sentidos novos** (vale registrar antes da
> bateria): na política do `Reativo` as features de ESTADO são iguais em todos
> os vizinhos, então `e_em_casa`/`e_aliq_local` **não sabem apontar direção** —
> só deslocam "mover" contra "servir" em bloco. `e_em_casa` consegue codificar
> "quando estou em casa, prefira o serviço (dormir)"; o que ninguém consegue
> expressar ainda é "**vá** pra casa" (faltaria um `d_casa` por vizinho). Isso é
> matéria da fase 2 / do agente CÉREBRO, e está declarado aqui como o que ficou
> de fora.

### 1.6 Preset e runner
- `cfg_cidade_grande(n=104, D=None, seed_tabela=0, moradia=True, hotel=8.,
  pax_cruza=.30, tarifa_distrito=True, rua_nao_dorme=True, fome=.15,
  refeicao=90., comida_no_posto=True, **kw)` = `cfg_pacote` do E19d/E20 + tudo
  acima. `--sem-moradia` no runner devolve a cidade grande **sem** moradia
  (controle).
- `src/e42_mundo.py` (molde do `e34_posto_denso.py`): troca `gerar_cidade`,
  `cfg_pacote` e `telemetria` do runner do E20 e roda 3 braços — **direto**
  (`Reativo`), **reações** (`ReativoReacoes`) e **mínimo 3**
  (`minimo.fabrica(['d_alvo','d_posto','e_fuel'])`, o campeão empatado do E23).
  `--n` (104/250/500), `--D`, `--P/--G/--T-evo/--T-aval` para fumaça. Teste-seed
  1000+ gera cidades grandes pela MESMA regra.

### 1.7 Flags e defaults (o que o integrador precisa saber)

| flag em `Cfg` | default (= hoje) | no `cfg_cidade_grande` | o que faz |
|---|---|---|---|
| `moradia` | `False` | `True` | casa, hotel, `e_em_casa`, `e_aliq_local` |
| `HOTEL` | `8.` | `8.` | preço base da diária fora de casa |
| `ALUGUEL_D` | `None` (=1.0) | tabela (D,) 0,5–2,0 | aluguel por distrito da casa |
| `rua_nao_dorme` | `False` | `True` | parada por fadiga não repõe à noite fora de casa |
| `pax_cruza` | `0.` | `0.30` | piso de destino em outro distrito |
| `tarifa_distrito` | `False` | `True` | tarifa × preço do distrito de origem |
| `D_DIST` | `3` | `round(6√(n/104))` | distritos (tabela tem de ter D linhas) |

Com as 4 primeiras desligadas o `lab.py` é **bit a bit** o de antes (teste 2 de
`src/cidade_grande.py`, mais o portão do perito e o `testes_e15.py`).
`cfg.moradia=True` **exige** `cfg.economia=True` (os distritos são do E15) — o
`Lote` levanta erro claro em vez de rodar errado. As 4 flags dependem de
`e15_dist`/`e15_rank`, então quem ligar moradia sem economia tem erro, não
silêncio.

### 1.8 Contratos da spec §1
- **Flag desligada = identidade bit a bit**: as 4 flags nascem desligadas em
  `Cfg`; nada aloca, nada sorteia, nenhum draw se desloca (o gerador `g42` é
  próprio e o `randint` do destino continua sendo consumido).
- **Zero sync no laço quente**: nenhuma linha nova usa `.item()`, `float()` ou
  `if tensor`; o sorteio do destino é Gumbel-argmax.
- **Nada em /tmp**; saídas em `/media/llm-data/universe-runs/neuromod-lab-taxi/e42/`.
- Edições em `lab.py` só em blocos `[E42 mundo]` (mais 3 inserções marcadas
  dentro do bloco do E15, onde os distritos moram).

---

## 2. O que ficou de fora (e por quê)

| ficou de fora | por quê |
|---|---|
| tabela de preços POR CIDADE | a `cfg` é compartilhada entre 4 cidades de treino e 3 de teste (tamanhos diferentes); a lei oculta já existe na permutação por mundo do E15 (§1.2) |
| `d_casa` (distância até o distrito-casa) por vizinho | é feature nova de MOVIMENTO, muda `NF` e o genoma — quebraria a comparação com todos os campeões salvos; é a peça que falta pro ser saber **ir** pra casa (fase 2) |
| mudar de casa (mudança/aluguel escolhido) | v1 da spec é "distrito de nascimento"; sem `d_casa` o ser nem sabe voltar, mudar seria decidir no escuro |
| profissões, prefeito, várias cidades | fase 2 da spec §4 |
| bateria honesta (G=120, 5 sementes, R=16) | a spec manda rodar depois do merge, na fila; aqui só fumaça |
| gate por dinheiro no hotel | o hotel pode empurrar pra dívida (piso −LIMITE, com juros, e `divida_mata`); barrar o descanso do quebrado criaria uma segunda espiral de morte — preferi a dívida, que já tem preço |

---

## 3. PREDIÇÃO 49 — registrada ANTES de qualquer bateria

> **49 (da spec):** na cidade grande, o **mínimo-3 perde ≥ 1,0 de fit** pro
> cérebro completo.

**Minha estimativa numérica (também antes de rodar): a 49 vai ser REFUTADA em
n=104 — o gap fica em +0,3 a +0,6 de fit (mínimo-3 abaixo do direto), e em
n=500 em 0,0 a +0,3.** Mecanismo, para poder errar por escrito:

1. No E23 honesto (n=26) mínimo-3 **empatou** (6,91 vs 6,90). O que a cidade
   grande acrescenta é sobretudo **preço/dinheiro**, e as decisões de dinheiro
   moram nos **6 pesos de serviço**, que o mínimo-3 **mantém intactos** (ele só
   cancela features de MOVIMENTO).
2. Das features que ele perde, as caras na cidade grande são `d_descanso`
   (achar onde dormir) e `e_em_casa` (dormir em casa). `d_comida` quase não
   conta: com `comida_no_posto=True` a comida segue o posto, e `d_posto` o
   mínimo-3 tem.
3. Genoma maior = busca maior: em G=120 o direto gasta parte da vantagem
   procurando (foi o que o E28/"enxuto" já mostrou).
4. Em n=500 a viagem média dobra (DI máx 21,5 → 44,0), as entregas por vida
   caem e o fitness **comprime**: um gap de 1,0 fica aritmeticamente mais
   difícil.

**Cláusula de refutação da minha estimativa:** se o gap vier ≥ 1,0, a cidade
grande virou o mundo em que **expressividade paga** — e a prova terá de
aparecer no retrato: peso não-trivial em `d_descanso`, `e_em_casa` ou
`e_preco_local` em ≥ 3/5 sementes. Se vier ≥ 1,0 **sem** peso nessas features,
o que mudou foi a busca, não a expressividade.

---

## 4. Verificação (portões) — saída colada

### (a) `NM_COMPILE=0 python src/rodar.py --perito`
```
--- portao de validacao ---
  arquitetura    PERITO  aleatorio   razao  avarias
  reativo           5.4        0.5   11.4x     29.1
  banco EMA         5.4        0.5   11.7x     29.1
  diadica           5.4        0.6    8.9x     29.1
  corpo             5.4        0.6    9.2x     29.1
  hibrido           5.4        0.6    9.7x     29.1
  mem custo         5.4        0.5   11.2x     29.1
  mapa servico      5.4        0.6    8.4x     29.1

  PASSOU: as 7 batem (spread 0.000)
```

### (b) `NM_COMPILE=0 python src/testes.py`
```
--- testes de equivalencia ---
  (sem caminho do lab antigo: pulando equivalencia da diadica)
  5 arquiteturas deterministicas (base)  OK
  5 arquiteturas deterministicas (cego)  OK
  5 arquiteturas deterministicas (hotspot)  OK
  5 arquiteturas deterministicas (mare)  OK
  5 arquiteturas deterministicas (ruas)  OK
  5 arquiteturas deterministicas (semgps)  OK
  evoluir_juntas == evoluir isolado (bit a bit, 2 arqs)  OK
  evoluir_sementes deterministico (2 sementes)  OK
ok
```
E o portão do E15 (a economia é onde eu mexi), `NM_COMPILE=0 python src/testes_e15.py`:
```
--- testes E15 (economia) ---
  portao perito base: ent 7.9740 av_fuel 25.1302  OK
  economia neutra == economia desligada (8 tensores, bit a bit)  OK
  fumaca economia (3 arqs, sem NaN)  OK
  divida no piso: min(dinh) -40.00 >= -40, div_max medio 36.2  OK
  imposto pela ORIGEM: 8/8 corridas cruzaram distrito, todas pagaram a aliquota da origem  OK
ok
```

### (c) `NM_COMPILE=0 python src/cidade_grande.py` (geometria + identidade + SEM SYNC)
```
--- E42 cidade grande: testes ---
  n=104 D=6  conexo, d_posto<=6 saltos, distritos nao-vazios (seed 1026: {'seed': 1026, 'n': 104, 'arestas_add': 0, 'postos_add': 1, 'hop_posto_max': 6, 'postos': 13, 'D': 6, 'nos_por_distrito': [20, 19, 16, 18, 21, 10]})  OK
  n=500 D=13 conexo, d_posto<=6 saltos, distritos nao-vazios (seed 1026: {'seed': 1026, 'n': 500, 'arestas_add': 0, 'postos_add': 0, 'hop_posto_max': 5, 'postos': 58, 'D': 13, 'nos_por_distrito': [36, 43, 38, 38, 33, 37, 36, 50, 35, 42, 37, 38, 37]})  OK
  flags E42 desligadas == mundo do E20 com D=6 (bit a bit, 10 campos)  OK
  moradia LIGADA muda o mundo (ent 0.53 -> 0.81; hotel 0.44; casa_frac 0.31)  OK
  n=104: 10 passos sem NENHUM sync CPU<->GPU  OK
  n=500: 10 passos sem NENHUM sync CPU<->GPU  OK
ok
```

### (d) Fumaça de evolução — P=256, G=10, T_evo=600, R=1, 1 semente, `nice -n 5`
```
$ nice -n 5 python src/e42_mundo.py --preset triagem --P 256 --G 10 --T-evo 600 \
      --T-aval 600 --R 1 --seeds 0 --n 104 --tag _f104
== E42 cidade grande | n=104 D=6 | {'seed': 0, 'n': 104, 'arestas_add': 0, 'postos_add': 0,
   'hop_posto_max': 5, 'postos': 12, 'D': 6, 'nos_por_distrito': [18, 13, 26, 17, 15, 15]}
   aliquotas (0.2673, 0.209, 0.1619, 0.3076, 0.0891, 0.1336)
   precos    (0.8377, 0.9166, 1.2363, 1.114, 1.3768, 1.5486)
   aluguel   (1.9785, 1.5553, 0.9773, 1.1783, 0.5307, 1.3383)
== E20 corpo fala | triagem P=256 G=10 R=1 x1 | pena 5.0 ==
  direto (Reativo)     NP  44 fit  -1.11 [-1.107] ent   1.7 mortos 0.49 [0.487] fome_fim   89 panes  5.1 posto  2.1 (61s)
  reacoes              NP  51 fit  -2.18 [-2.182] ent   0.1 mortos 0.24 [0.237] fome_fim   87 panes  3.0 posto  1.7 (40s)
  minimo 3 (d_alvo, d_posto, e_fuel) NP  44 fit  -0.85 [-0.846] ent   2.4 mortos 0.29 [0.294] fome_fim   65 panes  4.2 posto  1.1 (44s)
TOTAL 146s

$ ... --n 500 --tag _f500
== E42 cidade grande | n=500 D=13 | {'seed': 0, 'n': 500, 'arestas_add': 0, 'postos_add': 0,
   'hop_posto_max': 6, 'postos': 58, 'D': 13,
   'nos_por_distrito': [33, 48, 41, 46, 37, 36, 33, 39, 44, 34, 41, 37, 31]}
   aliquotas (0.1234, 0.1956, 0.2789, 0.1016, 0.1503, 0.3214, 0.2472, 0.0886, 0.1689, 0.291, 0.3402, 0.0681, 0.2171)
   precos    (0.7937, 0.7494, 0.8538, 1.0334, 1.0697, 0.971, 1.182, 1.4021, 1.3497, 1.232, 1.2564, 1.5978, 1.4861)
   aluguel   (1.8109, 1.1333, 1.6809, 1.6339, 1.5034, 0.5488, 1.8855, 1.0035, 1.2583, 0.7885, 0.9412, 0.6366, 1.4085)
  direto (Reativo)     NP  44 fit  -2.63 [-2.626] ent   0.0 mortos 0.31 [0.312] fome_fim   94 panes  4.3 posto  2.1 (40s)
  reacoes              NP  51 fit  -2.42 [-2.419] ent   0.0 mortos 0.13 [0.133] fome_fim   78 panes  3.0 posto  2.3 (45s)
  minimo 3 (d_alvo, d_posto, e_fuel) NP  44 fit  -1.73 [-1.73] ent   1.2 mortos 0.27 [0.268] fome_fim   76 panes  6.6 posto  1.1 (46s)
TOTAL 132s

$ ... --n 104 --sem-moradia --tag _f104ctrl    (CONTROLE: cidade grande SEM moradia/hotel/destino cruzado)
  direto (Reativo)     NP  44 fit  -1.34 [-1.336] ent   1.3 mortos 0.36 [0.359] fome_fim   88 panes  5.1 posto  1.9 (36s)
  reacoes              NP  51 fit  -2.01 [-2.007] ent   0.0 mortos 0.12 [0.122] fome_fim   85 panes  2.5 posto  1.2 (37s)
  minimo 3 (d_alvo, d_posto, e_fuel) NP  44 fit  -0.99 [-0.995] ent   1.2 mortos 0.38 [0.378] fome_fim   92 panes  3.8 posto  4.5 (40s)
TOTAL 113s

$ CONTROLE DE ORCAMENTO: mundo do E20 (n=26, D=3), mesmos 3 bracos, mesmo P/G/T
  direto (Reativo)     NP  44 fit   0.63 [0.631] ent   3.3 mortos 0.28 [0.281] fome_fim   81 panes  4.0 posto  3.2 (37s)
  reacoes              NP  51 fit   0.10 [0.098] ent   2.6 mortos 0.20 [0.203] fome_fim   86 panes  5.6 posto  0.2 (41s)
  minimo 3 (d_alvo, d_posto, e_fuel) NP  44 fit   2.54 [2.538] ent   5.8 mortos 0.17 [0.174] fome_fim   59 panes  5.9 posto  3.8 (44s)
TOTAL 123s
```

---

## 5. Leitura da fumaça

### 5.1 O que a fumaça NÃO mede
G=10, P=256, R=1, T=600, 1 semente, do zero. O **controle de orçamento** existe
para dizer isso com número: o MESMO braço direto, no MESMO mundo do E20 (n=26),
com o orçamento da triagem do doc 36 (R=8, G=40, T=1200, 3 sementes) dá **fit
4,85 / ent 9,4**; com o orçamento desta fumaça dá **fit 0,63 / ent 3,3**. Ou
seja: **nenhuma linha da tabela acima é veredito sobre arquitetura** — aqui se
mede que o mundo roda, responde e não explode.

### 5.2 O preço do tamanho (resposta ao pedido do n=500)
Mesmos 600 passos (2,5 dias), mesmo orçamento, braço direto:

| n | D | DI máx (média de 4 cidades) | entregas/vida | mortos | fit |
|---|---|---|---|---|---|
| 26 (E20) | 3 | 12,2 | **3,3** | 0,28 | +0,63 |
| 104 | 6 | 21,5 | **1,7** | 0,49 | −1,11 |
| 250 | 9 | 31,2 | (não rodado) | | |
| 500 | 13 | 44,0 | **0,02** | 0,31 | −2,63 |

**Sim: em n=500 as entregas por vida caem praticamente a zero** (0,02 no
direto, 0,01 em reações; só o mínimo-3 segurou 1,2). Como pedido, não mudei T —
reporto: a viagem média mais que dobra (DI máx 20 → 44) e uma vida de 600
passos não paga mais nem a primeira corrida com este orçamento de busca. O fit
vira quase só a pena de morte (−5·mortos) e as avarias: o que a evolução
enxerga em n=500 é **sobreviver**, não dirigir. Recomendação para a bateria
honesta em n=500: T_evo = T_aval ≥ 2400 (10 dias) **ou** medir taxa por dia em
vez de total — senão a cidade grande vira um mundo onde ficar parado é ótimo.

### 5.3 Armadilha paga no caminho (vale pra quem rodar a fila)
A 1ª fumaça rodou T_evo=600 com o T_aval=1200 padrão do E20 e deu **mortos
1,00 e fome_fim 100 nos três braços**. Não é bug: com `fome` subindo
0,32/passo e `fome_mata` só ferindo acima de 90, a inanição mata perto do passo
~1000 — a evolução em 600 passos **nunca vê a morte que a avaliação em 1200
cobra**. Com T_evo = T_aval a mortalidade cai para 0,24–0,49. Na bateria
honesta (T_evo = T_aval = 1200) o problema não existe; em qualquer triagem com
T menor, existe.

### 5.4 As três mecânicas novas estão vivas (telemetria, n=104 com moradia)
| grandeza | direto | reações | mínimo-3 | controle s/ moradia |
|---|---|---|---|---|
| `cruza_frac` (entregas que trocaram de distrito) | **0,65** | 0,24 | **0,63** | — |
| `casa_frac` (passos no distrito-casa; acaso = 1/6 = 0,17) | 0,37 | 0,55 | 0,21 | — |
| `n_hotel` (descansos pagos fora de casa) | 0,79 | 0,73 | 0,01 | — |
| `hotel_pago` (dinheiro) | 8,7 | 7,7 | 0,1 | — |
| `n_rua` (passos travados por fadiga à noite fora de casa) | 14,2 | 13,7 | 26,7 | — |
| `aluguel_agua` (por vida) | 22,2 | 23,3 | 23,0 | **18,8** |
| `div_frac` (fração da vida no vermelho) | 0,52 | 0,18 | 0,09 | 0,44 |

- o destino cruzado funciona **com folga**: ~2/3 das entregas trocam de
  distrito (o piso pedido era 30 %) — com distritos de ~17 nós em 104, o peso
  1/(1+d) já joga bastante massa pra fora sozinho;
- o aluguel por distrito encarece a vida ~20 % (18,8 → 22–23), que é exatamente
  o multiplicador médio 1,25 da tabela;
- **o ser prefere a rua ao hotel**: `n_rua` 14–27 passos contra `n_hotel` ≈ 0,8
  (e ≈ 0 no mínimo-3). Dormir na rua não custa dinheiro e o hotel custa
  8×fator; com este orçamento ninguém aprendeu a pagar. É o achado a vigiar na
  bateria honesta — se continuar assim, ou `HOTEL` está caro demais, ou falta o
  sentido que aponta **para** casa (§1.5), ou a fadiga não morde o bastante.

### 5.5 Moradia ligada ou desligada: diferença dentro do ruído
n=104, com vs sem moradia: direto **−1,11 vs −1,34**, reações −2,18 vs −2,01,
mínimo-3 **−0,85 vs −0,99**. Com 1 semente e G=10 (a régua do dia diz que nem o
honesto n=5 detecta menos de 0,65 de fit) isso é **empate**: a moradia encarece
a vida e acrescenta pressão sem quebrar o mundo. É o que a fumaça tinha que
provar.

### 5.6 Sinal precoce sobre a predição 49 (não é veredito)
Nos quatro mundos desta fumaça o **mínimo-3 ficou à frente do direto**: +1,91
(n=26), +0,26 (n=104), +0,90 (n=500), +0,34 (n=104 sem moradia) — sinal
CONTRÁRIO ao da 49. Cuidado com a leitura: com G=10 o que se mede é **busca**, e
genoma efetivo menor procura melhor. É exatamente a confusão que a bateria
honesta (G=120, 5 sementes, R=16) existe para desfazer — por isso a estimativa
da §3 fica registrada como está, sem ajuste depois de ver estes números.
