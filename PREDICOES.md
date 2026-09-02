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

## E12 — RESERVA (energia em 2 compartimentos + peso no chassi) — 2026-09-01 20:45, ANTES de rodar

Pedido do Leonardo: "combustível = calorias; sobra do dia vira reserva se não
for consumida por crescer/cérebro; a reserva PESA no chassi (lento, mais água,
mais fome, dorme pior); conversão lenta e com perda; a perda pode variar e o
cérebro desvendar". Números cravados por ele: reserva paga o cérebro / perda
~30% / teto limitado. Mundo: base + relógio (dia=240) + NOITE 22h-6h (posto
fechado, 1 de 6 passageiros acordado) + eco2. Reativo, NP=NF+18 (NF agora 21:
+reserva, +sin/cos hora). Preset rápido P=1024 G=20 T=600 R=4 × 3 sementes.

Teto medido ANTES (regra 1, N2/N10): perito à mão no mundo-noite faz 18
panes/3 dias e fica parado 74% da noite — a noite MORDE (N13 tinha 0 panes).

1. `noite` < `dia` por ≥ 3 de fitness: a noite magra custa (referência).
2. TETO da reserva (= panes evitáveis × custo da pane) no `noite` evoluído
   entre 1 e 6 de fitness. Se < 0.5 → reserva sem trabalho → negativo com
   mecanismo (o evoluído já dorme a noite toda e não precisa de gordura).
3. `reserva` (sem peso) ≥ `noite` — seguro grátis não perde além do ruído
   (amplitude entre sementes). Ganho ≤ teto.
4. `reserva+peso` ≤ `reserva` (o peso cobra) e — a aposta — `reserva+peso` ≥
   `noite`: mesmo pagando peso, sobreviver à noite compensa. Se `reserva+peso`
   < `noite` além do ruído: o peso está caro demais OU a reserva nunca se forma.
5. COMPORTAMENTO (o que vale mais que o número): (a) n_mob > 0 nas duas
   reservas — a reserva é USADA à noite; (b) `res_media` em `reserva+peso` <
   `res_media` em `reserva` (evolução mantém a gordura baixa quando ela pesa);
   (c) fuel_22 (tanque às 22h) em `reserva*` > em `noite` — "encher antes da
   noite" emerge (economia de precaução sem ninguém programar).
6. Fase B (cérebro come calorias, KAPPA_F=.05/consulta): gap `talamo` −
   `sempre` MAIOR que no E6 (fitness-κ), porque agora o cérebro ligado 100%
   drena o tanque que salva a noite. Se o gap encolher: calorias do cérebro
   são baratas demais neste mundo (declarar e recalibrar KAPPA_F uma vez).

**v1 (2026-09-01 20:45) INVÁLIDA — mundo morto, não conta contra as predições.**
Todos os braços deram ent 0.2–0.4 em 5 dias (base evoluído dá 15–18). Causa
isolada com o perito (mesmo genoma, 6 configs): `eco2` puro dá fuel=5 após
pane e 5 não paga UM salto até o posto → pane de novo → espiral (perito: ent
8.0→2.9, av_fuel 25→48). A evolução achou o ótimo local "ficar parado" (fit
−0.6). Lição: `eco2` tinha predição registrada mas NUNCA foi rodado — usei
flag de mundo não validada. Registrado como N14. v2 = `pane_fuel=15` (posto
ainda enche o tanque), braço `base` como âncora. Predições 1–6 mantidas
como estão, sem editar.

