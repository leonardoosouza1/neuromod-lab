# Neuromod Lab

Laboratório de arquiteturas de memória em agentes com corpo, economia e ambiente adverso.

## Instalação

```bash
pip install torch numpy          # GPU: siga pytorch.org para a versão CUDA certa
```

Sem mais dependências. Roda em CPU, GPU local ou Colab sem mudar nada.

## Uso

```bash
python src/rodar.py --smoke      # segundos — só confere que não quebra
python src/rodar.py --perito     # PORTÃO — obrigatório antes de qualquer bateria
python src/rodar.py --bateria    # bateria completa

# ajustando escala
python src/rodar.py --bateria -P 8192 -G 100 -R 8

# sementes da EVOLUÇÃO (I4): rode 0/1/2 e compare — efeito entre arquiteturas
# menor que a amplitude entre sementes é ruído, não efeito
python src/rodar.py --bateria --seed-evo 1

# mundos com estrutura oculta (ver PREDICOES.md)
python src/rodar.py --bateria --mundo hotspot
```

### Queda no meio? Retoma sozinho (2026-08-31)

A bateria salva **resultado PARCIAL após cada arquitetura** (JSON atômico) e
**checkpoint da evolução a cada 10 gerações**. Rodar o mesmo comando de novo
pula o que está pronto e retoma a evolução de onde parou. `--do-zero` ignora
tudo e recomeça.

### Performance (2026-08-31)

Loop reescrito sem sync CPU↔GPU + `torch.compile` (desligue com `NM_COMPILE=0`)
+ janela diádica por ring buffer fundido: **~3× no B da bateria (524k mundos),
~4× na avaliação**. `src/testes.py <lab_antigo.py>` prova equivalência
numérica; o portão `--perito` continua obrigatório após qualquer mudança.

## Colab

`notebooks/colab.ipynb` é **auto-contido**: escreve o código sozinho via
`%%writefile`, sem zip nem Drive. Abra no Colab (T4), rode as células em ordem.
Roda 3 sementes e salva os JSONs no Drive ao final.

O resultado sai em `resultados/resultado-taxi-AAAAMMDD-HHMM.json`.

## O portão (leia isto)

`--perito` roda a **mesma política** (pesos escritos à mão, memória zerada) nas
cinco arquiteturas. Elas *têm* que dar resultado idêntico — se são a mesma
política, o resultado é o mesmo.

```
PASSOU: as 5 batem (spread 0.000)
```

Se divergirem, há bug de porte e a bateria vai medir o bug, não a arquitetura.
**Este teste pegou cinco bugs** durante a migração CPU → GPU:

| Bug | Sintoma |
|---|---|
| NaN de `.mean()` em fatia vazia | `.abs().max()` retornava 0, escondendo o NaN |
| Buffer circular com índice absoluto | quebrava só depois do passo 64 |
| Serviço escolhido sem dinheiro pra pagar | 97% do tempo parado |
| `sv` binário sem ponderar necessidade | não sabia decidir *quando* abastecer |
| 1 passageiro em vez de 6 | quase nunca encontrava alguém |

Todos eram silenciosos: rodavam sem erro e produziam números plausíveis.

## Estrutura

```
src/lab.py      simulação vetorizada + arquiteturas + evolução
src/rodar.py    CLI: smoke, portão, bateria
docs/           15 documentos de achados (leia INDICE-MESTRE.md primeiro)
resultados/     saída JSON
notebooks/      versão Colab
```

## O mundo

Grafo urbano irregular (26 nós), táxi com corpo e economia:

```
corpo       combustível, fome, fadiga, pneu, temperatura, óleo
avarias     quebra por combustível, furo de pneu, superaquecimento, dano de motor
economia    tarifa por distância, imposto 18% sobre serviço, 9 upgrades compráveis
ambiente    semáforos com fase própria, tráfego NPC congestionando nós
```

Calibrado para que o perito escrito à mão faça ~6 entregas em 1200 passos e o
aleatório ~0.5 — razão de 10×, com as avarias disparando de verdade.

## As arquiteturas

Todas lineares por dentro, mesmo espaço de features. O que muda é **que memória**
alimenta o score:

| | params | memória |
|---|---|---|
| reativo | 24 | nenhuma |
| banco EMA | 30 | 3 EMAs sobre nós visitados, τ evoluído |
| diádica | 30 | blocos em potência de 2 (log₂ do horizonte) |
| corpo | 30 | drive dominante puxa para o serviço correspondente |
| híbrido | 36 | diádica + corpo |

## O que o JSON contém

```
hist          curva de fitness por geração
snapshots     distribuição da população a cada 5 gerações (diversidade, percentis)
pesos_finais  + nomes_pesos, para saber qual peso é o quê
entregas      média, desvio, percentis, histograma de 20 bins
paisagem      f(w) perturbando CADA peso em 9 pontos → vales e picos
trajetoria    série temporal de corpo/dinheiro em 200 amostras
```

A **paisagem** é o que mostra o rumo que a otimização tomou: curvatura alta
significa peso crítico, platô significa que a rede ignora aquela dimensão.

## Regras de método que custaram caro

1. **Valide o mundo antes da política.** Um "perito" escrito à mão precisa bater
   o aleatório por margem larga. Se nem ele consegue, o mundo está inviável e
   nenhuma evolução vai salvar.
2. **Valide cada dimensão que o experimento vai medir.** Uma bateria sobre
   decisão de investimento morreu porque a economia tinha margem negativa —
   ninguém tinha lucro para investir.
3. **Resultado estranho é bug até prova em contrário.** Todas as anomalias desta
   sessão foram método, não descoberta.
4. **Réplicas antes de população.** `R=8` dá fitness com erro 8× menor.
   População grande com fitness ruidoso seleciona sorte.
