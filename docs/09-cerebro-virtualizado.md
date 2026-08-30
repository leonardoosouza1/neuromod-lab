# Cérebro Virtualizado — Referência de Emulação

**Documento de engenharia.** Equações, constantes e limites para construir um cérebro artificial baseado em princípios biológicos reais — não uma cópia do humano, mas um substrato evolutivo lapidável.

**Escopo declarado:** o objetivo não é reproduzir cognição humana. É construir um substrato com a estrutura certa (múltiplas escalas de tempo, neuromodulação, esparsidade forçada, aprendizado local) sobre o qual evolução e corpo possam operar.

**Documentos irmãos:** `docs/01` (neurônio ≡ EMA), `docs/03` (neuromodulação), `docs/04` (dimensionamento), `docs/07` (corpo mínimo), `docs/08` (desenvolvimento e alocação).

---

## 0. A decisão de nível de abstração (leia antes de tudo)

### 0.1 Por que NÃO emular átomos

```
passo de dinâmica molecular:     10⁻¹⁵ s (femtosegundo)
duração de um spike:             10⁻³ s
passos necessários:              10¹²
átomos numa membrana neuronal:   ~10⁹
operações para UM spike:         10²¹

GPU moderna (~10¹⁴ FLOP/s) → 10⁷ s ≈ 4 meses de cálculo
para um único disparo de um único neurônio.
```

### 0.2 Por que não é preciso

**A química já está resolvida analiticamente.** A equação de Nernst *é* o resultado agregado do comportamento de 10²³ íons. Hodgkin e Huxley receberam o Nobel de 1963 precisamente por medir isso e fechar em quatro equações.

Emular átomos para obter `E_K = −95 mV` seria simular elétrons para calcular a corrente de um resistor. A Lei de Ohm existe porque o agregado tem lei própria.

### 0.3 Onde a química entra de verdade

| Fenômeno | Precisa de átomos? | Substituto analítico |
|---|---|---|
| Potencial de equilíbrio iônico | não | Nernst (§1.1) |
| Potencial de repouso | não | GHK (§1.2) |
| Abertura de canal por voltagem | não | cinética de Hodgkin-Huxley (§2.1) |
| Bloqueio de Mg²⁺ no NMDA | não | forma fechada de Jahr-Stevens (§3.3) |
| Difusão de neuromodulador | não | EDO de reserva + difusão (§6.2) |
| Cinética de receptor | não | cinética de dois estados (§3.2) |
| Dobramento de proteína, design de fármaco | **sim** | fora do escopo |

**Nível de abstração escolhido:** condutâncias e concentrações agregadas. Todas as equações abaixo operam nesse nível.

---

## 1. Camada química — as constantes que fixam tudo

### 1.1 Equação de Nernst

```
E_íon = (R·T)/(z·F) · ln([íon]_fora / [íon]_dentro)
```

`R` = 8,314 J/(mol·K) · `T` = 310 K (37 °C) · `F` = 96 485 C/mol · `z` = valência

**Valores calculados** (concentrações de mamífero, mM):

| Íon | [dentro] | [fora] | z | E (mV) |
|---|---|---|---|---|
| K⁺ | 140 | 4 | +1 | **−94,97** |
| Na⁺ | 15 | 145 | +1 | **+60,60** |
| Cl⁻ | 10 | 110 | −1 | **−64,05** |
| Ca²⁺ | 0,0001 | 2 | +2 | **+132,27** |

Estes números **não são escolhidos** — são consequência termodinâmica dos gradientes de concentração, mantidos pela bomba Na⁺/K⁺-ATPase (3 Na⁺ para fora, 2 K⁺ para dentro, 1 ATP). Essa bomba consome ~70 % do ATP cerebral: **o custo energético do cérebro é majoritariamente manter esses gradientes.**

### 1.2 Goldman-Hodgkin-Katz — o repouso real

O potencial de repouso não é o de nenhum íon isolado, mas a média ponderada pelas permeabilidades:

```
V_rest = (RT/F) · ln[ (P_K[K]_out + P_Na[Na]_out + P_Cl[Cl]_in) /
                      (P_K[K]_in  + P_Na[Na]_in  + P_Cl[Cl]_out) ]
```

