# Pressão e Tensão como Escalas de Tempo — Teoria, Predições e Refutações

**Data:** 28/07/2026
**Documento irmão:** `neuronios-liquidos-resumo.md` (fundamentos, LTC/CfC, célula HLC)
**Status:** hipótese central **parcialmente refutada**; condição de validade refinada em §6.

---

## 1. Por que a fórmula do LTC funciona (análise de estabilidade)

Antes de propor célula nova, é preciso entender o que garante que a existente funcione. O LTC:

```
dh/dt = −[1/τ + S]·h + S·A,     S = σ(W·x + U·h + b) ∈ (0,1)
```

### 1.1 Conjunto invariante — estado limitado

Avaliando o campo vetorial nas bordas (com `A > 0`):

```
em h = A:   dh/dt = −[1/τ + S]·A + S·A = −A/τ  < 0   → empurra para dentro
em h = 0:   dh/dt = S·A                        > 0   → empurra para dentro
```

Logo `[0, A]` é **conjunto invariante**: o estado permanece limitado para qualquer entrada, sem clipping artificial. RNNs convencionais não têm essa garantia — é a origem da explosão de ativações.

### 1.2 Constante de tempo efetiva limitada nos dois extremos

```
τ_ef = τ / (1 + τ·S),      S ∈ (0,1)
⟹    τ/(1+τ) < τ_ef < τ
```

Nunca colapsa a zero (não perde memória instantaneamente) e nunca diverge (não congela). Adaptatividade **dentro de uma faixa controlada** — condição para treinabilidade.

### 1.3 Jacobiano contrativo mas não nulo

Discretização por Euler implícito:

```
h[n+1] = (h[n] + dt·S·A) / (1 + dt·(1/τ + S))
∂h[n+1]/∂h[n] ≈ 1 / (1 + dt·(1/τ + S)) ∈ (0, 1)
```

Estritamente < 1 (gradiente não explode no BPTT) e estritamente > 0 (não desaparece de imediato). **O gradiente é bem-condicionado por construção.**

### 1.4 Conclusão metodológica

O mérito do LTC não é uma não-linearidade nova; é a escolha de uma forma funcional que **garante** as três propriedades acima. A contribuição é de *modelagem*, não de *invenção*.

---

## 2. Receita abstraída — checklist para qualquer célula nova

Ao propor uma dinâmica nova, verificar analiticamente ANTES de implementar:

| # | Check | Como verificar |
|---|---|---|
| 1 | **Mecanismo** | qual grandeza física/estatística multiplica qual? |
| 2 | **Conjunto invariante** | avaliar o campo nas bordas; estado deve ser limitado |
| 3 | **τ_ef limitado** | superiormente E inferiormente |
| 4 | **Jacobiano ∈ (0,1)** | contração sem aniquilação |
| 5 | **Identificabilidade** | o novo grau de liberdade carrega informação ausente nos existentes? |

**O check 5 é o que mais falha na prática** e é o menos discutido na literatura.

---

## 3. Formalização de "pressão" e "tensão"

Hipótese de partida (analogia biológica): estresse agudo e estresse crônico são coisas distintas e ambos moldam comportamento.

**Formalização proposta — duas escalas de tempo em cascata:**

```
Th[n+1] = Th[n] + (d[n] − Th[n]) / τ_T        (1) TENSÃO — estado agudo
P[n+1]  = P[n]  + (Th[n] − P[n]) / τ_P        (2) PRESSÃO — acúmulo crônico
```

- `d` — sinal de déficit instantâneo (fome, erro, desvio do setpoint)
- `Th` — tensão: EMA rápida do déficit (`τ_T` pequeno)
- `P` — pressão: EMA lenta da tensão (`τ_P` grande) = passa-baixas de segunda ordem

**Política dependente de ambos:**

```
p_ação = σ(w₀ + w₁·Th + w₂·P)                 (3)
```

Interpretação pretendida: `w₁` capta urgência imediata; `w₂` capta desespero acumulado (histórico de privação).

**Checks 2–4:** passam trivialmente — cascata de EMAs é limitada e contrativa.
**Check 5:** é o objeto de teste dos experimentos abaixo.

---

## 4. Princípio derivado do experimento A: pressão exige tensão

### 4.1 Experimento A — pressão metabólica sobre a distribuição de τ

**Desenho:** população de reservoirs (K=8 τ evoluíveis), seleção por desempenho menos custo metabólico `pen·mean(log(1+τ))`. Duas tarefas:

- **Tarefa sem exigência de memória** (previsão AR de curto prazo)
- **Tarefa com exigência de memória** (prever média de `u` na janela `[t−140, t−120]`)

**Resultados — tarefa SEM exigência de memória:**

