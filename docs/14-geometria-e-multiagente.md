# Geometria da Memória e Sistemas Multi-Agente

**Documento de resultados.** Duas linhas: (1) o que uma trajetória em 3D pode reter, (2) o que acontece quando carros e semáforos são ambos agentes.

**Contém dois artefatos metodológicos corrigidos** — ler §1.1 e §3.1 antes de confiar em qualquer número.

---

## 1. Geometria: cone, cilindro e espiral logarítmica

Uma hélice em 3D:

```
x(t) = r(t)·cos(ωt)     y(t) = r(t)·sin(ωt)     z(t) = t
```

A projeção 2D (x contra t) é **exatamente o oscilador amortecido**: picos e vales com envelope decaindo. Em 3D fica visível que decaimento e rotação são **eixos independentes**.

### 1.1 ⚠️ Artefato corrigido

O primeiro teste deu 100 % de recuperação para o decaimento puro em todos os horizontes. **Isso era artefato:** um readout linear desfaz qualquer escala, então sem um **piso de ruído absoluto** o teste não mede nada. E a espiral deu ~60 % porque usei regressão linear para decodificar uma fase que dá a volta em ±π.

Correção: piso de ruído fixo (1e−3, como um sensor real) e decodificação por `arctan2`.

### 1.2 Resultado corrigido

| após | raio | decaimento | **cone (afina)** | **cilindro** |
|---|---|---|---|---|
| 20 s | 8,2e−02 | 100,0 % | 100,0 % | 100,0 % |
| 30 s | 2,4e−02 | 99,5 % | 99,9 % | 100,0 % |
| 50 s | 1,9e−03 | 29,9 % | 87,9 % | **100,0 %** |
| 80 s | 4,5e−05 | 0,0 % | **0,0 %** | **100,0 %** |

> **O cone não preserva.** Quando o raio cai abaixo do piso de ruído, o ângulo morre junto — porque `x` e `y` são **ambos** multiplicados por `r`. Não se lê a fase de um ponto que virou ruído.
>
> Quem retém do começo ao fim é o **cilindro**: raio constante, ou seja, oscilador sem atrito. A fase é um relógio que não para.

### 1.3 Capacidade depende do raio, não do tempo

| raio | ruído | SNR | níveis distinguíveis | bits |
|---|---|---|---|---|
| 1,000 | 1e−3 | 1000 | 3010 | 11,6 |
| 0,100 | 1e−3 | 100 | 302 | 8,2 |
| 0,010 | 1e−3 | 10 | 30 | 4,9 |
| 0,001 | 1e−3 | 1 | 3 | 1,3 |

**Manter o raio grande é manter a capacidade. Afinar é perder.**

### 1.4 Para que serve a espiral, então: cobrir escalas

Espiral logarítmica `r = e^(−aθ)`. Em coordenadas log-polares é uma **reta** — auto-similar.

| volta | raio início | raio fim | razão |
|---|---|---|---|
| 1 | 1,0000 | 0,4710 | 2,1230 |
| 2 | 0,4703 | 0,2215 | 2,1230 |
| 3 | 0,2212 | 0,1042 | 2,1230 |
| 4 | 0,1040 | 0,0490 | 2,1230 |

**A razão é constante em toda volta.** Cada volta cobre uma faixa de escala — é o banco de τ log-espaçado desenhado como **uma curva contínua** em vez de N unidades separadas.

### 1.5 Testado como arquitetura

Osciladores com ω e γ em progressão geométrica (γ ∝ ω → auto-similaridade), reconstruindo 150 passos de passado:

| N | banco EMA | **espiral auto-similar** |
|---|---|---|
| 8 | **50,2 %** | 23,3 % |
| 16 | 52,3 % | 53,4 % |
| 32 | 54,1 % | **66,9 %** |

Com poucas unidades a espiral perde; a partir de 32 abre 12 pontos e continua subindo, enquanto o EMA satura em ~54 % — o mesmo teto de `docs/12` §1.2.

### 1.6 Síntese geométrica

```
CONE (broca)          →  perde tudo quando a ponta entra no ruído
CILINDRO              →  retém indefinidamente (fase não decai)
ESPIRAL LOGARÍTMICA   →  não retém um valor, mas COBRE escalas
```

**Um objeto só não faz as duas coisas.** Reter exige raio grande; cobrir escalas exige raio decrescente.

**Arquitetura recomendada:** osciladores de **raio constante** em **frequências log-espaçadas**. É a broca vista de topo — as voltas em espiral, mas cada anel mantendo sua espessura.

---

## 2. Multi-agente: carros e semáforos como agentes

Malha 5×5 em toro (sem bordas), 300 carros com origem-destino próprios, capacidade 1 por fase. **Carros escolhem rota; semáforos escolhem fase. Ambos veem o mapa e o estado do outro.**

Políticas:

```
CARRO  egoísta     → escolhe a direção que está com verde agora
       cooperativo → evita o próximo cruzamento mais cheio
       sabotador   → vai justamente para o mais lotado

SEMÁFORO egoísta     → verde para a própria pressão maior
         cooperativo → pressão própria MENOS congestionamento a jusante
         sabotador   → verde para a direção vazia (mata a fila)
         fixo        → ciclo cego
```

### 2.1 ⚠️ Artefato corrigido

A primeira medição usou **tempo médio de viagem dos que chegaram**, e o semáforo sabotador apareceu como *melhor* (8,2 contra 39,6). Era **viés de sobrevivência**: com vazão de 0,04, quase ninguém chegava, e os poucos que chegavam eram os de viagem curta.

Correção: métrica primária = **vazão**; secundária = **idade média de todos os carros**, incluindo os presos.

### 2.2 Matriz de cooperação (métricas corretas)

