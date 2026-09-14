# CLAUDE.md — instruções para assumir este projeto

Você está assumindo um laboratório de pesquisa sobre **arquiteturas de memória em
agentes com corpo**. Este documento é o briefing. Leia inteiro antes de mexer em código.

---

## 1. O que é este projeto

Investiga uma pergunta: **que estrutura de memória serve para quê?**

Começou em neurônios líquidos (EMA), passou por osciladores, memória diádica,
portas de escrita, e chegou num benchmark aplicado — táxis com corpo, economia e
avarias, competindo num grafo urbano irregular.

O valor acumulado está em **quinze documentos de achados**, metade deles negativos.
A regra do projeto: resultado negativo é resultado, e é documentado com o mesmo
cuidado que o positivo.

---

## 2. Leia nesta ordem

```
docs/CONTEXTO.md        visão geral: o achado central, o que caiu, o que sobreviveu
docs/INDICE-MESTRE.md   tabela validados vs refutados + invariantes I1-I9
docs/05-achados.md      os experimentos medidos
docs/16-poda.md         o achado mais recente (este é o que está quente)
```

Os outros documentos (`01` a `15`) são referência por tema. Abra quando o assunto
aparecer, não antes.

---

## 3. Regras que custaram caro

Estas não são preferências. Cada uma corresponde a horas perdidas.

### 3.1 O portão antes de qualquer bateria

```bash
python src/rodar.py --perito
```

Roda a **mesma política** (pesos à mão, memória zerada) nas cinco arquiteturas.
Elas *têm* que dar resultado idêntico — se são a mesma política, o número é o mesmo.

```
PASSOU: as 5 batem (spread 0.000)
```

Este teste pegou **cinco bugs silenciosos** na migração CPU → GPU:

| Bug | Por que passou despercebido |
|---|---|
| `.mean()` de fatia vazia → NaN | `.abs().max()` retorna 0 com NaN, escondendo o problema |
| Buffer circular com índice absoluto | só quebrava depois do passo 64 |
| Serviço escolhido sem dinheiro pra pagar | consumia o passo sem executar nada: 97% parado |
| `sv` binário sem ponderar necessidade | não sabia decidir *quando* abastecer |
| 1 passageiro em vez de 6 | quase nunca encontrava alguém |

Todos rodavam sem erro e produziam números plausíveis.

### 3.2 Valide o mundo antes da política

Antes de confiar em qualquer evolução, um **perito escrito à mão** precisa bater o
aleatório por margem larga (alvo: 10× ou mais). Se nem ele consegue, o mundo está
inviável e nenhuma busca vai salvar.

Uma bateria inteira foi perdida porque o mundo tinha 0.8 entregas para o perito —
dois bugs (pickup que nunca disparava, perito insistindo no vermelho) faziam o
ambiente parecer impossível.

### 3.3 Valide CADA dimensão que o experimento vai medir

Um experimento sobre decisão de investimento morreu porque a economia tinha
**margem negativa**: o táxi ganhava 105 e gastava 160. Ninguém tinha lucro para
investir. Eu havia validado mobilidade e sobrevivência, nunca o balanço.

### 3.4 Resultado estranho é bug até prova em contrário

Todas as anomalias desta pesquisa foram método, não descoberta. Quando um número
surpreender, o primeiro passo é instrumentar, não teorizar.

### 3.5 Réplicas antes de população

`R=8` (cada genoma avaliado em 8 mundos por cidade) dá fitness com erro 8× menor.
População grande com fitness ruidoso **seleciona sorte**. A variância travou
conclusões durante boa parte da pesquisa.

### 3.6 Amostra pequena mente

Um teste com 2 sementes deu "+55% para a poda". Com 20 sementes, a mesma
comparação deu p=0.053 — não significativo. **Não documente efeito com menos de
10 sementes.**

---

## 4. Como rodar

### Versão numpy (leve, CPU, rápida de iterar)

```bash
python src/poda2.py podar 0      # um modo, uma semente -> /tmp/poda2.jsonl
```

Use para experimentos exploratórios. Um lote de 300 genomas × 60 gerações leva
~4 minutos. `src/taxi_np.py` tem a simulação.

### Versão torch (GPU, escala)

```bash
pip install torch numpy
python src/rodar.py --smoke      # segundos
python src/rodar.py --perito     # o portão — obrigatório
python src/rodar.py --bateria -P 8192 -G 100 -R 8
```