**v2 (pane_fuel=15) rodou, viva** (base 5.75 ≈ dia 5.66; noite 2.74; reserva
2.54; reserva+peso 2.88; come:sempre −0.11; come:talamo 1.62). Reserva
OCIOSA: res~4/60, conv/dia 6, fuel22 32–33 (< 34 do noite), mob 1.4/vida
com 17 panes/vida. Antes de declarar negativo, v3 = preset LONGO (G=60,
T_evo=1200 = 5 meias-noites no treino) + braço NIVEL=30. Predição v3:
7. se a reserva é explorável dado tempo: conv/dia > 15, res_media > 15,
   fuel22(reserva*) > fuel22(noite) por ≥ 5, e reserva+peso − noite ≥ +0.5.
   Se continuar chapado (res_media < 8, fuel22 igual): a gordura não se forma
   porque o tanque às 22h vive abaixo de NIVEL — falha de DESIGN (o gatilho
   de conversão), não de evolução. NIVEL=30 separa as duas: se N30 forma
   gordura (res_media ≫) e ganha, era o gatilho; se forma e NÃO ganha, o peso
   come o ganho (ou a mobilização é cara demais: 3 passos + perda 15–45%).

**v3 (longo G=60, 5 meias-noites) rodou:** noite 4.83 [4.2–5.6]; reserva 5.34
[5.25–5.48]; reserva+peso 4.50 [3.9–4.8]; reserva+peso N30 4.16. res_media
3.7–4.5 em TODOS (gordura queimada assim que forma: 18 panes/vida drenam);
fuel22 37→39 (+2: "encher antes da noite" NÃO emergiu). Causa estrutural
achada no código (`um_passo`): score de serviço = w·necessidade·disponível;
hora/reserva são features de ESTADO e só deslocam mover-vs-servir em bloco —
o Reativo NÃO TEM alavanca pra "posto às 21h". E12b = `ReativoHora`: os 12
pesos mortos do Reativo viram modulação por hora (sin/cos × 5 serviços) e por
reserva (posto, descanso). Mesmo NP=36 → comparação justa. Telemetria nova:
n_posto (abastecimentos/vida) e pobre_frac (fração de passos com dinh<2).
8. Com a alavanca: fuel22(reserva*) ≥ 45 (> noite por ≥ 5), conv/dia ≥ 15,
   res_media ≥ 10, e reserva+peso ≥ noite. Se fuel22 subir mas res_media
   ficar < 8: a gordura forma e é queimada pelos panes de DIA — o gargalo é
   pobreza (pobre_frac alta: 12 dinh por pane × 18 panes = 216 > tudo que
   ganha), não a noite. Se nem fuel22 subir: a alavanca de hora não é usada
   → evolução não acha planejamento de 3 passos (relógio→posto→dinheiro) em
   60 gerações — negativo do mesmo tipo do N1 (memória decorativa).

**E12b (ReativoHora, longo) rodou:** noite 4.42; reserva 5.13; reserva+peso
4.42; N30 4.07. fuel22 37–39 (alavanca de hora NÃO usada), res~4–5 de novo.
Predição 8 → ramo 3: evolução não acha o plano de 3 passos. Dado novo:
`pobre_frac` 0.36–0.46 (o ser não tem 2 dinh pro posto em ~40% da vida) com
posto 8–12×/vida vs 17–19 panes/vida. Pane = 12 dinh × 18 = 216 > renda
(~11 entregas × ~12). v4 = braço RICO: `pane_dinh=0` (única mudança).
9. Se a pobreza é o gargalo: pobre_frac < 0.10, posto ≫ panes (av_fuel < 8),
   fuel22 ≥ 45, res_media ≥ 10, e reserva+peso rico ≥ noite rico. Se mesmo
   rico a gordura não forma (res_media < 8): o gargalo não é dinheiro — é
   que o tanque só sobra à meia-noite quando o ser abastece tarde, e nada
   no repertório faz isso → a reserva precisa de OUTRO gatilho de formação
   (conversão contínua acima de NIVEL, não em lote à meia-noite).

