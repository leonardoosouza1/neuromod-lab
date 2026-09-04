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

**E13e rodou (longo):** ReativoHora 7.75, mortos 0.27 (✗ pior que o Reativo
9.23/0.16 — 12 pesos a mais pra buscar e panes 8.0); Corpo 8.44, mortos 0.17
(✗ igual). Nenhuma alavanca de hora ou rota reduz os 17%: teto da política de
1 salto neste mundo (cidade 1002 mata 2× a 1001). Próxima alavanca: sono em
BLOCO à noite (doc 24) ou memória de posto — mecanismo novo, não peso novo.

**E13f (RECOMENDADO: massa + gordura contínua) — 2026-09-02 13:10, ANTES de rodar**
Leonardo: "gordura acumulável ao longo do tempo, peso influenciando, cálculo
base geral e o peso extra afeta". Peso = massa/chassi com massa = 1000 kg +
0.75·fuel + 2.5·res + 80·(carregando) — tanque cheio +7.5%, gordura cheia
(120) +30%, passageiro +8%; tudo (tempo, fuel, calor, fome, fadiga, sono)
deriva daí. Gordura: a cada passo 2% da sobra acima de NIVEL=50 vira reserva
(perda 10%) — acumula devagar, sem lote, sem compra no posto. Mundo: corpo +
cap 120 + reboque 0.
23. `recomendado` fit ≥ 8.5 e mortos ≤ 0.20 (perto do 9.23/0.16 do res-posto
    com peso .10/.30); gordura FORMA devagar (res~ 25–50, conv em ≥ 60% dos
    passos — não 5 lotes/vida). Taxa .05 ≥ taxa .02 (se a entrada limita).
    `sem gordura` ≤ recomendado − 1.0 e mortos +5 pp (gordura vale). `sem
    peso` ≈ recomendado + 1.0 (peso custa, não mata — como no E13d). O
    passageiro pesando é novo: se `sem gordura` cair > 2 abaixo do `corpo
    reboque 0` equivalente, o passageiro (+8%) é o custo, não a gordura.

**E13f rodou (longo):** recomendado 8.16 / mortos 0.21 (23: ≥ 8.5 ✗ por 0.3,
≤ 0.20 ✗ por 0.01); gordura forma devagar ✓ (res~ 45, mob 3.2); taxa .05 →
7.68 ✗ (pior: tira fuel do tanque rápido, panes 8.2); sem gordura 7.34
(−0.82, ✗ por 0.2; mortos +6 pp ✓); sem peso 10.42 (**+2.26**, ✗ previa +1.0
— o peso por massa custa mais; fervura 2.7 → 4.7). Suspeito do passageiro.

## Fila autônoma (Leonardo saiu 2026-09-02 13:40) — predições ANTES, em bloco

**E13g (de onde vem o custo do peso por massa):**
24. `taxa .01` ≥ `.02` +0.3 (acumular mais devagar drena menos o tanque);
    `pax 0 kg` = +1.0 a +1.5 (o passageiro é a maior parte do custo: pesa 8%
    em quase todo passo carregado); `gordura 1.5 kg` = +0.5 (gordura média 45
    → 112 kg vs 68 kg: pouca diferença). Se `pax 0` ≈ recomendado: o custo é
    a fervura por peso do tanque+gordura, não o passageiro.
**E13h (vida longa: T_aval 2400 = 10 dias; e cidades 2000+ nunca vistas):**
25. Recomendado treinado 5 dias, avaliado 10: mortos ≤ 0.35 (não dobra —
    quem passa do dia 3 vive; morte é cedo), gordura no fim ≥ 60 (acumula
    "ao longo do tempo"), fit/dia igual ao dos 5 dias ± 15%. Cidades 2000+:
    fit dentro de ±1.5 do 1000+ (generaliza; cidade pesa até 2×).
**E13i (replicação "a dor ensina", 5 sementes):**
26. corpo − noite s+r ≥ +0.4 na média de 5 sementes, ≥ 3 de 5 positivas;
    panes corpo ≤ 60% das de noite s+r em todas. Se ≤ 0: o +0.75 era ruído.
**E13j (sono come; cérebro come — tálamo × sempre no recomendado):**
27. `sono 5`: gordura −20% e fit −0.5 (dormir compete com engordar);
    `cerebro come` com Reativo: nada muda (Reativo não tem custo neural) —
    controle. `--arq talamo`: fit ≥ recomendado −1.5 e mortos ≤ 0.25;
    `--arq sempre`: colapsa (fit < 3, mortos > 0.5: o cérebro come o tanque
    e a noite mata) — o E12 fase B no mundo-corpo, agora com morte.
**E13k (greve 1 dia em 4 no recomendado):**
28. Greve custa ≥ 3 vs recomendado; `com gordura` − `sem gordura` ≥ +1.5 na
    greve (maior que os +0.8 sem greve: gordura contínua acumula 3 dias e
    cobre a fome rara — lei do E12 §7); mortos sem gordura ≥ 0.40.

**E13g rodou:** 24 ✗ nos três. taxa .01 → 7.58 (−0.58: menos gordura, res~ 35,
panes 8.7 — .02 é o VALE entre .01 e .05); pax 0 kg → 8.79 (+0.63, previa
+1.0–1.5: passageiro é ¼ do custo); gordura 1.5 kg → 7.77 (−0.4, ruído). O
custo restante (~1.7) é o TANQUE (+7.5%) cruzando o limiar de fervura: fervura
4.0–4.3 em todo braço com peso vs 2.7 sem — o limiar (92 °C) amplifica um
peso pequeno porque o ser evoluído roda encostado nele (N15 de novo: vive no
limite). "Gordo esquenta" é não-linear.

**E13h10 rodou (mesmo campeão, 10 dias):** fit 14.66 (1.47/dia vs 1.63/dia em
5 dias: −10% ✓); **mortos 0.39** (✗ ≤ 0.35): 0.21 nos 5 primeiros dias, ~0.18
nos 5 seguintes — risco ≈ 4%/dia CONSTANTE, não morte cedo (meia-vida ~17
dias). Gordura média 51 (✓ acumula). Quem sobrevive melhora: panes/dia
1.46 → 1.09, fervura/dia 0.94 → 0.67, oficina/dia 2.1 → 1.7.

