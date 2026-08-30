# Estático + Líquido: Quando a Adaptação Vale a Pena

**Documento de resultados.** Bateria completa no domínio de semáforos: 6 tipos de mudança × 6 arquiteturas × 5 seeds. Inclui os controles que isolam o mecanismo.

**Corrige:** a recomendação "não misture, empilhe com um portão" de sessão anterior — ela **não se sustentou** neste domínio.

---

## 1. Montagem

```
ESTÁTICO   pesos evoluídos offline em regime simétrico (NS=EW=0,40), depois CONGELADOS
LÍQUIDO    mesma base de features, pesos atualizados online por regra delta
FEATURES   pressão EMA em 3 escalas (τ=2,10,40) × 2 direções + sin θ + cos θ + bias
MUDANÇA    aplicada no passo 3000 de 6000; medida a fila média antes e depois
```

Ambos usam o mesmo espaço de features. A única diferença é congelado vs adaptando.

### 1.1 Pré-requisito: a regra de aprendizado funciona?

Diagnóstico obrigatório antes de qualquer comparação — um controlador incompetente invalida todo o teste:

| regra | fila ao longo de 40k passos |
|---|---|
| **delta** | 21, 21, 21, 21, 21, 22, 22, 21, 22, 21 |
| REINFORCE | 1700 → 58 089 (**diverge**) |
| REINFORCE normalizado | 3988 → 61 579 (**diverge**) |

> A regra delta converge para **21**, o mesmo do estático evoluído. As duas variantes de REINFORCE divergiram. Um teste anterior de revezamento foi invalidado porque usava um líquido que nunca aprendeu.

---

## 2. Resultado principal: duas famílias de mudança

### 2.1 Mudanças que a representação ABSORVE — estático vence

| mudança | estático | líquido pré-treinado | mistura | gate novidade |
|---|---|---|---|---|
| A — sem mudança (controle) | **20,3** | 21,5 | 21,4 | 21,7 |
| B — demanda assimétrica (0,14 / 0,72) | **22,1** | 31,4 | 34,2 | 37,3 |
| C — demanda alta (0,55 / 0,55) | **28,6** | 31,2 | 37,1 | 38,8 |

**O estático degradou só 9 % quando a demanda foi invertida** (NS caiu 65 %, EW subiu 80 %).

> **Motivo:** as features são pressões **relativas** por escala. Um controlador que decide por `pressão_EW − pressão_NS` funciona em qualquer proporção de demanda. A representação já normaliza a mudança.
>
> **Representação boa vale mais que adaptação.** Se as features são invariantes ao que muda, não há o que adaptar.

### 2.2 Mudanças que a representação NÃO absorve — estático colapsa

| mudança | estático | líquido pré-tr. | **mistura** | gate suave |
|---|---|---|---|---|
| D — capacidade desigual por cruzamento | 812,1 | 789,4 | **706,1** | 797,0 |
| E — amarelo caro (2 → 5 passos) | 1257,6 | 214,2 | **188,4** | 216,6 |
| F — desigual + assimétrico | 2429,7 | 127,1 | 125,6 | **119,2** |

**Na mudança F o estático fica 19× pior que a mistura** (2429,7 vs 125,6).

> **Motivo:** capacidade heterogênea e custo de amarelo **não aparecem nas features**. O controlador não tem como saber que aquele cruzamento passa 1 carro em vez de 4. Nenhuma escolha de pesos fixos resolve — só medir o resultado e corrigir.

### 2.3 A regra que emerge

```
a mudança é expressável nas features?   →  SIM  →  representação resolve, adaptação é peso morto
                                        →  NÃO  →  adaptação é obrigatória, e a diferença é de ordem de magnitude
```

---

## 3. ⚠️ Controle crítico: é adaptação ou só segunda opinião?

"Congelado" = o líquido participa da decisão mas **não** atualiza os pesos.

| mudança | estático só | mistura CONGELADA | mistura APRENDENDO |
|---|---|---|---|
| D — capacidade desigual | 812,1 | 794,6 | **706,1** |
| E — amarelo caro | 1257,6 | 942,6 | **188,4** |
| F — desigual + assimétrico | 2429,7 | 186,5 | **125,6** |

**Resultado decomposto:**

- Em **E**, a adaptação faz quase todo o trabalho: 942,6 → 188,4 (**5×**). Segunda opinião congelada quase não ajuda.
- Em **F**, ter a segunda política já resolve a maior parte: 2429,7 → 186,5 (**13×**); a adaptação acrescenta 1,5×.

> **São dois mecanismos distintos e ambos são reais.** Diversidade de política e adaptação online contribuem de forma diferente conforme o tipo de mudança. Sem este controle, os dois seriam confundidos.