`src/lab.py` tem a simulação vetorizada. Roda igual em CPU, GPU local ou Colab.
`--bateria` executa o portão sozinho e aborta se falhar.

### Dimensionamento de VRAM (medido em T4, 15.6 GB)

```
P=2048   com 8 cidades e R=8  ->  0.4 GB
P=8192                        ->  1.6 GB
P=32768                       ->  6.2 GB
P=57000                       ->  ~11 GB (teto prático)
```

O gargalo **não é a GPU** — os tensores são pequenos `(B, 26)`. O custo é o laço
sequencial de T passos lançando kernels minúsculos. Consequência: subir `P` é
quase de graça, subir `T` custa proporcionalmente.

---

## 5. O mundo

Grafo urbano irregular de 24-26 nós. O táxi tem corpo e economia:

```
corpo      combustível, fome, fadiga, pneu, temperatura, óleo
avarias    quebra por falta de combustível, furo, superaquecimento, dano de motor
economia   tarifa por distância, imposto 18% sobre serviço, 9 upgrades compráveis
ambiente   semáforos com fase própria, tráfego NPC congestionando nós
serviços   posto, comida, descanso, oficina (pneu/óleo/checkup), loja
```

Calibrado para que o perito faça ~10 entregas em 1000 passos e o aleatório ~0.5.
A dificuldade é parametrizada por `Cfg(d)`; `d=1.0` é onde o corpo aperta de
verdade (as avarias disparam) mas o agente ainda produz.

---

## 6. As arquiteturas

Todas **lineares por dentro**, mesmo espaço de features. O que muda é *que memória*
alimenta o score de cada candidato:

| | params | memória |
|---|---|---|
| reativo | 24 | nenhuma |
| banco EMA | 30 | 3 EMAs sobre nós visitados, τ evoluído |
| diádica | 30 | blocos em potência de 2 — cobertura log₂ do horizonte |
| corpo | 30 | drive dominante puxa para o serviço correspondente |
| híbrido | 36 | diádica + corpo |

Features por candidato (18): distância ao alvo, custo da rua, congestionamento,
semáforo, 5 distâncias a serviços, 8 de estado interno, bias.
Mais 5 scores de serviço e 1 bias de serviço.

---

## 7. O achado mais recente: PODA

**Hipótese do usuário:** o cérebro humano superproduz sinapses e depois poda.
Redes neurais *geram* pesos em vez de *selecionar*. Selecionar deveria ser melhor.

**Implementação:** cada genoma ganha uma máscara binária `M` do mesmo tamanho de
`W`. O score usa `W*M`. Três estratégias:

```
gerar    w += ruido(0.30)                    — o padrão
podar    nasce denso, bit desliga p=5%, religa p=1.5%, w += ruido(0.15)
crescer  nasce esparso, bit liga p=5%
```

**Resultado com 20 sementes, 6.000 amostras por modo:**

```
                    gerar          podar        diferença      p
fitness treino   9.04 ± 0.69   10.54 ± 1.15   +1.50 ± 0.32   <0.00001   ✅
generalização   13.76 ± 2.52   15.38 ± 2.33   +1.62 ± 0.84    0.053     🟡
```

A poda é melhor em **57 das 60 gerações** e estabiliza em **35% das conexões**.

**Núcleo convergente** — 20 evoluções independentes concordam:

```
MANTIDO                  DESCARTADO (em 20/20)
d_alvo      100%         e_tem_pax    0%   (redundante com d_alvo)
sv_posto     95%         semaforo     0%
e_temp       85%         custo_rua    0%   (contido em d_alvo)
e_fadiga     70%         d_loja       0%
                         d_descanso   0%
```

**Status:** poda confirmada como operador de busca superior. Vantagem de
generalização fica no limiar (p=0.053, 12/20 vitórias) — **não afirme**.

### Próximo passo natural

A hipótese para a lacuna de generalização: a poda especializa nas cidades de
treino e descarta features que cidades novas precisariam. **Teste: poda com mais
cidades de treino.** Se a fraqueza é especialização, mais variedade fecha a lacuna.

---

## 8. Achados consolidados (não refaça)

### Se sustentaram

```
banco misto (EMA + oscilador)     venceu em 3/3 sinais
early exit por confiança          46% do custo, sem perda de acurácia
gate por pressão (sequencial)     17% do custo, ganho 3×
porta Torricelli                  zero exato abaixo do limiar + diferenciável
mistura estático+líquido          4.4× melhor que estático multi-regime
integral para ler escala de tempo robusta a ruído 1000× maior que derivada
poda como operador de busca       p<0.00001, 18/20 sementes
```

