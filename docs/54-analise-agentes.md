# O laço de agentes: o que melhorou, por que parou, e qual é a alavanca estrutural

Análise de `docs/agentes/placar.json` (55 políticas, 8 lotes) mais a configuração dos
juízes. 2026-09-09.

---

## 1. O ganho é real — e não é maldição do vencedor

Primeira coisa que testei, porque era o modo de falha mais provável: escolher a melhor
de 8 numa régua ruidosa produz uma escada descendente sozinha, sem melhora nenhuma.
**Não é o caso aqui.** Nas 16 políticas que passaram pela confirmação de 5 sementes, a
diferença média para a triagem de 3 sementes é **+0.001** (IC ±0.004). O juiz de vocês
— 128 cópias × 3 mapas × 3 sementes — é preciso o suficiente para que a seleção não se
alimente de ruído. A escada 0.85 → 0.56 é ganho verdadeiro.

Vale registrar o que isso significa por si só: **uma política explícita bate o cérebro
evoluído por 29 pp no mesmo mundo.** Pela régua escrita no próprio `oraculo_campo.py`
("se o oráculo vive onde a evolução morre, o gargalo é MONTAGEM"), isso é a prova mais
forte que o laboratório já produziu de que o problema não é o mundo nem a arquitetura:
**é a evolução não achar o que um agente consegue escrever.**

## 2. Como a melhora aconteceu: vazão, e só vazão

Comparando as 8 melhores com as 8 piores, em taxas **por dia vivo** (sem normalizar,
"mais corridas → menos morte" é só sobreviver mais tempo):

| taxa/dia | 8 melhores | 8 piores | razão |
|---|---|---|---|
| abastecimentos | 1.92 | 0.80 | **2.40×** |
| renda | 30.2 | 18.4 | 1.64× |
| corridas | 3.24 | 2.03 | 1.60× |
| refeições | 1.43 | 0.95 | 1.51× |
| **panes** | **1.19** | **1.35** | **0.88×** |

Tudo que melhorou foi "fazer mais por dia". O ser aprendeu a encher o dia. Esse eixo
está esgotado: o dia acabou.

## 3. Por que parou: as alavancas deixaram de tocar o comportamento

O platô não é do buscador, é dos parâmetros. Entre as **8 melhores políticas**, a
mortalidade varia 1.6 pp (0.560 a 0.576) e todas as taxas são planas:

| taxa/dia | mín | máx | amplitude |
|---|---|---|---|
| corridas | 3.20 | 3.27 | 0.06 |
| refeições | 1.42 | 1.44 | 0.03 |
| panes | 1.18 | 1.21 | 0.03 |
| abastecimentos | 1.80 | 1.95 | 0.16 |

Oito alavancas diferentes — gasolina, noite, rua, água, ordem das compras, livre —
produzem **o mesmo ser**. E há precedente medido: nos lotes 3 e 4, sete políticas têm
vetor de medidas idêntico até a 3ª casa. Vocês já pegaram parte disso ("parser: recusa
igual à base", lote 4), mas o diagnóstico maior é que os agentes estão afinando
parâmetros que não amarram mais.

## 4. A alavanca estrutural: a pane não tem preço

O único comportamento que **não melhorou em 8 lotes** é o único sem relação com
sobreviver: correlação de Spearman entre panes/dia e mortalidade = **+0.19** nas 55
políticas (todas as outras taxas ficam entre −0.79 e −0.90).

O motivo está na configuração dos dois juízes — `src/politica_util.py:34` e
`src/julga_politica.py:34`, idênticas:

```python
kcal_pane=8., guincho=0., fuel_pane=15.
```

**Guincho de graça, entregando 15 L no posto.** Com 6.95 panes por vida, são ~104 L
de combustível grátis por vida. A pane não é um acidente: é um serviço de entrega de
combustível sem custo em dinheiro.

Isto é o negativo **N15** do livro-razão — *"a pane devolvia 15 L de graça: 2,5 tanques
por vida; todo órgão de escassez ficou ocioso"* — que foi corrigido para o E61
(guincho 10, 5 L) e voltou pela porta dos juízes. Oito lotes de agentes otimizaram num
mundo onde quebrar sai de graça, e por isso nenhum deles mexeu na pane: não havia o que
ganhar. O consolidador pediu "alavanca estrutural" — ela é esta, e não é mecanismo
novo: é restaurar um preço que vocês já tinham estabelecido.

**Predição (registrar antes de rodar):** com `guincho=10, fuel_pane=5` no juiz, (a) as
políticas do platô se separam de novo — amplitude entre as 8 melhores sobe de 1.6 pp
para ≥ 8 pp; (b) mortalidade de todas piora (a base 0.56 vai para 0.65–0.80); (c) pela
primeira vez panes/dia passa a correlacionar com mortalidade (Spearman ≤ −0.4); (d) a
alavanca vencedora do próximo lote é de combustível, não de comida.

## 5. Como ir além — três degraus, nesta ordem

**(1) Devolver o preço da pane** (uma linha em cada juiz). Sem isso, todo lote novo
mede o mesmo ser. Barato, e testa uma predição escrita.

**(2) Trocar o alvo da seleção.** A mortalidade saturou e o dia encheu; um escalar só
não separa mais nada. A fronteira de Pareto em (sobreviver, renda) põe "pedra" e
"trabalhador" em pontos diferentes por construção e dá ao consolidador um eixo novo
para realocar tarefas. O placar já tem `rec` — é só deixar de reduzir a um número.

**(3) Fechar o laço com a evolução — o degrau que atende à sua meta.** Hoje vocês têm
duas metades que não se falam: agentes que escrevem políticas explícitas de 0.56 e uma
evolução que chega a 0.85. E têm a peça que liga as duas: a **base fechada**
(W\* = (ΦᵀΦ+λI)⁻¹ΦᵀY) clona um comportamento em outra arquitetura com 97–99,5 % de
fidelidade em 0,1 s. Então:

- clonar a melhor política explícita para o cérebro linear e medir a fidelidade;
- semear a evolução a partir desse clone, com custo de gene ligado;
- perguntar o que a evolução faz com ela: **segura, melhora, ou perde?**

Isso mede diretamente a sua tese — "o ser aloca peso conforme o mundo pede" — porque
parte de um ser que já resolve o mundo e pergunta quais genes ele mantém quando cada
gene custa caloria. E responde o achado do item 1: se a evolução não consegue nem
*segurar* uma política que já funciona, o gargalo é a busca (mutação σ fixa, clamp ±5,
sem crossover, sem niching); se segura mas não melhora, o gargalo é a paisagem; se
melhora, o laço agente→clone→evolução vira o motor do laboratório.

Nota: o E45 já mediu que semear do clone **não economiza gerações** — mas aquilo foi
clonar um campeão evoluído (0.63) em outra arquitetura. Clonar uma política **melhor
que qualquer coisa que a evolução achou** é uma pergunta diferente, e é a primeira vez
que vocês têm esse objeto na mão.

## 6. Duas correções menores de método

- **Confirmação com sementes independentes.** Hoje a triagem usa 7777/7778/7779 e a
  confirmação 7777–7781: três das cinco são as mesmas da seleção. O viés medido é
  desprezível (+0.001), então isto não é urgente — mas trocar as 5 da confirmação por
  sementes que a triagem nunca viu custa zero e fecha a porta.
- **Registrar o dispositivo no JSON.** Se alguma célula rodar em GPU diferente, o
  portão de identidade de vocês deixa de valer sem avisar.
