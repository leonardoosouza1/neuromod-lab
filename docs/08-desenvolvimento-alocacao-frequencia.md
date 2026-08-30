# Desenvolvimento, Alocação e Frequência

**Documento de referência.** Como neurônios se distribuem, como regiões se especializam sozinhas, e o papel da frequência. Escrito para ser lido junto com `docs/01` (neurônio ≡ EMA, banco de filtros) e `docs/03` (neuromodulação).

**Princípio central deste documento:**

> Você não aloca neurônios por região. Você projeta quatro forças locais — cronograma, aferência, competição e custo — e a anatomia emerge. Nenhum mecanismo aqui precisa de conhecimento global da arquitetura.

---

## 1. Alometria — a lei da alocação

Quando o cérebro cresce, as partes **não crescem proporcionalmente**:

```
N_parte = a · N_total^b
```

Expoentes aproximados (mamíferos, contagem por fracionador isotrópico):

| Parte | Expoente `b` | Comportamento |
|---|---|---|
| Córtex | ~1,35 | **hiperalométrico** — cresce mais rápido que o total |
| Cerebelo | ~1,00 | isométrico — acompanha |
| Resto (tronco, etc.) | ~0,70 | **hipoalométrico** — fica para trás |

### 1.1 Cálculo trabalhado

Se `N_total` for multiplicado por um fator `f`, cada parte é multiplicada por `f^b`:

```
N_total ×1,5   →  córtex ×1,73   cerebelo ×1,50   resto ×1,33
N_total ×2,0   →  córtex ×2,55   cerebelo ×2,00   resto ×1,62
N_total ×4,0   →  córtex ×6,50   cerebelo ×4,00   resto ×2,64
```

**Dobrar o total multiplica o córtex por 2,55 e o resto por 1,62.** A composição muda sozinha, na direção de mais córtex, sem nenhum gene específico para córtex.

### 1.2 Fato conservado

Córtex e cerebelo mantêm razão de ~1:4 em número de neurônios através de quase toda a evolução dos mamíferos — mesmo com o córtex ocupando ~80 % da massa. Restrição de desenvolvimento profunda, útil como teste de sanidade: se um modelo produz razões muito fora disso, algo está errado.

---

## 2. Cronograma — o mecanismo por trás da alometria

Mecanismo descrito por Finlay & Darlington (*Science*, 1995): a neurogênese é **sequencial e exponencial**. As partes começam e terminam de proliferar em ordem fixa — tronco cedo, córtex tarde.

```
N_parte ∝ 2^((t_fim,parte − t_início,parte) · taxa)
```

### 2.1 O erro comum (e a correção)

Se todas as partes terminassem juntas, prolongar o cronograma escalaria todas igualmente e a **composição não mudaria**:

```
T=1,0  →  tronco 74,9%  cerebelo 17,5%  córtex 7,6%   N=85
T=1,6  →  tronco 74,9%  cerebelo 17,5%  córtex 7,6%   N=1036   ← composição idêntica
```

O mecanismo real é que **cada parte para em momento diferente** — o córtex é o último. Prolongar a janela terminal beneficia só quem ainda está proliferando:

```
extensão  tronco  cerebelo  córtex   N_total
  +0,0     43,1%    28,4%    28,4%      23
  +0,1     37,6%    24,8%    37,6%      26
  +0,2     31,5%    20,8%    47,7%      31
  +0,3     25,3%    16,7%    58,1%      39
```

**Estender a janela cortical em 0,3 leva o córtex de 28 % a 58 % da população.** Isso é "late equals large": o que se forma por último é o que mais cresce.

### 2.2 Consequência de projeto

> Você não codifica `N` por região no genoma. Você codifica **um parâmetro de cronograma**, e a alometria acontece como consequência.

```python
inicio = {"tronco": 0.00, "cerebelo": 0.35, "cortex": 0.55}   # ordem fixa
fim    = {"tronco": 0.55, "cerebelo": 0.80, "cortex": 1.00}   # córtex é o último
ext    = gene                                                  # UM gene evoluível

N = {p: round(k * 2 ** ((fim[p] + (ext if p == "cortex" else 0) - inicio[p]) * taxa))
     for p in inicio}
```

---

## 3. Aferência — como uma região vira "visual"

### 3.1 O achado que derruba a alocação explícita

Hipótese do protomapa (Rakic) + evidência experimental: em ferrets, a entrada da retina foi redirecionada para o córtex **auditivo**, e ele desenvolveu mapas visuais orientados; o animal enxergou por ali.

