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
  Genes dos modos (predição 66): os 3 centros SE SEPARAM (distância entre
  pares ≥ 1 σ em 3/3 sementes; pares 0.8–13 σ) e o modo com centro em
  "com passageiro" tem o peso de destino mais forte em 2/3 (s1: −2.03, s2:
  −2.75; s0 ✗). Mas o GANHO da mistura ficou baixo (0.53 / 0.17 / 0.09):
  a estrutura aparece e não é usada — bate com "modos = linear" na régua.
  Cláusula: o mundo (com loja no posto) ainda não pede modos; E47 decide.
- **13:35 E45 v2b:** professor guloso morre 1.00 (0.9 entregas; morre todo
  entre o dia 1.7 e 3.3 = quebra e a dívida fere): não valoriza dinheiro.
  v3: custo pesa pela escassez de dinheiro; trabalhar pesa mais quando pobre.
  E variante **clonagem**: professor = campeão evoluído (mínimo-3 da
  triagem, 43 % vivos) — Y = as notas dele; testa a ideia com professor
  garantido (quantas gerações a base poupa) e a transferência entre
  arquiteturas. Os dois na fila atrás do prefeito v2. Predição 69: a
  clonagem dá base sozinha ≈ campeão (±5 pp) e semeado-da-base em 25 ger.
  ≥ do-zero em 40 ger. (triagem); o professor v3 ainda morre ≥ 0.6 (guloso
  é míope pra dinheiro por construção).
- **13:35 triagem L=400:** 0.90–0.95 mortos em todos os braços, 8–9.5
  entregas (viagens 2× mais longas, renda cai pela metade); mínimo-3 ainda
  o melhor (0.90). Mapa grande em 10 dias pede vida mais longa ou economia
  mais densa — alavanca do prefeito (E44 v2 na fila).
- **13:35 E44 fumaça 3 (população que trabalha):** com o prefeito no teste
  **0.77 → 0.19 de mortos, 24 → 32.5 entregas**. Alavancas: imposto ×0.5,
  gasolina ×0.5, água ×2, comida ×0.5, aluguel ×0.5, tarifa ×2; obras: 27
  comidas + 26 postos. Funciona — talvez demais: o caixa vinha do imposto
  de 128–2048 cópias do mesmo táxi (cidade "grátis"), baixar preço não
  custava a ninguém, dobrar tarifa não afastava passageiro. **E44 v2 (moeda
  cruzada do prefeito):** caixa per capita (cidade de 16 táxis), subsídio
  pago do caixa e sobretaxa entra nele, tarifa com elasticidade (passageiro
  reaparece com prob. 1/(20·mult)), obra 60. Predição 70: com a moeda
  cruzada o ganho do prefeito cai mas fica (mortos −15 a −30 pp vs sem
  prefeito na triagem), e ele para de baixar tudo (≥ 1 alavanca acima de
  1.0 além da tarifa); se o ganho sumir, o prefeito v1 era só a cidade
  grátis.
- **14:06 E47 — serviços SEPARADOS (sem loja no posto), triagem L=200:**
  linear 0.91 / 18.6 entregas · reflexo **0.86 / 20.4** · produto 0.89 /
  18.8 · modos 0.92 / 17.4 · mínimo-3 0.89 / 19.8 — fome 80–82 no fim em
  todos: o mundo fica mais duro pra TODOS e ninguém aprende "comer longe da
  rota" em 40 gerações; mínimo-3 empata com produto/modos (predição 68 ✗).
  Leitura: o mundo já pede mais que 3 termos, mas a evolução não MONTA a
  capacidade (mesma lição do E30/E32/E35 no grafo: montagem é o gargalo).
  É o problema de fronteira: base fechada/clonagem, evolução cumulativa
  (120+ ger.), ou o prefeito aproximando a comida da rota.
- **14:06 retratos (L=200 com loja):** mínimo-3 abastece ~10× com
  EXATAMENTE 50 L e reserva 0–12; linear 5–10× com 50–90 L; modos 6–10×
  com 50–75 L. Publicado: retrato do mínimo-3.
  Leitura do retrato (mínimo-3, s0): **69 % dos mortos morrem de TANQUE
  VAZIO** (fome 10 %, sede 0, dívida 0); orçamento de tempo: andando 74 %,
  com passageiro 63 %; abastece SEMPRE 50 L (5/5 paradas na mediana) — 10
  paradas × 50 L = 500 L, exatamente o que queima em 10 dias: poupa dinheiro
  e morre de pane quando erra a conta. Genes fortes: oficina +4.7, posto50
  +3.6, água50 +3.2, comida +3.1, dinheiro −1.7, destino −1.7. É o joelho do
  E29b de novo: onde o reflexo deve entrar (honesto 120 ger. na fila:
  reflexo vs mínimo-3, 5 sementes).

