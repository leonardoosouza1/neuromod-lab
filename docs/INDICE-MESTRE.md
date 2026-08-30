# ÍNDICE MESTRE — Projeto Neuromod

**Como usar este pacote.** Leia esta página inteira antes de abrir qualquer outro arquivo. Ela diz o que está validado, o que foi refutado, e em que ordem implementar.

**Regra fundamental do projeto:** resultado negativo é resultado. Metade do valor deste material está no que **não** funcionou — isso evita retrabalho.

---

## 1. A tese do projeto em três frases

1. **Neurônio de tempo contínuo ≡ média móvel exponencial.** Um banco desses com τ log-espaçados é um banco de filtros multi-escala, e é o primitivo de tudo.
2. **Estrutura importa mais que escala.** Poucas unidades heterogêneas, sob pressão metabólica com tensão presente, superam muitas unidades homogêneas.
3. **A segunda camada (neuromodulação) transporta parâmetro, não dado.** Ela reconfigura τ, ganho e taxa de aprendizado multiplicativamente — nunca é somada ao estado.

Aposta falsificável: se um substrato de 10³–10⁶ unidades com essas propriedades não superar uma rede convencional de tamanho igual, a tese está errada.

---

## 2. Mapa dos documentos

| # | Arquivo | Conteúdo | Ler quando |
|---|---|---|---|
| — | **`docs/05-achados.md`** | **tudo que foi medido, incl. o que falhou** | **primeiro, sempre** |
| 01 | `01-fundamentos.md` | neurônio ≡ EMA, banco de filtros, derivação do LTC, célula HLC, readout ridge | base matemática |
| 02 | `02-pressao-tensao.md` | estabilidade do LTC, checklist de 5 pontos p/ células novas, exp00–04 | antes de propor célula |
| 03 | `03-neuromodulacao.md` | a segunda camada, 5 canais, três fatores, U invertido | antes de modular |
| 04 | `04-dimensionamento.md` | fórmulas de limiar, piso de N, memória como atrator | antes de dimensionar |
| 06 | `06-exp09-evolucao-neuromodulada.md` | fórmula do ganho **G**, plano PyTorch/GPU, predições registradas | próximo experimento |
| 07 | `07-exp10-corpo-minimo.md` | corpo virtual, recompensa homeostática, G calculado | corpo/interocepção |
| 08 | `08-desenvolvimento-alocacao-frequencia.md` | alometria, cronograma, aferência, frequência/bandas, poda trófica | alocação de neurônios |
| 09 | `09-cerebro-virtualizado.md` | química (Nernst/GHK/NMDA), Hodgkin-Huxley, Izhikevich, regiões, custo | emulação biofísica |
| 10 | `10-latencia-memoria-sensores.md` | hierarquia de latência, sistemas de memória, roteamento sensorial | fusão de sensores |
| — | `esparsidade-contextual-protocolo.md` | protocolo para medir esparsidade em Qwen real | sessão do LLM |
| — | **`SPEC.md`** | invariantes, tarefas priorizadas, hiperparâmetros | **antes de codar** |

---

## 3. Achados — o que está validado

| Achado | Evidência | Onde |
|---|---|---|
| Neurônio líquido ≡ EMA; `τ = −dt/ln α` | analítico | 01 |
| Diferença de dois τ ≈ derivada (= MACD) | analítico | 01 §3.1 |
| PID = reservoir de 3 neurônios | analítico | 01 §3.1 |
| LTC funciona por 3 garantias (invariante, τ_ef limitado, Jacobiano ∈(0,1)) | verificado em teste: entrada ×100 → max\|h\| = 0,987 | 02 §1 |
| Readout ótimo = vértice de parábola = ridge | verificado: w* = 2,5000 exato | 01 §5 |
| **U invertido do ganho** (Yerkes-Dodson) | medido: pico β=1,0; β=8 custa ~90 % | 05 §4 |
| **Pressão exige tensão** | medido: sem tensão → colapso; com tensão → especialização | 05 §5 |
| **6 neurônios bastam**; N≥10 piora; nenhum redundante | medido: exp05 + lesão | 05 §6 |
| Memória é inútil em MDP totalmente observável | teorema + medido (−8,1 %) | 05 §7 |
| Modulação constante = reparametrização (não adiciona poder) | teorema | 06 §2.1 |
| **Ganho G calculável em forma fechada** antes de simular | exp08 | 06 §3 |
| **2 shifts cobrem qualquer τ** com <5 % de erro, zero multiplicação | medido | esparsidade §7 |
| Reflexo é memória com timing aprendido | simulado: erro de +5 ms em dois ISIs | 10 §5.3 |
| Audição é mais rápida que visão **no cérebro** | transdução mecânica vs bioquímica | 10 §3.1 |

---

## 4. ⚠️ Refutado — não repetir

| Hipótese | Resultado | Onde |
|---|---|---|
| Célula HLC supera baselines | **não confirmada** (protocolo inconclusivo: reservoir congelado penaliza células treináveis) | 05 §8 |
| Pressão crônica ajuda em ambiente estacionário | **pior que ablado** (−8,1 %) — teorema do MDP observável | 05 §7 |
| τ_P evolui para 1/(2q) com regime oculto | **refutado**: mediana 2,1 vs predição 75 | 06 §6.3 |
| Modulação adaptativa > parâmetro fixo | **só sem ruído**; com ruído **−26,7 %** (gatilho mal-condicionado) | 05 §4 |
| Selecionar "os neurônios importantes" | **refutado**: 8 de 128 fica pior que o baseline; informação é distribuída | esparsidade §5 |
| Pular neurônios que mal mudam | ruim: 20 % de economia custa 1,5 % de erro | — |
| **Banco de τ alinha sensores defasados** | **refutado**: hardcode correto +3,05 % vs banco 0,04 % | **10 §4** |
| ML quebra criptografia / fatoração | correlação fitness-distância ≈ 0,04 — sem gradiente explorável | — |