**E13h20 rodou (cidades 2000+):** fit 4.71 vs 8.16 (✗ ±1.5), mortos 0.35.
Perito (independe da política) por conjunto: 0+ −1.12 / ent 4.1; **1000+ −0.67
/ ent 4.6 (o mais fácil)**; 2000+ −1.38 / ent 3.3 (−28%); 3000+ −1.23 / ent
3.4. O campeão cai −42%: ~⅔ é cidade mais dura, ~⅓ pode ser overfit ao
treino. Consequência: TODOS os números em 1000+ são otimistas ~30%. Daqui pra
frente avaliar em 6 cidades (1000+ e 2000+) — `--teste-seed` já existe.

**E13i rodou (5 sementes, mega-lote de 5 ≠ bit-igual ao de 3):** noite s+r
7.33 [5.9, 8.0, 8.5, 6.7, 7.6]; corpo 6.88 [6.8, 8.5, 5.9, 7.3, 5.9] →
**−0.45** (26 ✗: previa ≥ +0.4). 3/5 positivas mas média negativa; o +0.75 do
n=3 era ruído (replicação > σ: efeito seguiu o n). O que REPLICA 5/5: panes
13.3 → 8.3 e oficina 0 → 6.9 — a dor muda o comportamento; os 38% de mortos
comem o ganho. Corrigido em doc 27 §4.3 e N16.

**E13j rodou:** sono 5 → 6.91 (−1.25; 27 previa −0.5 ✗), mortos 0.26 (+5 pp),
gordura −11% (previa −20% ✗), sono 16 = 3 descansos/vida — dormir custa
tanque → pane → morte; o ser dorme pouco em vez de engordar menos.
`cerebro come` + Reativo = 8.16 bit-igual ao recomendado ✓ (controle limpo:
sem custo neural, a flag não muda nada).

**E13jt rodou (SerTalamo, custo neural sai do tanque):** 7.45 [6.2, 8.6, 7.5],
mortos 0.22, res~ 46 — ✓ (≥ 6.66 e ≤ 0.25): o tálamo paga o cérebro em
caloria e vive. 421 s (5× o Reativo).

**E13js rodou (sempre, todos os órgãos ligados, comendo do tanque):** fit
−0.52, ent 1.0, mortos 0.28, pobre 0.47, panes 4.2 — colapso ✓ (< 3) mas
não por morte (✗ > 0.5): PARALISIA. O cérebro come o tanque antes de o ser
andar; ele fica parado, pobre, e não engorda (res~ 19). Tálamo 7.45 vs sempre
−0.52 = gap 8.0 — o maior de todas as fases B (E6 6.3, E12 1.7): no mundo
onde a caloria é finita e o corpo morre, ligar tudo é fatal de outro jeito.

**E13l (sono em bloco à noite — os 17–21% que restam) — 2026-09-02, ANTES de rodar, implementar só após a fila k**
Mecanismo: à noite (22h–6h), escolher `descanso` vira SONO EM BLOCO — o ser
para até as 6h, recupera a fadiga inteira, e não roda de madrugada com o
tanque baixo (as mortes do §4.5 são panes noturnas longe do posto). É decisão
(o ser escolhe dormir), não roteiro; o Reativo só tem a fadiga como gatilho
do descanso, então a pergunta é se a evolução aprende a "ir dormir" quando
o tanque está baixo à noite.
29. Recomendado + sono em bloco: mortos 0.21 → ≤ 0.15 e panes 7.3 → ≤ 5.5,
    com `par_noite` ≥ 0.85 (dorme mais) e entregas noturnas caindo; fit
    dentro de ±0.5 (perde a madrugada, ganha vida). ReativoHora com o mesmo
    bloco: mortos ≤ 0.12 (tem alavanca de hora pro descanso). Se mortos
    ficam ~0.21: o Reativo não consegue condicionar o descanso à hora — o
    bloco existe mas ninguém entra nele (par_noite igual) — e a alavanca
    precisa ser um órgão (SerVital/tálamo com sinal noite), não a física.

**E13k rodou (greve 1 dia em 4 no recomendado):** greve custa −1.67 (28 previa
≥ 3 ✗); com gordura 6.49 vs sem 5.45 = **+1.04** (previa ≥ +1.5 ✗; sem greve
era +0.82 → a fome rara acrescenta só +0.2); mortos 0.30 vs 0.28 (✗ previa
sem gordura ≥ 0.40). Mecanismo: no mundo-corpo a noite diária JÁ gasta a
gordura (res~ 39, 3.95 mobilizações/vida) — não sobra estoque pro dia de
greve. Duas escassezes competem pela mesma poupança; a diária ganha porque
vem primeiro. Lei do E12 §7 com dois f: o estoque ao chegar a greve é
I/f_noite, não I/f_greve.

**E13l rodou (Reativo + sono em bloco):** 8.30 (+0.14 ✓ ±0.5), mortos 0.18
(✗ ≤ 0.15, mas −3 pp), panes 7.5 (✗ ≤ 5.5), bloco 1.1 noites de 5, par_noite
0.69 (✗ ≥ 0.85). Cláusula de fallback confirmada: o Reativo não condiciona o
descanso à hora — entra no bloco uma vez por vida. Falta o ReativoHora.

**E13m (números honestos + treino de 10 dias) — 2026-09-02 13:05, ANTES de rodar**
30. (a) Recomendado e sono-bloco em cidades 2000+: sono-bloco ≥ recomendado
    +0.3 e mortos −3 pp (o bloco vale mais onde a noite é mais dura). Média
    honesta (6 cidades) do recomendado ≈ 6.4. (b) Treino com vida de 10 dias
    (G=100, T_evo=2400, avaliado em 10 dias): mortos ≤ 0.30 (vs 0.39 do
    campeão de 5 dias em 10 dias) — a seleção vê as mortes tardias e baixa o
    risco; fit/dia ≥ 1.47. Se mortos ~0.39: o risco de 4%/dia é o piso do
    mundo pra política de 1 salto, não falta de treino.

**E13lh rodou (ReativoHora + sono em bloco):** 8.17, mortos 0.19, bloco 1.2 de
5 noites, par_noite 0.70 — igual ao Reativo (✗ ≤ 0.12). A alavanca de hora não
condiciona o descanso à noite (3ª vez que o ReativoHora não usa a hora: E12b,
E13e, E13l). Sono em bloco = −3 pp com n=3; replicar com 5 sementes.

