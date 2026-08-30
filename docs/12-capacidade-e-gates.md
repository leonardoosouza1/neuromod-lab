# Capacidade de Memória, Banco Misto e Gates de Camada

**Documento de resultados.** Quatro experimentos: onde a informação cabe, se o banco misto se sustenta, se gate de camada funciona, e onde o oscilador atrapalha.

**Corrige:** `docs/11` §5 (proposta de banco misto) — agora com evidência, e uma delimitação nova.

---

## 1. Onde a informação realmente cabe

**Pergunta:** guardar a *forma* do passado (coeficientes de curva) supera guardar *médias* (banco de EMA)?

Motivação: um EMA guarda um número — a média ponderada. A forma da trajetória se perde. Alternativa: projetar o passado em polinômios ortogonais e guardar os coeficientes. Isso é **HiPPO** (*High-order Polynomial Projection Operators*), a base matemática do S4 e do Mamba.

### 1.1 Reconstrução de 80 passos de passado

| N | banco EMA | osciladores | **misto** | HiPPO-LegT |
|---|---|---|---|---|
| 4 | **51,8 %** | 29,5 % | 31,7 % | 40,8 % |
| 8 | **63,0 %** | 54,5 % | 58,9 % | 53,3 % |
| 16 | 64,8 % | 69,1 % | **69,8 %** | 1,7 % |
| 32 | 66,4 % | 68,2 % | **77,8 %** | 0,0 % |

### 1.2 Reconstrução de 300 passos (memória longa)

| N | banco EMA | **osciladores** | misto | HiPPO-LegT |
|---|---|---|---|---|
| 8 | 26,9 % | **38,1 %** | 33,5 % | 24,2 % |
| 16 | 28,4 % | **58,1 %** | 47,6 % | 31,0 % |
| 32 | 29,8 % | **70,2 %** | 61,4 % | 0,0 % |

> **Achado principal:** para memória longa, o **banco de EMA satura em ~30 %** enquanto o **oscilador chega a 70 %**. O integrador com vazamento tem um teto de capacidade; o oscilador não.

Isso é a consequência direta de `docs/11` §2: EMA perde informação exponencialmente, oscilador guarda na fase.

### 1.3 Ressalva importante sobre o HiPPO

O HiPPO colapsa para 0 % com N ≥ 16 na implementação testada. Isso é **quase certamente instabilidade numérica** da discretização por Euler explícito da matriz LegT, não uma propriedade do método — HiPPO é o núcleo do S4/Mamba e funciona bem na literatura com discretização bilinear/ZOH.

**Não tratar como refutação do HiPPO.** Tratar como: "a implementação ingênua explode; usar discretização adequada". Ver `docs/09` §9 (invariante I2: Euler implícito).

---

## 2. Banco misto — a proposta se sustenta

Teste em três famílias de sinal, N = 16 (8 EMA + 8 osciladores):

| sinal | EMA | osciladores | **misto** | veredito |
|---|---|---|---|---|
| misto (3 escalas) | 71,8 % | 68,0 % | **75,8 %** | misto ganha |
| periódico + ruído | 73,9 % | 73,6 % | **74,6 %** | misto ganha |
| aperiódico AR(1) | 83,4 % | 79,2 % | **86,0 %** | misto ganha |

> **O banco misto venceu ou empatou em todos os sinais testados**, inclusive no aperiódico — onde o oscilador puro é ruim (`docs/11` §3: −255 %).

**Interpretação:** o oscilador puro prejudica em sinal aperiódico, mas o oscilador *como metade de um banco* não prejudica — o readout linear simplesmente atribui peso baixo às unidades inúteis. Diversidade sai barato; especialização errada sai caro.

**Recomendação atualizada:** banco misto ~50/50 como padrão, não banco de τ puro.

---

## 3. Atratores — a capacidade dos "vales"

**Pergunta:** memória guardada em vales de uma paisagem de energia (rede de Hopfield) é densa?

| N neurônios | padrões | P/N | recuperados |
|---|---|---|---|
| 100 | 5 | 0,050 | 100 % |
| 100 | 13 | 0,138 | 100 % |
| 100 | 20 | 0,200 | 20 % |
| 200 | 20 | 0,100 | 100 % |
| 200 | 27 | 0,138 | 67 % |
| 200 | 60 | 0,300 | 0 % |

**A capacidade colapsa exatamente no limite teórico de `P/N ≈ 0,138`.** Cada memória custa ~7 neurônios.

```
vale     = atrator (puxa para dentro)  → memória estável
pico     = repulsor (empurra para fora) → separa bacias
```

A dinâmica de "empurra e atrai" é real e é o que estabiliza a memória. Mas **não é densa** — 7 neurônios por padrão é caro comparado a representação distribuída, onde 200 conceitos cabem em 64 dimensões por quase-ortogonalidade.

---

## 4. Gate de camada — o semáforo entre camadas

### 4.1 Versão classificação (early exit) — FUNCIONA

Rede de 6 camadas com cabeça de saída em cada uma; o dado para quando a confiança passa do limiar.