| carros | semáforos | vazão | idade | vs base |
|---|---|---|---|---|
| egoísta | fixo | 6,33 | 46,4 | — |
| egoísta | egoísta | 7,27 | 39,4 | +15 % |
| egoísta | cooperativo | 7,21 | 38,6 | +14 % |
| **cooperativo** | **egoísta** | **7,59** | **29,7** | **+20 %** |
| cooperativo | cooperativo | 7,46 | 30,4 | +18 % |
| cooperativo | fixo | 6,40 | 37,8 | +1 % |
| sabotador | egoísta | 5,27 | 75,3 | −17 % |
| sabotador | fixo | 4,17 | 126,2 | −34 % |
| qualquer | **sabotador** | **0,04** | 1331 | **−99 %** |

**Amplitude total: 200×** entre o melhor e o pior arranjo.

Três leituras:

1. **A camada de infraestrutura domina.** Trocar o semáforo de fixo para adaptativo dá +15 %; trocar os carros de egoísta para cooperativo dá +1 % (com semáforo fixo). O semáforo tem alavanca maior.
2. **Cooperação dos carros só rende quando o semáforo é adaptativo** (+1 % com fixo, +4 % com egoísta). Sem um parceiro que responda, cooperar não adianta.
3. **Semáforo cooperativo não bateu o egoísta** (7,46 vs 7,59). Minha política "cooperativa" penaliza empurrar carro para rua cheia, e isso **atrasa demais** quem já está parado. Cooperação mal especificada é pior que egoísmo simples.

### 2.3 Fragilidade: quantos sabotadores derrubam?

**Carros sabotadores** (o sistema é robusto):

| % sabotadores | vazão | perda |
|---|---|---|
| 0 % | 7,46 | — |
| 25 % | 7,38 | 1 % |
| 50 % | 7,19 | 4 % |
| 75 % | 6,57 | 12 % |
| 100 % | 5,07 | 32 % |

**Semáforos sabotadores** (o sistema é frágil):

| % sabotadores | vazão | perda |
|---|---|---|
| 0 % | 7,46 | — |
| **4 %** (1 de 25) | 6,50 | **13 %** |
| **8 %** (2 de 25) | 3,51 | **53 %** |
| 16 % | 1,66 | 78 % |
| 32 % | 0,66 | 91 % |

> **Assimetria brutal: 2 semáforos de 25 (8 %) cortam a vazão pela metade. 50 % dos carros custam apenas 4 %.**
>
> Motivo estrutural: um carro sabotador prejudica principalmente **a si mesmo** — ele pega a rota pior. Um semáforo sabotador bloqueia **todos** que passam por ele, e o bloqueio se propaga rio acima.

**Regra de projeto:** proteja os nós, não os agentes. O ponto de falha está na infraestrutura compartilhada, não na população.

### 2.4 Teste inverso: cooperação compensa infraestrutura ruim?

| % semáforos sabotadores | carros egoístas | carros cooperativos | ganho |
|---|---|---|---|
| 0 % | 7,21 | 7,46 | +3 % |
| **8 %** | 2,87 | 3,51 | **+22 %** |
| 20 % | 0,90 | 0,93 | +4 % |
| 40 % | 0,30 | 0,32 | +8 % |

**A cooperação dos carros vale mais quando a infraestrutura está parcialmente quebrada** (+22 % a 8 % de sabotagem) do que quando está boa (+3 %). Faz sentido: com tudo funcionando, não há o que rotear em volta; com falha total, não há rota que salve.

> **Adaptação tem um regime ótimo de utilidade: nem ambiente perfeito, nem ambiente destruído.** Isso é o mesmo U invertido que apareceu em ganho, inibição, λ, η e atrito — agora na dimensão "quanto o ambiente está quebrado".

---

## 3. Achados acionáveis

| # | Achado | Ação |
|---|---|---|
| G1 | Cone não retém: raio decai → fase morre junto | usar raio constante para memória |
| G2 | Capacidade ∝ SNR (raio/ruído), não ∝ tempo | dimensionar pelo piso de ruído |
| G3 | Espiral log é auto-similar: razão constante por volta | uma curva cobre o que N unidades cobriam |
| G4 | Osciladores auto-similares superam EMA a partir de N=32 | usar em memória longa |
| M1 | Infraestrutura tem alavanca maior que agentes (+15 % vs +1 %) | investir no nó antes do agente |
| M2 | 8 % de nós sabotados = −53 %; 50 % de agentes = −4 % | proteger nós, não população |
| M3 | Cooperação mal especificada perde para egoísmo simples | validar a política cooperativa contra a egoísta |
| M4 | Cooperação rende mais em ambiente parcialmente quebrado | U invertido na dimensão "falha do ambiente" |

---

## 4. Ressalvas

- **Dois artefatos foram encontrados e corrigidos nesta sessão** (§1.1 e §3.1). Ambos produziam a conclusão oposta à correta. Qualquer número anterior a essas correções deve ser descartado.
- Simulação em toro, sem bordas nem geografia real; capacidade uniforme; sem pelotões, sem semáforos com mais de 2 fases.
- 3 seeds por célula — abaixo do invariante I4 (≥5). Diferenças menores que ~10 % devem ser tratadas como empate; em particular, cooperativo vs egoísta nos semáforos (7,46 vs 7,59) está dentro do ruído.
- As políticas "cooperativa" foram escritas à mão, não otimizadas. O resultado M3 diz que *a minha* política cooperativa perdeu, não que cooperação em geral perca.
- O sabotador é o pior caso adversarial que consegui especificar simplesmente; um adversário otimizado seria mais destrutivo.
- O teste de capacidade da espiral (§1.5) usa um sinal sintético com 3 escalas. Não generaliza automaticamente.