**E13n (replicação do sono em bloco, 5 sementes) — ANTES de rodar**
31. recomendado vs sono-bloco em 5 sementes: mortos −3 pp ± 2 (≥ 4/5
    sementes com menos mortos), fit +0.1 ± 0.5, bloco ~1.1/vida. Se mortos
    ≈ 0: o −3 pp de n=3 era ruído e o bloco é inerte pro Reativo.

**E13m2000 rodou:** recomendado 4.71 (bit-igual ao h20 ✓), sono bloco 4.74
(+0.03; ✗ ≥ +0.3), mortos 0.35 → 0.32 (✓ −3 pp — mesmo efeito que em 1000+:
0.21 → 0.18). **Números honestos (6 cidades):** recomendado 6.44 / mortos
0.28 (✓ ≈ 6.4); com bloco 6.52 / 0.25. O bloco não rende fitness; rende 3 pp
de vida, consistente em 2 conjuntos de cidades (falta o n=5).

**E13m10d rodou (G=100, T_evo=2400 = vidas de 10 dias no treino, avaliado 10 dias):**
recomendado 16.98 (1.70/dia, ✓ ≥ 1.47), **mortos 0.39** (✗ ≤ 0.30: igual ao
campeão de 5 dias em 10 dias — o risco de ~4%/dia é PISO do mundo pra política
de 1 salto, não falta de treino). **Sono em bloco: 18.02 (+1.04) e mortos 0.29
(−10 pp, 3/3 sementes: 0.32/0.29/0.27 vs 0.40/0.42/0.35)**, bloco 1.9 noites
de 10, vida_fim 63 vs 53. O efeito do bloco CRESCE com a vida (5 d: −3 pp;
10 d: −10 pp): o bloco evita as mortes tardias.

**E13o (replicação do bloco em vida de 10 dias, 5 sementes) — ANTES de rodar**
32. G=100, T_evo=T_aval=2400, 5 sementes: sono-bloco − recomendado: mortos
    −7 pp ± 3 (≥ 4/5 sementes com menos mortos), fit +0.7 ± 0.7, bloco ~2
    noites de 10. Se −10 pp segurar em 5/5: é o primeiro mecanismo que
    reduz a mortalidade tardia — vale virar padrão do mundo-corpo.

**E13n rodou (5 sementes, vida de 5 dias):** recomendado 8.76 / mortos 0.18;
sono bloco 7.55 / 0.21 → **−1.21 de fit e +3 pp de mortos** (2/5 sementes com
menos mortos). 31 ✗: o −3 pp de n=3 (e sua repetição em 2000+) era ruído. Em
vida de 5 dias o bloco é inerte ou levemente nocivo (perde a madrugada, não
evita morte). O −10 pp em 10 dias (n=3, §6.9) fica sob suspeita — E13o (5
sementes, 10 dias) decide. 4ª vez que n=3 enganou nesta sessão.

**E13o rodou (5 sementes, vida de 10 dias):** recomendado 18.70 / mortos 0.29
[0.36, 0.35, 0.22, 0.26, 0.26]; sono bloco 17.68 / 0.31 [0.21, 0.31, 0.34,
0.29, 0.42] → **−1.0 de fit, +2 pp de mortos, 1/5 sementes abaixo.** 32 ✗. O
−10 pp de n=3 era ruído. Sono em bloco: inerte-a-nocivo em 5 e 10 dias.
Piso de mortalidade (0.18–0.21 em 5 d, 0.29–0.39 em 10 d) não cede a treino
longo, hora, rota nem sono — teto da política reativa de 1 salto.

**E13p (replicar as DUAS decisões recomendadas, 5 sementes) — 2026-09-02 13:30, ANTES de rodar**
Cap 120 (+2.37, 3/3) e reboque 0 (mortos 0.31 → 0.17) foram n=3, e n=3
enganou 4× hoje. Braços: `corpo res-posto s/peso` (cap 60, reboque 20),
`… R120` (cap 120, reboque 20), `R120 reboque 0`.
33. Cap 120 − cap 60 ≥ +1.5 com ≥ 4/5 sementes e mortos −5 pp; reboque 0 −
    reboque 20 (ambos R120): mortos −10 pp com 5/5 e fit ≥ +0.8. Se cap 120
    < +0.8 ou reboque 0 < −5 pp: a recomendação ao Leonardo cai e o doc 27
    §5 é reescrito.

**E13p_b rodou (5 sementes):** cap 60: 8.06 / mortos 0.33; cap 120: 8.46 /
0.34 → **+0.40, 2/5 sementes acima, mortos +1 pp.** 33 (cláusula do cap) ✗:
o +2.37 (3/3) de n=3 era ruído. A gordura acumula mais (res~ 51 vs 27) e não
muda panes (6.4 vs 6.8) nem mortes. Recomendação "cap 120" ao Leonardo CAI.

**E13p_c rodou (5 sementes):** R120 reboque 0: 9.78 / mortos 0.23
[0.26, 0.23, 0.21, 0.23, 0.23] vs reboque 20: 8.46 / 0.34 [0.38, 0.31, 0.42,
0.27, 0.33] → **+1.32 (4/5), −11 pp (5/5)**. 33 (cláusula do reboque) ✓. A
armadilha de pobreza REPLICA; o cap não. Placar das decisões: reboque 0 ✓
(n=5), peso .10/.30 viável (n=3, a replicar), cap 120 ✗ (ruído).

**E13q (replicar o mundo recomendado, 5 sementes; números finais) — ANTES de rodar**
34. Em 1000+: gordura (recomendado − sem gordura) ≥ +0.5 e mortos −3 pp com
    ≥ 3/5 sementes; peso (sem peso − recomendado) ≥ +1.5 com 5/5 e fervura
    +1.0. Em 2000+, recomendado 5 sementes ≈ 4.7 ± 1; média honesta de 6
    cidades ≈ 6.5 ± 1, mortos ≈ 0.27. Se gordura < +0.3: a gordura contínua
    não paga nem no corpo (e a lei do E12 explica: a noite gasta antes).

**E13q1000 rodou (5 sementes):** recomendado 8.76 / 0.18 (bit-igual ao E13n
✓); sem peso 11.10 / 0.18 → **peso custa −2.34 (5/5), fervura 2.9 → 4.1** ✓;
sem gordura 7.97 / 0.25 → **gordura vale +0.79 (4/5), mortos −7 pp (4/5)** ✓.
34 ✓ nas duas cláusulas de 1000+. Das afirmações do recomendado, as duas
sobreviveram ao n=5 (ao contrário do cap e do sono em bloco).

