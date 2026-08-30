# Osciladores de 2ª Ordem — Correção ao Banco de τ

**Status:** este documento **corrige uma suposição implícita no `docs/01`**, que trata o banco de τ log-espaçados como solução universal. Ele não é.

---

## 1. A limitação descoberta

```
1ª ordem:  dh/dt = −h/τ + x           UM estado  → só decai ao equilíbrio
2ª ordem:  dv/dt = −γ·v − ω²·h + x
           dh/dt = v                  DOIS estados → OSCILA
```

**Medido** (impulso, 30 s de simulação):

```
EMA (1ª ordem, τ=2):        1 cruzamento do zero
oscilador (2ª ordem):      30 cruzamentos
```

> Um integrador com vazamento **nunca sobe sozinho**. Para produzir pico-vale-pico é preciso segunda ordem — um pêndulo, não um balde furado.

**Mapeamento físico:**
```
h    = posição            ω²·h = força restauradora (a mola)
v    = velocidade         γ    = atrito
```

É `F = m·a` dentro do neurônio.

---

## 2. Memória: onde o oscilador ganha

```
sistema                              informação >1 % do pico até
EMA τ=2                                      9,3 s
EMA τ=10                                    30,0 s
oscilador γ=0,05 (pouco atrito)             30,0 s
oscilador γ=0,005                           30,0 s   (teto do teste)
```

O oscilador guarda informação na **fase**, não na amplitude decaindo. Ataca diretamente a limitação apontada em `docs/09`: memória exponencial some rápido; memória oscilatória persiste.

---

## 3. Comparação medida: quando usar cada um

Banco de 12 EMAs (τ log-espaçados) vs banco de 12 osciladores (ω log-espaçados), previsão a 12 passos:

| sinal | banco EMA | banco OSC | vencedor |
|---|---|---|---|
| periódico (3 senoides) | **35,20 %** | 31,40 % | EMA |
| **periódico + ruído** | 27,33 % | **38,40 %** | **OSC (+11 pp)** |
| AR(1) aperiódico | **7,38 %** | −255,50 % | EMA (desastre do OSC) |
| caótico | 31,34 % | 31,27 % | empate |

**Interpretação:**

```
EMA / 1ª ordem     →  PASSA-BAIXAS   →  tendência, integração, sinal aperiódico
OSCILADOR / 2ª     →  PASSA-BANDA    →  ritmo, periódico em ruído, memória longa
```

O oscilador é **ressonante**: só responde forte na frequência dele e rejeita ruído fora da banda. Por isso ganha em sinal periódico enterrado em ruído.

O −255 % é igualmente informativo: **oscilador aplicado a sinal aperiódico é ativamente prejudicial** — impõe estrutura que não existe nos dados.

---

## 4. Seção de Poincaré — informação nos picos

Amostrar um fluxo contínuo nos **eventos** (cada pico) produz um sinal discreto. Técnica formal, não improviso.

Teste: mensagem `[0,3 · 0,9 · 0,5 · 0,7 · 0,2 · 0,8]` injetada num oscilador; amplitudes dos picos:

```
[0,093 0,087 0,082 0,078 | 0,351 0,331 0,311 0,293 | 0,431 0,406 0,382 0,360]
 └─ decaimento suave ──┘   └─ salto: info nova ──┘   └─ salto ─────────────┘
```

A sequência carrega a mensagem comprimida — 28 picos para 6 símbolos. A relação entre um pico e o próximo é o **mapa de retorno**, objeto central na análise de sistemas caóticos.

---

## 5. Proposta: banco misto

```
banco híbrido:
  N integradores (τ log-espaçados)  →  nível, tendência, acumulação
  M osciladores  (ω log-espaçados)  →  ritmo, fase, coordenação
```

Precedente: **coRNN** (Rusch & Mishra, *Coupled Oscillatory RNN*) — rede de 2ª ordem que resolve gradiente explodindo/desvanecendo porque osciladores não decaem.

