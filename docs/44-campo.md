# 44 — E43 Campo: o mundo contínuo (spec, 2026-09-03 22:15)

**Leonardo:** *"faça com campo contínuo e escale pra cidades maiores; rode tudo de
novo do zero com as descobertas; dar tudo o que o ser precisa: fome E sede
(gasolina e água), otimizar tudo (viver; dinheiro é extra — acumular dinheiro
= aprendeu a poupar, como a gordura); escolher quantos litros abastece, pra
ver se entende de cálculo."*

## 1. Por que campo e não nó
Grafo: gather de vizinhos por passo + matriz n×n. Campo: posição (x,y),
8 direções, serviços = pontos, distritos = regiões, ruas/trânsito = campo de
custo (textura GPU) sentido à frente. Custo por passo não depende do tamanho
do mapa. Caminho vira coisa TRAÇADA, não escolhida de uma lista — é onde 3
termos deixam de bastar e córtex/memória têm o que fazer.

## 2. Mundo (`src/campo.py`, tudo tensor na GPU; nada por passo na CPU)
- Mapa L×L (presets: pequeno 200, medio 400, grande 800). Custo c(x,y) ∈
  [1,3]: textura 64×64 (ruído suavizado na GPU) amostrada bilinear; multiplica
  gasolina e calor por unidade andada. Densidade de serviços por área fixa
  (posto 1/2500 u², comida 1/2500, água junto do posto e da comida, oficina
  1/2000, descanso 1/3000, loja 1/5000), mínimo 3 de cada.
- Distritos: K = round(6·L/200) centros; distrito(x,y) = centro mais perto.
  Alíquota [.05,.35], multiplicador de preço [0.7,1.6], aluguel ×[0.5,2.0]
  por distrito (sorteados pela seed do mapa). Casa = distrito de nascimento.
- Passageiros: NPX pontos vivos por mapa; destino sorteado com prob ∝
  1/(1+d) e ≥30 % em outro distrito; embarque/desembarque dentro de raio r=3;
  tarifa = 1.2 + 0.12·distância × multiplicador da ORIGEM; imposto pela origem.
- Tempo: passo = 1 min; dia 240; noite 22h–6h (posto fecha, só água/comida
  no posto ficam); vida = 5 dias (T=1200) — mesma escala do grafo.
- Movimento: 8 direções + ficar; velocidade 1.0 u/passo (× 0.7 à noite).
  Gasolina por passo = 0.9·c(x,y)·peso; calor sobe com c e desce parado.

## 3. Corpo
gasolina (cap 100), **água** (cap 100; cai 0.25/passo + 0.5 quando calor > 60;
< 10 → fere 0.15/passo), fome (como pacote: sobe 0.32/passo; > 90 fere),
fadiga, calor (> 92 desliga), vida, dinheiro, reserva/gordura (cap 120,
perda 2 %/dia), dano acumulado. Pane (gasolina 0) = reboque até o posto mais
perto cobrando calorias da reserva → vida (E15). Morte = vida ≤ 0.

## 4. Decisões (G = 9 movimentos + S serviços) — argmax único, como hoje
Serviços quando dentro do raio: posto × {25, 50, 75, 100, 150 L} (150 =
enche + 50 na reserva com 15 % de perda; preço/L × distrito), água × {50,
100}, comida (refeição 90), descanso (em casa: aluguel já pago; fora: hotel
= 8 × preço do distrito), oficina (repara), loja (upgrades, v2 = desligada).
Sentidos por opção (NF ≈ 30): pra cada direção, distância ao destino e aos
serviços mais perto DEPOIS do movimento, custo à frente, alíquota/preço do
distrito à frente, se está em casa; corpo: gasolina, água, fome, fadiga,
calor, vida, dinheiro, reserva, dano, tem passageiro, hora (sin, cos), noite.