**E13q2000 rodou (5 sementes, cidades 2000+):** 5.39 / mortos 0.30 (✓ 4.7 ± 1).
**NÚMEROS FINAIS (6 cidades × 5 sementes) do mundo recomendado: fit 7.08,
mortos 0.24.** 34 ✓ (≈ 6.5 ± 1, 0.27).

**E13r (portão do tálamo lê a noite) — 2026-09-02 14:05, ANTES de rodar**
`SerTalamoNoite`: gate = σ(a + b·need + c·carreg + d·noite), 5 genes a mais.
Mundo recomendado + cérebro comendo do tanque, 5 sementes, 5 dias, 1000+.
Referência: tálamo n=3 = 7.45 / mortos 0.22.
35. Previsão HONESTA: efeito ≈ 0 — mortos ±3 pp e fit ±0.5 vs tálamo sem
    noite. Motivo: a morte noturna é o posto FECHADO com o tanque vazio; nenhum
    órgão abre o posto, e os órgãos do SerVital modulam movimento, não
    "ficar parado". Se mortos caírem ≥ 5 pp com ≥ 4/5 sementes: o órgão achou
    um padrão noturno (ver duty por órgão à noite) e é a 1ª alavanca neural
    que mexe no piso. Se subir: 5 genes a mais que G=60 não ajusta (ReativoHora
    de novo).

**E13r_tal rodou (tálamo, 5 sementes, cérebro come):** 7.26 / mortos 0.24
[0.26, 0.11, 0.21, 0.37, 0.24] — espalhamento ±13 pp entre sementes (a maior
variância do dia). Referência para o tálamo-noite.

**E13r_noite rodou (tálamo com noite no portão, 5 sementes):** 7.01 / mortos
0.23 [0.15, 0.21, 0.19, 0.24, 0.35] vs tálamo 7.26 / 0.24 → **−0.25 de fit,
−1 pp** — 35 ✓ (previsão honesta: efeito ≈ 0). Sexta alavanca que não move o
piso (treino longo, hora, rota, sono em bloco, tálamo, tálamo-noite). O piso
de ~0.18–0.24 (5 dias) é do MUNDO × política reativa: posto fechado + tanque
vazio + 1 salto. Mexer nele exige memória de rota ou replanejamento (N2/N10),
não mais um sinal.

**E13s (últimas afirmações n=3 do recomendado, 5 sementes) — ANTES de rodar**
36. taxa .01 e .05 vs .02 (8.76 / 0.18 com 5 sementes): ambas ≤ 8.76 − 0.3
    (o vale replica, ≥ 3/5 sementes abaixo em cada); sono come 5: fit
    ≤ 8.76 − 0.8 e mortos ≥ +3 pp (≥ 3/5). Se .01 ou .05 ≥ 8.76: a "taxa
    ótima" era ruído e qualquer taxa serve.

**E13s05 rodou (taxa .05, 5 sementes):** 7.39 / mortos 0.18 vs taxa .02 8.76
/ 0.18 → **−1.37, 5/5 sementes abaixo** ✓ (36, cláusula .05). Acumular
depressa drena o tanque (panes 7.1 ≈ igual, mas ent 11.3 vs 12.8: o ser
anda menos). Mortalidade não muda.

**E13s01 rodou (taxa .01, 5 sementes):** 8.16 / mortos 0.22 vs .02 8.76 / 0.18
→ −0.60 mas só **2/5 sementes abaixo** (✗ ≥ 3/5); mortos +4 pp (4/5 acima).
O vale é ASSIMÉTRICO: .05 é pior com certeza (5/5), .01 é marginal (menos
gordura, res~ 35 vs 46, um pouco mais de mortes). Escolha .02 fica, sem
alarde: "entre .01 e .02 tanto faz no fitness; .05 custa".

**E13ssono rodou (sono come 5, 5 sementes):** 6.75 / mortos 0.27 vs 8.76 /
0.18 → **−2.01 (5/5), +9 pp (5/5)** ✓ (36). Dormir queimando caloria é
nocivo com certeza: o ser dorme 4×/vida, paga 22 de fuel, pane 9.6 vezes.
Predição 36 fechada: .05 pior (5/5), .01 marginal (2/5), sono come pior (5/5).

**E13t (TETO da alavanca "encher antes da noite") — 2026-09-02 14:25, ANTES de rodar**
Regra 1: antes de gastar evolução em hora-condicionada (ReativoHora falhou 3×),
medir o teto à mão. `ReativoRegra`: o campeão do recomendado (5 sementes,
JSON 5sem_f) com uma regra injetada — entre 20h e 22h, se fuel < 70, o
serviço posto ganha +50 no score. Mesmo genoma, mesma cidade, mesma semente.
37. Se a alavanca existe: mortos 0.18 → ≤ 0.10 e panes −40% (7.6 → ≤ 4.6),
    fit ≥ 8.76 − 0.5 (o desvio às 21h custa pouco). Aí o problema é
    EVOLVABILIDADE (G=60 não acha os 12 pesos da hora) e vale um E14 com
    hora no genoma de forma mais barata (1 peso: "posto × noite-chegando").
    Se mortos ≥ 0.15 mesmo com a regra: encher às 21h não atravessa a noite
    + manhã com tanque de 100 — o piso é FÍSICO (tanque pequeno vs noite
    longa) e a alavanca seria capacidade do tanque, não cérebro.

**E13t rodou (campeões 5 sementes + regra à mão, mesma cidade/semente):**
só o bônus no serviço: nada (0.181 → 0.178 — a regra não roteia). Com rota
puxada pro posto na janela: **20–22h fuel<70 → mortos 0.134 (−4.7 pp, 5/5),
panes 7.6 → 5.5, fit igual (8.75)**; 18–22h fuel<90 → 0.135, panes 3.1, fit
−0.6; "sempre encher" (24h fuel<40) → 0.319, fit 4.65 (vive no posto, e morre
mais). 37: ✗ no limiar (≤ 0.10), ✓ panes −28/−60%, ✓ fit. Veredito: a alavanca
existe e vale ~5 pp — o ReativoHora não a achou (evolvabilidade); os ~13%
restantes são FÍSICOS (tanque 100 cheio às 21h não atravessa noite + manhã;
fuel22 74 e ainda 3 panes/vida). Próxima peça: capacidade do tanque (a loja
vende +35 por 26 dinh — o ser compra?).

