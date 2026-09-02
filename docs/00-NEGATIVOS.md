# 00 — LIVRO-RAZÃO DOS NEGATIVOS (ler antes de propor qualquer coisa)

Princípio (Leonardo, 2026-09-01): *"negativos são positivos — provam o
contrário ou revelam a barreira; o modelo sabe por pesos positivos E negativos
se é ou não é."* Um laboratório sem refutações é um cérebro sem inibição.
Cada linha aqui é um peso negativo no espaço de design: poda uma direção e
barateia o resto da busca. Refutados antigos: INDICE-MESTRE §4. Estes são os
da era dos táxis (2026-08-30 → 09-01), todos com mecanismo.

| # | negativo | mecanismo | o que COMPROU |
|---|---|---|---|
| N1 | memória não vence reativo (base/semgps/ruas, 3 sementes cada) | mundo de 1 salto sem estrutura oculta acionável; memória DECORA treino e perde em cidade nova | recolocou a aposta em estrutura oculta + órgãos |
| N2 | evitar congestão por memória: teto ZERO em 3 calibres | política gulosa de 1 salto + GPS sem trânsito → desviar não reroteia, o GPS puxa de volta | apontou o órgão-calculista (rota = replanejar) |
| N3 | jam pesado matou o mundo | custo físico escalava com o jam (20+ fuel/travessia) | separação tempo×físico (jam custa TEMPO) |
| N4 | E4 órgão-rota: 1/3 das sementes acha a bacia boa | paisagem bimodal; mistura órgão+GPS correlacionados | apontou a ONTOGENIA (nascer com o órgão ligado) — o achado mais robusto do lab |
| N5 | poda por \|w·sinal\| manteve órgão inútil | contribuição-por-volume = MAGNITUDE (4ª aparição do uso≠contribuição) | poda causal por lesão |
| N6 | lesão de 8 passos = sorteio (sobrevivência chapada) | entrega é evento raro; janela curta não contém sinal | regra do sinal denso / janela longa |
| N7 | infância longa nem sempre paga | subsídio cobre energia, não lucro cessante | duração da infância é função do mundo |
| N8 | E9b: lei não aprendida (corr~0) | BUG: regressor afogado por passos de viagem com Δ=0 (2ª vez da lei "ruído na ENTRADA da regressão mata a lei" — 1ª foi o round() do e5) | fix partiu: corr 0.03→0.77 |
| N9 | E9c: sabe (corr 0.7) mas perde −7 | co-adaptação: lei crescendo em vida × peso de risco evoluído = paranoia (colapso 4.1) | clamp no risco (−7→−3.3) |
| N10 | E9d/e: usar custa ~0, aprender custa −1.85, teto +2.4 | sono ESPALHADO (muitos cochilos, cada um rouba um passo); margem do mundo apertada | sono em BLOCO em CASA (E11) + mundo mais quente |
| N11 | tálamo: rota NÃO é mais consultada carregando | o gate venceu por economia geral (duty ~10%), não pelo padrão previsto | humildade sobre COMO os mecanismos vencem |
| N12 | rotear por estatística fixa (pré-era, CONTEXTO) | estatística escolhida à mão ≠ informativa | gatilhos/gates sempre EVOLUÍDOS |

Regras que os negativos escreveram (não repetir):
1. Medir o TETO antes de rodar (N2, N10 — o erro foi cometido 2×).
2. Sinal de crédito precisa ser DENSO ou a janela longa (N6).
3. Ruído na entrada da regressão atenua a lei — logar a variável verdadeira (N8, e5).
4. Nunca podar/crescer por volume de ativação (N5 — uso≠contribuição, 4×).
5. Mecanismo novo em vida × peso evoluído = co-adaptação; LIMITAR a alavanca (N9).
6. Toda vitória tem uma história prevista e uma real — conferir a real (N11).

## N13 — MONOCULTURA TÉRMICA (achado 2026-09-01, pedido do Leonardo "parado por bug ou escolha?")

Instrumentando a ativação do cérebro do perito: 63% dos ticks o cérebro NAO
decide (preso). Decomposto: 42% da vida TRAVADO por avaria, e **100% das
avarias sao SUPERAQUECIMENTO** (combustivel/pneu/oleo = ZERO). O mundo "rico
com 4 avarias" do README e na pratica um jogo de gerenciar CALOR — monocultura.
- Comparacoes RELATIVAS seguem validas (mesmo mundo p/ todos os bracos).
- Comportamento ABSOLUTO era dominado por 1 eixo — nunca medido ate agora.
- Conserto natural = agua do radiador (E9): temperatura vira recurso APRENDIVEL
  em vez de imposto fixo. Alternativa: rebalancear as 4 avarias.
