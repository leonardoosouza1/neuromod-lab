# 43 — E42 agente CÉREBRO: `SerCamadas`, o cérebro em camadas (2026-09-03)

**Leonardo:** *"o cérebro em camadas, cada parte com sua função — tálamo, córtex, memória."*

Entrega da §3 do doc 41. Arquivos novos: `src/camadas.py` (a arquitetura),
`src/testes_e42.py` (portão), `src/e42_cerebro.py` (runner). Edição aditiva e
rotulada `# [E42 cerebro]` em `src/retrato.py`. **`lab.py` não foi tocado.**

`SerCamadas(ReativoReacoes)` **nasce bit a bit igual ao pai** e ganha três camadas
com genes próprios, cada uma ligável pela evolução e cada uma transparente no
nascimento — não só com o genoma do perito, mas com **qualquer** genoma (§4a).

---

## 1. Mapa de genes (índices exatos)

Herdados, intocados — `NOMES_F` de `src/rodar.py` + os 7 do E29b:

| índices | o quê |
|---|---|
| 0–25 | as 26 features de `obs()` (`d_alvo` … `bias`) |
| 26–31 | `sv_posto`…`sv_bias` (`NF`…`NF+5`) |
| 32–37 | `mem_0..5` (`NF+6`…`NF+11`) — **32,33,34 deixam de ser mortos aqui** |
| 38–43 | `corpo_0..5` (`NF+12`…`NF+17`) — seguem mortos |
| 44–50 | reflexo E29b: `tau_sede, tau_fome, w_sede, w_fome, v_sede, v_fome, portao` |

Novos (41 genes, `NP = 92`):

| camada | índices | genes |
|---|---|---|
| **TÁLAMO** (15) | 51–65 | 5 grupos × `(a, b, c)`: rota 51/52/53 · serviços 54/55/56 · corpo 57/58/59 · economia 60/61/62 · tempo 63/64/65 |
| **CÓRTEX** (24) | 66–89 | 6 distritos × 4 features, na ordem `d_alvo, d_posto, custo_rua, e_preco_local`: d0 66–69 · d1 70–73 · d2 74–77 · d3 78–81 · d4 82–85 · d5 86–89 |
| **HIPOCAMPO** (2) | 90, 91 | `hip_tau`, `hip_ganho` |

`nomes_genes()` em `camadas.py` devolve os 41 nomes; `retrato.py` já os usa.

### Grupos de sentidos do tálamo (cobertura exata das 26 features, `assert` no import)

| grupo | índices | features |
|---|---|---|
| rota | 0,1,2,3 | `d_alvo custo_rua congestao semaforo` |
| serviços | 4–8 | `d_posto d_comida d_descanso d_oficina d_loja` |
| corpo | 9–14, 20 | `e_fuel e_fome e_fadiga e_pneu e_temp e_oleo` + `e_dano` |
| economia | 15, 17, 21, 22 | `e_dinheiro e_reserva e_divida e_preco_local` |
| tempo | 16, 18, 19, 23, 24, 25 | `e_tem_pax h_sin h_cos h_gl0 h_gl1 bias` |

---

## 2. Como cada camada nasce desligada

Tudo entra por `extra()`, como **diferença** em cima do escore que `um_passo`
já calcula (`sc = F @ W[:NF] + extra`), para não precisar tocar em `lab.py`.

1. **Tálamo** — `gate_g = 2·sigmoid(a_g + b_g·necessidade_dominante + c_g·carregando)`.
   Genes 0 ⇒ `2·sigmoid(0) = 1.0` **exato** em float32 ⇒ `(gate−1) = 0.0` exato ⇒
   contribuição `F @ (W·(gate−1))` é exatamente zero.
   `necessidade_dominante` é a mesma do `SerVital`/`SerTalamo` do lab
   (`max` de sede, fome, fadiga, pneu, temperatura).
2. **Córtex** — `δ = 0.5·tanh(gene)`. `tanh(0) = 0` exato ⇒ `F·w·δ = 0`.
   O `0.5` é teto de alavanca (regra 5 / N9: no EXP10 o ganho 8.0 destruiu tudo);
   com δ saturado, `w_ef ∈ [0.5·w, 1.5·w]`.
3. **Hipocampo** — a memória nasce em zero **e** há um ganho mestre
   `hip_ganho = tanh(gene)`, 0 exato no nascimento. O ganho existe porque
   `mem_0..2` são genes **velhos**: sem ele, um genoma aleatório com peso de
   memória não-nulo deixaria de ser idêntico ao pai assim que a memória saísse de
   zero — e a regra 17 pede identidade para *qualquer* genoma, não só o do perito
   (é exatamente o que o teste `test_identidade_aleatoria` cobre).

