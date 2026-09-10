# 67 — Análise geral da madrugada (agente Opus, 10/09 ~00:30–02:00)

Escrito pelo agente de análise (Opus), em paralelo com o Fable. Tudo que afirmo aqui tem **arquivo de origem**
ao lado. Onde eu não medi, escrevo "não medi". Três coisas mudaram no código nesta rodada — estão em
`docs/AGENTE-OPUS-LOG.md` e todas nascem **desligadas**.

---

## 1. O que os dados de hoje realmente mostram

### 1.1 A célula que mais pesa: **"P512 ≡ P128" nunca aconteceu** (correção)

O diário de 23:10 diz: *"P512 rot = P128 ao milésimo (mesmo campeão em 35 ger. × 512 seres)"* e conclui
*"a evolução NÃO sai da semente"*. Conferi os JSONs:

| arquivo | `argv` pediu | `P` gravado no JSON | fit do linear | `cenario_hash` |
|---|---|---|---|---|
| `e78/e43_P128.json` | `--P 128` | (campo ainda não existia) | **4.844735336303711** | 54f2d8a1e8 |
| `e78/e43_P256.json` | `--P 256` | **512** | **4.844735336303711** | 54f2d8a1e8 |
| `e78/e43_P512rot.json` | `--P 512` | 512 | **4.844735336303711** | 54f2d8a1e8 |

Iguais **nos 16 dígitos**, mesmo hash de cenário. Não é "o mesmo campeão": é **o mesmo run três vezes**.
Os dois primeiros rodaram antes do fix de precedência (09-09 22:50) e `cenarios/mundo_vivo_v1.json` tem
`protocolo.P = 512` — o cenário sobrescreveu o `--P`. O próprio `e43_P256.json` grava `P: 512`.

Duas consequências:
1. **Nunca houve um run com P = 128.** O diário de 22:50 escreve "a pred 145 rodou P=128 três vezes" —
   é o contrário: rodou **P=512** três vezes.
2. A frase "P não é a alavanca" não tem medida por trás. O **único** par de P realmente medido no mesmo
   protocolo é P512 4.845 (36 ger.) × P256 4.688 (33 ger.) = **+3.4 % a favor do P maior**
   (`e78/e43_P512rot.json`, `e78/e43_P256rot.json`).

**Decide a próxima bateria:** o Mundo A está com `P: 128` (`cenarios/mundoA_seres.json`). Isso é uma escolha
de **orçamento** (8 seres × 5 sementes), não uma medida. Não é errado — é errado *chamar de medido*.
Registrei a pred **168** para fechar isso com uma célula de verdade quando houver GPU sobrando.

### 1.2 σ de mutação: o efeito é **maior** do que o diário diz, e .05 ≈ .1

O diário compara σ .1 (5.36) com "4.69–4.84". Esses dois números vêm de runs com **outro** protocolo
(P256 parando na ger. 33 e P512 parando na 36). O controle pareado — mesmo P, mesmo R, mesma parada por
janela, mesmas 60 gerações — é `e78/e43_P256R4jan.json` = **4.522**:

| célula | σ_mut | ger. efetivas | fit | por semente |
|---|---|---|---|---|
| `e43_P256R4jan` | .3 | 60 | 4.522 | 4.432 / 4.403 / 4.293 / 4.690 / 4.791 |
| `e43_P256sig05` | .05 | 60 | 5.211 | 5.273 / 4.954 / 5.438 / 5.341 / 5.047 |
| `e43_P256sig01` | .1 | 60 | 5.358 | 5.167 / 5.747 / 5.667 / 5.222 / 4.987 |

- σ .1 bate σ .3 em **5/5 sementes**, **+18.5 %** (não +11–14 %).
- σ .05 bate σ .3 em **5/5**, +15.2 %.
- **σ .05 × σ .1: empate.** Pareado dá 2/5 a favor do .1 (5.167<5.273, 5.747>4.954, 5.667>5.438,
  5.222<5.341, 4.987<5.047). Média +0.147 com desvio das diferenças ~0.4 → t ≈ 0.8.
  "Ótimo em ~.1" **não** está medido; o que está medido é "**.3 é grande demais**".
  Adotar .1 está certo por conveniência, não por ótimo.

