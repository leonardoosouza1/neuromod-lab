# 18 — Ferramentas matemáticas evoluíveis (pesos que usam/resolvem fórmulas)

**Origem (Leonardo, 2026-08-31):** *"e se os pesos tivessem como se especializar
em matemática? a matemática fica ali estática — fórmula ou leis — e se a gente
alterasse conforme o uso? deixar o próprio modelo modelar partes do cérebro...
se tem muito ruído ele separa, se passa-baixa pega o sinal, ele aplica...
se os próprios pesos resolvem equações, podem ajudar a resolver o próprio
modelo no runtime, na inferência e no treino."*

## 1. A ideia NÃO é fora da curva — é a convergência de 4 coisas já validadas

| peça | onde já foi validada |
|---|---|
| neurônio líquido ≡ EMA; banco de τ = banco de filtros multi-escala | doc 01 (analítico) |
| diferença de dois τ ≈ derivada (=MACD); PID = 3 neurônios | doc 01 §3.1 |
| readout ótimo por FÓRMULA FECHADA (ridge, vértice da parábola) | doc 01 §5; forja/ W*=(ΦᵀΦ+λI)⁻¹ΦᵀY validado 2026-08 |
| 2 shifts cobrem qualquer τ com <5% de erro, zero multiplicação | esparsidade §7 |

O que é NOVO na formulação dele: (a) a SELEÇÃO do operador é evoluível por
canal — o cérebro escolhe qual matemática aplicar em cada entrada; (b) a
fórmula fechada roda EM VIDA (runtime) — o ser resolve seus próprios pesos
com a experiência que acumulou, sem backprop.

Cuidado com o refutado: doc 15 provou que modular τ POR ORÁCULO perde do
banco fixo. Aqui não é isso — é seleção EVOLUÍDA e ESTÁTICA por canal (qual
filtro cada entrada recebe), que É o banco, com a fiação evoluída.

## 2. Arquitetura testável AGORA no lab: `CaixaFerramentas`

Cada feature de entrada x_i passa por UM operador do banco antes do score:

| operador | fórmula | quando paga (predição) |
|---|---|---|
| identidade | x | canal limpo |
| passa-baixa | EMA_τ(x) | canal RUIDOSO (tira ruído, fica sinal) |
| passa-alta | x − EMA_τ(x) | canal com drift (só a novidade importa) |
| derivada | EMA_τ1(x) − EMA_τ2(x) | tendência importa (está piorando?) |
| atraso | x de k passos atrás | crédito atrasado |

Genes: por canal, mistura contínua sobre os operadores (softmax de 5 logits —
diferenciável pra evolução, sem gene discreto) + τ em log (I3). Portão de
identidade: mistura toda na identidade ≡ reativo bit a bit.

**Mundo que força a escolha**: variante `ruido` — features de OBSERVAÇÃO
corrompidas com ruído POR CANAL (níveis diferentes e fixos por mundo: d_alvo
limpo, congestão ruidosa, corpo com drift...). Predição registrável: a mistura
evoluída correlaciona com o nível de ruído do canal (passa-baixa nos sujos,
identidade nos limpos) — "a rede equaliza a entrada" é exatamente isso,
falsificável com um scatter mistura×ruído.

## 3. Pesos que se RESOLVEM em vida (fase 2, maior)

Readout por fórmula fechada durante o episódio: o ser acumula (Φ, Y) da
própria experiência — features vividas × resultado (entregou? quebrou?) — e
a cada K passos RESOLVE W = (ΦᵀΦ+λI)⁻¹ΦᵀY para o próprio score. Aprendizado
em vida sem gradiente, por álgebra. Perguntas de projeto antes de codar:
- Y = o quê? (Δfitness local? entrega em ≤H passos? — reward shaping mora aqui,
  07 §11 manda inspecionar trajetória contra hack)
- λ pela Lei do Garimpo (2σ²·ln M) — já temos a régua.
- ΦᵀΦ é 36×36 = barato por mundo; solve em lote na GPU já foi feito (forja).
- Contrato de perf: acumulação em atualizar(), solve fora do grafo a cada K.

Gate G1 desta fase: o solve em vida precisa bater o MESMO ser com pesos só
evoluídos, no MESMO mundo, além do ruído entre sementes — senão é enfeite.

## 4. Ordem

1. `CaixaFerramentas` + mundo `ruido` + predição do scatter (barato, 1 dia).
2. Se 1 pagar: readout resolvido em vida (fase 2).
3. Se 2 pagar: o mesmo mecanismo vira candidato pro cérebro dos seres do
   Universe e pros órgãos da IARA (o ser que se re-resolve é a visão-mãe).