## 11. E48 — Comitê com inércia (Leonardo, 14:15: "rodar todos os cérebros num ser"; "andar 4 ticks pra comida, depois água")
Medido no retrato do mínimo-3: as 3 linhagens são a MESMA política (corr
0.86–0.96 sem atraso em vida/gasolina/reserva); ciclo de gasolina ~475
passos; dinheiro segue a gasolina com 150 passos (+0.38); reserva anda
contra o dinheiro (−0.19). Juntar cópias da mesma solução não soma nada;
juntar cérebros DIFERENTES com COMPROMISSO pode. `Comite` = Modos K=4 com
inércia (responsabilidade = EMA com τ gene, atualizada fora do grafo),
nascido dos 4 campeões da triagem (parte linear = média; dW_k = W_k −
média nos pesos de movimento). **Predição 72:** comitê ≥ melhor campeão
por ≥ 3 pp na triagem SÓ se o portão ficar desigual (ganho > 1) e τ > 4
ticks em ≥ 2/3 sementes; se uniforme, cérebros diferentes não têm o que
combinar neste mundo. Controle: Modos K=3 do zero.

## 12. E49 — Olho multi-escala (Leonardo, 14:30: saci-trader M1/M5/M15/M30)
No saci o que pagou foi o banco de τ (evolução achou [1, 17, 120, 2000,
20000]), não a célula líquida (teste justo: LTC ≈ GRU ≈ leaky). Aqui:
necessidades vistas em 3 escalas (agora, EMA 64, EMA 512) e entrando no
produto como `need + a·(need − e64) + b·(e64 − e512)` — micro e macro por
sentido, 6 genes nascendo em 0 (== Produto). Cuidado provado pela
auditoria: sentido de ESTADO não muda a direção numa política linear
(centrada); tendência só vale multiplicando — por isso entra nas
necessidades do produto (e, depois, nas coordenadas dos modos/comitê).
**Predição 73:** genes de tendência ≠ 0 em ≥ 2/3 sementes; panes −20 % vs
produto (antecipa o tanque); mortos −5 pp. Se ficarem em zero: 10 dias não
têm macro que valha — a escala de dias é do prefeito.
- **14:29 E45 v3:** professor guloso com dinheiro ainda morre 1.00 (3.7
  entregas, come 5.5) — três tentativas, abandono o professor à mão (é míope
  por construção: a sobrevivência aqui precisa de sequência, não de passo).
  **Clonagem do mínimo-3 morreu por BUG meu:** o campeão de 3 termos tem
  pesos nos 24 sentidos e a arquitetura ZERA os proibidos ao decidir; clonei
  os pesos crus → política de lixo. Corrigido (máscara), e clonagem do
  campeão LINEAR também na fila (não precisa de máscara). Predição 69
  segue valendo pra clonagem corrigida.

## 13. E50 — Reflexo com duas raízes (Leonardo, 14:45: "Bhaskara dá dois resultados")
A parábola `a(c − r₁)(c − r₂)` é negativa entre as raízes: dois limiares —
liga em r₂ (= portão atual), só desliga em r₁ = r₂ − largura. Histerese /
termostato: o "andar e manter" sem oscilar na fronteira (a doença do E32b).
1 gene (largura, nasce ~0 == Reflexo). Leituras: Δ < 0 = deserto; Δ = 0 =
mundo degenerado (todas as arquiteturas na mesma política — nosso caso com
loja); Δ > 0 = duas estratégias (linhagem com e sem reflexo). Vértice
−b/2a = a base fechada (mínimos quadrados). **Predição 75:** largura
evoluída > 0.15 em ≥ 2/3 sementes e panes −15 % vs reflexo simples; se a
largura ficar ~0, um limiar basta porque o posto enche o tanque de uma vez
(a histerese só paga quando o alvo se consome devagar).
- **15:11** honesto reflexo vs mínimo-3 há 42 min sem linha no log — NÃO
  é travamento: `evoluir_sementes` empilha as 5 sementes num lote só
  (B = 5 × 65 k = 327 k seres por passo, ~7 ms/passo) → ~35 min por braço.
  A regra "20 min sem log = kill" precisa de log por geração: runners
  passam a `verbose=True` (o lab imprime a cada 5 gerações). Não matei.
- **15:22 honesto L=200 (5 sementes, 120 ger., 10 dias, régua B), braço
  reflexo: 0.53 mortos [.52 .56 .51 .53 .52], 28.7 entregas, panes 5.3, 10
  abastecimentos × 54 L, reserva 23, dinheiro 31** — 53 min de GPU (327 k
  seres/passo). Espalhamento entre sementes ±0.02: a régua do campo é bem
  mais apertada que a do grafo (±0.07). Predição 71 (reflexo ≤ 0.5): ✗ por
  pouco (0.53); a comparação com mínimo-3 decide a cláusula dos 5 pp.
