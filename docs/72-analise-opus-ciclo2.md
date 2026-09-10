# 72 — Análise do ciclo 2 (agente Opus, 10/09 ~11:30)

Escrito pelo analista (Opus) em paralelo com o Fable. Regra do ciclo 1 mantida: tudo que afirmo tem
**arquivo de origem** ao lado; onde não medi, escrevo "não medi". Nada aqui rodou fora da fila `nmd` —
os números do Mundo A saem de `/media/llm-data/universe-runs/neuromod-lab-taxi/e79/e43_mundoA5.json`,
os da bancada de `e72/bancada_padrao.json` (via docs/67 §1.5) e o retrato de docs/69.

---

## 1. O Mundo A, lido pelo mecanismo

### 1.0 A conta do Mundo A, decomposta — ela fecha ao quarto dígito

`campo.py:539–554` diz exatamente o que o ser paga:

```
metab = 1 + custo_basal·dof/100 + custo_gene·Σ_b n_b·ativ_b/100
```

`n_b` = quantos genes o bloco tem (`rodar`: `n_b = sum(n.startswith(b) for n in Arq.nomes_genes())`),
`ativ_b` = fração média de `ativ_ref` que o bloco emitiu. Com λ_ativ = .3, λ_basal = .15 e os números
do COMPLETO no Mundo A (`dof 194.6`; `ativacao_bloco` rap .1407, len .1591, ref .7994, tal .9885,
cor .9700, hip .0874):

| bloco | genes `n_b` | `ativ_b` | `n_b·ativ_b` | fatia da conta de ativação |
|---|---|---|---|---|
| córtex | 48 | .970 | 46.6 | **30.9 %** |
| lenta | 279 | .159 | 44.4 | **29.4 %** |
| rápida | 192 | .141 | 27.0 | 17.9 % |
| hipocampo | 170 | .087 | 14.9 | 9.9 % |
| tálamo | 15 | .988 | 14.8 | 9.8 % |
| reflexo | 4 | .799 | 3.2 | 2.1 % |
| | | | **Σ 150.9** | |

`0.15·194.6/100 = 0.292` (basal) `+ 0.3·150.9/100 = 0.453` (ativação) `+ 1 = 1.745`, contra
`metab = 1.74447` gravado. **A conta é reprodutível inteira**: 39 % dela é existência (basal) e 61 % é
ativação. Isso vale para tudo o que segue.

### 1.1 Por que o `talamo fixo` piora (pred 164e ✗)

`completo.py:67`: com `talamo_norm = 'fixo'`, `gt = gt·(NG/Σgt)` — a soma dos 5 portões passa a ser
**exatamente 5**. docs/69 §(c) mediu o campeão evoluído em **Σ = 3.39**: o ser evoluiu para
**fechar 32 % da atenção líquida**. `fixo` não normaliza o que ele faz; **tira dele o único botão de
ganho global** — baixar um portão passa a subir os outros.

O preço aparece onde ninguém procurou. Refazendo a conta de §1.0 para o braço `talamo fixo`
(`ativ`: rap .0962, len **.3681**, ref .8638, tal .9871, cor .9947, hip .1062; `dof 180.2`):

| | COMPLETO | talamo fixo | Δ |
|---|---|---|---|
| conta de ativação | 0.453 | **0.616** | **+36 %** |
| — só a camada LENTA | 44.4 | **102.7** | **+131 %** |
| basal (dof) | 0.292 | 0.270 | −7 % |
| `metab` | 1.744 | **1.886** | +8.1 % |
| `rec` (renda) | 101.0 | **90.6** | −10 % |
| `fit` | 4.115 | 3.874 | −5.9 % |

Mecanismo: com o ganho global travado, a atenuação que o ser precisa passa a ser comprada pela camada
**lenta** — e a lenta é o segundo maior pagador da conta (279 genes). Ele paga 8 % mais de fome, trabalha
10 % menos e vive menos. **Não é a normalização divisiva que está errada: é que ela remove uma variável
que a evolução usava, e o substituto é o bloco mais caro do orçamento.**