Com `P_K : P_Na : P_Cl = 1 : 0,04 : 0,45` → **V_rest = −69,11 mV**

Note a inversão de Cl⁻ (ânion) no numerador/denominador.

### 1.3 Implementação mínima

```python
R, F, T = 8.314, 96485.0, 310.0
def nernst(c_in, c_out, z=1):
    return (R*T)/(z*F) * math.log(c_out/c_in) * 1000   # mV
```

Duas linhas substituem 10²¹ operações de dinâmica molecular.

---

## 2. Camada elétrica — o neurônio

### 2.1 Hodgkin-Huxley (referência exata)

```
C_m·dV/dt = −g_Na·m³h·(V−E_Na) − g_K·n⁴·(V−E_K) − g_L·(V−E_L) + I_ext

dm/dt = α_m(V)·(1−m) − β_m(V)·m        ativação Na⁺   (τ ~ 0,1 ms)
dh/dt = α_h(V)·(1−h) − β_h(V)·h        inativação Na⁺ (τ ~ 1–8 ms)
dn/dt = α_n(V)·(1−n) − β_n(V)·n        ativação K⁺    (τ ~ 1–5 ms)
```

Parâmetros clássicos (axônio de lula, 6,3 °C):
```
C_m = 1 µF/cm²
g_Na = 120 mS/cm²,  E_Na = +50 mV
g_K  =  36 mS/cm²,  E_K  = −77 mV
g_L  = 0,3 mS/cm²,  E_L  = −54,4 mV
```

Taxas (V em mV):
```
α_m = 0,1(V+40)/(1−e^(−(V+40)/10))      β_m = 4·e^(−(V+65)/18)
α_h = 0,07·e^(−(V+65)/20)               β_h = 1/(1+e^(−(V+35)/10))
α_n = 0,01(V+55)/(1−e^(−(V+55)/10))     β_n = 0,125·e^(−(V+65)/80)
```

**Observação estrutural crítica:** cada uma de `m`, `h`, `n` é uma EMA com τ dependente da voltagem. **O spike emerge da competição entre um τ rápido (m) e dois lentos (h, n).** É o banco de τ de `docs/01`, operando em escala de milissegundos. O potencial de ação não é programado — é uma consequência dinâmica.

**Integração:** sistema rígido (*stiff*). Exige passo ≤ 10 µs com Euler explícito, ou usar Runge-Kutta 4 / método exponencial. Ver §9.

### 2.2 Forma reduzida — a EMA

Fixando as condutâncias:

```
τ_m·dV/dt = −(V − V_rest) + R_m·I,     τ_m = R_m·C_m ≈ 10–20 ms
```

Discretizando com `α = e^(−Δt/τ_m)`:

```
V[n] = α·V[n−1] + (1−α)·(V_rest + R_m·I)
```

**Com Δt = 10 ms e τ_m = 14 ms, α ≈ 0,5.** É exatamente a EMA de `docs/01`. O neurônio biológico *é* um integrador com vazamento; a não-linearidade adicional é o limiar.

### 2.3 Izhikevich — o ponto ótimo custo/realismo

```
dv/dt = 0,04v² + 5v + 140 − u + I
du/dt = a·(b·v − u)
se v ≥ 30 mV:   v ← c,   u ← u + d
```

Quatro parâmetros geram ~20 padrões de disparo documentados:

| Tipo | a | b | c | d |
|---|---|---|---|---|
| Regular spiking (RS, excitatório cortical) | 0,02 | 0,2 | −65 | 8 |
| Intrinsically bursting (IB) | 0,02 | 0,2 | −55 | 4 |
| Chattering (CH) | 0,02 | 0,2 | −50 | 2 |
| Fast spiking (FS, interneurônio inibitório) | 0,10 | 0,2 | −65 | 2 |
| Low-threshold spiking (LTS) | 0,02 | 0,25 | −65 | 2 |

Para diversidade populacional: `a,b` fixos + `c = −65 + 15r²`, `d = 8 − 6r²`, com `r ∈ U(0,1)`.

### 2.4 AdEx (adaptive exponential)

```
C·dV/dt = −g_L(V−E_L) + g_L·Δ_T·e^((V−V_T)/Δ_T) − w + I
τ_w·dw/dt = a(V−E_L) − w
se V > V_peak:  V ← V_reset,  w ← w + b
```