Achado lateral que ninguém anotou: com σ .3, **rodar mais gerações piora**. P256 σ .3 parando na 33 deu
4.688; o mesmo com a parada por janela (60 ger.) deu 4.522, pior em 3/5 sementes. Mutação destrutiva não
vira melhora com tempo — vira deriva.

### 1.3 Jardim comum: **nulo** (fecha a pred 162)

`e78/e43_P256jardim.json` (σ .3, P256, R4, janela, 59 ger.) contra o controle pareado `e43_P256R4jan`
(idêntico, 60 ger.):

| | fit | por semente |
|---|---|---|
| jardim comum | **4.692** | 4.859 / 4.697 / 5.172 / 4.285 / 4.447 |
| controle (rot) | 4.522 | 4.432 / 4.403 / 4.293 / 4.690 / 4.791 |

Diferenças pareadas: +0.43, +0.29, +0.88, −0.41, −0.34. Média **+0.17 (+3.8 %)**, 3/5 sementes,
t ≈ 0.7. A aposta da pred 162 era **≥ +5 %** → **✗ (nulo)**. Contra o outro controle disponível
(P256 rot parando na 33, 4.688) a diferença é **+0.1 %**.

Por que o berço compartilhado não pagou, se 83 % da variância do tempo de vida é o berço (CS docs/66)?
Hipótese (não medida): a aptidão já é a **média sobre NC·R = 16 mundos** (`campo.py: avaliar` faz
`.view(B, NC*R).mean(1)`), então a maior parte da variância do berço já estava mediada antes do jardim;
o que o jardim acrescenta é parear os 16 mundos **entre genomas**, e isso troca ruído por
sobreajuste àqueles 16 mundos (que rodam a cada geração). Testável de graça: jardim com R=8 contra R=4.

**Decide a próxima bateria:** ligar `jardim_comum` no Mundo A não é obrigatório e não vai salvar nada;
é neutro. Se ligar, ligue **também** no Mundo B, senão A e B deixam de ser pareados.

### 1.4 A evolução anda (pred 159 ✗, já fechada) — e o gargalo é o **último passo**

`e43_G1` (só a população inicial, P256) = **4.145**; G60 = 4.5–4.8. A busca acrescenta +9 a +17 %.
Mas o campeão exportado é `Wv[si][0]` — o **argmax de P avaliações ruidosas** da última geração
(`src/lab.py`, fim de `evoluir_sementes`). Com σ_genoma 1.40 d e σ_erro 1.95 d (CS docs/66; SNR .72),
a correlação medido×verdadeiro é ~.58: o argmax de 128 sorteios chega a ~1.6 σ_g acima da média quando o
melhor verdadeiro está a ~2.7 σ_g. **Perde-se ~1 σ_g de genoma na última linha do run.** Isso é a mesma
"seleção por sorte" da noite, mas no ponto em que ela é mais barata de consertar (pred 166, implementada
como `campeao=reavaliado`, desligada por padrão, custo ~0.25 % do run).

### 1.5 Capacidade por bloco (bancada) e o que ela realmente diz

`e72/bancada_padrao.json` (2048 genomas uniformes ±1.5, 5 passos):

| bloco | genes | **dirige** (desvio entre as 9 opções) | **desloca** (modo comum) | dirige/desloca |
|---|---|---|---|---|
| espinha | 57 | .652 | 186.6 | 0.35 % |
| tálamo | 15 | .279 | 78.4 | 0.36 % |
| córtex | 48 | .182 | 25.6 | 0.71 % |
| reflexo | 4 | **.0022** | **14.3** | **0.016 %** |
| hipocampo (esc .01) | 170 | .0033 | 0.93 | 0.35 % |
| hipocampo (esc 1.0) | 170 | .330 | 93.3 | 0.35 % |
| rápida | 192 | .0069 | 2.00 | 0.34 % |
| lenta | 279 | .0098 | 2.67 | 0.37 % |

**Leitura que ficou errada no diário:** "as camadas quase não dirigem" confunde duas colunas. A coluna
`dirige` **somada** nos blocos (tálamo .279 + córtex .182 + rápida .0069 + lenta .0098 + hip .0033 +
ref .0022 = **.483**) é **74 % da espinha** (.652) — o cérebro tem ~43 % de toda a autoridade de direção.
O que é 0.3 % é a razão `dirige/desloca`, que fala do **preço**, não da **influência**. A trajetória
confirma o lado da influência (§6.3): linear e COMPLETO concordam em só **27 %** dos tiques.

