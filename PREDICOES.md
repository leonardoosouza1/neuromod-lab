# Predições registradas ANTES da bateria de mundos — 2026-08-30

Bateria: 4 mundos × 5 arquiteturas × 3 sementes de evolução, P=1024, G=40, R=8,
NP=36 para TODAS (I8 respeitado — pesos mortos nos menores). Raio de visão 4
(≈25% do tempo sem ver passageiro algum). Régua de ruído = amplitude entre sementes.

| mundo | oculto | predição |
|---|---|---|
| base | nada | memória NÃO paga (reativo ≥ demais; réplica do resultado de ontem com params agora iguais) |
| cego | visão limitada, spawn uniforme | memória NÃO paga — o passado não informa o futuro. CONTROLE: se memória ganhar aqui, a explicação "memória codifica estrutura" está ERRADA |
| hotspot | visão limitada + polo derivando | banco EMA e híbrido > reativo, por MAIS que a amplitude entre sementes |
| mare | visão limitada + 2 polos alternando período 128 | diádica > EMA > reativo (janelas 2^j detectam fase; EMA borra) |

Critério de falha da tese inteira: se em hotspot e mare NENHUMA memória bater o
reativo além do ruído, então "esconder estrutura espacial faz memória pagar" está
refutada neste mundo — e o problema é da ARQUITETURA de memória, não do ambiente.

Ligação: é a Tese do Corpo/E2 do Universe em miniatura — o teto vem do ACOPLAMENTO
(estrutura oculta ↔ mecanismo de memória), não da riqueza do ambiente.

---

# E8 — vida em fases (docs 21) — predições 2026-08-31, ANTES de rodar

5 modos do SerVital (5 órgãos, infância com subsídio+exploração, poda por
contribuição, custo por órgão na vida adulta), mundos ruas e base, 3 sementes,
evolução conjunta pareada. Fitness = entregas − 0.3·avarias − custo neural.

1. `poda` ≥ `direto` em fitness, além da amplitude entre sementes — a infância
   compra a informação de poda que o adulto-direto não tem.
2. `poda` > `poda_aleatoria` — podar POR CONTRIBUIÇÃO é o mecanismo; mesma
   contagem sorteada tem que perder.
3. `sem_poda` ≈ `poda` em ENTREGAS mas < em FITNESS (paga 5 órgãos pra sempre).
4. `curta` < `poda` — infância de 5% não dá tempo de medir contribuição.
5. Sobrevivência por órgão é DIAGNÓSTICA do mundo: no `ruas` a rota/mem-custo
   sobrevivem mais que no `base`; no `base` a poda mata os órgãos de custo
   (mundo não cobra). Se a poda mantiver tudo/nada indiscriminadamente, o
   limiar está mal calibrado — declarar e recalibrar UMA vez.
6. (ponte E4) no `ruas`, o órgão-rota com infância atinge confiança útil em
   ≥2/3 sementes (vs 1/3 do E4 sem infância).

## E8b — poda por LESÃO (causal) — predição 2026-09-01, ANTES de rodar

Furo medido no E8: contribuição por |w·sinal| é MAGNITUDE — manteve a rota em
100% também no `base`, onde ela não deveria pagar. E8b: lesões rotativas na
infância (cada órgão OFF em janelas de 8 passos) e poda mantém só quem,
ausente, PIOROU a taxa de fitness (margem 2%).

1. `lesao` ≥ `poda` em fitness nos dois mundos.
2. **Diagnóstica**: no `base`, `lesao` PODA a rota (que a magnitude mantinha);
   no `ruas`, MANTÉM a rota. Se mantiver rota no base, ou a rota ajuda de
   verdade lá (reforço do d_alvo — investigar antes de culpar o mecanismo) ou
   a janela de 8 passos é curta demais pro sinal causal.
3. `lesao` no ruas conserva o recorde (entregas ≥ nível do curta 16.7).

## E9b — RODADO: refutado por BUG (registrado) → E9c