Mais fiel a dados experimentais que Izhikevich; mesmo custo (2 EDOs). Preferível quando se quer ajustar a neurônios reais medidos.

### 2.5 Custo computacional medido

| Modelo | EDOs | FLOPs/ms | 10⁶ neurônios em tempo real |
|---|---|---|---|
| Hodgkin-Huxley | 4 | 1200 | **1200 GFLOP/s** |
| AdEx | 2 | 15 | 15 GFLOP/s |
| Izhikevich | 2 | 13 | **13 GFLOP/s** |
| LIF | 1 | 5 | 5 GFLOP/s |

**Decisão de projeto:** Izhikevich para escala; HH apenas para validar circuitos pequenos.

---

## 3. Camada sináptica — a química emulável

### 3.1 Corrente sináptica

```
I_sin = g_max · s(t) · (V − E_rev)
```

`s(t)` = fração de receptores abertos, `E_rev` = potencial de reversão.

### 3.2 Cinética de dois estados

```
ds/dt = α·[T]·(1−s) − β·s
```

Aproximação prática (dupla exponencial, disparo em `t₀`):

```
s(t) = A·(e^(−(t−t₀)/τ_decay) − e^(−(t−t₀)/τ_rise))
```

### 3.3 Constantes reais por receptor

| Receptor | τ_subida | τ_descida | E_rev | Função |
|---|---|---|---|---|
| **AMPA** | 0,5 ms | 3 ms | 0 mV | excitação rápida |
| **NMDA** | 2 ms | 100 ms | 0 mV | coincidência, Ca²⁺, plasticidade |
| **GABA_A** | 0,5 ms | 6 ms | −70 mV | inibição rápida |
| **GABA_B** | 50 ms | 200 ms | −95 mV | inibição lenta, metabotrópica |

### 3.4 NMDA — a química que implementa o Hebb

Bloqueio de Mg²⁺ dependente de voltagem (Jahr & Stevens):

```
B(V) = 1 / (1 + ([Mg²⁺]/3,57)·e^(−0,062·V))
I_NMDA = g_max · s · B(V) · (V − E_rev)
```

Com [Mg²⁺] = 1 mM:

```
V = −80 mV →  2,4 % de condução   BLOQUEADO
V = −70 mV →  4,4 %               BLOQUEADO
V = −60 mV →  8,0 %               BLOQUEADO
V = −40 mV → 23,0 %               parcial
V = −20 mV → 50,8 %               parcial
V =   0 mV → 78,1 %               ABERTO
V = +20 mV → 92,5 %               ABERTO
```

> **Este é o mecanismo físico do "disparam juntos, conectam-se".** O canal só conduz quando **o glutamato chegou (pré-sináptico) E a célula já está despolarizada (pós-sináptico)**. É uma porta lógica AND implementada em química, e o Ca²⁺ que entra por ele é o sinal que dispara a plasticidade.

Uma equação de sete caracteres substitui a simulação de um íon de magnésio num poro proteico.

### 3.5 STDP — plasticidade dependente de timing

```
Δw = +A₊·e^(−Δt/τ₊)     se Δt > 0   (pré antes de pós → potencia)
Δw = −A₋·e^(+Δt/τ₋)     se Δt < 0   (pós antes de pré → deprime)

Δt = t_pós − t_pré,   τ₊ ≈ τ₋ ≈ 20 ms,   A₋/A₊ ≈ 1,05
```

**Implementação por traços** (O(1) por sinapse, sem armazenar tempos):

```
dx_pré/dt  = −x_pré/τ₊  + Σ δ(t − t_pré)      traço pré-sináptico
dy_pós/dt  = −y_pós/τ₋  + Σ δ(t − t_pós)      traço pós-sináptico

no spike pré:  w ← w − A₋·y_pós
no spike pós:  w ← w + A₊·x_pré
```

**Ambos os traços são EMAs.** É a mesma estrutura de `plasticity.py`.

### 3.6 Regra de três fatores (a versão modulada)

```
de_ij/dt = −e_ij/τ_e + (traço STDP)          elegibilidade, τ_e ≈ 1–2 s
Δw_ij    = η(m_DA)·e_ij  −  λ(m_cort)·w_ij   consolidação + esquecimento
```

