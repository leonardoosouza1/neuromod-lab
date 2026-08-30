# Porta de Escrita vs Modulação de τ — Dois Mecanismos Distintos

**Documento de resultados, majoritariamente negativos.** Isola dois mecanismos que o projeto vinha tratando como um só, e mostra que o canal proposto no `docs/03` ataca o mecanismo redundante.

**Corrige:** `docs/03` (neuromodulação sobre τ) e `docs/01` (banco de τ como primitivo suficiente).

---

## 1. A distinção

```
(1) modular o TAU      →  muda a ESCALA de integração
(2) modular a ENTRADA  →  decide SE absorve (porta de escrita)
```

Um banco de N τ **já cobre (1)** — todas as escalas estão presentes simultaneamente. Nada no banco cobre (2).

---

## 2. Medição que separa os dois

Duas tarefas, quatro configurações:

| tarefa | N | nada | só TAU | **só PORTA** | as duas |
|---|---|---|---|---|---|
| cópia seletiva | 4 | 2,1 % | 38,9 % | **90,6 %** | 44,6 % |
| cópia seletiva | 12 | 1,5 % | 40,6 % | **97,4 %** | 45,6 % |
| regimes de escala | 4 | **26,2 %** | 14,1 % | 26,2 % | 14,1 % |
| regimes de escala | 12 | **26,3 %** | 14,7 % | 26,3 % | 14,7 % |

Três leituras:

1. **A porta domina** na cópia seletiva: 97,4 % contra 40,6 %. Não é uma versão melhor do mesmo mecanismo — é outro mecanismo.
2. **Modular τ é ativamente prejudicial** na tarefa de regimes: 26,3 % → 14,7 %. O banco já cobre as escalas; mexer nos τ destrói a cobertura.
3. **Combinar as duas é pior que só a porta** (45,6 % vs 97,4 %). Mecanismos que não se complementam degradam quando somados.

### 2.1 Confirmação por oráculo

Teste independente com conhecimento perfeito do regime:

| N | fixo g=1 | ORÁCULO (τ certo por regime) | headroom |
|---|---|---|---|
| 1 | 14,17 % | 10,29 % | **−3,88 pp** |
| 6 | 16,61 % | 10,29 % | **−6,32 pp** |
| 24 | 16,61 % | 10,15 % | **−6,47 pp** |

> **O oráculo perde para o fixo em todos os N.** Não existe ganho a extrair adaptando τ nessa tarefa — nem com informação perfeita. Isso encerra a questão: **adaptar τ é redundante com um banco de τ.**

### 2.2 Bug encontrado no caminho

A primeira versão multiplicava `α` por `g`, o que produz `α > 1` e **divergência numérica** (overflow, resultados zerados). O correto é escalar o **τ**:

```
ERRADO:  a = exp(-1/tau) * g          →  a pode passar de 1 → diverge
CERTO:   a = exp(-1/(tau * g))        →  a sempre em (0,1)
```

Registrado como armadilha de implementação.

---

## 3. ⚠️ O modulador por surpresa da entrada não funciona

Tentativa de descobrir a porta sozinho, sem informar qual canal é o marcador. Modulador = surpresa acumulada `|v[t] − v[t−1]|` com limiar adaptativo por z-score.

| N | sem porta | porta APRENDIDA | porta ORÁCULO |
|---|---|---|---|
| 4 | 2,1 % | 1,9 % | **90,6 %** |
| 12 | 1,5 % | 2,4 % | **97,4 %** |
| 24 | 1,5 % | 2,7 % | **97,7 %** |

Diagnóstico do detector:

```
surpresa média quando marcador=1:  +0,23
surpresa média quando marcador=0:  +0,05
separação:                          0,19 desvios
marcadores detectados:              6 de 82
falsos positivos:                   341
```

**Motivo estrutural, não de ajuste:** o marcador é um canal separado com valor 1. A surpresa mede a norma da mudança total, dominada pelo canal de valor (ruído gaussiano). Um pulso de 1 no segundo canal é engolido pela variação normal do primeiro.

> **Surpresa não é detector universal.** Ela funciona quando o evento importante *é* uma mudança grande de magnitude. Quando a informação está em **qual** canal mudou, e não em **quanto**, ela é cega.

### 3.1 O que funcionou: gate aprendido

Busca aleatória sobre 3 parâmetros, sem informar o marcador:

```
gate encontrado:  w_x = −0,63   w_marcador = −14,76   bias = +9,03
desempenho: 100,0 %
```

