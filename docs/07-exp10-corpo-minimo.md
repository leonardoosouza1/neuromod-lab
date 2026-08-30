# EXP10 — Corpo Mínimo: Neuromodulação Interoceptiva Evoluída

**Documento de projeto.** Tese, corpo, fórmulas, cálculos trabalhados, plano PyTorch/GPU e protocolo de falsificação.

**Pré-requisitos:** `docs/05-achados.md` (o que já foi refutado), `docs/03-neuromodulacao.md` (a segunda camada), `docs/06` (a fórmula do ganho `G`).

---

## 1. A tese

> O corpo não é periferia do cérebro — é a **fonte** dos sinais que modulam o cérebro. Num agente com interocepção, os gatilhos neuromoduladores não precisam ser projetados: eles emergem das variáveis fisiológicas, cada uma com sua constante de tempo. E como algumas dessas variáveis são lentas e ocultas, o critério `G` prevê que a modulação **paga** — coisa que não acontecia nos ambientes desencarnados dos exp03 e exp04.

### 1.1 A lacuna exata

| Trabalho | Evolui corpo | Interocepção → recompensa | Evolui modulador |
|---|---|---|---|
| DERL (Gupta et al., Nat. Comm. 2021) | ✅ | ❌ | ❌ |
| Homeostatic RL (Keramati & Gutkin, eLife 2014) | ❌ | ✅ | ❌ |
| exp09 (`docs/06`) | ❌ | ❌ | ✅ |
| **EXP10 (este)** | ❌ (corpo fixo) | ✅ | ✅ |

Corpo fixo é escolha deliberada: evoluir morfologia junto multiplicaria o custo e confundiria a atribuição de efeito. Morfologia entra só depois, se a hipótese central sobreviver.

---

## 2. O corpo mínimo

Não um bicho articulado. Um agente 2D com **quatro variáveis interoceptivas**, cada uma com constante de tempo física distinta.

### 2.1 Variáveis de estado interno

| Variável | Símbolo | τ (passos) | ρ = e^(−1/τ) | Setpoint `s*` | Observável? |
|---|---|---|---|---|---|
| Energia (glicogênio) | `E` | 200 | 0,99501 | 1,00 | sim |
| Temperatura corporal | `T` | 60 | 0,98347 | 37,0 | sim, com atraso |
| Fadiga (esforço) | `F` | 30 | 0,96722 | 0,00 | sim |
| Dano acumulado | `Dm` | 2000 | 0,99950 | 0,00 | **oculto** |

**Por que essas quatro:** cobrem quase duas ordens de magnitude de τ (30 → 2000), o que garante que o banco de neurônios precise de τ diversos. Dano é oculto de propósito — é a variável lenta que só se infere pela história, satisfazendo a condição 2 do §7 de `docs/02`.

### 2.2 Dinâmica do corpo

```
E[t+1]  = E  − c_base − c_mov·v²        + ganho_comida
T[t+1]  = T  + (T_amb − T)/τ_T + κ·v²   (esforço aquece)
F[t+1]  = F  + v² − F/τ_F
Dm[t+1] = Dm + dano_evento − Dm/τ_Dm    (cicatriza devagar)
```

`T_amb` é o **regime oculto** (ciclo dia/noite). O agente sente `T`, não `T_amb`.

### 2.3 Ações

| Ação | Efeito |
|---|---|
| mover(v, θ) | custa `c_mov·v²` de energia, aquece, fatiga |
| comer | só se sobre comida; `+ganho_comida` |
| descansar | `v = 0`; fadiga e temperatura caem mais rápido |
| abrigar | reduz acoplamento com `T_amb` |

---

## 3. Recompensa homeostática — não inventar função de reward

Seguindo Keramati & Gutkin: recompensa é **redução de drive**.

```
D(s) = ‖s − s*‖_w = √( Σ_i w_i·(s_i − s*_i)² )        drive
r_{t+1} = β·( D_t − D_{t+1} )                          recompensa
```

Pesos usados: `w = [1,0 (E), 0,35 (T), 0,6 (F), 1,4 (Dm)]`. Dano pesa mais porque é irreversível na escala do episódio.

### 3.1 Exemplo numérico trabalhado