Teste que fecha isto e já está na fila: `a2_retrato_mundoA` imprime a soma dos portões por braço.
Aposta: COMPLETO com Σ < 4.2 e `talamo fixo` com Σ = 5.000 cravado.

**Ressalva dura, e ela vale para os três braços de baixo:** o `talamo fixo` está abaixo do COMPLETO em
**3 de 5 sementes**, não em 5 de 5 como diz o diário de 11:00 (COMPLETO `[3.999, 4.040, 3.974, 4.516, 4.045]`
× fixo `[3.736, 3.733, 3.991, 3.817, 4.094]` — nas sementes 2 e 4 o fixo está **acima**). Pareado, a
diferença é −0.241 com desvio das diferenças ≈ 0.30, ou seja **t ≈ 1.8**. Ver §2 item 7.

### 1.2 Por que `sem hipocampo` ≤ COMPLETO **sob custo**, quando sem custo era +7 %

Refazendo a conta para `sem hipocampo` (`ativ`: rap .1345, len **.2466**, ref .8629, tal .9929, cor .9830,
hip **0.0**; `dof 229.4`):

| bloco | COMPLETO `n_b·ativ_b` | sem hipocampo | Δ |
|---|---|---|---|
| hipocampo | 14.9 | **0.0** | −14.9 |
| lenta | 44.4 | **68.8** | **+24.4** |
| rápida | 27.0 | 25.8 | −1.2 |
| córtex | 46.6 | 47.2 | +0.6 |
| resto | 18.0 | 18.4 | +0.4 |
| **conta de ativação** | 0.453 | **0.480** | **+6 %** |
| **dof** | 194.6 | **229.4** | **+34.8 genes** |
| **basal** | 0.292 | **0.344** | +18 % |
| **`metab`** | 1.744 | **1.825** | **+4.6 %** |

Os 34.8 genes novos saem por bloco assim: rápida +15.2, lenta +13.0, córtex +3.8, tálamo +1.4, reflexo +0.2,
hipocampo +1.2. Ou seja:

> **Tirar o hipocampo não barateia o ser: o resto do cérebro liga 35 genes a mais e a camada lenta passa a
> emitir 55 % mais, para fazer o que o hipocampo fazia. A compensação é cobrada; a peça original não era.**

Sem conta (pred 144), essa compensação era **de graça** — e por isso `sem hipocampo` ficava acima. Com a
conta ligada, o mesmo comportamento passa a ter preço. Isto **não** é "o hipocampo passou a valer":
é "o substituto ficou caro". A leitura correta da inversão da 144 é essa, e ela é medível: o sinal está
inteiro em `dof_bloco` e `ativacao_bloco`, sem precisar de história.

**E há um viés a favor do COMPLETO que ninguém declarou** (detalhe em §2 item 2): `liga['hipocampo'] = False`
(`completo.py:56`) zera só o **derivado** `s.g_hip`; os 170 genes do hipocampo continuam no genoma, continuam
mutando e continuam contados por `dof_de` (`campo.py:565`, que conta **todos** os genes depois de
`Linear.NP`). Prova no próprio arquivo: no braço `sem hipocampo`, `dof_bloco.hip = 52.0` com
`ativacao_bloco.hip = 0.0` — **52 genes ligados num órgão mudo**, pagando `0.15·52/100 = 0.078` de
metabolismo por nada. O braço de ablação é "o ser com o órgão desligado pagando aluguel", não "o ser sem
o órgão". Vale para **toda** ablação sob custo de gene, em todas as baterias.

### 1.3 Quem paga × quem dirige (é aqui que o Mundo A é injusto)

Cruzando §1.0 com a coluna `dirige` da bancada (docs/67 §1.5, `e72/bancada_padrao.json`):

| bloco | fatia da conta de ativação | `dirige` | dirigir por ponto de conta |
|---|---|---|---|
| **tálamo** | 9.8 % | **.279** | **.0285** |
| córtex | 30.9 % | .182 | .0059 |
| reflexo | 2.1 % | .0022 | .0011 |
| rápida | 17.9 % | .0069 | .00039 |
| lenta | 29.4 % | .0098 | .00033 |
| hipocampo | 9.9 % | .0033 | .00033 |

