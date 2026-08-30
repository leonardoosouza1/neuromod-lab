# EXP09 — Evolução de Neuromodulação Individual

**Documento de projeto.** Tese, fórmulas, encaixe arquitetural, plano de implementação em PyTorch/GPU e protocolo de falsificação.

**Pré-requisito de leitura:** `docs/05-achados.md` (o que já foi refutado) e `docs/03-neuromodulacao.md` (a segunda camada).

---

## 1. A tese em uma frase

> Num mundo cujo regime oculto alterna, **não existe um perfil hormonal ótimo único**. A seleção natural deve produzir uma *população com variância crescente* de genomas moduladores — e o ganho de desempenho dessa diversidade é previsível analiticamente pelo número `G` antes de qualquer simulação.

Isso é falsificável em três frentes independentes (§8).

---

## 2. Por que este experimento existe

### 2.1 O teorema que motiva tudo

Com `m` constante, a célula modulada é:

```
τ' = τ₀/(1 + a₁m)      W' = (1 + a₂m)·W      b' = (1 + a₂m)·b
```

**Isso é apenas outro LTC com parâmetros diferentes.** Reparametrização pura, zero ganho expressivo.

> **Corolário:** neuromodulação só adiciona poder quando `m` **varia**, e especificamente quando os parâmetros ótimos `(τ*, β*)` dependem de um **contexto oculto** inferível apenas pela história.

Isso explica rigorosamente as duas refutações anteriores:
- **exp03** (ambiente estacionário): um `θ*` serve para tudo → modulação é peso morto. Medido: −8,1%.
- **exp06 P3** (gatilho ruidoso): o modulador variava, mas na direção errada. Medido: −26,7%.

### 2.2 O que este experimento adiciona

Os experimentos anteriores testaram modulação **fixada à mão**. Este testa modulação **evoluída**, com duas hipóteses novas:

1. O gatilho não é dado — é **descoberto** pela seleção.
2. Indivíduos com o mesmo genoma inicial, submetidos a histórias diferentes, devem **divergir** em perfil hormonal.

---

## 3. A fórmula central — ganho de modulação `G`

### 3.1 Derivação

Tarefa canônica de rastreamento: sinal latente `s` é um processo Ornstein-Uhlenbeck discreto com persistência `ρ`; a observação é `y = s + v`, com `Var(v) = R`. O estimador é uma EMA com ganho `K` (equivalente a `τ ≈ 1/K`).

Dinâmica do erro (forma de Joseph, válida para **qualquer** K, não só o ótimo):

```
e⁻[n] = ρ·e[n−1] + w[n]              predição
e[n]  = (1−K)·e⁻[n] − K·v[n]         atualização
```

Tomando variância em regime estacionário, com `Q = σ_s²(1−ρ²)`:

```
              (1−K)²·Q + K²·R
   P(K) = ───────────────────────
             1 − (1−K)²·ρ²
```

### 3.2 O número que decide se vale construir

Para uma família de regimes `c` com pesos `π_c`:

```
J_fixo  = min_K  Σ_c π_c · P(K; c)          melhor τ ÚNICO para todos os regimes
J_adapt = Σ_c π_c · min_K P(K; c)           τ ótimo POR regime
G       = (J_fixo − J_adapt) / J_fixo       ganho relativo máximo
```

**`G` é o teto do que qualquer modulador pode comprar naquele mundo.** Nenhum arranjo de arquitetura, treino ou evolução supera esse limite.

### 3.3 Valores calculados (exp08, forma fechada, sem simulação)

| Cenário | G | τ* por regime |
|---|---|---|
| estacionário (1 regime) | **0,0 %** | [1,7 · 1,7] |
| ruído 2× (contraste fraco) | 1,7 % | [1,4 · 1,7] |
| ruído 10× | 12,5 % | [1,2 · 2,1] |
| **ruído 100× (contraste forte)** | **25,6 %** | [1,1 · 4,2] |
| **persistência 0,99 ↔ 0,70** | **21,2 %** | [2,8 · 1,2] |
| ambos mudam juntos | 1,2 % | [1,4 · 2,4] |