**E13t (upgrade) rodou:** o campeão JÁ compra o tanque grande — 3.6 upgrades
por vida, capacidade média 130 (135 no 1º upgrade). Regra "compra tanque"
não acrescenta (cap igual, fit −2 por viagens à loja). O piso de ~13% é
físico COM tanque de 135. Linha fechada: teto da alavanca de hora = 5 pp.

**E14a (evolvabilidade: 2 genes pra hora em vez de 12) — 2026-09-02 14:45, ANTES de rodar**
`ReativoNoite`: mesmo NP do Reativo; usa 2 pesos mortos: ss_posto += W[NF+6]
· g e movimento += −W[NF+7] · d_posto(vizinho) · g, com g = [20h ≤ h < 22h] ·
(1 − fuel/cap). A regra à mão (k=8, +50) deu −4.7 pp; a evolução tem que
achar só 2 números.
38. G=60, 5 sementes, mundo recomendado: mortos ≤ 0.15 com ≥ 4/5 sementes
    abaixo do Reativo (0.18) e fit ≥ 8.5; W[NF+7] > 0 na maioria (aprendeu a
    puxar a rota). Se mortos ≈ 0.18 e os 2 pesos ≈ 0: nem 2 genes de timing
    evoluem em G=60 — a seleção por morte é fraca demais (18% morrem e o
    resto entrega igual) e a alavanca só aparece com pressão maior (vida
    mais longa ou morte mais cara). Se piorar: o gene atrapalha de dia.

**E14a rodou (ReativoNoite, 5 sementes):** 7.25 / mortos 0.23 [.25 .23 .25
.29 .13] vs Reativo 8.76 / 0.18 → **−1.5 e +5 pp** (38 ✗, pior). Genes: posto
(0.96, −1.96, −1.20, 0.96, −1.81), rota (0.40, 0.43, −0.24, 0.32, 0.65) — 3/5
puxam CONTRA o posto ao anoitecer. Não é evolvabilidade: é AUSÊNCIA DE
GRADIENTE. No teto à mão (E13t) a regra tirou 5 pp de mortos com fitness
idêntico (8.75 = 8.75): quem morre no dia 4 entrega quase o mesmo que quem
vive 5. **A morte não custa fitness → não é selecionada.** É o mecanismo do
piso do dia inteiro (6 alavancas nulas): o objetivo não contém a vida.

**E14b (a vida no fitness) — 2026-09-02 15:00, ANTES de rodar**
`cfg.pena_morte` (0 = identidade): fit_evolução = ent − 0.3·avar − pena·[morreu].
Pena 5 ≈ 40% do fitness médio. Reativo e ReativoNoite, 5 sementes, mundo
recomendado. Reporto o fitness SEM a pena (comparável) e os mortos.
39. Com pena 5: Reativo mortos 0.18 → ≤ 0.15 (a evolução acha o que puder
    com os pesos que tem); ReativoNoite → ≤ 0.13 com gene do posto > 0 em
    ≥ 4/5 (o gradiente agora aponta pro posto às 21h); fit sem pena ≥ 8.3
    (custa pouco). Se mortos não caem nem com pena: as mortes são AZAR
    irredutível pra política de 1 salto e o teto de 5 pp da regra à mão só
    existe por injeção. Se caem só no Reativo: o gene certo não é hora.

**E14b Reativo rodou (pena 5, 5 sementes):** fit sem pena 7.18, mortos 0.22
[.25 .15 .29 .30 .10] — ✗ (previa ≤ 0.15): a pena não baixa a mortalidade do
Reativo e custa −1.6. Sem alavanca de timing no genoma, o gradiente da pena
não tem onde agir (ou se afoga: ver E14c).

**E14b ReativoNoite rodou (pena 5, 5 sementes):** fit sem pena 7.51, **mortos
0.16** [.15 .20 .19 .12 .16] (vs 0.23 sem pena, vs Reativo 0.18); genes posto
(1.73, 1.13, 4.03, 1.58, 4.40) — **5/5 positivos** (sem pena: 3/5 negativos);
rota positiva 4/5. 39: ✓ sinal dos genes (o mais forte: categórico), ✗ limiar
0.13 (0.16), ✗ fit 8.3 (7.51). A vida no objetivo faz a evolução apontar o
gene pro lado certo; o tamanho (−7 pp vs si mesmo, −2 vs Reativo) fica
dentro do ruído de ±8 pp. Efeito da pena no Reativo puro: nada (0.22) — sem
alavanca no genoma, pena não ajuda.

**E14c (ruído de avaliação: R=16 vidas por genoma) — 2026-09-02 15:25, ANTES de rodar**
Cada genoma é avaliado em NC×R = 4×4 = 16 vidas; mortalidade 18% em 16 vidas
tem σ ≈ 10 pp → a pena (5 × Δmortos) vira sinal de ±0.5 num fitness com
ruído ±1.5. R=16 → 64 vidas por genoma, σ ≈ 5 pp.
40. ReativoNoite pena 5 R=16: mortos ≤ 0.14 (chega perto do teto 0.134 da
    regra à mão) com fit sem pena ≥ 7.5; genes posto > 0 em 5/5 e maiores.
    Reativo pena 5 R=16 (controle): mortos ~0.18–0.22 (nada a achar). Se o
    ReativoNoite ficar em ~0.16 com R=16: o ruído não era o limite; o teto
    evoluível está em ~0.16 e o resto do caminho até 0.134 exige a regra
    exata (k=8), que 2 genes lineares só aproximam.

**E14c ReativoNoite rodou (pena 5, R=16, 5 sementes):** fit sem pena **9.11**
[9.5 8.8 9.2 9.1 8.9], **mortos 0.11** [.12 .08 .12 .12 .14] — 40 ✓ (≤ 0.14,
fit ≥ 7.5), abaixo até do teto da regra à mão (0.134). MAS genes posto
(−0.86, 0.35, −0.42, −1.67, 0.51), rota ≈ 0: **não foi o gene de timing** —
foi o RUÍDO DE AVALIAÇÃO. Com 64 vidas por genoma (era 16) a seleção enxerga
a mortalidade e a população acha sobrevivência pelos pesos que já tinha
(panes 7.6 → 6.4, vida_fim 62 → 75). Mecanismo: seleção por evento raro
precisa de MUITAS vidas por genoma — σ(mortos em 16 vidas) ≈ 10 pp afogava
o sinal. Controle em curso: Reativo puro, pena 5, R=16.