- Instrumento novo: inspetor de ativacao (livre-moveu / parado-a-toa / travado)
  vira debug padrao — "parado por escolha != parado por bug != mundo mal
  calibrado" (3a categoria, a que este achado revelou).

## N14 — MUNDO MORTO POR FLAG NÃO VALIDADA (E12 v1, 2026-09-01)

`eco2` (posto enche o tanque; pane deixa fuel=5) tinha predições registradas
desde a era anterior mas NUNCA tinha rodado. Liguei em E12 pra reserva poder
se formar à meia-noite. Resultado: os 6 braços nasceram mortos (ent 0.2–0.4
em 5 dias; base dá 15–18) e a evolução achou "ficar parado" (fit −0.6 > ir
e quebrar).
- Mecanismo: fuel=5 após pane não paga um salto (custo 2–6/aresta) até o
  posto → pane → 18 passos parado → fuel=5 → pane. Espiral sem saída.
  Perito isola em 6 configs: só `eco2` derruba (ent 8.0→2.9, panes 25→48);
  relógio, dia=240, noite, reserva, peso não mudam nada sozinhos.
- Quase custou uma conclusão falsa: "reserva+peso VENCE noite" (−0.66 vs
  −2.14) era verdade no mundo morto — vitória de quem quebra menos por andar
  menos. Sem o braço-âncora e sem olhar `ent`, teria passado.
- Regra 7: **flag de mundo só entra em bateria depois de rodada sozinha**
  (predição registrada ≠ validada). E toda bateria carrega um braço-âncora
  no mundo conhecido — `ent` absoluto é o detector de mundo morto.
- Conserto: `pane_fuel` desacoplado do `eco2` (15 mantém o posto alcançável).

**Adendo N13 (2026-09-01, E12):** o perito em `Cfg(1.0, base)` hoje faz 32.9
avarias/5 dias sendo **25.1 pane-seca e 3.8 superaquecimento** (76% fuel) —
idêntico bit a bit no HEAD b5955e2 e no lab.py do E12 (portão de identidade).
O "100% superaquecimento" do N13 veio de um inspetor que não está no repo e
não sei em que mundo/genoma rodou. Até re-medir: N13 vale como "1 eixo domina",
não como "o eixo é calor". Comando: perito_W × rodar(Reativo, base, T=1200,
seed=7777, 64 réplicas) — ver PREDICOES §E12 v1.

## N15 — A pane subsidiada sustenta a economia e deixa a gordura sem trabalho (E12, 2026-09-01)

**Afirmação:** no mundo base (com ou sem noite) a evolução aceita 15–19 panes
de fuel por vida em TODAS as condições — 26 braços, 78 sementes, 3
arquiteturas, pobre ou rico, G=20 ou 60. Não é falta de dinheiro (rico: pobre
0.09, panes iguais), nem de tempo de evolução, nem de alavanca pra hora
(ReativoHora), nem de previdência de rota (Corpo). É ESCOLHA: a pane devolve
15 de fuel por 18 passos parado = "posto grátis lento", 2.5 tanques grátis por
vida. Prova: tirar o fuel da pane (`reboque`) mata o mundo com multa 12 (fit
−4.3), 4 (−1.3) e 0 (+0.2) — sem a pane subsidiada não há economia que feche.
Consequência: o tanque às 22h nunca passa de ~39 e a reserva (NIVEL=50)
converte 6–9/dia; gordura oscila em 3–5/60. A reserva não teve o que guardar.

**Regra 8 (deriva da 1):** antes de dar um órgão de POUPANÇA ao ser, medir
se existe SOBRA no mundo (fluxo de entrada − saída > 0 sem subsídio). Sem
sobra, o órgão é airbag pequeno competindo com um airbag grátis. Medida
direta: `fuel22` (tanque às 22h) e `n_posto` vs `av_fuel`; se panes ≥ postos,
a pane virou posto.

**Regra 9:** um subsídio (pane que devolve recurso, reabastecimento gratuito,
fitness aditivo) nunca é neutro — vira a fonte de renda do ser e todo órgão
que dependa de escassez fica ocioso. Antes de testar mecanismo de escassez,
listar cada subsídio do mundo e o que ele vale por vida.