**v4 (rico, pane_dinh=0) rodou:** noite 8.21, reserva 7.85, reserva+peso
7.09; pobre_frac 0.06–0.09 ✓ mas av_fuel 16.5–17.7 (previsto < 8 ✗) e
res_media 3–5 ✗. Dinheiro NÃO era o motivo das panes. Emergente: com reserva
o ser vai MENOS ao posto (6.3 vs 10.2/vida) — a gordura substitui o posto,
não a noite. Hipótese que sobrou: o Reativo não tem previdência pra DESVIAR
até o posto (mesmo mecanismo do N1/N2: 1 salto, sem replanejar). Teste:
`Corpo` (steer pro serviço da maior necessidade via dsa) no mesmo trio.
10. Se é falta de previdência: Corpo faz av_fuel < 8 e posto > 15/vida; com
    reserva, res_media ≥ 10 e reserva+peso ≥ noite. Se Corpo pane igual (~17):
    a pane é ESCOLHA da evolução — pane devolve 15 de fuel por 18 passos e é
    aceita como "posto grátis lento"; o conserto é físico (pane sem fuel +
    reboque), não neural.

**v5 (Corpo) rodou:** noite 4.97, reserva 4.71, reserva+peso 4.42, N30 4.07;
av_fuel 15–17 ✗ (não é falta de previdência). **v6 (reboque):** perito
espirala (ent 3.1, pobre 0.81); evolução `dia reboque` fit −4.33; com multa 4:
−1.31; com multa 0: dia 0.24, noite −1.24, reserva −1.10, res+peso −2.71,
av_fuel 22–26 — mundo MORTO em qualquer multa. Conclusão: a pane que devolve 15
de fuel é o que SUSTENTA a economia — sem ela não há mundo; com ela não há sobra
(fuel22 31–39, res~ 3–5). A gordura nunca teve o que guardar.

**v7 (mundo COM sobra: fuel × 0.5, resto E12 padrão) — 2026-09-01 21:40, ANTES de rodar**
11. Com o salto custando metade, o tanque sobra: fuel22 ≥ 50, conv/dia ≥ 15,
    res_media ≥ 20 (gordura FORMA), av_fuel < 8. Aí a pergunta original vale:
    reserva − noite ≥ +0.5 (seguro grátis paga) e reserva+peso fica ENTRE
    (o peso morde porque agora há gordura). Se mesmo com sobra res_media < 8:
    o lote da meia-noite (NIVEL=50) é o furo, não a escassez.

**v7 rodou (rápido + longo, 6 braços, JSON `e12_reserva_longo_sobra`):** 11 ✓
— gordura forma (res~ 17.7 rápido, 20.6 longo; conv/dia 13–15; panes 5). Seguro
grátis +1.26 (rápido) / +0.34 (longo). Par justo reserva+peso vs noite+peso:
−0.41 (rápido) / **−1.66** (longo, 3/3 sementes); meio peso −0.38 / −0.38.
Emergente: sob peso o ser fica magro — 8.9 vs 17.7 no rápido, só 17.8 vs 20.6
no longo. Fecha o E12: física funciona, vantagem não sai do ruído (doc 26 §6).

**v8 (sobra + reboque: pane sem fuel grátis, mundo com renda) — 2026-09-01 22:05, ANTES de rodar**
Fecha a porta (a) do §6.3: no mundo fuel×0.5 a economia fecha sem o subsídio?
12. `dia sobra reboque` vivo: fit ≥ 8 e panes < 5 (rápido). Se vivo, a pane
    agora custa fuel de verdade e a reserva vira o ÚNICO seguro da noite:
    reserva − noite ≥ +1.0 (maior que os +0.34 do v7) e reserva+peso ≥
    noite+peso (o peso ainda morde, mas a gordura tem trabalho real).
    Se `dia sobra reboque` morre (fit < 3): nem com a metade do custo a renda
    sustenta o posto — a economia do táxi é estruturalmente subsidiada e o
    conserto é de RENDA (preço da corrida), não de física da pane.
    Se vivo mas reserva+peso < noite+peso: a reserva como desenhada não paga
    nem sendo o único seguro — linha fechada de vez.