```
setpoint s*        = [1,00  37,0  0,00  0,00]

estado t0          = [0,55  38,4  0,70  0,10]   →  D₀ = 1,0938
estado t1 (comeu)  = [0,78  38,0  0,55  0,10]   →  D₁ = 0,7706
                                    r = D₀ − D₁ =  +0,3232   ✅ recompensa

estado t1' (fugiu) = [0,50  39,5  0,85  0,25]   →  D₁' = 1,7200
                                    r' = D₀ − D₁' = −0,6262  ❌ punição
```

**A lógica que isso produz sozinha:** fugir de predador é *punido no curto prazo* (gasta energia, aquece, fatiga, pode ferir). O agente só aprende a fugir porque **não fugir custa mais adiante** — o dano tem τ = 2000, então uma mordida penaliza o drive por milhares de passos. É a estrutura temporal do corpo que torna a fuga racional, não uma recompensa artesanal dizendo "fugir é bom".

Isso é o principal ganho de projeto: **você para de desenhar reward shaping e passa a desenhar fisiologia.**

---

## 4. Por que a modulação deve pagar aqui — `G` calculado

Aplicando a fórmula de `docs/06` §3 aos regimes ocultos deste corpo:

| Regime oculto | G | τ* por regime | Veredito |
|---|---|---|---|
| predador ativo vs ausente (ruído no sensor de ameaça) | **25,6 %** | [1,1 · 4,2] | **vale** |
| dia/noite (ruído térmico 25×) | **19,1 %** | [1,4 · 4,7] | **vale** |
| estação: comida abundante vs escassa | 12,9 % | [5,0 · 2,1] | marginal |
| dano cicatrizando vs infeccionando | 9,4 % | [7,6 · 3,3] | marginal |
| **CONTROLE: mundo estacionário** | **0,0 %** | [3,8 · 3,8] | não vale |

**Decisão de projeto:** o ambiente principal usa os dois regimes de `G` alto (predador + dia/noite). O controle negativo remove ambos.

### 4.1 Calibração de `a₁` a partir de `G`

Faixa de `τ*` combinada: 1,1 → 4,7, razão 4,3. Como `τ_ef = τ₀/(1 + a₁·m)`:

```
a₁·m_máx = 4,3 − 1 = 3,3      com m_máx ≈ 1  →  a₁ ≈ 3,3
```

**O hiperparâmetro sai da fórmula, não de tentativa.** Compare com `docs/06` §5.3, onde o mesmo cálculo deu `a₁ ≈ 2,8` para outro ambiente — o valor é específico do mundo.

---

## 5. Dimensionamento dos neurônios sensoriais

Usando `t_disparo = −τ·ln(1 − θ/(u·τ))` de `docs/04`.

### 5.1 Exemplo: o neurônio de dor

Requisito: **disparar após 3 s de dor contínua, ignorar toques breves.**

```
escolhe τ = 8,0 s
θ = u·τ·(1 − e^(−t/τ)) = 1·8·(1 − e^(−3/8)) = 2,5017
```

Verificação em toda a faixa:

```
toque breve     t=0,4 s  →  h=0,390   ignora   ✅
esbarrão        t=1,0 s  →  h=0,940   ignora   ✅
dor sustentada  t=3,0 s  →  h=2,502   DISPARA  ✅
dor longa       t=6,0 s  →  h=4,221   DISPARA  ✅

piso de sensibilidade: u_min = θ/τ = 0,3127
→ estímulo com intensidade abaixo de 0,31 NUNCA dispara, por mais que dure
```

**Três requisitos comportamentais → dois números, sem tuning.** O mesmo procedimento fixa os limiares de fome, exaustão e frio.

---

## 6. Os gatilhos moduladores — o que o corpo alimenta

Aqui está o coração da tese: **os gatilhos não são projetados, são funções evoluídas da interocepção.**

| Canal | Gatilho φ (candidatos) | Efeito no núcleo | Lógica biológica |
|---|---|---|---|
| `gain` (NA) | ameaça súbita, ΔDm | `τ ← τ/(1+a₁m)`, `β ← β₀(1+a₂m)` | luta-ou-fuga: acelera o tempo interno |
| `lr` (DA) | `D_t − D_{t+1}` (redução de drive) | `η ← η·m` | consolida o que reduziu o drive |
| `plast_thr` (cortisol) | drive médio de longo prazo | `λ ← λ·(1+m)` | privação crônica acelera esquecimento |
| `sens_rec` (ACh) | variância do sensor | `h ← f(m·W_in x + (1−m)·W_rec h)` | ruído alto → confiar na memória |
| `discount` (5-HT) | reservas de energia | `γ ← γ₀·σ(m)` | com fome, horizonte encurta |