Implicação para `docs/08` §5: metade das bandas cerebrais (as oscilatórias) provavelmente é melhor modelada como **ressonadores**, não como integradores com vazamento.

---

## 6. Validação aplicada: controle de semáforos

Malha 4×4, 16 cruzamentos, custo de troca de fase (amarelo) = 2 passos, 2500 passos, 3 seeds.

**Demanda 0,40:**

| controlador | espera média | trocas/passo | pico de fila | vs fixo |
|---|---|---|---|---|
| ciclo fixo | 32,1 | 1,14 | 59 | — |
| guloso (fila instantânea) | 40,4 | 2,62 | 72 | −26 % |
| guloso + EMA | 55,3 | 1,90 | 87 | −72 % |
| **híbrido (osc + banco EMA)** | **20,7** | 2,53 | **43** | **+36 %** |

**Demanda 0,55:**

| controlador | espera média | pico | vs fixo |
|---|---|---|---|
| ciclo fixo | 45,6 | 75 | — |
| guloso | 45,8 | 74 | −1 % |
| **híbrido** | **29,2** | **50** | **+36 %** |

### 6.1 Por que funciona

O problema tem **duas dinâmicas simultâneas**:

```
RITMO      ciclo verde/vermelho, coordenação entre cruzamentos  →  OSCILADOR
ACÚMULO    filas crescendo e drenando                           →  INTEGRADOR (EMA)
```

Nenhum sozinho resolve:
- só oscilador → ritmo bom, zero adaptação à demanda
- só guloso → adapta, mas troca demais e paga amarelo

Regra do híbrido:

```
decisão = sinal( sin(θ_i)  +  ganho · tanh((pressão_EW − pressão_NS)/4) )
                  └ ritmo ┘         └──── pressão acumulada ────────────┘
```

Com acoplamento de Kuramoto entre vizinhos (onda verde):

```
dθ_i/dt = ω + K · Σ_j sin(θ_j − θ_i − δ_ij)
```

### 6.2 O genoma evoluído

Evolução simples (24 indivíduos, 25 gerações) sobre 10 parâmetros:

```
demanda 0,40:  período=12,6  K=0,31  desloc=0,48  τ=(2,3 · 10,5 · 65,2)  ganho=0,49
demanda 0,55:  período=13,1  K=0,77  desloc=0,49  τ=(1,6 · 15,4 · 23,1)  ganho=0,26
```

**A evolução escolheu três escalas de tempo distintas sem instrução** — um τ curto para reagir, dois longos para tendência. Confirma o princípio de `docs/01` num domínio aplicado.

Sob demanda maior ela **aumentou o acoplamento K** (0,31 → 0,77) e **reduziu o ganho** (0,49 → 0,26): mais coordenação, menos reatividade. Em congestionamento, ritmo estável vale mais que responder a cada fila.

### 6.3 O detalhe que inverteu o resultado

Sem custo de troca de fase, o guloso vencia. **Com o custo (2 passos de amarelo), ele passa a perder até do ciclo fixo** (−26 %).

> Modelar o custo real da ação mudou completamente qual controlador vence. Um experimento sem esse custo teria produzido a conclusão oposta.

---

## 7. Ressalvas

- Simulação de tráfego simplificada: sem conversões, sem rotas heterogêneas, sem pelotões, capacidade fixa por fase.
- O guloso testado é ingênuo; controladores reais (max-pressure, SCATS) têm histerese e tempo mínimo adaptativo, e seriam baselines mais duros.
- Parâmetros do híbrido evoluídos **na mesma demanda em que foram testados**. Falta testar generalização.
- 3 seeds está abaixo do invariante I4 (≥5). Repetir antes de tratar os 36 % como definitivos.
- O teste EMA vs oscilador (§3) usou 4 sinais sintéticos e um horizonte. Não generaliza automaticamente.