## 5. Régua e avaliação
Régua A (E41): fit = vivo·(1 + vida/100 + min(dinheiro,100)/100 + 0.05·ent
+ 0.5·reserva/120) − pena·morto. Retrato por campeão (genes, ativação,
trajetórias no mapa, litros escolhidos, reserva ao longo da vida).
Protocolo: 5 sementes, R=16, G=120, 3 mapas de teste nunca vistos, 3
tamanhos.

## 6. Predições (antes de rodar)
52. mínimo-3 perde ≥ 1.0 de fit pro linear completo em L=400 (o campo exige).
53. litros evoluídos: mediana ≥ 75 em L=800 e ≤ 50 em L=200; reserva média
    dos vivos > 20 em L=800 (poupança emerge onde a viagem é longa).
54. campo ≥ 5× mais rápido por passo que o grafo n=500 com o mesmo B.
55. reflexo de emergência (portão em gasolina) reaparece do zero em ≥ 3/5
    sementes em L=400 — o joelho é universal.

## 7. Fora desta fase
Profissões, prefeito, vários seres no mesmo mapa (fase 2), furo/óleo, loja.

## 8. Diário
- **22:20** `src/campo.py` v1: distâncias por força bruta = 320 ms/passo
  (65 k seres) — tensores de 300 MB por tipo de serviço.
- **22:30** v2: campos de distância e de distrito pré-computados na GPU
  (grade 128×128 por mapa), obs uma vez por passo, gasolina 0.25/u·custo →
  **25.7 ms/passo @ 65 536 seres, 0.29 GB de VRAM**; sem sync; reflexo com
  genes 0 == linear bit a bit; 4 mapas L=400 gerados em 0.31 s na GPU.
  Honesto (G=120) ≈ 62 min por braço; triagem ≈ 12 min.
- **22:35** fumaça (P=256, G=15, T=600): o ser "vence" parado (0 entregas,
  fome 100, água 0, 7 % mortos) — parar é de graça em vida curta (lição do
  E19). Fumaça passa a vida inteira (T=1200) e G=25; régua ganhou gradiente
  entre os mortos (morrer mais tarde > morrer cedo), senão deserto.
- **22:40** SerCamadas (agente) merged no main: 92 genes (tálamo 51–65,
  córtex 66–89, hipocampo 90–91), nasce bit-igual ao reflexo; portões ok.
  Ainda é do grafo (usa m.e15_dist/obs de 26 features) — a versão de campo
  precisa de adaptação de índices (fase seguinte).
- **22:50** v3: distância EXATA por opção ao ponto mais perto (a grade de
  1.5 u empatava o argmax perto do alvo: o ser parava a 4 u da água e nunca
  entrava no raio 3); raio 4; 10 ms/passo @ 49 k. Perito à mão ainda morria:
  água drenava 0.75/passo com motor quente (100 u = 2 h) e o calor subia
  1.5/passo (desligava a cada 45 passos) → recalibrado (água 2 dias, calor
  135 passos de estrada contínua, gasolina 0.15/u).
- **23:00 — achado de fundo:** no contínuo, política LINEAR sobre distâncias
  é um CAMPO DE POTENCIAL: a soma das atrações tem ponto de equilíbrio no
  meio; o perito −1/−1/−1/−1 vive 949 passos com ZERO entregas, parado entre
  passageiro, comida e água. O grafo escondia isso (nós discretos). O campo
  EXIGE escolher um alvo por vez: `Produto` (necessidade × distância com
  portão) — a família do E17/E29b vira o mínimo do campo.
- **23:05** economia matava: 1–2 entregas não pagam aluguel + gasolina (~200
  por vida). Calibração: passageiros nascem a ≤ 45 u (12), tarifa 3 + 0.25/u,
  gasolina 0.3/L e consumo 0.15/u, água 0.05/L, comida 2, aluguel 4·distrito,
  dinheiro inicial 100. Perito bilinear: 16 % vivos, 4 entregas, 15
  refeições (come demais — mal calibrado à mão; a evolução ajusta). Gradiente
  existe. Fumaça de evolução lançada (linear / reflexo / produto, régua B).
  **Predição 56:** linear ≥ 0.9 mortos (preso no potencial); produto ≤ 0.6;
  reflexo entre os dois (portão só na gasolina).
