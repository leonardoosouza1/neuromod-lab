# Jardim comum — a sua ideia, medida, e o que ela custa em código

A ideia (um mundo só, muitos seres diferentes, todos nascendo no mesmo lugar) tem nome em
biologia: **experimento de jardim comum**. Antes de opinar eu medi o que ela compra.
Figura: `jardim-comum.png`.

---

## 1. O número que decide: o berço vale mais que o genoma

Rodei o **mesmo campeão** replicado 384 vezes, num **único mapa**, mudando só o berço
(posição inicial sorteada, como o mundo faz hoje), 16 dias de horizonte:

```
tempo de vida do MESMO ser:   média 6.01 d   DP 3.91 d   p10 2.2 d   p90 12.5 d
```

O mesmo genoma vive entre **2 e 12 dias** dependendo unicamente de onde nasceu. O piso de
ruído do mundo é **65 % da média**.

Decompondo (mesmo genoma com berço fixo isola o fluxo; genomas diferentes com berço fixo
isola o ser):

| componente | % da variância do tempo de vida |
|---|---|
| berço (posição inicial) | **83 %** |
| fluxo de passageiros | 5 % |
| **o ser (genoma)** | **11 %** |

**Você está certo, e por uma margem maior do que imaginava: 89 % do desfecho não é o ser.**

Ressalva: os 11 % dependem de quão diferentes são os seres comparados — aqui foi o campeão
mais perturbações σ = 0.3. Com arquiteturas realmente distintas essa fatia sobe. O que não
depende do contraste é o piso: DP 3.91 d para um ser fixo.

## 2. Isso não é só medição ruim — é SELEÇÃO ruim

Aqui está a consequência que eu não tinha visto. Durante a evolução, cada genoma é avaliado
em R réplicas e a elite é o topo do ranking. Com DP do mundo de 3.91 d:

| R | erro do fitness de um genoma | DP do genoma | razão sinal/ruído |
|---|---|---|---|
| 4 (fumaça) | 1.95 d | 1.40 d | **0.72** |
| 8 | 1.38 d | 1.40 d | 1.01 |
| 16 (honesto) | 0.98 d | 1.40 d | 1.43 |

Com R = 4 o ruído é **maior que o sinal**. A elite de cada geração é, em boa parte, quem
nasceu num bom lugar. A evolução está selecionando sorte — e isso explica por que os
campeões variam tanto entre sementes, e por que P512 (que aumenta o número de sorteios)
ajudou tanto.

No jardim comum a comparação vira **pareada**: todos os genomas enfrentam o mesmo berço e
o mesmo fluxo, então a diferença entre dois genomas não contém nada do mundo.

```
variância da diferença não pareada / pareada = 8.8×
→ 3.0× de resolução, ou 9× menos réplicas para a mesma precisão
```

Para chegar a um erro de 0.5 d por genoma: hoje **R = 61**; no jardim comum **R = 8**.
E isso **compõe** com o ganho de P512 (7.7× por segundo), porque age em outro eixo.

## 3. Por que o portão de identidade falhou — e onde está o conserto

Igualei berço, corpo e passageiros iniciais e ainda assim o mesmo genoma deu DP 0.97 d.
Motivo: o mundo **sorteia durante a vida**, e todos os sorteios são `(B, …)`, independentes
por ser:

| linha em `campo.py` | sorteio | forma |
|---|---|---|
| 211, 215, 217 | onde nasce cada passageiro | `(B, n)` |
| 220, 221 | destino de cada passageiro | `(B, N)` |
| 387 | passageiro aparece no ponto (`vem`) | `(B,)` |
| 400 | respawn de passageiro (`volta`) | `(B, NPX)` |

Cada ser vive uma realização estocástica própria, mesmo no mesmo mapa. Então "mesmo mundo"
hoje é mentira: é o mesmo *mapa*, mundos diferentes.

