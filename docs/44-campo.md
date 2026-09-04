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