O traço marca coincidência e **espera**. Se o modulador chegar dentro de τ_e, consolida; senão evapora. Resolve atribuição de crédito temporal sem retropropagação.

---

## 4. Camada estrutural — as partes e suas matemáticas distintas

> **Não existe "o algoritmo do cérebro". Existem cinco, com arquiteturas e regras de aprendizado incompatíveis entre si.** Qualquer tentativa de arquitetura única copia a parte errada.

### 4.1 Cerebelo — ~69 dos 86 bilhões de neurônios

```
ARQUITETURA
  fibras musgosas (poucas) → células granulares (bilhões, esparsíssimas: ~1-5% ativas)
  → fibras paralelas → células de Purkinje (fan-in ~10⁵ cada)
  fibra trepadeira (1 por Purkinje) → sinal de ERRO

MODELO (Marr–Albus–Ito)
  granulares  = expansão dimensional esparsa  → É UM RESERVOIR
  Purkinje    = readout linear treinado
  fibra trep. = professor supervisionado
  Δw_pf→pk = −η · atividade_pf · sinal_fibra_trepadeira    (LTD)
```

**Quatro quintos dos neurônios do cérebro implementam reservoir computing com readout linear.** É a arquitetura de `docs/01` §5, em carne.

Função: modelo direto (*forward model*) do corpo, timing preciso, correção de erro motor.

### 4.2 Gânglios da base — seleção de ação

```
via direta   (D1, "go"):     córtex → estriado → GPi/SNr → tálamo → desinibe
via indireta (D2, "no-go"):  córtex → estriado → GPe → STN → GPi → inibe

DOPAMINA = erro de predição de recompensa (TD error)
  δ(t) = r(t) + γ·V(s_{t+1}) − V(s_t)

  δ > 0  → melhor que esperado → potencia via direta   (aprenda a fazer)
  δ < 0  → pior que esperado   → potencia via indireta (aprenda a evitar)
```

**Formalização:** actor-critic. Estriado = actor; dopamina = critic. Mapeamento neurociência↔RL mais bem estabelecido que existe.

### 4.3 Hipocampo — memória episódica

```
CA3 = rede recorrente atratora (Hopfield)
  capacidade ≈ 0,14·N padrões
  E = −½ Σᵢⱼ wᵢⱼ sᵢ sⱼ            energia; mínimos = memórias
  wᵢⱼ = (1/N) Σ_padrões ξᵢ ξⱼ     regra de Hebb

Células de lugar   → código de posição
Células de grade   → código modular (razão de escala ~1,4 entre módulos)
Replay em sono     → consolidação para o córtex
```

O código de grade é aritmética modular com módulos incomensuráveis — capacidade exponencial no número de módulos.

### 4.4 Córtex — hierarquia preditiva

```
CODIFICAÇÃO PREDITIVA
  ε_l = x_l − f(x_{l+1})          erro; apenas ele sobe na hierarquia
  Δx_{l+1} ∝ precisão_l · ε_l     atualização ponderada por confiança
```

```
Camada 4    → recebe entrada talâmica
Camadas 2/3 → processamento intracortical, saída para frente
Camada 5    → saída subcortical (motora)
Camada 6    → feedback ao tálamo
```

**Gradiente de escalas de tempo:** τ curto em áreas sensoriais (dezenas de ms) → τ longo em áreas associativas (segundos). É o banco de τ log-espaçado como princípio organizador global (`docs/08` §5.3).

### 4.5 Tálamo

Roteamento e gating; laços córtico-talâmicos com atraso de ~10 ms geram ritmos. Modula qual informação alcança o córtex — substrato da atenção.

### 4.6 Tabela de decisão de implementação

| Região | Modelo mínimo | Custo | Prioridade |
|---|---|---|---|
| Cerebelo | reservoir + readout ridge | baixo | **alta** (já implementado) |
| Gânglios | actor-critic com TD | baixo | **alta** |
| Hipocampo | Hopfield / atrator | médio | média |
| Córtex | rede hierárquica com τ graduado | alto | média |
| Tálamo | matriz de gating | baixo | baixa |

---

## 5. Comunicação, timing e reflexos

### 5.1 Latências (todas mensuráveis, todas fixáveis)