- **16:18 honesto L=200 completo (5 sementes, 120 ger., 10 dias, régua B):**

| braço | mortos | entregas | panes | abastecimentos × L | reserva | dinheiro |
|---|---|---|---|---|---|---|
| reflexo | 0.53 [.52 .56 .51 .53 .52] | 28.7 | 5.3 | 10.0 × 54 | 23 | 31 |
| mínimo-3 | 0.53 [.53 .52 .57 .52 .50] | 28.7 | 4.8 | 14.7 × 39 | 23 | 35 |

  Idênticos na régua (mortos, entregas, reserva), estratégias diferentes
  (mínimo-3: paradas frequentes e curtas; reflexo: raras e cheias).
  Predição 71 ✗ (sem 5 pp; nenhum ≤ 0.5). Δ = 0 neste mundo: **teto honesto
  do ser sozinho = 0.53 mortos / 28.7 entregas em 10 dias** — a régua que o
  prefeito v3 e o comitê/olho multi-escala precisam bater. ~55 min de GPU
  por braço (327 k seres/passo).
- **16:33 E48 comitê (triagem L=200):** comitê (4 campeões + inércia)
  **0.58 / 27.4** vs modos K=3 do zero 0.67 / 24.6 — bate o controle por
  9 pp, EMPATA com o melhor campeão sozinho (mínimo-3 0.57 na triagem;
  0.53 no honesto). A base "média dos 4 campeões" sem evoluir morre (0.98):
  média de políticas diferentes não é política — o comitê só volta a viver
  quando o portão separa os modos. Predição 72 (≥ melhor campeão por 3 pp):
  ✗ na régua; genes abaixo dizem se os modos foram usados.
  Genes do comitê: ganho da mistura 0.38 / 0.19 / 0.62 (baixo — os modos
  pesam pouco), τ de inércia 5.6 / 1.2 / 1.5 ticks (> 4 só em 1/3). A
  cláusula da predição 72 vale: com loja no posto, cérebros diferentes não
  têm o que combinar, e compromisso por trechos não paga. Reavaliar no
  mundo sem loja (onde o problema pede sequência) quando alguma
  arquitetura sobreviver lá.
- **16:43 E49 portão passou** (trend genes 0 == produto em eager e compile;
  sem sync; NP 48). Triagem: produto 0.62 / 26.2 (replica a triagem de
  ontem: 0.63 / 26.6 — régua estável); braço produto-trend rodando.
- **16:44 E49 (triagem):** produto-trend 0.66 / 25.2 vs produto 0.62 / 26.2
  — nada (ruído, levemente pior). Predição 73 ✗. Cláusula: em 10 dias não
  há macro que valha — a escala de dias é do prefeito. Genes de tendência
  (abaixo) dizem se a evolução os moveu.
  Genes de tendência: a e b saíram de zero com força (b_fome −4.3, a_fuel
  +4.1) SEM ganho — deriva neutra, não seleção; e o próprio produto está
  incoerente (w da sede negativo em 2/3 = empurra PRA LONGE do posto, θ
  0.01–0.36): na triagem com loja, tudo além dos 3 termos é ruído que a
  evolução carrega. Confirma o Δ = 0 do mundo com loja.
- **16:55 E51 oráculo (na fila atrás do E50):** regra da métrica de degrau —
  o E47 (0.86–0.92 mortos, fome 80 em todos) foi lido como "a evolução não
  monta", mas o TETO FÍSICO nunca foi medido. `src/oraculo_campo.py`: política
  escrita à mão, sem genes — urgência por necessidade, TRANCA um alvo
  (compromisso: "andar N ticks pra comida e depois voltar pra água"), anda
  reto pro ponto mais perto, compra o que cabe, solta e volta ao passageiro;
  pobre (< caixa_min) só atende necessidade crítica; solta e esfria 60 ticks
  se chega sem dinheiro ou se o posto fechou (noite). 8 variantes (limiar
  cedo/tarde, caixa 0/15/40, posto à noite) × 2 mundos (com/sem loja) × 3
  mapas × 128 cópias, L=200 e L=400. Lê-se: oráculo vive onde a evolução
  morre → gargalo é montagem (e o alvo trancado vira arquitetura evoluível,
  E52); oráculo também morre → recalibrar o mundo primeiro. Predição 76.
- **17:15 E45 clonagem — 1ª rodada inválida por bug do solver:** os dois
  professores vivem (mínimo-3 0.58, linear 0.55) mas o clone por ridge morre
  1.00 com 0 abastecimentos: |W| = 2.5e7 porque o bias dos serviços foi
  ajustado sobre notas que incluíam a máscara −1e9 dos serviços indisponíveis
  (b = −8.9e8 → nunca serve). Conserto: o ajuste do bias só olha linhas com
  serviço disponível. Semeado do clone contaminado ainda deu 0.60 (linear)
  vs 0.77 do-zero em 25 ger. — número suspeito, refazer. Re-enfileirado
  (e45h) atrás do E51; o honesto v3 passa pra trás dele (5 min a mais).