E9b deu fixo>aprendizes e corr~0. Diagnóstico numérico: (1) BUG no `partiu`
(sem rest_prev≤0, todo passo de viagem entrava com Δtemp=0 e afogava a
regressão — estimador dava corr 0.03 ATÉ com dados ricos); (2) sono raro
(2.3/2 dias) e sem volante de horário (circadiano sofria o α baixo sem poder
se adaptar). Consertos E9c: fix do partiu (corr do estimador 0.03→0.77 com
dados ricos), gene de hora-preferida-de-dormir + força do bônus (o volante).
As MESMAS predições abaixo valem para o E9c.

## E9c — RODADO 2026-09-01: metade confirmada, metade refutada COM teto medido

CONFIRMADO 3/3: corr(lei aprendida, k_agua oculto) = 0.73/0.69/0.67 nos que
consolidam, 0.0 no fixo — **o ser aprende a física oculta do próprio mundo
dormindo** (aprendizado-em-vida por forma fechada, gateado pelo sono: FUNCIONA).
REFUTADO: saber não pagou (fixo 19.1 > circadiano 14.0 > constante 11.1).
TETO MEDIDO DEPOIS (erro de método — era antes): ignorância custa 15.8% da
vida parado fervendo = teto de +2.4 entregas; os aprendizes perderam 5-8 —
pagaram >2× o teto em paranoia do previsor (risco×lei crescente = co-adaptação,
o colapso 4.1 da s1) e sono extra. Mecanismo de APRENDER validado; mecanismo
de USAR mal desenhado.

E9d (a rodar): penalidade de risco LIMITADA (clamp) + consolidação SÓ no
descanso que já ia acontecer (custo marginal zero) + predição: aprendiz
captura ≥1 entrega do teto de 2.4 (fixo + parte do teto).

## E9d/E9e — RODADOS 2026-09-01: a contabilidade fechou

E9d (risco clamp): gap fixo−aprendizes caiu −7→−3.3; corr subiu (até 0.85).
E9e (braço aprende-não-usa): custo de APRENDER = −1.85 (sono espalhado);
custo de USAR = −1.45 (previsor ≤0 em 3/3); teto = +2.4. Mesmo captura
perfeita renderia +0.5 líquido — margem do mundo apertada demais.
VEREDITO DO BLOCO: aprender-dormindo VALIDADO (corr 0.65-0.85, 12/12
braços-semente, lei POR MUNDO); lucrar exige sono em BLOCO em casa
(amortiza o −1.85) e/ou mundo com teto maior → E11-cidade. Ver 00-NEGATIVOS.

## E9c — predições originais (herdadas do E9b)

Mundo base + água de radiador com lei k_agua SORTEADA POR MUNDO. Braços SerSono:
fixo (α=0) · constante (α=.55) · circadiano (α por horário 1.0/0.5/0.2).

1. corr(lei aprendida, k_agua oculto) > 0.7 nos braços que consolidam; ~0 no
   fixo — o ser APRENDE a física do próprio mundo dormindo.
2. circadiano e constante > fixo em fitness (aprender em vida paga; a lei não
   é evoluível por construção).
3. Curva entregas-por-dia SOBE nos que consolidam (dia 5 > dia 1 além do
   ruído); plana no fixo — aprendizado em vida visível.
4. circadiano: sono concentra em 20h-00h (histograma) MAIS que no constante —
   a rotina emerge da moeda de retenção. Se circadiano ≈ constante em fitness,
   registrar: o gradiente de α não foi forte o bastante pra pagar o
   deslocamento de horário (dose baixa), não que consolidar não paga.

## E6 — tálamo no ser (doc 20) — predições 2026-09-01, ANTES de rodar

Gate por órgão POR PASSO lendo contexto interno (need + carregando); custo por
CONSULTA. Braços: sempre-ligado · tálamo contextual · cego (só bias — QUANTO
sem QUANDO) · poda-curta (E8 campeão, estático). Mundo ruas, 3 sementes, NP=54.

