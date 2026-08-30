# SPEC — Brief para agente especialista

Documento de trabalho. Leia `docs/05-achados.md` ANTES de escrever qualquer código:
ele contém os resultados negativos que impedem retrabalho.

## 0. Contexto em 30 segundos

Investigação sobre neurônios de tempo contínuo (LTC/CfC) e neuromodulação.
Já validado em numpy: U invertido do ganho, princípio pressão/tensão, arquitetura
mínima de 6 neurônios. Já refutado: célula HLC sob reservoir congelado, e a
predição de τ_P para pressão crônica.

**O que falta:** o teste justo com BPTT (todos os parâmetros treináveis) e um
gatilho de modulação bem-condicionado.

## 1. Invariantes do projeto — NÃO violar

| # | Invariante | Motivo |
|---|---|---|
| I1 | Modulação é **multiplicativa e lateral**, nunca camada em série | ver docs/03 §1 |
| I2 | Integração por **Euler implícito**, nunca explícito | `leak` é grande e variável; explícito diverge para `dt·leak > 2` |
| I3 | `τ` sempre parametrizado em **log** | garante positividade sob gradiente |
| I4 | Todo experimento roda com **≥5 seeds** e reporta desvio | diferenças <10% são ruído (docs/05) |
| I5 | Toda hipótese tem **predição registrada antes** de rodar | ver formato em exp06 |
| I6 | Resultado negativo é **documentado, não descartado** | metade do valor deste repo |
| I7 | Baseline obrigatório em toda comparação | leaky com τ fixo; e persistência para previsão |
| I8 | Contagem de parâmetros **igualada** entre células comparadas | senão a comparação é inválida |

## 2. Estrutura

```
src/cells.py        LeakyCell, LTCCell, HLCCell — hooks de modulação já embutidos
src/modulators.py   BancoModulador: 5 canais com dinâmica de reserva
src/plasticity.py   traço de elegibilidade + regra de três fatores
src/readout.py      ridge em forma fechada (o vértice da parábola)
src/core.py         RedeNeuromodulada: núcleo + acoplamento multiplicativo
src/analysis.py     lesão, espectro de τ, sigma de criticalidade, curva N
experiments/        exp00..exp06, todos em numpy, todos rodáveis direto
tests/test_smoke.py rode ANTES de qualquer coisa: pytest tests/ -v
```

## 3. Tarefas, em ordem de prioridade

### T1 — Teste justo da HLC (BPTT)  [ALTA]
**Objetivo:** decidir se a HLC tem valor quando `β`, `κ`, `τ_v` são treinados.
**Por que importa:** o resultado negativo de exp01 é inconclusivo por construção.

Protocolo:
- tarefas: (a) regime-switching sintético, (b) sMNIST permutado, (c) série real
- baselines: LeakyCell, LTCCell, GRU — **contagem de parâmetros igualada** (I8)
- ablação: `β>0,κ=0` e `β=0,κ>0` separadamente (atribui efeito a cada mecanismo)
- 5 seeds, reportar média ± desvio
- **critério de sucesso:** ganho >1 desvio sobre LTC em (a) sem perda em (b)

Critério de parada: se não superar em nenhuma tarefa, documentar em docs/05 e
encerrar a linha. Não insistir.

### T2 — Gatilho bem-condicionado para modulação  [ALTA]
**Objetivo:** corrigir a falha de P3 no exp06 (adaptativo −26.7% com ruído).

Diagnóstico registrado: `surpresa = |c − c_ant|` faz o ruído virar surpresa.
Implementar e comparar:
```
G1 (atual):    surpresa = |c[t] − c[t−1]|
G2 (filtrado): surpresa = |EMA_rápida(c) − EMA_lenta(c)|
G3 (predição): surpresa = |c[t] − ĉ[t]|, ĉ de readout linear sobre o estado
G4 (normaliz): G3 dividido por desvio-padrão corrente (surpresa em unidades de sigma)
```
**Predição a registrar antes:** G3/G4 recuperam a vantagem sob ruído; G1 não.

### T3 — Condição 3 da hipótese pressão/tensão  [MÉDIA]
Rodar exp04 com **evidência fraca**: contraste entre estações 0.50 vs 0.42
(em vez de 0.62 vs 0.16). Predição registrada: `τ_P` sobe para ordem de dezenas
e a ablação passa a doer além do ruído.

### T4 — Hierarquia de τ emergente  [MÉDIA]
Treinar rede recorrente hierárquica e verificar se o gradiente de τ
(sensorial curto → associativo longo) emerge sozinho. Medir com
`analysis.espectro_tau` por camada.