- **17:20 E50 reflexo com duas raízes (histerese) — triagem L=200:** 0.59 /
  27.3 vs reflexo 0.58 / 27.4; panes 5.9 vs 5.5; largura da banda ficou em
  0.004 / 0.076 / 0.012 (gene nasce em 0 e fica lá). Predição 75 ✗. Leitura:
  não há oscilação a resolver — o reflexo do campo age pelo GANHO DE SERVIÇO
  (v = 2.4–4.8 em 5/6 sementes: "abasteça quando estiver no posto e a sede
  passar de θ"), quase nada pelo empurrão de movimento (w entre −0.2 e +0.3
  no reflexo puro) — sem empurrão não há vaivém, e sem vaivém a histerese
  não tem o que consertar. Bhaskara fica anotado pra onde houver oscilação.
- **17:20 E51 oráculo caiu em 15 s** (vetor de genes de tamanho 1: `um_passo`
  fatia `Wb[:, NF:NF+S]` e dá (B,0)); corrigido (NP = Linear.NP), re-enfileirado
  (e51b) atrás da clonagem, honesto v3 atrás dele.
- **17:24 E45 clonagem (v4, bias consertado):** |W| 0.65 (normal) mas o
  clone AINDA morre 1.00 com 0.1 entregas — nem vai ao passageiro. Segundo
  bug, de álgebra: a nota-alvo é centrada por linha (G1), mas o Phi não era.
  Os 14 sentidos do corpo são IGUAIS nas 9 opções (constante por linha) e não
  podem explicar um alvo de média zero: o mínimo quadrado distorce todos os
  pesos pra compensar. Conserto v5: centrar Phi por linha (aí o clone de um
  professor linear é EXATO por construção) + medida de fidelidade (fração
  dos estados em que o clone decide igual ao professor — tem de dar ~100 %
  pro linear e pro mínimo-3). Lição registrada: fórmula fechada exige que o
  ajuste use a MESMA transformação que a política aplica (centragem,
  máscara). Re-enfileirado (e45j) atrás do oráculo; honesto v3 depois.
- **17:32 E51b oráculo — morre 1.00 em 22/22 braços** (com/sem loja, L=200 e
  400; limiar cedo/tarde, caixa 0/15/40, posto à noite): 7–12 entregas em 10
  dias (campeão: 27), 3 refeições, 3–4 abastecimentos de 60–95 L, dinheiro
  −5, fome 100 no fim. É o mesmo destino do professor guloso do E45 (morre
  1.00): a política à mão "atende necessidade, senão trabalha" NÃO fecha a
  economia — gasta em gasolina o que não ganha em corrida e morre de fome
  endividado. Predição 76 ✗ nas duas cláusulas, MAS o teto físico não ficou
  medido: o oráculo é pior que a evolução, logo não é teto. Antes de julgar o
  mundo, `diag_oraculo.py` (e51c) mede onde vai o tempo do oráculo e do
  campeão (anda / trancado em cada alvo / parado por pane / noite / com
  passageiro), série diária e causa de morte. Hipótese: o oráculo perde o
  dia trancado (ida ao posto cedo, espera no posto fechado) e entrega
  metade; o campeão evoluído entrega primeiro e abastece 50 L quando passa.
- **17:40 E45 clonagem v5 — a base fechada FUNCIONA como transplante, não
  como atalho:** com Phi centrado o clone por ridge decide igual ao professor
  em 99,5 % (mínimo-3) e 97,3 % (linear) dos estados, e sozinho vive tanto
  quanto ele (0.60 vs 0.58; 0.59 vs 0.55). Ou seja: a fórmula fechada
  W* = (ΦᵀΦ+λI)⁻¹ΦᵀY transporta uma política inteira pra outra arquitetura
  em 0,1 s — inclusive o mínimo-3 (3 sentidos) pro linear cheio (24), com
  os 21 pesos extras ≈ 0 (o clone "sabe" que não precisa deles).
  Mas semear a evolução do clone NÃO rende: 25 ger. a partir dele dão 0.63
  e 0.68 — igual ou PIOR que o próprio clone. Evolução com P=512, R=4 é
  ruído em cima de um campeão (seleciona no treino ruidoso, regride no
  teste); confirma o platô dos 120 ger. e a régua (R=16). Predição 69:
  clone ≈ professor ✓; semeado ≥ do-zero-40 ✗; professor guloso morre ✓.
  O que a base compra depende inteiramente do professor: clone de campeão
  = campeão; professor à mão = morre (E45 v2/v3, E51). Mesma lição da ponte
  de sabedoria (gargalo = qualidade do professor). Uso legítimo que sobra:
  TRANSPLANTE entre arquiteturas (mínimo-3 → linear → produto/modos como
  ponto de partida exato) e diagnóstico (fidelidade < 95 % = a arquitetura
  destino não representa a política).