**v8 rodou (rápido):** `dia sobra reboque` VIVO, fit 9.61 (12 ✓ primeira
metade; panes 9.1, não < 5). Noite 4.65; reserva 4.70 (**+0.05**, ✗ ≥ +1.0);
noite+peso 2.96; reserva+peso 2.40 (−0.56); meio 3.40 (+0.44, ruído). A reserva
NÃO paga nem sendo o único seguro. Mecanismo (lido no código, não é o portão
`res>0` — mobiliza qualquer quantia): a ENTRADA é só a sobra da meia-noite
acima de NIVEL, ~10 fuel/dia, contra 3 panes/dia × 15 = 45/dia de buraco.
Cobre 20% e nunca alcança. Pior: a conversão tira fuel do tanque exatamente
quando o posto fecha e devolve com perda + 3 passos. Poupança só pode pagar
quando a escassez é RARA e GRANDE (fome), não diária e pequena (noite) — a
noite o tanque resolve.

**v9 (greve do posto: escassez rara e grande) — 2026-09-02 09:20, ANTES de rodar**
Mundo: sobra (fuel×0.5) + reboque (pane sem fuel grátis) + SEM noite + a cada
4 dias o posto fecha o DIA INTEIRO (passageiros normais). Gordura acumula 3
dias e tem UM trabalho grande no 4º.
13. `greve4` custa ≥ 2.0 de fitness vs `dia s+r` (teto). `greve4 reserva` −
    `greve4` ≥ +1.0 (res~ ≥ 15, mobilizações concentradas no dia de greve);
    N30 ≥ N50 (mais entrada); `greve4 reserva+peso` ≥ `greve4` (positivo MESMO
    com peso — cada unidade de gordura vale mais aqui). Se reserva ≈ greve4
    mesmo assim: a entrada de 10–20/dia é pequena demais pra qualquer nicho,
    o design precisa de outra fonte (abastecer a reserva no posto) — linha
    fechada de vez.

**v9 rodou (rápido + longo, 9 braços, JSON `e12_reserva_longo_greve`):** 13 ✓
nas 3 primeiras cláusulas — greve custa −4.53; reserva **+1.20** (N50) /
**+1.84** (N30) sobre greve4, 6/6 sementes positivas; N30 > N50. Cláusula do
peso: reserva+peso −0.32 vs greve4 (✗) mas +1.71 vs o par justo greve4+peso;
meio peso −0.57 — empate dentro do ruído (±1.5; `greve4 peso meio` deu +0.65
sobre greve4 sem poder). Cobertura 41% da greve, prevista pela lei 37–47%
(estoque I/f 37–47 vs buraco S≈100). Lei da poupança em doc 26 §7.2:
benefício = v·min(I, f·S, f·RES_MAX); ótimo I* = f·S. E12 FECHADO.

## E13 — CORPO = CARRO (dano real, morte, gordura fácil, sono que come) — 2026-09-02 10:10, ANTES de rodar

Leonardo: "colocar dano no carro, dano real, fura o pneu demora mais, motor
aquecido o carro desliga, o reboque custa mais, pra que os seres tentem deixar
o carro o mais vivo possível porque é o corpo deles" + "mais gordura, ela entra
mais fácil, porque dormir e melhorar o cérebro custa caloria".

Mundo: sobra (fuel×0.5) + reboque + pane_dinh 20 + noite + `corpo`
(vida 100; pane −6, furo −5 e 30 passos parado com pneu→40, óleo −12,
motor >92 DESLIGA 20 passos e −10, rodar machucado −0.15/passo; ferido =
tempo e consumo ×(1+0.6·dano); oficina +30 por 10 dinh; vida≤0 = morte).
Teto medido (perito, 64 réplicas): **86% morrem** em 5 dias (t_vida 60%),
dano 137 = quente 81 + panes 44 + furos 7 + rodar ~6; oficina 7.1/vida.
Feature nova `e_dano` (zero sem corpo); portão base bit-exato (7.9740/25.1302).