Três usos práticos:
1. **Filtro de cenário** — `G ≈ 0` significa que nenhum modulador ajuda; descarte antes de escrever código.
2. **Calibração de amplitude** — os `τ*` dizem exatamente qual faixa o canal precisa varrer, o que fixa `a₁` (§5.3).
3. **Resultado não-óbvio** — quando ruído *e* persistência mudam juntos, os efeitos se cancelam (G = 1,2 %). Um mundo "mais complexo" pode exigir **menos** modulação.

**Decisão de projeto:** usar contraste alto em **uma** dimensão só. Ambiente A (ruído 100×, G ≈ 25,6 %) como principal, ambiente B (estacionário, G = 0 %) como controle negativo.

---

## 4. Onde a modulação encaixa na fórmula da célula

Sistema de duas etapas, uma expressão:

```
ETAPA 1 — rápida (τ ~ ms), transporta DADO:

  dh/dt = −[ (1 + a₁·m)/τ₀ + S ]·h  +  S·A
                └── vazamento ──┘

  S = σ( (1 + a₂·m) · (W_in·x + W_rec·h + b) )
        └── ganho ──┘

ETAPA 2 — lenta (τ ~ s), transporta PARÂMETRO:

  dR/dt = (R_máx − R)/τ_repor − a·G_trig·R      reserva finita
  dm/dt = a·G_trig·R − m/τ_limpeza              circulante
  G_trig = σ(w_g · φ(x, h, δ))                  o GATILHO — evoluído, não dado
```

**Regras de acoplamento (invariante I1):**

| Alvo | Operação | Nunca |
|---|---|---|
| `τ` | **dividido** por `(1 + a₁m)` | somado |
| ganho `β` | **multiplicado** por `(1 + a₂m)` | somado |
| taxa de aprendizado `η` | multiplicada por `m_DA` | — |
| esquecimento `λ` | multiplicado por `m_cort` | — |
| estado `h` | **nunca tocado diretamente** | somar `m` a `h` |

Somar `m` ao estado transformaria o modulador em mais uma entrada de dado — exatamente o erro que a §2.1 proíbe.

### 4.1 Interpretação comportamental (verificada em exp07)

Mesmo bicho, mesmos pesos, só `m` mudando:

```
estado        m      τ efetivo             memória
relaxado    0,0    [3, 8, 20, 60]            900
adrenalina  2,0    [1, 2.7, 6.7, 20]         900
terror     15,0    [0.2, 0.5, 1.2, 3.8]        9   ← colapso da retenção
```

O tempo interno acelera 16×: o bicho resolve detalhe temporal mais fino (corresponde ao relato humano de "o tempo pareceu lento" — mesmo fenômeno, referencial invertido). O preço é a memória de trabalho, que despenca de 900 para 9 passos.

**Ressalva honesta:** no exp07 a resolução *subiu* monotonicamente com o ganho em vez de colapsar — nessa faixa o sigmoide ainda não satura. A saturação morde em ganhos mais altos ou bias diferente. A narrativa "muito ganho cega" precisa dessa qualificação.

---

## 5. Arquitetura do experimento

### 5.1 Dois níveis de adaptação

```
ONTOGENIA (dentro da vida) — os PESOS mudam:
    Δw_ij = η(m_DA)·e_ij − λ(m_cort)·w_ij
    e_ij é o traço de elegibilidade (τ_e ~ 20 passos)
    → o indivíduo aprende o que a sobrevivência exige

FILOGENIA (entre gerações) — o GENOMA MODULADOR muta:
    g = [a₁, a₂, τ_limpeza, τ_repor, taxa_liberação, w_gatilho(4)]
    → o que dispara adrenalina em cada linhagem evolui
```

**O requisito central — "não quero que todos passem pela mesma neuromodulação" — é satisfeito estruturalmente:** o gatilho `G_trig = σ(w_g · φ)` é uma função aprendida do estado interno. Dois indivíduos com genoma inicial idêntico, colocados em histórias diferentes, desenvolvem sensibilidades diferentes. Um vira reativo (libera com pouco), outro vira frio (limiar alto). A seleção então decide qual perfil o mundo premia — e a tese diz que **não haverá um vencedor único**.

### 5.2 Genoma completo