"dirige" é o que muda a escolha; "desloca" é o que é **igual nas 9 opções**. O `um_passo` centra a nota
(`src/campo.py:427`: `sc = sc - sc.mean(1, keepdim=True)`), então **o modo comum tem efeito exatamente
zero** — na direção e também no mover-vs-servir (centrar mata qualquer constante por linha).
Ou seja: **99.6 % do que cada bloco emite é jogado fora por construção.**

O caso extremo é o **reflexo**: 0.016 % — **20× pior que todo o resto** (os outros blocos ficam em
0.34–0.37 %). O reflexo mexe no peso de `d_posto` (`src/completo.py:89`,
`Wtot.index_add(1, s.IDX1, -(s.w*a))`), e `d_posto` é uma distância **absoluta**: o que dirige é o
**gradiente** entre as 9 opções (metros), o que ele emite é o **nível** (dezenas de metros).
Mecanismo geral: com sentido de distância absoluta, o poder de virar de qualquer bloco escala com
Δd/d — **cai** quanto mais longe está o alvo, o contrário do que um reflexo deveria fazer.
Ressalva honesta: sob retina com oclusão o `d_posto` salta para `k_cego·R = 120` nas direções cegas, e aí
o gradiente é grande; o 0.016 % é o estado congelado da bancada (uma posição, 5 passos), não a média de uma
vida. **Não medi** a distribuição de Δd/d ao longo de uma vida — é a medida que fecharia este ponto.

### 1.6 O achado com mais consequência: **a conta do cérebro cobra o modo comum**

`ativ_blocos` (`src/campo.py`, fim da classe `Cerebro`) cobra `|saída do bloco|.mean(1)` — o **desloca**
da tabela acima, não o **dirige**. Consequências, todas verificáveis:

1. **Um cérebro com os genes praticamente todos em zero paga 70 % a mais de metabolismo.**
   Medido agora, no smoke do Mundo A (`_nmd/log/s0_smoke_mundoA.log`, P=8 G=1): linear `metab 1.00`,
   COMPLETO `metab 1.71` com **dof = 15** (de 708 genes novos). Pela regra de existência esses 15 genes
   custariam 0.045. A regra de ativação cobra **0.69** — 15× mais, de um genoma que é quase todo zero.
   A spec F2 dizia "silêncio é grátis"; o que ela cobra é **presença de escala**, não atividade.
2. Explica a tabela do ledger sem precisar de história nenhuma: tálamo e córtex "sempre ligados"
   (pred 136: tal .997, cor .981; pred 143: tal 1.00, cor 1.00) são os blocos que multiplicam sentidos de
   **distância** (60–200 m); rápida/lenta/hipocampo agem sobre sentidos do corpo (∈[0,1]) e ficam em .01–.18.
   A diferença entre "pagar cheio" e "pagar quase nada" é a **unidade do sentido**, não o quanto o bloco trabalha.
3. Explica o "**COMPLETO vira pedra**" da pred 143 sem apelar para "o portão emite sempre": a única forma
   de baixar uma conta que é 99.6 % modo comum é **zerar o bloco**; e como o útil é 0.4 % da conta, a
   evolução zera. O experimento mediu o preço da escala dos sentidos, não o preço do cérebro.
4. **O caso extremo, medido no portão novo** (`_nmd/log/o4_testes_ativ.log`, `test_ativ_centrada`):
   uma camada lenta com pesos **só** em sentidos do corpo — que são iguais nas 9 opções por construção
   (achado E58, docstring do `Bilinear`), ou seja um bloco que **não pode mudar decisão nenhuma** — é
   cobrada no **máximo** pela regra de hoje (ativação **1.000**, metab **1.837**: 84 % a mais de comida)
   e passa a **0.00000** (metab **1.000**) com a conta centrada. Não é uma diferença de grau.
