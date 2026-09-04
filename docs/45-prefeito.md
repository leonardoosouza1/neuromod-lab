# 45 — E44 Prefeito: quem calibra o mundo é um ser, não eu (spec, 2026-09-03 23:25)

**Leonardo:** *"era para o prefeito pegar isso e resolver; você está validando
errado e chutando; treina só 5 dias; o prefeito deve ser treinado junto — se
no dia 2 está horrível para todos, ele testa e muda algo. N prefeitos criando
mais cidades: estados com várias cidades e milhares de distritos (mais pro
fim)."*

## 0. O erro que isto corrige
Hoje à noite calibrei à mão água, calor, gasolina, tarifa, aluguel,
passageiros (docs/44 §8) até um perito sobreviver — chute informado, mas
chute. O que o programa diz desde o doc 28 é que isso é papel do PREFEITO:
um agente que sente a cidade e mexe nos preços/serviços/impostos, treinado
JUNTO com os seres, com horizonte maior que a vida de um ser.

## 1. O que o prefeito é
- **Um por mapa.** Vive muitas vidas de ser (mandato = uma geração inteira
  da população, 1200 passos × R vidas simultâneas; e persiste entre gerações
  se reeleito pelo próprio desempenho).
- **Sente, uma vez por dia (240 passos), agregados da cidade** (tudo tensor,
  sem sync): mortos até agora, mortes por causa (fome/sede/pane/dívida),
  fome/água/gasolina/vida médias, dinheiro (mediana e fração quebrada),
  entregas por dia, uso de cada serviço, fração de tempo parado, receita de
  imposto arrecadada, caixa da prefeitura.
- **Age, uma vez por dia, com alavancas por distrito** (K distritos):
  alíquota (0.02–0.4), multiplicador de preço de gasolina/água/comida,
  aluguel, tarifa base, **e constrói**: gasta o caixa pra abrir um ponto de
  serviço (posto/água/comida/oficina) num distrito escolhido. Cada alavanca
  tem limite físico (regra 16: nada abaixo do custo real).
- **É pago pelo bem-estar da cidade, não pelo caixa**: régua B agregada
  (bem-estar integral médio da população + sobrevivência) com o caixa como
  RESTRIÇÃO (não pode gastar o que não arrecadou) — dinheiro é meio, como
  pro ser. Variante a testar depois: prefeito pago pelo caixa (o que emerge é
  um explorador? predição: sim, e a cidade morre).
- **Genoma**: política linear pequena (agregados → alavancas) + memória de
  ontem (o que mudou depois da última ação) — 12 sentidos × 6 alavancas ×
  K distritos compartilhados por um gene de "sensibilidade ao distrito" ≈ 80
  genes. Nasce fazendo NADA (regra 17: alavancas no valor do mapa).

## 2. Treinar junto (co-evolução, 2 populações)
Geração g: seres evoluem contra os prefeitos atuais (um por mapa de treino);
prefeitos são avaliados pelo resultado da SUA cidade nessa mesma geração;
a cada 5 gerações os prefeitos passam por seleção/mutação entre si (elite
de mapas). Predições antes de rodar: 57. com prefeito, a mortalidade do
campo cai ≥ 15 pp vs os preços fixos do doc 44 em L=200, e o prefeito
constrói ≥ 2 pontos de água/comida por mandato; 58. o prefeito "explorador"
(pago pelo caixa) sobe a alíquota até a cidade quebrar (mortos ≥ 0.6) — a
régua do prefeito manda mais que a do ser.

## 3. Estados (fase 3, como o Leonardo disse: "pro fim")
N cidades por estado (mapas), N prefeitos, migração de seres entre cidades
quando o bem-estar cai (o ser que sente que a cidade piorou vai embora —
pressão evolutiva sobre o prefeito), governador como glândula do estado.
Milhares de distritos = K grande por mapa; o campo aguenta (K só entra no
Voronoi por célula, pré-computado).

## 4. Ordem
1. Fumaça do campo (rodando) tem de mostrar evolução escapando do deserto
   com os preços de hoje — senão o prefeito nasce num mundo morto.
2. E44 v1 na GPU: sentir + 3 alavancas (alíquota, preço da gasolina,
   construir água/comida) com régua B agregada; co-evolução a cada 5 ger.
3. Retrato do prefeito: o que ele mexeu dia a dia, e a curva da cidade.