**E14d (célula que falta do 2×2: R=16 SEM pena) — ANTES de rodar**
41. Reativo, sem pena, R=16: mortos ~0.16–0.18 e fit ≥ 8.8 — R sozinho não
    baixa a morte porque ela não está no objetivo (E13t: fit idêntico com −5
    pp). Se mortos ≤ 0.12 sem pena: o objetivo já valorizava a vida o
    suficiente e o ruído era a história inteira — aí a "lei" é só R.

**E14c Reativo (controle) rodou (pena 5, R=16):** fit 8.17, mortos **0.17**
[.17 .18 .19 .19 .13]. Reativo puro com pena e R=16 NÃO chega a 0.11; o
ReativoNoite chegou (4/5 sementes abaixo). Mas os genes de timing do campeão
R16 são ~0 (escala: gene O(1)·g contra pesos de serviço O(20) → inerte?).
Teste: zerar os 2 genes do campeão e reavaliar — se mortos ficam 0.11, o
ganho veio da TRAJETÓRIA (paisagem diferente), não do gene, e o "0.11" é
sugestivo sem mecanismo identificado (não vender).

**Ablação do campeão R16 (ReativoNoite pena 5):** genes de timing = 0 →
mortos 0.126 (+1.2 pp), fit 8.98; genes ×10 → 0.137, fit 8.20. **Os genes de
timing são inertes** (~1 pp). O 0.11 está nos OUTROS pesos: a paisagem do
ReativoNoite + pena + R=16 levou a população a uma política sobrevivente que o
Reativo puro (mesmo pena, mesmo R) não achou em 4/5 sementes. Mecanismo =
trajetória evolutiva, não alavanca de hora. Veredito honesto: R=16 + pena
torna a morte VISÍVEL à seleção (Reativo 0.22 → 0.17; Noite 0.16 → 0.11), e
o ponto de chegada depende da paisagem. Não vender 0.11 como "achou o
timing".

**E14e (números com a avaliação certa: R=16 + pena em cidades 2000+) — ANTES de rodar**
42. Reativo e ReativoNoite, pena 5, R=16, 5 sementes, cidades 2000+: mortos
    ≤ 0.24 (vs 0.30 com R=4 sem pena) em ambos; ReativoNoite ≤ Reativo em
    ≥ 3/5 (se a trajetória repetir); fit sem pena ≥ 5.0. Média honesta (6
    cidades) do Reativo pena+R16: mortos ≈ 0.20; do ReativoNoite ≈ 0.17.

**E14d rodou (Reativo, R=16, sem pena):** fit **9.12** [9.5 8.6 9.8 10.0 7.6]
(melhor fitness do Reativo até aqui: +0.36 sobre R=4), **mortos 0.18** [.16
.17 .16 .14 .30] — 41 ✓. R sozinho compra fitness, não vida. 2×2 do Reativo
completo: (R4,p0) 0.18 · (R4,p5) 0.22 · (R16,p0) 0.18 · (R16,p5) 0.17 — no
Reativo nada move a morte mais que 1 pp. O 0.11 é do ReativoNoite com pena e
R=16 (trajetória; 4/5 sementes). E14e testa em 2000+.

**E14e Reativo rodou (pena 5, R=16, cidades 2000+):** fit 5.29, mortos 0.27
[.25 .20 .29 .32 .27] vs 0.30 (R=4, sem pena) — −3 pp, ruído; 42 ✗ pro
Reativo (≤ 0.24). Consistente com o 2×2: no Reativo a morte não cede.

**E14e ReativoNoite rodou (pena 5, R=16, cidades 2000+):** fit 5.77, mortos
**0.24** [.26 .16 .23 .27 .28] vs Reativo 0.27 → −3 pp, 3/5 sementes abaixo.
42 ✓ no limite (≤ 0.24; ≥ 3/5; fit ≥ 5). **Números honestos com a avaliação
certa (6 cidades × 5 sementes, pena 5 + R=16):** Reativo 6.73 / 0.22;
**ReativoNoite 7.44 / 0.175** — contra o recomendado padrão (R=4, sem pena)
7.08 / 0.24. Direção replicada em 2 conjuntos de cidades (−6 pp, −3 pp);
mecanismo = trajetória (genes inertes). Sugestivo, não fechado.

**E14f (10 dias com a avaliação certa) — 2026-09-02 15:20, ANTES de rodar**
ReativoNoite, pena 5, R=16, G=100, T_evo=T_aval=2400, 5 sementes, 1000+.
Referência: recomendado R=4 sem pena em 10 dias = 18.70 / mortos 0.29 (n=5).
43. mortos ≤ 0.25 e fit/dia ≥ 1.75 (17.5 em 10 dias). Se mortos ≥ 0.29:
    em vida longa a vantagem some (o risco constante de 4%/dia domina e a
    pena fixa por morte não pesa mais que 10 dias de entregas).

**E14f rodou (ReativoNoite, pena 5, R=16, G=100, vida de 10 dias, 5 sementes, 1782 s):**
fit **19.64** [20.3 18.4 21.7 20.3 17.5] = 1.96/dia (vs 18.70 do R=4 sem pena),
**mortos 0.24** [.26 .21 .18 .27 .29] vs 0.29 → −5 pp, 3/5 sementes. 43 ✓
(≤ 0.25; ≥ 1.75/dia). Em vida longa a direção persiste; tamanho sugestivo.

**E14g (controle de paisagem: é a hora, é a alavanca, ou é diversidade?) — ANTES de rodar**
Duas paisagens com 2 genes nos pesos mortos, pena 5, R=16, 5 sementes, 1000+:
(i) `ReativoNoite24`: os mesmos 2 genes, mas g = (1 − fuel/cap) em TODAS as
horas (sem informação de hora); (ii) `ReativoRuido`: os 2 genes multiplicam
um ruído uniforme por passo (alavanca sem informação nenhuma).
Referências (mesmo protocolo): Reativo 8.17 / 0.17; ReativoNoite 9.11 / 0.11.
44. Se é DIVERSIDADE de busca (qualquer gene extra abre caminho): ambas
    ≤ 0.14. Se é a ALAVANCA "puxa pro posto quando o tanque baixa" (sem
    hora): só (i) ≤ 0.14, (ii) ~0.17. Se é a HORA (contradizendo a ablação):
    nenhuma; e o 0.11 pede outra explicação. Aposta: (i) chega, (ii) não —
    a ablação zerou os genes DEPOIS de evoluir; durante a evolução a
    alavanca "tanque baixo → posto" (a qualquer hora) pode ter guiado a
    população e depois virado redundante com os pesos de serviço.

