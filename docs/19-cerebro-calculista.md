# 19 — Cérebro Calculista: eficiência como raiz, cálculo como órgão

**Brainstorm Leonardo + Claude, 2026-08-31.** Visão dele: *"o ponto inicial de
tudo é ser eficiente e quem pode ser é a rede de pesos — eles mesmos se
ajustam. O cérebro consome pouca energia e lida com muitas coisas porque é bom
de cálculo. Partes da rede que fazem cálculo podem DAR a resposta. A visão tem
sua parte alocada; o modelo descobre sozinho como ajustar os pesos da visão."*

## 1. A tese em uma linha

**Rede neural comum APRENDE até o que dava pra CALCULAR — essa é a
ineficiência. O cérebro faz o contrário: cristaliza algoritmos como órgãos e
só gasta plasticidade no resíduo.**

Retina = passa-alta espacial (centro-periferia). Cóclea = Fourier mecânico.
Cerebelo = calculadora de modelo-forward (80% dos neurônios em 10% da massa —
neurociência já anotada). Hipocampo = recall associativo com algoritmo
conhecido. Nada disso foi "aprendido como peso livre" — evolução achou o
ALGORITMO e a vida só ajusta coeficientes.

## 2. A hierarquia dos 3 níveis (o coração do programa)

| nível | o que é | quem resolve | custo | escala de tempo |
|---|---|---|---|---|
| 1. ESTRUTURA | qual operador/órgão usar em cada canal | evolução | caro | gerações |
| 2. COEFICIENTES | os números do operador escolhido | **fórmula fechada em vida** (W=(ΦᵀΦ+λI)⁻¹ΦᵀY da experiência própria) | barato (álgebra) | segundos |
| 3. RESÍDUO | o que não tem estrutura conhecida | pesos livres evoluídos | o mais caro | gerações |

**Eficiência = empurrar conhecimento pra CIMA na hierarquia** (de peso caro
pra cálculo barato). A pressão que empurra é o custo metabólico — e nós JÁ
temos a régua: Lei do Metabolismo met=σ²(1+2·dof)=AIC e Lei do Garimpo
2σ²·ln(M) (iara-água, validadas). E4 do Universe provou que preço
termodinâmico DESLOCA o ótimo cognitivo — logo a pressão de eficiência muda o
que a inteligência VIRA, não só quanto custa.

## 3. O que JÁ existe no ecossistema (não começar do zero)

| peça da visão | onde já está validado |
|---|---|
| neurônios que calculam e DÃO a resposta | Computable Neurons: perceptron/ELM/Hopfield/Oja/readout fechado como órgãos; verificador computado sei-vs-blefo 100% |
| pesos resolvidos por álgebra, sem gradiente | forja (W* fechado), doc 01 §5 (ridge = vértice da parábola) |
| banco de filtros como primitivo | doc 01: neurônio≡EMA, derivada=2 τ, PID=3 neurônios; 2 shifts ≅ qualquer τ |
| não carregar tudo / só o necessário | Qwen MLP 95-99% esparso; atlas 350k neurônios (especialistas profundos); colibrì streama experts do SSD (744B em 25GB); gate por pressão doc 12 (17% do custo, 3× ganho) |
| alocação regional ditada pelo uso/corpo | N1: corpo dita arquitetura (corr 0.972; elefante 98% na tromba); cerebelo/córtex |
| cálculo substituindo parâmetro | reflexo raiz-digital 0-param (mod9/Kaprekar); água÷grau multi-hop 100% |
| sobrevivência enxuga ao essencial | iara-água: ser útil ↘ ~39 params |

## 4. O experimento MATADOR: ressuscitar o `ruas` com um órgão calculista

Hoje (2026-08-31) o mundo `ruas` morreu com mecanismo claro: política de 1
salto não reroteia — lembrar a congestão não adianta se ninguém RECALCULA a
rota. Pois é EXATAMENTE o buraco que um órgão calculista preenche:

**E4 — órgão-Dijkstra**: o táxi guarda MemCusto (congestão lembrada por nó,
já implementada) e um órgão de CÁLCULO roda caminho-mínimo sobre os custos
LEMBRADOS (não sobre o oráculo) a cada K passos. O peso evoluído só decide o
quanto confiar no órgão.

- Controle já medido: memória sem cálculo = teto 0 (PREDICOES §ruas).
- Predição: memória + cálculo > reativo além do ruído no MESMO mundo onde
  memória sozinha deu zero. Se confirmar: **cálculo-como-órgão paga exatamente
  onde peso puro não alcança** — a tese inteira em um experimento, com o
  negativo de hoje como controle perfeito.
- Custo: Floyd-Warshall (26³) por mundo a cada K=32 passos, em lote na GPU —
  barato (já fazemos igual no gerar_cidade).

## 5. Escada completa (cada degrau falsifica algo)

| exp | pergunta | predição registrável |
|---|---|---|
| E1 `CaixaFerramentas` + mundo `ruido` (doc 18) | evolução casa operador com o canal? | mistura evoluída correlaciona com ruído por canal (passa-baixa nos sujos) |
| E2 pesos que se RESOLVEM em vida | álgebra em vida > evolução pura quando o mundo muda por instância? | mundo `leis-próprias` (tarifa/custo/risco sorteados POR CIDADE): ser que se re-resolve bate ser de pesos fixos; no base (estático) empata — o ganho é da adaptação, não do truque |
| E3 orçamento competido (auto-alocação) | regiões emergem por demanda? | orçamento fixo de unidades + custo metabólico: perfil de alocação difere POR MUNDO além do ruído (semgps→mapa, ruido→filtros) — o "córtex visual" do táxi cresce onde o mundo cobra |
| E4 órgão-Dijkstra no `ruas` | cálculo paga onde peso não alcança? | ver §4 |
| E5 verificador computado | o órgão sabe quando NÃO sabe? | portão sei/não-sei das ativações (já validado na IARA) acoplado ao táxi: abster de corrida ruim |

Ordem sugerida: **E4 primeiro** (controle já pago, resposta mais nítida),
depois E1, E2, E3, E5.

## 6. Perigos e refutados (pra não escorregar)

- "Treinar rede PRA fazer matemática" (aritmética emergente em rede pequena):
  NÃO — Small-Model-No-Retrieval provou que rede de 2M não aprende nem recall
  associativo. A seta é a oposta: a rede CHAMA o órgão exato (calculadora como
  ferramenta), ou a matemática RESOLVE a rede (forma fechada). Nunca pesos
  imitando aritmética.
- Auto-ajuste de pesos em vida = fast weights/hypernetworks — campo conhecido;
  nosso diferencial é (a) resolver por FORMA FECHADA (não gradiente), (b) sob
  economia de sobrevivência, (c) com evolução escolhendo a estrutura.
- Doc 15: porta de escrita não coexiste com aprendizado online da MESMA
  memória — o solve em vida precisa de buffer próprio (Φ,Y), separado da
  memória que a política lê.
- Y do solve em vida é reward-shaping disfarçado — inspecionar trajetória
  (07 §11) e testar 2 formulações de Y antes de acreditar.
- Cada degrau com portão de identidade (órgão com confiança 0 ≡ política sem
  órgão) e ruído entre sementes como régua. Sempre.

## 7. Onde isso desagua (a visão-mãe)

Se E1-E4 pagarem: os órgãos viram biblioteca compartilhada (táxi, Universe,
saci, IARA) — o ser não carrega tudo: ROTEIA pro órgão certo (Selector-not-
Generator, onde a tese água ganha), os coeficientes se resolvem em vida, e o
custo metabólico poda o resto. "Ser eficiente" deixa de ser otimização e vira
O PRINCÍPIO ORGANIZADOR do cérebro — que é exatamente a aposta IARA desde o
início, agora com escada experimental.