**Composição** tálamo × córtex é **aditiva**: `w·gate + w·δ` (e não `w·gate·(1+δ)`).
A diferença é de segunda ordem (`w·δ·(gate−1)`), é mais barata e ambas as camadas
continuam nascendo em zero. Declarado como decisão, não como acidente.

---

## 3. Hipocampo: o que é lembrado, quando, e por quem

`MEM` é `(B, 6, 3)`: 6 distritos × 3 slots. `τ = 1 + 200·sigmoid(gene − 4)` — mesma
forma do `tau` do E29b, então **nasce rápido** (~4,6 passos), que foi a lição da
triagem 2 do E20 (nascer lento fazia a "sede" ficar alta 100 passos depois de abastecer).

A atualização é **EMA por evento**, `in-place` em `atualizar()` (fora do grafo), com
os eventos detectados por **diferença de estado do Lote** — nada de flag nova em `lab.py`:

| slot | evento | valor | distrito creditado |
|---|---|---|---|
| `mem_renda` | `m.rec` subiu ⇒ corrida entregue | Δ`m.rec`/50 | **origem** da corrida (`m.e15_dorig` do passo anterior — lido antes que o embarque do próprio passo o sobrescreva) |
| `mem_espera` | todo passo | `1` se sem passageiro e parado (`pd_<0 & rest<=0 & tpar<=0`) | distrito atual |
| `mem_preco` | pagou serviço | `(m.e15_d0 − m.dinh)⁺/30` — `e15_d0` é o saldo *antes* das compras, então a diferença é exatamente `gasto × fator do distrito` | distrito atual |

A leitura é o distrito **atual**: os 3 valores entram nos pesos `mem_0..2` que já
existiam. Como qualquer feature de estado (o bloco `est` de `obs()` é expandido igual
em todos os vizinhos), a contribuição é **constante em G**: desloca *mover-vs-servir*,
não a direção. Isso é uma limitação real, e é a razão da minha estimativa baixa na
predição 50 (§7).

Sem `cfg.economia` há um distrito só (índice 0) e `mem_preco` cai no fallback
`(dinh_anterior − dinh)⁺` — o slot fica mais pobre, mas vivo.

---

## 4. Verificação obrigatória (saída colada)

Ambiente: `export TORCHINDUCTOR_COMPILE_THREADS=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4`,
`nice -n 5`, GPU compartilhada (outro job em 99 % o tempo todo).

### (a) identidade bit a bit + (b) sem sync + alavancas + ativação

`NM_COMPILE=0 python src/testes_e42.py`

```
--- testes E42 (cerebro em camadas) | modo eager | cuda ---
  layout: pai 51 | talamo 51..65 | cortex 66..89 | hipocampo 90..91 | NP 92  OK
  IDENTIDADE perito+reflexo: (m1.ent - m2.ent).abs().max() == 0.0 (ent 1.94) e 6 campos do corpo  OK
  IDENTIDADE com 2 populacoes aleatorias (mem_* nao-nulo)  OK
  extra/extra_serv puras (5 chamadas iguais; Lote e o proprio ser intactos)  OK
  zero sync CPU<->GPU em 10 passos + ativacao()  OK
    talamo (fecha o grupo rota: a=-3)      ent      94.0 ->      26.0
    talamo (b do grupo corpo: +3)          ent     112.0 ->     108.0
    cortex (delta d0 x d_alvo: +3)         ent      94.0 ->      93.0
    hipocampo (ganho: +3)                  ent      94.0 ->      97.0
  4 alavancas vivas (talamo x2, cortex, hipocampo)  OK
  ativacao(): 18 chaves, todas tensores (B,), gate==1 e delta==0 no nascimento  OK
    seed 99: ent   0.61 panes 10.08 vida   56.8
    seed 100: ent   0.77 panes  9.23 vida   56.6
  fumaca com genomas aleatorios, sem NaN  OK
ok
```

A identidade é do jeito que o doc 41 pediu — perito com o reflexo ligado
(`W[:,44+2]=3.`, `W[:,44+6]=1.`), genes novos em zero:
`(m1.ent − m2.ent).abs().max() == 0.0`, e mais `av_fuel, vida, dinh, fome, res, avar`
todos com diferença exata 0. O sync foi checado no padrão dos runners: 5 passos de
aquecimento, `torch.cuda.synchronize()`, `set_sync_debug_mode('error')`, 10 ×
`um_passo(m,a,Wb); a.atualizar(m)` (+ uma chamada a `ativacao()`), volta a `'default'`.