O tálamo é **86× mais eficiente** que a camada lenta em direção por ponto de conta, e a conta cobra a
lenta 3× mais que o tálamo. **As camadas livres (rápida + lenta) pagam 47 % da conta de ativação e
respondem por 1.7 % da direção da espinha.** Isso é a régua, não a peça.

(Ressalva: a coluna `dirige` vem da bancada com genes uniformes ±1.5, não do genoma evoluído. Não medi
`dirige` por bloco no campeão do Mundo A — `retrato_bateria` não o calcula. É a medida que fecharia esta
tabela e ela é barata.)

Mecanismo por trás disso, já registrado no ciclo 1 e agora com número: a conta cobra `|saída do bloco|`,
e `campo.py:472` (`sc = sc - sc.mean(1, keepdim=True)`) prova que a parte igual nas 9 opções tem efeito **exatamente
zero**. Quem multiplica sentidos de **distância** (tálamo, córtex: 60–200 m) satura `ativ_b` em .97–.99;
quem multiplica sentidos do **corpo** (∈[0,1]) fica em .09–.16. **A unidade do sentido é que decide a
conta, não o trabalho do bloco.**

### 1.4 O que o Mundo A mede de verdade (n = 5, pareado)

Diferenças pareadas por semente, contra o COMPLETO, com o desvio das **diferenças** (a conta oficial sai
do `a1_pareado_mundoA_fit`, que está na fila; a minha é a de cabeça e pode estar na terceira casa):

| par | Δ médio | sementes a favor | t aproximado |
|---|---|---|---|
| **linear − COMPLETO** | **+0.861** | **5/5** | **≈ 4.4** |
| COMPLETO − sem hipocampo | +0.148 | 3/5 | ≈ 1.1 |
| COMPLETO − sem reflexo | +0.147 | 4/5 | ≈ 1.1 |
| COMPLETO − talamo fixo | +0.241 | 3/5 | ≈ 1.8 |

> **O Mundo A tem UM resultado e três não-resultados.** O resultado é "a espinha ganha de todo cérebro"
> (−17.3 %, 5/5, t ≈ 4.4). As três comparações **entre** cérebros estão em t ≈ 1.1–1.8 — ordenação de
> ruído. Qualquer frase da forma "sem hipocampo é pior que COMPLETO" ou "talamo fixo é o pior" não tem
> base a n = 5; o que tem base é o **mecanismo da conta** (§1.1, §1.2), que é aritmética do arquivo e não
> depende de teste estatístico nenhum.

### 1.5 O que o Mundo B precisa mostrar para separar "a conta" de "a peça" (pred 167)

O smoke A × B (docs/67 §6.1) já disse que com `ativ_centrada` a sobretaxa de ativação do COMPLETO cai de
**0.688 para 0.018** — fator **38×**, não 17× (a conta do ciclo 1 usou `metab − 1` sem tirar o basal;
correção em §2 item 6). Com λ = .3 a conta de ativação em B fica **desligada**, não "justa". Consequência
metodológica: **B, sozinho, não separa "a conta era a penalidade" de "qualquer conta menor daria o mesmo".**

O que B tem de mostrar, na ordem em que eu leria o JSON:

1. **Identidade.** `linear` idêntico ao Mundo A nas 5 sementes (a lei só toca blocos). Se não for igual,
   alguma outra coisa mudou e o resto não vale.
2. **A conta cai E o ranking inverte.** Não basta `metab` cair (pred 167a pede ≥ 30 %; o smoke prevê
   −94 % da parte de ativação). O que decide é **quem** paga: hoje a razão
   `(n·ativ)_lenta / (n·ativ)_tálamo` = 44.4/14.8 = **3.0**. Se a conta passar a cobrar influência, essa
   razão tem de cair **abaixo de 1**. Se cair `metab` mas a razão continuar > 1, a conta nova está
   cobrando o mesmo com outro nome.
3. **O buraco tem de fechar na proporção da conta que sumiu — não mais.** Defina
   `recuperação = (fit_B − fit_A)/(fit_linear − fit_A)`. A ativação é 61 % da sobretaxa; se a recuperação
   passar muito de 0.6, a conta não é o mecanismo inteiro — algo mais mudou (o gradiente de custo muda a
   busca, e a busca é a variável escondida).