**A refutação de §10 §4 é a mais importante para implementação:** alinhamento temporal exige **atraso puro (buffer)**, não suavização. EMA borra, não translada.

---

## 5. Padrão recorrente: o U invertido

Apareceu cinco vezes, em domínios independentes:

| Domínio | Pouco | Muito |
|---|---|---|
| λ da regressão ridge | pesos explodem | pesos morrem |
| inibição na rede (E/I) | epilepsia | silêncio |
| pressão metabólica | sem estrutura | colapso total |
| ganho β (neuromodulação) | não reage | satura, resolução colapsa |
| taxa de aprendizado η | não converge | diverge |

**O regime útil é sempre a borda.** Nome técnico: criticalidade. Alvo prático: `σ ≈ 1` (parâmetro de ramificação), mantido por ~20–30 % de inibição.

---

## 6. Convergência externa (validação independente)

O Google publicou **Nested Learning / HOPE** (NeurIPS 2025) com estrutura equivalente:

| Nosso conceito | Equivalente deles |
|---|---|
| banco de τ log-espaçados | **Continuum Memory System** (razão 10⁶ entre extremos) |
| readout ridge fechado | "deep optimizers" com perda L2 |
| traço de elegibilidade / surpresa | priorização por "surprise" no Titans |
| esquecimento controlado por escala | mitigação de esquecimento catastrófico por frequência |

**A lacuna que permanece nossa:** as frequências do CMS são **hiperparâmetro fixo**. Nenhum trabalho conhecido as evolui por indivíduo nem as modula em tempo real por estado interno. Isso é exatamente `docs/06` + `docs/03`.

Ressalva: resultados do HOPE são dos próprios autores; falta replicação independente.

---

## 7. Ordem de implementação

### Fase 0 — validar a base (custo: minutos, INEGOCIÁVEL)
```
1. rodar tests/test_smoke.py
2. docs/07 §10 passo 1: reproduzir G numericamente com EMA fixa
   → se o MSE não bater com P(K), a teoria está errada e nada mais importa
```

### Fase 1 — o substrato (dias)
```
3. Izhikevich isolado, 5 tipos → reproduzir padrões publicados
4. 1000 neurônios, E/I 80/20 → medir σ, alvo ≈ 1
5. + NMDA e STDP → verificar emergência de assembleias
```

### Fase 2 — os experimentos abertos (semanas)
```
6. SPEC T1: HLC com BPTT (o teste justo)
7. SPEC T2: gatilho bem-condicionado (G3/G4) — o achado mais acionável
8. docs/06 exp09: evolução de neuromodulação
9. docs/07 exp10: corpo mínimo com interocepção
```

### Fase 3 — aplicação (contínuo)
```
10. docs/10 §6: roteamento por latência no piloto virtual
11. esparsidade-contextual-protocolo.md: medir em Qwen real
```

**Regra:** cada fase precisa de um teste que pode **falhar**. Sem critério de falha, não é validação.

---

## 8. Invariantes de código (do SPEC.md)

| # | Invariante | Motivo |
|---|---|---|
| I1 | Modulação **multiplicativa e lateral**, nunca camada em série | 03 §1 |
| I2 | Integração por **Euler implícito**, nunca explícito | leak grande → explícito diverge para `dt·leak > 2` |
| I3 | `τ` sempre parametrizado em **log** | positividade sob gradiente/mutação |
| I4 | Todo experimento com **≥5 seeds** e desvio reportado | diferenças <10 % são ruído |
| I5 | **Predição registrada antes** de rodar | ver formato em exp06/exp08 |
| I6 | Resultado negativo **documentado**, não descartado | metade do valor do repo |
| I7 | Baseline obrigatório em toda comparação | leaky com τ fixo; persistência p/ previsão |
| I8 | Contagem de parâmetros **igualada** entre células comparadas | senão a comparação é inválida |
| I9 | **Alinhar antes de filtrar**: buffer de atraso, depois banco de τ | 10 §4 |

---

## 9. Fórmulas de bolso

```
τ ↔ α          α = e^(−dt/τ)          τ = −dt/ln α
período P      α = 1 − 2/(P+1)
99 % do alvo   n ≈ 4,6·τ
frequência     f_corte = 1/(2πτ)

limiar         t_disparo = −τ·ln(1 − θ/(u·τ))       u_min = θ/τ
vértice        w* = −b/(2a)
ridge          W = (FᵀF + λI)⁻¹Fᵀy
Newton         w ← w − (dL/dw)/(d²L/dw²)
η ótimo (1D)   η* = 1/(2a)            estabilidade: η < 1/a

ganho G        G = [min_K E_c P(K;c) − E_c min_K P(K;c)] / min_K E_c P(K;c)
               G ≈ 0 → modulação é peso morto; G > 15 % → vale construir

Nernst         E = (RT/zF)·ln([out]/[in])
homeostase     r = β·(D_t − D_{t+1}),  D = ‖s − s*‖_w
alometria      N_parte = a·N_total^b   (córtex b≈1,35; resto b≈0,70)
```

---

## 10. Ressalva geral

Nenhum resultado deste pacote foi obtido com dados reais ou modelos treinados de grande porte. Todos vêm de sinais sintéticos e pesos aleatórios ou pequenos. As constantes biológicas foram compiladas de conhecimento de literatura e **não verificadas contra publicações primárias**. Confirmar antes de qualquer uso formal.

O valor deste material é **direcional e metodológico** — a estrutura dos experimentos, os invariantes, e o registro do que falhou. As magnitudes precisam ser remedidas no ambiente real.
