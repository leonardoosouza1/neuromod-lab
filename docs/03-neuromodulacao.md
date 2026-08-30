# Neuromodulação — A Segunda Camada

## 1. A distinção arquitetural

```
NEURÔNIO:   rápido, ponto-a-ponto, ADITIVO,        transporta DADO
MODULADOR:  lento,  broadcast,     MULTIPLICATIVO, transporta PARÂMETRO
```

Camada normal:   `h' = f(W·h + b)`
Camada modulada: `h' = f(g(m)·W·h + b(m))`, com `τ`, `θ`, `η` também funções de `m`.

**O modulador entra como hiperparâmetro em tempo real.** Não é somado à entrada —
reconfigura a rede. Uma "camada extra em série" NÃO implementa isso; o canal correto
é lateral e multiplicativo.

Equivalentes já existentes em ML:
- **FiLM** — `h = γ(m)·h + β(m)` (Perez et al., 2018). É o gancho para mexer num LLM.
- **Hypernetworks** — uma rede gera os pesos de outra.
- **Gain modulation** — literatura de neurociência computacional.

## 2. Dinâmica de liberação (reserva finita)

```
dR/dt = (R_max − R)/τ_repor  −  a·S(t)·R      (reserva)
dm/dt = a·S(t)·R  −  m/τ_limpeza              (circulante)
```

`S(t)` = gatilho. Adrenalina: `τ_limpeza` ≈ 2–3 min, `τ_repor` = horas.

Propriedades emergentes (não programadas):
- pico rápido, decaimento lento → o susto dura muito mais que a causa
- `R` esgota sob estímulo repetido → não dá para assustar duas vezes em 10 s
- estresse crônico mantém `R` baixo → **burnout é reserva esgotada, calculável**

Verificado em `tests/test_smoke.py::test_modulador_reserva_esgota`
(após 30 passos de gatilho contínuo: reserva 1.0 → 0.014).

## 3. Os cinco canais

| Canal (código) | Análogo | Hiperparâmetro controlado | Efeito |
|---|---|---|---|
| `gain` | noradrenalina | ganho global β, encurta τ | urgência, reatividade — **a TENSÃO** |
| `plast_thr` | cortisol | limiar de plasticidade, λ de esquecimento | crônico — **a PRESSÃO** |
| `lr` | dopamina | taxa de aprendizado η, gating go/no-go | o que consolida |
| `sens_rec` | acetilcolina | razão entrada sensorial ÷ recorrência | confiar no mundo vs na memória |
| `discount` | serotonina | fator de desconto γ, custo do esforço | paciência, horizonte temporal |

**Dois eram conhecidos** (tensão e pressão, dos experimentos A–C). Os outros três
controlam **aprendizado, atenção e horizonte** — as dimensões que faltavam.

## 4. Dopamina ≈ erro de predição de recompensa

```
δ(t) = r(t) + γ·V(s_{t+1}) − V(s_t)
```

Recompensa esperada → sem disparo. Melhor que o esperado → disparo.
Pior → pausa abaixo da linha de base. É o resultado mais bem estabelecido
da interface neurociência–ML.

## 5. Plasticidade de três fatores — "como forçar o sistema a aprender"

Resposta: **você não força, você libera.**

```
de_ij/dt = −e_ij/τ_e + pré_i · pós_j          traço de elegibilidade
Δw_ij    = η(m_lr)·e_ij  −  λ(m_plast)·w_ij   consolidação + esquecimento
```

O traço marca "essas duas células estavam ativas juntas há pouco" e **espera**.
Se o modulador chegar dentro de `τ_e` (~1–2 s), consolida; senão evapora.
Resolve atribuição de crédito no tempo sem BPTT.

Implementado em `src/plasticity.py`.

## 6. Nervosismo, raiva, alegria — a matemática do prejuízo

```
h = tanh(β·(sinal + ruído))
```

Três mecanismos de degradação sob β alto:
1. **Amplifica sinal E ruído igualmente** — a razão sinal/ruído não melhora
2. **Satura o tanh** — a derivada `1 − tanh²` → 0, **a resolução colapsa**;
   tudo vira ±1, decisões binárias e grosseiras
3. **τ curto destrói memória de trabalho** — a janela de integração encurta

Resultado: desempenho × ativação é um **U invertido** (Yerkes-Dodson).
Medido em `experiments/exp06_yerkes_dodson.py` — ver docs/05 §4.

**Esquecimento modulado:**
```
dw/dt = −λ(m)·w        λ sobe com cortisol crônico
```
Estresse prolongado → λ alto → esquecimento acelerado.

**Estados afetivos como pontos no espaço (NA, DA, 5-HT, ACh):**
- raiva ≈ NA alta + 5-HT baixa (horizonte curto, age já)
- alegria ≈ DA alta + NA média (aprende bem, explora)
- apatia ≈ tudo baixo
- ansiedade ≈ NA alta + cortisol alto (reativo e com plasticidade prejudicada)

## 7. Crescer e podar

**Podar:** pressão metabólica (exp02, validado — ver docs/02 §4).

**Crescer** — gatilho calculável:
```
adiciona capacidade quando:  erro residual estagnou
                          E  unidades existentes saturadas
                          E  resíduo ainda correlaciona com algo não representado
```
Algoritmos: cascade-correlation, Net2Net, redes dinamicamente expansíveis.

**Ciclo completo:** cresce onde o erro correlaciona → poda sob pressão →
sobra a arquitetura mínima suficiente. Mesmo par tensão/pressão, agora sobre
a topologia em vez dos τ.

## 8. Ressalvas

- Dopamina ≈ RPE é sólido. **As outras quatro atribuições são simplificações de
  literatura em disputa.** Noradrenalina tem pelo menos dois modos (fásico vs
  tônico) com efeitos diferentes.
- Neuromodulador real não é escalar: são subtipos de receptor com efeitos
  **opostos** no mesmo alvo (D1 vs D2). O vetor de 5 é caricatura útil, não mecanismo.
- Nada disso foi validado em rede grande. É especificação + um experimento piloto.
