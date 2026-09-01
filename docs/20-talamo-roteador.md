# 20 — Tálamo: a rede que não processa, ROTEIA

**Brainstorm Leonardo, 2026-08-31:** *"uma rede recebe sinais de sensores e
sabe pra qual outra rede enviar — não processa os dados, entende O QUE SÃO,
analisa como o sinal É e roteia pra área adequada que já nasce com uma base
daquilo. Se for visão, joga pra parte da visão; ou acha a fórmula, ou dá um
help."*

## 1. Isso é o tálamo — e fecha a pilha que estamos montando

| doc | peça | papel |
|---|---|---|
| 16 | endócrino | QUANDO mudar o modo (hormônios) |
| 17 | prefeito | o MUNDO que governa |
| 18 | caixa de ferramentas | COMO ler cada sinal (operadores) |
| 19 | órgãos calculistas | QUEM resolve (cálculo como órgão) |
| **20** | **tálamo** | **PRA ONDE vai cada sinal (roteamento)** |

A sacada central dele: o roteador **não precisa entender o conteúdo** — só a
ASSINATURA do sinal. E assinatura é estatística barata: espectro, τ de
autocorrelação, esparsidade, faixa, periodicidade. É a mesma família da tese
byte (bit 5 = case: o TIPO está visível na superfície) e os operadores do doc
18 são exatamente os detectores (sinal que melhora sob passa-baixa é ruidoso;
sinal previsível por EMA tem τ lento; sinal que a derivada explica é
tendência). **Caixa de ferramentas = sensor de assinatura do tálamo.**

"Área que já nasce com uma base" = biblioteca de órgãos com prior inato
(nível 1 da hierarquia do doc 19, escolhido pela evolução). O tálamo completa:
órgãos existem → assinatura identifica → rota entrega.

## 2. ⚠️ O REFUTADO que quase mata isso (e como desviar)

O CONTEXTO deste projeto registra: **"rotear por escala medida: perdeu do
aleatório"** — rotear por uma estatística escolhida À MÃO já falhou aqui. E o
doc 15 §3 mostrou surpresa-genérica como gatilho: 341 falsos positivos.

Regra de desvio (mesma lição 2×): **o roteador é EVOLUÍDO/selecionado pela
qualidade do roteamento (gate σ(w·φ) sobre um banco de assinaturas), nunca
fiado numa estatística que NÓS achamos informativa.** A evolução decide quais
assinaturas importam — nós só oferecemos o banco.

## 3. Por que rotear paga: eficiência (a raiz do doc 19)

Cérebro sempre-ligado paga todos os órgãos todo passo. Tálamo paga o órgão SÓ
quando consultado — "não precisa de tudo carregado". Já medido em outros
contextos: gate por pressão = 17% do custo com 3× de ganho (doc 12 §4.2);
Qwen MLP 95-99% esparso; colibrì streama expert do SSD só quando chamado.

## 4. E6 — experimento no lab (depois do E4)

Setup: táxi com biblioteca de órgãos (mem custo, mapa serviço, rota calculada,
janelas) + custo metabólico POR CONSULTA (κ·uso no fitness). Braços:
1. sempre-ligado (todos os órgãos todo passo, paga tudo) — teto de fitness
2. tálamo evoluído (gate σ(w·φ) decide quem consulta a cada passo)
3. CONTROLE: gate ALEATÓRIO com o mesmo duty-cycle do braço 2
4. CONTROLE: rotear por estatística fixa à mão (replicar o refutado — deve perder)

Predições a registrar antes de rodar:
- fitness(2) ≈ fitness(1) com fração do custo (eficiência sem perda);
- roteamento CONTEXTUAL: mapa consultado quando necessidade alta em território
  novo; rota calculada quando carregando passageiro em região congestionada —
  medível por correlação consulta×contexto;
- (3) e (4) perdem de (2) além do ruído — senão o tálamo é decoração.

## 4.1 E7 — cérebro MONTADO com telemetria de nascimento (pedido 2026-08-31)

*"Recriar cada parte além do tálamo e ver como fica da primeira geração ao
final — como se distribui, como funcionou, que dados pegamos."*

UM ser com todas as partes: entradas→caixa de ferramentas (18) → órgãos
(mem custo, mapa serviço, rota calculada, janelas, corpo) → tálamo gateando
consultas (20) → score; custo metabólico por consulta. E o produto principal
NÃO é só o fitness final — é o FILME do cérebro se organizando:

**Dados capturados POR GERAÇÃO (população/elite, não só campeão):**
| série | mostra |
|---|---|
| `alocacao_elite` (média de \|w\| por bloco) — **JÁ IMPLEMENTADO em toda evolução** | qual "área do cérebro" engorda/murcha ao longo das gerações |
| duty-cycle de cada gate do tálamo | quando cada órgão passa a ser consultado |
| custo metabólico médio | a eficiência caindo (ou não) com as gerações |
| correlação consulta×contexto | o roteamento ficando CONTEXTUAL |
| fitness percentis + diversidade | população aprendendo vs sortudo puxando |

Visual: área empilhada da alocação por gerações (o "mapa cortical" do táxi
se formando) + linhas de duty-cycle. Painel dedicado.

**Lição do E4 a incorporar antes de rodar**: paisagem do órgão é BIMODAL
(semente presa em confiança negativa afunda; semente na bacia positiva vence)
— o E7 nasce com SEMEADURA (parte da população começa com gates abertos e
confiança positiva) e mutação por bloco, senão o filme registra o vale, não o
cérebro. Predições registradas em PREDICOES.md antes de rodar.

## 5. Onde desagua (IARA)

O mesmo tálamo em escala de bytes: assinatura do stream (estatística de bytes)
roteia pro especialista — o roteador-97% da IARA já é um proto-tálamo. Se o E6
pagar no táxi, a arquitetura unifica: sensores → tálamo → órgãos (inatos +
resolvidos em vida) → endócrino modula → prefeito governa. A pilha inteira
nasce de UMA pressão: eficiência (Garimpo/metabolismo) — a intuição-raiz dele.