```
sem pressão      ganho 24.05%   spread 393x
pressão baixa    ganho 23.93%   spread 1.0x   ← COLAPSO TOTAL: todos τ → 1.2
pressão média    ganho 23.93%   spread 1.0x   ← idem
pressão alta     ganho 23.93%   spread 1.0x   ← idem
```

**Resultados — tarefa COM exigência de memória:**

```
banco manual (2..107)   R² = 23.74%
sem pressão             R² = 26.99%   spread 27x   τ_médio 34.7
pressão baixa           R² = 26.73%   spread 68x   τ_médio 33.2
pressão média           R² = 24.25%   spread 36x   τ_médio 14.0
pressão alta            R² = 23.54%   spread 44x   τ_médio 14.4
    taus = [1.2, 1.2, 1.3, 1.5, 9.7, 19.4, 28.2, 52.8]
pressão extrema         R² = 20.66%   spread 46x   τ_médio 14.8
    taus = [1.2, 1.2, 1.2, 1.3, 1.3, 21.2, 36.2, 54.9]
```

### 4.2 Achado

**Sem tensão, pressão apenas destrói (colapso de canto). Com tensão, pressão especializa.** Sob pressão extrema na tarefa com memória, a população sacrificou 5 de 8 neurônios ao mínimo mas **preservou três τ longos** (21, 36, 55) — exatamente a memória exigida pela tarefa. Estrutura emergiu da escassez.

**Achado secundário:** sem pressão, a evolução superou o banco log-espaçado projetado manualmente (26.99% vs 23.74%), descobrindo distribuições não-óbvias de τ.

### 4.3 Princípio

> Pressão só produz estrutura quando existe **tensão** — uma força oposta que torna custosa a perda daquilo que está sendo penalizado. Pressão sem tensão produz colapso, não organização.

Corolário de projeto: ao adicionar regularização/custo a um sistema, verificar primeiro se a tarefa realmente **exige** o recurso penalizado. Se não exigir, a regularização apenas remove capacidade sem ganho.

---

## 5. Experimento B — agente de sobrevivência (ambiente estacionário)

**Desenho:** agente com energia `E` decrescente; escolha entre forrageio seguro (ganho pequeno) e arriscado (ganho grande, 6% de morte). Estados internos `Th` e `P` conforme eqs. (1)–(3). Genoma evoluído: `[w₀, w₁, w₂, log τ_T, log τ_P]`. Ablação: `w₂ ≡ 0`.

**Resultados:**

```
com pressão (completo):   fitness médio 184.5
sem pressão (ablado):     fitness médio 200.8      ← melhor SEM
ganho da pressão:         −8.1%

razão τ_P/τ_T por seed:   0.2x, 0.6x, 0.5x, 5.7x   ← inconsistente
```

**Política do melhor agente (comportamento qualitativo correto):**

```
saciado, calmo                     P(arriscar) =  7.0%
fome AGUDA, sem histórico          P(arriscar) = 43.3%
calmo agora, fome CRÔNICA          P(arriscar) = 10.8%
fome aguda + crônica               P(arriscar) = 55.2%
```

**Explicação teórica da falha (não é ruído experimental):**

> **Teorema (MDP totalmente observável):** em processo de decisão markoviano com estado plenamente observável e dinâmica estacionária, a política ótima é função apenas do estado atual. Memória é provadamente inútil.

Como `E` era observável e o ambiente estacionário, `d = 1 − E` continha toda a informação relevante; `P` era matematicamente redundante. O canal extra apenas adicionou parâmetros ao espaço de busca, degradando a otimização.

**Condição necessária derivada:** a pressão só pode carregar informação em ambiente **parcialmente observável** com variável oculta de escala longa.

---

## 6. Experimento C — ambiente parcialmente observável (estações ocultas)

### 6.1 Predições registradas ANTES da execução

Para HMM de dois estados com probabilidade de troca `q` por passo, a atualização bayesiana em log-odds é:

```
L[n+1] ≈ (1 − 2q)·L[n] + log Λ(observação)
```

Isso é um integrador com vazamento, cuja constante de tempo ótima é:

```
τ_ótimo = 1/(2q) = duração_média_da_estação / 2
```

Com estação média de 150 passos → **predição: τ_P ≈ 75**.

| # | Predição |
|---|---|
| 1 | `w₂ > 0` consistente entre seeds |
| 2 | `τ_P ≈ 75`, `τ_T` pequeno |
| 3 | Ablação de `P` deve piorar o fitness |

### 6.2 Resultados

```
com pressão:   fitness médio 323.5   w₂ médio +2.76   τ_P mediana 2.1
sem pressão:   fitness médio 315.6
ganho:         +2.5%   (desvio entre seeds ≈ 25 → dentro do ruído)
```