### Foram refutados

```
banco de τ alinha sensores        ❌ EMA borra, não translada — precisa de buffer
banco de τ é universal            ❌ satura em ~30% na memória longa
rotear por escala medida          ❌ perdeu para escolha aleatória
ritmo em gate de camada           ❌ perdeu para aleatório
"empilhe com portão" (políticas)  ❌ mistura 50/50 venceu os gates
cone/broca retém informação       ❌ raio decai → a fase morre junto
modular τ                         ❌ redundante com banco de τ (provado por oráculo)
surpresa como gatilho universal   ❌ 6 de 82 detectados, 341 falsos positivos
herança lamarckiana de upgrades   ❌ metade do desempenho
cronograma desenvolvimentista     ❌ não superou poda constante
```

### O padrão que atravessa tudo

**U invertido, oito vezes**: λ da ridge, inibição E/I, pressão metabólica, ganho β,
taxa η, atrito do momentum, ganho do semáforo, escala do softmax. O regime útil é
sempre a borda.

### O achado central

> **A escolha da memória é decidida pelo horizonte, não pela sofisticação.**

```
K < 10        janela explícita     99.8%   (e 0% fora do alcance)
10 < K < 50   diádica              86.2%
50 < K < 300  oscilador            73.7%
K > 300       diádica log           8.9%   (única que não satura)
```

---

## 9. Convergência com a literatura

| Nosso conceito | Nome estabelecido |
|---|---|
| banco de τ log-espaçados | Continuum Memory System (Nested Learning, Google 2025) |
| guardar a forma da curva | HiPPO → base do S4/Mamba |
| porta de escrita por entrada | seleção do Mamba / forget gate do LSTM (1997) |
| gate entre camadas | early exit / Mixture-of-Depths |
| busca "pelo meio" com pesos | learned index (Kraska et al. 2018) |
| poda como seleção | Lottery Ticket Hypothesis (Frankle & Carbin 2019) |

**Lacuna que permanece aberta:** todos usam frequências como hiperparâmetro fixo.
Ninguém as evolui por indivíduo nem as modula em tempo real por estado interno.

---

## 10. Como o usuário trabalha

Divisão acordada explicitamente:

> Ele traz as ideias e faz a visualização conceitual. Você constrói os artefatos
> (código, experimentos, widgets HTML) e **testa empiricamente, reportando com
> honestidade — inclusive quando falha.**

Preferências:
- comunicação direta, alta densidade técnica
- pensa em sistemas e pipelines
- quer ver resultado medido, não afirmação
- quando pede visualização, quer HTML interativo que ele possa manipular

**O que ele mais valoriza:** quando você mata a própria hipótese com dados.
Aconteceu várias vezes nesta pesquisa e é o que faz o material valer.

---

## 11. Estrutura de arquivos

```
src/
  taxi_np.py      simulação numpy — leve, para iterar rápido
  poda2.py        experimento de poda (CLI: modo + semente)
  lab.py          simulação torch vetorizada — para escala
  rodar.py        CLI da versão torch: --smoke, --perito, --bateria
docs/
  CLAUDE.md       este arquivo
  CONTEXTO.md     resumo executivo
  INDICE-MESTRE.md tabela validados/refutados + invariantes
  COLAB.md        dimensionamento de VRAM, limpeza, armadilhas
  01..16          documentos temáticos de achados
resultados/
  poda2.jsonl     dados brutos do experimento de poda (20 sementes)
notebooks/
  colab.ipynb     versão Colab
```

---

## 12. Invariantes de código

| # | Regra | Motivo |
|---|---|---|
| I1 | Modulação multiplicativa e lateral, nunca camada em série | docs/03 |
| I2 | Integração por Euler implícito, nunca explícito | leak grande diverge |
| I3 | `τ` sempre parametrizado em log | positividade sob mutação |
| I4 | Todo experimento com ≥10 sementes e desvio reportado | amostra pequena mente |
| I5 | Predição registrada antes de rodar | evita racionalização |
| I6 | Resultado negativo documentado, não descartado | metade do valor |
| I7 | Baseline obrigatório em toda comparação | |
| I8 | Contagem de parâmetros igualada entre arquiteturas | senão a comparação é inválida |
| I9 | Alinhar antes de filtrar: buffer, depois banco de τ | docs/10 §4 |
| I10 | `a = exp(-1/(tau*g))`, nunca `exp(-1/tau)*g` | o segundo diverge |
