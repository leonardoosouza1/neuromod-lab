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