- **17:41 E51d diagnóstico de tempo (campeão mínimo-3 vs oráculo, L=200
  com loja, 128 cópias × 3 mapas) — o MECANISMO do teto 0.53–0.58:**
  · **Campeão:** anda 87 % dos ticks, 64 % com passageiro, 4,7 entregas no
    dia 1; dinheiro sobe a 44 no dia 1 e estabiliza em ~32; come UMA vez por
    dia exatamente quando abastece (come 9,6 = abast 9,5 — a loja no posto
    é o truque); água 80, fome 37 o tempo todo. Morre de **dano**: só 12 %
    com fome ≥ 90 e 11 % em dívida; 77 % "outro" = **5,7 panes por vida**
    (D_PANE 6 + até 20 kcal da reserva) + calor. A mortalidade do melhor
    ser não é economia nem fome: é ficar sem gasolina no meio do caminho
    (abastece tarde, 50 L, tanque médio 33) e andar quente. Alvo claro pra
    qualquer arquitetura: pane = alcance (gasolina × distância ao posto).
  · **Oráculo:** anda 65 %, 30 % dos ticks TRANCADO no posto (só 4
    abastecimentos: chega e não paga), 12 % em comida — duas viagens onde
    o campeão faz uma. Gasta 15 dos 20 de caixa em 50 L no dia 1 → "pobre"
    no dia 2 → só necessidade crítica → tanque em 15–18 (nível pós-pane) →
    fome 36 → 45 → 60 → 76 → 86 → morre de fome endividado (fome 100 %,
    dívida 91 %). Entregas caem 3,8 → 2,5 → 2,0 → 1,2 por dia. Diagnóstico:
    política à mão míope pra DINHEIRO e sem oportunismo.
  · v2 (e51e, na fila antes do honesto): oportunista (compra tudo que
    precisa quando está num ponto) + piso de caixa (gasolina só com o que
    sobra acima de 8–12: a gordura é o dinheiro, não o tanque) + diagnóstico
    com dano por causa (pane / calor / fome / sede) no campeão.
- **17:46 E51e diagnóstico v2 — dano por causa no campeão (vida = 100):**
  total 176 por ser; **pane 34–147 (5,7 panes)**, calor 40 (265 ticks
  andando quente, 0 desligamentos), fome 14, sede 0, 28 ticks em dívida. A
  reserva (gordura) é o que decide se a pane custa 6 ou 26: é literalmente o
  amortecedor de pane. **O teto do ser sozinho é ALCANCE**: tanque baixo
  LONGE do posto. Nenhuma arquitetura atual gateia isso (reflexo lê só a
  sede; produto lê need×dist mas sem limiar de distância). → **E52 reflexo
  de alcance**: portão a = relu(c + k·d_posto/100 − θ), o "km até esvaziar"
  do painel; k nasce ~0 (= reflexo). Predição 77.
  Oráculo v2 (oportunista, piso de caixa): ainda 0.95–1.00 — agora 40–52 %
  dos ticks trancado no posto sem pagar (quebrado + crítico fura o
  esfriamento e volta pro posto onde não paga) e 70 % dos ticks COM
  passageiro a bordo fazendo só 8 entregas: pega o passageiro (automático no
  raio) e abandona o destino pra ir ao posto. v3 = entrega primeiro + não
  fura o esfriamento (predição 78), na fila atrás do honesto (E52 antes).
- **18:00 painel visual da autópsia (E51c/e):** série diária (vivos,
  caixa, tanque, fome), dano por causa e orçamento de tempo — campeão vs
  oráculos. `docs/painel-51-autopsia.html` ·
  https://claude.ai/code/artifact/042b657f-9bd5-48a0-bc03-a409233cce5f
- **19:05 Leonardo: "gate focado é você resolvendo pelo modelo; o
  interessante é deixar ele tentar até achar algo que crie". E: "mediu o
  cérebro? ativação, distribuição de pesos, camadas lentas e rápidas, por
  tempo?"** Resposta honesta: no campo o ser é 35–48 números sem camada; medi
  genes, τ do reflexo (1,4–5,5 ticks: tudo rápido; w ≈ 0) e retrato do corpo,
  não neurônios — porque não havia. → **E52 vira controle** (mede o prêmio do
  alcance) e a linha principal é **E53 cérebro livre**: camada rápida (4
  unidades relu sobre os 24 sentidos de cada opção → nota de movimento) +
  camada lenta (3 unidades relu sobre o corpo, estado EMA com τ próprio num
  banco log-espaçado ~5/25/100 ticks; z modula os pesos de movimento
  (bilinear) e as notas de serviço). Nasce transparente (V = M = P = 0 ==
  linear). Sem dica. Fila: portão → triagem 40 → 300 gerações → **retrato do
  cérebro** (`retrato_cerebro.py`: EEG das unidades tick a tick, τ, o que
  cada unidade lê, contribuição de cada parte, ablação, pesos por bloco).
  Predição 79 (aposta honesta: a evolução NÃO monta o alcance em 300 ger.;
  o ganho é ver o cérebro).