5. Vale também no genoma **evoluído**, não só na bancada: `e72/retrato_e43_P128.json` mostra portões dos
   campeões entre 0.29 e 1.68 (`gates0`/`gates8`), ou seja |gate−1| até 0.7 multiplicando pesos O(1) sobre
   distâncias de dezenas de metros. O modo comum do tálamo num campeão é grande.

**Isto é o que decide o Mundo B** (§3).

### 1.7 Deriva e delegação: nada mudou, mas a régua está errada por um lado conhecido

`e72/deriva_nula_s0.02_e0.05.json`: passeio sem seleção liga dof 46 % (g5) → 76 % (g30) → 88 % (g120).
`e72/campeao_vs_nulo_e43_P128.json`: os campeões (30 ger. efetivas) têm dof .64–.77, equivalente ao nulo
a **14–33 gerações** — em **10/10** casos **abaixo** do nulo na geração certa. Duas leituras:

- dof **não é** evidência de seleção (pred 156 ✓), e
- o campeão anda **menos** que o passeio puro — coerente com a ressalva do Fable: 15 % da população
  (a elite) é copiada **sem mutar**, então a linhagem do campeão sofre menos passos de σ do que g·σ.
  O nulo justo é a própria GA com aptidão aleatória (**pred 158, reservada no diário e ainda não escrita
  no ledger** — não a implementei nesta rodada; ver §4).

Delegação tálamo↔reflexo: e77 −.52/−.49, P128 −.28/−.32, com sinal **invertido** (+.40/+.50) dentro do
sem-hipocampo (`e72/retrato_*`). Com n=5 por braço isso é ruído com um sinal fraco dentro do COMPLETO.
A ablação (`completo sem reflexo`) já está entre os 8 seres do Mundo A — é ela que decide.

### 1.8 Trajetória (pred 163): **não rodou — ferramenta quebrada**

`g73_trajetoria_P128` saiu com **exit=1**: `AttributeError: 'Namespace' object has no attribute '_explicit'`
(`_nmd/log/g73_trajetoria_P128.log`). O fix de precedência de 09-09 (`a._explicit`) assumiu que quem chama
`aplica_cenario` veio do argv; `politica_util.mundo()` monta um Namespace sem `_explicit`.
Quebra **5 ferramentas**: `trajetoria.py`, `julga_politica.py`, `julga_lote.py`, `clona_politica.py`,
`dados_campeao.py`. **Consertado** nesta rodada (uma linha, §4). Pred 163 pode ser re-enfileirada.

---

## 2. Onde o Fable ou o CS podem ter errado (com arquivo:linha)

| # | afirmação | veredito | evidência |
|---|---|---|---|
| 1 | "P512 rot = P128 ao milésimo" / "P não é alavanca" (diário 23:10) | **errado** | os 3 JSONs são o mesmo run (P=512); `e78/e43_P256.json` grava `P: 512`; argv em cada arquivo |
| 2 | "a pred 145 rodou P=128 três vezes" (diário 22:50) | **errado no número** | rodou P=**512** (o cenário v1 tem `protocolo.P = 512`) |
| 3 | σ .1 dá "+11–14 %" | **subestimado / base errada** | base pareada é `e43_P256R4jan` 4.522 → **+18.5 %** |
| 4 | "ótimo em ~.1" (pred 161) | **não medido** | .05 × .1 pareado = 2/5, t ≈ 0.8 |
| 5 | spec F2 "custo por ativação: silêncio é grátis" (`campo.py`, `ativ_blocos`) | **mede a coisa errada** | cobra `\|saída\|.mean`, e `campo.py:427` prova que o modo comum tem efeito zero; bancada: 99.6 % da conta é modo comum; smoke A: dof 15 ⇒ metab 1.71 |
| 6 | CS §E orçamento de atividade (`_fator_orc`) | **mesmo erro** | projeta pela soma de `\|saída\|`, também modo comum (corrigido junto, mesmo flag) |
| 7 | CS: "com R=4 a elite é quem nasceu bem" ⇒ jardim comum resolve | **✗ na prática** | jardim +3.8 %, 3/5, t ≈ 0.7 (§1.3) |
| 8 | fix de precedência `a._explicit` (09-09) | **regressão** | quebra 5 ferramentas via `politica_util.mundo`; `g73` exit=1 |
| 9 | "o reflexo empurra pro posto" (leitura da bancada) | **quase inerte** | dirige/desloca = 0.016 %: 99.98 % do empurrão é modo comum descartado |