1. tálamo ≥ sempre em fitness (entregas ~iguais, custo menor).
2. tálamo > cego além do ruído ⟺ o QUANDO importa. Empate = "duty aprendido
   basta" (eco do refutado 'rotear por estatística') — registrar como está.
3. Δconsulta da ROTA carregando passageiro > 0 nas 3 sementes (roteamento
   contextual visível).
4. tálamo vs poda-curta: sem predição forte — dinâmico vs estático é medição.

# Predições — mundos `ruas` e `semgps` + arqs `mem custo` e `mapa servico` — 2026-08-31

Registradas ANTES de qualquer bateria (mini-bateria de CALIBRAÇÃO das constantes
do mundo é permitida; as predições valem para a bateria cheia). Motivação
(Leonardo): tirar os oráculos — o táxi só sabe o que dá pra saber estando lá.
ARQS agora são 7 (I8: todas com NP=36, pesos mortos nos menores).

| mundo | oculto | predição |
|---|---|---|
| ruas | congestão crônica por nó, invisível nos vizinhos (sorteada POR MUNDO — evolução não decora) | **mem custo > reativo além da amplitude entre sementes** (lembrar rua ruim = desviar); diádica/EMA/corpo ≈ reativo (memória do tipo errado); mapa servico ≈ corpo |
| semgps | oráculo distância-até-serviço removido na fonte (features E corpo/híbrido leem constante) | **mapa servico > todos**; corpo ≈ reativo (perdeu o oráculo); reativo cai vs base com MAIS avarias de combustível (não acha posto) |
| base (controle das arqs novas) | nada | mem custo ≈ reativo (congestão do base é ruído sem estrutura — nada útil pra lembrar); mapa servico ≈ corpo (oráculo ds já está nas features, mapa é redundante) |

Critério de falha: se `mem custo` não bater o reativo em `ruas` E `mapa servico`
não bater em `semgps`, a tese "esconder o oráculo faz a memória CERTA pagar"
falha aqui — e como cada arq foi desenhada exatamente para o buraco do seu mundo,
a culpa não pode ser "arquitetura errada": ou o custo escondido é pequeno demais
(calibração, medir teto: rodar clarividente com congestão visível), ou memória
in-life não é selecionável nesta escala de episódio.

Teto físico a medir ANTES da bateria cheia (regra métrica-de-degrau): em `ruas`,
rodar o reativo com congestão VISÍVEL (clarividente) — o gap clarividente−cego é
o máximo que qualquer memória pode recuperar. Se < amplitude entre sementes,
engrossar cron_alto/cron_frac antes de rodar.

## MEDIDO 2026-08-31 — `ruas` REPROVADO no teto, com mecanismo

Teto clarividente−cego ≈ 0 ou NEGATIVO em 3 calibres (alto 1.6/3.5/6.0, n=26 e
52, evolução P=2048 G=40, 3 sementes) e alto=8.0 matou o mundo (fuel escalava
com o jam → morte em série; consertado: no `ruas` o jam custa TEMPO, físico só
30%). **Mecanismo do zero**: a política é gulosa de 1 salto e o oráculo `d_alvo`
não sabe de congestão — evitar o vizinho engarrafado não reroteia; o `d_alvo`
puxa de volta pro mesmo nó no passo seguinte. Evitação local não compõe rota
global. Memória de congestão só pagaria com REPLANEJAMENTO (distância ciente de
congestão) — que nenhuma arq linear de 1 salto tem. `ruas` fica no código como
negativo documentado; NÃO rodar bateria cheia nele com as arqs atuais.

## E4 — órgão calculista no `ruas` (doc 19 §4) — predição 2026-08-31, ANTES de rodar

Braços: reativo (piso) · mem custo (memória SEM cálculo — controle, já medido
teto 0) · rota calculada (memória + Floyd-Warshall sobre custos lembrados,
K=16). Mundo ruas cron_alto=3.5, 3 sementes, evolução conjunta pareada.