- **19:15 Leonardo: "refatorou o projeto e não pôs o modelo completo no
  mundo aberto; ele precisa de tudo o que tinha antes: tálamo, córtex,
  hipocampo; pare a GPU e teste o cérebro completo, em parte e completo".**
  Certo. Parei o honesto do prefeito (braço 2, 1 h perdida) e as filas E52/
  E53. **E54 `completo.py`**: porta o SerCamadas do grafo (E42) pro campo e
  junta com o campo: linear (espinha) + reflexo (τ, w, v, θ) + tálamo (5
  grupos de sentidos: rota/serviços/corpo/economia/tempo, gate = 2·σ(a +
  b·need + c·pax)) + córtex (δ por distrito em d_alvo, d_posto,
  custo_frente, preço_frente, |δ| ≤ .5, 12 distritos) + hipocampo (memória
  por distrito: renda da última corrida com origem ali, tempo sem
  passageiro, gasto; EMA com τ; entra BILINEAR memória×sentido no movimento
  e nos serviços, ganho tanh) + rápida (4 relu) + lenta (3 EMA, banco de τ).
  460 genes, tudo nasce transparente; partes desligáveis (sem tálamo / sem
  córtex / sem hipocampo / sem reflexo / sem livre = só camadas). Fila:
  portões → triagem (linear, reflexo, completo, 5 partes) → 300 gerações
  (completo vs linear) → retrato do cérebro (EEG das unidades, gates,
  memória, reflexo tick a tick; ablação por parte; pesos por bloco).
  Predição 80. GPU: só isto, do início ao fim.
- **19:40 E54 portão:** completo transparente == linear bit a bit ✓ (460
  genes); sem-tálamo / sem-córtex / sem-hipocampo / sem-reflexo desligados
  == genes zerados ✓; "sem-livre" deu ✗ por erro do TESTE (zerava também os
  genes das camadas ao cortar até NP; corrigido, re-teste na fila); partes
  vivas com genes aleatórios: gates 0.99–1.09, memória de espera 0.04,
  reflexo ativo 51 % dos ticks, z das lentas 0.75–1.9; sem sync. Triagem
  (linear, reflexo, completo + 5 partes) rodando.
- **19:30 E54 triagem em andamento:** linear 0.65 / 25.4; reflexo 0.58 /
  27.4; completo na ger. 30 com fitness −2.5 (linear tinha +1 nessa altura):
  do zero, 460 genes aleatórios são um terreno muito mais duro — é a
  montagem. Por isso enfileirei também (regra 19) o **completo SEMEADO do
  campeão linear** (genes novos nascem em zero = espinha pronta, partes
  desligadas; 300 ger.) com o **linear semeado** como controle, + retrato.
  Ordem na GPU: triagem (8 braços) → 300 ger. do zero (completo vs linear)
  → retrato → re-teste → 300 ger. semeado (completo vs linear) → retrato.
- **20:05 E54 do zero: completo 0.98 / 14.6 em 40 ger. (vs linear 0.65,
  reflexo 0.58) e 5× mais lento (1445 s vs 287 s):** 460 genes aleatórios
  não montam nada em 40 gerações — o problema de montagem, de novo. Custo
  medido: 2.6 vs 1.4 ms/passo em lote de 8k, mas 15 vs 3 ms em 98k — as
  matmuls minúsculas por ser (rápida: 98k × (9×24)·(24×4), 4 ms sozinha)
  saturam a GPU. Parei os braços do zero das partes (2 h de 0.98). Novo
  protocolo (regra 19): **SEMEADO do campeão linear** (genes novos em zero =
  espinha pronta, partes desligadas), P=512, R=4, 120 ger., 3 sementes, 7
  braços (linear-controle, completo, só-camadas, sem-tálamo, sem-córtex,
  sem-hipocampo, sem-reflexo) → retrato do completo → completo 300 ger.
  A pergunta certa é "a evolução LIGA alguma parte a partir de uma espinha
  que funciona?", não "monta tudo do zero em 40 gerações?".
- **20:15 E54d semeado (120 ger., P512, R4, 3 sementes, do campeão linear):**
  linear-controle 0.63 / 25.9 / 6.3 panes; **completo 0.64 / 26.1 / 5.4
  panes** — empate (panes −14 %, dentro do ruído de n=3). A espinha
  funciona e as partes, mesmo disponíveis, não mudaram o resultado em 120
  gerações. Faltam as 5 partes desligadas (se alguma delas MELHORAR o
  completo, a parte atrapalha; se piorar, ajuda), o retrato (quais genes
  se moveram, ablação) e as 300 gerações.