- **23:20** merge do agente MUNDO (grafo 104/500, moradia, hotel) no main;
  portões: testes ok, testes_e42 ok, campo identidade ok; `--perito` deu
  "Memory access fault by GPU node-1" UMA vez (GPU disputada por 3
  processos) e PASSOU na repetição (spread 0.000) — falha transitória do
  driver sob contenção, não de identidade; registrada.
- **23:25** Leonardo: "era para o prefeito pegar isso e resolver" — a
  calibração à mão do doc 44 §8 é chute; vira E44 (docs/45-prefeito.md).
- **23:40** auditoria do campo (agente) aplicada: G1 notas de movimento
  centradas (mover-vs-servir decidido pela necessidade, não pelo nível das
  distâncias); G2 "ficar" custa marcha lenta e o gradiente entre mortos paga
  comer/beber/abastecer, não só morrer tarde (a pedra era o p90 da população
  inicial); G3 escala direcional 1/vel; G4 litros dependem do que CABE no
  tanque (+ sobra pra reserva); G5 dívida com piso e dano gradual; G6 fadiga
  para o táxi, descanso nunca aumenta fadiga; G7 uma varredura de serviços
  por passo (15 → 5); G8 `Produto` sem lista Python (sync); G9 código morto.
  Resultado: perito bilinear 0 % → **40 % vivos, 6.6 entregas, 3.6
  refeições, 3 abastecimentos de ~100 L, panes 0.4**; linear −1s segue
  paralisado (0.1 entregas, 80 % mortos) — o mundo discrimina arquitetura.
  9.8 ms/passo @ 49 k, sem sync. Fumaça relançada com o código auditado.
- **00:05 — REGRA 21: um processo na GPU por vez.** "Memory access fault by
  GPU node-1" apareceu 3× hoje, sempre com um processo `torch.compile`
  rodando junto com outro processo na GPU (perito + fumaça; teste de
  identidade + fumaça; o auditor viu sob troca de arquitetura com o job do
  outro agente a 99 %). Nunca reproduziu sozinho. Tudo passa pela fila
  (`fila2.sh --depois-de`); testes de identidade viram script
  (`src/testes_campo.py`) enfileirado. Compile no campo: 1.51 ms/passo @ 49 k
  (honesto G=120 ≈ 4 min/braço); identidade eager×compile: o auditor achou
  bit a bit no Linear/60 passos; meu teste (Produto/200) deu diferença —
  quantificar no script (mesma regra do grafo: todos os braços de uma
  bateria no mesmo modo, gravado no JSON).
- **00:15** fumaça 4 (código auditado, eager), braço linear: **mortos 0.01
  com ZERO entregas** — come, bebe o mínimo e vive das economias (100 → 51).
  Sob bem-estar, com vida de 5 dias, viver de poupança é a estratégia ótima.
  É o ponto do Leonardo ("você treina só 5 dias"): o horizonte curto não
  cobra trabalho. Vida passa a 10 dias (`--dias`, padrão 10; T=2400) — com
  compile são ~3 min por braço honesto mesmo assim. **Predição 59:** com 10
  dias o linear "vive de renda" colapsa (mortos ≥ 0.5) e o produto só
  sobrevive entregando ≥ 6 por vida; a reserva (gordura) aparece como
  poupança de quem trabalha (res médio dos vivos > 10).
- **23:50** fumaça 4 (eager) TRAVOU no braço reflexo: 1h06 de processo, log
  parado desde 22:41, GPU 99 % sem progresso — stream travada depois das
  falhas de memória (regra 21). Morto pelo PID; fila segue (portões do
  campo → fumaça 5 de 10 dias compilada → prefeito → portões do grafo). O
  resultado do linear na fumaça 4 (0.01 mortos, 0 entregas, viver de
  poupança) fica registrado; reflexo/produto da 4 não existem.