**A alavanca do córtex mudou pouco (94 → 93)** porque o perito só passa por 3
distritos numa cidade de 26 nós e δ está limitado a 0,5. Ela é viva, não potente —
a cidade grande (D=6) é que vai dizer.

### (c) portões do lab (nada regrediu)

```
$ NM_COMPILE=0 python src/rodar.py --perito
  reativo           5.4 | banco EMA 5.4 | diadica 5.4 | corpo 5.4 | hibrido 5.4 | mem custo 5.4 | mapa servico 5.4
  PASSOU: as 7 batem (spread 0.000)

$ NM_COMPILE=0 python src/testes.py
  5 arquiteturas deterministicas (base/cego/hotspot/mare/ruas/semgps)  OK
  evoluir_juntas == evoluir isolado (bit a bit, 2 arqs)  OK
  evoluir_sementes deterministico (2 sementes)  OK
  ok
```

### (d) `torch.compile` não quebra

`extra()` é **pura de verdade**: não muta `m` nem o próprio ser (nenhum `setattr`),
não tem `.item()`/`float()`/`if` em tensor. A telemetria do tálamo/córtex é
**recalculada** em `atualizar()` (5 sigmoides e um gather), justamente para o grafo
não precisar exportar nada.

```
$ NM_COMPILE=1 python <chk_compile>
modo: compile
identidade sob compile: (m1.ent - m2.ent).abs().max() = 0.0
genoma cheio sob compile: ent 0.312 vida 57.83 finito True
```

### Custo do passo (o que a camada cobra)

`B = 4096` (P=256 × 4 cidades × R=4), 300 passos após aquecimento, GPU disputada:

| arquitetura | eager | compile |
|---|---|---|
| `reativo-reacoes` (NP 51) | 5,47 ms/passo | 1,18 ms/passo |
| `ser-camadas` (NP 92) | 7,41 ms/passo | **1,91 ms/passo (+62 %)** |

Metade desse custo é o `m.obs()` **recomputado** dentro de `extra()`: o tálamo
precisa das 26 features e `um_passo` não passa `F` para `extra`. `obs()` é pura
(nenhum gerador, nenhuma escrita), então recomputar dá exatamente o mesmo `F` — a
identidade bit a bit acima prova isso. **Não corrigi** porque o contrato do E42 diz
não tocar em `lab.py`; se a bateria honesta apertar, a correção é uma linha atrás de
flag (`a.extra(m, Wb, viz, F=F)` com `F=None` default = comportamento atual).
VRAM: 0,04 GB nos dois — a camada não muda a conta de memória.

---

## 5. Glândulas (item 4 do doc 41 §3): **fase 2, e o porquê**

`corpo_fala.py` **não cabe sem quebrar a identidade**, e o motivo é de projeto, não
de merge: o `SerCorpoFala` nasce *cancelando* as features do corpo (`extra()` subtrai
`(fc*W[:,IDX_CORPO]).sum()`) e a necessidade crua (`extra_serv` subtrai
`svn*W[:,NF:NF+5]`). Ele **é** um gargalo por construção — com genes zerados ele não
vira o pai, vira um ser cego para o corpo. Ligá-lo aqui exigiria um gene de mistura
(corpo cru ↔ hormônio) nascendo em "100 % cru", mais os ~90 genes da rede do corpo —
e o E20 já mostrou que sem *prior* 97 % morrem de fome nessa faixa de genes.

Enquanto isso, o corpo **já tem** glândulas ortogonais e ligáveis por cfg: as `GL_K=2`
do E16 vivem no `Lote` (`cfg.glandulas`), são alimentadas por déficits/eventos e o
cérebro as *sente* pelas features `h_gl0`/`h_gl1` — que estão no grupo **tempo** do
tálamo, ou seja, já são gateáveis por esta entrega sem nenhuma linha nova.

---

## 6. Fumaça (P=256, G=10, T=600, 1 semente, R=4 ⇒ B=4096)

Mundo atual: `cfg_pacote(fome=.15, refeicao=90., comida_no_posto=True)`, pena 5,
teste em 3 cidades ×128 réplicas. `NM_COMPILE=1`.

```
== E20 corpo fala | triagem P=256 G=10 R=4 x1 | pena 5.0 ==
  reacoes (pai)   NP  51 fit 1.00 [1.003] ent 3.1 mortos 0.16 [0.161] fome_fim 84 panes 3.7 posto 2.8 (31s)
  ser camadas     NP  92 fit 1.34 [1.342] ent 3.2 mortos 0.13 [0.128] fome_fim 83 panes 2.9 posto 3.0 (28s)
TOTAL 59s
```