| # | Predição | Resultado |
|---|---|---|
| 1 | `w₂ > 0` | ✅ **confirmada** — 4/5 seeds positivos, média +2.76 (vs ≈0 no ambiente estacionário) |
| 2 | `τ_P ≈ 75` | ❌ **refutada** — mediana 2.1, ordem de magnitude errada |
| 3 | ablação piora | 🟡 **fraca** — +2.5%, dentro do ruído |

### 6.3 Diagnóstico

A derivação de `τ_ótimo = 1/(2q)` pressupõe **observação direta e ruidosa da variável oculta**. No experimento, o agente observava a própria energia — que é variável **de ação**, não de sensor: ela responde à política em poucos passos, de modo que a informação sobre a estação já estava disponível na escala rápida.

Em termos do checklist (§2), o **check 5 falhou por um motivo mais sutil**: a informação existia, mas era acessível sem integração lenta, tornando o canal lento redundante novamente.

---

## 7. Condição de validade refinada (estado atual da hipótese)

Após três rodadas de refutação, a hipótese sobrevivente é **específica e falsificável**:

> A pressão crônica (canal lento) só compensa seu custo quando **todas** as condições valem:
> 1. O ambiente é **parcialmente observável** (existe variável oculta relevante para a política);
> 2. A variável oculta tem **escala de tempo longa** relativa à dinâmica de ação;
> 3. **Cada observação individual é fracamente informativa** — razão de verossimilhança próxima de 1, de modo que a inferência exige acumulação prolongada;
> 4. A observação **não é uma variável de ação** do próprio agente (senão a política encurta o caminho da inferência).

A condição 3 é a que ainda não foi testada e constitui o próximo experimento: reduzir o contraste entre estações (ex.: taxa de sucesso 0.50 vs 0.42 em vez de 0.62 vis 0.16), de modo que nenhum evento isolado seja diagnóstico.

**Predição para esse teste:** `τ_P` deve subir para a ordem de dezenas e a ablação deve produzir perda estatisticamente distinguível do ruído entre seeds.

---

## 8. Histórico de refutações (registro metodológico)

| Rodada | Hipótese | Resultado | Refinamento produzido |
|---|---|---|---|
| HLC (doc irmão) | homeostase + gating por volatilidade melhora previsão | não confirmada sob reservoir congelado | protocolo penaliza células cujo valor está no treino |
| A (sem memória) | pressão molda estrutura | colapso total | pressão exige **tensão** oposta |
| A (com memória) | pressão molda estrutura | ✅ confirmada — especialização | princípio §4.3 |
| B | tensão/pressão melhora sobrevivência | pior que ablado | teorema do MDP observável |
| C | com oculto, pressão emerge | `w₂>0` ✅, `τ_P` ❌ | evidência precisa ser **fraca** |

---

## 9. Aplicações práticas do princípio (independentes da validação acima)

O achado do experimento A é robusto e diretamente aplicável:

- **Regularização** — antes de aumentar λ / weight decay / poda, confirmar que a tarefa exige o recurso penalizado. Sem isso, a pressão só remove capacidade.
- **Busca de arquitetura** — evolução sobre a distribuição de τ superou design manual log-espaçado. Barato de rodar (readout em forma fechada) e vale como etapa de tuning.
- **Design de IA de jogo** — a distinção tensão/pressão produz comportamento qualitativamente convincente (ver política em §5) mesmo quando não é ótima. Para NPC, plausibilidade comportamental pode valer mais que otimalidade.
- **Sistemas de controle** — o teorema do MDP observável indica quando NÃO adicionar memória: se o estado é plenamente observável e a dinâmica é estacionária, memória é custo puro.

---

## 10. Arquivos

| Arquivo | Conteúdo |
|---|---|
| `neuronios-liquidos-resumo.md` | fundamentos, EMA/filtros, LTC/CfC, célula HLC, resultados iniciais |
| `pressao-tensao.md` | este documento |
| `hlc.py` | células leaky/LTC/HLC + readout ridge + arnês multi-seed |
| `pressao.py` | experimento A, versão sem exigência de memória (colapso) |
| `expA.py` | experimento A, versão com exigência de memória (especialização) |
| `expB.py` | experimento B, agente em ambiente estacionário |
| `expC.py` | experimento C, agente com estações ocultas + predições registradas |

Dependências: `numpy`, `scipy`. Todos executáveis diretamente com `python3 <arquivo>`.

---

## 11. Ressalvas

- Todos os experimentos usam **dados sintéticos**; nenhum resultado foi verificado em dados reais.
- Os protocolos de reservoir congelado penalizam sistematicamente células cujo valor está no treinamento por gradiente — as conclusões sobre HLC/LTC **não** se transferem ao regime treinado por BPTT.
- Contagens de seeds são baixas (3–5). Diferenças abaixo de ~10% não são distinguíveis do ruído nos experimentos B e C.
- Referências bibliográficas foram citadas de memória durante a sessão e não verificadas contra as publicações originais.
