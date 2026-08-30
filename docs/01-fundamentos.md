# Neurônios Líquidos — Derivações, Célula HLC e Resultados Experimentais

**Data:** 28/07/2026
**Escopo:** fundamentação matemática de neurônios líquidos (LTC/CfC), proposta de célula nova (HLC), protocolo de avaliação e resultados obtidos.
**Status dos achados:** hipótese HLC **não confirmada** sob o protocolo testado — ver §7 e §8.

---

## 1. Fundamento: o neurônio como balde furado

O neurônio de integração-com-vazamento (*leaky integrator*) é a EDO:

```
dh/dt = -h/τ + u(t)
```

- `h` — estado (nível de ativação)
- `τ` — constante de tempo (tamanho do "furo"; horizonte de memória)
- `u(t)` — entrada (corrente injetada)

### 1.1 Solução exata (entrada constante)

Para `u` constante e `h(0) = 0`:

```
h(t) = uτ · (1 − e^(−t/τ))
```

**Equilíbrio:** `h* = uτ` quando `t → ∞`. A aproximação é exponencial — nunca "chega e para", desacelera assintoticamente porque o vazamento cresce junto com o nível. Mesma equação do resfriamento de Newton e da carga de capacitor RC.

### 1.2 Condição de disparo

Para um neurônio com limiar `θ`:

- `h* = uτ > θ` → dispara (transborda)
- `h* = uτ < θ` → integra em silêncio, estabiliza abaixo do limiar

Em modo *spiking* (LIF), o disparo reseta `h = 0` e propaga corrente aos vizinhos. Em modo contínuo (LTC/CfC), não há reset: a saída é o próprio estado saturado por uma não-linearidade — é a versão diferenciável, treinável por gradiente.

---

## 2. Teorema central: neurônio líquido ≡ média móvel exponencial

Discretizando exatamente (entrada constante dentro do passo `dt`), com `α = e^(−dt/τ)`:

```
h[n] = α·h[n−1] + (1−α)·x[n]
```

**Isso é literalmente uma EMA.** Conversões úteis:

```
τ = −dt / ln(α)
τ ≈ (P+1)/2        para uma EMA de período P
```

Expandindo a recursão:

```
h[n] = (1−α) · Σ(k≥0) α^k · x[n−k]
```

Soma ponderada de todo o passado com decaimento geométrico. **O horizonte efetivo de memória é τ**; a contribuição de um evento ocorrido há `t` unidades vale `e^(−t/τ)`.

**Implicação prática:** qualquer código do tipo `estado = lerp(estado, alvo, k)` já é um neurônio líquido. Suavização de câmera, envelope follower de áudio, sistemas de aggro/heat, *leaky bucket* de rate limiting — todos são a mesma equação.

---

## 3. Resposta em frequência: cada τ é um filtro

Substituindo `x(t) = e^(jωt)`:

```
H(ω) = 1 / (1 + jωτ)
|H(ω)| = 1 / √(1 + (ωτ)²)
f_corte = 1 / (2πτ)
```

**Cada neurônio é um passa-baixas.** Um banco de neurônios com τ log-espaçados decompõe o sinal em escalas de tempo — análogo temporal de uma transformada wavelet. É essa diversidade de τ que dá capacidade expressiva à camada.

### 3.1 Corolário: dois τ formam um derivador (= MACD)

Expansão de Taylor para sinal suave: `h(t) ≈ x(t) − τ·ẋ(t)`. Logo:

```
h_rápido − h_lento ≈ (τ_lento − τ_rápido) · ẋ(t)
```

**A diferença de duas EMAs é uma estimativa da derivada.** O indicador MACD é exatamente isso; o cruzamento por zero corresponde à inversão do sinal da derivada. Três neurônios em cascata aproximam a segunda derivada.

**Consequência arquitetural:** um controlador PID é um reservoir de 3 neurônios:

| Termo PID | Equivalente |
|---|---|
| P (proporcional) | neurônio com `τ → 0` (só o instante atual) |
| I (integral) | neurônio com `τ → ∞` (acumulador sem vazamento) |
| D (derivativo) | diferença de dois τ |

Tunar Kp/Ki/Kd manualmente é fazer à mão o que a regressão fechada (§5) resolve analiticamente.

---

## 4. Rede de N neurônios: formulação vetorial

Não se itera N baldes; empilha-se o estado num vetor e resolve-se de uma vez:

```
dh/dt = −h/τ + W·σ(h) + W_in·x
```

- `h ∈ R^N` — estado
- `τ ∈ R^N` — constante de tempo individual por neurônio
- `W ∈ R^(N×N)` — matriz de conexões recorrentes (**é o grafo**: `W[i][j] ≠ 0` = aresta de j para i)
- `W_in ∈ R^(N×d)` — projeção da entrada
- `σ` — saturação (tanh/sigmoid)

Implementação de referência (100 neurônios):

```python
import numpy as np
N = 100
h    = np.zeros(N)
tau  = np.random.uniform(2, 20, N)
W    = np.random.randn(N, N) * 0.1
W    = W * (np.random.rand(N, N) < 0.08)     # esparsifica: 8% de densidade
W_in = np.random.randn(N, 4) * 0.5

def step(h, x, dt=0.1):
    dh = -h/tau + W @ np.tanh(h) + W_in @ x
    return h + dt*dh
```

### 4.1 Onde a informação reside (três escalas de tempo)

| Substrato | Natureza | Papel |
|---|---|---|
| `h` (estado) | volátil, muda a cada passo | contexto recente — **RAM** |
| `W`, `τ` (parâmetros) | aprendidos no treino | conhecimento permanente — **disco** |
| topologia (padrão de esparsidade) | fixada por design | estrutura do problema — **arquitetura** |

**Correção de intuição comum:** o nível `h` **não** armazena conhecimento; armazena contexto. O que foi aprendido está nos pesos e nos τ.

Mapeamento de intuições geométricas para parâmetros reais:

| Intuição | Parâmetro real | Efeito |
|---|---|---|
| "profundidade" | `τ` | horizonte temporal de memória |
| "largura/abrangência" | fan-in (nº de conexões chegando) | quantidade de evidência integrada |
| "o que ele sabe" | linha de `W` | pesos aprendidos |
| "quando reage" | limiar + bias | ceticismo do neurônio |

### 4.2 Topologia como conhecimento (NCP)

*Neural Circuit Policies* (grupo do MIT) copiaram a fiação do *C. elegans*: sensorial → interneurônios → comando (recorrente, onde a memória reside) → motor. **19 neurônios** dirigiram um carro autônomo — tarefa que arquiteturas densas exigem ordens de magnitude a mais. A topologia carrega parte da indução que senão teria de ser aprendida.

### 4.3 Regimes dinâmicos observados (simulação de 100 neurônios)

- **Silencioso** — entrada insuficiente para vencer o vazamento
- **Crítico** — atividade rica e propagante, sem explosão (regime útil)
- **Epiléptico** — saturação global e sincronizada

O parâmetro de controle mais determinante foi a **fração de conexões inibitórias**: com 0% de inibição a rede colapsa em epilepsia sob ganho moderado; ~20–30% mantém o regime crítico. Sem inibição não há computação, apenas ruído sincronizado.

---

## 5. Leitura (readout) em forma fechada — sem backprop

Arquitetura *reservoir computing*: dinâmica interna fixa, treina-se apenas a camada linear de saída.

```
ŷ[n] = W_out · f[n]        onde f = [h₁, …, h_K, 1]
```

Minimizando erro quadrático — **caso 1D revela a estrutura**:

```
L(w) = Σ(yᵢ − w·hᵢ)² = (Σhᵢ²)w² − 2(Σhᵢyᵢ)w + Σyᵢ²
                        └─ a ─┘    └──── b ────┘   └ c ┘
```

É uma **parábola em w**. O peso ótimo é o vértice:

```
w* = −b/(2a) = Σhᵢyᵢ / Σhᵢ²
```

Generalizando para K pesos (regressão ridge):

```
W = (FᵀF + λI)⁻¹ Fᵀ y
```

- `F` — matriz de estados (uma linha por instante)
- `λ` — regularização; geometricamente **soma λ ao coeficiente `a`**, fechando a curvatura da parábola e impedindo pesos explosivos
- Custo: `O(K³)` — trivial para K ~ 12–100

**Nota metodológica:** treinar apenas o readout isola o efeito da *dinâmica*, o que torna esse protocolo adequado para comparar células diferentes — mas ver §8, limitação (1).

---

## 6. Derivação do LTC (como Hasani chegou lá)

O insight não veio de ML, veio de modelagem biofísica. Em RNNs convencionais a entrada é **corrente injetada**. Numa sinapse real é uma **condutância** — a corrente depende do estado atual (força motriz):

```
I_sin = S(x,h)·(A − h)
```

Substituindo na EDO do balde:

```
dh/dt = −h/τ + S(x,h)·(A − h)
      = −[1/τ + S(x,h)]·h + S(x,h)·A
         └──── 1/τ_efetivo ────┘
```

com `S(x,h) = σ(W·x + U·h + b)`.

**Constante de tempo efetiva:**

```
τ_ef = τ / (1 + τ·S(x,h))
```

O τ passa a **depender da entrada** — daí "líquido". Sinal forte → τ menor → reage rápido; sinal fraco → τ maior → memória longa.

**CfC (Closed-form Continuous-time):** aproximação em forma fechada da solução dessa EDO, eliminando o solver numérico:

```
h(t) = σ(−f(x,h)·t) ⊙ g(x,h) + [1 − σ(−f(x,h)·t)] ⊙ k(x,h)
```

Interpolação aprendida entre dois modos, com o gate dependente do tempo. Ganho principal: velocidade (sem integração numérica) mantendo o comportamento de tempo contínuo.

---

## 7. HLC — Homeostatic Liquid Cell (proposta desta sessão)

### 7.1 Hipóteses de domínio

Estrutura de séries financeiras **não** codificada pelo LTC padrão:

1. **Clusterização de volatilidade** — regimes calmos e agitados se agrupam temporalmente
2. **Não-estacionariedade de escala** — amplitude varia por ordens de magnitude
3. **Horizonte de memória dependente de regime** — em regime calmo a tendência persiste; em regime volátil o passado perde valor preditivo rapidamente

### 7.2 Formulação

Dois estados por neurônio: atividade `h` e energia recente `v` ("metabolismo").

```
dv/dt = (h² − v) / τ_v                              (1) estimativa de variância local
dh/dt = −(1/τ_h + β·√v)·h + g(v)·S(x,h)·(A − h)     (2) dinâmica com vazamento vol-dependente
g(v)  = (σ_alvo / √(v + ε))^κ                       (3) ganho homeostático
S(x,h) = σ(w·g(v)·x + u·h + b)                      (4) ativação com entrada normalizada
```

**Parâmetros:**

| Símbolo | Papel | Valor testado |
|---|---|---|
| `τ_h` | constante de tempo base | log-espaçados, 2·1.6^k, k=0..11 |
| `τ_v` | janela do estimador de variância | 60 |
| `β` | acoplamento volatilidade → vazamento | 2.5 |
| `κ` | intensidade da homeostase | 0.7 |
| `σ_alvo` | escala de saída desejada | 0.5 |
| `A` | potencial de reversão | 1.0 |
| `ε` | estabilizador numérico | 1e-6 |

**Mecanismos:**