> **Regra:** a identidade de uma região cortical é dominada pela **entrada que ela recebe**, não por genes daquela região. O tecido é largamente equipotente; o input esculpe.

### 3.2 Implementação

Não fazer:
```python
regioes = {"visual": 200, "auditivo": 150, "motor": 120}      # ❌ alocação explícita
```

Fazer — folha equipotente + gradientes fracos (análogo a FGF8/Emx2):
```python
pos  = grid_2d(N)                      # (N,2): a folha cortical
grad = [pos[:,0], pos[:,1]]            # protomapa fraco, 2 gradientes ortogonais

# aferências chegam com viés ESPACIAL, não com destino fixo
P(aferência_k → unidade_i) ∝ exp(−‖pos_i − alvo_k‖² / σ²)
```

`σ` grande → modalidades se sobrepõem no início e se segregam depois por atividade.
`σ` pequeno → especialistas desde o começo, menos plasticidade.

---

## 4. Segregação — a fronteira emerge da correlação

Regra hebbiana com **competição por recurso finito** (normalização subtrativa):

```
Δw_ik = η · ( a_i·a_k  −  α·w_ik·Σ_j a_j·a_k )
```

Entradas que disparam juntas ficam juntas; descorrelacionadas se separam. Reproduz sem nenhuma instrução explícita:

- **colunas de dominância ocular** — dois olhos descorrelacionados → faixas alternadas
- **mapas retinotópicos** — vizinhança na retina → vizinhança no córtex
- **fronteiras entre áreas** — modalidades diferentes → territórios distintos

> A fronteira entre "visual" e "auditivo" não é desenhada. **Ela é onde a correlação cruzada cai.**

---

## 5. Frequência — o canal que faltava

Correlação não é apenas "ativo ao mesmo tempo". É **em fase, na mesma banda**. Duas populações simultaneamente ativas em frequências diferentes não se acoplam eficientemente.

### 5.1 Coerência de comunicação

Hipótese de Fries: dois grupos só trocam informação eficientemente se seus ciclos de excitabilidade estiverem alinhados. A janela em que um neurônio aceita entrada é rítmica — entrada em fase errada é ignorada.

**Consequência:** frequência é um canal de **multiplexação**. Várias conversas no mesmo tecido, separadas por banda em vez de por espaço.

### 5.2 Plasticidade depende de frequência (corrige §4)

Hebb simples é incompleto — o **sinal** da mudança depende da frequência:

```
baixa frequência (~1 Hz)      → depressão de longo prazo (enfraquece)
alta frequência (~50–100 Hz)  → potenciação (fortalece)
```

Versão dependente de timing (STDP), janela ≈ ±20 ms:

```
pré antes de pós (Δt > 0)  → fortalece
pós antes de pré (Δt < 0)  → enfraquece
```

**Implicação de projeto:** não basta "entrada rica". A estatística temporal fina determina se as sinapses fortalecem ou apagam. Entrada rica mas lenta demais pode **podar** o território em vez de capturá-lo.

### 5.3 Bandas ≡ o banco de τ log-espaçado

```
banda     f (Hz)        τ = 1/(2πf)      papel
gamma     30–100        1,6 –  5,3 ms    processamento local, ligação de features
beta      13–30         5,3 – 12,2 ms    manutenção de estado motor
alpha      8–13        12,2 – 19,9 ms    inibição / gating de atenção
theta      4–8         19,9 – 39,8 ms    memória, sequências (hipocampo)
delta    0,5–4         39,8 – 318  ms    consolidação, sono
```

Razão média entre bandas vizinhas ≈ **2,3×**, espaçamento **logarítmico**.

> **Esta é a mesma estrutura projetada em `docs/01` §3 e que emergiu sozinha no exp05** (a evolução escolheu τ = 1,5 e 23,4 — spread de 16×, sem instrução). Frequência e constante de tempo são o mesmo objeto em dois domínios: `f_corte = 1/(2πτ)`, `|H(ω)| = 1/√(1+(ωτ)²)`.

### 5.4 Acoplamento entre bandas = a segunda camada

A fase da theta modula a amplitude da gamma. **Ritmo lento organizando o rápido — estruturalmente idêntico ao que o modulador faz com o núcleo** em `docs/03`: multiplicativo, lento sobre rápido.

E neuromodulação desloca a banda dominante: acetilcolina empurra para gamma; estados de sono para delta. Ou seja, o canal `sens_rec` (ACh) não muda só a razão entrada/recorrência — muda **em qual escala de tempo a rede opera**.

### 5.5 Ondas espontâneas — antes de haver mundo