Regra que emergiu: *"normalmente segure (bias alto); quando o marcador acender, jogue fora e absorva."*

**A informação de "quando escrever" precisa vir de uma feature aprendida, não de uma estatística genérica de surpresa.**

---

## 4. ⚠️ A porta não transferiu para o tráfego

Porta acionada por surpresa de **desempenho** (erro recente por cruzamento, z-score), não de entrada:

| mudança | fixo | aprende | **+ PORTA** | % aberta |
|---|---|---|---|---|
| D — capacidade desigual | 819,4 | **774,2** | 790,2 | 14 % |
| E — amarelo caro | **1261,8** | 1397,2 | 1315,1 | 15 % |
| F — desigual + assimétrico | 2431,1 | **361,1** | 2281,7 | 14 % |

**A porta piorou em todos os casos, e catastroficamente em F** (361,1 → 2281,7, seis vezes pior).

Diagnóstico: em F o aprendizado online é o que salva (6,7× de ganho). A porta **descarta a memória EMA periodicamente**, e como o sinal de aprendizado depende dessa memória (as features são as EMAs), descartá-la destrói o aprendizado que estava funcionando.

> **Porta de escrita e aprendizado online competem pelo mesmo recurso.** A porta protege contra memória obsoleta; o aprendizado precisa de memória acumulada para estimar gradiente. No tráfego, o segundo vale mais.

---

## 5. Onde a porta vale e onde não vale

| condição | porta ajuda? | evidência |
|---|---|---|
| informação chega em eventos discretos e esparsos | **sim, categórico** (2 % → 97 %) | cópia seletiva |
| é preciso descartar o passado ao chegar algo novo | **sim** | mesma tarefa |
| o sinal é contínuo e todo relevante | não | regimes de escala |
| existe aprendizado online dependendo da memória | **não, prejudica** | tráfego F |
| o gatilho precisa ser inferido de estatística genérica | não | detector de surpresa |

---

## 6. Consequências para o projeto

### 6.1 O `docs/03` precisa de revisão

O canal proposto como "noradrenalina = surpresa encurta τ" ataca o mecanismo **redundante**:

```
docs/03 propõe:   modulador altera τ                ← redundante com o banco (§2.1)
o teste indica:   modulador deveria abrir/fechar a PORTA DE ESCRITA
```

E mesmo a porta só vale sob as condições da §5 — que **não incluem** o domínio de controle testado.

### 6.2 O `docs/01` precisa de uma linha

Banco de τ é suficiente para cobrir escalas e **não precisa de modulação de τ**. O que falta ao banco é a porta, e ela é um mecanismo de outra natureza — controle, não estrutura.

### 6.3 Convergência externa

O mecanismo da porta é o **forget gate do LSTM** (1997) e o **mecanismo de seleção do Mamba/S6** (2023). O Mamba usa precisamente a tarefa de cópia seletiva para motivar a seleção, pelo mesmo motivo medido aqui: é a tarefa que separa os dois regimes.

---

## 7. Achados acionáveis

| # | Achado | Ação |
|---|---|---|
| P1 | Modular τ é redundante com banco de τ (oráculo perde) | não implementar modulação de τ |
| P2 | Porta de escrita dá ganho categórico em tarefa seletiva (2 % → 97 %) | implementar porta, não modulação de escala |
| P3 | Combinar porta + modulação de τ é pior que só porta | não somar mecanismos sem medir |
| P4 | Surpresa genérica não detecta o gatilho (6 de 82) | gatilho precisa ser feature aprendida |
| P5 | Porta destrói aprendizado online que depende da memória | não usar porta junto com adaptação de pesos |
| P6 | `a = exp(-1/tau)*g` diverge; usar `a = exp(-1/(tau*g))` | armadilha de implementação |

---

## 8. Ressalvas

- A tarefa de cópia seletiva é sintética e construída para favorecer a porta. O ganho de 2 % → 97 % mede a existência do mecanismo, não sua importância em dados reais.
- O detector de surpresa testado é um único desenho (norma da diferença + z-score). Um detector melhor poderia funcionar; o que está demonstrado é que **este** não funciona e **por quê**.
- O teste de tráfego usa 4 seeds, abaixo do invariante I4 (≥5).
- A porta no tráfego foi acionada por surpresa de desempenho, uma escolha entre várias possíveis. Um acionamento diferente poderia não competir com o aprendizado.
- Todos os resultados vêm de simulação sintética. Nenhum dado real.