- **23:46 portões do campo (`testes_campo.py`, GPU sozinha):** compile ×
  eager: 1–2 seres de 384 com posição diferente por ≤ 9.5e-07 (Linear,
  Produto, Reflexo; T=60 e 300), demais campos 0 ou 7.6e-06 (res/dinh) —
  arredondamento, SEM amplificação de trajetória (no grafo amplificava). Genes
  0 == Linear bit a bit sob compile (Produto, Reflexo). **1.34 ms/passo @
  49 k; sem sync.** Compile é o modo padrão do campo; regra do grafo
  mantida: todos os braços de uma bateria no mesmo modo.
- **23:51 fumaça 5 (10 dias, compilada, régua B, L=200, G=25, 1 semente):**
  linear 11.3 entregas / 5.9 abastecimentos de 45 L / reserva 64 / dinheiro
  73; produto 10.0 / 3.6 × 66 L / 56; reflexo 9.3 / 1.9 × 122 L / 55 —
  **os seres trabalham, poupam e abastecem; e 100 % morrem com fome 87–100
  e dinheiro no bolso.** Predição 59: "viver de renda colapsa" ✓; "produto
  sobrevive" ✗; entregas ≥ 6 ✓; reserva > 10 ✓. O que falha agora é COMER
  (comida custa 2–3, eles têm 60–73). Diagnóstico enfileirado (refeições
  por vida, estado na morte, comer forçado).
- **00:00 diagnóstico (diag_campo.py):** campeões da fumaça 5 morrem no DIA 3
  (733/2400) com 10 entregas: sprint de entregas, comem 1–5×, bebem 1×, e
  "comer forçado" não muda NADA — nunca chegam a 4 u de um ponto de comida
  (16 pontos em 200×200; o táxi vive na rota). Acesso, não decisão.
- **00:05 mundo: loja no posto (comida e água vendidas no posto; água também
  no ponto de comida) e raio 6.** Mesmo campeão: come 9.6×, bebe 7.8×, vive
  até o dia 5.3, entrega 17.7; fome ≥ 90 na morte cai de 84 % pra 9 %. Agora
  morre de AVARIA (14.8 eventos: 6.2 panes + calor/exaustão) e 29 % quebram
  — o que a evolução tem de aprender (abastecer antes, descansar; é onde o
  reflexo entra). Fumaça 6 (10 dias, 3 braços) e prefeito no mundo novo
  lançados em fila. Predição 60: na fumaça 6, produto e reflexo ≤ 0.7 de
  mortos (era 1.00) e o reflexo tem menos panes que o produto.
- **00:07 fumaça 6 (loja no posto, 10 dias):** 1–5 % mortos nos 3 braços com
  0.1 entregas e 0 abastecimentos — **vive de poupança 10 dias inteiros**
  (100 → 11 de dinheiro). A poupança inicial dura mais que a vida. Predição
  60 ✗ (não pelo motivo previsto). Correção: **nasce pobre** (dinheiro
  inicial 100 → 20; aluguel 4–8/noite quebra no dia 3 sem trabalhar).
  Predição 61: com 20, linear/produto/reflexo entregam ≥ 8 por vida ou
  morrem; mortos entre 0.3 e 0.8; o reflexo tem menos panes que o produto.
- **2026-09-04 00:10–08:21** máquina desligada (Leonardo); a fila morreu no
  meio da fumaça 7. **E44b (prefeito no mundo "vive de poupança")**: sem
  0.05 / com 0.01 mortos, 0.1 entregas nos dois — prefeito irrelevante onde
  ninguém trabalha (esperado). **Fumaça 7, braço linear (nasce com 20):**
  0.96 mortos, **16.3 entregas**, fome 43 (come), água 73, 2.7
  abastecimentos de 94 L, reserva 17, dinheiro 29, panes 4.7 — trabalham,
  comem, poupam e morrem. Predição 61: entregas ≥ 8 ✓; mortos 0.3–0.8 ✗
  (0.96 em G=25). Braços reflexo/produto relançados + diagnóstico do linear
  na fila (12:05).

