# Contexto para o Claude Science — projeto IARA / neuromod-lab (2026-09-08)

## O que é o projeto
Pesquisa independente (1 pessoa + agente Claude, GPU doméstica AMD RX 6750 XT) sobre **como surge inteligência por
sobrevivência**: um "ser" com corpo (tanque, água, fome, fadiga, calor, vida, dinheiro, reserva calórica) vive
num mundo simulado como taxista, precisa trabalhar para comer e abastecer, e um cérebro pequeno (35–500 genes)
é **evoluído** (algoritmo genético, populações de 512–1024, 40–300 gerações, tudo na GPU em PyTorch) para
sobreviver 10 dias. A tese-mãe: sobrevivência é um SELETOR (escolhe/roteia/emerge), não um gerador; peças de
cérebro só viram função quando o mundo cobra e quando custam algo.

## O mundo (campo contínuo, `campo.py`)
Cidade 200×200 com ruas (custo 1 na rua, 3 fora), 6 distritos com perfil (centro caro e cheio, industrial com
posto barato e sem comida, residencial com comida e sem posto, periferia vazia), preços que oscilam ±50 % em
ciclos de 3 dias, passageiros com demanda por distrito, postos/comida/água/oficina como pontos, noite (posto
fecha), calor, panes (ficar sem gasolina: guincho até o posto; hoje o guincho cobra 10 e deixa 5 L). O ser nasce
pobre (10 de dinheiro, 5 refeições) e paga aluguel. Existe um **prefeito** co-evoluído que ajusta preços,
impostos, aluguel, tarifa e constrói postos/comidas com o caixa (moeda cruzada: subsídio custa em outra moeda).

## Os cérebros (todos nascem "transparentes": genes novos em zero = idênticos à espinha)
- **Linear** (espinha): nota por opção de movimento = Σ peso × sentido (26 sentidos: distâncias a alvo/posto/
  comida/água/oficina, custo e preço à frente, e 16 do corpo, incl. consumo medido e autonomia), + notas de serviço.
- **Reflexo** (sede de gasolina com portão θ), **Produto** (necessidade × distância), **Modos** gaussianos,
  **Comitê**, **Bilinear** (peso de cada sentido de opção modulado pelo corpo), **Cérebro completo** (tálamo =
  atenção por grupo de sentidos; córtex = política por distrito; hipocampo = memória por distrito com τ; reflexo;
  camadas genéricas rápida e lenta com banco de τ) — 460 genes, partes desligáveis para ablação.
- **Custo de gene** (λ): cada gene ligado além da espinha custa fome (Lei do Metabolismo = AIC).

## Método
Toda bateria tem **predição registrada antes** (ledger com 88 entradas, ✓/✗ com mecanismo), "régua honesta"
(5 sementes, 120 gerações, 16 cópias de mundo), portões de identidade (compile = eager bit a bit, transparência,
sem sync CPU-GPU), **portão de sensibilidade** (cada sentido consegue mudar direção e serviço?) e **teste de
escala** (ruído de semeadura não pode afogar a espinha). Negativo com mecanismo conta como resultado.

## O que já está estabelecido (números)
1. Teto honesto do ser sozinho no mundo com loja: 0.53 de mortalidade em 10 dias; ele morre de **pane** (5,7 por
   vida = 34–147 de dano), não de fome (14).
2. **Prefeito com orçamento fechado: −40 pp** (0.62 → 0.22) subsidiando gasolina/comida e cobrando em aluguel/
   água; no mundo distinto e pobre, −13 pp construindo 8 postos e 22 comidas.
3. **Base fechada** (W* = (ΦᵀΦ+λI)⁻¹ΦᵀY) clona um campeão em outra arquitetura com 97–99,5 % de fidelidade em
   0,1 s — transplante exato, mas semear a evolução a partir do clone não economiza gerações.
4. **Cérebro completo = linear** (0.64 vs 0.63; 300 gerações não mudam). Ablação mostra peças "usadas" por
   co-adaptação; com custo de gene λ = 0.3 a evolução larga 350 de 355 genes sem perda: **peça sem custo é
   decoração**; nenhuma peça paga custo neste mundo.
5. Três erros de base achados e corrigidos esta semana: (a) no Linear os sentidos do corpo são invisíveis na
   direção (centragem por opção) — o ser nunca "procura" o posto; (b) ruído de semeadura afogava a espinha do
   cérebro completo (58 % das decisões); (c) "pedra": com 20 de dinheiro o ser vivia 10 dias parado.
6. Mesmo com um sentido retificado de risco ("luz de reserva", zero quando seguro) e um caminho direto do corpo
   ao volante (bilinear), **a evolução não montou em 120 gerações o gene "ir ao posto quando a luz acende"**; os
   genes são cortados em ±5 e a solução parece exigir |M| ≈ 12; testando escala 3 agora.

## Perguntas abertas onde precisamos de literatura e de método
1. **Evolvabilidade de funções de dois sentidos**: em que condições uma população evolutiva monta uma função
   que depende de dois sinais simultâneos (risco alto E direção do posto), quando cada um sozinho é neutro ou
   prejudicial? (epistasia, paisagens NK, cost of complexity de Fisher-Orr, neutral networks, exaptação, "cryptic
   genetic variation", evolução de plasticidade/gating). O que a literatura recomenda: população, mutação,
   clamp de genes, seleção por torneio vs elitismo, currículo, semear vs do zero?
2. **Custo metabólico como seletor de módulos**: evidência de que módulos só se fixam sob custo de manutenção;
   como calibrar λ (a nossa Lei do Metabolismo: met = σ²(1 + 2·dof) = AIC).
3. **Co-adaptação e ablação**: ablação exagera contribuição quando o resto se afinou ao módulo; qual o protocolo
   correto (knock-out desde o nascimento vs knock-out no campeão; "lesion + re-training")?
4. **Régua**: mortalidade em 10 dias satura (degrau) e é explorável ("pedra"); que métricas de "juízo" a
   literatura de vida artificial/RL usa que separem sobreviver de fazer bem?
5. **Reprodutibilidade/pré-registro**: um trilho formal para hipótese → critério → n → resultado travado.

## O que gostaríamos que o Claude Science fizesse
- Revisão dirigida com fontes verificáveis para cada pergunta acima, marcando [R] reportado / [E] opinião / [?]
  controverso, e traduzindo em **mudanças concretas de experimento** (parâmetros, protocolo, métrica).
- Um formato de pré-registro por bateria que possamos manter no repositório.
- Depois: esboço de artigo curto e honesto com o que já está estabelecido (itens 1–6).

Repositório privado `leonardoosouza1/neuromod-lab`; docs em `docs/44-campo.md` (diário), `docs/47-relatorio-2026-09-07.md`,
`PREDICOES.md` (ledger), `docs/acervo/` (compêndios de neurociência/física/biologia que já lemos).