```
sinapse química (atraso):     0,5 – 2 ms
sinapse elétrica (gap):       ~0 ms, bidirecional → sincronização
condução amielínica:          0,5 – 2 m/s
condução mielínica:           até 120 m/s (saltatória entre nódulos de Ranvier)
difusão de neuromodulador:    100 ms – minutos (transmissão em volume)
```

### 5.2 Arcos reflexos — calculáveis exatamente

```
REFLEXO PATELAR (monossináptico)
  fuso muscular → aferente Ia → motoneurônio α → contração
  2 sinapses, latência 20–30 ms, SEM participação do cérebro

REFLEXO DE RETIRADA (polissináptico)
  nociceptor → interneurônios → motoneurônios
  latência 50–100 ms

REFLEXO CORTICAL (piscar, evitar)     ~100–150 ms
DECISÃO DELIBERADA                    300–500 ms
```

**Princípio de arquitetura:** o reflexo é local e rápido; o córtex é lento e global. Esta separação por latência é o que garante estabilidade — o mesmo princípio da separação rápido/lento entre núcleo e modulador (`docs/03`).

### 5.3 Decisão — drift-diffusion

```
dx = A·dt + σ·dW           acumula evidência com ruído
decide quando x cruza ±θ

tempo médio de decisão = (θ/A)·tanh(θA/σ²)
probabilidade de erro   = 1/(1 + e^(2θA/σ²))
```

Prediz distribuições de tempo de reação com precisão notável. **É um integrador com ruído** — mesma estrutura recorrente do documento inteiro.

### 5.4 Oscilações e bandas

```
banda    f (Hz)      τ = 1/(2πf)       função
gamma    30–100      1,6 – 5,3 ms      ligação de features, processamento local
beta     13–30       5,3 – 12,2 ms     manutenção de estado motor
alpha     8–13      12,2 – 19,9 ms     gating inibitório, atenção
theta     4–8       19,9 – 39,8 ms     memória, sequências (hipocampo)
delta   0,5–4       39,8 – 318  ms     consolidação, sono
```

Razão média entre bandas vizinhas ≈ **2,3×** — espaçamento logarítmico. Acoplamento fase-amplitude (theta modula gamma) é a mesma estrutura lento-sobre-rápido do modulador.

**Ressalva:** a função computacional das oscilações é debatida; há corrente que as trata como epifenômeno de laços E-I.

---

## 6. Camada neuromoduladora — a segunda camada

### 6.1 Princípio

```
NEURÔNIO:   rápido, ponto-a-ponto, ADITIVO,        transporta DADO
MODULADOR:  lento,  broadcast,     MULTIPLICATIVO, transporta PARÂMETRO
```

Modulação **nunca** é somada ao estado. Ela reconfigura parâmetros: `τ`, ganho, limiar, taxa de aprendizado.

### 6.2 Dinâmica de liberação com reserva finita

```
dR/dt = (R_máx − R)/τ_repor  −  a·S(t)·R        reserva
dm/dt = a·S(t)·R  −  m/τ_limpeza                circulante
```

Propriedades emergentes (não programadas):
- pico rápido, decaimento lento → o efeito dura mais que a causa
- `R` esgota sob estímulo repetido → **não é possível assustar duas vezes em 10 s**
- estresse crônico mantém `R` baixo → **burnout é reserva esgotada, calculável**

### 6.3 Os cinco canais

| Canal | Análogo | Parâmetro controlado | τ_limpeza |
|---|---|---|---|
| `gain` | noradrenalina | ganho β, encurta τ | ~25 passos |
| `plast_thr` | cortisol | limiar de plasticidade, λ de esquecimento | ~400 |
| `lr` | dopamina | taxa η, gating go/no-go | ~8 |
| `sens_rec` | acetilcolina | razão entrada sensorial ÷ recorrência | ~60 |
| `discount` | serotonina | fator de desconto γ | ~300 |

### 6.4 Acoplamento

```
τ_i  ← τ_i / (1 + a₁·m_gain)
β    ← β₀ · (1 + a₂·m_gain)
h    ← f(m_ACh·W_in·x + (1−m_ACh)·W_rec·h)
Δw   ← η(m_DA)·e_ij − λ(m_cort)·w
```

### 6.5 O U invertido (medido, `docs/05` §4)