## 9. E45 — Base fechada (ideia do Leonardo, 2026-09-04 12:15)
"Como no Universe/forja: reproduzir o cérebro do campeão por fórmula fechada;
treinar uma base quase pronta e deixar a evolução só pro resto." Política
linear = nota Φ·W ⇒ ridge fechado `W* = (ΦᵀΦ+λI)⁻¹ΦᵀY` a partir de um
PROFESSOR de utilidade de um passo (o que cada opção compra em vida, fome,
água, tanque, dinheiro; movimento = reduzir a distância ao que FALTA,
necessidade ao quadrado). Argmax é invariante a deslocamento → Y centrado
por linha. `src/base_fechada.py`: coleta ~200 k estados (professor com
ruído), resolve W_base (movimento por ridge; serviços por coluna), mede a
base sozinha, e compara evoluir do zero vs semeado da base (25 ger.).
**Predições 62–64 (antes de rodar):** 62. base sozinha ≥ 0.6 de vivos em 10
dias (o professor guloso resolve o básico); 63. semeado da base em 25 ger.
≥ do-zero em 25 ger. por ≥ 20 pp de mortos; 64. o preço é diversidade
(fingerprint entre sementes < 0.3). Cláusula: se a base sozinha morrer
(≥ 0.8), o professor está errado (escalas entre movimento e serviço), não a
ideia — corrigir o professor antes de julgar.
- **12:08 fumaça 7b (pobre):** reflexo **0.88 / 18.4 entregas** / 4.7
  abastecimentos; produto 0.98 / 13.9. Diagnóstico do linear pobre: morre
  no dia 4.4 com 15 entregas; fome ≥ 90 só 8 %, sede 1 %, quebrado 15 %;
  **dano 176 = 12 avarias/vida (4.7 panes + ~7 desligamentos por calor)**.
  Comer forçado não muda nada (já come). A conta do calor não fecha: a 70 %
  de rodagem o motor esquenta +0.14/passo líquido → desliga a cada ~7 h
  com 10 de dano → morto no dia 4. Física do corpo (não é alavanca do
  prefeito): `calor_sobe` .25 → .15 (sustentável a ~70 % de rodagem),
  `D_QUENTE` 10 → 6. Predição 61: entregas ≥ 8 ✓ (14–18), mortos 0.3–0.8 ✗,
  "reflexo menos panes" ✗ (4.6 vs 3.4) mas reflexo vive mais. Fumaça 8 (calor
  calibrado) na fila atrás do E45. **Predição 65:** com o calor sustentável,
  reflexo ≤ 0.6 de mortos e ≥ 20 entregas em 10 dias; linear ≤ 0.8.
- **12:11 E45 v1:** professor guloso sozinho morre 1.00 com 0.2 entregas →
  base ajustada nele nasce morta (1.00, 0 entregas) e **semear dela PIORA**
  (1.00 / 4.9 entregas vs do-zero 0.96 / 16.3): prior errado custa.
  Cláusula da predição 62 ✓: o professor está errado, não a ideia. Causa:
  utilidade de movimento em distância ABSOLUTA (diferença entre direções
  ~0.1) afogada por ruído 0.5. v2: utilidade = variação da distância
  ponderada pela necessidade vs ficar (±1/passo), ruído 0.15, ficar sem
  necessidade custa; o script aborta se o professor morrer ≥ 0.8. Na fila
  atrás da fumaça 8.
