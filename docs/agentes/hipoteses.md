# Hipóteses já testadas (não repetir) — atualizado pelo consolidador
| # | hipótese | resultado | onde |
|---|---|---|---|
| H1 | ir ao posto por precaução (autonomia < .3) evita morte | ✗ morre de fome no dia 3: desvio demais, 6 corridas em vez de 17 | r3, r4 |
| H2 | evitar pane a todo custo | ✗ o campeão tem 6.8 panes/vida e vive mais: pane + guincho (15 L) é transporte barato ao posto | r5 |
| H3 | política que nunca vai ao posto por vontade e compra tudo lá (pane como transporte) | ✓ chega ao modo de morte do campeão (dano), 13.7 corridas | r5 |
| H4 | + reparo na oficina quando vida < .5 | ✓ 0.76 (bate o campeão 0.85); o campeão TAMBÉM repara (1,5 oficinas/vida, medido 09/09) | r6 |
| H5 | + comer mais no posto (fome > .15) e comida perto | ✓ 0.73 | r7 |
| H6 | tirar o 'ficar' (23 % das escolhas) | ✗ 0.88: o 'ficar' era no raio do serviço, completando compras (uma ação por tick) | r8 |
| H7 | abastecer 100 L sempre que no posto com dinheiro > 40 | ✗ 0.80: come o dinheiro do reparo/comida | r6_2 |
| H8 | reparo só com caixa > 25 | ✗ 0.90 (junto com H6) | r8_2 |
| H9 | densidade de passageiro na cidade muda mortalidade | ✗ npx 24/36/48 → 0.82/0.81/0.78 | q17 |
| H10 | ler lugar/demanda/espera paga (cérebro em camadas) | ✗ em 10 cenários; no válido da cidade o linear é o melhor | r1–r3 |
| H11 | penalizar sair da rua (custo_frente) ao escolher direção | ✗ 0.99: paralisa o táxi (1.7 corridas) — a penalidade domina a distância ao alvo | L1 p7 |
| H12 | comer mais no posto (limiar de fome mais baixo) sem mudar onde come | ✗ 0.78, fome 74 % das mortes: o posto fecha à noite; comer mais de dia não cobre a noite | L1 p1 |
| H13 | comer à noite em pontos de comida (posto fecha) | ✓ leve: 0.74 → 0.72 (5 sementes), fome ainda 47 % das mortes | L2 p6 |
| H14 | lote 2: 6/8 respostas sem bloco ```python → recusadas | bug de formato do orquestrador (parser agora aceita ```py / ``` com def fabrica) | L2 |
| H15 | rua como DESEMPATE (peso .15 em custo_frente, não 5.0) + comida à noite em ponto de comida + nunca desviar com passageiro a bordo + comida antes de água no posto | ✓ 0.66 (3 sementes): melhor da série; o agente calibrou o peso pelos dados do L1 p7 (que paralisou com peso 5) | L3 p7 |

| H16 | AGUA: beber/comprar mais cedo | ✓ 0.71 mas sede era so 7% das mortes — ganho veio de menos paradas, nao de sede | L3 p2 |
| H17 | REPARO mais cedo/mais barato (2o teste) | ✗ 0.82: reparo come caixa e ticks, corridas caem 16.4 → 12.7 | L1 p3, L3 p3 |
| H18 | GASOLINA: mais litros por parada | ✓ 0.73 (empata com a base) — menos paradas nao basta sozinho | L3 p4 |
| H19 | ORDEM das compras + ticks parado no posto (2o teste) | ✗ 0.99: uma acao por tick vira fila, 7.1 corridas | L3 p5 |
| H20 | NOITE = descansar/parar de rodar | ✗ 0.88: corta renda e nao evita fome (fome vira 73% das mortes) | L3 p6 |
| H21 | LIVRE: comida noturna + nao desviar com passageiro | ✓ 0.68, 2o melhor da serie | L3 p8 |
| H22 | limiar de fome baixo de DIA (3o teste) | ✗ 0.73: refeicoes sobem 7.3 → 8.2 e mortos nao cai — comer de dia nao cobre 22h-6h | L3 p1 |
| H16 | ÁGUA: comprar menos/na hora certa sobre a base p7 | ✓ 0.66 → 0.62 (5 s 0.63): sede sobe para 19 % das mortes mas fome/dano caem; renda 172 | L4 p2 |
| H17 | (bug) parser pegava o maior bloco python: em respostas sujas pelo hook, era o código-base ecoado → 6/8 do lote 4 idênticos à base | corrigido: último bloco + recusa 'igual à base' | L4 |
| H18 | GASOLINA: paradas mais frequentes com menos litros (abast 11.4 vs 8) sobre L4 p2 | ✓ 0.62 → 0.57 (5 s 0.58): o agente previu empate (0.65–0.68) e errou para MELHOR | L5 p4 |
| H19 | (bug do laço) relançamento usava tarefa_L1 e lote 6 rodou com tarefa vazia (fallback para arquivo inexistente) | corrigido: tarefa mais recente existente | L5–L6 |

| H23 | GASOLINA: paradas ainda mais frequentes com menos litros (3o teste, sobre L5 p4) | ✓ 0.57 → 0.56, corridas 18.9 → 19.0 — melhor global; unica direcao que pagou 3 lotes seguidos | L6 p4 |
| H24 | ORDEM das compras + ticks parado (3o teste, base nova) | ~ 0.57: empata com a base — alavanca saturada, nao repetir sem mudar de eixo | L6 p5 |
| H25 | NOITE/descanso/fadiga | ✗ 3 lotes: 0.78 / 0.74 / 0.78, corridas 15.0 / 16.0 / 14.3 — corta renda e nao mexe na fome. APOSENTAR a alavanca | L4 p6, L5 p6, L6 p6 |
| H26 | AGUA mais agressiva sobre a base de gasolina | ✗ 0.56 → 0.62: sede sobe de 21 % para 34 % das mortes. Agua chegou ao fim do curso util | L6 p2 |
| H27 | REPARO mais cedo/mais barato (4o teste) | ~ 0.63: dano cai de 48 % para 42 % mas corridas caem para 17.8 — o caixa gasto na oficina falta depois | L6 p3 |
| H28 | mortalidade e' funcao do throughput: mortos ≈ 1.48 − 0.047 × corridas (r = −0.97, n=19) | ✓ regressao sobre placar+feedbacks; explica por que noite/reparo/fila sempre perdem | L3–L6 |
| H29 | LIVRE sem eixo proprio (agente escolheu fadiga de novo) | ✗ 0.77, corridas 14.9 — slot LIVRE precisa de eixo prescrito, senao repete alavanca morta | L6 p8 |
| H30 | ficar parado no raio do servico so' enquanto ha' compra pendente (livre = cacar passageiro): 42.8 % → ~26 % do campeao | ⏳ a testar — previsao −0.05 a −0.08 de mortos via +1.5 corridas | L7 |
| H31 | comida estocada antes das 21h para cobrir 1h-5h (27 refeicoes contra ~400 do campeao) | ⏳ a testar — fome e' 47 % e o furo e' noturno, nao diurno (H12/H22 ja' mostraram) | L7 |
| H32 | RUA com peso dependente da vida (0.15 normal, 0.30 com vida < 40) | ⏳ a testar — primeira tentativa de atacar dano sem gastar caixa na oficina | L7 |
| H20 | (regra medida pelo Opus em 19 políticas) mortos ≈ 1.48 − 0.047 × corridas, r = −0.97: quem corre mais morre menos; alavanca = tempo livre parado no raio (43 % vs 26 % do campeão) | em teste (lote 7) | L6 consolidação |
| H21 | config limpa (CLAUDE_CONFIG_DIR sem plugins) para os agentes | ✓ lote 7: 8/8 respostas válidas, 0 contaminação (lotes 2–5: 25–75 % perdidas) | L7 |
| H22 | (Opus, lote 7) top-up voluntário de 20–25 L ao passar perto de posto com tanque < 60 | ✗ 0.65 (base 0.56): contradiz H2/H3 — o campeão nunca abastece por vontade | L7 p4 |
| H23 | (Opus, lote 7) reparo só com vida < 35 e caixa > 40 | ✗ 0.76 (pior do lote): o campeão repara com vida ~42; reparo tardio mata | L7 p3 |
| H24 | (Opus) "cada corrida a mais vale ~5 pp" (mortos ≈ 1.48 − 0.047·corridas) | correlação confirmada por mim (n=37: r = −0.96), mas é metade causalidade invertida: quem vive mais corre mais. Variável honesta: corridas por dia vivo | auditoria Fable |
| H25 | alavancas 'estruturais' de manutenção (parada ≤ 2 ticks, comida noturna forte, caça-passageiro) sobre L6 p4 | ✗ platô: parada mínima 0.94 (parou de comprar: abast 2.9, panes 9.8), comida 0.62, caça 0.60; melhor do lote 0.57 = base | L8 |
| H26 | TETO provisório da busca local de uma alavanca = 0.56–0.58 (5 s, lotes 5–8, 55 políticas); predições calibradas (empate previsto = empate medido) | registrado (ledger 131); próximo eixo = camada de TRABALHO (lugar/preço), nunca tocada | consolidador |

| # | hipótese | resultado | onde |
|---|---|---|---|
| H33 | slots RUA e NOITE viraram no-op: L7/L8/L9 p7 = 0.57 / 18.9 / 8.4 / 5.8 idênticos nos 3 lotes, L7 p6 = L9 p6 = 0.56 / 18.9 / 8.4 = a base | ✗ 6 de 24 políticas dos lotes 7–9 não mudaram nada — peso ≤ .3 sobre feature de fronteira (custo_frente) nunca flipa uma decisão; trocar o slot de alavanca | L7–L9 |
| H34 | o gargalo é CAIXA e não limiar: base abastece com dinheiro 20.8 vs 37.1 do campeão e compra 50 L vs 100 L; toda alavanca que gasta piora (reparo 0.70–0.76, comida 0.62–0.66, água 0.60) e as que pagaram só cortam gasto/ticks (gasolina 0.62→0.57→0.56) | ✓ derivado do placar (n=24 políticas, 4 lotes) | consolidação L9 |
| H35 | throughput não é causa: L9 p1 faz 20.0 corridas (3.57/dia vivo, o maior medido) e morre 0.66; a base faz 19.0 (3.28/dia) e morre 0.56 | ✗ refuta a leitura causal de mortos ≈ 1.48 − 0.047·corridas; confirma a auditoria do Fable (H24) — a variável é renda, não contagem | L9 p1 |
| H36 | renda por corrida depende do distrito de EMBARQUE: tarifa·pmul·(1−aliq) = centro 1.30, residencial 0.85, industrial 0.54, periferia 0.50 (campo.py:47-51,332-334); e os slots de passageiro voltam com prob demanda/20 por tick no distrito DO TÁXI (centro 0.10 vs periferia 0.015) | ⏳ a testar no L10 p3 (W .5–1.0, só quando livre e e_espera > .6) — previsão −0.02 a −0.06 de mortos | L10 |
| H37 | genes de lugar do campeão (evita aliq alta e distrito-casa) são de uma política PIOR (0.85 vs 0.56): aliq corta no máximo 35 % enquanto pmul dobra a tarifa e a demanda | ⏳ L10 p3 (rumo ao caro) contra L10 p7 (mesmo código, W negativo) decide o sentido no mesmo lote | L10 |
| H38 | a política já enxerga e_demanda (F[:,0,27] = demanda/2, 0.15 a 1.0) e e_espera (F[:,0,28] = ticks/100, mediana entre corridas 57) por causa de NM_PONTO=1, e nenhuma das 55+ políticas leu essas colunas | ⏳ gatilho estrutural do L10: trocar de distrito quando e_espera > .6 e e_demanda < .5 | L10 |
| H39 | camada de TRABALHO/LUGAR sobre L6 p4: rumo a preço alto (W +.5…1, L10 p3) vs evitar imposto alto como o campeão (W negativo, L10 p7) | ✗ os dois pioram: 0.61 e 0.62 vs base 0.56; H37 resolvida: nenhum sentido paga; lugar não é alavanca neste mundo | L10 |
| H40 | parada mínima (≤ 2 ticks no raio) | ✗ pela 2ª vez colapsa (0.97, abast 1.0): a compra exige ficar no raio vários ticks; qualquer teto de ticks quebra o abastecimento | L10 p5 (e L8 p5) |
| H41 | (análise externa) pane com preço (guincho 10, 5 L) separa o platô | ✗ todas em 0.95 idênticas; campeão 0.98; ninguém tem estratégia de combustível voluntária — o mundo do guincho grátis moldou todas | t1 |
| H42 | lote 11 (tarefa L10 do Opus: caixa/renda): 8 alavancas, melhor 0.56 = base; comida 0.58, gasolina 0.58, corrida 0.66, rua 1.00 (paralisou de novo), 1 erro de exec | ✗ platô confirmado pela 7ª vez (lotes 5–11); com trabalho/lugar/renda/caixa testados, o espaço de uma alavanca sobre esta base está esgotado | L11 |
| H43 | clone por forma fechada (ridge Φ→escolha) da política 0.56 num Linear | ✗ fidelidade 60 %, clone 1.00 (sede): regra com limiar/estado não cabe em nota linear centrada (achado 84 de novo: o corpo é invisível na direção) | t2, pred 134 |

| H44 | CALOR: parar pra esfriar ao entrar na zona de sangramento (D_RODAR .15/tick andando com calor > 80 raw), histerese soltando em raw 66 | ✓ 0.56 → 0.53 (melhor global): dano cai 45 % → 39 % e corridas/dia vivo só 3.28 → 3.15 — primeiro eixo de CORPO que paga desde a gasolina | L12 p8 |
| H45 | GASOLINA: limiar de caixa por tier dependente do preço do distrito (100 L com dinh > 20 no barato, > 70 no caro) | ✓ 0.55 com 19.3 corridas (maior throughput do lote) — o mesmo litro por menos caixa, sem mexer em nutrição | L12 p4 |
| H46 | RESERVA: a pane custa 6 + (20 − reserva) de dano; a reserva nasce em 0 e NENHUMA das 87 políticas comprou o tier de 150 L (G+4), logo cada uma das ~7.5 panes/vida custa 26 e não 6 | ⏳ L13 p2/p3 — até 150 de dano evitável por vida (vida máx 100) por ~9 de caixa a mais no distrito barato; previsão −0.03 a −0.08 de mortos | L13 |
| H47 | ÁGUA à noite no PONTO DE COMIDA (serv_ab faz perto['agua'] receber comida e posto; só o posto fecha à noite) — canal noturno nunca usado, base só bebe via disp[:,5] com d_agua < 8 | ⏳ L13 p4 — sede subiu a 32 % no p8 e o desvio de comida noturna já existe (custo marginal ~0 tick, ~2.5 de caixa) | L13 |
| H48 | calor > 60 raw multiplica a sede por 2.5 (agua_passo .08 + agua_calor .12); a histerese do p8 solta em raw 66, ainda dentro da faixa cara | ⏳ L13 p5 — soltar em raw 58 custa ~13 ticks parados e compra ~145 ticks de rodagem na rua abaixo do limiar | L13 |
| H49 | COMIDA tem preço de distrito e de dia (2·pmul·fase: ≈1.2 industrial, ≈4.0 centro, ±50 % em ciclo de 3 dias); os 5 testes de limiar de fome (H5/H12/H22/L10-L12 p1) foram todos cegos ao preço | ⏳ L13 p6 — comer barato é a única forma de aumentar refeições sem disputar o caixa (H34) | L13 |
| H50 | dois ganhos independentes do MESMO lote somam (calor 0.53 + tier por preço 0.55) | ⏳ L13 p1 — primeira fusão testada em 13 lotes; se não somar, o platô é de corpo e não de política | L13 |
| H51 | parar para esfriar (e_calor > .667, histerese .55) sobre L6 p4 | ✓ 0.53 (5 s 0.55): primeira alavanca que reduz o DANO (39 % vs 46–48 %); custa 0.4 corrida/dia | L12 p8 |
| H52 | ganho por lote do laço v2 (12 lotes, 86 políticas): 0.73 → 0.66 → 0.62 → 0.57 → 0.56 → platô (5 lotes) → 0.55 (esfriar). Rendimento decrescente: os últimos 6 lotes (48 políticas) renderam 2 pp | fechado 13:40 |
| H53 | (portão) testes_completo imprime SYNC! para o SerCompleto — e JÁ imprimia ontem (q7c, 09-08), que eu aprovei sem ler a última linha | dívida pré-existente, não regressão do F2 (g9 e o resto de g8 verdes); diag_sync.py na fila para apontar a operação | g8 |
| H54 | lote 13 (tarefa Opus: reserva/água noturna/calor): p7 = p8 = base exata (0.53/0.55), p1/p2/p4 0.54, p5 parada mínima 0.95 (3ª vez), p3 erro de forma | ✗ platô em 0.53–0.55; parada mínima refutada 3× — retirar a alavanca | L13 |

| # | hipótese | resultado | onde |
| H55 | lote 14 = platô (0.52–0.56): p3/p6/p8 saíram com métricas idênticas à base (18.6 / 8.4 / 5.9) — TRABALHO/LUGAR, TRABALHO/CORRIDA e RUA são no-op sobre esta base pela 2ª–4ª vez; parada mínima colapsou de novo (0.96) | ✗ retirar os 3 slots e realocar | L14 |
| H56 | aritmética da pane (campo.py:296): 6.2 panes × (6 + 8 não coberto pela reserva) = 87 de dano/vida ≈ 59 % do orçamento de vida (100 + 25×1.9 de oficina ≈ 148); 100+ políticas rodaram com res = 0 | ⏳ L15 p5/p4/p3/p7 — previsão −0.03 a −0.08 de mortos | L15 |
| H57 | a reserva NÃO exige o tier 150: qualquer compra acima da falta vira sobra e res += sobra×0.85 (campo.py:309-310); 8 de reserva = 9.4 L = 2.8 de caixa (1.7 no industrial) = 8 de vida, contra 0.4/ponto da oficina MAIS o desvio em ticks | ⏳ L15 p4 (tier acima da falta) vs p5 (tier 150 após a pane) decidem qual é mais barato | L15 |
| H58 | a reserva tem custo: peso = 1 + .002·res (res 50 = +10 % de gasolina ≈ 12 de caixa/vida) e perda 2 %/dia; res só é lida pela pane (8 por evento) → dose ótima ~16–48, encher é pior | ⏳ L15 p3 (alvo 16) vs p7 (alvo 48) medem a dose | L15 |
| H59 | a coluna "causa" do juiz é ESTADO na morte, não causa: c_fome = fome ≥ 90 ao morrer e se sobrepõe a c_sede (49+40+29 > 100); c_dano é só o resíduo | ✓ julga_politica.py:44-47 — "fome 49 %" superestima a fome; dano da pane aparece dentro dela | auditoria do código |
| H60 | e_reserva (F[:,0,17] = res/120) nunca foi lida por nenhuma das 100+ políticas dos 14 lotes | ✓ grep nos lotes L1–L14 | consolidação L14 |
| H61 | limiar de COMIDA: 7º teste (L14 p1, posto .15 → .35) deu 0.56 com 7.0 refeições contra 0.52/8.3 da base — subir o limiar perde; a fome não é limiar, é acesso (posto fecha à noite) | ✗ aposentar o eixo "limiar de fome"; comer oportunista no posto é bom porque é barato (2·pmul) e o tick já está gasto | L14 p1 |
| H55 | F2 custo por ATIVAÇÃO (por bloco) vs existência, λ .3, COMPLETO fumaça | dof 318 vs 165, metab 1.40 vs 1.49, mortos 0.87 vs 0.86: silêncio deixa de custar; tálamo/córtex sempre ligados; nada muda na sobrevivência | m1/m2, pred 136 |
| H56 | lote 14 p7 (RUA sobre esfriar): 0.50 em 5 s (−5 pp), panes 6.2 | ✓ novo teto; primeiro ganho em 6 lotes veio de uma combinação (esfriar + rua) | L14 |
| H57 | retina: `livre` (por opção) muda a direção no Linear ✓; `ret_t_k`/`ret_d_6,7` invisíveis no Bilinear/Completo em 240 ticks | sinais esparsos (rótulo 0 / cego 120 quase sempre) — tolerados no portão com razão; não estrutural | g18 |
| H58 | lote 16 (último): p2/p3 0.49 (5 s 0.50) = empate com L15 p8; laço v2 fechado em 0.49 | ✗ sem ganho; teto do mundo transparente para busca local de uma alavanca | L16 |

| # | hipótese | resultado | onde |
| H62 | 5 de 8 políticas do L16 saíram com métricas idênticas à base (18.4–18.6 corridas / 8.3–8.4 refeições / 5.9 dias): AGUA, TRABALHO/LUGAR, TRABALHO/CORRIDA, GASOLINA e LIVRE | ✗ no-op pela 2ª–5ª vez; só p1 (comida) e os dois colapsos (p5 0.93, p7 0.68) mudaram comportamento — o espaço de limiar sobre esta base está fechado | L16 |
| H63 | economia do táxi é deficitária e TODO preço de compra escala com o pmul do distrito ONDE se compra (gasolina .3·L·pmul, comida 2·pmul, água .05·L·pmul, oficina 10·pmul), enquanto a tarifa escala com o pmul do distrito de EMBARQUE | ✓ verificado no código (campo.py:296-300, 375); ~223 L/vida = 67·pmul contra renda ~172 → comprar a pmul .6 em vez de 1.2 devolve ~23 % da renda | leitura de campo.py |
| H64 | arbitragem de distrito: comprar (gasolina/comida/água/oficina) só com pmul ≤ 1.0 e embarcar com pmul alto — os dois sentidos ao mesmo tempo, coisa que H37/H39 nunca separaram (aplicaram um sinal só, e sobre a direção) | ⏳ L17, portão duro sobre a compra; previsão −0.03 a −0.05 de mortos | L17 |
| H65 | morrer "de fome" é morrer de CAIXA: a compra exige dinh ≥ custo (campo.py:343), logo sem dinheiro a loja recusa a refeição; a única fonte de dívida é o aluguel de meia-noite (4·alug = 3.2–10/dia) | ✓ mecanismo confirmado no código; explica por que toda alavanca que gasta (reparo, comida, água) piorou e só as que cortam gasto pagaram (H34) | leitura de campo.py |
| H66 | a dívida fere 2·(div/60)²/tick (até 2/tick = 480/dia) e o juiz MEDE c_divida, dinh_fim, renda, panes e oficina — mas placar.json e feedback.md descartam as 5 colunas | ✗ dívida jamais entrou no diagnóstico em 16 lotes; recomendação de processo (já feita na consolidação do L9, nunca adotada): acrescentar renda / dinheiro_fim / dívida % ao feedback | campo.py:383, politica_util.py:47,70-73 |
| H67 | oficina custa 10·pmul: 5–6 na periferia/industrial contra 20–30 no centro em pico do ciclo — o "reparo caro demais" de H17/H27 pode ser reparo no LUGAR errado, não na hora errada | ⏳ L17 (oficina condicionada a pmul) | L17 |
| H68 | peso sobre a escolha de direção está proibido: 6 no-ops com peso ≤ .3 (H33, H55, H62) e 3 paralisias com peso ≥ 1 (H11, L15 p7 1.00, L16 p7 0.68) | ✓ regra de processo: alavanca só vale se muda QUAL ação de compra é emitida | L1–L16 |
| H69 | a base come 1.42 refeições/dia contra 1.03 do campeão, comendo com fome ~15 (refeição devolve 90, fome sobe 76.8/dia → 83 % da refeição é jogada fora); subir o limiar puro já falhou 7× (H61), mas condicionar ao PREÇO (comer cedo só onde pmul ≤ 1) nunca foi medido — H49 foi declarada no L13 e não aparece no placar | ⏳ L17 | L13 (declarada), L17 |
| H59 | retina (cegueira real) piora a evolução | ✗ linear 0.81 com vs 0.83 sem; COMPLETO 0.81: o guincho grátis é o GPS (pane = transporte ao posto) e o passageiro continua oráculo — a evolução nunca dependeu de ver o posto; políticas explícitas com limiar em d_* desabam (0.49→0.91) | n1–n3, pred 138 |
| H60 | Mundo Vivo v1 (retina + guincho pago + régua vida): a régua separa (p10 1.7 d, p90 7.3 d) onde 'mortos 10 d' cravaria; COMPLETO = linear (−2 %); SEM hipocampo de nascença +11 % (4.98 vs 4.50) | ✓ régua; peça não paga; hipocampo semeado com ruído ATRAPALHA (custo de 119 genes sem função) | o1, pred 142 |
| H61 | Mundo Vivo v2 (v1 + estações amp .5 + custo por ativação λ .3): COMPLETO e sem-hipocampo viram PEDRA (fit 3.43 vs linear 3.85, −11 %, p .002; 1.1 corridas; tal/cor sempre ligados = metab 1.33) | ✗ camadas; achado: custo por ativação pune PORTÕES (modulam todo tick) e a evolução curta responde parando; regime amp .5 derruba até o linear (ent 11.9 → 5.6) | p1b, pred 143 |
| H62 | v2 completo sem livre (só camadas) 3.47 = COMPLETO 3.43 = sem-hip 3.43, todos −10 % vs linear e todos PEDRA | ✗ nenhuma variante com camadas sobrevive ao custo por ativação + inverno; próximo: separar ruído de semeadura (pred 144) | p1b |
| H63 | (método) linear no v1 com σ0 .02 deu fit 4.87 vs 4.59 com σ0 .2 (mesmo cenário, mesmas sementes): o ruído da espinha é `randn·σ0·(σ_esp/σ0)` — arredondamento diferente → trajetória caótica diferente em 60 gerações | ±6 % é a variância do PIPELINE (não da peça): comparações só valem pareadas DENTRO do run; entre runs, exigir ≥ 10 % ou mais sementes | q1 vs o1 |
