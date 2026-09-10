# Bancada do cérebro — um ser completo, entradas sintéticas, sem evolução

Você pediu para fechar um ser completo e injetar entradas falsas para ver o que sai. Isto
é isso: `SerCompleto` instanciado com **2048 genomas aleatórios** (uniformes em ±1.5),
mundo distinto L=200, corpo posto à mão em regime de escassez (tanque 0–30 L, fome 40–90,
água 30–90, dinheiro ±20), EMA do reflexo carregada e memória por distrito preenchida com
ruído. Uma passagem para frente, 2 threads, segundos de CPU. **Nenhuma evolução, nenhuma
bateria.** Figura: `bancada-cerebro.png`; dados brutos em `nm_bench.json`.

Isto mede **capacidade da arquitetura**, não desempenho de campeão. É o tipo de coisa que
vale medir uma vez e nunca mais duvidar.

---

## A separação que muda tudo: dirigir ≠ deslocar

A nota de cada opção é `q_g`. A escolha é `argmax` sobre 9 movimentos + 10 serviços.
Portanto **uma parcela que é igual nas 9 opções de movimento não muda a direção** — ela só
desloca "mover" contra "servir". Separando a contribuição de cada bloco nas duas partes:

| bloco | genes | **dirige** | desloca | dirige / total | muda a ação |
|---|---|---|---|---|---|
| espinha (linear) | 38 | **0.947** | 65.34 | 1.4 % | — |
| reflexo | 4 | 0.125 | 8.12 | 1.5 % | 14.7 % |
| tálamo | 15 | **0.412** | 26.66 | 1.5 % | 23.6 % |
| córtex | 48 | 0.167 | 7.32 | 2.3 % | 16.9 % |
| hipocampo | 113 | **0.0051** | 0.35 | 1.5 % | 0.8 % |

**Primeiro fato: 98–99 % de tudo que o cérebro calcula não dirige.** Vale para a espinha
também. O `argmax` sobre movimento vê apenas ~1,5 % da magnitude que o cérebro produz; o
resto desloca a fronteira mover-vs-servir. Não é bug — é a geometria de centrar por opção
(achado 84) vista de frente. Mas significa que **a arquitetura gasta quase toda a faixa
dinâmica numa decisão binária, e quase nada nas 9 direções**.

## Custo-benefício por gene: o hipocampo é 690× pior que o reflexo

| bloco | dirige por gene |
|---|---|
| reflexo (4 genes) | **0.03126** |
| tálamo (15) | 0.02749 |
| espinha (38) | 0.02493 |
| córtex (48) | 0.00348 |
| hipocampo (113) | **0.00005** |

O hipocampo tem **28× mais genes que o reflexo e dirige 690× menos por gene**. E muda a
ação escolhida em **0.8 %** dos seres, contra 23.6 % do tálamo, que tem 15 genes.

Isso reescreve a interpretação de dois meses de resultados. "O hipocampo não paga" não é
um fato sobre memória — é um fato sobre **a geometria da leitura do hipocampo**. Ele
recebe 113 genes de orçamento e entrega quase nada ao volante, porque a memória entra
multiplicando apenas os 10 sentidos que variam por opção, e com ganho mestre `tanh(g)` que
nasce em zero.

Ressalva honesta: os números de "dirige" dependem da distribuição de genomas (aqui
uniformes ±1.5); um campeão evoluído concentra pesos e pode mudar as magnitudes. O que
**não** depende do genoma é a razão dirige/desloca ≈ 1.5 %, que é geométrica, e o item
seguinte.

## Tálamo: a atenção total varia 4.6× entre seres

Soma dos 5 portões: **mínimo 1.81, mediana 5.00, máximo 8.29**. Com normalização divisiva
seria **fixa em 5.00** para todo mundo, sempre.

Ou seja: um ser pode ter 4.6× mais "atenção total" que outro, de graça. Não há recurso
escasso — logo não é atenção. E a evolução tem um caminho aberto para inflar todos os
portões ao mesmo tempo, que é exatamente o tipo de almoço grátis que o N19 descreve.

Conserto de uma linha, no `_gate`: `gate ← gate · NG / gate.sum()`.

## Córtex: a inversão de sinal é literalmente inalcançável

Multiplicador `1 + δ` medido sobre 2048 seres × 12 distritos × 4 sentidos:
**faixa [0.547, 1.453]**, e inversão de sinal em **0.00 %** dos casos — como tem de ser,
já que `|δ| ≤ 0.5` por construção.

E o mundo pede inversão: no distrito industrial a densidade de comida é **0.0** e no
residencial **2.0**. A política ótima para `d_comida` tem sinais opostos nesses dois
lugares. **A peça não consegue expressar a política ótima do mundo em que está sendo
testada** — e nenhuma quantidade de gerações resolve isso, porque é um limite de
representação, não de busca.

Conserto: `δ = A·tanh(·)` com `A` evoluído (ou fixo em 2.0), o que abre a faixa para
[−1, 3].

---

## O que isto sugere fazer antes da próxima bateria

1. **Portão de capacidade** — este banco vira um teste: para cada peça, medir *dirige*,
   *dirige por gene* e *muda a ação*. Peça que dirige menos que ~1 % da espinha por gene
   não deveria entrar numa bateria de arquitetura: o resultado nulo dela já está garantido
   pela geometria. Roda em segundos, em CPU, e teria poupado as baterias do hipocampo.
2. **Denominador no tálamo** (1 linha) e **amplitude do córtex** (1 linha).
3. **Repetir esta bancada com o campeão evoluído** em vez de genomas aleatórios, para ver
   se a evolução encontra sozinha uma geometria melhor de leitura — se encontrar, o
   diagnóstico muda de "a peça não pode" para "a peça pode, mas é cara".