O genoma evolui `w_g` (quais sinais interoceptivos alimentam cada canal) e as constantes de acoplamento. **Dois indivíduos com genoma inicial idêntico, em histórias diferentes, desenvolvem perfis diferentes** — porque `φ` depende do estado interno, que depende da história vivida.

### 6.1 Exemplo de comportamento previsto

```
estado: E=0,25 (faminto)  Dm=0,30 (ferido)  predador visível

→ m_discount alto (reservas baixas)  → γ cai → horizonte curto → arrisca
→ m_gain alto (ameaça)               → τ cai → reage rápido, memória curta
→ m_cortisol alto (drive crônico)    → λ sobe → esquece estratégias antigas

resultado: comportamento IMPULSIVO E ARRISCADO — não programado,
           consequência de três canais respondendo à fisiologia
```

Um agente saciado e ileso, no mesmo cenário, teria `γ` alto e `τ` longo: rodearia, esperaria, planejaria. **Mesmos pesos, comportamento oposto.**

---

## 7. Plano de implementação (PyTorch / GPU)

### 7.1 Vetorização

A população é a dimensão de batch. O corpo é aritmética elementar — barato.

```
s_corpo   (P, 4)        estado interno
pos, vel  (P, 2)        cinemática
h         (P, N)        núcleo neural
m, R      (P, 5)        moduladores e reservas
W_rec     (P, N, N)     pesos individuais
e         (P, N, N)     traços de elegibilidade
```

Com P = 4096, N = 16: o corpo custa ~5 % do tempo; o núcleo domina via `einsum` em `(P,N,N)`.

### 7.2 Laço

```
para cada geração:
    inicializa corpo, h, m, R, e
    para t em 1..T:
        s_ext  = sensores externos (comida, predador, luz)
        φ      = features(s_corpo, h, ΔD)         # interocepção
        m, R   = passo_reserva(R, m, σ(w_g·φ))    # etapa 2 (lenta)
        τ_ef   = τ₀/(1 + a₁·m_gain)
        S      = σ((1 + a₂·m_gain)·(W_in·[s_ext,s_corpo] + W_rec·h + b))
        h      = (h + S·A)/(1 + 1/τ_ef + S)       # Euler implícito (I2)
        ação   = readout(h)
        s_corpo, s_ext = passo_mundo(ação)         # física do corpo
        D_novo = drive(s_corpo)
        r      = β·(D_ant − D_novo)                # recompensa homeostática
        e      = e − e/τ_e + outer(h, h_ant)
        W     += η(m_lr)·e·r − λ(m_cort)·W         # três fatores, no_grad
        vivo   = (E > 0) & (Dm < Dm_letal) & (|T−37| < ΔT_letal)
    seleção proporcional a tempo de vida + mutação
```

### 7.3 Decisões técnicas

| Decisão | Escolha | Motivo |
|---|---|---|
| Corpo | **fixo**, não evoluído | isola o efeito do modulador (evitar confundir com DERL) |
| Integração | Euler implícito | `leak` grande e variável (I2) |
| Otimização | evolução + três fatores | plasticidade não-diferenciável; é o objeto de estudo |
| Morte | sim, por E, Dm ou T | sem morte, homeostase vira decoração |
| Reprodução | proporcional a tempo de vida | seleção precisa de pressão real |
| Precisão | `float32` | `τ_Dm = 2000` envolve diferenças pequenas |
| Custo do modulador | `κ_m·Σm` explícito no drive | senão `m` cresce sem limite |

**Sobre a morte:** é o que faz a homeostase importar. Sem limiar letal, desviar do setpoint é só um custo escalar, e o agente aprende a ignorá-lo. Com morte, o drive vira restrição dura.

---

## 8. Métricas