`ativacao()` média do campeão de `ser camadas` (128 réplicas × 3 cidades, T=600):

| chave | valor | leitura em português |
|---|---|---|
| `talamo_gate_rota` | **1,894** | quase o dobro de peso nas 4 features de rota |
| `talamo_gate_servicos` | **0,762** | *abaixa* o volume das 5 distâncias-até-serviço |
| `talamo_gate_corpo` | 1,568 | amplifica fome/sede/dano |
| `talamo_gate_economia` | 1,955 | quase no teto (2,0) |
| `talamo_gate_tempo` | 0,900 | abaixa hora/tem_pax/bias |
| `talamo_gate_min` | 0,706 | o grupo mais fechado |
| `cortex_delta_abs` | 0,234 | |δ| médio usado, de um teto de 0,5 |
| `cortex_delta_max` | 0,467 | algum distrito×feature está quase saturado |
| `hipocampo_mem_renda_abs` / `_var` | 0,088 / 0,0069 | os slots enchem e diferem entre distritos |
| `hipocampo_mem_espera_abs` / `_var` | 0,159 / 0,113 | **a espera é o slot com mais contraste entre distritos** |
| `hipocampo_mem_preco_abs` / `_var` | 0,094 / 0,013 | |
| `hipocampo_ganho` | 0,859 | de um teto de 1,0 |
| `hipocampo_distritos_visitados` | 2,58 | de 3 (D=3 na cidade de 26 nós) |
| `reflexo_frac` | 0,696 | o reflexo do pai segue ativo 70 % do tempo |

**O que esta fumaça prova e o que NÃO prova.** Prova que roda em compile, que as
três camadas se movem (gate longe de 1, δ longe de 0, slots enchendo) e que a
telemetria sai sem sync. **Não prova ganho**: G=10, **1 semente**, P=256 e o braço
novo tem 41 genes a mais sorteados de `randn·0.8` — muda a geometria de mutação, não
só a arquitetura. `1,00 → 1,34` de fit aqui é ruído com nome bonito. Comparação
honesta = `--init-from` (genes novos nascem em 0, mede-se o **incremento**), G=120,
5 sementes, R=16, com o braço `camadas sem hipocampo` como controle.

Reproduzir: `NM_COMPILE=1 nice -n 5 python src/e42_cerebro.py --preset fumaca`
(saída em `/media/llm-data/universe-runs/neuromod-lab-taxi/e42/e42_fumaca.json`;
retrato em `.../e42/retratos/retrato_e42_fumaca.json`, com o bloco `camadas`).
`--ablacoes` acrescenta os 4 controles (`sem talamo`, `sem cortex`, `sem hipocampo`,
`so hipocampo`), que são a forma de intervir em vez de só medir.

---

## 7. Predições (registradas ANTES da bateria honesta)

### Predição 50 — hipocampo: ≥ 5 pp menos mortos **ou** +10 % de renda vs sem memória, na cidade grande
**Minha estimativa: ~30 % de chance da disjunção; ~15 % da perna "mortos".**

Contra:
1. A memória entra como **constante em G**. Ela consegue dizer "aqui eu espero muito,
   ande em vez de parar", mas **não** consegue dizer "vá para o distrito 4" — não há
   feature de distrito *por vizinho*. O canal certo para renda-por-distrito seria o
   córtex (que é por-distrito-atual) ou uma feature nova no `obs()`, que é do MUNDO.
2. `mem_preco` é quase redundante: `e_preco_local` (feature 22) já é o oráculo do
   fator do distrito atual. Sobra o valor absoluto pago, que mistura preço e consumo.
3. Base histórica deste lab é contra memória: `mem_*` ficou morto por construção
   dezenas de experimentos, e `BancoEMA`/`Diádica`/`MemCusto` empatam com o `Reativo`
   no portão do perito.

A favor: `mem_espera` é o slot com maior variância entre distritos já na fumaça
(0,113, ~10× a da renda), e "onde não aparece passageiro" é justo a informação que o
mundo grande (104 nós, 6 distritos, ≥30 % das corridas cruzando distrito) esconde do
`obs()`. Se a predição 50 passar, aposto que passa **por `mem_espera`**, não por renda
nem por preço — e a ablação `so hipocampo` mais um braço com só um slot ligado
decidem isso em uma rodada.

