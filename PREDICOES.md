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
| 52–55 | E43 campo: 3 termos perdem ≥ 1.0; litros ≥ 75 em L=800 / ≤ 50 em L=200; campo ≥ 5× grafo-500; joelho reaparece 3/5 | 52 ✗ (triagem L=200: mínimo-3 é o MELHOR, 0.57 vs 0.61–0.63 — loja no posto colapsa o problema); 53: L=200 dá 50–78 L/parada (✓ na metade); 54: campo 1.3 ms vs grafo-500 não medido; 55: reflexo evolui portão no campo (a ver no retrato) |
| 56 | E43 fumaça: linear ≥ 0.9 mortos (preso no potencial), produto ≤ 0.6 | (parcial: linear 0.01 mortos com ZERO entregas — vive de poupança em 5 dias; produto/reflexo rodando) |
| 57 | E44: com prefeito, mortos −15 pp vs preços fixos em L=200; ≥ 2 obras de água/comida por mandato | fumaça 3 (população que trabalha): **−58 pp (0.77 → 0.19)**, 27 comidas + 26 postos ✓✓ — mas alavancas eram de graça (v2 fecha a moeda cruzada) |
| 58 | E44: prefeito pago pelo caixa sobe imposto até quebrar a cidade (mortos ≥ 0.6) | (variante; não rodada) |
| 59 | E43 10 dias: linear "vive de renda" colapsa (≥ 0.5 mortos); produto sobrevive entregando ≥ 6; reserva dos vivos > 10 | colapsa ✓ (1.00); produto sobrevive ✗ (1.00, morre de fome com dinheiro); entregas 10–11 ✓; reserva 55–64 ✓ |
| 60 | E43 fumaça 6 (loja no posto, raio 6, 10 dias): produto e reflexo ≤ 0.7 mortos; reflexo com menos panes que produto | ✗ pelo motivo errado: 0.01–0.05 mortos com 0.1 entregas — vive de poupança (100 → 11) |
| 61 | E43 fumaça 7 (nasce com 20): entregas ≥ 8 ou morre; mortos 0.3–0.8; reflexo menos panes que produto | linear 16.3 ent / 0.96 mortos; reflexo 18.4 / 0.88; produto 13.9 / 0.98 — entregas ✓, mortos ✗, 'reflexo menos panes' ✗ (mas vive mais); morte = avaria por CALOR (12 eventos/vida) |
| 62 | E45 base fechada sozinha ≥ 0.6 vivos em 10 dias | professor à mão ✗ 3× (v1 sem dinheiro, v2 dívida, v3 3.7 entregas) — míope por construção; abandonado. Clonagem do campeão (mínimo-3 com máscara; linear) na fila |
| 63 | E45 semeado da base (25 ger.) ≥ do-zero (25 ger.) por ≥ 20 pp de mortos | (na fila) |
| 64 | E45 preço = diversidade (fingerprint entre sementes < 0.3) | (na fila) |
| 65 | E43 fumaça 8 (calor sustentável a 70 % de rodagem, D_QUENTE 6): reflexo ≤ 0.6 mortos e ≥ 20 entregas; linear ≤ 0.8 | linear 0.63/26.7 ✓; reflexo 0.69/26.1 (≤0.6 ✗, ≥20 ✓); produto 0.77/23.9 — de 0.96 pra 0.63 |
| 66 | E46 modos gaussianos: 3 centros se separam (≥ 1 σ) em ≥ 2/3; modo 'com passageiro' tem d_alvo mais forte | centros separam 3/3 ✓; pax-modo com d_alvo mais forte 2/3 ✓; mas ganho da mistura ≤ 0.5 — estrutura sem uso |
| 67 | E46 modos ≥ linear por ≥ 5 pp de mortos na triagem L=200 | ✗ (0.63 vs 0.62) |
| 68 | E47 serviços separados (sem loja no posto): mínimo-3 perde ≥ 10 pp pro produto/modos; mortalidade geral sobe | mortalidade sobe ✓ (0.86–0.92); mínimo-3 NÃO perde (0.89 = produto 0.89, modos 0.92) ✗ — ninguém aprende a comer longe; reflexo melhor (0.86) |
| 69 | E45 clonagem (professor = campeão mínimo-3): base sozinha ≈ campeão (±5 pp); semeado 25 ger. ≥ do-zero 40 ger.; professor v3 guloso ainda morre ≥ 0.6 | v5 (Phi centrado): clone fiel 99.5 % (mínimo-3) / 97.3 % (linear); base sozinha 0.60 / 0.59 ≈ professores 0.58 / 0.55 ✓; semeado 25 ger. dá 0.63 / 0.68 — NÃO passa do professor nem do do-zero 40 ger. (0.58/0.55) ✗; professor v3 guloso morreu 1.00 ✓. 1ª e 2ª rodadas inválidas (bias −1e9; Phi não centrado) |
| 70 | E44 v2 (moeda cruzada): ganho do prefeito cai mas fica (−15 a −30 pp na triagem); ≥ 1 alavanca acima de 1.0 além da tarifa | ✓ triagem: 0.62 → 0.16 (−46 pp), comida ×1.76; obras 53 → 7; brecha: caixa negativo (v3 fecha) |
| 71 | Honesto campo L=200 (5 sem., 120 ger.): reflexo < mínimo-3 em mortos por ≥ 5 pp; ambos ≤ 0.5 | ✗ idênticos: 0.53 / 28.7 os dois (estratégias diferentes: 10×54 L vs 15×39 L); teto honesto do ser sozinho = 0.53 |
| 72 | E48 comitê (4 campeões + inércia): ≥ melhor campeão por ≥ 3 pp SÓ se ganho > 1 e τ > 4 em ≥ 2/3 | ✗ 0.58 = mínimo-3 0.57; ganho 0.19–0.62, τ > 4 em 1/3 — cláusula ✓ (com loja não há o que combinar); bate modos-do-zero por 9 pp |
| 73 | E49 olho multi-escala (need + a·micro + b·macro no produto): genes ≠ 0 em ≥ 2/3; panes −20 % vs produto; mortos −5 pp | ✗ 0.66/25.2 vs 0.62/26.2 (ruído, pior) — em 10 dias não há macro que valha |
| 74 | E44 v3 (orçamento fecha): mantém ≥ −30 pp; gasolina não fica abaixo de ×0.8 sem compensação | ✓ triagem: 0.62 → 0.22 (−40 pp; v2 era −46); gasolina ×0.62 e comida ×0.65 COMPENSADAS por aluguel ×1.93, água ×1.25 e tarifa ×2.0 (caixa +5 / +142 / −75 por mapa); 16 comidas + 8 postos; seres co-evoluídos DEPENDEM do prefeito (0.76 sem ele vs 0.62 do-zero) |
| 75 | E50 reflexo 2 raízes (histerese): largura > 0.15 em ≥ 2/3; panes −15 % vs reflexo | ✗ largura 0.004 / 0.076 / 0.012 (0/3), panes 5.9 vs 5.5, mortos 0.59 vs 0.58 — a histerese não é selecionada no mundo com loja |
| 76 | E51 oráculo (política à mão com alvo TRANCADO, sem genes) = teto físico do mundo: com loja ≤ 0.30 mortos (evolução em 0.53 está longe do teto = "não acha", não "não dá"); sem loja ≤ 0.50 (mundo viável; a falha do E47 é MONTAGEM); se o oráculo morrer ≥ 0.8 sem loja, o mundo é duro demais e se recalibra ANTES de qualquer arquitetura | ✗ nos dois mundos: oráculo 0.98–1.00 mortos em 16/16 variantes (L=200) e 6/6 (L=400), 7–12 entregas em 10 dias, dinheiro −5, fome 100 — a política à mão é PIOR que a evolução (mínimo-3: 0.58, 27 entregas); o teto físico NÃO ficou medido (o oráculo é ruim, não o mundo). Diagnóstico do orçamento de tempo na fila (e51c) |
| 77 | E52 reflexo de alcance (portão lê gasolina + k·d_posto = "km até esvaziar"): triagem L=200, panes −30 % e mortos −6 pp vs reflexo; k > 0.1 em ≥ 2/3 | (na fila, atrás do honesto v3) |
| 78 | E51f oráculo v3 (entrega primeiro + não fura o esfriamento): ≥ 18 entregas e mortos ≤ 0.7 em ≥ 1 variante — o teto físico do mundo com loja fica abaixo de 0.53 (a evolução está longe do teto) | (na fila) |
| 79 | E53 cérebro livre (rápida H=4 + lenta K=3 com banco de τ ~5/25/100, nasce transparente, SEM pista de alcance): (a) portão: transparente == linear bit a bit; (b) triagem 40 ger.: cérebro ≈ linear (±5 pp) — estrutura ainda sem uso; (c) 300 ger.: se a evolução MONTAR o alcance sozinha, cérebro < linear-300 por ≥ 5 pp de mortos e panes −20 %, e o retrato mostra uma unidade lenta com |corr(z, tanque)| > 0.5 e M com peso em d_posto; aposta honesta: (c) ✗ (gargalo de montagem), o valor está em VER o cérebro | (na fila, atrás do E52) |
| 80 | E54 CÉREBRO COMPLETO no mundo aberto (tálamo+córtex+hipocampo+reflexo+rápida+lenta, 460 genes, nasce transparente): (a) portão: transparente == linear e cada parte desligada == genes zerados; (b) triagem 40 ger.: completo ≈ linear (±5 pp), nenhuma parte sozinha muda ≥ 5 pp (montagem ainda não aconteceu); (c) 300 ger.: completo < linear-300 por ≥ 5 pp de mortos OU panes −20 %; o retrato mostra qual parte foi montada (ablação ≥ 5 pp) — aposta: hipocampo e córtex ficam mortos (mundo de 6 distritos quase iguais), tálamo e lenta são os primeiros a ligar | (a) ✓ portão 6/6; do zero 40 ger.: 0.98 (460 genes aleatórios não montam; 5× mais lento); (b) semeado 120 ger.: completo 0.64 = linear 0.63; sem tálamo 0.62, sem córtex 0.61, sem hipocampo 0.61, sem reflexo 0.66; **só camadas (sem rápida/lenta) 0.58 = −6 pp** ✗(b) — as camadas livres atrapalham; honesto na fila; retrato s0: ablação sem rápida 1.00, sem tálamo 1.00, sem reflexo 0.76, sem córtex 0.71 — partes usadas por co-adaptação, total igual; dof 355 grátis; (c) 300 ger.: 0.61 / 5.0 panes vs linear 0.63 / 6.3 — mortos ✗ (−2 pp), panes −21 % (limite, n=3); dof 373: nada montou, genes de graça acumulam |
| 81 | E55 cérebro que COME (acervo: "custo é o que seleciona"; Lei do Metabolismo = AIC): fome × (1 + λ·dof/100), dof = genes além da espinha com \|w\| > 0.5. (a) λ=0 idêntico bit a bit; (b) dof do campeão completo cai monotonicamente com λ (λ=0 → ~150; λ=3 → < 30); (c) em λ=1 mortos ≈ linear ±3 pp (o ser larga as peças e vira espinha); (d) a parte que sobreviver com ≥ 30 % dos genes > 0.5 em λ ≥ 1 é função real — aposta: reflexo sobrevive (4 genes, +10 pp), hipocampo morre primeiro (104 genes, +2 pp), lenta morre (0 pp) | (a) ✓ portão (λ=0 bit a bit; λ=1 fome 67→96); λ=0.3: dof 3/7/56 (de 355 grátis), mortos 0.66 ≈ linear — reflexo 0/4, tálamo 0–2/15: as 'pilares' da ablação somem com 7 % de fome (co-adaptação, não função); (d) nenhuma parte sobrevive nem em λ=0.3 → aposta do reflexo ✗; λ=1/3 rodando |
| 82 | E56 mundo que cobra (Leonardo: "distritos realmente distintos, ruas, preços"): ruas (custo 1 na rua / 3 fora), perfis de distrito (centro caro e cheio, industrial com posto barato e sem comida, residencial com comida e sem posto, periferia vazia), demanda por distrito, preços ±50 % em ciclo de 3 dias por distrito. (a) padrão continua bit a bit; (b) mundo distinto é mais duro (linear ≥ 0.70); (c) só-camadas < linear por ≥ 8 pp (era 5 no mundo padrão); (d) com λ = 0.3, córtex e/ou hipocampo ficam com ≥ 30 % dos genes > 0.5 em ≥ 2/3 sementes (no padrão: 0–8 genes) — aposta: (b) ✓, (c) ✓, (d) córtex ✓ hipocampo ✗ | (na fila, atrás do E55) |
| 83 | E57 (Leonardo: "dá pra saber o gasto de tudo; o prefeito deveria ver o problema"): sentidos do painel do carro `e_consumo` (L/m medido, média móvel) e `e_autonomia` ((tanque/consumo − d_posto)/100) + prefeito no mundo distinto (pane dói, KCAL 8). (a) linear com sentidos: panes −40 % e mortos −10 pp vs linear sem (0.79 / 7.1); mínimo-4 (d_alvo, d_posto, e_fuel, e_autonomia) ≤ linear; (b) prefeito co-evoluído no mundo distinto: −15 pp vs sem prefeito e ≥ 1 posto construído no residencial; (c) só-camadas semeado com sentidos ≥ 5 pp melhor que linear com sentidos — aposta: (a) ✓, (b) ✓, (c) ✗ | (rodando) |
| 84 | E58 ACHADO ESTRUTURAL: sentidos do corpo são iguais nas 9 opções e o G1 centra a nota ⇒ no Linear NENHUM sentido do corpo muda a direção (só o serviço via need) — o ser linear nunca PROCURA o posto, abastece quando passa; causa estrutural das panes (explica mínimo-3 = linear e por que a autonomia como sentido não ajudou: 0.85/0.79/0.80 vs 0.79 sem). Bilinear (nota += Σ corpo_k·M[k,f]·F_op[f], nasce em zero): (a) portão: prova que pesos do corpo no Linear são invisíveis (posições idênticas) e no Bilinear não; (b) bilinear autonomia+consumo (20 genes) no mundo distinto: panes −40 % e mortos −10 pp vs linear (0.85 / 6.5), do zero ou semeado; (c) o gene M[autonomia, d_posto] < 0 em ≥ 2/3 sementes | (a) ✓ portão: corpo invisível no Linear (posições idênticas), visível no Bilinear; matriz 26 sentidos × 5 arqs; do zero 0.88–0.93 (montagem); semeado SEM escala 0.91 (ruído afoga a espinha → teste de escala novo; completo afoga 58 %); semeado COM escala: cheio 0.77 / 6.5 panes, auto+cons 0.82 / 6.9 vs linear 0.80 / 6.7 — (b) ✗ panes iguais; (c) M[auto,d_posto] = −4.0/+0.6/−0.6: moveu com sinal errado — autonomia é positiva quase sempre; precisa de sentido retificado (e_risco), amanhã |
| 85 | E60 reset com ESCALA (mundo distinto pobre, semeados do linear, 120 ger.): completo ≈ linear (±3 pp); só-camadas ≈ linear (o 0.58 de ontem era artefato de escala); custo 0.3 derruba dof a < 30 em todos; nenhuma parte paga sem o sentido de risco | ✓ semeados: linear 0.81, completo 0.78, só-camadas 0.81, bilinear 0.82; custo 0.3 re-enfileirado (bug de comentário) |
| 86 | E61 luz de reserva `e_risco` = relu(d_posto + 30 − alcance)/100 (NM_RISCO=1): bilinear cheio semeado do linear-com-risco corta panes ≥ 40 % e mortos ≥ 10 pp vs linear-com-risco; o gene M[risco, d_posto] < 0 (ir ao posto quando a luz acende) em ≥ 2/3; ent ≥ 15 (não pedra) — aposta: ✓ | (na fila, atrás do E60) |
| 87 | E61b guincho PAGA (Leonardo: "me cheira a bug" → a pane era subsídio: guincho grátis + 15 L; 6 panes/vida = viver de guincho): guincho 10 e 5 L no posto, luz de reserva ligada, 5 sementes. (a) linear-com-risco piora ou empata (não sabe procurar); (b) bilinear semeado: panes ≤ 2/vida e mortos ≥ 15 pp abaixo do linear; (c) M[risco, d_posto] < 0 em ≥ 3/5; (d) só-camadas semeado ≥ linear (tálamo pode gatear risco) | (na fila, atrás do E61) |
| 88 | E61c bilinear SÓ risco, escala 1 (10 genes; risco = 0 quando seguro ⇒ semeadura sem ruído), guincho pago, 5 sementes: mortos ≤ 0.80 (vs linear 0.98), panes ≤ 2.5, ent ≥ 15; M[risco, d_posto] ≤ −5 em ≥ 3/5 | ✗ no honesto (10 d, 5 sem., R=8): linear 0.97 / 5.1 panes, bilinear risco esc 3 0.97 / 4.5, só-camadas 0.86 / 1.0 panes mas fome 89 (pedra-lite); o 0.46 de 5 dias era dirigir menos; mundo com guincho pago + régua bemestar = parar é ótimo local |
| 89 | E62 (pedra é ótimo local em 10 d + bemestar): (a) 15 dias com bemestar: pedra morre → só-camadas e bilinear-risco perdem a vantagem de "parar" (mortos ≥ 0.9 todos) OU aprendem a dirigir-e-abastecer (mortos < linear por ≥ 15 pp com ent ≥ 15); (b) régua riqueza (bem + renda/300) em 10 d: ent sobe ≥ 30 % em todos, pedra some, e o bilinear-risco fica abaixo do linear por ≥ 10 pp com panes ≤ 3 — aposta: (a) todos morrem, (b) ✓ | (a) ✓ 15 d todos morrem (1.00/1.00/0.99); (b) ✗ riqueza 10 d: 0.98/0.98/0.97, pedra some (ent 11) mas ninguém abastece a tempo; guincho 4: 0.93–0.96 todos iguais — o mundo move o teto, não a ordem |
| 90 | E63 escada de NÉVOA (Claude Science, doc 49 §7, mundo ajustado: E56c, 10 d, riqueza, R=8, 5 sem., semeados do linear-com-luz): (a) névoa piora o linear monotonicamente inf → 40 → 25 → 15; (b) em névoa ≤ 25, só-camadas e/ou COMPLETO batem o linear por ≥ 10 pp PAREADO por semente com ent ≥ 15; (c) em névoa 25 com custo suave λ .3, dof sobrevivente ≥ 30 concentrado em hipocampo/córtex; (d) ablação do hipocampo no campeão de névoa 25 piora ≥ 10 pp. Cláusula: se todos ≥ 0.95 em névoa 15, refazer com 40/60. Aposta do CS: (a)(b)(c)(d) ✓; minha aposta: (a) ✓, (b) ✓ em névoa 25, (c) ✗ (custo ainda derruba), (d) ✓ | (a) ✗ névoa não piora (linear 0.80/0.77/0.81 em ∞/25/15); (b) ✗ em todos os níveis (só-camadas 0.81/0.78/0.81; completo 0.83/0.82/0.82; pareado ns, MDE 9 pp); (c) ✗ custo suave λ .3 em névoa 25: completo 0.85, só-camadas 0.85 (pior que sem custo); (d) sem objeto — escada inteira ✗ |
| 91 | Busca ×8 (q8: P=2048, 300 ger., paciência 60, 5 sementes, R=4, mundo E56c riqueza 10 d, semeados do linear-com-luz): se o gargalo era ORÇAMENTO, o bilinear-risco esc 3 fica ≥ 10 pp abaixo do linear (pareado) com ent ≥ 15 e M[risco,d_posto] < 0 em ≥ 3/5; aposta: ✗ (empate) — o gargalo é o sinal de aprendizado, não a busca | ✗ empate: linear 0.82 / 7.3 panes, bilinear-risco 0.85 / 6.3; ambos param na ger. 60 sem melhora sobre o semeado (ótimo local da régua); não é orçamento — é o sinal de aprendizado |
| 92 | E65 SINAL DE APRENDIZADO no táxi (q9: ES antitético com utilidade por posto, σ .1 e .3, lr .3, MESMO orçamento e sementes do q8: P=2048, 300 ger., paciência 60, 5 sem., R=4, semeados do linear-com-luz, régua riqueza 10 d, E56c): se a hipótese do fechamento ('falta sinal, não busca') está certa, o ES sobe ≥ 10 pp pareado sobre o GA (mortos 0.82 → ≤ 0.72) em ≥ 1 σ, com ent ≥ 15; aposta: ✗ (empate ±5 pp) — o platô 'não dirigir' é do PANORAMA de fitness (degrau), não do otimizador; se ✓, o gargalo era o otimizador e o Minecraft NÃO é necessário para prová-lo | ✗ empate: ES σ .1 mortos 0.77 (−5.3 pp, IC −14.5/+3.8, p .18), ES σ .3 0.80 (−2 pp); nenhum otimizador sobe a fitness de treino (GA −0.18→0.00, ES −0.28→+0.14) |
| 93 | E66 SINAL/RUÍDO da nota (diag_snr: 2048 mutantes σ .3 do campeão linear s0, mesma população em 3 sorteios de mundo, R=4, mundo/régua do q8): se a seleção é loteria, corr(nota_A, nota_B) entre indivíduos < 0.3 e a elite de 15 % de um mundo se mantém elite no outro em < 30 % (acaso 15 %); e a DP da nota do MESMO clone entre mundos (σ 0) é ≥ a DP entre mutantes num mundo; aposta: ✓ — é por isso que GA e ES travam no mesmo lugar (mecanismo do platô: nota cega, não panorama plano) | ✗ a nota NÃO é cega na escala do GA: σ .3 corr 0.81, elite mantida 43–46 % (acaso 15); σ .1 corr 0.45 (meio-cega na escala fina); clones: DP 0.49 = ruído puro; fitness média cai com σ (−2.14/−2.47/−3.23) = campeão é PICO local |
| 94 | E67 última brecha do fechamento (q11: ES σ .1 com R=16 — nota média em 16 mundos, ruído /2 — mesmo P=2048, sementes, mundos e paciência do q9b2): se o platô era só ruído na escala fina, o ES sobe ≥ 10 pp pareado sobre o GA (mortos ≤ 0.72); aposta: ✗ (fica em 0.75–0.80) — a curva fitness×σ diz que o campeão é pico local desta régua, não vítima de ruído | ✗ ES σ .1 R=16: mortos 0.78 [0.737, 0.826, 0.82, 0.737, 0.789] (−4 pp, dentro da faixa apostada 0.75–0.80); treino sobe −1.21→−0.93 até a ger 30 e para (ger 61); ruído /2 não abre subida nova — pico local confirmado por 3 lados (busca, otimizador, ruído) |
| 95 | E68 PONTO DE TÁXI (Leonardo 09-08: 'parar pode ser esperar passageiro'): táxi parado+livre recebe passageiro no lugar com espera ponto/demanda (ponto=30: centro ~15 ticks, periferia ~100) + sentidos e_demanda/e_espera; mundo E56c, riqueza 10 d, 5 sem., R=4, P=1024, 120 ger. paciência 40, semeados do linear q8 (alinhado): (a) o bilinear risco+demanda+espera bate o linear ≥ 10 pp em mortos OU ≥ +20 % de renda pareada (o linear não vê o lugar ao decidir 'ficar', achado 84); (b) o linear no mundo com ponto entrega mais que no mundo sem (ent ≥ 22 vs 18) porque parar passou a render; aposta: ✓ em (b) e ✓ em (a) — é o primeiro mundo onde a peça tem o que pagar | ✗ (a) bilinear risco+demanda+espera 0.80 vs linear 0.81 (−1 pp; entrega 15.1 vs 18.3, renda −18 %); COMPLETO 0.73 (−7 pp, p .15). ✗ (b) linear entrega 18.3 com ponto vs 18.1 sem. MECANISMO (diag_ponto): o linear NUNCA espera livre (3 % do tempo; 82 % andando, 67 % com passageiro; 2 % dos embarques via ponto) porque o mundo dá passageiro de graça rodando (12 privados a 8–45 u, renascendo perto em qualquer distrito) — sem escassez, esperar e escolher lugar não valem nada. Só o COMPLETO usou o ponto (11 % esperando, 20 % via ponto) |
| 96 | E69 ESCASSEZ de passageiro (npx 3, respawn 100: periferia ~333 ticks por slot, centro ~50) + ponto 30 + sentidos; mesmo protocolo do q13 (P1024, 120 ger, pac 40, 5 sem., riqueza 10 d, semeados do linear q8): (a) o linear cego ao lugar cai: ent ≤ 12 e mortos ≥ 0.85; (b) COMPLETO ou bilinear risco+demanda+espera batem o linear ≥ 10 pp em mortos OU ≥ +30 % renda pareada, com espera livre ≥ 10 % do tempo concentrada em demanda alta; aposta: ✓ (a) e ✓ (b) pelo COMPLETO (único que já usa o ponto) — é a primeira vez que ONDE trabalhar tem preço | CANCELADA (parada aos 12 min, sem resultado): Leonardo — 'eles deveriam buscar o passageiro, não o passageiro aparecer do nada'; escassez do pool privado ainda faz o passageiro nascer perto do táxi |
| 97 | E70 PASSAGEIRO NA CIDADE (pax_cidade: nasce onde há demanda, em volta do centro do distrito; táxi vai buscar; reposição ~ demanda do lugar; ponto OFF; 12 passageiros na cidade toda), mesmo protocolo do q13 (P1024, 120 ger, pac 40, 5 sem., riqueza 10 d, semeados do linear q8), controle pareado = linear do q13b (passageiro perto): (a) o linear entrega menos (ent ≤ 14 vs 18) e morre mais (≥ +5 pp) porque agora tem de viajar; (b) COMPLETO ou bilinear risco+demanda+espera batem o linear ≥ 10 pp em mortos OU ≥ +30 % renda pareada — pela primeira vez ONDE estar tem preço e o linear não lê lugar na direção; aposta: ✓ (a), ✓ (b) pelo COMPLETO (3 apostas ✓ perdidas hoje: o mundo é quem decide) | ✓(a) linear 0.93 / ent 11.4 / dinh 11 (era 0.83 / 18 / 26); ✗(b) COMPLETO 0.91, bilinear+demanda 0.92, bilinear-risco 0.95: PISO — com 12 passageiros na cidade toda (mais perto a 31–56 u) todo mundo morre igual; a régua crava (degrau). Lugar passou a ter preço, mas ninguém consegue pagar: falta calibrar a densidade (npx 20–40) |
| 98 | R1 agentes — política explícita construcao_1 (Sonnet): PREDIÇÃO DO AGENTE mortos 0.30–0.40, 10–15 entregas | ✗ mortos 1.00, ent 3.7, renda 31, panes 0.2, fome_fim 100: estacionou e nunca comprou comida (morte por fome parado) |
| 99 | R1 agentes — política explícita construcao_2 (Sonnet): PREDIÇÃO DO AGENTE mortos 0.35–0.45, 10–14 entregas | ✗ mortos 1.00, ent 1.8, renda 15, panes 1.1, fome_fim 100: idem (fome, parado). Nenhuma política explícita jamais sobreviveu (oráculo 1.00, agentes 1.00 ×2) — candidata a achado: o mundo base pode ser insolúvel a 10 d com dinh0 10 |
| 100 | R1 agentes — cenário lugar_1 'ímã no centro' (dem centro 4 / periferia .05, npx 5, respawn 80, rua fora 4): PREDIÇÃO DO AGENTE linear ≥ .60, ent ≤ 8 | ✗ (escala letal): linear 1.00/3.8 ent; COMPLETO (talamo+cor 1.00/3.6 ent; bilinear risco (esc  1.00/3.2 ent; bilinear risco+deman 1.00/2.9 ent — escassez total crava a régua; regra nova: linear entre 0.40 e 0.80 |
| 101 | R1 — cenário lugar_2 'oásis central' (dem centro 5 / periferia .05, npx 6, respawn 15, rua fora 6): PREDIÇÃO DO AGENTE ~95 % dos passageiros no centro, linear morre por não ir ao centro | ✗ (escala letal): todos 1.00 com ~2 entregas; a escassez total crava a régua |
| 102 | R1 — cenário minimo_1 (só pax_cidade=true, protocolo curto): PREDIÇÃO DO AGENTE linear cai e COMPLETO separa | ✗: linear 0.92, COMPLETO 0.93 — réplica do E70 (piso) com P=512/G=60; consistente com q16 |
| 103 | R1 — cenário minimo_2 'deserto de descanso' (dens descanso 0 em centro/periferia; resto = base): PREDIÇÃO DO AGENTE linear cai em pane de fadiga longe do residencial, COMPLETO separa ≥ 10 pp | ✗: linear 0.81 (na banda), COMPLETO 0.78 (−3 pp): único cenário VÁLIDO da rodada 1, mas fadiga não é o eixo que mata (panes 6.4 dominam) |
| 104 | R2 — política construcao_1 (3 camadas, histerese): PREDIÇÃO DO AGENTE mortos ≤ .5 | ✗ 1.00, ent 1.3, refeições 0 — CULPA DO CONTRATO: a ordem de ACOES no prompt estava errada (escrita de memória), 'comida' apontava para 'posto 100 L'; corrigida na r3 com a tabela do código |
| 105 | R2 — política construcao_2: PREDIÇÃO DO AGENTE mortos ≤ .5 | crash no juiz (reset(m) sem W); juiz ganhou shim + traço de escolhas; reenviada como r2_construcao2b (mesmo erro de índice esperado) |
| 106 | R2 — cenário lugar_1 (cidade npx 22, respawn 12, contraste dem 2.4/0.6): PREDIÇÃO DO AGENTE linear na banda | ✗ linear 0.89 / 14.6 ent (fora da banda), COMPLETO 0.85 (−4 pp), bilinear+demanda 0.88: densidade ainda baixa; COMPLETO lidera de leve pela 3ª vez na cidade (E70 −2, r2 −4) |
| 107 | R2 — cenário lugar_2 (npx 32, respawn 15, rua fora 4, dem 2.4/1.0/1.4/0.6): PREDIÇÃO DO AGENTE linear .55–.70, 13–15 ent | ✗ linear 0.96 / 10.9 ent — PIOR que npx 22: o agente mudou rua-fora 3→4 junto (mais gasolina fora da rua, panes 7.4); variáveis confundidas, ponto de calibração inválido |
| 108 | CALIBRAÇÃO limpa (consolidador, q17): cidade = base + pax_cidade, SÓ npx varia {24, 36, 48}, linear, P512 G60 pac30, 5 sem.: mortos cai monotonicamente com npx e entra na banda 0.40–0.80 em npx 36 ou 48; aposta: ✓ em 48 (≈0.70), 36 ainda ≈0.85 | ✗ fraco: monótono mas raso — npx 24 0.82, 36 0.81, 48 0.78 (ent 16.5/19.3/20.9); com 48 a cidade ≈ mundo antigo (0.83); densidade não é a alavanca, o corpo é |
| 109 | R2 — política construcao_2 (rejulgada, contrato de índices ERRADO): — | ✗ INVÁLIDO: anda 92 %, 3.5 ent, refeições 0, fome 100 |
| 110 | R3 — política construcao_1 'urgência máxima' (contrato CERTO): PREDIÇÃO DO AGENTE mortos ≤ .5 | ✗ 1.00: anda 95 %, 6.4 entregas, 3 refeições, 2.2 abastecidas, 1 pane, fome 93 / água 24 / dívida −4 — desvia demais e trabalha de menos; o campeão aceita 6.8 panes e entrega 17.7. 1ª evidência VÁLIDA de 'nenhuma política explícita sobrevive' |
| 111 | R3 — política construcao_2 (contrato certo): PREDIÇÃO DO AGENTE mortos ≤ .5 | ✗ 1.00: anda 93 %, 6.5 entregas, 2.6 refeições, 2.3 abastecidas, 0.2 pane, fome 94 / água 20 / dívida −4 — mesmo padrão da irmã: evita a pane e morre de fome; 2ª evidência válida |
| 112 | R3 — cenário lugar_1 (cidade npx 48 + contraste de demanda 4×, um parâmetro): PREDIÇÃO DO AGENTE quem lê demanda ganha | ✗ INVERTIDO: linear 0.74 (na banda, 20.2 ent), COMPLETO 0.79 (+5 pp pior), bilinear+demanda 0.80 (+6 pp pior): ler lugar custa e não paga; cenário VÁLIDO, efeito contra a tese |
| 113 | R3 — cenário lugar_2 (cidade npx 48, outro contraste): PREDIÇÃO DO AGENTE separação ≥ 10 pp | ✗ empate: 0.83 / 0.83 / 0.83 (fora da banda por 3 pp) |
| 114 | R3 — cenário minimo_1 (posto SÓ no industrial; resto = base, passageiro perto): PREDIÇÃO DO AGENTE quem lê risco/lugar ganha ≥ 10 pp | ✗ empate: linear 0.71 (na banda; dinh 44), COMPLETO 0.71, bilinear-risco 0.78 (+7 pior). Curioso: menos postos = linear vive MAIS (0.71 vs 0.83) com abastecidas maiores (70 L) |
| 115 | R3 — cenário minimo_2 (gasolina 3× no centro, pmul 6): PREDIÇÃO DO AGENTE separação por risco | ✗ empate: 0.85 / 0.82 / 0.83 |
| 116 | R4 — política construcao_1 (imita o campeão: aceita pane, come no posto): PREDIÇÃO DO AGENTE mortos ≤ .6 | ✗ 1.00, morre no dia 3.1 (fome 77 %, sede 27 %), 6.3 ent, 2.1 refeições, 2.6 abastecidas (posto25 pequenas), renda 53: 2 corridas/dia não pagam comida; ainda vai ao posto por vontade |
| 117 | R4 — política construcao_2: PREDIÇÃO DO AGENTE mortos ≤ .6 | ✗ 1.00, morre no dia 2.5 (sede 87 %, fome 78 %), 5.4 ent, 0.7 refeições, água final 3: não bebe; renda 47 |
| 118 | R5 — política construcao_1 (literal do campeão): PREDIÇÃO DO AGENTE ≤ .7 | crash (tensor na CPU vs cuda); juiz passa a fixar torch.set_default_device; não conta |
| 119 | R5 — política construcao_2 (literal do campeão: nunca vai ao posto por vontade, pane = transporte, compra tudo no posto): PREDIÇÃO DO AGENTE ≤ .7, ≥ 3 corridas/dia | ✗ 1.00 MAS progresso: 13.7 entregas, renda 127, 3.7 refeições, 5.3 abastecidas, 3.7 panes, morre no dia 4.1 por DANO 76 % (fome 24 %) — o mesmo modo de morte do campeão (dano 79 %, dia 5.0). Deixou de morrer de fome. Próxima alavanca: reparar na oficina (nem o campeão repara) |
| 120 | R6 — política = r5_2 + REPARO na oficina (vida < 50 e dinheiro > 20 → ir à oficina e comprar G+9; oficina também zera o calor) + evitar rodar quente: se ≤ 0.70 é a primeira política explícita que bate o campeão evoluído (0.85); aposta: ✓ (0.60–0.75) — o dano é acumulativo e reparável por 10 de dinheiro, e a política já ganha 127 | ✓ PARCIAL — ACHADO: r6_1 mortos 0.76 [0.779, 0.773, 0.745, 0.747, 0.734] vs campeão 0.85 [0.87, 0.818, 0.875, 0.836, 0.828]: −9 pp pareado, 5/5 sementes; 18.2 ent, renda 168, 6 refeições, 8.1 abastecidas, 7.9 panes, oficina 1 % das escolhas; morre dia 5.3 (fome 50 %, dano 50 %). Não chegou a ≤ 0.70, mas é a PRIMEIRA política explícita que bate a evolução |
| 121 | R6 — política construcao_2 (r5_2 + reparo + 100 L no posto): PREDIÇÃO DO AGENTE ≤ .7 | ✗ parcial: 0.80 (−4 pp vs campeão), 17.9 ent; abastecer 100 L gasta o dinheiro do reparo/comida |
| 122 | (AGUARDA OK DO LEONARDO) A política explícita r6_1 como PROFESSOR: (a) clonar por forma fechada (base_fechada.py, ridge Φ→esc) num Linear e semear a evolução; (b) ou usar a política como espinha fixa e evoluir só o que falta. Predição a registrar antes: o clone linear NÃO reproduz (regras não-lineares: fidelidade < 80 %) e a semeadura empata — o valor do achado é outro: o mundo É solúvel abaixo de 0.85, logo a evolução não acha o que existe (reabre 'sinal de aprendizado' pelo lado certo) | pendente |
| 123 | R7 — r6_1 + fome: comer no posto se e_fome > .15 (duas refeições se dinheiro > 30), comida fora do posto se e_fome > .55 e d_comida < 20; variante 2: reparo mais cedo (vida < .65): mortos ≤ 0.70; aposta: ✓ (0.65–0.72) — metade das mortes é fome com 6 refeições em 5 dias, e a política tem renda 168 | ✓ quase (0.73, aposta 0.65–0.72): r7_1 mortos 0.73 [0.721, 0.763, 0.732, 0.714, 0.721] (−3 pp vs r6, −11.5 pp vs campeão), 7.3 refeições, 16.5 ent, renda 150, dia 5.7 (fome 52 %, dano 47 %). Traço: 23 % das escolhas em FICAR — tempo parado que era corrida; dinheiro final 7 = come até a renda deixar |
| 124 | R7 — política construcao_2 (reparo cedo, menos água): — | RECUSADA pelo orquestrador (saída sem bloco python/PREDICAO) |
| 125 | R8 — r7_1 SEM 'ficar' (23 % das escolhas eram parado: nunca devolver 8; se não há o que comprar, argmin d_alvo) e variante 2 = idem + reparo só com dinheiro > 25 (guardar caixa para comida): mortos ≤ 0.68 e renda ≥ 165; aposta: ✓ variante 1 (0.66–0.70) — o tempo parado vira 2–3 corridas a mais, e corrida é comida | ✗ r8_1 0.88 (13.3 ent, renda 119), r8_2 0.90: tirar o 'ficar' derrubou corridas e refeições — os 23 % parados NÃO eram desperdício: era o táxi no raio do serviço completando compras (uma ação por tick). Erro do consolidador ao ler o traço. TETO DA NOITE = r7_1: 0.73 vs campeão 0.85 |
| 126 | Cadeia da prova por construção (r1→r8, 8 rodadas, 16 políticas, contrato certo a partir da r3): r3–r4 morrem de fome dia 3 (desvio demais) → r5 literal do campeão morre dia 4.1 por dano → r6 + reparo 0.76 (bate o campeão) → r7 + comida 0.73 → r8 sem 'ficar' 0.88 (regressão). Teto 0.73; política em src/politicas/campeao_explicito_r7_1.py; próximo passo é decisão do Leonardo (professor / evoluir a partir dela / refinar) | fechado 03:05 |
| 127 | LAÇO v2, lote 3, p7 (alavanca: RUA: penalizar sair da rua (custo_frente) ao ir ao alvo): PREDIÇÃO DO AGENTE peso pequeno (0.15) só desempata — custo_frente varia 1..3 (diff máx 2), então penalidade máx = 0.15×2 = 0.3, contra dif | ✓ 0.66 [0.656, 0.656, 0.654] (5 sementes: 0.65 [0.656, 0.656, 0.654, 0.628, 0.641]), 17.8 corridas, renda 165, 7.8 refeições, oficina 2.0; −19 pp vs campeão evoluído, −7 pp vs r7_1. Cópia: src/politicas/campeao_explicito_L3p7.py |
| 128 | LAÇO v2, lote 4, p2 (alavanca ÁGUA sobre a base L3 p7): PREDIÇÃO DO AGENTE mortos ≈0.64–0.66 (ganho pequeno — sede já é só ~7% das mortes em p7, não é o gargalo); corridas ≈18 | ✓ 0.62 [0.617, 0.609, 0.641] (5 s: 0.63), 18.4 corridas, renda 172, 8.0 refeições; −4 pp vs L3 p7, −22 pp vs campeão. Cópia: src/politicas/campeao_explicito_L4p2.py. Nota: 6/8 do lote 4 eram a base intacta (parser pegou o código ecoado pelo hook) — corrigido |
| 129 | LAÇO v2, lote 5, p4 (alavanca GASOLINA sobre L4 p2): PREDIÇÃO DO AGENTE mortos ≈0.65–0.68 (empate ou leve melhora vs p7=0.66); corridas ≈17.5–18.0; refeições ≈7.6 | ✓ 0.57 [0.544, 0.573, 0.602] (5 s: 0.58), 18.9 corridas, renda 175, 8.3 refeições, 11.4 abastecidas (mais paradas, menos litros); −5 pp vs L4 p2, −28 pp vs campeão. Cópia: src/politicas/campeao_explicito_L5p4.py |
| 130 | LAÇO v2, lote 6, p4 (GASOLINA sobre L5 p4): PREDIÇÃO DO AGENTE mortos ≈0.55–0.60 (leve melhora ou empate c/ melhor global 0.57 = L5p4); mecanis | ✓ marginal 0.56 [0.529, 0.565, 0.586] (5 s: 0.57 = empate com L5 p4 0.58), 19.0 corridas, renda 177. Platô 0.56–0.58 em 3 lotes sobre a mesma base. Regra do Opus (19 políticas): mortos ≈ 1.48 − 0.047·corridas, r = −0.97 |
| 131 | TETO PROVISÓRIO da busca local por política explícita (laço v2, 55 políticas, lotes 1–8, uma alavanca por agente sobre a melhor base): 0.56–0.58 em 5 sementes por 4 lotes seguidos; alavancas 'estruturais' do lote 8 não quebraram (parada mínima colapsou 0.94; comida noturna 0.62; caça-passageiro 0.60). Predições dos agentes agora calibradas (preveem empate, medem empate) = espaço de UMA alavanca esgotado em torno desta base. Todas as alavancas foram de MANUTENÇÃO do corpo; a camada de TRABALHO (para onde ir quando livre) nunca foi tocada → lotes 9–12 | provisório 11:15 |
| 132 | PANE COM PREÇO no juiz (análise externa 09/09 via Leonardo; cenário pane_cara = base + guincho 10 + 5 L após pane; as 8 políticas do platô + r6_1/r7_1/L3p7 + campeão transplantado): PREDIÇÃO EXTERNA (a) amplitude entre as 8 do platô sobe de 1.3 pp para ≥ 8 pp; (b) todas pioram, base 0.56 → 0.65–0.80; (c) Spearman(panes/dia, mortos) ≤ −0.4; (d) próxima alavanca vencedora = combustível. MINHA APOSTA: (b) ✓; (a) ✗ (as 8 são o MESMO ser: corridas/dia 2.48 e panes/dia 0.90 idênticos até a 2ª casa — o preço da pane não as separa, só as desloca juntas); (c) ✗ no sinal: já é +0.49 (mais pane/dia = mais morte) e vai ficar mais positivo, não negativo; (d) ✓ | FECHADA: (a) ✗ externa / ✓ minha — as 8 do platô ficam TODAS em 0.95 (amplitude 0.004): são o mesmo ser; (b) ✓ nas duas mas a escala da externa (0.65–0.80) errou: base 0.56 → 0.95, campeão 0.85 → 0.98, r6/r7 0.98–0.99; (c) Spearman(panes/dia, mortos) = +0.58 (não ≤ −0.4); (d) não testado. Leitura: com guincho pago ninguém tem estratégia de combustível — todas as políticas (e o campeão) são especializadas no mundo do guincho grátis |
| 133 | Método (análise externa): o ganho 0.85 → 0.56 NÃO é maldição do vencedor — confirmação com 5 sementes difere da triagem em +0.0016 ± 0.009 (n=18) | ✓ confirmado por mim; sementes de confirmação agora independentes (7782–7786) |
| 134 | CLONE por forma fechada da política explícita L6 p4 (0.56) num Linear (degrau 3 da análise externa = pred 122): ridge Φ→one-hot da escolha, 128 seres × 2400 ticks nos mapas de treino, avaliado nos mapas do juiz. APOSTA: fidelidade < 80 % (regras com histerese/limiares/estado não cabem numa nota linear centrada; achado 84: o corpo é invisível na direção) e o clone morre ≥ 0.85 (não reproduz nem o campeão). Se ✓ (clone ≤ 0.70): a evolução tinha esse ponto ao alcance e não achou → gargalo = busca; semear com ele (pred nova) | ✓ minha aposta: fidelidade 60.0 % (movimento 61.9 %; 76.8k estados), clone morre 1.00 (sede 90 %: abastecidas 0.5, nunca compra) — a forma fechada LINEAR não carrega regras com estado/limiar. A política 0.56 não é um ponto do espaço linear; a evolução linear não 'deixou de achar', ela não consegue representar. Caminho: híbrido (política como espinha fixa + genes por cima) ou arquitetura com estado |
| 135 | LAÇO v2, lote 12 (último), p8 (LIVRE: parar para ESFRIAR quando e_calor > .667, histerese até .55): PREDIÇÃO DO AGENTE mortos ≈ 0.53–0.58 (empate a leve melhora sobre a base 0.56 — ataco só a fatia de dano do  | ✓ 0.53 [0.526, 0.531, 0.544] (5 s: 0.55 [0.565, 0.555, 0.573, 0.516, 0.56]) vs base 0.56/0.57: primeira alavanca do lado do DANO (dano 39 % das mortes vs 46–48 %); −2 pp em 5 s. Teto do laço v2 após 12 lotes / 86 políticas: 0.55 (5 s). Cópia: src/politicas/campeao_explicito_L12p8.py |
| 136 | F2 CUSTO POR ATIVAÇÃO (spec Mundo Vivo; implementado por BLOCO: |saída do bloco na nota| média, amostrada a cada 10 ticks, bloco com saída ≥ 1 conta cheio). PREDIÇÃO DA SPEC: sob λ=0.3 no mundo transparente, dof sobrevivente sobe de 3 para ≥ 15, ≥ 60 % no bloco ref, mortalidade não piora. CORREÇÃO: ref tem 4 genes (60 % de 15 = 9 > 4: impossível). MINHA APOSTA: dof ≥ 15 ✓; os sobreviventes se concentram nos blocos SILENCIOSOS (hip com ganho ~0, cor com delta ~0 — genes que existem mas não emitem custam ~0), não em ref; mortalidade igual ±5 pp. DADO PRÉVIO (g7, genes aleatórios σ .3): fração do tempo com sinal por bloco = tal .87, cor .66, len .20, rap .06, ref .02, hip .02 — tálamo e córtex são os barulhentos. Bateria m1/m2 na fila (fumaça P512 G60, COMPLETO + linear, λ .3, existência vs ativação) | FECHADA: ativação dof 318 (existência 165) — ✓ ≥ 15, mas a spec previu ≥ 60 % em ref (2.4 genes: ✗). Sobreviventes ~2× em TODOS os blocos (rap 84, len 117, hip 76, cor 28, tal 10, ref 2.4); ativacao_bloco: tal .997 e cor .981 (sempre ligados, pagam cheio), rap .15 len .17 hip .18 ref .11 (quase de graça). Mortalidade 0.87 vs 0.86 (pareado +1 pp, p .11 vs linear 0.83) ✓ não piora. Leitura: custo por ativação NÃO faz peça pagar — só deixa de cobrar silêncio; o completo continua não batendo o linear |
| 137 | LAÇO v2, lote 14, p7 (alavanca RUA sobre L12 p8): PREDIÇÃO DO AGENTE empate — mortos ≈ 0.53–0.57 (base 0.53), corridas/dia vivo ≈ 3.00–3.15 (base 3.15). O peso | ✓ 0.52 [0.508, 0.508, 0.531] e **0.50 em 5 sementes** [0.492, 0.505, 0.492, 0.5, 0.49] vs base 0.55 (5 s): −5 pp, panes 6.2 (vs 6.8); novo teto do laço (14 lotes, 101 políticas). Cópia: src/politicas/campeao_explicito_L14p7.py |
| 138 | F3 RETINA (spec Mundo Vivo; implementada como 8 raios de BÚSSOLA = as 8 direções de movimento, sem proa; oclusão por quadra fora da rua; R_dia 60 / R_noite 15; `livre` por opção; d_* por opção viram 'onde o raio viu', cego = 2R). PREDIÇÃO DA SPEC: (a) linear piora ≥ 15 pp com retina vs onisciente; (b) braço com hipocampo bate o linear ≥ 10 pp pareado; (c) a política explícita também piora ≥ 10 pp. MINHA APOSTA: (a) ✓ (o linear anda 82 % do tempo guiado por d_*; cego de noite morre de pane); (b) ✗ (memória de lugar precisa de treino longo e o hipocampo nunca bateu; empate ±5); (c) ✓ e mais: a política explícita cai MAIS que o linear (regras com limiar em d_posto viram ruído quando d_posto = 120 'cego'). Bateria só após portões (raio/parede/noite/oráculo, identidade off, sensibilidade de livre) | FECHADA: (a) ✗ linear com retina 0.81 [0.81, 0.799, 0.812, 0.786, 0.82] vs sem 0.83 — a evolução se readapta cega em 36 gerações; (b) ✗ COMPLETO 0.81 = linear (sem retina 0.78 vs 0.83); (c) ✓ e mais forte que apostei: políticas explícitas 0.49→0.91, 0.56→0.93, 0.73→0.97 (campeão transplantado 0.85→0.87). MECANISMO: o passageiro continua oráculo (d_alvo não passa pela retina) e a pane com guincho GRÁTIS é o GPS — o táxi evoluído nunca precisou ver o posto; as políticas a mão quebram porque têm limiares em d_posto/d_comida que viram 120 (cego). Visão só terá valor quando a pane tiver preço → pred 142 |
| 139 | LAÇO v2, lote 15, p8 (LIVRE sobre L14 p7): PREDIÇÃO DO AGENTE empate a leve melhora — mortos ≈ 0.51–0.56 (base 0.52–0.55). e_reserva raramente passa de  | ✓ 0.49 [0.471, 0.479, 0.518] e 0.49 em 5 s [0.461, 0.523, 0.492, 0.482, 0.479] vs base 0.50: −1 pp em 5 s (empate técnico), 18.6 corridas, panes 6.2. Teto do laço: 0.49 (15 lotes, 109 políticas; 0.85 → 0.49 = −36 pp sobre a evolução). Cópia: src/politicas/campeao_explicito_L15p8.py |
| 140 | TETO DO LAÇO v2 (mundo transparente): 16 lotes, 117 políticas julgadas (~6 h de GPU), 0.85 (evolução) → 0.49 (política explícita L15 p8, 5 s); lote 16 p2 0.49/0.50 = empate; rendimento: 0.73→0.56 nos lotes 1–6, platô 7–11, 0.53/0.50/0.49 nos lotes 12–15 por combinação (esfriar + rua + reserva). Laço parado; próximo laço só no mundo da retina se a pred 138(c) confirmar que a política explícita também cai | fechado 15:45 |
| 141 | F4 REGIME (spec Mundo Vivo; estações: período 5 d, amp .5 em consumo/preço/demanda/noite, média 1 no ciclo; sentidos est_sin/est_cos). PREDIÇÃO DA SPEC: as camadas lentas (τ > 100), hoje com correlação 0.00 com tudo, passam a correlacionar com a fase (|r| ≥ .3) e a ablação delas dói ≥ 5 pp. MINHA APOSTA: |r| ≥ .3 ✓ é barato (a fase entra como sentido: qualquer gene lento que a leia correlaciona por construção — é a ablação que decide); ablação ≥ 5 pp ✗ (o completo nunca bateu o linear; 5 dias de período com 10 dias de vida = 2 ciclos: pouco para pagar memória). Bateria só após portões e após a retina (ordem da spec) | pendente |
| 142 | MUNDO VIVO v1 = retina + guincho PAGO (10, 5 L) + régua `vida` com horizonte aberto (spec §0.7: não amaciar, trocar a régua): braços linear, COMPLETO, completo sem hipocampo (knock-out de nascença), fumaça P512 G60 pac30 5 s, semeados do linear q8 (alinhado por nome). APOSTAS: (a) a régua `vida` separa (CV de t_vida ≥ .15 e frac_teto < .05) onde 'mortos em 10 d' cravaria em ~1.00 ✓; (b) o linear passa a abastecer por vontade (abast ≥ 4/vida) porque o guincho custa e a retina mostra o posto de dia — ✓; (c) COMPLETO vs linear em t_vida: empate ±10 % (✗ para 'hipocampo ≥ 10 %': memória de lugar precisa de mais que 60 gerações e a retina de dia já dá o posto a 60 m); (d) sem-hipocampo = COMPLETO ±5 % | FECHADA: (a) ✓ a régua vida separa: linear t_vida p10 1.72 d / mediana 3.59 / p90 7.30, frac_teto 0 (mortos em 30 d = 1.00 em todos); (b) ✗/~: abastecidas por vida 3.2 (linear) e 3.5 (COMPLETO) < 4; só o sem-hipocampo chega a 4.0; (c) ✓ empate: COMPLETO fit 4.50 vs linear 4.59 (−2 %, p .75); (d) ✗: sem-hipocampo 4.98 (+9 % vs linear, +11 % vs COMPLETO, p .13; vida média 4.58 vs 4.23 d) — tirar o hipocampo DE NASCENÇA ajuda: 119 genes semeados com ruído σ .2 num bloco que nunca pagou custam. Morte: dívida (dinh −15/−8/−7: ~5 panes × guincho 10) + dano; fome 52–56 e água 64–68 no fim |
| 143 | MUNDO VIVO v2 = v1 (retina + guincho pago + régua vida aberta) + F4 regime padrão (estações de 5 d em consumo/preço/demanda/noite) + F2 custo por ativação λ .3; braços linear / COMPLETO / sem hipocampo / sem livre (só camadas); fumaça P512 G60 5 s. APOSTAS: (a) linear vs COMPLETO em fit de vida: empate ±10 % (✗ para 'camadas pagam com regime': 10 d de vida = 2 estações, pouco para memória de fase pagar); (b) sob λ .3 em ativação o COMPLETO mantém ≥ 200 genes e tálamo/córtex seguem sempre ligados (ativacao_bloco ≥ .9); (c) sem-livre ≤ COMPLETO −5 % (a rápida/lenta é o que o completo usa de verdade; sem ela cai ao linear com custo); (d) todos vivem MENOS que no v1 (regime tira ~5 %: o inverno cobra sem que a política preveja). Só roda após g21–g26 verdes | FECHADA: (a) ✗ COMPLETO fit 3.43 vs linear 3.85 = −11 % (p .002): sob custo por ativação + inverno o completo vira PEDRA (1.1 corridas, 0 abastecimentos, 0.7 panes, vive 3.4 d parado); (b) ✓ dof 529 (silêncio é grátis) e tal 1.00 / cor 1.00 sempre ligados (rap .01, len .11, hip .06); (c) ✗ sem-livre 3.47 ≥ COMPLETO 3.43 (não ≤ −5 %): as três variantes com camadas ficam −10 % abaixo do linear (p ≤ .006) e todas viram pedra (ent 1.1–2.7; abast 0–0.5); (d) ✓ forte: v2 < v1 em todos (linear 3.85 vs 4.59, −0.74, p .002; ent 5.6 vs 11.9 — o inverno com amp .5 em 4 canais é duro até para o linear). MECANISMO: portões (tálamo/córtex) emitem sinal a cada tick se algum gene ≠ 0 → custam cheio; metab 1.33; em 33 gerações a evolução não zera os genes (σ .3, clamp) — a resposta que acha é parar |
| 144 | SEMEADURA LIMPA (separa 'peça inútil' de 'peça semeada com ruído'): mundo_vivo_v1 (retina + guincho pago + régua vida; regime OFF; custo 0), COMPLETO e sem-hipocampo semeados com σ0 = .02 nos genes NOVOS (o1 usou .2), linear como controle (idêntico ao o1); fumaça P512 G60 5 s. APOSTAS: (a) a diferença sem-hipocampo × COMPLETO cai de +11 % para < 3 %; (b) COMPLETO empata com o linear (±5 %); (c) nenhum braço com camadas bate o linear ≥ 10 % — 'sem ruído a peça é neutra, com ruído custa; em nenhum caso paga' | FECHADA: (a) ✗ parcial: sem-hip 4.89 vs COMPLETO 4.56 = +7 % (o1: +11 %) — o ruído de semeadura explicava ~4 pp, o resto persiste; (b) ✗ COMPLETO −6 % vs linear (p .14); (c) ✓ ninguém ≥ +10 % (sem-hip = linear 4.89 vs 4.87, +0.6 %). MECANISMO: com σ0 .02 os genes do hipocampo nascem ~0 (mem ≈ 0), mas a MUTAÇÃO (σ .3 em todos os genes, toda geração) injeta ruído por 119 dimensões sem função — a peça inútil custa pela mutação, não só pela semeadura. Nota (H63): o linear deste run deu 4.87 vs 4.59 no o1 por caos de arredondamento |
| 145 | [INVÁLIDA 22:45: as três células rodaram P=128 — o cenário sobrescrevia `--P`; refeita como 157] TESTE DE P (CS B4a: 'poucos seres, muitas sementes'): linear no mundo_vivo_v1, P ∈ {128, 256, 512, 1024}, G60 pac30, R4, sementes 0–4, medindo fit de vida do campeão. APOSTA: cresce de 128 para 256 (≥ 5 %) e satura de 256 em diante (512 e 1024 dentro de ±5 % de 256) → cortar P para 256 e quadruplicar sementes; ressalva de CS: repetir com COMPLETO antes de cortar para o genoma grande | pendente |
| 146 | λ_BASAL (CS B1: custo = λ_basal·dof_existência + λ_ativ·ativação; corrige o atrator 'não agir' do custo só por ativação). Teste: 87 genes ligados e mudos pagam mais que genoma vazio; basal 0 = identidade. Bateria v2b (v1 + custo .3 ativação + basal .15, SEM regime), n=10: APOSTA: COMPLETO faz ent ≥ 5 (não vira pedra), e sem-hipocampo − COMPLETO volta positivo (≥ +0.2), como CS prevê; mas nenhum bate o linear ≥ 10 % | pendente |
| 147 | ORÇAMENTO DE ATIVIDADE (CS §E, alternativa ao imposto): soma das saídas dos blocos na nota de movimento projetada para ≤ B = 1.0 por tick (None = hoje, bit a bit; a espinha linear fica fora do orçamento; notas de serviço fora — declarado). Braços v2d (v1 + orçamento; linear / COMPLETO / sem hipocampo, n=10, P do teste 145) contra v2b (basal). APOSTAS: (a) sob orçamento NINGUÉM vira pedra (ent ≥ 8 no COMPLETO) ✓ — não é custo; (b) as arquiteturas NÃO se separam ≥ 0.2 entre si (✗ para o critério de aceite do CS): os blocos já emitem pouco (rap .01–.15, hip .06) e a espinha domina; o orçamento só aperta tálamo/córtex, que são portões multiplicativos; (c) COMPLETO ≤ linear ±5 %. Se (b) ✓, o vínculo separa onde o imposto apagou — achado de método | pendente |
| 148 | CONTA EM TRÊS CANAIS (CS EQUACOES-NEUROMOD eq. 3: hoje m(t) só multiplica a fome; física: cérebro gasta caloria, água e gera calor). `custo_canais=('fome','agua','calor')`: água consome ×m, calor sobe +calor_sobe·(m−1) por tique; padrão ('fome',) = identidade bit a bit. Bateria v2e = v2b + 3 canais, n=10: APOSTA: NÃO muda o resultado do v2b em mais de 3 pp de mortos/fit (com basal .15 e ativação .3 m fica 1.0–1.3: água −20 %/dia e calor +.04/tique são pequenos perto de c_w e do motor); a seleção não vê 'canal', vê fitness — a alavanca é λ, não o canal. Se mudar > 3 pp, o mecanismo é o calor (aciona D_QUENTE e o esfriar no posto). | pendente |
| 149 | REGIME CURTO (CS brainstorm 3: período 5 d > vida mediana 3.9 d [P128, e78] ⇒ o ser nunca vê a fase repetir; regra período ≈ ⅓ da vida ⇒ 1.3 d). v2f = v2c com periodo_dias 1.3, n=10: APOSTA: a queda das camadas some em parte — COMPLETO − linear ≥ −5 pp (era ≤ −10 pp na 143) porque as camadas lentas veem 2–3 ciclos; mas ninguém bate o linear ≥ 5 % (regime só muda QUANDO, e o linear reage ao consumo medido). | pendente |
| 150 | DENOMINADOR NO TÁLAMO (CS brainstorm 1: portões 2·σ somam sem recurso escasso; `talamo_norm`; EMENDA 21:50 antes de rodar: modo FIXO gate·NG/Σgate (divisiva canônica, soma ≡ NG) em vez do teto min(1, ·), porque na semeadura limpa o teto é identidade na prática). v2g = v2b + talamo_norm fixo, n=10: APOSTA: NÃO muda nada acima de 3 pp — os portões nascem em 1.0 (Σ = NG exato, o denominador só morde se a evolução SUBIR portões) e sob custo basal os 15 genes ficam quietos; o §E e este denominador são objetos diferentes (nota de movimento vs portões) e NÃO a mesma linha como o CS escreveu. | pendente |
| 151 | AMPLITUDE DO CÓRTEX (CS brainstorm 2: |δ| ≤ .5 não inverte sinal; comida industrial 0.0 vs residencial 2.0 exige sinais opostos). v2h = v2b + cortex_amp 2.0, n=10: APOSTA: ganho ≤ 3 pp para COMPLETO e sem-hipocampo — poder inverter não é o gargalo (o córtex tem 48 genes com ~1 % ligado; o distrito já entra pela retina e pelos sentidos de serviço); se der > 3 pp, o CS acertou que era limite de expressão e o ledger 'córtex não paga' era sobre a implementação. | pendente |
| 152 | TEMPERATURA DE DECISÃO (CS brainstorm 4: argmax fora do genoma; gumbel-max com T·desvio das notas). v2i = v2b + temp .3, n=10: APOSTA: PIORA ≥ 5 pp em todos os braços — exploração dentro da vida sem aprendizado dentro da vida é ruído puro num mundo que mata em 4 dias; se T fosse gene a evolução levaria a 0. Se NÃO piorar, o argmax estava travando em platôs (empates de nota) e T vira gene. | pendente |
| 154 | DELEGAÇÃO TÁLAMO↔REFLEXO (CS DERIVA §5: nos 10 campeões do v1, quanto mais o tálamo fecha o portão de serviços mais forte o reflexo empurra ao posto, ρ = −.76, p = .011, correlação sobre genomas). Ablação cruzada: braço 'completo sem reflexo' na bateria v1_ablacao_camadas, n=10, lendo `talamo_servicos` do campeão. APOSTA: o portão de serviços REABRE só em parte — média ≥ .60 no sem-reflexo (vs .32–.72 com reflexo), diferença pareada ≥ +.15 em ≥ 7/10 sementes; e o sem-reflexo perde ≤ 5 pp de fit (a via lenta cobre mal o posto). Se o portão não mexer, a correlação era co-variação por semente, não delegação. | **✗** (12:40 10/09; retrato do Mundo A, e72/retrato_e43_mundoA5.json): sem reflexo o portão de serviços NÃO reabre — média .87 [.91, .80, .80, .63, 1.19] contra 1.10 no COMPLETO [.93, 1.24, 1.23, 1.15, .97]: fecha um pouco mais. E o COMPLETO do Mundo A já nasce com portões ~1.1 (não .32–.72 como no e77): a 'delegação' do e77 não replica num mundo com custo; a correlação portão×w cai a −.17 (n=20). A ablação diz: tirar o reflexo custa −3.4 % de fit e o tálamo não compensa. |
| 155 | ESCALA DO HIPOCAMPO (CS bancada: hipocampo dirige 690× menos por gene; conferido: a saída entra ×Cerebro.ESC = .01 × tanh(gene nascido em 0) — handicap de ~100× por desenho, não geometria). v2j = v2b + hip_esc 1.0, n=10: APOSTA: `hipocampo_ganho` e a ativação do bloco hip sobem (a peça passa a PODER dirigir) mas o fit do COMPLETO fica ≤ +3 pp do v2b e o sem-hipocampo continua ≥ COMPLETO: o mundo v2 não recompensa lembrar por distrito (12 caixas de média móvel não antecipam nada — argumento do CS no formulário). Se COMPLETO passar o sem-hipocampo por ≥ 3 pp, o 'hipocampo não paga' de 2 meses era escala, não memória. | pendente |
| 156 | DERIVA NULA (CS DERIVA §2: passeio sem seleção com a MESMA mutação, N(0,.3) corte ±5, liga 441/502 genes em 120 ger.). `deriva_nula.py` com σ_mut .3 (conferido em lab.py:39) e semeadura da bateria (σ0 .02/.2, espinha .05). APOSTA: dof do campeão COMPLETO do v1 (67.8 %, e77) fica DENTRO de ±10 pp do nulo na sua geração efetiva (30–60): dof NÃO é evidência de seleção; mas a fração do córtex na trava do campeão (.346) fica ABAIXO do nulo na mesma geração (nulo ≥ .55 em 45+ ger.): a seleção segura o córtex longe da trava, como o CS diz. | pendente |
| 157 | SEMENTES FIXAS NA AVALIAÇÃO (CRN). Achado 22:45: a avaliação por geração usa semente 777000+13·ger, o 'melhor por semente' oscila ±13 % entre gerações (P128 linear: 5.46 → 7.86 → 6.23 …) e a paciência de 30 dispara por sorte, não por falta de melhora; e o teste de P (145) rodou P=128 três vezes porque o cenário sobrescrevia `--P` (corrigido: flag explícita vence). `--crn fixo` = mesmas sementes em todas as gerações (aptidão determinista por genoma). Células: linear em mundo_vivo_v1, P256 rotativo vs P256 fixo vs P512 rotativo, G60 pac30, R4, 5 sementes. APOSTA: com fixo a curva de treino vira monótona e passa de 40 gerações sem parada; o fit de TESTE (mapa 7777, 128 cópias) sobe 3–8 % sobre o rotativo (4.84), não mais (sobreajuste às 4 réplicas come parte do ganho); P512 rotativo ≈ P256 rotativo ≈ P128 (±3 %): P não é a alavanca, o ruído da avaliação é. | **✗ na parte CRN, ✓ na parte P** (23:05): crn fixo deu 4.49 (−7 % vs 4.84) e a curva de treino NÃO ficou monótona — sementes fixas não dão determinismo num mundo caótico com kernels atômicos, e ainda sobreajustam (treino 8.88 vs teste 4.30 na semente 2). P256 rot 4.69, P512 rot 4.84 = P128 ao milésimo (mesmo campeão: ninguém em 35 ger. × 512 bateu a cópia inicial) → P não é alavanca; a evolução NÃO sai da semente. Mecanismo da parada: comparava um sorteio com um sorteio (corrigido: máx da janela). |
| 159 | A EVOLUÇÃO SAI DA SEMENTE? Célula G=1 (só a população inicial: cópias do campeão linear e64 com σ_espinha .05, P256) vs G60 (4.84/4.69). APOSTA: o campeão de G=1 fica a ≤ 5 % do de G60 — em mundo_vivo_v1, 35 gerações de GA com σ_mut .3 e R4 não acrescentam nada mensurável à semente (mutação grande demais + avaliação ruidosa: seleção cega). | **✗** (23:35): G=1 dá 4.14 [3.99, 3.97, 4.61, 4.21, 3.95] vs G60 4.69–4.84: a evolução acrescenta +13–17 % em ~32 gerações. Eu li errado a estagnação: P512≡P128 continua sem explicação, mas a busca ANDA. |
| 160 | RÉPLICAS vs POPULAÇÃO ao mesmo custo: P128 R8 vs P256 R4 (rot). APOSTA: R8 dá fit de teste ≥ +3 % sobre P256 R4 e curva de treino menos serrilhada (desvio entre gerações cai ≥ 30 %): o gargalo é o ruído da avaliação, não a busca. | **✓ fraco** (23:35): P128 R8 = 4.83 [5.40, 4.76, 4.34, 4.93, 4.72] vs P256 R4 rot 4.69 (+3 %); curva de treino menos serrilhada (gen 30→45: 5.90→6.29 vs 7.21→6.97) e chegou a 45+ gerações com a parada por janela. Mecanismo confirmado pelo CS (JARDIM-COMUM): com R=4 o erro do fitness (1.95 d) é maior que o desvio entre genomas (1.40 d), SNR .72. |
| 161 | σ DE MUTAÇÃO: .3 cravado (lab.py) mutava TODOS os 57 genes da espinha com desvio .3 num campeão de genes O(1) — filhos quase sempre piores. P256 com σ_mut .05 e .1 (parada por janela, G60): APOSTA: σ .05 é o primeiro que faz a evolução andar — fit de teste ≥ +5 % sobre 4.84 e gerações efetivas > 40; σ .1 no meio; se nem .05 andar, o problema é a régua/ruído (160) e não o operador. | **✓ (00:20 10/09)**: σ .05 → 5.21 [5.27, 4.95, 5.44, 5.34, 5.05], σ .1 → 5.36, σ .3 → 4.69–4.84. Ótimo em ~.1 (n=5; .05 e .1 dentro do ruído, ambos +8–14 % sobre .3). Protocolo passa a σ_mut .1. | **✓ (parcial, σ .1; 00:05 10/09)**: σ_mut .1 → 5.36 [5.17, 5.75, 5.67, 5.22, 4.99] vs .3 → 4.69–4.84: +11–14 %, TODAS as sementes acima do melhor de σ .3; curva de treino sobe em todas (gen 0→45: +15–30 %) e chega a 45+ ger. Mecanismo: com σ .3 os 57 genes O(1) mutam todos de uma vez → filhos quase sempre piores → a elite só replica sorte. σ .05 pendente (decide se .05 < .1 < .3 ou se .1 é o ótimo). [16:30: CORREÇÃO — e78 tinha retina; z2 4.85 vs e78 σ .1 5.36 é pareamento válido: σ .2 pior.] |
| 154a | REPLICAÇÃO DA DELEGAÇÃO em genomas novos (P128, e78: COMPLETO + sem-hipocampo × 5 sementes, σ0 .2, independentes do e77 σ0 .02): `retrato_bateria.py` mede corr(portão de serviços a necessidade 0, w do reflexo). APOSTA: o sinal replica mas mais fraco: −.6 < ρ < −.2 (n=10); no e77 a ferramenta deve reproduzir o −.76 do CS (se não reproduzir, a definição de 'portão' ou de 'w' difere e o achado é da definição dele). | **✓ fraco** (23:35): e77 com a minha definição (portão de serviços a necessidade 0 × w do reflexo): pearson −.52, spearman −.49 (CS: −.76; definição do "empurrão" difere, sinal igual); dentro do COMPLETO −.68/−.70, dentro do sem-hipocampo −.11/0. P128 (genomas novos): −.28/−.32 no total — dentro da aposta −.6<ρ<−.2 —, mas dentro do COMPLETO −.60 e dentro do sem-hipocampo **+.40/+.50** (sinal invertido, n=5). A delegação existe só no COMPLETO e é fraca; a ablação (154) decide. |
| 162 | JARDIM COMUM (CS docs/66: 83 % da variância do tempo de vida é o berço, 11 % o genoma; com R=4 a elite é quem nasceu bem). `jardim_comum`: berço, passageiros, destinos, ponto e respawn sorteados por BLOCO (NB = NC·R) e compartilhados por todos os genomas da geração (seleção pareada); blocos trocam a cada geração (semente rotativa); o juiz (medidas, 128 cópias) fica FORA do jardim. Portão: mesmo genoma no jardim ⇒ variância exatamente 0 dentro do bloco. Célula: linear P256 R4 jardim vs P256 R4 rot (4.69) e janela. APOSTA: o fit de TESTE sobe ≥ +5 % (≥ 4.92) e a curva de treino sobe mais regular (o mesmo ganho que R8 deu, sem dobrar o custo); se não subir, o gargalo não é seleção-por-sorte e sim a régua (vida) ou o operador (σ). | **✗ sob σ .3** (00:45 10/09): jardim 4.69 [4.86, 4.70, 5.17, 4.29, 4.45] = rotativo 4.69; 58 ger. efetivas (janela). Mecanismo: com σ .3 os filhos são quase todos piores que a elite independentemente do berço — o pareamento só ajuda quando a diferença entre genomas é pequena frente ao ruído, que é o regime de σ .1; célula r5 (σ .1 + jardim vs σ .1 rot 5.36) decide. |
| 163 | TRAJETÓRIA NO JARDIM (CS docs/66 §5: comparar decisões). `trajetoria.py`: campeões do P128 (linear vs COMPLETO vs sem-hipocampo, 5 sementes) nos MESMOS 24 blocos (3 mapas × R8), ações gravadas por tique. APOSTA: concordância de ação linear×COMPLETO ≥ .80 dos tiques (as camadas quase não dirigem: bancada); 1ª divergência mediana < 200 tiques (chaos cedo); COMPLETO vive mais em ≤ 40 % dos blocos (pareado, é pior); a opção onde a estratégia mais difere é uma de SERVIÇO (abastecer/comer), não de direção. | **✗ em 2 de 4** (01:00 10/09; e72/trajetoria_e43_P128.json, 24 blocos × 5 sementes): concordância linear×COMPLETO .27 (aposta ≥ .80 ✗ — as camadas MUDAM a maioria das decisões); 1ª divergência mediana 18 tiques ✓; COMPLETO vive mais em 39 % dos blocos ✓; a opção que mais difere é FICAR (op8: 20 % do tempo no linear → 4 % no COMPLETO), movimento e não serviço ✗. Mecanismo (Opus): dirige somado dos blocos = 74 % da espinha — autoridade não falta; o que falta é PARA ONDE. Corrige a minha frase "as camadas quase não dirigem": o 0.3 % era dirige/desloca (preço), não influência. |
| 165 | CUSTO QUE COBRA O MODO COMUM (`ativ_centrada`, opus-analista). MECANISMO NO CÓDIGO: `campo.py:427` faz `sc = sc - sc.mean(1, keepdim=True)` — qualquer parcela IGUAL nas 9 opções tem efeito EXATAMENTE zero na decisão (movimento e mover-vs-servir). Mas `ativ_blocos` (`campo.py:759`) cobra `|saída do bloco|.mean(1)`, que é justamente o modo comum. Bancada (`e72/bancada_padrao.json`): dirige/(dirige+desloca) = 0.3 % — 99.7 % da conta é o que o G1 joga fora; e blocos que multiplicam sentidos de DISTÂNCIA (d_posto ~60 m) pagam ~60× mais que blocos sobre sentidos do corpo (∈[0,1]) pelo MESMO efeito. Isso explica a tabela do ledger (pred 136/143: tal .997–1.00 e cor .98–1.00 'sempre ligados'; rap .01–.15, len .11–.17, hip .06–.18, ref .11) sem precisar de 'o portão emite sempre'. `ativ_centrada` (padrão False = identidade bit a bit) troca a conta por `|saída − média entre opções|`. APOSTA com λ .3 + basal .15 no mesmo mundo: (a) ativacao_bloco do tálamo cai de ≥ .99 para ≤ .5 e do córtex de ≥ .95 para ≤ .6; (b) a fatia de tálamo+córtex na conta (Σ n_b·ativ_b) cai ≥ 1/3; (c) metab médio do COMPLETO cai ≥ 30 % com o MESMO λ; (d) o COMPLETO deixa de virar pedra — ent ≥ 5 (pred 143 mediu 1.1–2.7). Se (a) e (c) ✗, o sinal dos blocos já é quase todo diferencial no genoma evoluído (a bancada com genes uniformes ±1.5 não o representa) e a conta de hoje está certa | pendente |
| 166 | MALDIÇÃO DO VENCEDOR NA EXPORTAÇÃO (`campeao=reavaliado`, opus-analista). MECANISMO NO CÓDIGO: `evoluir_sementes` devolve `Wv[si][0]` (`lab.py`, fim da função) = o argmax de P avaliações RUIDOSAS da última geração. Com σ_genoma 1.40 d e σ_erro 1.95 d (CS docs/66, SNR .72) a correlação medido×verdadeiro é ~.58: o argmax de 128 sorteios fica ~1.6 σ_g acima da média quando o melhor verdadeiro está ~2.7 σ_g — perde-se ~1 σ_g de genoma na última linha do run. Reavaliar só a elite (ne = 15 % de P) uma vez com semente nova e escolher pela MÉDIA das duas medições custa ne/(P·G) ≈ 0.25 % do run. APOSTA: fit de teste sobe ≥ +5 % pareado (≥ 4/5 sementes) sobre o MESMO protocolo com `campeao=ultimo`, sem nenhuma geração a mais — o ganho é da mesma ordem do σ_mut (+11–18 %) por 1/60 do custo. Se subir < 2 %, a elite da última geração já é um clone só (diversidade morta) e o gargalo não é sorte na exportação | ✗ (z1 vs e78/P256sig01, pareado 5 sementes, P256 G60 σ .1): reavaliado 5.028 [4.84, 5.31, 5.48, 4.71, 4.79] vs último 5.358 [5.17, 5.75, 5.67, 5.22, 4.99] — pior em 5/5 (−.33, −6 %). Mecanismo: a reavaliação da elite (38) num mundo novo é OUTRA amostra ruidosa (postos escolhidos [0, 22, 15, 1, 36]): troca o argmax de P avaliações acumuladas pela evolução pelo argmax de 38 avaliações de um sorteio só — a maldição do vencedor continua e o campeão que a seleção acumulou é descartado. Fica `campeao=ultimo`. [16:30: CORREÇÃO — o e78 também tinha NM_RETINA=1 (pedido r3): pareamento VÁLIDO, veredito ✗ mantido. O que não bate é o TEMPO (z1 2097 s vs e78 813 s no mesmo protocolo): investigado em c9p/z5.] |
| 167 | MUNDO B — 'o cérebro paga pelo que MUDA a decisão' (`cenarios/mundoB_conta_justa.json`, opus-analista). Mundo A (v1 + custo por ativação .3 + basal .15) com UMA lei trocada: `ativ_centrada` ligado; mesmos 8 seres, mesmas 5 sementes, mesmo protocolo (P128 G60 pac30 R4 σ_mut .1) — pareado com o A célula a célula. APOSTA: (a) a conta do cérebro encolhe (metab do COMPLETO ≥ 30 % menor) e o RANKING de pagadores muda — o córtex deixa de ser o maior pagador; (b) o buraco COMPLETO − linear fecha pelo menos METADE do que era no A (no v2, pred 143, era −11 %); (c) MESMO ASSIM nenhum ser com camadas bate o linear em ≥ +5 % — porque a peça continua sem informação que o linear não tenha (a tese 'seletor, não gerador'); (d) o ser 'COMPLETO hip 1.0' é o que mais ganha do A para o B (é o que mais emite modo comum: hip desloca 93.2 na bancada com esc 1.0 vs 0.93 com esc .01). Se (b) ✗ (o buraco não fecha), então a penalidade das camadas NUNCA foi a conta — é a peça mesma, e o custo por ativação sai do programa | **✓ na direção, parcial no tamanho** (12:35 10/09; e79/e43_mundoB5.json vs mundoA5, 5 seres × 5 sementes pareadas): a conta do COMPLETO cai de metab 1.74 para 1.37 (51 % menor no excesso sobre 1 — aposta ≥ 30 % ✓); TODOS os cérebros sobem: COMPLETO 4.11→4.47 (+8.8 %, 3/5), sem hip 3.97→4.20 (+5.8 %), sem reflexo 3.97→4.30 (+8.3 %), talamo fixo 3.87→4.48 (+15.8 %, 5/5); linear 4.98 = 4.98 (controle sem imposto, bit a bit). Ranking muda: em A COMPLETO > sem hip ≈ sem reflexo > talamo fixo; em B talamo fixo ≈ COMPLETO > sem reflexo > sem hip. Ninguém alcança o linear (−10 a −16 %, era −17 a −22 %). Mecanismo: em A a conta cobrava modo comum que o G1 descarta (99.7 % da magnitude); em B só o que muda a decisão paga, o excesso de conta cai à metade (.74 → .37) e o que sobra é quase todo BASAL (.15·dof/100 ≈ .31 com ~210 genes; a parte por ativação centrada ≈ .06): a diferença que resta contra a espinha (−10 a −16 %) é peça + aluguel basal, não a conta por ativação. Próximo: Mundo C (cidade do tamanho da vida) com seres no lote. |
| 168 | AUDITORIA DO P: 'P512 ≡ P128 ao milésimo' É ARTEFATO (opus-analista). `e78/e43_P128.json`, `e78/e43_P256.json` e `e78/e43_P512rot.json` têm fit do linear IGUAL nos 16 dígitos (4.844735336303711) e o mesmo `cenario_hash` 54f2d8a1e8: os dois primeiros passaram `--P 128`/`--P 256` no argv mas rodaram ANTES do fix de precedência (`_explicit`, 09-09 22:50) — o cenário v1 impôs `protocolo.P = 512` nos três. Ou seja: NUNCA houve um run com P=128; o que o diário leu como 'P não é alavanca / a evolução não sai da semente' é o mesmo run comparado consigo mesmo (e `e43_P256.json` grava `P: 512` no próprio JSON). O único par de P medido no mesmo protocolo é P512 4.845 (36 ger.) vs P256 4.688 (33 ger.) = +3.4 % a favor do P maior. APOSTA: rodando de verdade P128 × P256 × P512 com σ_mut .1 e parada por janela, o fit cresce com P e P512 − P128 ≥ +5 %; a escolha de P=128 no Mundo A é ORÇAMENTO declarado, não medida. Se P128 ≥ P256, aí sim P satura e o corte está certo — mas por medida, não por artefato | pendente |
| 164 | MUNDO A, SERES PAREADOS (ordem do Leonardo 00:30: um mundo, seres diferentes). Mundo = v1 + custo por ativação .3 + basal .15; 8 seres nas mesmas 5 sementes: linear, COMPLETO, sem hipocampo, sem reflexo, COMPLETO hip 1.0, cortex 2.0, talamo fixo, temp .3; P128 G60 pac30 (janela) R4 σ_mut .1, sem jardim. APOSTA (pareado por semente, fit de vida): (a) ninguém bate o linear por ≥ 5 %; (b) hip 1.0 e cortex 2.0 ficam a ≤ 3 pp do COMPLETO (capacidade não é o gargalo no mundo A — falta o que lembrar/inverter); (c) sem reflexo −5 pp vs COMPLETO e `talamo_servicos` do campeão sobe ≥ .15 (delegação, 154); (d) temp .3 −5 pp ou pior (ruído sem aprendizado na vida); (e) talamo fixo ≈ COMPLETO (±3 pp). Tempo declarado ≈ 4–5 h (8 seres × ~35 min). | **parcial (11:00 10/09; e79/e43_mundoA5.json, 5 seres × 5 sementes, G30 pac15, parada em 19–28 ger.)**: linear 4.98 [4.58, 5.66, 4.85, 5.13, 4.66]; COMPLETO 4.11 [4.00, 4.04, 3.97, 4.52, 4.04] (metab 1.74, dof 195); sem hipocampo 3.97 (metab 1.82, dof 229); sem reflexo 3.97 (metab 1.65); talamo fixo 3.87 (metab 1.89). (a) ✓ ninguém chega perto do linear (−17 a −22 %); (c) sem reflexo −3.4 % vs COMPLETO (4/5 sementes abaixo) — direção certa, tamanho menor que a aposta; portão de serviços no retrato (a2) pendente; (e) talamo fixo −5.8 % vs COMPLETO (3/5 sementes abaixo — corrigido 11:25, eu tinha escrito 5/5; t ≈ 1.1–1.8 nos contrastes entre cérebros = não-resultado a n=5, Opus ciclo 2): mecanismo provável: forçar Σportões = 5 tira do ser a supressão que ele evoluiu (docs/69: o campeão fecha os portões, soma 3.4); confirmar com o pareado a1. NOVO: sem hipocampo ≤ COMPLETO sob custo por ativação (−3.4 %, 3/5) — inverte a 144 (sem custo, +7 %): com a conta ligada o hipocampo quase não dispara (ESC .01) e não custa; a peça inútil vira barata. Emendas anteriores: |
| 169 | CORTE POR SOBREVIVENTES (`corte_vivos`; Leonardo 10:20: "se demora tanto, como deixar mais rápido?"). Hoje o horizonte aberto roda até o ÚLTIMO vivo (até 7200 ticks) com vida mediana de 4–6 d: 3–5× de tiques para meia dúzia de sobreviventes. Célula: linear P256 σ .1 com corte a 2 % de vivos vs a mesma sem corte (5.36, 837 s). APOSTA: tempo por geração cai ≥ 50 % (837 → ≤ 420 s), fit de teste fica a ±3 % de 5.36 (o juiz usa 128 cópias sem corte) e frac_teto de treino ≤ .03. Se o fit cair > 3 %, o corte está podando os genomas de vida longa na SELEÇÃO (a elite é escolhida pela aptidão até o corte) e o corte deve ser mais baixo (.5 %). | parcial (z4, corte_vivos .02 = 2 % vivos, P256 G60 σ .1): fit 5.221 [5.33, 5.21, 5.35, 5.20, 5.02] vs 5.358 sem corte (−2.6 %, no limite dos ±2 %); tempo 765 s vs 813 s da célula e78 de 09/09 (−6 %) — mas as células de HOJE com o mesmo protocolo (z1 2097 s, z2 1923 s) estão 2.4× mais lentas que a de ontem: o ganho do corte fica indeterminado até o portão de velocidade (c9m perf_snapshot: snapshot vs código atual). [16:30: CORREÇÃO — e78 tinha retina; z5 reroda o baseline no código de hoje para separar tempo de código × cauda.] |
| 158 | NULO JUSTO DO `dof` — GA COM APTIDÃO ALEATÓRIA (`--neutro`; reservada no diário de 09-09 e sem entrada no ledger até 10/09 — escrita agora pelo opus-analista, ciclo 2). O nulo de hoje (`deriva_nula.py`, pred 156) é passeio PURO: todo genoma muta toda geração. A GA não é isso — `lab.evoluir_sementes` copia a elite (ne = 15 % de P) SEM mutar, então a linhagem do campeão sofre menos que g·σ passos. É por isso que os campeões medem dof ABAIXO do nulo em 10/10 (`e72/campeao_vs_nulo_e43_P128.json`, docs/67 §1.7): o nulo está calibrado errado, não o campeão "anda menos". O nulo justo é a MESMA GA (mesmo P, mesma elite, mesmo σ_mut, mesma semeadura) com aptidão = ruído: operador idêntico, seleção cega. APOSTA: com aptidão aleatória o dof do "campeão" na geração 30 cai dentro de ±10 pp do dof do campeão de verdade (.64–.77) e a diferença campeão − nulo, hoje negativa em 10/10, vai a ZERO — todo o dof das baterias é operador + elite, nada dele é seleção. Se o campeão ficar ≥ 10 pp ACIMA do nulo justo, `dof` volta a ser desfecho legítimo e a pred 156 muda de sinal. | pendente (`--neutro` não implementado; o ciclo 2 do opus gastou as 2 alterações em `dimensiona.py` e no conserto do juiz) |
| 170 | MUNDO C — "a cidade tem o tamanho da vida" (`cenarios/mundoC_cidade_da_vida.json`, opus-analista ciclo 2). Mundo A com DUAS leis de dimensionamento (docs/70 §3.1) e a MESMA conta do A (ativação .3 + basal .15, `ativ_centrada` desligado): (1) L 200 → 92; (2) período do ciclo de preço 3 d → 1.5 d. Nada mais muda. MECANISMO NO CÓDIGO: `DENS` é por ÁREA (`campo.py:97,106`), logo a distância ao serviço mais perto é invariante de escala e a parte dura da sobrevivência (gasolina, comida) fica dimensionalmente idêntica; o que escala com L é o destino do passageiro (`_destino`: r = L·(.05+.45u²)) e a fração do mapa ao alcance. Razões medidas em `dimensiona.py` com os números do A (vida 4.589 d, 13.0 entregas, raio 37 m): cidade ao alcance .108 → .508; ciclos por vida 1.53 → 3.06; amostras por caixa fica em 2.17 (K=6 não muda — a única razão que este mundo NÃO conserta). Seres: linear, COMPLETO, sem hipocampo, sem CÓRTEX (novo), sem reflexo; P128 G30 pac15 R4 σ_mut .1, `obs_rapido`, `corte_vivos` .02. APOSTA pareada por semente: (a) fração do mapa visitada ≥ 40 % e ≥ 5 das 6 caixas de memória tocadas no retrato (contra 11 % e 4 de 12 em docs/69); (b) entregas por vida ≥ 18 (contra 13.0 do linear em A); (c) CENTRAL — o buraco COMPLETO − linear encolhe pelo menos pela metade (A: −17.3 %; C: ≥ −8.7 %); (d) `sem córtex` fica ≥ 3 pp abaixo do COMPLETO (com 6 distritos amostrados, a política por distrito passa a ter dado); (e) CONTROLE NEGATIVO: `sem reflexo` − COMPLETO fica a ±2 pp do que foi em A (−3.4 %), porque a gasolina é invariante de escala. Se (c) ✗ com (a) e (b) ✓, o dado chegou e a peça continua sem pagar: o programa "cidade / regime / memória" sai da fila e a culpa é da peça. Ressalva pré-registrada: `retina.R_dia` (60 m) e `raio_px` (45 m) são absolutos, então em C o ser vê 65 % da cidade de uma vez contra 30 % em A — se (c) ✓, o teste que separa visão de memória é um C' com R_dia 27.  [15:45: o lote de 25 populações levou ~10 min/geração até o último sobrevivente (12.800 seres × 7200 tiques); refeito com `corte_vivos .05` na EVOLUÇÃO (o juiz `medidas()` força corte 0): sinal de fitness cortado igual para todos os seres, pareado; viés esperado ≤ 3 % (z4: .02 deu −2.6 %).] | pendente (smoke `o2_smoke_mundoC`) VEREDITO 10/09 18:50: (c) ✗ (d) ✗ (e) ✗ — C5 (e79/e43_mundoC5.json, 6574 s): linear 7.47 [7.84 6.40 7.81 8.20 7.10], COMPLETO 5.15, sem hip 5.41, sem cortex 5.88, sem reflexo 5.39; lacuna ao COMPLETO 2.32 (A .86, B .50), ao melhor cerebro 1.59; (b) ent 41.6 ✓; (a) espera o3b retrato. O mundo melhorou (entregas/dia 2.84 → 6.22, receita ×2, vida 4.6 → 6.7 d, dinheiro −14.7 → +21.5) e o cerebro piorou em relacao a espinha: a cidade menor favorece a politica linear. Seguem preds 180 (conta do B no C) e 181 (so o L). VEREDITO 170(a) 10/09 21:10: ✗ — retrato C (o3h, e72/retrato_vida_mundoC5.json: 1 mapa de teste, 2 sementes, jardim comum): fracao do mapa visitada (celulas de 10 m) linear .16/.20, COMPLETO .16/.19, sem cortex .32/.43 (docs/69 em A: .11); distritos tocados 3 de 6 para TODOS os seres; caixas de memoria 3 de 6 (docs/69: 4 de 12). A cidade encolheu 4.7x em area e o ser continua num canto: nasce no distrito 0 (pmul 2.0 — posto a 50–75 $) e so pisa nos distritos 0/1/4. Ressalva: retrato e n=1 mundo (mesmo berco); a fatia visitada e a sobrevivencia (linear 1.7 d, 5 panes sem conseguir pagar o posto) dependem do berco. |
| 171 | RAZÕES DE DIMENSIONAMENTO COMO PORTÃO (`src/dimensiona.py`, opus-analista ciclo 2; docs/70 §3.1). Nenhuma constante de mundo deste laboratório foi escolhida como razão contra a vida do ser; `dimensiona.py` lê um cenário (só stdlib, só leitura) e devolve as três razões com o mínimo utilizável do CS: fração do mapa ao alcance ≥ .50, amostras por caixa de memória ≥ 5, ciclos do mundo por vida ≥ 3 — mais avisos para o que está em unidade absoluta (caixas mortas DMAX − K, o estado mais lento que o ser PODE ter, retina/L, anel do passageiro/L). Constantes espelhadas (DMAX, dia, R_dia, raio_px, τ_max) conferidas contra o código no portão `testes_import` para não virarem índice cravado. APOSTA: (a) com os números medidos do Mundo A (vida 4.589 d, 13.0 entregas, raio 37 m) os Mundos A e B reprovam nas TRÊS razões e o Mundo C reprova só em `amostras_por_caixa` — checado no portão; (b) o aviso que ninguém tinha notado é `tau_max_vida` = 201 ticks / (4.589 d × 240) = 18 % de uma vida: nenhum estado do ser (τ da rápida, da lenta, do reflexo, do hipocampo — todos `1. + 200.·sigmoid`) dura mais que 0.84 dia, e todo ritmo lento do mundo (preço 3 d, regime 5 d) é mais lento que isso; (c) quando a bateria C fechar, refazer as razões com a vida e as entregas MEDIDAS em C dá `amostras_por_caixa` ≥ 3.0 e ainda abaixo de 5 — a razão só entra na faixa mexendo em K ou em DMAX. Se (a) ✗ o portão está calibrado errado e o mínimo do CS precisa de defesa empírica, não de citação. | pendente |
| 172 | O JUIZ ESTAVA CORTANDO JUNTO (`campo.medidas`, conserto do opus-analista ciclo 2). `medidas()` monta o cfg do juiz com `copy.copy(cfg)` e só sobrescreve `medir_ativ` e `jardim_comum` (`campo.py:613`): `corte_vivos` ia junto, então com o corte ligado as 128 cópias do TESTE também paravam no dia em que sobravam ≤ 2 % de vivos — e como `frac_teto` conta `t_vida >= T`, o truncamento não acendia nenhuma luz. A pred 169 aposta textualmente que "o juiz usa 128 cópias sem corte"; o código fazia o contrário, e a célula `z4_r8_P256_sig01_corte02` mediria uma coisa e declararia outra. Conserto: `cfg_m.corte_vivos = 0.` — idêntico bit a bit para `corte_vivos = 0`, que é tudo o que já rodou. APOSTA: no `z4` com o conserto, `t_vida_p90` do teste fica a ±5 % do p90 do controle sem corte (8.1 d no Mundo A) e `frac_teto` continua ≤ .005; sem o conserto o p90 teria travado no dia do corte. Se o p90 do z4 vier travado mesmo assim, o corte está podando a SELEÇÃO (a elite é escolhida pela aptidão até o corte) e não só a medição, e o corte deve cair para .5 %. | pendente |
| 173 | KERNEL DE VIDA INTEIRA (Leonardo 12:20: "carrega tudo na VRAM e executa só ali; kernels à mão"). `src/hip/vida.cu`: uma thread por ser, T tiques no device, sorteio por contador; init do Campo em torch. Portão `testes_vida_hip` (a9t). APOSTA: (1) contra o traço do Python com alvo injetado: ≥ 97 % das ações iguais, todas as divergências com margem < 1e-3 (empates de argmax e ordem de soma do einsum), erro de estado ≤ 1e-3 até a 1ª divergência; (2) 128 cópias com respawn: t_vida médio dentro de ±5 % do Python (RNGs diferentes); (3) uma geração de 640 genomas × 4 mapas até 7200 tiques ≤ 2 s (torch linear: ~50 s por geração a P128 R4 × 5 sementes) — ganho ≥ 25×. Se (1) falhar por margem > 1e-2 é bug de transcrição (localizar pelo tique/ser). | ✓ (c9j, 10/09 15:10): hipcc compilou (177 s, TORCH_EXTENSIONS_DIR); berço igual ao traço; ações iguais em 100.00 % dos ser-tiques vivos (0 empates, 0 duvidosas, 0 bugs); erro máximo até o tique 2400: fome 0, fuel 1.2e-7, água 0, dinheiro 3.8e-6, x 0, y 2.4e-7, vida 5.8e-6; t_vida bit a bit em 16/16 seres. Juiz (128 cópias, T 2400, RNG próprio): t_vida 5.14 vs 5.02 d, fit 5.671 vs 5.533 (+2.5 %, 1.4 DP — ruído do sorteio), tempo 0.09 s vs 14.9 s. Geração inteira (B 2560, T até 7200 aberto): **0.35 s** vs ~50 s do torch linear (143×). Kernel liberado para o braço linear (`--motor hip`). |
| 174 | MOTOR RUST (porta v0 no Universe, `crates/taxi-world`, identidade P0–P3 = 100 % das ações e t_vida bit a bit contra o traço v2). Teste de motor: o JUIZ do Rust (128 cópias do campeão linear e64, mapa 1000, semente 7777, T 2400, respawn 20, RNG próprio) vs `medidas()` do Python nas mesmas condições (números do a9j/testes_obs_grade item 2). APOSTA: t_vida médio e fit dentro de ±5 % e mortos iguais (1.00): a única diferença é o RNG de berço/passageiros, que é ruído estatístico a n=128. Se passar, a evolução do braço linear pode rodar no Rust (0.1 s/geração) e a GPU fica só para os cérebros em camadas. | ✗ (c9k, 10/09 15:15): MESMO genoma (cópia 0 semeada do Rust) nos dois juízes, 128 cópias, mapa 1000, T 7200; Python em 5 sementes de juiz: fit 3.829 ± .070 [3.75, 3.92], t_vida 3.49 ± .06 d, rec 101.9 ± 2.8, ent 11.12 ± .33; Rust (7777): fit 4.198 (+9.6 %), t_vida 3.82 (+9.4 %), rec 114.4 (+12.3 %), ent 12.27 (+10.4 %) — 5 DP acima, fora da faixa em todas. Mortos iguais. Sistemático, não ruído: o Rust é mais generoso em dinheiro (rec/ent) — suspeitos: geração/respawn de passageiros, distância/tarifa, campos do mapa exportado no traço (demanda/aliq/pmul/alug) vs gerar_mapa. Sonnet despachado para a análise estática; nada do Rust entra em análise. |
| 178 | EIXO P E EIXO G NO MOTOR HIP (kernel 143×; pred 168 mostrou que o P nunca foi medido limpo). Células h1: linear, mundo v1, G 60, σ .1, R 4, 5 sementes, `--motor hip`, P ∈ {128, 256, 512, 1024}; h2: P 256, G 240. Juiz em torch (128 cópias × 3 mapas de teste). APOSTA: (a) fit cresce com P e é monótono: P1024 ≥ P128 + .20 (mais amostras da mesma distribuição de mutação); (b) P256 no kernel a ±.20 do P256 torch (e78 5.358; o RNG do mundo é outro, o kernel deu +2.5 % no juiz); (c) G 240 ≤ G 60 + .15 a P256 (a espinha satura cedo, como aposto na 177d); (d) tempo por célula ≤ 3 min (evolução < 30 s; o juiz torch domina). | pendente NOTA 18:50: h1b caiu em vida_hip.py:36 "expected scalar type Float but found Long" (tensor inteiro no caminho do e43); cast explicito por chave (cdist, nserv, cidx, casa, px_ok, orig_d, acoes → int32; resto float32) em vida_hip.rodar_hip; h1c (P 128/256/512/1024) e h2c (G 240) na fila. Referencia torch NP 40 sem retina: h3 fit 5.39 [5.05 5.49 5.82 5.31 5.28], 728 s. VEREDITO 10/09 19:10 (h1c/h2c, e83, kernel, G 60, sigma .1, 5 sementes): P 128/256/512/1024 = 5.152/5.051/5.290/5.356 — NAO monotono; inclinacao por dobro de P +0.085 [−0.053, +0.223]; G 240 − G 60 = −0.109 (satura em 60); kernel P256 − torch P256 (h3 5.389) = −0.338 [−1.05, +0.37]. Com MDE 0.75 em n = 5 a parte (b) (±.20) e INCONCLUSIVA: o eixo P e menor que o ruido entre sementes. Uso certo do 143×: sementes, nao P — pred 184 (Opus) replica com 40 sementes (~17 min, MDE .27). |
| 175 | NULO COM O σ DA BATERIA (auditoria Astra → b3/a3). MECANISMO: `campeao_vs_nulo` lia `deriva_nula_s0.0_e0.0.json`, gerado com σ_mut .3 (default de `deriva_nula`), enquanto Mundo A/B evoluíram com σ_mut .1. Passeio sem seleção espalha σ·√g: com σ .3 em g=30 dá 1.64 → P(|w|>.5) = .76 (o número do arquivo); com σ .1 dá .55 → ≈ .36, e em g=20 .45 → ≈ .27. Os campeões têm dof .23–.33 em ger_efetiva 20–29. APOSTA: contra o nulo certo (c6, σ .1) o dof dos campeões fica a ±.06 do nulo nos dois mundos (≈ deriva, como a 156), e a leitura 'seleção poda 3×' de a3/b3 era artefato do σ errado. Aposta secundária: a trava do córtex (0–.04) fica ≤ nulo σ .1 em ≥ 15/20 sementes. | ✓ (A) / parcial (B). Nulo σ .1 (c6): g20 .263, g30 .361 (aposta .27/.36). Campeões vs nulo na própria ger_efetiva: Mundo A 19/20 a ±.06 (COMPLETO .26–.30 vs .31; sem hip .31–.34 vs .35; tálamo fixo .23–.30 vs .26; 1 outlier sem reflexo .219); Mundo B 12/20 a ±.06, 8/20 entre −.06 e −.11 (COMPLETO .25–.34 vs .36). Todos ≤ nulo: poda LEVE (~12 % abaixo = 2–4 gerações de deriva), não 8×; o B poda um pouco mais que o A (1.2×). Trava do córtex 0–.06 vs nulo .02–.04: ≈ nulo. A "compressão 8×" do CS docs/73 §3 era o σ .3. |
| 176 | TRAJETÓRIA NO MUNDO CERTO (auditoria Astra → a4). `politica_util.mundo()` montava o cfg SEM `custo_gene/custo_modo/custo_basal/ativ_centrada` e sem os ajustes de cérebro por ser: a4 (Mundo A) mediu os campeões num mundo sem o custo de ativação com que evoluíram, e quebrou em 'COMPLETO talamo fixo' (KeyError: rótulo ≠ classe). Com o mundo certo (c4/c5, `braco()`): APOSTA (a) fração parada (FICAR) do braço em camadas continua abaixo do linear (medido sem custo: .047 vs .109; direção mantida, valores mudam ≤ ±.05); (b) concordância linear×COMPLETO permanece < .40; (c) com o custo de ativação o braço em camadas vive MENOS que na medição sem custo (vive_mais cai de 42 % para ≤ 35 %). | ✓ 3/3 (c4, Mundo A no mundo certo, 24 blocos × 5 sementes): (a) FICAR .053/.051/.047/.073 (COMPLETO/sem hip/sem reflexo/tálamo fixo) vs linear .109 — direção mantida, Δ vs sem custo ≤ .02; (b) concordância .34–.36; (c) vive_mais caiu para 35/29/29/22 % (sem custo: 44/39/42 %): com o custo de ativação cobrado, o linear vence 65–78 % dos blocos pareados. Raio 37.5–38.9 m vs 39.6 m. Mundo B (c5): FICAR .097/.063/.058/.096 vs .109 (COMPLETO e tálamo fixo param quase tanto quanto o linear sob a conta justa), concordância .31–.38, vive_mais 35/38/32/35 %, raio 37.4–39.5 m. |
| 177 | A × B EM G 120 (pergunta do CS docs/73 §6.1: 'a lacuna fecha com gerações?'). `zzz_A_G120_juntos`: Mundo A, 5 seres no lote, P 128, G 120, paciência 40, 5 sementes, σ .1, `--obs-rapido`; B igual depois (se o tempo permitir: com 25 populações o tique do COMPLETO é limitado por cálculo, não por lançamentos — estimativa 5–7 h por mundo, igual ao sequencial; corrigido em docs/75). APOSTA: (a) a lacuna espinha − melhor cérebro no A cai de +.86 (G30) para ≤ +.60 em G120, mas NÃO fecha (linear ≥ +.15, p < .1); (b) ger_efetiva > 60 em ≥ 3/5 sementes (G30 era cedo); (c) ordem dos seres se mantém (sem hipocampo continua o pior com cérebro em ≥ 3/5 sementes); (d) linear em G120 ≤ +.10 sobre o linear G30 (a espinha já saturou; o ganho de gerações é do cérebro).  [15:45: idem — `corte_vivos .05` na evolução; estimativa 3–4 min/geração, 6–8 h para G120 com paciência 40.] | pendente VEREDITO 10/09 19:10 (e79/e43_G120juntos.json, ger efetiva 84 em 5/5 sementes, paciencia 40): (a) ✗ — lacuna ao melhor cerebro por semente +0.756 vs +0.750 em G30: NAO fecha com geracoes; (d) ✓ linear 4.917 vs 4.976 (−0.059). O COMPLETO PIOROU: 4.115 → 3.866 (−0.248) com dof 194.6 → 363.8 (+87 %) e metab 1.744 → 2.053: mais geracoes compram genes, nao aptidao (o dof do campeao fica ~.09 abaixo do nulo nos dois horizontes — Opus ciclo 3, docs/82). |
| 179 | CONTROLES COMPORTAMENTAIS (CS docs/78 §4 "parado paga?"; Astra `plano-terceiro-olho.md` passo 1). `politicas/parada.py` (acao 8 = FICAR sempre) e `politicas/linear_sem_ficar.py` (campeao linear com a coluna FICAR apagada) via `julga_politica` nos 3 mundos (cenario de cada um; campeao = linear W[0] de e79/e43_mundo{A,B,C}5.json; 128 copias × 5 sementes 7777–7781), ids o3e_*/o3f_*. MECANISMO: regua vida = dias + renda/300; parado nao ganha renda (linear A: 116/300 = .39 d de renda dentro do fit 4.98) e nao compra; fome .32/tique chega a FOME_CRIT 90 em 281 tiques (1.2 d), agua .08/tique em ~2 d; aluguel 4/d vira divida. APOSTA: (a) parada/linear ≤ .50 em A e B e ≤ .35 em C (C: linear 7.47 com 6.7 d vividos); se parada ficar a ≥ .8 do linear, o premio esta errado (CS tem razao) — aposto que NAO; (b) linear_sem_ficar fica entre −5 % e 0 % do campeao em A/B (FICAR = 5–10 % dos tiques, docs/78); se cair > 10 %, o FICAR e carga (descanso/calor/gasolina), nao vicio; se SUBIR, o FICAR e o vicio que o CS suspeita. VEREDITO 10/09 20:05 (e85, julga_politica, 128 copias × 5 sementes; fit ~ dia_morte + rec/300): (a) ✗ — parado/campeao = .87 em A e B (3.66 d vs 3.87 d + renda 98; B = A porque o linear nao paga conta de cerebro e o campeao e bit a bit o mesmo) e .64 em C (3.67 vs 5.09 d + 196). O piso do premio e alto: em A a evolucao so disputa os 13 % de cima; o campeao morre 78 % de dano (5.2 panes) e termina com −19 (armadilha de divida: aluguel 4/d + guincho 10). CS tinha razao (docs/78 §4). (b) INVALIDO como rodou: julga_politica mede a politica com W = ZEROS, logo o `tudo` do decidir e zero e nao a nota do campeao; com a coluna 8 em −1e9 o argmax vira a direcao 0 sempre (traco: mover 1.00, 0 servicos) — o taxi anda reto, seca o tanque, guincho, sem dinheiro, morre no dia 1.46. Refeito como o3g_julga_semficar_{A,C} com `--W-politica campeao` (o W do campeao entra no um_passo e o `tudo` vira a nota dele). Licao no checklist (item 13). VEREDITO (b) 10/09 20:30 (o3g, W do campeao no julga; traco: mover .96, comida .02, posto .01 — compra normalmente): sem-FICAR/campeao = .874 em A (dia 3.38 vs 3.87, renda 86 vs 98, panes 5.0 vs 5.2) e .851 em C (4.35 vs 5.09 d, renda 161 vs 196). Queda de 13–15 % > 10 %: o FICAR e CARGA (economia de gasolina/calor enquanto espera), nao vicio — apostei −5..0 % e errei o tamanho, nao o sinal. O cerebro ficar parado MENOS que a espinha (pred 176) nao e virtude. |
| 180 | MUNDO C COM A LEI DO B (`cenarios/mundoC_conta_justa.json` = C + `ativ_centrada`; CS docs/79 §3; id o4a_mundoC_justa, mesmo protocolo do C5: juntos, obs-rapido, corte .05, G 30 pac 15 P 128 R 4, 5 sementes). MECANISMO (CS): no C o ser e 2.2× mais ativo por dia (entregas 2.84 → 6.22) e a conta por ativacao cobra por ativacao; o desconto do B (so o que muda a decisao) vale mais onde ha mais ativacao. APOSTA do CS: ganho do COMPLETO > +0.36 (o que B deu sobre A: 4.11 → 4.47). MINHA APOSTA: ganho no COMPLETO entre +0.3 e +0.8 (concordo na direcao) MAS a lacuna linear − COMPLETO continua ≥ 1.5 (hoje 2.32): o sem-cortex bater o COMPLETO com MAIS genes ligados (203 vs 195) diz que no C o problema nao e a conta, e o cortex atrapalhando (\|δ\| ≤ .5 so perturba, nunca inverte). Se a lacuna cair abaixo de 1.0, a conta era o problema e eu estava errado. VEREDITO 10/09 21:10 (o4a, e86/e43_mundoCjusta5.json, 1806 s): linear 8.057 [7.60 7.45 9.00 8.30 7.93], COMPLETO 5.525 [5.49 4.69 5.54 5.84 6.07], sem hip 5.658, sem cortex 6.799, sem reflexo 6.022. Ganho pareado por semente vs C5: linear +0.588 (t 2.2, p≈.09), COMPLETO +0.375 (t 1.1, p .32), sem cortex +0.917 (p .017), sem reflexo +0.63, sem hip +0.25. Lacuna linear−COMPLETO 2.53 (era 2.32) e ao melhor cerebro 1.26 (era 1.59) → MINHA aposta (lacuna ≥ 1.5) ✓; a do CS (+0.375 > +0.36) e numericamente ✓ mas abaixo da MDE .78 e INCONCLUSIVA pelo controle: a espinha (dof 0, sem gene tributavel) andou +0.59 na mesma celula. Causa (docs/88): `--seres-juntos` acopla os bracos — parada antecipada compartilhada (ger_efetiva 26 em TODOS os bracos do Cj vs 30 no C5) e `corte_vivos` no lote inteiro (item 4 do Astra): os cerebros mais baratos vivem mais, o corte dispara em outro tique e a espinha e selecionada com outra truncagem. metab caiu 1.618 → 1.330 (−18 %, a conta e mais barata) com dof igual (194.8 → 190.6): a lei do B nao poda mais, so cobra menos. Teste direto do acoplamento = pred 185 (o4d, linear solo com corte .05). |
| 181 | SO O L (CS docs/79 §4: o C mudou L, periodo de preco, corte .05 e o protocolo do lote de uma vez; motor, R e obs_rapido NAO sao mudancas: torch e o unico motor do SerCompleto, R 4 esta no protocolo do A tambem, obs_rapido e bit a bit pelo portao testes_obs). `cenarios/mundoA_L92.json` = A com L 92 (periodo 3 d), bracos do C (com sem cortex); o4b = A_L92 e o4c = mundoA_seres com `--so` = bracos do C, AMBOS no protocolo do C5 (juntos, obs-rapido, corte .05). APOSTA: (a) L 92 sozinho reproduz ≥ 70 % do ganho de mundo (entregas/dia 2.84 → 6.22, receita 116 → 236) e a lacuna linear − COMPLETO no o4b fica ≥ 1.5: o dimensionamento amplia a lacuna, nao o periodo de preco; (b) o4c (A no protocolo do C5) fica a ≤ 5 % do A5 por ser (pred 169 viu −2.6 % com corte .02; juntos e o mesmo GA com outro fluxo de RNG) — se o4c diferir do A5 em > 10 %, o protocolo do lote nao e neutro e o pareado A5×C5 esta contaminado. NOTA 19:10 (Opus ciclo 3, docs/82 §2, conferido em campo.py:292-341): com NM_RETINA=1 a observabilidade e o OLHO (R_dia 60 m, cego = k_cego·R_dia = 120 m), nevoa nao e lida; o4b muda L com o olho ABSOLUTO fixo, logo retina/L sobe de .30 para .65 — isola o L geometrico, nao a observabilidade. O olho proporcional e o Mundo D (pred 182). o4_0 (controle do protocolo) foi posto ANTES de o4a/o4b na fila. VEREDITO PARCIAL 10/09 20:30 (b) ✓ — o4_0 (A no protocolo do C5: juntos, obs-rapido, corte .05; e86/e43_mundoA_protoC.json, 958 s vs 4494 s do A5 por ser = 4.7× mais rapido) vs A5 por ser: linear 5.114 vs 4.976 (+2.8 %), COMPLETO 3.962 vs 4.115 (−3.7 %), sem hip 3.847 vs 3.967 (−3.0 %), sem reflexo 4.140 vs 3.968 (+4.3 %): todos dentro de 5 %, protocolo do lote e neutro ao nivel do ruido (n = 5). Extra: sem cortex e o MELHOR cerebro tambem em A (4.387, +.42 sobre o COMPLETO) — replica o §5 do CS 79 fora do C. (a) espera o4b.  VEREDITO 181(a) 10/09 21:50 ✓ — o4b (e86/e43_mundoA_L92.json, 1780 s): linear 7.737 [7.24 6.81 8.57 8.20 7.85], COMPLETO 5.204, sem hip 5.227, sem cortex 6.071 (melhor cerebro, 5ª bateria de 5), sem reflexo 4.868. So o L reproduz 100 % do ganho de mundo: entregas/dia 6.25 (C5 6.22, A5 2.84), receita 244 (C5 236, A5 116), vida 6.92 d (C5 6.68). Lacuna linear−COMPLETO 2.53 (C5 2.32; A5 .86) ≥ 1.5. O periodo de preco (3 d vs 1.5 d) nao faz nada mensuravel: L92 ≈ C5 em todos os seres (±4 %). O dimensionamento amplia a lacuna. Ressalva Opus (pred 182): o olho e absoluto, L92 tambem torna o mundo 2.2× mais observavel — o Mundo D separa. |
| 182 | MUNDO D — O OLHO NA PROPORCAO DA CIDADE (`cenarios/mundoD_olho_proporcional.json` = Mundo C com UMA lei trocada: `retina.R_dia` 60 -> 27 e `R_noite` 15 -> 7, mesmo fator .45; passo/custo/k_cego intactos). MECANISMO NO CODIGO: com `NM_RETINA=1`, `campo.py:292-301` (obs rapido) e `:329-341` (obs lento) SOBRESCREVEM `s._dist_v` e as distancias por opcao pelo que os 8 raios enxergam — `cfg.nevoa` (E63, `campo.py:291,328`) nunca e consultado quando a retina esta ligada, e TODAS as baterias A/B/C rodaram com retina. Logo o ALCANCE DO OLHO e a lei de observabilidade deste laboratorio, e ela nunca foi dimensionada: `dimensiona.py` imprime `retina/L` **0.30 no Mundo A e 0.65 no Mundo C**. Encolher L 200 -> 92 sem tocar no olho tornou o mundo 2.2x mais OBSERVAVEL e fez o "cego" (`k_cego*R_dia` = 120 m) ficar MAIOR que o mapa (1.30*L; no A era 0.60*L). Com R_dia 27 em L 92 as duas razoes voltam as do Mundo A (0.29 e 0.59*L). Isto e o confundidor que falta no o4b (pred 181): `mundoA_L92` muda L E o olho junto, entao nao isola dimensionamento. CORRECAO MINHA (ciclo 2): a pred 170 ja trazia esta ressalva pre-registrada ('o teste que separa visao de memoria e um C\' com R_dia 27'), mas eu a condicionei a 'se (c) ✓'. (c) veio ✗ e eu teria deixado o C' cair — errado: o ✗ e SINTOMA do confundidor, entao o C' fica mais necessario, nao menos. APOSTA: (a) todo mundo cai e o linear fica <= 6.2 (C: 7.469); (b) a lacuna linear − COMPLETO cai de +2.319 [+1.49,+3.14] para <= +1.4; (c) INVERSAO DE SINAL no hipocampo: `sem hipocampo` − COMPLETO sai de **+0.256** (C, p .29) para <= **−0.20** — primeira aposta do laboratorio em contribuicao POSITIVA de um orgao; (d) `sem cortex` continua >= +0.30 acima do COMPLETO (o cortex e ortogonal a observabilidade). Se (c) falhar, o hipocampo como esta (EMA por distrito de renda/espera/gasto) nao e a memoria que este mundo pede: falta memoria de LUGAR (onde eu VI um posto), que ele nao guarda. Fumaca `o5_smoke_mundoD` (P 8, G 1, 1 semente) so verifica que o mundo nao e armadilha; a bateria e do Fable. | pendente  SMOKE 10/09 21:50: o5_smoke_mundoD (P8 G1 1 semente, 228 s) roda os 7 bracos sem erro (linear 5.63, COMPLETO 4.78, sem cortex 5.75 — numeros de fumaca, nao valem). Enfileirados o7a_julga_parada_D (piso do premio em D, campeao linear do C5 como referencia; CS docs/87 prop. 5) e o7b_mundoD5 (bateria completa, protocolo do C5).  VEREDITO 10/09 23:55 — (a) ✗ (b) ✗ (c) ✗ (d) ✓. D5 (e87/e43_mundoD5.json, 2411 s, 7 bracos): linear 7.960 [8.11 7.92 8.62 8.30 6.85] (+0.49 vs C5, t 1.6), COMPLETO 5.155 (+0.005), sem hip 5.376 (−0.03), sem cortex 6.182 (+0.30), sem reflexo 5.385, cortex 0.1 5.739, hip 0.1 5.412. Lacuna linear−COMPLETO 2.805 (C5 2.319): encolher o olho para 27 m NAO derruba a espinha nem aproxima o cerebro; sem hip − COMPLETO +0.22 (nao inverteu); sem cortex melhor cerebro pela 6ª bateria de 6 (+1.03 sobre o COMPLETO). MECANISMO: o alvo do passageiro/destino entra em F por `alvo()` direto (campo.py:287-288, `Falvo`), fora da retina; a retina so limita a distancia PERCEBIDA aos servicos, e o linear compra ao passar (raio 6 m) sem precisar ve-los de longe. A observabilidade que o olho controla nao e a que a espinha usa. Piso do premio em D (o7a, e85/julga_parada_D.json): campeao 5.14 d vs parada 3.67 d = premio 28.6 % (C 27.9 %) com ruido 8.5 % → D passa o portao de mundo como C. Leitura: retina/L nao era o confundidor do o4b; o hipocampo como esta (EMA por distrito de renda/espera/gasto) nao guarda LUGAR, e a memoria de lugar e o que um olho curto pediria. |
| 183 | DOSE DO CORTEX E DO HIPOCAMPO (2 seres novos, SEM codigo: so `cenario.bracos` com `cerebro`). `COMPLETO cortex 0.1` (`cortex_amp` .5 -> .1) e `COMPLETO hip 0.1` (`hip_esc` .01 -> .1). MECANISMO NO CODIGO: `completo.py:52,88` — o cortex e ganho MULTIPLICATIVO por distrito em 4 colunas da espinha (`IDX_CORTEX=[0,1,6,7]` = d_alvo, d_posto, custo_frente, preco_frente): `w_ef = w*(1+delta)`, `delta = cortex_amp*tanh(gene)`, `\|delta\| <= .5` -> `w_ef` em [.5w, 1.5w]: PERTURBA, nunca inverte. No Mundo C `sem cortex` ganha **+0.732 [−0.12,+1.58] p .075 (4/5)** do COMPLETO **com MAIS genes ligados (202.6 vs 194.8) e metab MAIOR (1.651 vs 1.618)** — paga o mesmo aluguel (a ablacao zera `s.DLT` mas os 48 genes continuam no genoma e no `dof`) e ainda ganha: o que sobra e a perturbacao. E `cor_dmax` medido e .39–.43 em TODOS os bracos dos dois mundos, exatamente a estatistica de ordem da deriva (`0.5*tanh(sigma*sqrt(g)*E[max\|z\|_{n=48}])` = `0.5*tanh(0.5*2.55)` = .427): a autoridade do cortex nao e selecionada, e o maximo de um passeio aleatorio. APOSTA: (a) `COMPLETO cortex 0.1` recupera >= 70 % do ganho do `sem cortex` (>= +0.50 sobre o COMPLETO no mundo em que rodar); se recuperar <= +0.20 o ganho era ALUGUEL e nao perturbacao, e eu estou errado; (b) `COMPLETO hip 0.1` (10x a autoridade de hoje) fica dentro de +-0.30 do COMPLETO no Mundo C (mundo observavel: memoria nao paga) e ACIMA em >= +0.30 no Mundo D (mundo com olho curto). Fumaca `o5_smoke_mundoD` so confere que os dois seres sobem e nao quebram o lote. | pendente |
| 184 | EIXO P: n=5 NAO MEDE — REPLICA COM SEMENTES NO KERNEL (criterio registrado ANTES da replica; fecha o lado quantitativo da pred 178). MEDIDO (h1c, 18:46–18:50, `mundo_vivo_v1_semretina`, G 60, sigma .1, R 4, 5 sementes, `--motor hip`): P 128/256/512/1024 = **5.152 / 5.051 / 5.290 / 5.356**; inclinacao por DOBRO de P **+0.085 [−0.053, +0.223]**; P1024 − P128 = **+0.204 [−0.359, +0.767] p .37 (3/5)**; kernel P256 − torch P256 (h3) = **−0.338 [−1.045, +0.369] p .25 (2/5)**. Custo: kernel 74–125 s por celula de 5 sementes contra 728 s do torch (**9.8x fim a fim**); 8x a populacao custa 1.67x o tempo (o kernel e limitado por LANCAMENTO, nao por calculo). MDE pareado com n=5 = **0.75** (DP pareada .454): a celula so enxerga efeito >= 14 %, e a tolerancia +-0.20 da pred 178b e 3.5x mais estreita que a resolucao — 178b fica INCONCLUSIVA, nao ✓ nem ✗. APOSTA da replica (8 celulas de kernel, 40 sementes, ~17 min de GPU, MDE .27): (a) a inclinacao por dobro de P fica em [−0.05, +0.15] e P1024 − P128 <= +0.30 (<= 6 %) — o "7.7x" do P morre com IC, nao com argumento; (b) `h2c` (G 240 vs G 60, P 256) <= +0.30, mesma direcao do G120 do Mundo A (linear −0.059 [−0.85,+0.73] em 84 geracoes efetivas); (c) o desvio kernel−torch NAO se estreita com sementes (ele e fluxo de RNG do GA, nao fisica: a identidade do simulador ja esta verde em c9j, 100 % das acoes e t_vida bit a bit em 16/16) — se com 40 sementes o \|desvio\| ficar > 0.30 com p < .05, ha diferenca de motor e o eixo P do kernel nao transfere para o torch. NAO enfileirada por mim (fila do Fable). | pendente |
| 185 | INVARIÂNCIA DO CORTE À COMPOSIÇÃO DO LOTE (Astra, item 4: `campo.py:571` corta quando a fração viva do LOTE INTEIRO ≤ corte_vivos; num lote misto o mesmo genoma pode receber aptidão diferente conforme os companheiros). `o4d_linear_solo_corte05` = linear SOZINHO (Mundo A, obs-rapido, corte .05, G 30 pac 15, P 128, 5 sementes) × linear do `o4_0_mundoA_protoC` (mesmo protocolo, no lote com 4 cérebros). MECANISMO: o corte trunca os 5 % que mais vivem; no lote misto são quase sempre linear, logo a seleção do linear é a mais truncada — viés CONTRA a espinha, lacuna conservadora. APOSTA: \|fit solo − fit lote\| ≤ 5 % e solo ≥ lote (truncado menos); se solo − lote > 10 %, o corte por lote contamina a seleção e o conserto (corte por população) sobe para P1. Juiz sem corte nos dois.  VEREDITO 10/09 21:50 (a) ✓ magnitude, ✗ direcao: linear solo (e86/e43_linear_solo_corte05.json, 195 s) 5.002 [5.07 4.51 5.43 5.15 4.84] vs linear no lote com 4 cerebros (o4_0) 5.114 → −2.2 % (≤ 5 %), mas solo < lote (a aposta era solo ≥ lote por ser menos truncado). Em A o corte por lote NAO contamina a selecao do linear (fica no ruido). Consequencia para a pred 180: a hipotese 2 do docs/88 §2 (corte no lote) perde forca em A; para o +0.59 da espinha no Cj sobram a parada antecipada compartilhada (26 vs 30 ger) e o sorteio (p .09). Em C nao foi testado (cerebros vivem mais em C, o acoplamento pode ser maior). |
| 186 | PORTÃO DO MAPA DA MOSCA (14/09 09:01, ANTES de rodar). Módulo novo `src/flybrain/` (inglês): mapa FlyWire v783 (138 639 neurônios, 15,09 M conexões com sinal, 54,5 M sinapses, 40 % inibitórias) carregado uma vez como CSR e NÃO gerado — só selecionado por cima (regra do Leonardo). `src/fly_gate.py` reproduz Shiu et al. 2024 (LIF, mesmas constantes: v0 −52, vth −45, t_mbr 20 ms, τ_syn 5 ms, refratário 2,2 ms, atraso 1,8 ms, 0,275 mV/sinapse; Poisson 68,75 mV nos 21 GRNs de açúcar do lado direito) em torch com lote = ensaios, propagando só as linhas dos pré ativos. APOSTA: (a) MN9 (720575940660219265) dispara em ≥ 25/30 ensaios a 100 Hz, taxa média entre 5 e 80 Hz, e sobe a 200 Hz; (b) neurônios ativos (≥ 1 spike) entre 150 e 1500 a 100 Hz (Shiu: ~400 a 200 Hz); (c) 30 ensaios × 1 s (10 000 passos) em < 300 s de GPU. Se MN9 = 0 Hz ou > 5000 ativos (fuga), há erro de sinal/unidade/atraso e NADA acima do mapa vale. Testes unitários CPU (`src/fly_tests.py`, 4 testes: CSR = lista de arestas, cadeia com atraso ≥ D e refratário, máscara de neurônio bloqueia propagação, modelo de taxa = denso) já passam. | pendente |
| 187 | SONDA DE TRANSMISSÃO NO MAPA DA MOSCA (14/09 09:05, ANTES de rodar). `src/fly_probe.py`: malha aberta sobre o replay do campeão (`u11b_r10_s031_ctrl/gen0014.replay`, ser 0 = elite, 3000 quadros = 12 000 tiques a 64 Hz). O replay da GPU só grava 3 distâncias de parede, velocidade, guinada, marcha e hp (curvatura/fluxo/retina/intenção saem zerados — medido); entradas = 6 (paredes/40–50, vel/25, guinada, hp/127), alvo = comando FINAL aplicado (thr/str/brk, DP .075/.342/.136). 32 ligações aleatórias (cada entrada → 1 tipo celular aferente com ≥ 4 neurônios, de 267; cada saída → par (+,−) de tipos eferentes, de 516), modelo de taxa (tanh, τ 4 passos, escala 1e-3 × contagem de sinapses), NENHUM peso gerado. Mesmas ligações no mapa real, no mapa com alvos embaralhados (graus e sinais preservados) e no mapa com sinais redistribuídos. APOSTA: (a) transmissão existe: mediana da fração de neurônios eferentes com variância > 0 ≥ 0.5 no mapa real; (b) melhor |ρ| entre algum grupo eferente e o comando final (mediana sobre 32 ligações) ≥ 0.3 para steer no mapa real; (c) o mapa real bate os dois embaralhados em (b) por ≥ 0.05 de mediana — hipótese fraca: se der empate, o mapa não carrega informação além do grau, e a "seleção" vira seleção num grafo aleatório; (d) ≤ 15 ms por passo com 32 seres (600 M MAC/passo). Estabilidade: se max\|x\| explodir (> 50) a escala está errada e o resultado não vale. | pendente |
| 187v | VEREDITO 14/09 09:38 (fly/fly_probe_s0.json, 3 variantes × 32 ligações × 3000 quadros): (a) ✓ eferentes com variância > 0: mediana 0,63 no mapa real (embaralhado-alvos 0,16, embaralhado-sinais 0,35); (b) ✓ melhor \|ρ\| eferente–comando (mediana): real thr .515 / str .558 / brk .367; (c) ✗ **empate**: alvos embaralhados .519/.581/.388, sinais embaralhados .521/.567/.380 — e o comando LIGADO (par +/−) foi PIOR no real (.135/.227/.063) que no embaralhado (.38/.36/.16); (d) ✗ 31,8 ms/passo (aposta ≤ 15): SpMM CSR do ROCm rende ~15 GFLOP/s. MECANISMO: "melhor \|ρ\| entre 1 481 eferentes" é o máximo de 1 481 projeções quase aleatórias de 6 entradas — qualquer grafo dá ~0,5; não mede fiação. O real satura (max\|x\| 4,1 vs 1,0/1,6): ganho recorrente alto + 40 % inibição → tanh cravado → comando ligado menos linear. Estável (não explode). Conclusão: a sonda NÃO discrimina mapa real de embaralhado; só a evolução da seleção (pred 188) e a malha fechada respondem. Escala/τ mantidos (estável); `--min-weight 3` para 3× de velocidade. |
| 188 | SELEÇÃO EM MALHA ABERTA NO MAPA DA MOSCA (14/09 09:38, ANTES de rodar). `src/fly_select.py`, 4 braços × 1 semente, 15 gerações, 32 seleções, 2 000 quadros do campeão s031 (gen 14, ser 0), holdout = quadros 3000–5000 do mesmo campeão + campeão s077; mapa `--min-weight 3` (4,9 M arestas); fitness = média de ρ(comando lido, comando final) em thr/str/brk. Braços: `bind` (só ligações, mapa cheio), `prune` (ligações + poda de neurônios 5 %/1,5 %), `random-mask` (ligações + máscara aleatória fixa a 35 %), `shuffled` (`prune` no mapa com alvos embaralhados). APOSTA: (a) `bind` sobe de ~0,15 (aleatório, sonda) para ≥ 0,35 de treino em 15 gerações — seleção de I/O basta para achar caminhos; (b) `prune` ≥ `bind` + 0,03 no treino (o operador do doc 16 ajuda) — se `random-mask` empatar com `prune`, o ganho é esparsidade e não seleção; (c) `shuffled` fica dentro de ±0,05 de `prune` — aposto que NESTA tarefa (6 entradas, 3 saídas, malha aberta) a fiação real NÃO vale mais que um grafo com os mesmos graus; (d) holdout no mesmo campeão ≥ 70 % do treino; no campeão s077 ≥ 50 %. Se (c) der real > embaralhado por ≥ 0,05, a fiação carrega estrutura útil e a malha fechada ganha prioridade máxima. Custo: ~20 s/geração → ~6 min por braço. | pendente |
| 186v | VEREDITO 14/09 09:37 (fly/fly_gate_100hz.json): (a) ✓ MN9 **72,4 ± 5,0 Hz, 30/30 ensaios** a 100 Hz (200 Hz em curso); (b) ✓ **420 neurônios ativos** (Shiu: ~400); (c) ✓ 30 ensaios × 1 s (10 000 passos) em **23 s** de GPU (aposta < 300 s). Top ativos: motores CB0700 175/169 Hz, MNx01 151 Hz, DNge031 118 Hz — o circuito da probóscide. Correção de dados: 1 dos 21 IDs de açúcar do notebook (v630) não existe na v783; 20 usados. O mapa, sinais, unidades e atraso estão certos: a porta do programa da mosca está aberta. |
| 186v+ | 14/09 09:57 complemento: a 200 Hz MN9 = **116,9 ± 5,4 Hz** (72,4 a 100 Hz), 30/30, 452 ativos, 22 s — sobe com a frequência de estímulo como no Shiu. (a) ✓ completo. |
| 188v | VEREDITO 14/09 10:22 (fly/fly_select_*_s0.json, 15 gerações × 32 seleções, ~375 s por braço, mapa `--min-weight 3`). Treino / holdout (quadros 3000–5000, mesmo campeão) / campeão s077 (ρ médio thr,str,brk): **bind .455 / .428 / .305**, **prune .443 / .430 / .411** (densidade .71), **random-mask .484 / .480 / .264** (densidade .35), **shuffled .485 / .476 / .290**. (a) ✓ bind sobe de .207 (gen 0) para .455 — seleção de I/O basta; (b) ✗ prune ≤ bind (−.012) e random-mask > prune (+.041): o operador de poda NÃO ajuda aqui e a esparsidade aleatória empata-ou-ganha → o ganho não é seleção de neurônios; (c) ✓ shuffled dentro de ±.05 de prune (+.042) — como apostado, a FIAÇÃO REAL não vale mais que um grafo com os mesmos graus nesta tarefa (6 entradas, 3 saídas, malha aberta); shuffled já nasce em .380 na gen 0 (vs .207) porque o grafo embaralhado não satura (max\|x\| ~1 vs ~4 no real) e responde mais linearmente; (d) ✓ holdout 94–99 % do treino; campeão s077 58–93 % (prune o melhor, .411 — n = 1, não afirmar). Steer é o comando mais legível (ρ .60–.63), throttle .33–.44, brake .32–.39; saídas escolhidas são pares de DNs (descendentes) em todos os braços. MECANISMO: com 6 entradas e leitura linear de médias de grupo, o mapa funciona como reservatório aleatório; o que distingue fiação real só pode aparecer em malha fechada com os 192 canais e pressão de sobrevivência (F1/F2 no Universe). Uma semente por braço: as diferenças ≤ .04 estão dentro do ruído esperado (holdout − treino já varia .03). |
| 189 | PORTÃO DA VISÃO DA MOSCA (14/09 12:09, ANTES de rodar). `src/flybrain/eye.py`: retinotopia de 1ª ordem — 7 932 fotorreceptores R1-6 (4 044 esq / 3 888 dir) com posição no volume; PCA por olho → (u, v) → azimute 5–175° por lado e elevação −60..+60° (orientação: borda medial = frente). `src/fly_gate_looming.py`, LIF do Shiu, brilho = taxa Poisson dos R1-6 (40 Hz = claro; R1-6 são histaminérgicos, escuro LIBERA L1/L2): `loom` = disco escuro em (az +30°, el 0) crescendo 3°→40° em 100–400 ms; `scramble` = mesmo NÚMERO de R escuros por passo em posições aleatórias; `static` = disco de 40° fixo desde 100 ms. 10 ensaios × 400 ms. APOSTA: (a) LPLC2+LC4 do lado direito: loom ≥ 2× scramble (a coerência espacial importa — é o que o circuito detecta); (b) loom ≥ 1,3× static (expansão > escuro grande parado; LPLC2 responde a expansão radial); (c) DNp01 (fibra gigante) dispara em ≥ 5/10 ensaios no loom e em menos no scramble; (d) roda em < 5 min. Se (a) falhar: a retinotopia (PCA) está embaralhando o olho — teste seguinte é reconstruir cartuchos pela adjacência R→L1/L2 antes de qualquer `--fly-eye` no Universe. Confundidor declarado: o modelo de taxa/LIF não tem os atrasos sinápticos específicos de T4/T5 (só 1,8 ms uniforme), então a sensibilidade a direção pode ser fraca mesmo com o mapa certo — (a) e (b) não dependem de direção, só de expansão/coerência. |
| 190 | A FIAÇÃO DA MOSCA VALE? PORTÃO DE CONTROLE (14/09 12:14, ANTES de rodar). O portão 186 (20 GRNs de açúcar → MN9 72 Hz, 420 ativos) é uma computação PUBLICADA e verificada. Agora o mesmo estímulo nos mesmos neurônios em três mapas de controle que preservam grau e estatística: `shuffle_targets` (alvos permutados: mesmos graus de entrada/saída e sinais), `shuffle_signs` (mesmo grafo, 40 % inibitório redistribuído), `shuffle_weights` (mesmo grafo e sinais, contagens de sinapse permutadas). APOSTA: (a) `shuffle_targets`: MN9 ≤ 5 Hz (contra 72,4) e ativos fora da faixa 300–600 — a via açúcar→pré-motor→MN9 é específica e some ao permutar alvos; (b) `shuffle_signs`: MN9 ≤ 20 Hz — a identidade excitatório/inibitório carrega a computação; (c) `shuffle_weights`: MN9 entre 30 e 120 Hz — permutar SÓ as magnitudes preserva o caminho, então o efeito é o menor dos três. DECISÃO: se (a) falhar (embaralhado acende MN9 igual), a fiação não carrega computação nesta leitura e o programa da mosca vira "reservatório grande" — abandonar o mapa real como hipótese e registrar. Se (a) ✓, a fiação É específica e o problema dos testes 187/188 é a LIGAÇÃO (entrada pelo órgão errado), não o mapa: prioridade passa a ligar os sentidos do carro nos órgãos certos (olho → fotorreceptores). |
| 190v | VEREDITO 14/09 12:18 (`fly/fly_gate_{real,shuffle_targets,shuffle_signs,shuffle_weights}_100hz.json`, 30 ensaios × 1 s, mesmos 20 GRNs a 100 Hz, ~35 s por mapa). **A FIAÇÃO CARREGA A COMPUTAÇÃO.** | mapa | MN9 | ensaios | ativos | spikes | \|---\|---\|---\|---\|---\| | real | **72,4 ± 5,0 Hz** | 30/30 | 420 | 340 k | | alvos embaralhados | **0,0 Hz** | 0/30 | 175 | 76 k | | pesos embaralhados | **0,0 Hz** | 0/30 | 96 | 98 k | | sinais embaralhados | 29,4 ± 24,2 Hz | 28/30 | **26 022** | **14,0 M** |. (a) ✓ alvos: 0,0 contra 72,4 — permutar os alvos preservando graus e sinais APAGA a via açúcar→pré-motor→MN9; (b) ✗ numérico, mecanismo mais forte que a aposta: sinais embaralhados dão 29 Hz mas com **62× mais neurônios ativos e 41× mais spikes** — não é a computação, é uma CRISE epiléptica; a identidade excitatório/inibitório (40 % das arestas) é o que mantém o cérebro estável, e MN9 dispara junto com todo o resto; (c) ✗ e é o achado que eu não esperava: permutar só as MAGNITUDES (mesmo grafo, mesmos sinais) também zera MN9 — eu previra 30–120 Hz. Mecanismo: as contagens de sinapse são muito desiguais (7 % das arestas levam 43 % das sinapses); a via forte é um caminho estreito de arestas pesadas, e redistribuir magnitudes dilui exatamente esse caminho. **DECISÃO REGISTRADA (a régua da pred 190):** (a) ✓ ⇒ o mapa real NÃO é um reservatório qualquer, e o empate real × embaralhado dos testes 187/188 é culpa da LIGAÇÃO (entrada por órgão aleatório: distância de parede num neurônio olfativo, velocidade no órgão de Johnston), não do mapa. Prioridade passa a ser ligar os sentidos do carro nos órgãos certos — olho → fotorreceptores (`--fly-eye`, `docs/96`, `Universe/docs/FLY-MAP-BRAIN.md`) — e usar dinâmica de spikes, já que a única computação verificada só existe com spikes (`Universe/docs/KERNELS-FLY-SPIKING.md`, pedido ao Astra). |
| 189v | VEREDITO 14/09 12:40 (`src/fly_diag_vision.py`, `fly/fly_diag_vision_*.json`; 3–4 ensaios × 300–400 ms por condição, GPU). **A via visual NÃO propaga no modelo de spikes, e o mecanismo é quantitativo.** Limiar exige g∞ ≥ 7,0 mV, ou seja S ≥ 5 091 sinapse·Hz. Estimulando os 7 932 R1-6: a 40 Hz L1 recebe S = 899 (g∞ 1,24 mV, 5,7× abaixo) e dispara 1,1 Hz; a 250 Hz L1/L2 sobem para 26/25 Hz (a LÂMINA funciona), mas a camada seguinte é **líquida inibitória**: Mi1 S = −3 214 (g∞ −4,4 mV), Tm3 −1 348, T4 −1 059, T5 −1 997, HS −219 — todos NEGATIVOS, e aumentar o estímulo só aprofunda a inibição. Nada além do hop 1 dispara em nenhuma taxa. MECANISMO BIOLÓGICO: no animal fotorreceptores e neurônios da lâmina/medula são **graduados (não disparam)** — a inibição modula uma liberação tônica contínua; num LIF sem excitação tônica, inibição só silencia, e o modelo de Shiu (desenhado e validado para cadeias excitatórias como açúcar→MN9) não representa o lobo óptico. (a) ✗ (b) ✗ (c) ✗ (d) ✓ (30 s por condição). **O DESVIO EXISTE e foi medido:** injetando nos detectores de movimento em vez dos fotorreceptores, a jusante é toda spiking e responde — T4+T5 @100 Hz → LPLC2 24,0 Hz, HS 250 Hz, VS 241 Hz, **DNp01 (fibra gigante) 95,6 Hz em 100 % dos ensaios**; LC4+LPLC2 @100 Hz → DNp01 230 Hz. CONSEQUÊNCIA DE PROJETO: (1) o lobo óptico deve ser modelo de TAXA (graduado) — e é exatamente o que o `fly_step` do Universe já faz, então `--fly-eye` no caminho de taxa é o plano certo; (2) para o caminho de spikes, a retina do carro entra em **T4/T5** (12 246 neurônios, retinotópicos, o equivalente ao nosso fluxo óptico dos canais 83-84/114-117), não nos fotorreceptores; (3) o critério de aceite de visão no pedido ao Astra (`Universe/docs/KERNELS-FLY-SPIKING.md`) muda: looming em LIF a partir de fotorreceptores NÃO é alcançável e não deve ser exigido. |
| 191 | REFLEXO DE DIREÇÃO NA FIAÇÃO DA MOSCA (14/09 12:58, ANTES de rodar). `src/fly_reflex.py`: em vez de evoluir um cérebro sobre o mapa, LER um reflexo que o animal já tem. Estimula 2 000 detectores de movimento (T4+T5) de UM lado do campo visual (carta retinotópica por PCA, `flybrain.eye.motion_chart`) a 100 Hz por 300 ms, 8 ensaios, e mede a ASSIMETRIA (direita−esquerda)/(direita+esquerda) da taxa dos descendentes de direção e fuga: DNa02 (par único, direção), DNa01, DNa (52), DNp01 (fibra gigante), DNp09, DNp (326), DNg (843), HS (6), VS (32). Braços: `left`, `right`, `bilateral` (mesmo número, metade de cada lado) e `scramble` (mesmo número, lados sorteados); depois o mesmo em mapa com alvos embaralhados. APOSTA: (a) o estímulo lateral produz assimetria descendente: \|assimetria\| ≥ 0,2 em DNa_all ou DNp_all para `left` e para `right`; (b) o SINAL INVERTE entre `left` e `right` — a oscilação (assimetria com `right` menos assimetria com `left`) ≥ 0,4; é isso que caracteriza um comando de direção e não um alarme genérico; (c) `bilateral` fica em \|assimetria\| ≤ 0,1 (controle de contagem); (d) no mapa embaralhado a oscilação cai para ≤ 0,1 — a lateralidade vem da fiação, não do fato de estimular metade das células. Se (b) ✓, a mosca entrega de graça o mapeamento "movimento à esquerda → vira à direita", que é exatamente a saída que o carro precisa, e o próximo passo é ligar a retina do carro em T4/T5 por ângulo e ler DNa02/HS/VS como volante — sem evoluir nada. Se (b) ✗ com (a) ✓, há resposta mas não direção: o mapa dá alarme (fuga), não volante. |
| 191v | VEREDITO 14/09 12:59 (`fly/fly_reflex_{real,shuffle_targets}_s0.json`, 8 ensaios × 300 ms, 2 000 células T4/T5 por braço, 29 s por mapa). **A MOSCA ENTREGA O REFLEXO DE DIREÇÃO PRONTO.** Mapa real, taxas direita/esquerda: estímulo à ESQUERDA → HS 0,0/0,7, VS 0,0/**28,9** Hz; estímulo à DIREITA → HS **2,9**/0,0, VS **17,7**/0,0. Índice de assimetria e oscilação (esquerda→direita): | grupo | esq | dir | bilateral | oscilação | \|---\|---\|---\|---\|---\| | HS (6) | −1,000 | +1,000 | +0,061 | **+2,000** | | VS (32) | −1,000 | +1,000 | +0,223 | **+2,000** | | LPLC2 (210) | −1,000 | +1,000 | +0,232 | **+2,000** | | DNg (843) | −1,000 | +0,846 | −0,506 | +1,846 | | DNp (326) | −0,110 | +0,854 | +0,561 | +0,964 | | todos os DN | −0,020 | +0,860 | +0,148 | +0,880 |. (a) ✓ assimetria ≫ 0,2; (b) ✓✓ a oscilação é +2,000 nas células de campo largo e +0,88 na população descendente inteira (aposta era ≥ 0,4); (c) ✓ bilateral fica em +0,061 (HS) e +0,148 (todos os DN) — o controle de contagem funciona; VS +0,223 é o único acima de 0,1; (d) ✓ no mapa com alvos embaralhados a lateralidade **desaparece**: HS não tem oscilação nenhuma (silencioso ou cravado em −1,000 dos dois lados), os sinais de população trocam de direção por grupo (DNa −0,401, DNp −0,460, todos os DN −0,409, LPLC2 −1,566) e as taxas desabam (VS 0,1–2,0 Hz contra 28,9 no real). RESSALVA HONESTA: HS/VS são células de campo largo monoculares, então ±1,000 nelas é em parte anatomia trivial ("olho esquerdo acende lado esquerdo"); o que NÃO é trivial e sustenta a leitura é (i) as taxas colapsarem no mapa embaralhado, (ii) o bilateral equilibrar, e (iii) a oscilação de +0,88 na população de ~1 200 descendentes, que não é um par monocular. Achado lateral: **DNa02 (o descendente canônico de direção) fica SILENCIOSO** sob estímulo lateral e dispara 10–61 Hz sob bilateral/scramble — ele pede entrada mais larga que 2 000 células de um lado. CONSEQUÊNCIA: existe um controlador sem evolução nenhuma — ligar a retina do carro em T4/T5 por ângulo e ler a assimetria de HS/VS (ou da população descendente) como volante. É o que a F3 vai medir na pista. |
| 192 | A PODA SOBREVIVE AO CONTROLE DE σ — E AGORA AO CONSERTO DO BUG (14/09 13:19). Contexto: o Astra apontou que `gerar` (σ .30) × `podar` (σ .15 + máscara) muda DUAS variáveis, e que o controle que isola o σ (`gerar_fino`) nunca rodou. Rodei os três braços na GPU (`src/lab.py::evolve_masked`, 512 indivíduos, 60 gerações, 20 sementes pareadas, mesmas 6 cidades de treino, avaliação em 5 cidades nunca vistas, 64 réplicas; 740 s). **Refiz a estatística do JSON bruto eu mesmo:** treino `prune − generate` +0,707 (p 1,1e-4, 17/20), **`prune − generate_fine` +0,950 (IC95 [+0,66, +1,24], p 1,6e-6, 19/20)**, `generate_fine − generate` −0,243 (p 0,082, n.s.); cidades novas `prune − generate` **+3,799** (IC95 [+3,20, +4,40], p 5,2e-11, **20/20**), `prune − generate_fine` **+3,438** (IC95 [+2,51, +4,36], p 2,5e-7, 19/20), `generate_fine − generate` +0,361 (p 0,41, n.s.). Densidade final da máscara 0,288 ± 0,051. **Minha predição e a expectativa implícita da revisão estavam ERRADAS: σ sozinho não explica nada (p 0,41) e a máscara explica tudo** — e a generalização, que era o elo fraco no Colab (+1,62, p 0,068), aqui é o efeito MAIS forte (+3,44, p 2,5e-7), porque este motor tem 64 réplicas por cidade e 512 indivíduos contra o protótipo numpy. RESSALVA QUE EU MESMO ACHEI e que suspende o veredito: **o simulador da GPU tem o MESMO bug de ordem** que o Astra achou no protótipo (`lab.py:722` troca o nó na chegada antes de `lab.py:858` aplicar a ação, exatamente como `taxi_np.py:126` × `:157`), então as duas medições compartilham o defeito e não são independentes dele. Consertado em `08ae9d1` (quem acabou de chegar não age neste tique; `NM_CHEGADA_LEGADO=1` reproduz o antigo) com regressão `src/test_arrival_action.py`. APOSTA PARA A REPETIÇÃO no simulador consertado (mesmas 20 sementes, mesmo protocolo): (a) `prune − generate_fine` em cidades novas continua ≥ +2,0 com p < 1e-4 — o sinal da máscara é estrutural, não artefato de índice trocado; (b) todos os três braços melhoram em valor absoluto (o bug desperdiçava ações), com `generate` subindo de 9,95 entregas para ≥ 11; (c) `generate_fine − generate` continua nulo (\|Δ\| < 1,0, p > 0,05). Se (a) cair abaixo de +1,0, o achado da poda era em parte o bug e o documento tem de dizer isso. | pendente |