```
β = 0,25 → desempenho 2,00     (não reage)
β = 1,00 → desempenho 4,28     ← PICO
β = 8,00 → desempenho 0,44     (satura, resolução colapsa)
```

Três mecanismos de degradação sob ganho alto: amplifica sinal **e** ruído igualmente; satura o tanh (derivada `1−tanh²` → 0); τ curto destrói memória de trabalho.

**Ressalva medida:** em `exp07`, a resolução *subiu* monotonicamente na faixa testada — o sigmoide não saturou. A narrativa "muito ganho cega" precisa dessa qualificação.

### 6.6 Ressalvas

Dopamina ≈ RPE é sólido. **As outras quatro atribuições são simplificações de literatura em disputa.** Neuromodulador real não é escalar: D1 e D2 têm efeitos **opostos** no mesmo alvo. O vetor de 5 é caricatura útil, não mecanismo.

---

## 7. Restrições físicas e de escala

### 7.1 Energia

```
potência total do cérebro:     ~20 W
custo por evento sináptico:    ~10⁻¹⁵ J
custo de um MAC digital:       ~10⁻¹³ J        (100–1000× mais)
taxa média de disparo:         ~1 Hz
fração ativa simultaneamente:  1–5 %
```

**A esparsidade não é escolha de design — é orçamento energético.** É o `exp02` executado pela evolução: pressão metabólica com tensão presente produz especialização.

### 7.2 Fiação

```
substância branca escala como ~N^1,23     (mais rápido que os neurônios)
conexões densas:   N²
conexões esparsas: ~N·log N

N = 10³  →  razão 10×
N = 10⁶  →  razão 5017×
```

**Regra:** aumentar N exige aumentar esparsidade ou modularidade, senão o custo de conexão domina.

### 7.3 Alometria (`docs/08` §1)

```
N_parte = a · N_total^b

córtex   b ≈ 1,35   (hiperalométrico)
cerebelo b ≈ 1,00
resto    b ≈ 0,70   (hipoalométrico)
```

Dobrar N_total multiplica o córtex por 2,55 e o resto por 1,62.

---

## 8. Arquitetura recomendada para implementação