14. Morte SELECIONA: campeão evoluído (G=20) morre < 10% (perito 86%) e
    t_vida > 0.95; quente cai ≥ 50% (8.1 → ≤ 4) — a evolução aprende a não
    ferver o motor (oficina antes dos 80 °C ou rodar menos quente). Se morrer
    ≥ 30%: o mundo é letal demais pra política de 1 salto (dano por passo
    domina) — recalibrar D_QUENTE/D_RODAR, não o cérebro.
15. `corpo` custa ≥ 2.0 vs `noite s+r` mesmo evoluído (o corpo exige
    oficina/tempo/dinheiro que antes eram grátis).
16. Gordura fácil (`reserva_posto=20`, I ≈ 3 postos/dia × 18 = 54/dia ≥ f·S 45):
    pela lei, regime vira "teto = buraco": panes < 3/vida e reserva_posto −
    corpo ≥ +1.0 MESMO com peso (.10/.30). `reserva` só-meia-noite (I=10)
    fica ≈ corpo (±0.5), como no v8.
17. Sono come (5 fuel/descanso): gordura média cai ≥ 30% vs reserva_posto e
    fit dentro de ±1.0 (custo ≈ 1 tanque/vida); se fit cair > 1.5, o ser está
    dormindo com a gordura (mob sobe) — dormir virou o buraco.
18. Emergente esperado: `n_oficina` sobe com corpo (perito 7 → evoluído
    ≥ 8) e `vida_fim` > 50. Se vida_fim < 30 com mortos < 10%: o ser vive no
    limite (repara só pra não morrer) — igual ao "pane como posto lento".

**E13 longo rodou (G=60, T_evo=1200):** noite s+r 6.45; **corpo 7.20** (15 ✗
invertida: +0.75 — a dor ensina: panes 15.5→8.0, oficina 0→7.5); mortos 0.39
(14 ✗: < 10% previsto; treino com morte baixou 52→39); reserva 4.80, res-posto
4.74 (16 ✗), sono 4.42 (17 ✓ gordura −21%, fit −0.3). Perito instrumentado:
0 panes com res>0 (sem bug); reserva BIMODAL — cheia (cap 60) 30% do tempo,
vazia 46–59%; uma noite drena os 60 e o resto vira pane; posto 4.4×/vida.
Braços de reserva carregam peso .10/.30 e fervem mais (2.4→4.0) — falta o par
justo.

**E13b (decomposição peso × reserva × cap) — 2026-09-02 11:05, ANTES de rodar**
19. `corpo peso` (só tanque pesa) = corpo −0.5 a −1.5. `res-posto SEM peso`
    ≥ corpo +0.5 e panes ≤ 6 (a reserva ajuda quando não pesa). `res-posto
    SEM peso, RES_MAX 120`: panes ≤ 4, mortos ≤ 0.25 (cap deixa de morder: a
    noite cabe na gordura). `res-posto COM peso, R120`: entre os dois. Se nem
    sem peso e cap 120 as panes caem: o buraco não é o tanque, é a ROTA
    (o ser roda à noite sem posto e pane onde está) — a gordura não resolve
    rota.

**E13b rodou (longo):** corpo peso 5.48 (−1.72 ✓ faixa); reserva s/peso 7.46
(+0.26, ≥ +0.5 ✗ — lei: I=10); res-posto s/peso 7.82 (+0.62 ✓, panes 7.4 ✗
> 6); **res-posto s/peso cap 120: 9.57 (+2.37, 3/3), panes 5.9, mortos 0.31**
(✓ direção, ✗ limiares 4 / 0.25); res-posto peso cap 120: 5.68 (−1.5 vs corpo,
✗ "entre os dois" — o peso come tudo). Cap mordia; peso é o custo dominante.

