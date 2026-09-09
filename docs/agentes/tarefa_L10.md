TAREFA L10 — BASE = L6 p4 (0.56). Platô 0.56–0.58 em 4 lotes (55+ políticas): LIMIAR ACABOU. Mude UMA alavanca; mantenha comida noturna, pane=transporte, reparo com vida<.5, água<.50, tiers de gasolina e PESO_RUA .15.
O gargalo é CAIXA: a base abastece com dinheiro 20.8 (campeão 37.1) e compra 50 L (campeão 100 L) — por isso reparo (0.70–0.76), comida (0.62–0.66) e água (0.60) sempre pioram: disputam o mesmo caixa.
RENDA nunca foi tocada: tarifa = (3+.25·d)·preco·(1−aliq) do distrito onde EMBARCA, e o passageiro reaparece com prob demanda/20 por tick no distrito ONDE O TÁXI ESTÁ.
Números do mapa de teste: centro ×1.30 e 0.10/tick; residencial ×0.85 e 0.05; industrial ×0.54 e 0.035; periferia ×0.50 e 0.015 (centro = 2.6× a tarifa e 6.7× o passageiro da periferia). Mas gasolina no caro custa 4×: 100 L = 60 no centro, 15 na periferia.
Sentidos nunca usados: F[:,0,27] = e_demanda do meu distrito (0.15 periferia … 1.0 centro); F[:,0,28] = e_espera = ticks desde a última coleta /100 (mediana entre corridas = 57 → 0.57).
p3 LUGAR (sentido A): livre, sem compra pendente e (e_espera > .6 ou e_demanda < .5) → mover por d_alvo + .15·custo_frente − W·preco_frente·(1−aliq_frente), com W entre .5 e 1.0; segure o rumo ≥ 20 ticks e volte ao normal ao pegar passageiro.
p7 (era RUA, hoje INERTE: 0.57/18.9/8.4/5.8 idêntico em L7, L8 e L9): MESMO código do p3 com W NEGATIVO (evitar preço/imposto alto, como os genes do campeão). p3 contra p7 = os dois sentidos medidos no mesmo lote.
Nos dois: se e_fuel < .3, inverta o rumo para preco_frente BAIXO — a pane leva ao posto mais perto, e no distrito barato 100 L cabem no caixa.
p6 CORRIDA: com d_alvo = F[:,8,0] > 40 e serviço no raio, compre ANTES de sair; nunca desvie com passageiro a bordo.
p5 PARADA MÍNIMA: ≤ 2 ticks no raio (100 L se dinh ≥ 35, senão 50; comida se fome > .3) SEM bloquear compra já pendente — L8 p5 travou (0.94, abastecidas 2.9, panes 9.8).
p1/p2/p4 (comida/água/gasolina): 4 testes sem ganho — só entre se gastar MENOS caixa ou menos ticks pela MESMA nutrição (mexer na água leva sede a 33 %). p8 LIVRE: eixo obrigatório = renda/lugar (preço, demanda, hora), nunca fadiga (H29).
PREDIÇÃO: dê faixa de mortos E corridas por dia vivo (base = 19.0/5.8 = 3.28). Peso ≤ .3 sobre feature de fronteira é inerte: se prevê empate, diga empate.
