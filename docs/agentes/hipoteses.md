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