| # | Métrica | Como | Testa |
|---|---|---|---|
| M1 | ganho medido vs `G` previsto (25,6 %) | fitness(modulado)/fitness(ablado) | **a fórmula de `docs/06`** |
| M2 | variância do genoma modulador por geração | `var(w_g, a₁, a₂)` | a tese central |
| M3 | info mútua entre `m_gain` e presença de predador | MI estimada | o gatilho aprendeu a inferir? |
| M4 | correlação `m_discount` × energia | Pearson | o horizonte encurta com fome? |
| M5 | lesão de cada canal | zera `m_i`, mede perda | quanto cada canal vale |
| M6 | clones em histórias diferentes | divergência de trajetória de `m` | individualidade emergente |
| M7 | espectro de `τ_ef` sob `m` vivo | `analysis.espectro_tau` | cobre [1,1 · 4,7]? |

---

## 9. Predições registradas ANTES da execução

| # | Predição | Refuta se |
|---|---|---|
| P1 | Ambiente principal: ganho entre 8 % e 25,6 % | ganho ≈ 0, ou > 25,6 % (violaria o teto teórico) |
| P2 | Controle estacionário: ganho ≤ 2 % | ganho significativo sem regime oculto |
| P3 | M2 cresce no principal, colapsa no controle | cresce nos dois → deriva, não seleção |
| P4 | M4 negativo: energia baixa → `γ` baixo | sem correlação → o canal não achou função |
| P5 | M7 cobre a faixa [1,1 · 4,7] prevista | faixa descolada → calibração de `a₁` errada |
| P6 | Agentes com dano oculto alto exibem mais `m_cortisol` | sem relação → interocepção lenta não foi usada |
| P7 | M6: clones divergem no principal, não no controle | divergência igual → ruído |

**P1 é o teste mais forte.** Se o ganho exceder `G`, a derivação de `docs/06` §3 está errada.

---

## 10. Ordem de execução

1. **Validar `G` numericamente** — simular os regimes com EMA fixa, conferir contra `P(K)`. *Minutos. Inegociável.*
2. **Corpo sem cérebro** — política aleatória, verificar que o agente morre e que o drive se comporta. Sanidade da física.
3. **Cérebro sem modulador** — evoluir só o núcleo. Este é o **baseline** de M1.
4. **Controle estacionário com modulador** — confirmar P2 e P3-colapso antes de gastar no principal.
5. **Ambiente principal** — 5 sementes.
6. **M6 (clones)** — só se 5 der sinal positivo.

---

## 11. Riscos

| Risco | Sintoma | Mitigação |
|---|---|---|
| Reward hacking do simulador | fitness alto, comportamento absurdo | inspecionar trajetórias, não só números |
| Modulador vira constante | M3 ≈ 0 com fitness alto | é reparametrização — teorema `docs/06` §2.1 |
| Extinção precoce | população morre na geração 1 | `Dm_letal` generoso no início, apertar depois |
| Custo do episódio | GPU ociosa esperando passos sequenciais | aumentar P antes de aumentar T |
| Deriva confundida com seleção | M2 cresce nos dois ambientes | o controle existe para isso |

**Critério de parada:** se P1 e P3 falharem juntos com orçamento adequado, a tese está refutada. Documentar em `docs/05` e encerrar — mesma regra da T1 na SPEC.

---

## 12. O que este experimento NÃO decide

- Não valida a **HLC** (tarefa T1 da SPEC, exige BPTT).
- Não evolui morfologia — isso é o DERL, e seria um experimento separado.
- Não testa corpo articulado nem física de contato; o *reality gap* não se aplica porque não há alvo real.
- As atribuições hormonais seguem sendo caricatura útil (`docs/03` §8).

---

## 13. Referências

| Trabalho | Uso aqui |
|---|---|
| Gupta, Savarese, Ganguli, Fei-Fei — *Embodied Intelligence via Learning and Evolution*, Nature Communications 12:5721 (2021); arXiv:2102.02202; código: `github.com/agrimgupta92/derl` | estrutura de dois laços; efeito Baldwin morfológico; escala de referência |
| Keramati & Gutkin — *A Reinforcement Learning Theory for Homeostatic Regulation*, NIPS 2011; e eLife 3:e04811 (2014) | fórmula da recompensa homeostática (§3) |
| Man & Damasio — *Homeostasis and soft robotics in the design of feeling machines*, Nature Machine Intelligence 1:446 (2019) | argumento conceitual de corpo como pré-requisito |
| Karl Sims — *Evolving Virtual Creatures*, SIGGRAPH 1994 | trabalho fundador da linha |

*Verificar as publicações antes de citar em trabalho formal.*
