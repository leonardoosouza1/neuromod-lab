# Esparsidade Contextual e Aritmética de Shift — Achados e Protocolo para Modelo Real

**Documento de trabalho.** Resultados obtidos com pesos sintéticos, ideias derivadas, e o protocolo exato para validar em Qwen.

**Aviso central:** todos os números deste documento vêm de **pesos aleatórios**. Redes treinadas têm estrutura que pesos aleatórios não têm — a esparsidade real é maior e a co-ativação existe. Os resultados aqui indicam **direção**, não magnitude. O objetivo do documento é dizer exatamente o que medir no modelo real.

---

## 1. A premissa

Em FFN com ReLU (ou variantes como SwiGLU), boa parte dos neurônios produz zero para um dado token:

```
z = W₁·x + b₁          projeção para a camada oculta
a = ReLU(z)            metade (ou mais) vira zero
y = W₂·a               os zeros não contribuem em nada
```

**Medido com pesos aleatórios:** 50,1 % das ativações > 0. Em LLMs treinados, a literatura reporta esparsidade tipicamente entre 80 % e 95 % — o desperdício real é maior.

### 1.1 O paradoxo

```
Para saber se zᵢ > 0, é preciso calcular zᵢ = wᵢ·x — o produto escalar inteiro.
Ou seja: você precisa calcular para descobrir que não precisava calcular.
```

Toda a técnica existe para resolver isso: **um preditor barato que adivinha o sinal sem fazer a conta completa.**

### 1.2 Isto já existe

A ideia tem nome — *contextual sparsity* — e implementações conhecidas:

- **DejaVu** — preditor treinado por camada, prevê o conjunto ativo antes de calcular
- **PowerInfer** — separa neurônios "quentes" (ativam quase sempre → GPU) de "frios" (raros → CPU)

**Não é território virgem.** O que este documento propõe é uma extensão específica (§4) que parece pouco explorada.

---

## 2. Achado 1 — preditor de posto baixo funciona

Método: aproximar `W₁` por uma matriz de posto `r` via SVD, usar essa versão barata para prever quais neurônios ativam, e calcular exatamente apenas os selecionados.

```
posto r    custo relativo    recall@top-k    erro final    FLOPs poupados
     8          52,1 %          58,8 %         57,35 %        47,9 %
    16          54,0 %          62,0 %         52,18 %        46,0 %
    32          57,9 %          66,8 %         44,45 %        42,1 %
    64          65,7 %          73,2 %         33,65 %        34,3 %
```

**Interpretação:** o mecanismo funciona (recall sobe com o posto), mas o erro final é alto porque com pesos aleatórios a esparsidade é de apenas 50 % e não há estrutura para o preditor capturar.

**O que medir no Qwen:** a mesma tabela. A expectativa é recall muito mais alto para o mesmo posto, porque a matriz treinada tem espectro concentrado — poucas direções dominantes.

---

## 3. Achado 2 — prever o SINAL é muito mais barato que prever o VALOR

```
posto r = 8    acerto do sinal = 58,5 %    correlação do valor = 0,243
posto r = 32   acerto do sinal = 66,4 %    correlação do valor = 0,489
```

Prever "vai ser positivo?" é **classificação binária**; prever `zᵢ` é regressão. O sinal se recupera com posto muito menor.

**Consequência de projeto:** o preditor pode ser ridiculamente pequeno, porque só precisa da decisão, não do número. Isso justifica economicamente toda a arquitetura.

---

## 4. Achado 3 — coerência temporal (a ideia mais promissora)

```
sobreposição do conjunto ativo entre passos consecutivos:  97,0 %
sobreposição com um passo aleatório (baseline):            75,3 %
ganho real de informação temporal:                        +21,6 pontos
```

**O conjunto de neurônios ativos quase não muda entre passos consecutivos.**

### 4.1 A proposta

```
DejaVu:                prevê os N sinais do zero, a cada token
Preditor incremental:  mantém o conjunto anterior e prevê apenas quem MUDA
```

Se 97 % permanece, o preditor lida com ~3 % dos neurônios por passo. O custo do preditor cai por uma ordem de magnitude.

### 4.2 Por que isso é plausível

A esparsidade tem **inércia** — mesma estrutura de um neurônio líquido: estado que persiste com pequenas atualizações. O conjunto ativo é ele próprio uma variável de estado com constante de tempo própria.

### 4.3 Ressalva forte

O teste usou trajetória artificialmente suave (`cumsum` de ruído gaussiano). **Em texto real, a mudança entre tokens é mais brusca.** O número verdadeiro pode ser muito menor que 97 %.

**Este é o experimento mais importante do documento** (§8, E1). Se a persistência real for alta (>80 %), há economia adicional sobre o estado da arte. Se for baixa (<50 %), a ideia morre e isso precisa ser registrado.

---

## 5. Refutado — importância não é concentrada