- **Termo `β·√v` (eq. 2):** volatilidade alta → vazamento maior → `τ_ef` menor → memória mais curta. Codifica a hipótese 3 explicitamente.
- **Ganho `g(v)` (eq. 3):** o neurônio regula o próprio ganho para manter a saída em faixa útil independentemente da escala da entrada. Codifica a hipótese 2. Base biológica: plasticidade intrínseca / *synaptic scaling* — mecanismo real e sub-explorado em RNNs.

**τ efetivo completo:**

```
1/τ_ef = 1/τ_h + β·√v + g(v)·S(x,h)
         └base┘  └volatilidade┘ └entrada (LTC)┘
```

O LTC é o caso particular `β = 0, κ = 0, g ≡ 1`.

### 7.3 Discretização (Euler implícito — estável)

```python
v = v + dt*(h*h - v)/tau_v
sd = np.sqrt(v + eps)
g  = (sig_alvo/sd)**kappa
S  = 1/(1 + np.exp(-(w*g*x + 0.3*h)))
leak = 1/tau + beta*sd + g*S
h = (h + dt*g*S*A) / (1 + dt*leak)      # implícito: incondicionalmente estável
```

O Euler implícito foi escolhido porque o `leak` é grande e variável — Euler explícito diverge para `dt·leak > 2`.

---

## 8. Protocolo experimental e resultados

### 8.1 Desenho

- **Sinais:**
  - *regime-switching*: AR(1) com troca de `(φ, σ)` entre `(0.985, 0.05)` e `(0.70, 0.55)`, probabilidade de troca 0.004/passo
  - *estacionário* (controle): soma de senoides + ruído gaussiano
- **Células comparadas:** leaky (τ fixo) · LTC (τ ~ entrada) · HLC (homeostático)
- **K = 12** neurônios, τ log-espaçados idênticos entre células
- **Readout:** ridge em forma fechada, `λ = 1e-2`
- **Tarefa:** prever `x[t+10]`; treino nos primeiros 60%, teste nos 40% finais
- **Métrica:** ganho de RMSE sobre baseline de persistência (`ŷ = x[t]`)
- **8 seeds**, 6000 amostras cada

### 8.2 Resultados

```
REGIME-SWITCHING (não-estacionário)
  leaky (τ fixo)        ganho  24.54% ± 2.24
  LTC (τ ~ entrada)     ganho  22.81% ± 2.77
  HLC (homeostático)    ganho  22.57% ± 2.89

ESTACIONÁRIO (controle)
  leaky (τ fixo)        ganho  19.32% ± 0.12
  LTC (τ ~ entrada)     ganho −18.50% ± 0.55
  HLC (homeostático)    ganho  −9.64% ± 0.35
```

### 8.3 Conclusões

**A hipótese HLC não foi confirmada.** No sinal alvo (regime-switching), HLC empatou com LTC dentro do desvio-padrão e ambos ficaram **abaixo** do reservoir linear simples. No controle estacionário, ambas as células não-lineares tiveram desempenho pior que o baseline de persistência.

**Diagnóstico — limitações do protocolo (ordenadas por gravidade):**

1. **Parâmetros da dinâmica não foram treinados.** LTC e CfC obtêm seu desempenho de `W`, `U`, `b`, `τ` *aprendidos* por BPTT. Congelados em valores aleatórios/arbitrários, a não-linearidade só distorce o sinal. O protocolo de reservoir isola a dinâmica, mas **penaliza sistematicamente células cujo valor está no treinamento**. `β`, `κ` e `τ_v` nunca foram otimizados.
2. **Vantagem estrutural do baseline.** Com readout linear sobre features lineares, o reservoir leaky é ótimo por construção para alvos aproximadamente lineares. O sinal AR(1) sintético é quase o caso ideal para ele.
3. **Sinal sintético.** O gerador de regimes é uma caricatura; volatilidade real tem memória longa (efeito GARCH), assimetria (efeito alavancagem) e saltos.
4. **Ausência de varredura de hiperparâmetros.** Um único ponto de `(β, κ, τ_v)` foi testado — não há evidência de que seja próximo do ótimo.