Nada disso muda um resultado publicado como positivo — muda **negativos**: os "a peça não paga" medidos sob
custo por ativação (preds 136, 143) foram medidos com uma balança que pesa a escala do sentido.

---

## 3. Mundo B — `cenarios/mundoB_conta_justa.json` (pred 167)

**Uma lei trocada, o resto bit a bit igual ao Mundo A** (conferido: `diff` de A e B sem
`nome`/`predicao`/`ativ_centrada` é vazio). Mesmos 8 seres, mesmas 5 sementes, P128 G60 pac30 R4 σ .1.

> **A lei:** o cérebro paga pelo que **muda a decisão** — `ativ_centrada: true`, a conta do bloco passa a
> ser `|saída − média entre as 9 opções|` em vez de `|saída|`.

Por que essa e não o regime de 1.3 d ou o orçamento: porque as duas outras só fazem sentido **depois** de
saber se a penalidade das camadas era a conta ou a peça. Hoje o Mundo A vai gastar 4–5 h medindo arquiteturas
numa balança que cobra 99.6 % de nada; B é o controle que separa as duas coisas — e A **é** o controle de B.

Aposta (pred 167, com mecanismo): (a) metab do COMPLETO cai ≥ 30 % com o **mesmo** λ; (b) o buraco
COMPLETO − linear fecha pelo menos metade; (c) mesmo assim ninguém com camadas bate o linear em ≥ 5 %
(a peça continua sem informação nova — "seletor, não gerador"); (d) o ser que mais ganha de A para B é o
`COMPLETO hip 1.0` (é o que mais emite modo comum: desloca 93.3 com esc 1.0 contra 0.93 com esc .01).
Se (b) falhar, o custo por ativação sai do programa e a culpa é da peça.

**Armadilha de leitura (importante):** com `ativ_centrada` ligado, `medidas()` também mede centrado
(`campo.py: medidas` só força `medir_ativ`, o resto do cfg vem por cópia). Então `ativacao_bloco` do
Mundo B **não é comparável em valor absoluto** com o do Mundo A — são duas réguas. O que se compara entre
A e B é `metab`, `fit`, `ent`, `dof` e o **ranking** dos blocos, nunca o valor cru da ativação.

**Smoke já enfileirado** (`o7_smoke_mundoB`, P=8 G=1, e79) — ele é diretamente comparável ao
`s0_smoke_mundoA` (mesmo P, G, semente): basta comparar a coluna `metab` das duas saídas para ter a
primeira leitura da aposta (a) antes de gastar 4 h. **Não enfileirei a bateria B** — é do Fable, depois do A.

---

## 4. Alterações de código desta rodada (3, todas desligadas por padrão)

Detalhe e commits em `docs/AGENTE-OPUS-LOG.md`. Resumo:

1. **`e43_campo.py: aplica_cenario`** — `if not hasattr(a, '_explicit'): a._explicit = set()`.
   Conserta a regressão que quebrou 5 ferramentas (§1.8). Sem efeito no caminho do argv.
2. **`campo.py: ativ_centrada`** (cfg, `--ativ-centrada`, chave `corpo.ativ_centrada`) — `False` = hoje
   **bit a bit**. Muda `ativ_blocos` e `_fator_orc` para medir a saída centrada nas 9 opções.
   Portão novo em `testes_ativ.py` (`test_ativ_centrada`): camada lenta com `M` só em sentidos do **corpo**
   (iguais nas 9 opções por construção, achado E58) ⇒ saída puramente modo comum ⇒ cobra cheio no cru e
   ~0 no centrado; e identidade com λ = 0.
3. **`lab.py: campeao='reavaliado'`** (`--campeao`, chave `protocolo.campeao`) — `'ultimo'` = hoje
   **bit a bit**. Reavalia a elite (ne = 15 % de P) num mundo novo e exporta o campeão pela **média** das
   duas medidas. Custo ~0.25 % do run.