Hipótese testada: "existem poucos neurônios que carregam quase tudo; basta achá-los".

```
top-k neurônios    % da contribuição    ganho usando só eles
        4                 6,6 %             −62,06 %
        8                13,1 %             −26,43 %
       16                24,5 %             +47,86 %
       32                44,8 %             +52,46 %
       64                75,0 %             +58,03 %
      128               100,0 %             +63,35 %
```

Com 8 de 128 neurônios o desempenho fica **pior que o baseline**. É preciso ~50 % deles para chegar perto do total.

> **A informação é distribuída.** Selecionar um subconjunto fixo não funciona.
> O que funciona é **projetar** (PCA / low-rank), não **descartar**.
> Referência interna: 8 componentes reconstruíram 64 neurônios com 1,87 % de erro.

**Distinção importante:** esparsidade *contextual* (quais ativam **para este token**) é real e explorável. Esparsidade *estática* (quais neurônios são globalmente importantes) não é.

---

## 6. Não conclusivo — co-ativação

```
co-ativação média entre pares:      25,1 %
esperado se independentes:          25,1 %
excesso sobre independência:        −0,1 %
```

Com pesos aleatórios, **zero estrutura de grupo** — cada neurônio decide sozinho, como esperado.

**Isto não refuta a hipótese.** É justamente o treino que cria co-ativação, e é o que PowerInfer explora. O teste precisa ser refeito no modelo real (§8, E3).

---

## 7. Achado paralelo — aritmética de shift para τ

Linha independente, aplicável à parte recorrente/state-space, não à FFN.

### 7.1 O mecanismo

```
h = α·h + (1−α)·x                  EMA normal, 2 multiplicações
com α = 1 − 2^(−k):
h += (x − h) >> k                  1 subtração, 1 shift, 1 soma — ZERO multiplicação
```

Cada `k` inteiro dá um τ:

```
k=1 → τ=1,44     k=3 → τ=7,49     k=6 → τ=63,5     k=8 → τ=255,5
```

### 7.2 A limitação e a correção

Com **um** shift só existem ~7 valores de τ (grade log base 2), erro médio de 26,9 % contra os τ desejados. Isso custava desempenho na única tarefa sensível a sintonia fina.

**Solução: dois shifts somados** (representação canônica com sinal, técnica clássica de DSP):

```
k alvo    2^(−k) exato      shifts          obtido     erro
  1,50       0,3536      >>1 − >>3         0,3750     6,1 %
  4,70       0,0385      >>5 + >>7         0,0391     1,5 %
  5,20       0,0272      >>5 − >>8         0,0273     0,5 %
  6,80       0,0090      >>7 + >>10        0,0088     2,1 %
```

Resultado na tarefa que perdia (multi-senoidal, 5 seeds):

```
N=8:   τ livre 48,73 %  |  1 shift 47,21 %  |  2 shifts 48,90 %   (recupera 111 %)
N=16:  τ livre 52,34 %  |  1 shift 50,18 %  |  2 shifts 51,92 %   (recupera 81 %)
```

τ únicos disponíveis: 1 shift → 7; **2 shifts → 16 (todos distintos)**.

### 7.3 Restrições

**`k` deve ser ≥ 1.** Com `k < 0`, `α` sai de (−1,1) e o sistema diverge — condição de estabilidade da EDO, não escolha de projeto.

```
k = −1 → α = −1  oscila, não integra
k = −2 → α = −3  DIVERGE
```

**Zona morta em inteiro:** se `|x − h| < 2^k`, o shift resulta em zero e `h` **trava** antes de atingir o alvo.

```
16 bits, k=6 → travou no passo 109 com h=167, alvo=230
```

Mitigações: dithering de ±1 LSB, ou acumulador de resíduo (delta-sigma).

### 7.4 Onde vale

```
✅ FPGA / ASIC        multiplicador custa milhares de portas; shift custa zero
✅ MCU sem FPU        float emulado ~50 ciclos; shift 1 ciclo
✅ quantização int8   estado exato, sem erro de arredondamento acumulado
❌ CPU x86 + numpy    MEDIDO: 0,94× (mais lento — SIMD já resolve)
❌ GPU                FMA é a operação nativa mais barata
```

**Medição:** float64 EMA 554,9 ms vs int32 shift 588,7 ms em 200 mil passos. O ganho real exige C compilado ou hardware sem multiplicador.

---

## 8. Protocolo para o modelo real (Qwen)

### Preparação

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

mod = AutoModelForCausalLM.from_pretrained("Qwen/Qwen2.5-0.5B", torch_dtype=torch.float32)
tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")

ativ = {}
def hook(nome):
    def f(m, inp, out):
        ativ.setdefault(nome, []).append(out.detach().cpu())
    return f

for i, blk in enumerate(mod.model.layers):
    blk.mlp.act_fn.register_forward_hook(hook(f"L{i}"))   # saída da não-linearidade