**O que o resultado permite afirmar:** sob avaliação em reservoir congelado, a homeostase e o gating por volatilidade não conferem vantagem. **Não permite afirmar** que a hipótese seja falsa sob treinamento completo.

---

## 9. Próximos passos (ordenados por custo/benefício)

1. **Varredura de `β`, `κ`, `τ_v`** no protocolo atual (custo: minutos). Se nenhuma combinação superar o baseline leaky no regime-switching, a hipótese perde força substancialmente.
2. **Porte para PyTorch com BPTT**, tornando `β`, `κ`, `τ_v`, `W`, `U`, `b` treináveis. Comparação justa com contagem de parâmetros igualada, múltiplas seeds, e LTC/CfC oficiais como baseline.
3. **Dados reais** — substituir o gerador sintético por séries de preço reais; avaliar em janelas com mudança de regime documentada.
4. **Ablação componente a componente** — testar `β > 0, κ = 0` e `β = 0, κ > 0` separadamente para atribuir efeito a cada mecanismo.
5. **Benchmarks padronizados** (sequências longas, tarefas de memória) para verificar se o ganho, se existir, é específico de domínio ou geral.

---

## 10. Aplicações validadas de neurônios líquidos (fora de previsão financeira)

| Domínio | Uso | Observação |
|---|---|---|
| Controle (drone, robótica) | PID generalizado; NCP com poucos neurônios | τ = latência do atuador |
| Detecção de anomalia | resíduo `\|h_rápido − h_lento\|` acima de limiar | detecta mudança de regime |
| IA de jogo | aggro/heat/stamina com esquecimento gradual | τ vira parâmetro de personalidade |
| Áudio | envelope follower, compressor, gate | attack/release = dois τ |
| Infraestrutura | *leaky bucket* rate limiting | mesmo algoritmo, mesmo nome |
| Segurança (defensivo) | análise de canais laterais (tempo/energia) | motivo pelo qual se exige código *constant-time* |

**Contraindicação documentada:** aritmética modular / criptografia. Neurônios líquidos são passa-baixas e exploram autocorrelação temporal; saídas criptográficas são projetadas com autocorrelação nula. Medição de correlação fitness-distância no espaço de fatoração retornou `r ≈ +0.04` numa janela estreita em torno do fator — ausência de gradiente explorável.

---

## 11. Código de referência

Arquivo: `hlc.py` — implementação das três células, geradores de sinal, readout ridge em forma fechada e arnês de avaliação multi-seed. Executável com numpy apenas.

Estrutura:

- `sinal_regimes(T, seed)` / `sinal_estacionario(T, seed)` — geradores
- `res_leaky(x, taus)` — baseline linear
- `res_ltc(x, taus, A, w)` — LTC com Euler implícito
- `res_hlc(x, taus, A, w, beta, kappa, tau_v, sig_alvo)` — célula proposta
- `avaliar(H, x, horizonte, lam, frac_treino)` — ridge + RMSE vs baseline de persistência

---

## Referências mencionadas

- Hasani et al., *Liquid Time-constant Networks* (LTC), 2020
- Hasani et al., *Closed-form Continuous-time Neural Networks* (CfC), 2022
- Lechner et al., *Neural Circuit Policies* (NCP), 2020
- Rusch & Mishra, *Coupled Oscillatory RNN* (coRNN) — alternativa de segunda ordem, relevante para domínios com inércia física
- Power et al., *Grokking*, 2022 — aprendizado de aritmética modular por transformers em módulos pequenos

*As referências foram citadas de memória durante a sessão e não foram verificadas contra as publicações originais. Confirmar autoria, ano e resultados antes de citar em trabalho formal.*