### T5 — Plasticidade de três fatores end-to-end  [MÉDIA]
Usar `TracoElegibilidade` num agente RL simples. Comparar com REINFORCE.
M�trica: amostras até convergir.

### T6 — Criticalidade auto-organizada  [BAIXA]
Plasticidade que ajusta E/I para manter `sigma ≈ 1` sozinho.
Medir com `analysis.sigma_ramificacao`.

## 4. Hiperparâmetros — valores de partida

### Células
| Param | Valor | Faixa de busca | Nota |
|---|---|---|---|
| `n_units` | 6–64 | 2..128 | rodar curva N (exp05); mais nem sempre é melhor |
| `tau_min` | 1.0 | 0.5..2 | |
| `tau_max` | 100 | 20..400 | cobrir a escala do comportamento |
| `dt` | 1.0 | — | manter 1.0 e escalar τ |
| `A` | 1.0 | 0.5..2 | limite superior do conjunto invariante |
| `frac_inib` | 0.25 | 0.15..0.35 | mantém sigma≈1; 0% → epilepsia |

### HLC (específicos)
| Param | Valor | Faixa | Nota |
|---|---|---|---|
| `beta` | 2.5 | 0..6 | 0 recupera LTC |
| `kappa` | 0.7 | 0..1.5 | 0 desliga homeostase |
| `tau_v` | 60 | 20..200 | janela do estimador de variância |
| `sigma_alvo` | 0.5 | 0.2..1.0 | escala de saída desejada |

### Moduladores (τ em passos)
| Canal | τ_limpeza | τ_repor | a | Racional |
|---|---|---|---|---|
| `gain` (NA) | 25 | 400 | 0.20 | rápido, reserva média |
| `plast_thr` (cortisol) | 400 | 3000 | 0.05 | lento; crônico |
| `lr` (DA) | 8 | 120 | 0.35 | fásico, reserva rápida |
| `sens_rec` (ACh) | 60 | 600 | 0.12 | intermediário |
| `discount` (5-HT) | 300 | 2000 | 0.06 | lento |

### Acoplamento
| Param | Valor | Nota |
|---|---|---|
| `a_tau` | 1.0 | `τ ← τ/(1 + a_tau·m_gain)` |
| `b_gain` | 1.0 | `β ← β₀·(1 + b_gain·m_gain)` |
| `β₀` | **1.0** | **pico medido do U invertido (exp06). β=8 custa ~90%.** |

### Plasticidade
| Param | Valor | Faixa |
|---|---|---|
| `tau_e` | 20 | 5..50 (a ponte temporal) |
| `eta` | 1e-3 | 1e-4..1e-2 |
| `lam` | 1e-5 | 1e-6..1e-3 |

### Readout
| Param | Valor | Nota |
|---|---|---|
| `lam` (ridge) | 1e-2 | normalizado por T; alto→subajuste, baixo→sobreajuste |

## 5. Protocolo de validação obrigatório

Todo resultado novo passa por:
1. **curva N × desempenho** — achar o mínimo suficiente (`analysis.curva_N`)
2. **lesão sistemática** — `analysis.lesao`; nenhum neurônio deve ser redundante
3. **espectro de τ** — `analysis.espectro_tau`; spread revela a arquitetura
4. **sigma** — `analysis.sigma_ramificacao`; alvo ≈ 1
5. **≥5 seeds** com desvio reportado

## 6. Armadilhas conhecidas (já custaram tempo)

1. **Euler explícito diverge** com `leak` grande. Usar implícito (I2).
2. **Reservoir congelado penaliza células não-lineares.** Não tirar conclusão
   sobre LTC/HLC sem treinar (docs/05 §8).
3. **Modulação com gatilho ruidoso é pior que nada** (exp06 P3, −26.7%).
4. **Mais neurônios pioram** sem pressão que organize (exp05, N≥10).
5. **Memória é inútil em MDP observável** — teorema, não bug (docs/05 §7).
6. **λ da ridge deve escalar com T**, senão a regularização muda com o tamanho
   do dataset sem você perceber.

## 7. Como rodar

```bash
pip install -r requirements.txt
pytest tests/ -v                              # smoke, ~5 s
python3 experiments/exp06_yerkes_dodson.py    # ~2 min, o mais informativo
python3 experiments/exp05_minimo_neuronios.py # ~3 min, curva N + lesão
```

## 8. Definição de pronto

Uma tarefa está pronta quando:
- há predição registrada **antes** do resultado
- há ≥5 seeds com desvio
- há baseline com parâmetros igualados
- o resultado (positivo OU negativo) está em `docs/05-achados.md`
- os hiperparâmetros usados estão nesta SPEC