4. **Atenção ao basal:** em B o termo basal (`0.15·dof/100`) **não muda de lei**. No smoke ele era 0.022
   porque `dof` era 15 (genomas = semente linear + ruído, G = 1). Num genoma evoluído com `dof ≈ 195` o
   basal sozinho já é **+0.29 de `metab`**. Portanto **não espere `metab ≈ 1.04` na bateria B** — espere
   ~1.3, e se a conta nova barateou o gene, `dof` pode **subir** e o basal com ele.
5. **O que B não responde e exige um terceiro ponto.** "A peça paga o próprio preço?" só se responde com a
   **mesma conta total** repartida por influência. O λ equivalente medido no smoke é
   `0.3 × 0.688/0.018 ≈ 11.4` — mas medido em genoma **não evoluído**, onde a fração diferencial é a menor
   possível. **Não escreva um Mundo D com λ = 11 antes de refazer a conta com a bateria B**:
   `λ_eq = 0.3 × (Σ n_b·ativ_b)_A / (Σ n_b·ativ_b)_B`, os dois vindos de campeões evoluídos.

---

## 2. Auditoria: onde o Fable, o CS ou eu podemos ter errado

| # | afirmação | veredito | evidência |
|---|---|---|---|
| 1 | pred 169: "o juiz usa 128 cópias sem corte" | **o código dizia o contrário** | `campo.py:613`: `medidas()` faz `copy(cfg)` e só sobrescreve `medir_ativ`/`jardim_comum` — `corte_vivos` ia junto, e como `frac_teto` conta `t_vida >= T` o truncamento não acendia luz nenhuma. **Consertado** nesta rodada (§4) |
| 2 | ablação = "o ser sem a peça" | **é "o ser com a peça muda, pagando aluguel"** | `completo.py:56` zera só `s.g_hip`; `campo.py:565 dof_de` conta todos os genes depois de `Linear.NP`. Prova: `e79/e43_mundoA5.json`, braço `sem hipocampo`, `dof_bloco.hip = 52.0` com `ativacao_bloco.hip = 0.0` → 0.078 de `metab` por um órgão mudo. **Não consertei** (proposta em §4) |
| 3 | docs/69:33 e :75 "um mapa de **12 distritos**"; "4 caixas de **12**" | **o mundo tem 6 distritos, não 12** | `completo.py:28 DMAX = 12` contra `campo.py:39 K = max(3, round(6·L/200))` = 6 em L = 200 (e o cenário crava `K: 6`). `distrito()` devolve 0..5. Logo **6 das 12 caixas e 24 dos 48 genes do córtex nunca são instanciados** — são gene morto por construção, não distrito não visitado. A razão certa é **4 de 6 tocadas**, que é bem menos alarmante |
| 4 | política/memória por distrito transferem entre mapas | **o alfabeto de distrito não é fixo** | `campo.py:90`: `perfil = randint(0, len(NOMES_PF), (K,)); perfil[:len(NOMES_PF)] = arange(len(NOMES_PF))[:K]` — com K = 6 os **dois últimos distritos recebem perfil sorteado**, então quantos "centro" existem varia de mapa para mapa. Córtex (política por distrito) e hipocampo (memória por distrito) não têm alfabeto estável para transferir. Nenhum documento registrou isso |
| 5 | docs/70:139 "o regime tem período de 5 dias" como diagnóstico dos mundos que rodaram | **o regime está DESLIGADO em A e B** | os cenários não têm `mundo.regime`; `NM_REGIME` não está no env de `s1b_mundoA5`/`z0_s2_mundoB`; e `NF = 46` no JSON confirma (com regime seriam 48). O único ciclo lento do Mundo A é o de **preço** (`precos.periodo` = 3 d ⇒ 1.53 ciclos por vida) |
| 6 | docs/67 §6.1 (meu, ciclo 1): "λ equivalente ≈ 5.3" | **errado: era 11.4** | usei `metab − 1` sem separar o basal (0.022 no smoke). Com o basal fora: 0.688 → 0.018, fator 38, λ_eq = 11.4. E o número só vale para genoma **não** evoluído |
| 7 | docs/48 11:00: "talamo fixo −5.8 % vs COMPLETO (**5/5 abaixo**)" | **3/5, não 5/5** | `fit_por_semente`: COMPLETO `[3.999, 4.040, 3.974, 4.516, 4.045]` × fixo `[3.736, 3.733, 3.991, 3.817, 4.094]` — sementes 2 e 4 o fixo está acima. Pareado t ≈ 1.8 |
| 8 | docs/68:74 "Isto é fumaça: 1 semente, **25 gerações**" | **1 geração** | `_nmd/feitos/s0_smoke_mundoA.json` e `o7_smoke_mundoB.json`: `"P": 8, "G": 1`. O preset `fumaca` tem G = 25, mas o pedido passou `--G 1` e a flag explícita vence desde o fix de precedência |
| 9 | docs/69:83 "neurônio morto é gene morto; **sob o custo por ativação do Mundo B ela deveria ser eliminada**" | **a conta por ativação não vê unidade morta** | `ativ_blocos` mede `\|saída do BLOCO\|` (`campo.py:808`, `_blk['rap'] = einsum(h, V)·ESC`): uma unidade com V = 0 não muda a saída do bloco, logo custa **zero** de ativação — em A e em B igualmente. Quem cobra a unidade morta é o **basal**, que tem a mesma lei nos dois mundos. Previsão: contar unidades mortas no campeão de A contra o de B dá **nulo** |
| 10 | pred 164 (a) "ninguém bate o linear" | **✓, e é o único resultado do Mundo A** | 5/5, t ≈ 4.4. Os três contrastes entre cérebros ficam em t ≈ 1.1–1.8 (§1.4) |