```
┌─────────────────────────────────────────────────────────────┐
│ NÍVEL 0 — CONSTANTES (calculadas uma vez, §1)               │
│   E_Na=+60,6  E_K=−95,0  E_Cl=−64,1  V_rest=−69,1 mV        │
├─────────────────────────────────────────────────────────────┤
│ NÍVEL 1 — NEURÔNIOS (Izhikevich, §2.3)                      │
│   2 EDOs, 13 FLOPs/ms, tipos RS/FS/IB/CH                    │
│   diversidade de τ log-espaçada                             │
├─────────────────────────────────────────────────────────────┤
│ NÍVEL 2 — SINAPSES (§3)                                     │
│   AMPA (τ=3ms) + NMDA (τ=100ms, gate de Mg²⁺) + GABA_A      │
│   esparsidade ~2–10 % · E/I ~80/20                          │
├─────────────────────────────────────────────────────────────┤
│ NÍVEL 3 — PLASTICIDADE (§3.5–3.6)                           │
│   STDP por traços + terceiro fator modulador                │
├─────────────────────────────────────────────────────────────┤
│ NÍVEL 4 — REGIÕES (§4)                                      │
│   cerebelo(reservoir) · gânglios(actor-critic) ·            │
│   hipocampo(atrator) · córtex(hierarquia de τ)              │
├─────────────────────────────────────────────────────────────┤
│ NÍVEL 5 — NEUROMODULAÇÃO (§6)                               │
│   5 canais, reserva finita, acoplamento multiplicativo      │
├─────────────────────────────────────────────────────────────┤
│ NÍVEL 6 — CORPO E AMBIENTE (docs/07)                        │
│   interocepção → drive → recompensa homeostática            │
│   r = β·(D_t − D_{t+1})                                     │
├─────────────────────────────────────────────────────────────┤
│ NÍVEL 7 — EVOLUÇÃO (docs/06, docs/08)                       │
│   genoma: cronograma + modulador + topologia                │
│   alometria emerge do cronograma                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Notas numéricas (evita meses perdidos)

| Problema | Solução |
|---|---|
| HH é sistema **rígido** | passo ≤ 10 µs com Euler; ou RK4; ou integração exponencial |
| Vazamento grande e variável | **Euler implícito**: `h = (h + dt·S·A)/(1 + dt·leak)` — incondicionalmente estável |
| τ deve ser positivo sob gradiente/mutação | parametrizar em **log** |
| Sinapses dominam o custo | representação esparsa (CSR) + fila de eventos, não matriz densa |
| Precisão | `float32` suficiente para V; **`float64` se houver τ > 10³ passos** |
| Escala | população/neurônios como dimensão de **batch**; `einsum` em (P,N,N) |
| Passos sequenciais não paralelizam | aumentar P (população) antes de T (tempo) |

**Escolha de passo:** Δt = 0,1 ms para Izhikevich com sinapses AMPA; Δt = 1 ms se apenas modelos de taxa.

---

## 10. Roteiro de construção (ordem obrigatória)

| Fase | Entrega | Validação | Custo |
|---|---|---|---|
| **1** | Izhikevich isolado, 5 tipos | reproduzir os padrões de disparo publicados | horas |
| **2** | 1000 neurônios, E/I 80/20, AMPA+GABA | medir `σ` de ramificação → deve ficar ~1 | horas |
| **3** | + NMDA e STDP | verificar emergência de assembleias | dias |
| **4** | + reservoir cerebelar com readout ridge | tarefa de timing motor | dias |
| **5** | + gânglios (actor-critic) | tarefa de escolha com recompensa | dias |
| **6** | + neuromodulação (5 canais) | reproduzir o U invertido (`docs/05` §4) | dias |
| **7** | + corpo mínimo (`docs/07`) | sobrevivência homeostática | semanas |
| **8** | + evolução (`docs/06`) | divergência de perfil modulador | semanas |

**Regra:** cada fase precisa de um teste que pode **falhar**. Sem critério de falha, não é validação.

---

## 11. Onde a ciência acaba — limites honestos

1. **A regra de aprendizado do córtex é desconhecida.** Backprop não é biologicamente plausível. Candidatos (codificação preditiva, feedback alignment, erro dendrítico) seguem em disputa aberta.

2. **Conectoma não dá função.** O conectoma completo do *C. elegans* (302 neurônios, todas as sinapses) foi publicado em **1986**. O projeto OpenWorm, quarenta anos depois, ainda não reproduz o comportamento do animal. Faltam pesos, constantes cinéticas, moduladores e corpo.

3. **Glia é ignorada** e participa da computação — astrócitos modulam sinapses ativamente.

4. **Escala:** 86×10⁹ neurônios em Izhikevich a Δt=1 ms exigiriam ~10¹⁵ FLOP/s só na dinâmica, mais ~10¹⁴ sinapses a atualizar. Fora de alcance atual.

5. **Precedente institucional:** o Human Brain Project europeu recebeu ~1 bilhão de euros com meta de simulação cerebral completa e foi reorientado após carta aberta de centenas de neurocientistas apontando que o objetivo era prematuro. Isso não invalida a direção — indica que "recriar o cérebro" é um **campo**, não um projeto.

6. **Todas as constantes deste documento** foram compiladas de conhecimento de literatura e não verificadas contra as publicações primárias nesta sessão. Confirmar em Hodgkin & Huxley (1952), Izhikevich (2003, 2004), Jahr & Stevens (1990), Marr (1969)/Albus (1971), Schultz et al. (1997) antes de uso formal.

---

## 12. O que este documento defende

**Não** reproduzir cognição humana. **Sim** construir um substrato com a estrutura correta:

```
✅ múltiplas escalas de tempo (banco de τ log-espaçado)
✅ neuromodulação multiplicativa (segunda camada)
✅ esparsidade forçada por custo energético
✅ inibição ~20–30 % (mantém σ ≈ 1)
✅ aprendizado local com três fatores (sem backprop global)
✅ corpo e interocepção gerando a recompensa
✅ evolução operando sobre cronograma e modulador
```

Sobre esse substrato, evolução e ambiente fazem o resto. **A aposta central do projeto é que a estrutura importa mais que a escala** — e isso é falsificável: se um substrato de 10³–10⁶ unidades com essas propriedades não superar uma rede convencional de tamanho igual nas tarefas de `docs/06` e `docs/07`, a aposta está errada.