**O que NÃO é negativo:** no mundo com sobra (fuel×0.5) a cadeia inteira
funciona e um comportamento emergiu sem roteiro: sob peso o ser fica MAGRO
(gordura 8.9 vs 17.7, metade das visitas ao posto, mais panes aceitas).
Homeostase de peso por seleção. O fitness só não saiu do ruído.

**Fechamento (v8/v9, 2026-09-02):** a reserva PAGA quando a escassez é rara e
grande (greve do posto 1 dia em 4: +1.2/+1.8, 6/6 sementes) e não paga contra
a noite diária (+0.05 sem subsídio) — lei em doc 26 §7.2: benefício =
v·min(I, f·S, f·RES_MAX), ótimo I* = f·S. **Regra 10:** antes de dar um órgão
de estoque, calcular a razão entrada/buraco (I vs f·S). Se I ≪ f·S o órgão
fica no regime "teto = entrada" e o ganho é ℓ-negativo; testar noutro f, não
noutro cérebro.

## N16 — Reboque caro em dinheiro = armadilha de pobreza; rápido não vê a morte (E13, 2026-09-02)

**Afirmação 1:** no mundo-corpo, 31% dos campeões morrem — e morrem QUEBRADOS
(dinh 0.6–1.0, 16 panes até morrer) enquanto os vivos fazem 1.3 panes/vida com
a mesma política. O reboque de 20 dinh cobra na moeda que compra o conserto
(posto 2, oficina 10): a 1ª pane tira o dinheiro do posto → 2ª pane → morte.
Zerar a multa (o corpo já paga −6 vida): mortos 0.31 → 0.17, fit +1.1.
**Regra 12:** antes de pôr multa, perguntar com que o ser paga a recuperação;
se for a mesma moeda, a multa mata por espiral, não por seleção (eco da lei
da moeda cruzada, EXP10).

**Afirmação 2:** o preset rápido (treino 2.5 dias) "evoluiu" 52% de
mortalidade porque ninguém morre antes do dia 3 — a seleção nunca viu a morte.
Longo (5 dias): 39%. **Regra 11:** medir o dia em que o perito morre e treinar
mais longo que isso antes de qualquer seleção por morte.

**Correção (5 sementes):** "a dor ensina" como GANHO não replicou — corpo −
sem corpo = −0.45 (n=5) contra +0.75 (n=3); efeito seguiu o n e trocou de
sinal. O que replica 5/5 é o comportamento (panes 13 → 8, oficina 0 → 7); a
morte come o ganho. 3ª vez que n=3 enganou (ver feedback replicação > σ). Gordura que cabe (cap 120, sem peso): +2.4, −8 pp de
mortes. "Gordo esquenta" (fervura 2.2 → 3.5 com peso) emergiu sem roteiro.

## N17 — Sono em bloco é inerte; n=3 enganou 5 vezes num dia (E13, 2026-09-02)

**Afirmação:** dar ao ser a opção de dormir a noite inteira (descanso à noite
= bloco até as 6h) não reduz mortalidade: n=3 deu −3 pp (5 dias) e −10 pp
(10 dias); n=5 deu +3 pp e +2 pp, com fit −1.2 e −1.0. O Reativo e o
ReativoHora entram no bloco ~1 noite em 5 e perdem a madrugada sem evitar
a pane. Mecanismo: a morte noturna é pane LONGE do posto com res=0; dormir
só evita se o ser dorme ANTES de o tanque zerar, e nenhuma feature de hora
condiciona isso na família reativa (3ª–4ª vez que o ReativoHora não usa a
hora).

**Regra 13 (a mais cara do dia):** efeito de MORTALIDADE só conta com n ≥ 5
sementes. Hoje n=3 inverteu de sinal 5 vezes ("a dor ensina" +0.75 → −0.45;
bloco −3 pp → +3 pp em dois conjuntos de cidades; bloco −10 pp → +2 pp;
greve). Mortalidade é bimodal (quem pane cedo morre) e a variância entre
sementes é ±8 pp: qualquer efeito < 10 pp precisa de 5 sementes ou mais.
Fitness também: ±1.5 entre sementes em todo mundo-corpo.

**Replicado com n=5 (E13p):** reboque só no corpo SOBREVIVE (+1.3, −11 pp,
5/5 sementes); cap 120 CAI (+0.4, 2/5, +1 pp — a noite gasta a gordura antes
de o cap importar). Das cinco afirmações de n=3 do dia, uma sobreviveu.