A retina gera ondas de atividade correlacionada **antes de o animal abrir os olhos**, e elas já esculpem os mapas.

**Consequência de projeto:** é necessário um gerador rítmico endógeno na fase de aferência, senão a segregação não tem o que correlacionar no início do desenvolvimento.

### 5.6 Endereçamento com dimensão de banda

```
P(conexão) ∝ exp(−d²/σ²)                        ← só espaço (incompleto)
P(conexão) ∝ exp(−d²/σ²) · coerência(f_i, f_j)  ← espaço E banda
```

Permite que áreas se separem **sem estarem espacialmente distantes**.

### 5.7 Ressalva

A função computacional das oscilações é **debatida**. Existe corrente que as trata como epifenômeno — subproduto de laços excitatório-inibitórios, não mecanismo causal. A evidência de coerência de comunicação é forte, mas não é consenso fechado.

---

## 6. Poda — o tamanho se ajusta à demanda

Aproximadamente **50 % dos neurônios gerados morrem**. A sobrevivência depende de competição por fatores tróficos limitados produzidos pelo **alvo**:

```
quota_i = trófico_total · atividade_i / Σ_j atividade_j
sobrevive_i  ⟺  quota_i > limiar
```

### 6.1 O detalhe que faz funcionar

Com trófico **fixo**, a poda não se adapta ao ambiente:

```
ambiente pobre  (demanda 0,2)  →  sobrevivem 71,9 %
ambiente médio  (demanda 0,5)  →  sobrevivem 68,6 %
ambiente rico   (demanda 0,9)  →  sobrevivem 71,2 %      ← quase idêntico, inútil
```

Com trófico **proporcional à demanda do alvo** (alvo pouco usado produz pouco):

```
ambiente pobre  (trófico 80)   →  sobrevivem  6,8 %
ambiente médio  (trófico 200)  →  sobrevivem 62,1 %
ambiente rico   (trófico 360)  →  sobrevivem 79,8 %      ← agora se auto-dimensiona
```

> **A população se ajusta ao tamanho do problema sem você especificar nada** — desde que o suprimento trófico escale com o uso do alvo.

Isto é o **exp02 do projeto** em outro domínio: pressão metabólica com tensão presente produz especialização, não colapso. Já validado.

---

## 7. Custo de fiação — por que esparsidade é obrigatória

Volume de conexões cresce mais rápido que número de neurônios. Substância branca escala como ~`N^1,23` — mais rápido que os neurônios, e é ela que limita.

```
N          conexões densas   esparsas (~N·logN·10)   razão
1e3            1,00e+06            9,97e+04             10×
1e4            1,00e+08            1,33e+06             75×
1e5            1,00e+10            1,66e+07            602×
1e6            1,00e+12            1,99e+08          5 017×
```

Soluções observadas na biologia:
- conectividade **esparsa e local** (maioria das conexões curtas)
- **modularidade** (denso dentro, esparso entre)
- **girificação** (dobrar a superfície para encurtar distâncias)

**Regra de projeto:** aumentar `N` exige aumentar esparsidade ou modularidade. Mesma lição do exp05, onde `N ≥ 10` piorou — capacidade sem estrutura que a organize é passivo.

### 7.1 Nota sobre densidade

O córtex cresce em **área**, não em espessura (~2–4 mm através de espécies que variam mil vezes em área). O número de neurônios por coluna vertical é aproximadamente conservado — é uma folha que se expande.

Roedores e primatas seguem regras de escalonamento **diferentes**: o córtex de primatas ganha neurônios sem aumento proporcional no tamanho celular. Não existe lei universal de densidade.

---

## 8. Períodos críticos — quando o mapa trava

O período crítico não é um relógio separado. É **plasticidade modulada**:

```
η(t) = η₀ · m_ACh(t) · f(maturação_inibitória)
```

Evidência: o período crítico **abre** quando a inibição (interneurônios PV) amadurece, e pode ser **reaberto** em adulto por manipulação da inibição ou por acetilcolina.

```
ACh alta (novidade, atenção)      →  plasticidade alta  →  mapa maleável
inibição madura + ACh baixa       →  plasticidade baixa →  mapa consolidado
```

**Isto fornece o botão de "quando travar".** Sem fechamento, o mapa nunca estabiliza e o sistema esquece continuamente. Note que é o mesmo canal `sens_rec`/ACh de `docs/03`, agora atuando no desenvolvimento.

---

## 9. O algoritmo completo