**O que eu NÃO mexi, e por quê:**
- **`DMAX` configurável** (córtex/hipocampo): é a mais arriscada (muda `N_COR`/`N_HIP` ⇒ nomes de genes,
  `GRUPOS`, `_LAYOUTS`, `alinha_semente`, e invalida toda semente gravada), e vai ao ar com uma bateria de
  4–5 h prestes a entrar. Além disso o argumento do CS (só 3.2 das 12 caixas são tocadas numa vida) prevê
  **nulo** para o hipocampo por falta de dado, não ganho — não vale o risco hoje.
- **`--neutro`** (GA com aptidão aleatória, pred 158): cabe, é barato, mas conserta a régua de uma métrica
  (`dof`) que já sabemos ser ≈ deriva. Fica atrás das três acima na fila de valor. Pred 158 continua **sem
  entrada no ledger** — alguém precisa escrevê-la.
- **O gradiente da distância como sentido** (§1.5, o reflexo a 0.016 %): é a mudança certa
  (dar ao ser `Δd` em vez de `d`, ou centrar os sentidos de opção), mas mexe no **espaço de sentidos** —
  invalida toda semente e todo campeão gravado. É proposta, não alteração; merece um cenário próprio.

---

## 5. O que decide a próxima bateria (resumo para o Fable)

1. **Mundo A pode rodar como está** — mas o resultado dele sobre "custo do cérebro" só é interpretável
   junto com o **Mundo B**. Rodar A sem B é medir a balança, não o cérebro.
2. **Jardim comum é neutro** (+3.8 %, 3/5, t ≈ 0.7). Ligue ou não ligue — mas o **mesmo** nos dois mundos.
3. **σ .1 está certo**; não gaste GPU procurando o ótimo entre .05 e .1 (empate a n=5). Se sobrar GPU,
   σ .02 responde se a curva ainda sobe.
4. **P = 128 é orçamento, não medida** (§1.1). Se alguma conclusão do Mundo A depender de "P não importa",
   ela não tem base.
5. **A célula mais barata da noite** é `--campeao reavaliado` no mesmo protocolo do σ (P256, σ .1, 60 ger.,
   5 sementes, ~14 min): se der ≥ +5 %, todo run futuro herda o ganho por 0.25 % de custo (pred 166).
6. **Pred 163 (trajetória) pode voltar para a fila** — a ferramenta está consertada (dois bugs, §1.8 e §6.2).

---

## 6. Medido depois de escrever o resto (02:1x) — o smoke A × B já responde parte da pred 167

### 6.1 Mundo A × Mundo B, os MESMOS 8 seres, mesmo P=8 G=1 semente 0

`_nmd/log/s0_smoke_mundoA.log` × `_nmd/log/o7_smoke_mundoB.log`. Única diferença entre os dois runs:
`ativ_centrada`.

| ser | fit A | fit B | Δ | metab A | metab B | ent A | ent B |
|---|---|---|---|---|---|---|---|
| linear | 4.085 | **4.085** | 0 | 1.00 | 1.00 | 11.9 | 11.9 |
| COMPLETO | 3.575 | **4.141** | **+0.57** | 1.71 | 1.04 | 10.8 | 12.1 |
| completo sem hipocampo | 3.581 | 4.131 | +0.55 | 1.69 | 1.04 | 10.8 | 12.1 |
| completo sem reflexo | 3.583 | **4.169** | **+0.59** | 1.70 | 1.04 | 10.8 | 12.2 |
| COMPLETO hip 1.0 | 3.572 | 4.051 | +0.48 | **1.78** | **1.06** | 10.6 | 11.7 |
| COMPLETO cortex 2.0 | 3.591 | 3.657 | **+0.07** | 1.34 | **1.12** | 6.3 | 6.2 |
| COMPLETO talamo fixo | 3.744 | 4.048 | +0.30 | 1.65 | 1.05 | 10.7 | 11.6 |
| COMPLETO temp .3 | 2.788 | 2.882 | +0.09 | 1.63 | 1.05 | 7.8 | 7.9 |

O que isso diz (com a ressalva dura: **n = 1 semente, P = 8, G = 1** — os genomas são a semente linear
mais ruído; isto isola o efeito da CONTA, e não diz nada sobre o que a evolução acha depois):