Nada disto derruba um positivo. Derruba **ordenações**: as três frases "peça X é pior que peça Y" do
Mundo A e o diagnóstico do hipocampo por "12 caixas".

---

## 3. `dimensiona.py` — as razões, com número

docs/70 §3.1 propõe: nenhuma constante de mundo em unidade absoluta; toda constante é **razão contra a
vida do ser**, e um portão recusa rodar se alguma razão sair da faixa. A proposta concreta, com os
mínimos que o CS declarou e as medidas do Mundo A (`e79`, braço linear: vida **4.589 d**, **13.02**
entregas por vida; docs/69: raio de ação **37 m**):

| razão | fórmula | Mundo A | mínimo | o que a põe na faixa |
|---|---|---|---|---|
| **cidade × raio de ação** | `min(1, π·raio²/L²)` | **.108** | ≥ .50 | `L ≤ raio·√(π/.5)` = **93** |
| **período do regime × vida** | `vida / período` | **1.53** (preço, 3 d) | ≥ 3 | `período ≤ vida/3` = **1.53 d** |
| **caixas de memória × entregas** | `entregas / min(DMAX, K)` | **2.17** | ≥ 5 | `K ≤ entregas/5` = **2.6**, ou entregas por vida ≥ 30 |

E três avisos que não são portão, mas explicam metade dos nulos:

- **`caixas_mortas` = DMAX − K = 6.** Metade do córtex e metade do hipocampo nunca existem (§2 item 3).
- **`tau_max_vida` = 201 tiques / (4.589 d × 240) = 18 %.** Todo estado do ser — τ da rápida, da lenta,
  do reflexo, do hipocampo — é `1. + 200.·sigmoid(·)`, ou seja **no máximo 201 tiques = 0.84 dia**.
  Nenhum órgão deste ser consegue guardar coisa alguma por mais de 18 % de uma vida, e **todo ritmo lento
  do mundo é mais lento que isso** (preço 3 d; regime padrão 5 d). Não medi, mas essa é a candidata mais
  forte a explicar por que "memória de longo prazo" nunca pagou aqui: não há substrato para ela.
- **constantes que não acompanham L:** `retina.R_dia` = 60 m e `raio_px` = 45 m são absolutos. Em L = 200
  a retina vê 30 % da cidade; em L = 92 vê 65 %.