---

## 4. ⚠️ REFUTADO: o gate não venceu a mistura

| mudança | mistura fixa 50/50 | gate duro | gate suave | gate por desempenho |
|---|---|---|---|---|
| D | **706,1** | 798,8 | 797,0 | 799,0 |
| E | **188,4** | 238,3 | 216,6 | 1373,5 |
| F | 125,6 | 128,0 | **119,2** | 839,6 |

**A mistura fixa 50/50 venceu em D e E; o gate suave venceu em F por margem estreita.** Nenhum gate foi consistentemente melhor.

E o **gate por desempenho foi desastroso** (1373,5 em E — pior que o estático sozinho). Motivo provável: ele mede desempenho por cruzamento com ruído alto e exploração de 6 %, então alterna erraticamente entre políticas e nunca deixa nenhuma estabilizar.

### 4.1 Por que o gate funcionou em camadas e não aqui

```
GATE DE CAMADA (funcionou)        GATE ESTÁTICO/LÍQUIDO (não venceu)
as duas opções são a MESMA rede    duas políticas diferentes
parar cedo ou seguir: ambas certas ambas parcialmente certas o tempo todo
o sinal (confiança) é do próprio   o sinal (novidade) é indireto
  cálculo já feito
```

> Quando duas políticas são **ambas parcialmente competentes**, mediar as duas extrai mais que escolher uma. Escolher joga fora informação; a média a preserva.

Isso corrige a recomendação anterior ("empilhe com portão"): ela vale para early exit, **não** para combinar políticas.

---

## 5. Competidor justo: estático treinado em múltiplos regimes

Um estático evoluído nos **quatro** regimes simultaneamente (simétrico, assimétrico, amarelo caro, capacidade desigual):

| controlador | D | E | F | média |
|---|---|---|---|---|
| estático 1 regime | 812,1 | 1257,6 | 2429,7 | 1499,8 |
| **estático MULTI-regime** | 797,1 | 970,8 | 2428,7 | **1398,9** |
| mistura (est. 1 reg + líquido) | 706,1 | 188,4 | 125,6 | **340,0** |
| mistura (est. multi + líquido) | 690,2 | 198,2 | 118,9 | **335,8** |

**Treinar o estático em todos os regimes melhorou só 7 % (1499,8 → 1398,9).** Adicionar o líquido melhorou **4,4×** (1499,8 → 340,0).

> **Robustez por cobertura de treino não substitui adaptação online.** Mesmo tendo visto todos os regimes, os pesos fixos não conseguem se comportar de forma diferente em cada um — porque a feature que distingue os regimes não existe no vetor de entrada.

E note: com o líquido presente, **qual estático se usa quase não importa** (340,0 vs 335,8). O líquido carrega a adaptação.

---

## 6. Achados acionáveis

| # | Achado | Ação |
|---|---|---|
| B1 | Regra delta converge; REINFORCE diverge neste setup | usar delta; sempre diagnosticar o aprendiz antes de comparar |
| B2 | Mudança expressável nas features → estático basta | investir em representação invariante antes de adaptação |
| B3 | Mudança fora das features → adaptação dá 5–19× | identificar o que as features NÃO capturam |
| B4 | Mistura 50/50 ≥ gate em 2 de 3 mudanças | combinar políticas por média, não por seleção |
| B5 | Gate por desempenho é instável e prejudicial | não usar |
| B6 | Multi-regime melhora 7 %; líquido melhora 4,4× | cobertura de treino não substitui adaptação |
| B7 | Diversidade e adaptação são mecanismos separados | medir os dois com o controle "congelado" |

---

## 7. Ressalvas

- Um único domínio (semáforos, malha 4×4). Não generaliza automaticamente.
- 5 seeds por célula, acima do invariante I4, mas os desvios não foram reportados por célula; diferenças menores que ~15 % devem ser tratadas como empate.
- Os carros só se movem para sul e leste, sem rotas alternativas. Por isso bloqueio total satura e teve de ser substituído por capacidade heterogênea.
- A regra delta foi ajustada informalmente (lr=0,05, clip ±6). Não houve busca de hiperparâmetro para o líquido nem para os gates — os gates podem estar subotimizados.
- O limiar de novidade (z > 2,0) foi escolhido a olho. Um gate melhor calibrado poderia superar a mistura.
- "Antes da mudança" o estático é sempre o melhor (20,2); todas as arquiteturas com líquido pagam ~1 ponto de custo permanente. Em ambiente estacionário, adaptação é peso morto — consistente com o achado de `docs/05` §7.