- **O linear é idêntico nos dois** (a lei só toca blocos): identidade confirmada fora do teste unitário.
- **A conta do cérebro cai 94 %**: sobretaxa do COMPLETO (metab − 1) 0.71 → **0.04**.
- **O buraco COMPLETO × linear some**: A = −12.5 %, B = **+1.4 %**. A pred 167(b) previa fechar metade;
  fechou inteiro **neste smoke**. Ou seja: a penalidade das camadas no Mundo A é **a balança**, não a peça.
- **A conta justa DISCRIMINA, a antiga não.** Na conta antiga todo mundo pagava 1.6–1.8 (menos o
  `cortex 2.0`). Na conta nova quem continua pagando é exatamente quem **emite sinal diferencial de
  verdade**: `cortex 2.0` (1.12; na bancada é o que mais dirige, .714, e inverte sinal em 31.8 %) e
  `hip 1.0` (1.06; dirige .330). Os demais caem para 1.04–1.05. Isso é o que uma conta deve fazer.
- **Pred 167(d) ✗**: apostei que `hip 1.0` seria quem mais ganharia de A para B; quem mais ganhou foi
  `completo sem reflexo` (+0.59) e o `hip 1.0` foi o 4º (+0.48). Mecanismo do erro: o `hip 1.0` emite
  modo comum **e** diferencial, então continua pagando na conta nova — ganha menos líquido. O sinal do
  mecanismo está certo, o ranking que eu previ estava errado.

**Consequência prática para o Fable:** com `ativ_centrada` e λ = .3 a conta do cérebro fica **quase
desligada** (0.04 de metab). O Mundo B como está responde *"a penalidade era a balança?"* — e o smoke já
diz que sim. Se o objetivo for um mundo onde o cérebro **paga de verdade, mas dividido por influência**,
o λ equivalente é `0.3 × 0.71/0.04 ≈ 5.3` (mesma conta total do Mundo A, repartida pelo que muda a
decisão). Isso é um **Mundo C**, não escrevi o arquivo e não enfileirei — é decisão de vocês.

### 6.2 Segundo bug na mesma cadeia (trajetória), consertado

Depois do fix do `_explicit`, a `trajetoria.py` andou mais e morreu adiante:
`TypeError: int() argument must be ... not 'NoneType'` — `politica_util.mundo()` copia `cfg.horizonte`
do cenário mas **nunca copia `T_max`**, então com `horizonte='aberto'` o `cfg.T_max` fica `None`
(em `e43_campo.main` o `T_max` vem do preset, e essa parte não existe no `politica_util`).
Consertado com a mesma regra do e43 (`240*30` quando aberto). Re-enfileirado como `o10_trajetoria_P128`:
**exit=0 em 694 s**, `e72/trajetoria_e43_P128.json` gravado. A cadeia inteira está de pé de novo.

### 6.3 Pred 163 tem números (fechamento é do Fable)

`_nmd/log/o10_trajetoria_P128.log` — campeões do e43_P128 nos mesmos 24 blocos (3 mapas × R8, 5 sementes):

| par | concordância de ação | 1ª divergência (mediana) | braço vive mais em | opção que mais difere |
|---|---|---|---|---|
| linear × COMPLETO | **0.269** | **18** tiques (p10 1) | 39 % dos blocos | **op8** (movimento) |
| linear × sem hipocampo | 0.277 | 19 tiques (p10 4) | 40 % dos blocos | op8 (movimento) |

Contra a aposta da pred 163: concordância ≥ .80 **✗ e por muito** (deu .27); 1ª divergência < 200 tiques
**✓ e muito mais cedo** (18); vive mais em ≤ 40 % dos blocos **✓** (39–40 %, no fio); "a opção que mais
difere é de SERVIÇO" **✗** — é de movimento.

O detalhe que vale mais que os quatro: **o estado do linear na divergência é um corpo SAUDÁVEL**
(fome 18, gasolina 76, água 83, vida 100). A divergência não é disparada por necessidade — ela acontece
já no tique ~18, com o tanque cheio. Ou seja: os dois cérebros **não são o mesmo ser com um enfeite**;
divergem desde o começo, em opção de direção, com o corpo em ordem. Isso mata de vez a leitura
"as camadas quase não dirigem" (§1.5) e recoloca a pergunta certa: as camadas dirigem bastante e
**mesmo assim** não vivem mais (39 % pareado). O problema não é autoridade, é **para onde** elas dirigem.