```
FASE 1 — PROLIFERAÇÃO
  gene de cronograma → N por parte via 2^((t_fim − t_início)·taxa)
  unidades nascem numa folha 2D com 2 gradientes fracos
  → alometria emerge (§1, §2)

FASE 2 — AFERÊNCIA
  P(input_k → unidade_i) ∝ exp(−d²/σ²) · coerência(f_i, f_k)
  ondas espontâneas fornecem atividade antes do mundo (§5.5)
  → endereçamento probabilístico, sem destino fixo (§3)

FASE 3 — SEGREGAÇÃO
  Hebb + normalização subtrativa, com sinal dependente de frequência (§5.2)
  → mapas e fronteiras emergem da estrutura de correlação (§4)

FASE 4 — PODA
  competição trófica com suprimento proporcional ao uso do alvo
  → cada área se dimensiona à demanda (§6)

FASE 5 — CONSOLIDAÇÃO
  maturação inibitória + queda de ACh → η despenca
  → mapa trava; modulação continua ajustando ganho (§8)
```

Cinco fases, todas locais. Nenhuma precisa saber a anatomia final.

---

## 10. Como guiar — tabela de controle

Você nunca escreve "esta região é visual". Você cria a condição:

| Objetivo | Parâmetro a mexer | Efeito |
|---|---|---|
| mais "córtex" | estender janela terminal cortical | 28 % → 58 % da população (§2.1) |
| área visual maior | mais aferências visuais / entrada mais rica | mais território capturado na segregação |
| áreas mais separadas | descorrelacionar as entradas | fronteiras mais nítidas |
| separar sem separar no espaço | bandas de frequência distintas | multiplexação (§5.6) |
| mais especialistas | `σ` menor na aferência | menos sobreposição inicial |
| mapa trava mais cedo | fechar período crítico antes | menos plasticidade adulta |
| menos neurônios sobrando | reduzir suprimento trófico | poda mais agressiva (§6.1) |
| suportar `N` maior | aumentar esparsidade/modularidade | evita explosão de fiação (§7) |

---

## 11. Predições testáveis

| # | Predição | Refuta se |
|---|---|---|
| D1 | Treinar o mesmo genoma com estatísticas de entrada diferentes produz mapas com **proporções de área diferentes**, previsíveis pela variância de cada canal | proporções idênticas → o input não esculpe |
| D2 | Razão córtex:cerebelo emergente fica próxima de 1:4 sem ser imposta | razão arbitrária → cronograma mal calibrado |
| D3 | Entrada rica mas de baixa frequência **poda** o território em vez de capturá-lo (§5.2) | captura igual em qualquer frequência → STDP irrelevante no modelo |
| D4 | Remover ondas espontâneas degrada os mapas iniciais | mapas idênticos → a fase 2 não depende de atividade endógena |
| D5 | Com trófico fixo, a população **não** se adapta à demanda; com trófico proporcional, adapta | comportamento igual nos dois → a poda não é o mecanismo de dimensionamento |
| D6 | Aumentar `N` sem aumentar esparsidade degrada o desempenho | ganho monotônico com `N` → custo de fiação não está modelado |

D5 já tem evidência numérica (§6.1). D6 já tem evidência no exp05.

---

## 12. Ressalvas

- Os expoentes alométricos (~1,35 córtex, ~0,70 resto) e a razão 1:4 foram **citados de memória**. Verificar em Herculano-Houzel (2009, *Frontiers in Human Neuroscience*, "The human brain in numbers") e Finlay & Darlington (1995, *Science*) antes de uso formal. Apenas o item sobre escalonamento diferencial roedor/primata foi verificado em fonte durante a sessão.
- A função computacional das oscilações é debatida (§5.7).
- O experimento de reroteamento em ferrets (Sur e colegas) é real, mas a extensão de "70 % determinado pelo input" é uma paráfrase, não um número medido.
- Nada aqui foi implementado ou testado. É especificação com cálculos ilustrativos, não resultado.

---

## 13. Referências

| Trabalho | Uso |
|---|---|
| Herculano-Houzel — contagens por fracionador isotrópico; "The human brain in numbers" (2009) | §1 alometria, §7.1 densidade |
| Finlay & Darlington — *Linked regularities in the development and evolution of mammalian brains*, Science 268:1578 (1995) | §2 cronograma, "late equals large" |
| Rakic — hipótese do protomapa | §3 aferência |
| Sur e colegas — reroteamento retina→córtex auditivo em ferrets | §3.1 |
| Fries — hipótese de coerência de comunicação | §5.1 |
| Hensch — períodos críticos e maturação inibitória | §8 |
| Buzsáki — *Rhythms of the Brain* | §5.3 hierarquia de bandas |