### Predição 51 — tálamo usado em ≥ 3/5 linhagens (gate médio < 0,8 em algum grupo)
**Minha estimativa: ~85 % como está escrita — e é por isso que ela, como está, não decide nada.**

`gate_g < 0,8 ⟺ a_g + b_g·need + c_g·carreg < −0,98`. Com a inicialização padrão da
evolução (`randn(P, NP)·0.8`), só o viés `a_g` já cai abaixo de −0,98 com
`P ≈ 11 %` por grupo — sobre 5 grupos, ~44 % das linhagens **nascem** cumprindo o
critério, antes de qualquer seleção, e `b`/`c` só somam variância. A fumaça, que roda
exatamente assim, já entrega `gate_min = 0,706`. Ou seja: o critério mede
**inicialização**, não uso.

**Versão estrita que proponho** (e que o runner já suporta, verificado —
o pai entra com 51 genes e o campeão sai com 92): rodar com
`--init-from <json do campeão reacoes> "reacoes (pai)"`. Aí todo gene novo nasce em
`N(0, σ₀ = 0,2)` em vez de `N(0, 0,8)`, ou seja **gate ≈ 1,000 no nascimento**:
`P(gate < 0,8) = Φ(−0,98/0,2) ≈ 5·10⁻⁷` por grupo, contra 11 % com a
inicialização padrão. Aí "gate médio < 0,8 no fim" é seleção, não sorteio. **Minha estimativa para a versão estrita: ~50 %**, e aposto que
o grupo que fecha é **serviços** (é o que fechou na fumaça: 0,76) — fechar as cinco
distâncias-até-serviço quando não há necessidade é exatamente o que o
`serv_need`/reflexo já faz melhor, e o tálamo dá o desconto de graça.

Registro também a predição barata que cai de graça junto: **o gate de `economia` vai
ficar > 1 em quase toda linhagem** (1,955 na fumaça, quase no teto de 2,0) — o E15 pôs
dívida e preço local no `obs()` com escala pequena (0..1) e o tálamo é a primeira
alavanca que consegue **amplificar** um bloco em vez de só mexer nos pesos um a um.

---

## 8. Decisões tomadas e o que ficou de fora

**Decisões**
1. `extra()` **recomputa `m.obs()`** em vez de receber `F`. Correção acima de
   micro-otimização: `obs()` é pura, a identidade bit a bit prova, e a alternativa
   exigia mexer em `lab.py`. Custo medido e declarado: +62 % no passo sob compile.
2. `δ` do córtex é `0.5·tanh(gene)`, não o gene cru — teto de alavanca (regra 5).
3. **Gene extra no hipocampo** (`hip_ganho`, o 2º dos "1 gene" do doc 41): sem ele a
   regra 17 só valeria para genomas com `mem_0..2` zerados. 41 genes novos em vez de 40.
4. Composição tálamo × córtex **aditiva** (§2).
5. `mem_renda` é creditada ao distrito de **origem** da corrida (a tarifa é
   proporcional ao multiplicador da origem, e é na origem que o ser procura corrida),
   lendo `m.e15_dorig` **do passo anterior** — no mesmo passo ele pode ser sobrescrito
   por um novo embarque.
6. `D` é lido no `reset` como `cfg.D` → `cfg.D_DIST` → 3. Os genes cobrem sempre 6
   distritos; com D < 6 as linhas extras simplesmente nunca são indexadas.
7. `retrato.py` recebeu 4 blocos aditivos `# [E42 cerebro]` (registro das arqs,
   coleta de `ativacao()` no fim do rastro, campo `camadas` no resumo, nomes dos
   genes). Nenhum caminho existente muda.

**Fora desta entrega**
- **Glândulas** (§5) — fase 2, com o motivo técnico.
- **Bateria honesta** — só fumaça, como manda o doc 41 §1.
- **Steering por distrito**: nenhuma feature de distrito *por vizinho* foi criada
  (seria do agente MUNDO, em `obs()`). É a peça que falta para a predição 50 ter
  chance alta, e está dita aqui de propósito em vez de silenciada.
- **`corpo_0..5` e `mem_3..5`** seguem mortos (9 genes ociosos no genoma).

**Nota de máquina**: uma execução do benchmark sob `NM_COMPILE=1` com 4 trocas de
arquitetura no mesmo processo morreu com `Memory access fault by GPU node-1`, com
outro job de outro agente ocupando a GPU em 99 %. Não reproduziu nos dois caminhos
que importam (fumaça completa com as 2 arqs sob compile, e o `chk_compile`), que
rodaram limpos depois. Registro sem atribuir causa — não investiguei.
