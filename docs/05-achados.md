# Achados Consolidados — incluindo os NEGATIVOS

Todos os números abaixo foram medidos, não estimados. Scripts em `experiments/`.

## 1. Neurônio líquido ≡ média móvel exponencial  ✅ SÓLIDO

```
h[n] = α·h[n−1] + (1−α)·x[n],    α = e^(−dt/τ),    τ = −dt/ln α
```

Consequências verificadas analiticamente:
- banco de τ = banco de filtros passa-baixas, `f_corte = 1/(2πτ)`
- diferença de dois τ ≈ derivada → **é o MACD**
- PID = reservoir de 3 neurônios (P: τ→0, I: τ→∞, D: dois τ)

## 2. Por que o LTC funciona  ✅ SÓLIDO (verificado em código)

Três garantias, não uma não-linearidade mágica:

| Propriedade | Verificação |
|---|---|
| conjunto invariante `[0, A]` | `test_celulas_estaveis`: entrada ×100, max\|h\| = 0.987 |
| `τ_ef ∈ (τ/(1+τ), τ)` | analítico |
| Jacobiano ∈ (0,1) | Euler implícito, analítico |

## 3. Readout ótimo = vértice de parábola  ✅ SÓLIDO

```
1D:  L(w) = (Σh²)w² − 2(Σhy)w + Σy²   →   w* = −b/2a = Σhy/Σh²
K-D: W = (FᵀF + λI)⁻¹Fᵀy
```
λ soma ao coeficiente `a`, **fechando a curvatura da parábola**.
Verificado: `test_ridge_recupera_vertice` → w* = 2.5000 exato.

## 4. U INVERTIDO do ganho (Yerkes-Dodson)  ✅ CONFIRMADO — exp06

Rede de 6 neurônios, quimiotaxia com 1 sensor:

```
SEM ruído sensorial                    COM ruído sensorial
  β= 0.25  comida 2.00                   β= 0.25  comida 0.39
  β= 0.50  comida 3.78                   β= 0.50  comida 2.28
  β= 1.00  comida 4.28  <== PICO         β= 1.00  comida 5.00  <== PICO
  β= 2.00  comida 3.94                   β= 2.00  comida 4.56
  β= 4.00  comida 0.61                   β= 4.00  comida 0.89
  β= 8.00  comida 0.44                   β= 8.00  comida 0.17
  β=16.00  comida 1.00                   β=16.00  comida 0.28
```

| Predição | Resultado |
|---|---|
| P1 — pico interior | ✅ **confirmada**, pico em β=1.0 nos dois casos; β=8 custa ~90% do desempenho |
| P2 — ruído desloca pico p/ β menor | ❌ **refutada** — pico ficou em β=1.0 nos dois; o ruído tornou a queda em β baixo MAIS acentuada (0.39 vs 2.00) |
| P3 — adaptativo ≥ melhor fixo | 🟡 **parcial** — sem ruído +2.6%; com ruído **−26.7%** |

**Interpretação de P3:** o gatilho usado foi `surpresa = |c − c_ant|`. Com ruído
sensorial, o próprio ruído vira "surpresa" → o modulador amplifica exatamente
quando não deveria. **O gatilho precisa ser filtrado antes de modular.**
Correção a testar: `surpresa = |c_filtrado − c_predito|` com predição de um
τ intermediário, em vez de diferença bruta.

Este é o achado mais acionável do documento: **modulação adaptativa com gatilho
mal-condicionado é pior que parâmetro fixo.**

## 5. Pressão exige tensão  ✅ CONFIRMADO — exp00 vs exp02

Tarefa SEM exigência de memória → qualquer pressão colapsa tudo:
```
sem pressão   ganho 24.05%  spread 393x
pressão baixa ganho 23.93%  spread 1.0x   ← COLAPSO (todos τ → 1.2)
```