**O conserto é compartilhar os números aleatórios, não os resultados** (é a técnica de CRN
feita direito). Sorteie com forma `(NB, …)` onde `NB = NC*R` é o número de **blocos**, e
indexe por `bloco = cidx*R + r` em vez de por ser. Cada genoma compara-se com os outros
sob o mesmo `u ~ U(0,1)`, e ainda assim reage conforme o próprio estado — o limiar de
`vem`, por exemplo, continua dependendo do distrito onde *aquele* ser está.

Contrato: `cfg.jardim_comum: bool = False` reproduz hoje **bit a bit**; `True` troca `B` por
`NB` nas seis linhas acima e replica o berço por bloco.

## 4. O desenho que eu recomendo (e o que evitar)

**Não um berço só.** No teste, o berço único deu média 2.97 d contra 6.01 d da população —
aquele ponto específico é ruim. Um berço só troca ruído por viés.

O desenho certo é **blocos**, que é a estrutura que o `R` já tem:

```
bloco = (mapa, berço, fluxo de passageiros)      NB = NC × R blocos
todos os genomas de uma geração rodam nos MESMOS NB blocos
os blocos MUDAM a cada geração (ou a cada k gerações)
```

Isso é um delineamento em blocos completos: a comparação dentro da geração é exata, e a
rotação entre gerações impede que a população decore um berço.

**E separe os dois usos:**

| uso | mundo | por quê |
|---|---|---|
| evoluir | mapas variados, blocos rotativos | senão o campeão decora a cidade |
| **julgar / comparar braços** | jardim comum, blocos fixos | máxima potência, comparação pareada |

Um resultado que não separa no jardim comum certamente não separa em mundos variados —
por isso ele é a **peneira**, e a régua honesta em mundos variados vira a **confirmação**.

## 5. O que o jardim comum permite medir que hoje é impossível

Esta é a parte que me anima mais, e responde a pergunta aberta 4 do projeto ("métricas de
juízo que separem sobreviver de fazer bem"). Com todos os seres no mesmo estado, dá para
comparar **decisões**, não só desfechos:

1. **Concordância de ação** — em que fração dos tiques dois braços escolhem o mesmo? Uma
   matriz braço × braço de concordância é um mapa de quão diferentes eles realmente são.
2. **Tempo de divergência** — quantos tiques até dois seres tomarem caminhos diferentes.
3. **Ponto de decisão** — no tique em que divergem, qual era o estado? Isso localiza *onde*
   a vantagem de uma arquitetura nasce, em vez de só dizer que ela existe.
4. **Agrupamento comportamental** — agrupar seres pela sequência de ações, sem olhar genes;
   depois perguntar quais genes predizem o grupo. É a única forma de descobrir *estratégias*
   em vez de *pesos*.

Nada disso precisa de GPU: é análise de trajetória.

## 6. Sobre o agente do mundo

A ideia de um agente que lê resultados e propõe mudanças no mundo é boa como **gerador de
hipóteses** e perigosa como decisor. O risco tem nome: jardim de caminhos que se bifurcam —
se o mundo muda em resposta ao resultado, e o resultado é reavaliado no mundo mudado, não
há teste, há ajuste.

A regra que mantém isso honesto já existe na casa: **toda proposta do agente entra no ledger
como predição escrita antes de rodar**, com critério e n. O agente propõe; o ledger decide.
Com isso ele vira um bom uso de LLM — ler 160 corridas e sugerir o que ninguém olhou — sem
virar um gerador de resultados falsos.

---

## Custo de implementação

| item | tamanho |
|---|---|
| `cfg.jardim_comum` + índice de bloco nas 6 linhas de sorteio | ~15 linhas |
| berço por bloco no `__init__` | ~3 linhas |
| portão: `jardim_comum=False` idêntico bit a bit; `True` com um genoma replicado ⇒ DP exatamente 0 | teste |
| análise de trajetória (concordância, divergência, agrupamento) | script novo, CPU |

O portão do meio é o que dá confiança: **no jardim comum, o mesmo genoma tem de dar
variância exatamente zero.** Foi ele que reprovou a minha primeira tentativa e apontou as
seis linhas.