**Predição**: rota calculada > reativo E > mem custo, além da amplitude entre
sementes; peso de confiança no órgão evolui positivo e consistente entre
sementes. mem custo ≈ reativo (replica o negativo). Se rota calculada NÃO
vencer: ou o custo crônico ainda é pequeno demais frente ao desvio (checar
comprimento médio do desvio vs 3.5), ou a mistura órgão×GPS confunde a
evolução (testar órgão SUBSTITUINDO d_alvo em vez de somando) — declarar qual.

## `semgps` — mini-escala INCONCLUSIVA, vai pra bateria cheia

Mini (P=2048, G=40, 4 cidades treino): amplitude entre sementes 4.2–5.5 >>
qualquer gap. Sem poder estatístico nesta escala — a predição registrada acima
se decide na bateria cheia (P=8192, G=100, R=8, ≥3 sementes), na fila do Colab.
Mundo validado no portão (perito 6.7, razão 3–7.5×, 7 arqs spread 0.000).

## ECO-FUEL V2 — predições 2026-09-01, ANTES de rodar (achado do replay visual)

Censo instrumentado: pane-seca domina as paradas (25-34/episódio, ~1 a cada 50
ticks; 450-600 ticks parados só de fuel). O táxi ABASTECE (15-31×) e quebra
mesmo assim: +30 de recarga paga 3-4 ruas; pane devolve fuel=15 quase de graça.
O jogo real virou "gerir pane", não "navegar" — suspeita de por que memória
espacial nunca paga e reativo-corpo sempre ganha.

A/B `eco2` (posto enche o tanque; pane dá fuel=5), base, reativo vs banco EMA vs
híbrido, 3 sementes, P=2048 G=60 R=8:
1. pane-seca/episódio cai >5× com eco2.
2. fração parada cai de ~45-55% para <25%.
3. entregas sobem para TODAS as arquiteturas (maré que levanta os barcos).
4. o GAP reativo−memória no base NÃO muda de sinal (base continua observável;
   eco2 não cria estrutura oculta — se memória passar a pagar no base, há outro
   mecanismo que não entendi e vou declarar).
5. (decisiva, rodada depois) semgps+eco2: com navegação valendo de novo, o
   mapa-serviço tem sua chance REAL — re-testar a predição que a s0 matou.

## ARENA v1 — predições 2026-09-01, ANTES da primeira evolução

Mundo: n=120 nós, K=6 táxis DISPUTANDO no mesmo mundo, visão raio 7, sem
oráculo de serviço, congestão = densidade real de táxis, serviço capacidade 1
(fila), pane+sem-dinheiro = morte, fome cravada 60 ticks = morte (vida ganha).
Portão: porte 7/7 spread 0.0000; assentos sem vício. Perito do mundo pequeno
faz 0.31 entregas e morre 88% — o mundo novo é OUTRO jogo.

1. evolução (reativo, P=512, G=30) supera o perito >3× em entregas e derruba
   mortalidade da elite para <40%.
2. ficar parado NÃO domina (com fome-morte); táxis evoluídos ANDAM (>30% ticks).
3. banco EMA ou mem custo > reativo ALÉM da amplitude entre 3 sementes — na
   cidade grande com visão local, lembrar onde há gente/serviço finalmente tem
   o que codificar. ESTA é a predição central da virada-arena.
4. táxis evoluídos se ESPALHAM (var da densidade por nó CAI vs população
   aleatória) — evitar aglomeração emerge da disputa, sem ser programado.
5. mortes por fome ≈ 0 na elite (comer é barato); mortes restantes = pane.

### ARENA v1 — RECALIBRAÇÃO DECLARADA (a única permitida) 2026-09-01 11:55

T=1500: mortalidade 100% em TODAS as arqs/sementes (degrau batido). Causa
geométrica declarada: cidade 4.6× maior com os MESMOS 3-4 nós de cada serviço
(gerar_cidade tinha contagens fixas), invisíveis além do vizinho — achar comida
às cegas é impossível por construção, não por mérito. Conserto: densidade de
serviço escala com n (n=26 bit a bit igual ao original; n=120 → 14/14/9/18/9).
As 5 predições ARENA v1 continuam valendo, agora contra o mundo consertado.