**E14g ReativoNoite24 rodou (2 genes sem hora, pena 5, R=16, 5 sementes):** fit
8.58, **mortos 0.12** [.07 .10 .16 .12 .14], panes 5.2 (Reativo mesmo protocolo:
0.17, panes 7.7). Genes posto (3.60, 3.76, 3.75, 3.75, 2.82) e rota (0.47,
0.13, 0.19, 0.49, 0.31) — **convergência 5/5** (ao contrário do ReativoNoite,
cujos genes ficaram ~0). 44 cláusula (i) ✓. A alavanca que faltava não é a
hora: é **tanque baixo × distância ao posto no MOVIMENTO** — um termo
bilinear (fuel × d_posto) que a política linear não expressa (as features
entram somando). "Vai pro posto quando o tanque está baixo, de onde estiver"
= roteamento condicional, a memória-de-rota mínima que N2/N10 pediam.

**Ablação do campeão Noite24:** genes zerados → mortos **0.351**, fit 4.90,
panes 12.2; só posto = 0 → 0.194; só rota = 0 → 0.253. Causal e co-adaptado
(a política evoluída DEPENDE da alavanca; ressalva da co-adaptação: ablação =
contribuição + desarranjo). O gene de MOVIMENTO (rota, fuel × d_posto) é o
que mais pesa. Três evidências: evoluções independentes (0.12 vs 0.17),
convergência 5/5 dos genes, ablação. É o mecanismo mais limpo do dia.

**E14h (números finais do Noite24 com a avaliação certa) — ANTES de rodar**
45. ReativoNoite24, pena 5, R=16, 5 sementes: cidades 2000+ → mortos ≤ 0.22
    (Reativo 0.27, Noite 0.24), fit ≥ 5.5; média 6 cidades ≤ 0.17. Vida de
    10 dias (G=100) → mortos ≤ 0.22 (Noite 0.24, padrão 0.29), fit ≥ 19. Se
    2000+ ficar ≥ 0.26: a alavanca só funciona onde o posto é perto (cidades
    fáceis) — e a média honesta decide.

**E14g ReativoRuido rodou (2 genes × ruído por passo, pena 5, R=16):** fit
7.63, mortos 0.19 [.16 .22 .26 .13 .20] — igual ao Reativo (0.17). **44 fechada:
é a ALAVANCA "tanque baixo × distância ao posto" (Noite24 0.12), não hora
(Noite: genes inertes), não diversidade (Ruído 0.19).** Aposta registrada
antes ("(i) chega, (ii) não") ✓.

**E14h Noite24 em 2000+ rodou (pena 5, R=16, 5 sementes):** fit 5.30, mortos
**0.25** [.16 .15 .31 .34 .29] — 45 ✗ (≤ 0.22; fit ≥ 5.5). Panes 7.3 (Reativo
2000+: 9.6, −24%) mas mortos só −2 pp vs Reativo (0.27), bimodal por semente.
**Média honesta 6 cidades: Noite24 6.94 / 0.185** (padrão 7.08 / 0.24; Noite
7.44 / 0.175; Reativo pena+R16 6.73 / 0.22). Onde o posto é longe a alavanca
"puxa pro posto" leva o ser a atravessar a cidade com o tanque baixo — ajuda
menos. Cláusula prevista: "só funciona onde o posto é perto" — meio ✓.

**E14i (a alavanca precisa da pena? Noite24 SEM pena, R=16) — 2026-09-02 16:50, ANTES de rodar**
Referências (R=16, 1000+, 5 sementes): Reativo sem pena 9.12 / 0.18; Noite24
com pena 8.58 / 0.12.
46. Sem pena, os genes ainda convergem (posto ≈ 3–4 em ≥ 4/5) porque panes
    custam avarias (0.3 cada) e tempo, que o fitness vê mesmo sem a morte:
    mortos ≤ 0.14 e fit ≥ 9.0 (melhor dos dois mundos). Se mortos ~0.18 e
    genes dispersos: a alavanca só é selecionada quando a MORTE conta —
    então pena + R=16 são ambos necessários (regra 14 completa).

**E14h Noite24 em 10 dias rodou (pena 5, R=16, G=100, 1786 s):** fit **20.43**
[18.2 19.8 24.7 18.9 20.6] = 2.04/dia (melhor de 10 dias; padrão 18.70, Noite
19.64), **mortos 0.21** [.33 .28 .09 .19 .16] (padrão 0.29, Noite 0.24) — 45
✓ nesta cláusula (≤ 0.22, fit ≥ 19). Dispersão grande entre sementes
(0.09–0.33): a alavanca ajuda muito ou pouco conforme a cidade/sorte.

**E14i rodou (Noite24 SEM pena, R=16, 5 sementes):** fit **8.95** [8.6 8.0 9.7
8.3 10.1], **mortos 0.14** [.19 .18 .16 .11 .07]; genes posto (1.48, 2.42,
4.74, −0.56, 2.50) → 4/5 positivos, rota 5/5 positivos. 46 ✓ (≤ 0.14; genes
≥ 4/5; fit 8.95 vs ≥ 9.0 por 0.05). **A alavanca não precisa da pena — precisa
das 64 vidas por genoma.** Panes custam avarias e tempo, que o fitness já vê;
o que faltava era enxergar (R). Pena acrescenta −2 pp (0.14 → 0.12) e custa
−0.4 de fitness: opcional. Recomendação 2 revisada: R=16 obrigatório, pena
a gosto.

**E14j (média honesta da melhor config: Noite24 sem pena R=16 em 2000+) — ANTES de rodar**
47. Cidades 2000+: mortos ≤ 0.26, fit ≥ 5.3; média 6 cidades ≈ 7.1 / 0.20
    (contra padrão 7.08 / 0.24): mesmo fitness, −4 pp de mortos, sem pena.

**E14j rodou (Noite24 sem pena, R=16, cidades 2000+):** fit 5.12, mortos
**0.30** [.34 .34 .35 .28 .20] = padrão (0.30). 47 ✗ (≤ 0.26). Sem pena, nas
cidades difíceis a alavanca não rende nada; com pena rendia 0.25. **Média
honesta 6 cidades, Noite24 sem pena: 7.04 / 0.22** (padrão 7.08 / 0.24; com
pena 6.94 / 0.185). Leitura final: R=16 + produto bastam onde o posto é perto;
onde é longe a pena por morte ainda compra 5 pp. Fim das baterias do dia
(predições 1–47).