**Está implementado** como `src/dimensiona.py` (só stdlib, só leitura, não roda mundo nenhum) com as
constantes do código espelhadas e conferidas no portão `testes_import` — sem isso viram índice cravado que
envelhece em silêncio. Uso: `python dimensiona.py --cenario cenarios/X.json [--exigir]`.

---

## 4. Mundo C — `cenarios/mundoC_cidade_da_vida.json` (pred 170)

**Duas leis, três números, o resto bit a bit igual ao Mundo A** (conferido por `diff`: só mudam `nome`,
`predicao`, `L`, `precos.periodo`, os dois flags de protocolo e um braço).

> **Lei 1 — a cidade tem o tamanho da vida:** `L` 200 → **92**.
> **Lei 2 — o ciclo do mundo cabe na vida:** `precos.periodo` 3 d → **1.5 d**.

A conta **não muda** (`ativacao` λ .3 + basal .15, `ativ_centrada` desligado): C é pareado com A no eixo
da balança, e o eixo da balança é o que A × B mede. O desenho completo é um 2×2 —
{conta antiga, conta justa} × {cidade grande, cidade da vida} — do qual A, B e C são três células.

**Por que encolher a cidade não é só "facilitar":** `DENS` é por **área** (`campo.py:97,106`), então a
densidade de postos/comida/água é invariante de escala e **a distância ao serviço mais perto não muda**.
A parte dura da sobrevivência (gasolina, fome, pane) fica dimensionalmente idêntica. O que escala com `L`
é o **destino do passageiro** (`_destino`: `r = L·(.05 + .45u²)`) e a **fração do mapa ao alcance**. Ou
seja: a intervenção é sobre o **dado disponível às peças de lugar**, não sobre a dificuldade de viver.

Razões, pelo `dimensiona.py`, com as medidas do A: cidade ao alcance **.108 → .508 ✓**; ciclos por vida
**1.53 → 3.06 ✓**; amostras por caixa **2.17, inalterado ✗** — esta é a razão que este mundo **não**
conserta, porque `K` continua 6 e `DMAX` continua 12. Deixei `K` fora de propósito: `K` controla ao mesmo
tempo o número de distritos, o tamanho do distrito **e a densidade de ruas** (`campo.py:87`: K linhas
verticais + K horizontais), e três efeitos num número só não se atribuem.

**Seres (5):** `linear`, `COMPLETO`, `sem hipocampo`, **`sem córtex` (novo)**, `sem reflexo`. O `talamo fixo`
sai — o mecanismo dele já está entendido (§1.1) e ele não fala sobre dimensionamento. O `sem córtex` entra
porque a política por distrito é a peça mais diretamente alimentada pela Lei 1. O `sem reflexo` fica como
**controle negativo**: o reflexo é sobre gasolina, e gasolina é invariante de escala — se a distância dele
ao COMPLETO mudar de A para C, mudou alguma coisa que eu não quis mudar.

Aposta completa e falsificável: pred 170. O ponto que decide é **(c)**: se o buraco COMPLETO − linear
(−17.3 % em A) não encolher pelo menos pela metade **mesmo com (a) e (b) confirmados** (o ser passa a
conhecer o mapa e a entregar mais), então o dado chegou e a peça continua sem pagar — **o programa
"cidade / regime / memória" sai da fila e a culpa é da peça.**

Ressalva pré-registrada, escrita antes de rodar: em C o ser vê 65 % da cidade de uma vez (retina 60 m
absolutos) contra 30 % em A. Se (c) der ✓, parte do ganho pode ser **visão**, não **memória**, e o teste
que separa é um C' com `R_dia` 27.

**Enfileirado só o smoke** (`o2_smoke_mundoC`, P 8 G 1 semente 0, e79), diretamente comparável ao
`s0_smoke_mundoA`. A bateria C é do Fable, depois do B.

---

## 5. Alterações de código desta rodada (2) e o que eu NÃO mexi

Detalhe e commit em `docs/AGENTE-OPUS-LOG.md`.

1. **`src/dimensiona.py`** (novo) + portão em `src/testes_import.py`. Só stdlib, só leitura, não importa
   torch nem campo — por isso `DMAX`, `dia`, `R_dia`, `raio_px` e `τ_max` estão espelhados e o portão
   confere cada um contra o código. O portão também trava os vereditos: A e B reprovam nas três razões,
   C reprova só em `amostras_por_caixa`. Nada disto muda mundo nenhum.