| Bloco | Tamanho | Herdável | Muda em vida |
|---|---|---|---|
| `W_rec` (núcleo) | N×N | sim | sim (três fatores) |
| `W_in`, `b` | N·d + N | sim | sim |
| `log_tau₀` | N | sim | não |
| `a₁, a₂` (acoplamento) | 2 | sim | não |
| `τ_limpeza, τ_repor, taxa` | 3 | sim | não |
| `w_gatilho` | 4 | sim | não |
| readout motor | N·k | sim | sim |

Com N = 8, d = 2, k = 2: ≈ 100 parâmetros por indivíduo. População de 4 096 cabe folgada em GPU.

### 5.3 Calibração de `a₁` a partir de `G`

Não chutar. Do exp08, ambiente A tem `τ* ∈ [1,1 · 4,2]`, razão ≈ 3,8. Como `τ_ef = τ₀/(1 + a₁m)`, para cobrir a faixa com `m ∈ [0, m_máx]`:

```
a₁·m_máx = (τ*_max/τ*_min) − 1 ≈ 2,8
```

Com `m_máx ≈ 1` (saturação da reserva), `a₁ ≈ 2,8`. **A fórmula fixa o hiperparâmetro.**

### 5.4 Ambientes

| | Ambiente A (principal) | Ambiente B (controle) |
|---|---|---|
| regime | ruído alterna 100× | ruído fixo |
| `G` previsto | **25,6 %** | **0 %** |
| predição | variância do genoma modulador **cresce** | variância **colapsa** |

O controle negativo é obrigatório: sem ele, qualquer diversidade observada pode ser deriva genética, não seleção.

---

## 6. Plano de implementação (PyTorch / GPU)

### 6.1 Princípio de vetorização

A população **é** a dimensão de batch. Nenhum laço sobre indivíduos.

```
h        (P, N)         estado do núcleo
W_rec    (P, N, N)      pesos individuais
m        (P, C)         C = canais moduladores
R        (P, C)         reservas
e        (P, N, N)      traços de elegibilidade
```

Passo de simulação = `torch.baddbmm` / `einsum` sobre `(P, N, N)`. Com P = 4 096 e N = 8, cada passo são ~262 k FLOPs — trivial para GPU. O gargalo é o número de passos sequenciais (o tempo não paraleliza), não a largura.

### 6.2 Laço principal

```
para cada geração:
    inicializa h, R, m, e, energia
    para t em 1..T:                          # sequencial, inevitável
        φ    = features(x, h, δ)             # entradas do gatilho
        G_t  = sigmoid(w_g · φ)              # (P,)
        R, m = passo_reserva(R, m, G_t)      # etapa 2
        τ_ef = τ₀ / (1 + a₁·m)
        S    = sigmoid((1 + a₂·m) · (W_in x + W_rec h + b))
        h    = (h + S·A) / (1 + 1/τ_ef + S)  # Euler implícito (invariante I2)
        e    = e − e/τ_e + outer(h, h_pre)   # traço
        W   += η(m_DA)·e − λ(m_cort)·W       # três fatores, sob no_grad
        energia += recompensa(h) − custo(m)  # custo metabólico da modulação
    seleção + mutação sobre o genoma
```

### 6.3 Decisões técnicas

| Decisão | Escolha | Motivo |
|---|---|---|
| Integração | Euler **implícito** | `leak` grande e variável; explícito diverge para `dt·leak > 2` (I2) |
| Otimização | evolução, **não backprop** | plasticidade de três fatores é não-diferenciável; e o objeto de estudo é justamente uma regra de aprendizado alternativa |
| Precisão | `float32` | `float16` degrada a reserva, que envolve diferenças pequenas em `τ_repor` longo |
| `τ` | parametrizado em **log** | positividade garantida sob mutação (I3) |
| Custo da modulação | explícito, `κ_m·Σm` | sem custo, `m` cresce sem limite e a comparação com o controle fica inválida |
| Semente | ≥ 5 por condição | diferenças < 10 % são ruído (I4) |

### 6.4 Custo estimado

Com P = 4 096, N = 8, T = 600, 200 gerações: ~120 M passos-indivíduo. Em GPU moderna, ordem de minutos por condição. Rodar 2 ambientes × 5 sementes é viável numa tarde.

---

## 7. Métricas obrigatórias