## 2026-09-03 — E23 a E37 (detalhe e mecanismos em docs/37 §5–§9, docs/38, docs/28 §7)

Régua do dia (E28b, 15 sementes da mesma função): honesto n=5 só detecta ≥ 0.65 fit / ≥ 8.5 pp de mortos; panes ±0.4. Triagem (n=3) só descarta desastres (regra 18).

| # | predição (resumo) | veredito |
|---|---|---|
| 19 | E23 mínimos ≥ direto no honesto | mínimo-3 ✓ (empate 6.91/0.34); mínimo-5 ✗ |
| 20 | E27 pena proporcional muda dia da morte/entregas | ✗ nulo (quase ninguém morre cedo — cláusula própria) |
| 21 | E28 enxuto ≥ direto | ✗ (6.43 vs 6.90 = piso de ruído; virou a régua) |
| 22–24 | E26 transmissão | cancelado (linha aprendiz fechada) |
| 25 | E25b curiosidade tira o aprendiz do deserto | ✗ deserto 0.93; regra de recompensa errada |
| 26 | E29a log ≥ noite24; perde menos em 2000+ | ✗✗ (2.19/0.81; perde 73 % vs 45 %) |
| 27 | E29b reações: mortos ≤ 0.32 fit ≥ 6.6 | ✓ mortos (10 sem. 0.28 vs 0.36, t=−2.4/−3.3); motivo errado (não é persistência) |
| 28 | τ das espécies > 20 | ✗ (τ sede ≈ 1) |
| 29 | w NEGATIVO em ≥ 4/5 | ✗ na letra (sinal contra a convenção do código); mecanismo "pro posto" ✓ 4/5 |
| 30 | τ divergem ≥ 3× em ≥ 3/5 | 3/5, sem padrão de escala |
| 31 | E29c log-corpo ≈ direto | ✓ (4.67/0.63 vs 4.85/0.60) |
| 32 | E29d reflexo puro ≈ reações | ✓ no honesto (7.22/0.31) |
| 33 | E29d sem portão ≥ 0.45 mortos | ✓✓ (0.71, pior que direto) |
| 34 | E29e portão da fome ≤ 0.7 e mortos ≤ 0.28 | ✗ (fome não é reflexo) |
| 35 | reflexo puro honesto 0.30 ± 0.06 | ✓ (0.31) |
| 36 | E30 viés5 ≤ 0.26 | ✗ (0.53 do zero; ≈ controle semeado) |
| 37 | E32 β > 0.3 e panes ≤ 4.5 | β ✓ / resto ✗ (oscila na fronteira) — v1 foi erro de parametrização (regra 17) |
| 38 | E33 pane cara: portão desce, panes ≤ 4 / mortos | portão ✓, panes ✓, mortos ✗ (sobem; dano por pane constante ~35) |
| 39 | E34 +2 postos: reações ≤ 0.22, direto ≤ 0.50 | honesto ✓✓ (0.18 / 0.23); triagem tinha invertido |
| 40 | E35 portão de abastecer: panes ≤ 3.5, mortos ≤ 0.24 | ✗ (do zero: montagem; semeado: neutro E36, pior E37) |
| 41 | E36 semeado: controle ≥ 6.8/≤ 0.33; E35 panes ≤ 4.5; E30 ≈; E29e portão fome ≥ 0.85 | controle ✓; E35 triagem ✓ / honesto ✗; E30 ✓; E29e portão desceu mas w≈0 |
| 42 | E37: controle ≤ 0.15; abastecer panes ≤ 3.0 e mortos ≤ controle − 0.02 | controle ✓ (0.14); abastecer ✗ (0.19) → cláusula "portão único é o ótimo" ✓ |
| 43 | E37b 180 ger.: fit +0.2..0.4, mortos −1..3 pp | ✗ ganho; ✓ cláusula 'platô → 120 é o número' (9.20/0.15 vs 9.40/0.14) |
| 44 | E38 recusa por fome: θ_p ≤ 0.8 em 3/5, mortos ≤ 0.12 | ✗ (θ_p 92–99 %, = controle) → cláusula 'fome é preço aceito' ✓ |

Regras novas: 17 (gene novo nasce desligado), 18 (triagem só descarta), 19 (variante só semeada do melhor pai + controle semeado). Estado da arte: 9.40 / 0.14 / 2.8 panes (1000+, 5 postos, 120 ger.).

| 49 | E42 mundo: mínimo-3 perde ≥ 1.0 fit pro completo na cidade grande | (agente MUNDO; rodando) |
| 50 | E42 cérebro: hipocampo de distrito ≥ 5 pp mortos ou +10 % renda | (SerCamadas merged; estimativa do agente ~30 %) |
| 51 | E42 cérebro: tálamo usado em ≥ 3/5 (gate < 0.8) | (versão estrita com --init-from; ~50 %) |
| 52–55 | E43 campo: 3 termos perdem ≥ 1.0; litros ≥ 75 em L=800 / ≤ 50 em L=200; campo ≥ 5× grafo-500; joelho reaparece 3/5 | (campo.py pronto: 26 ms/passo @65k; fumaça rodando) |
| 56 | E43 fumaça: linear ≥ 0.9 mortos (preso no potencial), produto ≤ 0.6 | (parcial: linear 0.01 mortos com ZERO entregas — vive de poupança em 5 dias; produto/reflexo rodando) |
| 57 | E44: com prefeito, mortos −15 pp vs preços fixos em L=200; ≥ 2 obras de água/comida por mandato | ✗ fumaça: −4 pp (0.96 vs 1.00); obras 27 postos / 1 comida / 0 água — alavancas sensatas, obra errada; população não come (gargalo é o ser) |
| 58 | E44: prefeito pago pelo caixa sobe imposto até quebrar a cidade (mortos ≥ 0.6) | (variante; não rodada) |
| 59 | E43 10 dias: linear "vive de renda" colapsa (≥ 0.5 mortos); produto sobrevive entregando ≥ 6; reserva dos vivos > 10 | colapsa ✓ (1.00); produto sobrevive ✗ (1.00, morre de fome com dinheiro); entregas 10–11 ✓; reserva 55–64 ✓ |
| 60 | E43 fumaça 6 (loja no posto, raio 6, 10 dias): produto e reflexo ≤ 0.7 mortos; reflexo com menos panes que produto | (rodando) |