- **12:16 fumaça 8 (calor sustentável, pobre, 10 dias) — a virada:** linear
  **0.63 mortos / 26.7 entregas / 10 abastecimentos de 50 L / reserva 26**;
  reflexo 0.69 / 26.1 / 47 L; produto 0.77 / 23.9 / 74 L. De 0.96 pra 0.63
  com um ajuste de física; o ser trabalha, come, bebe, abastece e POUPA.
  Predição 65: entregas ≥ 20 ✓; reflexo ≤ 0.6 ✗ (0.69); linear ≤ 0.8 ✓.
  Agora baterias de verdade, em série na fila: portão dos modos gaussianos
  (E46) → triagem L=200 (5 braços: linear, reflexo, produto, modos,
  mínimo-3) → triagem L=400 → prefeito (fumaça) neste mundo → E45 v2 já
  estava antes. **Violação da regra 21 registrada:** rodei o teste dos
  modos com a fumaça na GPU → memory access fault no meu teste; a fumaça
  sobreviveu. Sem exceção: todo teste pela fila.

## 10. E46 — Modos gaussianos (ideia do Leonardo, 12:20)
"Gaussiana com 3 direções; depende de onde se observa." K=3 gaussianas no
espaço das necessidades (tanque, água, fome, dinheiro, passageiro), cada
uma com centro, largura por 3 eixos (tanque+água / fome+dinheiro /
passageiro) e um vetor de pesos de movimento próprio; a mistura (softmax
das densidades × ganho) decide "de onde o ser olha". Nasce == linear
(pesos por modo = 0). É a generalização principiada do "necessidade ×
distância com portão" que salvou o campo. **Predições 66–67:** 66. na
triagem L=200 os 3 centros se separam (distância ≥ 1 σ entre pares em ≥
2/3 sementes) e o modo que ganha responsabilidade quando `tem_pax`=1 tem
o peso de `d_alvo` mais forte; 67. modos ≥ linear em mortos por ≥ 5 pp na
triagem; se os centros colapsarem num só, o mundo ainda não pede modos.
- **12:38** E45 v2 ficou 18 min sem escrever nada no log (regra 21: morto
  pelo PID); relançado com progresso no log e `timeout 1500`, atrás da
  bateria 1. **Portão do E46 (modos gaussianos) passou:** genes 0 == linear
  (eager e compile), sem sync, NP 132, responsabilidades iniciais
  0.35/0.33/0.32. Triagem L=200 (5 braços) rodando.
- **13:00 triagem L=200 (3 sementes, G=40, 10 dias, régua B, nasce pobre,
  loja no posto, calor sustentável):**

| braço | mortos | entregas | panes | abastecimentos × L | reserva |
|---|---|---|---|---|---|
| linear | 0.62 | 26.6 | 6.2 | 7.2 × 74 | 27 |
| reflexo | 0.61 | 26.6 | 5.6 | 8.5 × 57 | 21 |
| produto | 0.63 | 26.6 | 5.9 | 6.7 × 78 | 29 |
| modos gaussianos K=3 | 0.63 | 26.2 | 6.4 | 7.5 × 66 | 24 |
| **mínimo 3 (destino, posto, tanque)** | **0.57** | **28.6** | **5.1** | 10.1 × 50 | 22 |

  Todos empatam na régua da triagem, e a política de 3 termos é a melhor —
  como no grafo. **Predição 52 ✗ (o campo não pede mais que 3 termos) e 67 ✗
  (modos = linear).** Mecanismo: a loja no posto fez comida e água caberem
  na ida ao posto, que os 3 termos já fazem; os sentidos extras (fome, água,
  dinheiro, distrito) não têm o que decidir. Pra exigir cérebro os serviços
  têm de ficar SEPARADOS: **E47 (`--sem-loja`) na fila** — predição 68:
  sem loja, mínimo-3 perde ≥ 10 pp de mortos pro produto/modos (precisa de
  d_comida/d_agua), e a mortalidade geral sobe (mundo mais duro). Retratos
  dos campeões (mínimo-3, linear, modos) enfileirados.