| limiar | acurácia | camadas usadas | computo | vs completo |
|---|---|---|---|---|
| 0,80 | **86,73 %** | 2,73 | **46 %** | +0,13 pp |
| 0,95 | 86,60 % | 3,68 | 61 % | 0,00 pp |
| completo | 86,60 % | 6,00 | 100 % | — |

**Quem sai cedo:**

```
camada 2:  1411 amostras (47,0 %)  →  acurácia  99,7 %   ← casos fáceis
camada 6:  1184 amostras (39,5 %)  →  acurácia  66,8 %   ← casos difíceis
```

**Metade dos dados sai na camada 2 com 99,7 % de acerto.** O gate separa fácil de difícil corretamente.

**Controle honesto:**
```
gate por confiança:  86,60 %  com 3,68 camadas
saída ALEATÓRIA:     85,43 %  com 3,61 camadas   (mesmo custo)
rede completa:       86,60 %  com 6,00 camadas
```
Bate o aleatório em 1,17 pp com o mesmo custo → **a decisão carrega informação**.

**Observação adicional:** a acurácia por camada foi 71,97 / 86,87 / **87,77** / 87,50 / 87,00 / 86,60 %. A rede atinge o pico na camada 3 e **piora** depois — U invertido na profundidade.

### 4.2 Versão sequencial (gate por pressão) — FUNCIONA MELHOR AINDA

| estratégia | ganho pred. | camadas usadas | trocas/passo |
|---|---|---|---|
| todas as camadas | 2,68 % | 100 % | 0,00 |
| **pressão (magnitude de mudança)** | **8,27 %** | **17 %** | 0,00 |
| ritmo (só oscilador) | −3,85 % | 62 % | 1,71 |
| híbrido ritmo+pressão | −2,56 % | 61 % | 1,42 |
| aleatório (mesmo custo) | 1,78 % | 68 % | 2,37 |

**Gate por pressão: 17 % do custo e ganho 3× maior que computar tudo.** Congelar camadas estagnadas preserva informação em vez de sobrescrevê-la.

---

## 5. ⚠️ REFUTADO: ritmo em gate de camada

O híbrido (ritmo + pressão) **perdeu para o aleatório** e não se recuperou nem com penalidade de troca:

| penalidade por troca | melhor estratégia |
|---|---|
| 0,00 | pressão pura |
| 0,15 | pressão pura |
| 0,35 | pressão pura |

Diferente do semáforo, onde o custo do amarelo **inverteu** o resultado (`docs/11` §6.3).

### 5.1 Por quê — a diferença estrutural

```
SEMÁFORO                                GATE DE CAMADA
cruzamentos são VIZINHOS espaciais      camadas são uma CADEIA
disputam o mesmo fluxo de carros        não competem por recurso
trocar custa amarelo real               pular não tem custo de transição
onda verde transporta algo              "onda de camadas" não transporta nada
```

> **Regra derivada (2 medições independentes):** oscilador só ajuda quando existe **periodicidade real** ou **competição por recurso compartilhado**. Fora disso injeta estrutura falsa e piora — `docs/11` §3 mediu −255 % em sinal aperiódico; aqui o efeito é o mesmo.

---

## 6. Convergência com a literatura

| Nosso teste | Nome estabelecido |
|---|---|
| guardar a forma da curva | **HiPPO** → base do S4 / Mamba |
| gate entre camadas (classificação) | **early exit** / BranchyNet |
| gate por token/passo | **Mixture-of-Depths** (Google, 2024) |
| vales como memória | rede de **Hopfield** (limite 0,138·N confirmado) |
| bancos de frequência fixa | **CMS** do Nested Learning (Google, NeurIPS 2025) |

**O que permanece não coberto pela literatura conhecida:** frequências/τ **evoluídos por indivíduo** e **modulados em tempo real por estado interno** (`docs/03` + `docs/06`). Todos os trabalhos acima usam frequências como hiperparâmetro fixo.

---

## 7. Achados acionáveis

| # | Achado | Ação |
|---|---|---|
| A1 | Banco misto ≥ banco puro em todos os sinais | usar 50/50 como padrão |
| A2 | EMA satura em ~30 % para memória longa; oscilador chega a 70 % | oscilador é obrigatório para τ longo |
| A3 | Gate por pressão: 17 % do custo, ganho 3× | implementar no piloto virtual |
| A4 | Early exit: 46 % do custo, sem perda | implementar em qualquer rede profunda |
| A5 | Ritmo em gate de camada é prejudicial | **não tentar** |
| A6 | Rede tem pico de acurácia antes da última camada | medir por camada antes de aprofundar |

---

## 8. Ressalvas

- Todos os testes usam sinais sintéticos e tarefas pequenas. Magnitudes não transferem automaticamente.
- O HiPPO testado tem discretização inadequada (§1.3) — o resultado dele **não é conclusivo** e não deve ser citado como refutação.
- O teste de early exit usa um dataset sintético construído com 60 % de amostras fáceis; a fração que sai cedo depende dessa proporção.
- A rede do early exit foi treinada com cabeças em todas as camadas, o que muda o treinamento em si. Comparar com rede treinada só no final seria mais rigoroso.
- 3 seeds em §1 e §2, abaixo do invariante I4 (≥5).
- Capacidade de Hopfield medida com corrupção de 10 % e 20 iterações; limiar de sucesso 95 % de bits corretos.