Tarefa COM exigência de memória → pressão ESPECIALIZA:
```
sem pressão      R² 26.99%  τ = [4, 6, 12, 18, 32, 35, 62, 109]
pressão alta     R² 23.54%  τ = [1.2, 1.2, 1.3, 1.5, 9.7, 19.4, 28.2, 52.8]
pressão extrema  R² 20.66%  τ = [1.2, 1.2, 1.2, 1.3, 1.3, 21.2, 36.2, 54.9]
                              └── sacrificados ──┘ └── PRESERVADOS ──┘
```

> **Pressão sem tensão produz colapso, não organização.**

Achado secundário: sem pressão, a evolução **superou o banco log-espaçado
projetado à mão** (26.99% vs 23.74%).

## 6. Poucos neurônios bastam  ✅ CONFIRMADO — exp05

Quimiotaxia com 1 sensor, motor lendo apenas neurônios:

```
 N   comida/ep   Δ vs N−1    τ do melhor
 1      2.75        —        [9.6]                        ← só passa-baixas, não navega
 2      5.17     +87.9%      [1.5, 23.4]                  ← SALTO: spread 16x = derivada
 3      4.08     −21.0%      [8.0, 10.9, 57.9]
 4      6.00     +46.9%      [1.6, 6.6, 12.9, 13.3]
 6      6.67     +11.1%      [1.1, 5, 8.6, 9, 9.6, 26.9]  ← PICO
10      5.50     −17.5%      (τ colapsam em 1-5)
16      5.25      −4.5%      (τ colapsam em 1-5)
```

- N=2 reinventou o par SA/RA (rápido + lento) **sem instrução**
- **Mais neurônios pioraram** — capacidade sem pressão que a organize é passivo

**Lesão (N=6):** nenhum neurônio redundante.
```
sem neurônio 0 (τ=9.6):  perda 100.0%
sem neurônio 1 (τ=5.0):  perda  95.0%
sem neurônio 5 (τ=1.1):  perda  73.8%
sem neurônio 4 (τ=8.6):  perda  41.2%   ← o menos crítico
```

## 7. Memória só compensa em ambiente parcialmente observável  ✅ + teorema

**exp03** (ambiente estacionário, estado observável): pressão crônica PIOROU
(184.5 vs 200.8 ablado, −8.1%).

> **Teorema (MDP totalmente observável):** com estado plenamente observável e
> dinâmica estacionária, a política ótima é função apenas do estado atual.
> Memória é provadamente inútil.

**exp04** (estações ocultas): `w₂ > 0` em 4/5 seeds (média +2.76), mas
`τ_P` mediana 2.1 contra predição de 75 → **refutada**.

Diagnóstico: o agente observava a própria energia (variável de AÇÃO, não sensor),
que responde em poucos passos → informação já disponível na escala rápida.

## 8. HLC (célula proposta)  ❌ NÃO CONFIRMADA — exp01

```
regime-switching:  leaky 24.5%  |  LTC 22.8%  |  HLC 22.6%
estacionário:      leaky 19.3%  |  LTC −18.5% |  HLC −9.6%
```

**Limitação decisiva:** protocolo de reservoir congelado penaliza sistematicamente
células cujo valor está no TREINAMENTO. `β`, `κ`, `τ_v` nunca foram otimizados.
**O teste justo (BPTT) é o objetivo de `src/cells.py::HLCCell`.**

## 9. Padrão recorrente: o U invertido aparece 4 vezes

| Onde | Pouco | Muito |
|---|---|---|
| λ da regressão ridge | pesos explodem | pesos morrem |
| inibição na rede | epilepsia | silêncio |
| pressão metabólica | sem estrutura | colapso |
| ganho β (exp06) | não reage | satura, resolução colapsa |

**O regime útil é sempre a borda.** Nome técnico: criticalidade.

## 10. Condições de validade da hipótese pressão/tensão (estado atual)

Após três refutações, a hipótese sobrevivente é específica e falsificável:

> A pressão crônica só compensa seu custo quando TODAS valem:
> 1. ambiente **parcialmente observável**
> 2. variável oculta com **escala de tempo longa**
> 3. **cada observação individualmente fraca** (razão de verossimilhança ≈ 1)
> 4. a observação **não é variável de ação** do próprio agente

Condição 3 ainda não testada — é o próximo experimento.