**E13c (armadilha de pobreza) — 2026-09-02 11:50, ANTES de rodar**
Diagnóstico do campeão R120 (3 sementes, 384 réplicas): mortos morrem de PANE
(16 até morrer; causa nas últimas 50 passos = pane 16, resto 0.4) e quebrados
(dinh 0.6–1.0); vivos fazem 1.3 panes/vida com vida 83–90. Morte no dia 2–3,
meio-dia. Perda oculta não pesa (0.26–0.37); cidade pesa (1001: 17–23%,
1002: 30–47%). Mecanismo: reboque 20 → pobre → sem posto (2) nem oficina (10)
→ pane → morte. Armadilha com gatilho aleatório (a 1ª pane).
20. Mesma config vencedora (res-posto s/peso cap 120) com `pane_dinh` 8:
    mortos 0.31 → ≤ 0.20; com `pane_dinh` 0 (só o corpo paga a pane, −6 vida):
    mortos ≤ 0.12, dinh dos mortos > 5, panes sobem (pane barata) mas dano
    total cai. Fit sobe ≥ +1.0 nos dois. Se mortos ficam ~0.3 com multa 0:
    não é dinheiro, é rota/noite (o ser roda sem posto) — a alavanca seria
    o sono noturno, não a economia.

**E13c rodou (longo):** reboque 8: 9.35, mortos 0.27 (≤ 0.20 ✗); **reboque 0:
10.67 (+1.1 ✓), mortos 0.17** (≤ 0.12 ✗ perto), pobre 0.28 → 0.07 ✓, panes
5.9 → 6.5 ✓ (pane barata), dano 74 → 84 (✗ previa cair). Metade das mortes
era a multa em dinheiro; o resto é rota/noite. Regras 11 e 12 em 00-NEGATIVOS.

**E13d (calibração do peso) — 2026-09-02 12:05, ANTES de rodar**
Config vencedora (res-posto s/peso, cap 120, reboque 0 = 10.67, mortos 0.17)
com peso ligado em duas escalas.
21. WF/WR = .03/.10: fit ≥ 9.9 (perde ≤ 0.8), mortos ≤ 0.22, fervura ≤ 3.5 —
    o peso é SENTIDO (res~ cai ≥ 15% vs sem peso) sem matar. .05/.15: fit
    ≥ 9.2, mortos ≤ 0.25. Se .03/.10 já perde > 1.5: o peso não tem escala
    viável nesta economia (a margem é fina demais) — mudar a renda antes de
    insistir no peso.

**E13d rodou (longo, config vencedora reboque 0 = 10.67 s/peso):** .03/.10 →
9.78 (−0.89; ≥ 9.9 ✗ por 0.1; mortos 0.18 ✓; fervura 3.4 ✓; res~ 53 vs 52 —
não emagreceu ✗); .05/.15 → 9.46 (✓); **.10/.30 → 9.23, mortos 0.16** — com a
multa zerada o peso cheio custa −1.44 (custava −3.9 com reboque 20). O peso
era amplificado pela armadilha: pesado → pane → quebrado → morte. Os números
do Leonardo são viáveis sem a multa em dinheiro.

**E13e (os 17% que restam: rota noturna?) — 2026-09-02 12:35, ANTES de rodar**
Config vencedora (res-posto, cap 120, reboque 0, peso .10/.30) com arqs que
têm alavanca de HORA (ReativoHora: serviço × sin/cos da hora) e de ROTA
(Corpo: desvia pro serviço da maior necessidade).
22. Se a morte restante é rodar de noite sem posto: ReativoHora aprende
    "descansar à noite / posto às 21h" → mortos ≤ 0.10, par_fad/par_noite
    sobem, panes ≤ 4. Corpo (rota pro posto) → mortos ≤ 0.12. Se ambos ~0.16:
    o resto é azar de cidade (1002 mata 2× a 1001) — teto da política de
    1 salto, próxima alavanca é sono em bloco (doc 24) ou memória de posto.