- **2026-09-07 01:40 (máquina desligada de 09-04 20:20 a 09-06 22:06):** a
  fila E54d morreu no braço "só camadas" (ger. 100/120). Relançado como
  E54e, nesta ordem: retrato do completo semeado (já tem campeão) → 5
  partes semeadas (120 ger.) → completo semeado 300 ger.
- **2026-09-07 01:45 retrato do completo semeado (s0):** ver docs/47. Ablação:
  sem rápida 1.00, sem tálamo 1.00, sem reflexo 0.76, sem córtex 0.71, sem
  hipocampo 0.68, sem lenta 0.66 (= completo), só linear 1.00. As partes
  foram usadas (co-adaptação), o total não mudou. Retrato morreu com status
  137 depois da semente 0 (sem JSON/HTML); agora grava por semente e roda de
  novo atrás da fila (e54f).
- **2026-09-07 13:50 E54 partes desligadas desde o nascimento (semeado, 120
  ger., P512, R4):** sem tálamo 0.62 / 25.7 · sem córtex 0.61 / 27.2 · sem
  hipocampo 0.61 / 26.6 (dof 355: o campeão carrega 355 genes > 0.5 além da
  espinha, de graça) — todas iguais ao completo (0.64) e ao linear (0.63).
  Predição 80(b) ✓: nenhuma parte muda ≥ 5 pp. Faltam sem reflexo e só
  camadas; depois 300 ger., retrato e E55 (custo de gene).
- **14:25 E54 partes, fim:** sem reflexo 0.66 / 25.3 (+2 pp, ruído); **só
  camadas (tálamo+córtex+hipocampo+reflexo, SEM rápida/lenta) 0.58 / 27.3**
  [0.55 0.58 0.61] — 6 pp abaixo do completo (0.64) e 5 abaixo do linear
  (0.63), dof 360. Leitura: os 254 genes das camadas livres (rápida+lenta)
  são ruído que a evolução carrega; sem eles, as camadas do grafo (171
  genes) rendem. É o primeiro Δ ≥ 5 pp em dias, com n=3 (±0.03): vai pro
  **honesto** (5 sementes, R=16, 120 ger., P512, semeado; só-camadas vs
  linear; ~4,6 h) atrás da fila. Se segurar, é a primeira peça que paga.
- **15:16 E54 completo semeado, 300 ger.:** 0.61 / 26.2 / 5.0 panes [0.60
  0.66 0.56], dof 373 (51 min). Contra 120 ger. (0.64) e linear (0.63): −2 pp
  em mortos (ruído), panes −21 % (5.0 vs 6.3; n=3, cláusula de 80(c) batida
  no limite). Nada montou em 300 gerações além do que 120 já davam; o dof só
  cresce (355 → 373): genes de graça acumulam. Retrato em seguida.
- **15:24 retrato do completo semeado, 3 sementes (ablação no teste):** tálamo
  removido → 1.00 / 1.00 / 0.96; reflexo → 0.76 / 0.99 / 0.72; córtex → 0.71 /
  0.62 / 0.97; hipocampo → 0.68 / 0.65 / 0.63; **rápida → 1.00 / 0.60 / 0.64;
  lenta → 0.66 / 0.61 / 0.64** (unidades com correlação 0.00 com tudo: mortas,
  z constante); só linear → 1.00. Leitura: as peças do grafo (tálamo, reflexo,
  córtex) ligam e viram pilar por co-adaptação; hipocampo e as camadas
  genéricas são decoração carregando 70–90 % dos genes acima de 0.5. Bate com
  "só camadas" 0.58 < completo 0.64. Painel publicado (artifact).
- **15:45 E55 λ = 0.3 (cada gene ligado custa 0,3 % de fome; semeado, 120
  ger.):** mortos 0.66 / 25.3 / 6.0 panes, **dof 3 / 7 / 56** (era 355–373
  de graça), metab 1.07. Com um custo de 7 % na fome a evolução LARGA quase
  tudo: reflexo 0/4 genes, tálamo 0–2/15, córtex 0–5/48, hipocampo 0–8/104,
  camadas genéricas 0–40/254. As "pilares" da ablação (tálamo, reflexo)
  sumiram sem dó → eram co-adaptação, não função. Mortos ≈ linear (0.63 +3
  pp, o próprio imposto). Leitura honesta: neste mundo, com loja e 10 dias,
  nenhuma peça além da espinha paga nem 0,3 % de fome por gene. λ = 1 e 3
  rodando (esperado: dof → ~0).