2. **`src/campo.py:613`** — `medidas()` passa a zerar `corte_vivos` no cfg do juiz (§2 item 1).
   **Idêntico bit a bit para `corte_vivos = 0`, que é tudo o que já rodou.** É conserto, não lei nova:
   alinha o código com o que a pred 169 diz por escrito. Reverter = tirar `; cfg_m.corte_vivos = 0.`.

**O que eu NÃO mexi, e por quê:**

- **`dof` da ablação** (§2 item 2, o achado com mais consequência desta rodada). O conserto certo é
  `dof_de` ignorar os genes de blocos desligados por `liga` — uma máscara construída de
  `Arq.nomes_genes()` + `Arq.liga`, passada por `rodar`/`medidas`, atrás de um flag `dof_ablacao` com
  padrão = hoje. São ~10 linhas, mas mexem no caminho do `metab` **com a bateria B rodando** e eu já tinha
  gasto as duas alterações. Fica como proposta declarada, com o número: o viés é 0.078 de `metab` no
  `sem hipocampo` (52 genes mudos × λ_basal), contra uma diferença de fit de 0.148 — **da mesma ordem**.
- **`DMAX` configurável** (§2 item 3). Mesmo argumento do ciclo 1: muda `N_COR`/`N_HIP` ⇒ nomes de genes,
  `GRUPOS`, `_LAYOUTS`, `alinha_semente`, e invalida toda semente gravada. Agora com um argumento a mais
  a favor (6 caixas mortas são gene morto pago em basal) e um contra (é a mudança mais cara de reverter).
- **`--neutro`** (pred 158, agora **escrita no ledger** — era o buraco apontado no ciclo 1). Continua
  atrás das duas acima: conserta a régua de uma métrica que já sabemos ser ≈ deriva.
- **`rap_norm`** (entrada da camada rápida normalizada). O mecanismo que docs/69 mostra é mais forte do
  que "saturação": `relu` **não tem teto**, então uma unidade que nunca cruza zero é uma unidade
  **linear** — e uma unidade linear sobre os mesmos sentidos é redundante com a espinha. É a explicação
  mais simples para "192 genes que dirigem .0069". Mas isso é intervenção no **ser**, e docs/70 §3.2 é
  explícito: peça passa pela bancada antes da bateria. O teste certo é de bancada, não de mundo.

---

## 6. Resumo para o Fable

1. **O Mundo A tem um resultado só** (a espinha ganha, 5/5, t ≈ 4.4). As três ordenações entre cérebros
   estão em t ≈ 1.1–1.8 e o "5/5" do `talamo fixo` é 3/5. Confira com `a1_pareado_mundoA_fit`.
2. **`talamo fixo` piora porque `fixo` tira o ganho global** que o ser evoluiu (Σportões 3.4 < 5) e a
   atenuação é recomprada pela camada lenta, que é o bloco mais caro: conta de ativação +36 %, renda −10 %.
3. **`sem hipocampo` não fica mais barato**: o resto do cérebro liga +35 genes e a lenta emite +55 % para
   substituir a peça, e a compensação é cobrada. Sem custo isso era de graça — daí a inversão da pred 144.
4. **O juiz estava cortando junto com o treino** (`campo.py:613`). Consertado; sem isso o `z4` mediria
   uma coisa e declararia outra (pred 172).
5. **A ablação paga aluguel pelo órgão mudo** (52 genes, 0.078 de `metab`, mesma ordem do efeito medido).
   Não consertei — decisão sua, proposta em §5.
6. **O mundo tem 6 distritos, não 12**: metade do córtex e do hipocampo é gene morto por construção, e o
   perfil dos dois últimos distritos é sorteado por mapa (não há alfabeto de distrito para transferir).
7. **Nenhum estado do ser dura mais que 0.84 dia** (τ = `1. + 200.·sigmoid`), e todo ritmo lento do mundo
   é mais lento que isso.
8. **Mundo C está escrito** (2 leis, 3 números, pareado com A) e só o smoke foi enfileirado.
