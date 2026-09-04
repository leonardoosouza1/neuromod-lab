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

## 5. Diário
- **23:54 fumaça E44 (10 dias, L=200, régua B, P=512, G=25, 1 semente,
  prefeito selecionado a cada 5 ger.):** sem prefeito 1.00 mortos / 10.0
  entregas; com prefeito (co-evolução) 0.99 / 9.7; prefeito campeão
  aplicado no teste: **0.96 / 10.6**. Alavancas que ele escolheu: alíquota
  ×0.5, gasolina ×2.0, água ×0.5, comida ×0.65, aluguel ×0.5, tarifa ×2.0 —
  direções sensatas (barateia o que mata, encarece o que não mata, sobe a
  renda). Obras: **27 postos, 1 comida, 0 água** (3 mapas) — gastou o caixa
  no serviço errado: a fitness dele (bem-estar agregado) ainda não "vê" que
  a morte é por fome. Predição 57 ✗ na fumaça (−4 pp, não −15). O gargalo
  é dos seres (não comem, ver docs/44 23:51) — o prefeito só amplifica uma
  população que funciona. Próximo: consertar o comer; depois prefeito com
  sentido de "morte por fome" ligado à obra de comida (já é sentido `m_fome`;
  falta gene selecionado) e mais gerações de prefeito.
- **14:09 portão v2:** "prefeito genes 0 == sem prefeito" deu FALSE — `construir()`
  sorteava posição mesmo sem construir e consumia o gerador do mundo (desvia
  o fluxo dos passageiros). Corrigido com gerador próprio do prefeito
  (`int(s.t)` é lido uma vez, fora do laço quente). Portão re-enfileirado.
  Os resultados v2 que estão rodando valem como experimento (a mecânica é a
  mesma; só o fluxo aleatório diferia), mas a comparação "com vs sem" só é
  bit-limpa depois do portão passar. Caixa per capita inicial 10–22 (v1 era
  milhares).
- **14:28 E44 v2 (moeda cruzada) — fumaça:** com prefeito no teste 0.74 →
  0.21 mortos, 24.6 → 31.5 entregas; obras 7 comida + 5 postos (caixa real,
  não milhares); alavancas: imposto ×0.53, gasolina ×0.5, água ×1.61, comida
  ×0.5, aluguel ×2.0, tarifa ×2.0. **Triagem (3 sementes):** sem 0.62 / 26.2;
  com prefeito no teste **0.16 / 31.5**; obras 4 comida + 3 postos;
  alavancas: imposto ×0.5, gasolina ×0.5, água ×0.5, comida ×1.76, aluguel
  ×0.9, tarifa ×2.0. Predição 70 ✓ (ganho cai de −58 pra −46 pp e FICA; ≥ 1
  alavanca acima de 1.0 além da tarifa). Nota: os seres co-evoluídos COM
  prefeito ficam piores SEM ele (0.78 vs 0.62) — co-adaptação: viraram
  especialistas na cidade dele. Brecha que sobrou: o caixa pode ficar
  negativo (subsídio de gasolina ×0.5 sem limite). **v3: orçamento fecha —
  com caixa ≤ 0 nenhum preço fica abaixo de 1.0** (imposto e tarifa livres).
  Triagem v3 na fila. Predição 74: v3 mantém ≥ −30 pp e o prefeito para de
  subsidiar gasolina abaixo de ×0.8 (ou compensa com tarifa/imposto).