| # | Métrica | Como | Por quê |
|---|---|---|---|
| M1 | ganho medido vs `G` previsto | fitness(modulado) / fitness(ablado) | **testa a fórmula do §3** |
| M2 | variância do genoma modulador | `var(a₁, a₂, w_g)` por geração | testa a tese central |
| M3 | correlação gatilho ↔ contexto oculto | info mútua entre `m` e o regime real | o gatilho aprendeu a inferir? |
| M4 | espectro de `τ_ef` | `analysis.espectro_tau` com `m` vivo | a faixa varrida bate com `τ*` do exp08? |
| M5 | lesão do canal modulador | zera `m`, mede perda | quanto vale de fato |
| M6 | divergência intra-genoma | clones em histórias diferentes | o perfil individual diverge? |

M6 é o teste direto do requisito "cada um com sua reação": pega **clones idênticos**, roda em sequências de eventos diferentes, e mede se as trajetórias de `m` divergem sistematicamente.

---

## 8. Predições registradas ANTES da execução

| # | Predição | Refuta a tese se |
|---|---|---|
| P1 | Ambiente A: ganho medido entre 5 % e 25,6 % | ganho ≈ 0 ou > G (violaria o teto teórico) |
| P2 | Ambiente B: ganho ≤ 2 % | ganho significativo sem contraste de regime |
| P3 | M2 cresce em A, colapsa em B | variância cresce nos dois → é deriva, não seleção |
| P4 | M3 > 0 em A: o gatilho correlaciona com o regime oculto | gatilho aleatório com bom fitness |
| P5 | M4: faixa de `τ_ef` cobre [1,1 · 4,2] previsto | faixa descolada do previsto → fórmula errada |
| P6 | M6: clones divergem em A, não em B | divergência igual nos dois → é ruído |

**P1 é o teste mais forte da fórmula.** Se o ganho medido exceder `G`, a derivação do §3 está errada — o teto teórico foi violado. Se ficar em zero com `G = 25,6 %`, a fórmula está certa mas a arquitetura não consegue explorá-la, e o problema é implementação.

---

## 9. Riscos e critérios de parada

| Risco | Sintoma | Mitigação |
|---|---|---|
| Modulação cresce sem limite | `m` satura em todos | custo metabólico explícito `κ_m` |
| Deriva genética confundida com seleção | M2 cresce em A **e** B | controle negativo (é o motivo dele existir) |
| Gatilho degenera em constante | M3 ≈ 0 mas fitness alto | então a modulação virou reparametrização — teorema §2.1 |
| Plasticidade instável | pesos divergem | clip em `W`, `λ` mínimo não-nulo |
| Orçamento de busca insuficiente | fitness estagnado em todas condições | aumentar gerações antes de concluir qualquer coisa |

**Critério de parada:** se P1 e P3 falharem juntos com orçamento adequado, a tese está refutada. Documentar em `docs/05-achados.md` e encerrar a linha — não insistir (mesma regra da T1 na SPEC).

---

## 10. Ordem de execução

1. **Reproduzir `G` numericamente** — simular os regimes do exp08 com EMA fixa e verificar que o MSE bate com `P(K)`. Se não bater, a fórmula está errada e nada mais importa. *Custo: minutos.*
2. **Ablação estática** — população sem evolução, `m` fixo em vários níveis, medir ganho contra o `G` previsto. Isola arquitetura de evolução.
3. **Evolução em B (controle)** — confirmar P2 e P3-colapso antes de gastar tempo em A.
4. **Evolução em A** — o experimento principal, 5 sementes.
5. **M6 (clones)** — só depois de A dar sinal positivo.

O passo 1 é inegociável: valida a base teórica com custo desprezível antes de qualquer GPU.

---

## 11. O que este experimento NÃO decide

- Não valida a célula **HLC** — isso é a tarefa T1 da SPEC, com BPTT.
- Não generaliza para percepção de alta dimensão (§4 de `docs/04`).
- Não testa os cinco canais moduladores, apenas `gain` e `lr`. Os outros três (`plast_thr`, `sens_rec`, `discount`) ficam fixos para não confundir atribuição de efeito.
- Não é modelo de neurociência: as atribuições hormonais são caricatura útil (ressalva em `docs/03` §8).