```

**Atenção:** Qwen usa SwiGLU, não ReLU pura. A saída de `act_fn` não é exatamente zero — é preciso definir um limiar (ex.: `|a| < 0.01·std`) e reportar qual limiar foi usado. Este detalhe muda todos os números.

### E1 — Persistência temporal (PRIORIDADE MÁXIMA)

Testa o §4. É a única ideia potencialmente nova do documento.

```
1. rodar um texto real de ~2000 tokens
2. para cada camada, montar máscara binária A[t] = (|ativação| > limiar)
3. medir: persist[t] = |A[t] ∩ A[t−1]| / |A[t]|
4. baseline obrigatório: |A[t] ∩ A[aleatório]| / |A[t]|
5. reportar média e desvio POR CAMADA (o comportamento deve variar com a profundidade)
```

**Predição registrada:** persistência entre 60 % e 85 %, acima do baseline por pelo menos 15 pontos, e **maior nas camadas profundas** que nas iniciais.

**Critério de refutação:** se persistência − baseline < 10 pontos, a ideia do preditor incremental morre. Documentar e encerrar.

### E2 — Esparsidade real por camada

```
1. fração de ativações acima do limiar, por camada
2. histograma: distribuição da fração ativa por token
3. comparar camadas iniciais vs finais
```

**Predição:** 70–95 % de esparsidade, maior nas camadas intermediárias.
**Uso:** calibra o quanto há a ganhar. Se a esparsidade real for ~50 % como nos pesos aleatórios, todo o resto tem pouco valor.

### E3 — Co-ativação (refaz o §6)

```
1. matriz C[i][j] = P(i e j ativos juntos), sobre ~5000 tokens
2. comparar com o produto das marginais P(i)·P(j)
3. medir excesso sobre independência
4. clusterizar e verificar se emergem grupos
```

**Predição:** excesso claramente positivo (ao contrário dos pesos aleatórios), com grupos identificáveis. É a base do PowerInfer.

### E4 — Neurônios quentes vs frios

```
1. frequência de ativação de cada neurônio ao longo de todo o corpus
2. ordenar e plotar a distribuição
3. medir: quantos neurônios cobrem 80 % de todas as ativações?
```

**Predição:** distribuição de cauda longa. Uma fração pequena ativa quase sempre.
**Uso:** particionamento GPU/CPU.

### E5 — Preditor de posto baixo (refaz o §2)

```
1. SVD de W_gate por camada; olhar o espectro
2. para r em {8, 16, 32, 64}: prever sinal, medir recall@k
3. medir erro de saída da camada usando apenas os top-k previstos
4. contar FLOPs de verdade, incluindo o custo do preditor
```

**Predição:** recall > 90 % com posto 32, muito acima dos 66,8 % dos pesos aleatórios.

### E6 — Preditor incremental (só se E1 passar)

```
1. treinar um classificador leve que, dado A[t−1] e x[t], prevê apenas as MUDANÇAS
2. comparar custo e recall contra o preditor completo do E5
3. métrica decisiva: FLOPs totais (preditor + FFN esparsa) vs FFN densa
```

Este é o experimento que decide se a ideia do §4 tem valor prático.

---

## 9. Ordem de execução

1. **E2** (esparsidade real) — se for baixa, o resto perde sentido. *Custo: minutos.*
2. **E1** (persistência) — a ideia potencialmente nova.
3. **E4** (quente/frio) — barato, reproduz resultado conhecido, valida a instrumentação.
4. **E3** (co-ativação) — estrutura de grupo.
5. **E5** (preditor low-rank) — reproduz DejaVu.
6. **E6** (incremental) — só se E1 der sinal positivo.

---

## 10. Armadilhas conhecidas

| Armadilha | Como evitar |
|---|---|
| SwiGLU não zera exatamente | definir e **reportar** o limiar; testar sensibilidade a ele |
| Medir só um texto | usar ≥3 domínios (código, prosa, diálogo) — a esparsidade varia |
| Ignorar o custo do preditor | contar FLOPs totais, sempre; um preditor caro anula o ganho |
| Confundir esparsidade estática com contextual | são coisas diferentes (§5) |
| Cache KV mascarando o resultado | medir na FFN, que não tem cache |
| Concluir a partir de uma camada | o comportamento varia muito com a profundidade |
| Achar que ganho de FLOPs = ganho de tempo | acesso à memória frequentemente domina; cronometrar de fato |

---

## 11. O que este documento NÃO afirma

- **Não** afirma que a esparsidade contextual é nova — é DejaVu/PowerInfer.
- **Não** afirma magnitudes: todos os números vêm de pesos aleatórios.
- **Não** valida o preditor incremental — é hipótese, e E1 pode matá-la.
- **Não** mediu ganho de velocidade real em nenhum caso (FLOPs ≠ tempo).
- A aritmética de shift (§7) aplica-se a modelos recorrentes/SSM, **não** à FFN de um transformer.
