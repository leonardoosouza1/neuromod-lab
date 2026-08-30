# Contexto para retomar em outra sessão

## O que é este projeto

Investigação sobre **arquiteturas de memória** — que estrutura de memória serve
para quê. Começou em neurônios líquidos (EMA), passou por osciladores, memória
diádica e portas de escrita, e chegou num benchmark aplicado: táxis com corpo
competindo num grafo urbano.

## O achado central

> **A escolha da memória é decidida pelo horizonte, não pela sofisticação.**
> Nenhuma arquitetura testada é boa em mais de uma faixa.

```
K < 10        janela explícita     99.8%   (e 0% fora do alcance)
10 < K < 50   diádica              86.2%
50 < K < 300  oscilador            73.7%
K > 300       diádica log          8.9%    (única que não satura)
```

## O que foi refutado (não repetir)

| Hipótese | Resultado |
|---|---|
| Banco de τ alinha sensores defasados | ❌ EMA borra, não translada — precisa de buffer |
| Banco de τ é universal | ❌ satura em ~30% na memória longa |
| Rotear por escala medida | ❌ perdeu para escolha aleatória |
| Ritmo em gate de camada | ❌ perdeu para aleatório; oscilador precisa de periodicidade real |
| "Empilhe com portão" (políticas) | ❌ mistura 50/50 venceu os gates |
| Cone/broca retém informação | ❌ raio decai → fase morre junto |
| Modular τ | ❌ redundante com banco de τ (provado por oráculo) |
| Surpresa como gatilho universal | ❌ 6 de 82 detectados, 341 falsos positivos |
| Herança lamarckiana de upgrades | ❌ metade do desempenho — remove a pressão que ensina |

## O que se sustentou

```
banco misto (EMA + oscilador)     venceu em 3/3 sinais
early exit por confiança          46% do custo, sem perda
gate por pressão (sequencial)     17% do custo, ganho 3×
porta Torricelli                  zero exato abaixo do limiar + diferenciável
mistura estático+líquido          4.4× melhor que estático multi-regime
integral para ler escala          robusta a ruído 1000× maior que derivada
```

## O padrão que atravessa tudo

**U invertido, oito vezes**: λ da ridge, inibição E/I, pressão metabólica, ganho β,
taxa η, atrito do momentum, ganho do semáforo, escala do softmax. O regime útil é
sempre a borda.

## Convergência externa

| Nosso conceito | Nome estabelecido |
|---|---|
| banco de τ log-espaçados | Continuum Memory System (Nested Learning, Google 2025) |
| guardar a forma da curva | HiPPO → base do S4/Mamba |
| porta de escrita por entrada | mecanismo de seleção do Mamba / forget gate do LSTM |
| gate entre camadas | early exit / Mixture-of-Depths |
| busca "pelo meio" com pesos | learned index (Kraska et al. 2018) |

**Lacuna que permanece aberta:** todos usam frequências como hiperparâmetro fixo.
Ninguém as evolui por indivíduo nem as modula em tempo real por estado interno.

## Estado atual

O benchmark de táxis está calibrado e verificado. A bateria GPU roda em Colab
(`notebooks/`) ou local (`src/rodar.py`). O portão de validação passa.

**Próximo passo:** analisar o JSON de resultado — principalmente a paisagem, para
saber se cada arquitetura usou sua memória ou se a evolução a desligou.