- **16:06 E55 λ = 1:** mortos 0.70 / 24.2 / 6.3 panes, **dof 5** (metab
  1.05). Pior que o linear (0.63) em 7 pp: com custo alto o ser fica com 5
  genes que ainda custam 5 % de fome e nada rende; a mutação (σ 0.2) impede
  zerar tudo. Nenhuma parte sobrevive em λ ≥ 1 (predição 81(d): aposta do
  reflexo ✗; hipocampo/lenta ✓ morrem). λ = 3 e retrato em seguida.
- **16:27 E55 λ = 3:** mortos 0.72, dof 6, metab 1.17 — igual ao λ = 1. Fecha
  a varredura: no mundo padrão nenhuma peça paga custo algum.
- **16:40 Leonardo: "não dá pra fazer o mesmo no mundo dos táxis? foi você
  que fez — melhora o mundo pra usar mais o cérebro: distritos realmente
  distintos, ruas, preços".** Sim. **E56 `gerar_mapa(distinto=True)`:** ruas
  (custo 1 na rua, 3 fora — o custo_frente passa a decidir), 4 perfis de
  distrito (centro: tudo caro ×2, muito passageiro; industrial: posto ×0.6
  farto, SEM comida; residencial: comida e descanso, SEM posto; periferia:
  barato, vazio, pouco passageiro), demanda de passageiro por distrito,
  preços oscilando ±50 % num ciclo de 3 dias com fase por distrito. Mundo
  padrão continua bit a bit (amp 0, demanda 1). Fila (antes do honesto
  antigo): portões → linear e reflexo do zero no mundo distinto → só-camadas,
  completo e linear semeados → só-camadas e completo com λ = 0.3. Predição 82.
- **16:36 retrato E55 λ = 1 (s2):** ablação plana (completo 0.71; sem
  qualquer parte 0.68–0.74; só linear 0.72): sob custo o cérebro É a espinha.
  Curioso: as 2 unidades lentas que sobraram leem algo (z0: fome +0.41, pax
  +0.35; z1: tanque −0.33, pax −0.39) — sinal sem uso. Fila E54g fechada; E56
  (mundo distinto) começou.
- **16:53 E56 mundo distinto, do zero (P512, R4, 120 ger.):** linear **0.87**
  / 16.9 entregas / 4.9 panes / dinheiro 32 / fome 44; reflexo 0.86 / 17.4.
  Predição 82(b) ✓ (mais duro), mas perto do degrau (0.9): com dinheiro e
  fome ok, de que morrem? Diagnóstico de dano por causa (diag_oraculo com
  --braco linear --mundo distinto) enfileirado antes do honesto. Se for calor
  (custo 3 fora da rua → calor sobe 3×), o mundo está duro demais no lugar
  errado e se recalibra (calor_sobe) antes dos braços semeados valerem.
- **18:28 E56 (PC reiniciou 17:56; filas relançadas):** portão do mundo ok
  (preços variam até 47 % em 1 dia; rua 33 %). Semeados no mundo distinto:
  linear 0.86 / 16.1; **completo 0.87 / 16.3** — empate de novo, num mundo
  onde todo mundo morre 0.86 (degrau). Só-camadas rodando; diagnóstico de
  causa vem depois — sem ele, não dá pra dizer se o mundo cobra o cérebro
  ou só cobra demais de todo mundo.
- **18:46 E56 semeados, mundo distinto:** linear 0.86 · completo 0.87 ·
  só-camadas 0.86 — **degrau**: todo mundo morre igual, com dinheiro 31–37 e
  fome 43–54 (não é economia). Regra da métrica de degrau: não concluir
  nada sobre peças com o teto batendo. Matei o braço λ = 0.3 (inútil sob
  degrau) e o honesto antigo saiu da fila por ora; diagnóstico de dano por
  causa do linear distinto rodando agora — a suspeita é calor (custo 3 fora
  da rua ⇒ calor sobe 3×). Recalibrar o mundo com o diagnóstico na mão.
- **18:47 diagnóstico do linear no mundo distinto:** dano 136 por ser: **pane
  28–123 (4,7 panes)**, calor 31 (0 desligamentos), fome 11, sede 0. NÃO é
  calor: é o mesmo assassino do mundo antigo, a pane (alcance), agravada
  porque residencial não tem posto e periferia tem metade. Mundo certo no
  lugar errado: o assassino uniforme (pane) esconde tudo o que os distritos
  cobrariam. **E56c**: mesma cidade distinta com a pane doendo em vez de
  matar (KCAL_PANE 20 → 8; D_PANE 6 fica) para tirar o degrau e deixar
  preços/distritos/memória serem a margem. Fila: linear+reflexo do zero →
  só-camadas/completo/linear semeados → λ 0.3 → diagnóstico do só-camadas.
  Honesto antigo atrás disso. Predição 82 vale para o E56c.
