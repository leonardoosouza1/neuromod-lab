import os as _os; _os.environ.setdefault('TORCHINDUCTOR_COMPILE_THREADS', '1')   # [auditoria 16] pool de 17 processos de compilacao travava a CPU
import torch, numpy as np, json, time, os
from datetime import datetime
DEV = 'cuda' if torch.cuda.is_available() else 'cpu'

GMAX = 5    # grau maximo de um no
NPX  = 6    # passageiros disponiveis por mundo

# ============================ CIDADES ============================
def gerar_cidade(seed, n=26):
    r = np.random.default_rng(seed); pos = []
    lado = max(12., 1.62*np.sqrt(n)*1.2)   # 12x12 so cabe ~100 pontos; n>100 sem escalar = loop infinito
    while len(pos) < n:
        p = r.random(2)*lado
        if all(np.hypot(p[0]-q[0], p[1]-q[1]) > 1.2 for q in pos): pos.append(p)
    pos = np.array(pos)
    D = np.hypot(pos[:,None,0]-pos[None,:,0], pos[:,None,1]-pos[None,:,1])
    np.fill_diagonal(D, 1e9)
    adj = [set() for _ in range(n)]
    for i in range(n):
        for j in np.argsort(D[i])[:int(r.integers(2,5))]:
            adj[i].add(int(j)); adj[int(j)].add(i)
    for i in range(n):
        if not adj[i]:
            j = int(np.argmin(D[i])); adj[i].add(j); adj[j].add(i)
    adj = [sorted(a)[:GMAX] for a in adj]
    A = np.full((n,GMAX), -1, dtype=np.int64)
    W = np.zeros((n,GMAX), dtype=np.float32)
    for i in range(n):
        for k, j in enumerate(adj[i]):
            A[i,k] = j; W[i,k] = max(1, round(D[i,j]/1.5))
    DI = np.full((n,n), 1e6, dtype=np.float32); np.fill_diagonal(DI, 0)
    for i in range(n):
        for k, j in enumerate(adj[i]): DI[i,j] = W[i,k]
    for k in range(n): DI = np.minimum(DI, DI[:,k:k+1] + DI[k:k+1,:])
    idx = list(r.permutation(n))
    serv = np.zeros((n,5), dtype=np.float32)   # posto, comida, descanso, oficina, loja
    # DENSIDADE escala com n (n=26 -> contagens originais, bit a bit): cidade
    # 4.6x maior com os MESMOS 3 postos = morte por geometria, nao por merito.
    esc_n = n/26.
    cts = [max(1,round(3*esc_n)), max(1,round(3*esc_n)), max(1,round(2*esc_n)),
           max(1,round(4*esc_n)), max(1,round(2*esc_n))]
    ac = 0
    for t, ct in enumerate(cts):
        for i in idx[ac:ac+ct]: serv[i,t] = 1.0
        ac += ct
    grp = np.zeros((n,GMAX), dtype=np.int64); tem = np.zeros(n, dtype=np.float32)
    for i in range(n):
        if len(adj[i]) >= 3:
            tem[i] = 1.0
            for k, j in enumerate(adj[i]):
                ang = np.arctan2(*(pos[j]-pos[i])[::-1]) % np.pi
                grp[i,k] = 0 if ang < np.pi/2 else 1
    return dict(n=n, A=A, W=W, DI=DI, serv=serv, grp=grp, tem=tem, pos=pos)

class Cfg:
    def __init__(s, d=1.0, trafego=.35, imposto=.18, mundo='base', raio=4.,
                 deriva=.02, per_mare=128):
        # mundo: o que fica OCULTO do taxi.
        #   base    visao global, spawn uniforme      -> memoria nao tem o que pagar
        #   cego    visao raio R, spawn uniforme      -> CONTROLE: oculto sem estrutura
        #   hotspot visao raio R, polo que DERIVA     -> memoria de onde apareceu paga
        #   mare    visao raio R, 2 polos alternando  -> estrutura PERIODICA (fase oculta)
        #   ruas    congestao CRONICA por no (sorteada POR MUNDO, nao por cidade —
        #           evolucao nao decora) e INVISIVEL nos vizinhos: so sente ao pisar.
        #           Lembrar quais ruas entopem = MemCusto. Resto igual ao base.
        #   semgps  oraculo de distancia-ate-servico REMOVIDO (features ds e leitura
        #           do corpo/hibrido ficam neutras). Saber onde tem posto = ter
        #           passado la = MapaServico. Resto igual ao base.
        s.mundo=mundo; s.raio=raio; s.deriva=deriva; s.per_mare=per_mare
        s.cron_frac=.30; s.cron_alto=1.6   # ruas: fracao cronica e teto do custo extra
        s.clarividente=False   # diagnostico: ruas com congestao VISIVEL = teto fisico
        # E9b (doc 24): agua de radiador + relogio de 24h
        s.com_agua=False       # liga o recurso agua (fisica extra de temperatura)
        s.dia=480              # passos por dia (1 passo ~ 3 min)
        s.fuel=.70+1.4*d; s.pneu=.18+.9*d; s.temp=1.6+4.*d; s.fome=.07+.25*d
        s.fadiga=.45+1.2*d; s.risco=.02+.12*d; s.oleo=.25+.7*d
        s.per=max(int(round(16-6*d)),6); s.base=6.; s.km=2.6
        s.trafego=trafego; s.imposto=imposto
        # ECO-FUEL V2 (opt-in): posto enche o TANQUE (nao +30) e pane vira
        # punicao real (fuel=5, mal da pra rastejar ao posto). Predicao
        # registrada em PREDICOES.md antes de rodar. Default False: nao
        # contamina baterias em andamento.
        s.eco2=False
        # pane_fuel: quanto sobra no tanque apos pane-seca. None = 5 com eco2,
        # 15 sem. Com 5 o perito entra em ESPIRAL (5 nao paga 1 salto ate o
        # posto -> pane de novo): ent 8.0 -> 2.9, av_fuel 25 -> 48 (E12 v1).
        s.pane_fuel=None
        s.pane_dinh=12.   # multa da pane-seca em dinheiro (E12b: 18 panes x 12 = 216 > renda)
        # reboque (E12 v6): pane NAO devolve 15 de fuel — devolve so a RACAO pra
        # rastejar ate o posto mais perto (galao do guincho). 5 baterias
        # mostraram que a pane e ESCOLHA: 15 de fuel por 18 passos e aceita
        # como "posto gratis lento" (15-19 panes/vida em todo braco, pobre ou
        # rico, Reativo/Hora/Corpo) e a gordura nunca acumula.
        s.reboque=False
        # E12 (doc 26): energia em DOIS compartimentos + peso no chassi.
        #   relogio  relogio de 24h sempre (features sin/cos da hora; fase por mundo)
        #   noite    22h-6h: posto FECHADO e so 1 dos NPX passageiros acordado
        #            (noite magra: e o que faz a energia MORDER — sem isto o
        #            teto da reserva e zero, vide N13: av_fuel=0 no base)
        #   reserva  sobra do tanque acima de NIVEL vira RESERVA a meia-noite
        #            (perde PERDA_ARMAZ); tanque vazio mobiliza a reserva em vez
        #            de pane (para TPAR_MOB passos, perde `perda` — sorteada POR
        #            MUNDO se perda_var: so se descobre vivendo)
        #   peso     1 + WF*fuel/cap + WR*res/RES_MAX multiplica tempo de viagem,
        #            consumo de fuel/agua/aquecimento, fome e fadiga; divide a
        #            recuperacao do descanso ("nao dorme tao bem")
        #   cerebro_come  custo neural sai do TANQUE (calorias), nao do fitness
        s.relogio=False; s.noite=False; s.reserva=False; s.peso=False
        s.perda_var=True; s.cerebro_come=False
        s.greve=0          # E12-v9: a cada N dias o posto fecha o DIA INTEIRO (escassez rara e grande)
        # E13 (doc 27): CORPO = CARRO. Dano real acumulado, morte.
        #   corpo    vida 0..100; avarias FEREM (pane/furo/oleo/quente), rodar
        #            machucado fere por passo, ferido = lento e bebe mais,
        #            oficina repara REPARO, vida<=0 = morte (para de entregar)
        s.corpo=False
        s.D_PANE=6.; s.D_FURO=5.; s.D_OLEO=12.; s.D_QUENTE=10.; s.D_RODAR=.15
        s.REPARO=30.; s.K_SAUDE=.6
        s.reserva_posto=0.   # >0: posto tambem enche a reserva com este tanto (gordura entra facil)
        s.sono_come=0.       # >0: cada descanso custa este tanto de fuel (dormir custa caloria)
        # E13f (Leonardo): "calculo base geral e o peso extra afeta" + "gordura acumulavel ao longo do tempo"
        #   massa    peso = massa/chassi, massa = chassi + kg_fuel*fuel + kg_res*res + kg_pax*(carregando)
        #            (gasolina 0.75 kg/L; gordura pesa 3.3x mais por unidade; passageiro 80 kg)
        #   reserva_continua  >0: a CADA passo esta fracao da sobra do tanque acima de NIVEL
        #            vira gordura (com PERDA_ARMAZ) — substitui o lote da meia-noite
        s.massa=False; s.M_CHASSI=1000.; s.KG_FUEL=.75; s.KG_RES=2.5; s.KG_PAX=80.
        s.reserva_continua=0.
        # E13l: sono em BLOCO — a noite, descansar = dormir ate as 6h (fadiga zera; nao roda de madrugada)
        s.sono_bloco=False
        # E14b: a VIDA no fitness — pena por morrer (0 = identidade). Sem isto a morte nao custa
        #       fitness (quem morre no dia 4 entrega quase o mesmo) e nao e selecionada.
        s.pena_morte=0.
        s.pena_prop=False      # E27: pena proporcional a VIDA PERDIDA — morrer cedo custa 2x pena, no fim ~0 (False = fixa)
        # E19 DENTES (pacote): ficar parado NAO pode ser de graca (um ser que nao faz nada por
        #   5 dias terminava com vida 100, fome 100, fit 0 — o atrator "parar" dos colapsos)
        #   fome_mata   dano de vida por passo quando fome >= FOME_CRIT, escalado ate fome=100
        #   divida_mata dinh <= -LIMITE_DIVIDA (economia) = perde o carro = vida 0
        s.fome_mata=0.; s.FOME_CRIT=90.; s.divida_mata=False
        s.REFEICAO=45.         # quanto uma refeicao tira de fome (45 = identidade; fome sobe ~77/dia)
        s.fome_gracia=0        # E25 infancia individual: passos de cada vida em que a fome NAO fere (0 = identidade)
        s.comida_no_posto=False  # E19d: o posto tambem vende comida (so 3 de 26 nos tem comida; o ser ja sabe ir ao posto)
        # [E15 economia] flags/constantes — SO o agente E15 edita este bloco
        # doc 29. economia=False => IDENTIDADE BIT-EXATA (nada aloca, nada sorteia,
        # nenhum draw dos geradores do mundo se desloca).
        #   economia   dinheiro compra TUDO: aluguel+agua por dia, imposto ao RECEBER
        #              (pela aliquota do distrito de ORIGEM da corrida) e ao GASTAR
        #              (preco base x multiplicador do distrito ATUAL x (1+aliquota)),
        #              divida com juros em vez de morte por dinheiro, reboque em CALORIAS.
        s.economia=False
        s.D_DIST=3                        # distritos por cidade (particao espacial k-means)
        s.ALIQ=(.10,.20,.30)              # aliquota por distrito (receber E gastar)
        s.PMUL=(0.8,1.0,1.3)              # multiplicador de preco dos servicos por distrito
        s.dist_sorteia=True               # QUAL distrito e caro: sorteado POR MUNDO (lei oculta,
                                          # como npc_base/perda) — geografia nao se decora
        s.ALUGUEL=6.; s.AGUA=2.           # cobranca diaria a meia-noite, em dinheiro
        s.LIMITE_DIVIDA=60.               # piso do saldo: dinh nunca abaixo de -LIMITE
        s.JUROS=.05                       # juros diarios sobre o saldo NEGATIVO
        s.KCAL_REBOQUE=1.0                # calorias por unidade de distancia ate o posto (gordura -> tanque)
        s.KCAL_VIDA=0.                    # >0: o que a gordura nao cobrir vira VIDA (tanto por kcal) em vez
                                          # de sair do TANQUE. O tanque e a moeda que leva ao posto: cobrar
                                          # nele e regra 12 na moeda calorica (mede-se a espiral no doc 29 §5)
        # ATENCAO (N16 / regra 12): com economia o reboque cobra CALORIAS, entao
        # `pane_dinh` TEM que ser 0 (o Lote levanta erro se nao for) e o runner
        # baixa D_PANE de 6 para 3 — senao a pane pune tres vezes (vida+caloria+dinheiro).
        # [E15 fim]
        # [E16 glandulas] flags/constantes — SO o agente E16 edita este bloco
        # Doc 30. O hormonio e do CORPO, nao do cerebro: K integradores com
        # vazamento vivem no Lote, sao alimentados por DEFICITS (tonicos) e
        # EVENTOS de ganho do passo anterior (fasicos), e devolvem GANHOS
        # MULTIPLICATIVOS. tau/a/b sao GENES (src/glandulas.py). O cerebro so
        # SENTE h (features e16_a/e16_b) e e modulado por ele.
        # glandulas=False => identidade bit-exata (nada alocado, nada roda).
        s.glandulas=False
        s.GL_K=2               # numero de glandulas (sem nome: a selecao decide)
        s.KAPPA_H=.25          # calorias/passo por unidade de h (gordura primeiro)
        s.H_MAX=2.             # teto de cada h: clamp [0, H_MAX]
        s.GL_TAU_MIN=10.; s.GL_TAU_MAX=2000.   # tau em PASSOS (gene -> sigmoide -> log-uniforme)
        s.GL_GAMMA_EV=.5       # ganho dos EVENTOS (impulso). Deficits entram
                               # normalizados por 1/tau: amplitude e tau viram
                               # genes independentes (regra 15: escala do gene).
        s.GL_ESCALA_B=.25      # escala dos ganhos de saida (EXP10: 0.5-1.0 ajuda, 8.0 destroi)
        # botoes moduláveis, na ordem das colunas de b:
        #   0 necessidade  ganho do score de servico   (arquitetura, extra_serv)
        #   1 exploracao   ruido Gumbel na decisao     (arquitetura, opt-in)
        #   2 metabolismo  consumo de COMBUSTIVEL      (bloco 2 do passo)
        #   3 sono         recuperacao de fadiga       (bloco 2 do passo)
        #   4 velocidade   CALCULADO, NAO aplicado     (precisa de 1 linha fora do bloco; doc 30 §6)
        s.GL_CANAIS=('necessidade','exploracao','metabolismo','sono','velocidade')
        s.GL_LIM=((.25,2.5),(0.,3.),(.70,1.30),(.50,2.),(.70,1.30))  # clamp por canal (N9/regra 5: limitar a alavanca)
        s.gl_censo=True        # acumuladores de correlacao h x sinal (diagnostico)
        s.gl_regime=0.         # >0: REGIME oculto — o consumo do combustivel oscila
                               # por dia (fase por mundo). "Preco variavel" na moeda
                               # de energia, sem tocar no E15.
        s.gl_regime_dias=2.    # periodo do regime, em dias
        # [E16 fim]
        # [E17 produtos] flags/constantes — SO o agente E17 edita este bloco
        # [E17 fim]
        # [E42 mundo] flags/constantes da CIDADE GRANDE — SO o agente E42-mundo
        # edita este bloco. Doc 42. Todas nascem no comportamento de hoje:
        # moradia=False, pax_cruza=0, tarifa_distrito=False, rua_nao_dorme=False
        # => IDENTIDADE BIT-EXATA (nada aloca, nada sorteia, nenhum draw se desloca).
        #   moradia         m.casa = distrito de NASCIMENTO; descansar no distrito-casa
        #                   e como hoje, fora custa HOTEL (preco base x fator do
        #                   distrito, igual a qualquer gasto); libera os sentidos
        #                   `e_em_casa` e `e_aliq_local` nos slots reservados
        #                   (ex-h_gl0/h_gl1, so quando as glandulas estao desligadas)
        #   HOTEL           preco BASE da diaria fora de casa (x fator do distrito)
        #   ALUGUEL_D       (D,) multiplicador do aluguel por LINHA da tabela de
        #                   precos (None = 1.0). O aluguel e cobrado pelo distrito
        #                   da CASA, nao pelo lugar onde o ser esta.
        #   rua_nao_dorme   parado por fadiga (fad>=95) a NOITE e fora do distrito-casa
        #                   nao repoe fadiga: perde o tempo e acorda cansado
        #   pax_cruza       >0: destino do passageiro ~ 1/(1+d) (nunca o proprio no)
        #                   com no minimo esta FRACAO da massa em OUTRO distrito
        #   tarifa_distrito tarifa = base x distancia x multiplicador de preco do
        #                   distrito de ORIGEM (o imposto pela origem ja e do E15:
        #                   nao duplicar)
        s.moradia=False; s.HOTEL=8.; s.ALUGUEL_D=None
        s.rua_nao_dorme=False; s.pax_cruza=0.; s.tarifa_distrito=False
        # [E42 fim]
        s.RES_MAX=60.; s.NIVEL=50.; s.PERDA_ARMAZ=.10; s.MOB=25.; s.TPAR_MOB=3.
        s.WF=.10; s.WR=.30; s.KAPPA_F=.05

# ============================ MUNDO EM LOTE ============================
# REGRA DE PERF (esta reescrita rendeu ~10x; nao regredir):
#   1. NENHUM sync GPU->CPU no loop quente: nada de `if tensor.any():`,
#      `.item()`, `.nonzero()` — toda ramificacao vira mascara.
#   2. NENHUM tensor novo de constante por passo (torch.tensor(...) e H2D):
#      constantes vivem em __init__.
#   3. Contadores sao tensores no device (int python vira guard/recompile
#      no torch.compile).
#   4. Amostragem categorica por Gumbel-argmax (multinomial faz sync).
class Lote:
    """B = P genomas x NC cidades x R replicas, tudo num tensor so."""
    def __init__(s, cidades, P, cfg, seed=0, R=1):
        s.cfg = cfg
        NC = len(cidades); s.NC, s.P, s.R = NC, P, R
        n = cidades[0]['n']; s.n = n
        s.B = B = P*NC*R
        st = lambda k, dt=torch.float32: torch.stack(
            [torch.tensor(c[k], device=DEV, dtype=dt) for c in cidades])
        s.Aa=st('A',torch.long); s.Wa=st('W'); s.DIa=st('DI')
        s.serva=st('serv'); s.grpa=st('grp',torch.long); s.tema=st('tem')
        if cfg.comida_no_posto:   # E19d: comida disponivel onde ha posto (serva[...,1] herda serva[...,0])
            s.serva = s.serva.clone(); s.serva[:,:,1] = torch.maximum(s.serva[:,:,1], s.serva[:,:,0])
        ds = []
        for c in range(NC):
            linha = []
            for j in range(5):
                m = cidades[c]['serv'][:,j] > 0
                linha.append(s.DIa[c][:, torch.tensor(m, device=DEV)].min(1).values
                             if m.any() else torch.full((n,), 20., device=DEV))
            ds.append(torch.stack(linha))
        s.dsa = torch.stack(ds)                       # (NC,5,n)
        s.dposto = s.dsa[:,0,:].clone()               # distancia real ao posto (reboque)
        if cfg.mundo == 'semgps':
            # oraculo removido NA FONTE: features ds e a leitura direta do
            # corpo/hibrido enxergam a mesma constante (ninguem trapaceia)
            s.dsa = torch.full_like(s.dsa, 20.)
        # mundo b pertence ao genoma gidx[b] e a cidade cidx[b]
        s.cidx = torch.arange(NC, device=DEV).repeat_interleave(R).repeat(P)
        s.gidx = torch.arange(P, device=DEV).repeat_interleave(NC*R)
        g = torch.Generator(device=DEV); g.manual_seed(seed); s.g = g
        s.gsim = torch.Generator(device=DEV); s.gsim.manual_seed(seed+999983)
        ri = lambda hi, sh: torch.randint(0, hi, sh, generator=g, device=DEV)
        s.no=ri(n,(B,)); s.indo=torch.full((B,),-1,dtype=torch.long,device=DEV)
        s.rest=torch.zeros(B,device=DEV); s.tpar=torch.zeros(B,device=DEV)
        s.fuel=torch.full((B,),85.,device=DEV); s.fome=torch.full((B,),10.,device=DEV)
        s.fad=torch.full((B,),10.,device=DEV);  s.pneu=torch.full((B,),100.,device=DEV)
        s.temp=torch.full((B,),25.,device=DEV); s.oleo=torch.full((B,),100.,device=DEV)
        s.dinh=torch.full((B,),60.,device=DEV); s.up=torch.zeros(B,9,device=DEV)
        s.po_=torch.full((B,),-1,dtype=torch.long,device=DEV)
        s.pd_=torch.full((B,),-1,dtype=torch.long,device=DEV)
        s.ent=torch.zeros(B,device=DEV); s.rec=torch.zeros(B,device=DEV)
        # censo de avarias por CAUSA (diagnostico; mascaras somadas, zero sync)
        s.av_fuel=torch.zeros(B,device=DEV); s.av_furo=torch.zeros(B,device=DEV)
        s.av_oleo=torch.zeros(B,device=DEV); s.av_quente=torch.zeros(B,device=DEV)
        s.par_fad=torch.zeros(B,device=DEV)
        s.imp=torch.zeros(B,device=DEV); s.avar=torch.zeros(B,device=DEV)
        s.melh=torch.zeros(B,device=DEV)
        s.fase=ri(2,(B,n)).float(); s.tsem=ri(cfg.per,(B,n)).float()
        if cfg.mundo == 'ruas':
            # nos CRONICOS por mundo: rua que sempre entope. Por mundo (nao por
            # cidade) de proposito: evolucao entre episodios nao tem como decorar
            # — so memoria DENTRO da vida resolve.
            cron = (torch.rand(B,n,generator=g,device=DEV) < cfg.cron_frac).float()
            s.npc_base = cron*(cfg.cron_alto*(0.6+0.4*torch.rand(B,n,generator=g,device=DEV))) \
                         + (1-cron)*0.08
            s.npc = s.npc_base.clone()
        else:
            s.npc_base = None
            s.npc=torch.rand(B,n,generator=g,device=DEV)*cfg.trafego*2
        s.po=ri(n,(B,NPX)); s.pd=ri(n,(B,NPX))
        s.t=torch.zeros((),dtype=torch.long,device=DEV)
        if cfg.com_agua:
            # agua do radiador; a LEI (aquecimento por deficit) e SORTEADA POR
            # MUNDO: a evolucao nao decora — so aprendizado EM VIDA alcanca
            s.agua = torch.full((B,), 80., device=DEV)
            s.k_agua = 1.0 + 3.0*torch.rand(B, generator=g, device=DEV)
            s.fase_dia = ri(cfg.dia, (B,)).float()
        # constantes cacheadas (regra 2)
        s.ARB   = torch.arange(B, device=DEV)
        s.AR5   = torch.arange(5, device=DEV)
        s.CUSTO = torch.tensor([2.,3.,0.,10.,26.], device=DEV)
        s.MP    = torch.tensor([0,1,2,3,3], device=DEV)
        s.UNS   = torch.ones(B, GMAX, 1, device=DEV)
        # estado OCULTO do mundo (o taxi nunca ve estes tensores)
        if cfg.mundo in ('hotspot','mare'):
            s.hot = ri(n,(B,))                      # polo atual
            if cfg.mundo == 'mare':
                s.polo2 = ri(n,(B,))                # segundo polo
                s.tmare = ri(cfg.per_mare,(B,)).float()
            # respawn ja concentrado no polo desde o inicio
            for k in range(NPX):
                s.po[:,k] = s._spawn_polo()
        # E12: relogio + reserva (sorteios no FIM: nao desloca os draws acima)
        s.RELOGIO = bool(cfg.relogio or cfg.com_agua)
        if s.RELOGIO and not cfg.com_agua:
            s.fase_dia = ri(cfg.dia, (B,)).float()
        elif not s.RELOGIO:
            s.fase_dia = torch.zeros(B, device=DEV)
        s.res = torch.zeros(B, device=DEV)                  # reserva (gordura)
        # E13: corpo — vida (HP) e censo
        s.vida = torch.full((B,), 100., device=DEV)
        s.recusa = torch.zeros(B, dtype=torch.bool, device=DEV)   # [E38] recusa de passageiro (a arq escreve em atualizar)
        s.bem_soma = torch.zeros(B, device=DEV)                    # [E41 B] integral do bem-estar
        s.t_vida = torch.zeros(B, device=DEV); s.n_oficina = torch.zeros(B, device=DEV)
        s.sono_soma = torch.zeros(B, device=DEV); s.dano_soma = torch.zeros(B, device=DEV)
        s.n_bloco = torch.zeros(B, device=DEV)   # E13l: noites dormidas em bloco
        # [E15 economia] estado (distrito por no, precos, divida, censo) — SO E15
        if cfg.economia:
            if cfg.pane_dinh:
                raise ValueError('E15: com economia=True o reboque cobra CALORIAS — '
                                 'ponha cfg.pane_dinh=0 (N16 / regra 12: multa na moeda '
                                 'que compra a recuperacao = espiral de pobreza).')
            D = cfg.D_DIST
            # [E42 mundo] D generalizado (era 3 fixo): as tabelas TEM que ter D linhas,
            # senao AL[pr] indexa fora / ignora linhas em silencio.
            if len(cfg.ALIQ) != D or len(cfg.PMUL) != D:
                raise ValueError(f'E15/E42: D_DIST={D} mas ALIQ tem {len(cfg.ALIQ)} e '
                                 f'PMUL tem {len(cfg.PMUL)} valores (use cfg_cidade_grande).')
            # DISTRITOS por particao espacial (k-means determinista: sementes por
            # ponto-mais-distante + 8 iteracoes de Lloyd). Roda 1x por Lote, no host.
            # A geografia e a MESMA em todos os mundos da cidade; o que muda por
            # mundo e QUAL distrito e caro (permutacao oculta abaixo).
            dl = []
            for cd in cidades:
                p = cd['pos']; C = None
                ce = [int(np.argmax(((p - p.mean(0))**2).sum(1)))]
                for _ in range(D-1):
                    dd = np.min(np.stack([((p - p[k])**2).sum(1) for k in ce]), 0)
                    ce.append(int(np.argmax(dd)))
                C = p[ce].copy()
                for _ in range(8):
                    lb = np.argmin(((p[:,None,:] - C[None,:,:])**2).sum(2), 1)
                    for k in range(D):
                        mk = lb == k
                        if mk.any(): C[k] = p[mk].mean(0)
                lb = np.argmin(((p[:,None,:] - C[None,:,:])**2).sum(2), 1)
                dl.append(lb)
            s.e15_dist = torch.tensor(np.stack(dl), device=DEV, dtype=torch.long)   # (NC,n)
            # gerador PROPRIO: nao desloca nenhum draw de `g` — com economia=False a
            # identidade e bit-exata, e com economia=True o mundo (npc, perda, spawn)
            # e o MESMO do braco sem economia. So a economia muda.
            ge = torch.Generator(device=DEV); ge.manual_seed(seed + 777771)
            AL = torch.tensor(cfg.ALIQ, device=DEV, dtype=torch.float32)
            PM = torch.tensor(cfg.PMUL, device=DEV, dtype=torch.float32)
            pr = (torch.rand(B, D, generator=ge, device=DEV).argsort(1) if cfg.dist_sorteia
                  else torch.arange(D, device=DEV)[None,:].expand(B, D))
            s.e15_aliq = AL[pr]; s.e15_pmul = PM[pr]      # (B,D)
            # posto do distrito na tabela de precos (0 = mais barato). A telemetria
            # por distrito e indexada por AQUI, nao pela etiqueta geografica: com a
            # permutacao por mundo, so o POSTO diz se o ser prefere o barato.
            s.e15_rank = pr
            s.e15_fat  = s.e15_pmul*(1.+s.e15_aliq)       # fator de preco local (gastar)
            fa = PM*(1.+AL); fmin = float(fa.min()); fmax = float(fa.max())
            s.e15_fatn = (s.e15_fat - fmin)/max(fmax-fmin, 1e-6)   # feature e15_b em 0..1
            s.ARD = torch.arange(D, device=DEV)
            s.e15_dorig = torch.zeros(B, dtype=torch.long, device=DEV)  # distrito de ORIGEM da corrida
            s.e15_d0 = torch.zeros(B, device=DEV)        # saldo antes das compras (ver passo)
            z = lambda: torch.zeros(B, device=DEV)
            s.imp_orig=z(); s.imp_gastar=z(); s.aluguel_pago=z(); s.juros_pago=z()
            s.div_max=z(); s.t_divida=z(); s.kcal_reb=z()
            s.ent_dist=torch.zeros(B,D,device=DEV); s.t_dist=torch.zeros(B,D,device=DEV)
        # [E15 fim]
        # [E42 mundo] MORADIA + destino que cruza distrito — SO o agente E42-mundo.
        # Gerador PROPRIO (g42): ligar a moradia/o destino cruzado NAO desloca
        # nenhum draw de `g` nem de `gsim` — o mundo (npc, perda, spawn de
        # passageiro, congestao) fica IDENTICO ao do braco sem as flags.
        s.g42 = torch.Generator(device=DEV); s.g42.manual_seed(seed + 424243)
        if cfg.moradia or cfg.pax_cruza or cfg.tarifa_distrito or cfg.rua_nao_dorme:
            if not cfg.economia:
                raise ValueError('E42: moradia/pax_cruza/tarifa_distrito/rua_nao_dorme '
                                 'precisam de cfg.economia=True (distritos vem do E15).')
        if cfg.moradia:
            D = cfg.D_DIST
            # CASA = distrito onde NASCEU (v1: nao muda na vida)
            s.casa = s.e15_dist[s.cidx, s.no]                       # (B,)
            AM = torch.tensor(cfg.ALUGUEL_D if cfg.ALUGUEL_D is not None else (1.,)*D,
                              device=DEV, dtype=torch.float32)
            if AM.numel() != D:
                raise ValueError(f'E42: ALUGUEL_D tem {AM.numel()} valores, D={D}')
            s.e42_alug = AM[s.e15_rank]              # (B,D) aluguel por distrito GEOGRAFICO
            # aliquota do distrito atual NORMALIZADA 0..1 (regra 15: escala do
            # gene — crua ela e 0.05..0.35 e o peso teria de ser 3x maior que
            # o das outras features pra dizer a mesma coisa)
            amin = float(AL.min()); amax = float(AL.max())
            s.e42_aliqn = (s.e15_aliq - amin)/max(amax - amin, 1e-6)
            z42 = lambda: torch.zeros(B, device=DEV)
            s.t_casa=z42(); s.n_hotel=z42(); s.e42_hotel=z42(); s.n_rua=z42()
            s.ent_cruza=z42()
        if cfg.pax_cruza:
            # destino inicial pela MESMA regra do respawn (senao os NPX primeiros
            # passageiros do episodio seriam uniformes e o mundo mudaria com o tempo)
            for k in range(NPX):
                s.pd[:,k] = s._spawn_destino(s.po[:,k])
        # [E42 fim]
        # [E16 glandulas] estado (h, genes copiados no reset, censo) — SO E16
        # NAO consome o Generator `g`: ligar as glandulas nao desloca nenhum
        # sorteio do mundo (`s.perda` logo abaixo continua identico).
        if cfg.glandulas:
            K = cfg.GL_K; s.GL_NX = 10        # 6 deficits + 4 eventos do passo anterior
            s.h    = torch.zeros(B, K, device=DEV)            # hormonios (estado do CORPO)
            s.tau  = torch.full((B, K), 100., device=DEV)     # gene: constante de tempo
            s.G_a  = torch.zeros(B, K, s.GL_NX, device=DEV)   # gene: pesos de entrada
            s.G_b  = torch.zeros(B, K, 5, device=DEV)         # gene: pesos de saida
            s.mult = torch.ones(B, 5, device=DEV)             # ganhos (lidos pelo cerebro no passo seguinte)
            s.ev   = torch.zeros(B, 4, device=DEV)            # entregou, abasteceu, consertou, descansou
            s.GL_LO = torch.tensor([a for a, _ in cfg.GL_LIM], device=DEV)
            s.GL_HI = torch.tensor([b for _, b in cfg.GL_LIM], device=DEV)
            s.h_custo = torch.zeros(B, device=DEV)   # calorias gastas com hormonio
            s.h_sono  = torch.zeros(B, device=DEV)   # quanto o sono limpou de h
            s.h_soma  = torch.zeros(B, K, device=DEV)
            s.mult_soma = torch.zeros(B, 5, device=DEV)
            s.h_n = torch.zeros((), device=DEV)
            if cfg.gl_censo:
                # somas para correlacao exata h_k x sinal_i, sem nenhum sync
                s.h2_soma = torch.zeros(B, K, device=DEV)
                s.x_soma  = torch.zeros(B, s.GL_NX, device=DEV)
                s.x2_soma = torch.zeros(B, s.GL_NX, device=DEV)
                s.hx_soma = torch.zeros(B, K, s.GL_NX, device=DEV)
        else:
            s.h = None; s.mult = None
        if cfg.gl_regime:
            # regime OCULTO do combustivel: do mundo, nao das glandulas —
            # existe tambem no braco de referencia (fase por mundo via fase_dia)
            s.gl_reg = torch.ones(B, device=DEV)
        # [E16 fim]
        if cfg.perda_var:
            s.perda = .15 + .30*torch.rand(B, generator=g, device=DEV)   # 15..45%
        else:
            s.perda = torch.full((B,), .30, device=DEV)
        s.ARNPX = torch.arange(NPX, device=DEV)
        # telemetria E12 (somas mascaradas, zero sync)
        s.n_mob=torch.zeros(B,device=DEV); s.n_conv=torch.zeros(B,device=DEV)
        s.res_soma=torch.zeros(B,device=DEV); s.conv_soma=torch.zeros(B,device=DEV)
        s.fuel_22=torch.zeros(B,device=DEV); s.n_22=torch.zeros(B,device=DEV)
        s.ent_noite=torch.zeros(B,device=DEV); s.par_noite=torch.zeros(B,device=DEV)
        s.n_posto=torch.zeros(B,device=DEV); s.t_pobre=torch.zeros(B,device=DEV)
    def hora(s):
        """(B,) hora do dia 0..24 (fase oculta por mundo)."""
        return ((s.t.float() + s.fase_dia) % s.cfg.dia) / s.cfg.dia * 24.
    def noite_(s):
        if not s.cfg.noite:
            return None
        h = s.hora(); return (h >= 22.) | (h < 6.)
    def greve_(s):
        """dia de greve do posto: fecha o dia inteiro a cada `greve` dias (passageiros normais)."""
        if not s.cfg.greve:
            return None
        d = ((s.t.float() + s.fase_dia) // s.cfg.dia).long()
        return (d % s.cfg.greve) == (s.cfg.greve - 1)
    def peso_(s):
        """1 + carga no chassi: tanque pesa pouco, reserva pesa muito."""
        if not s.cfg.peso:
            return 1.
        c = s.cfg
        if c.massa:   # E13f: calculo base geral — tudo deriva de massa/chassi
            kg = c.KG_FUEL*s.fuel + c.KG_RES*s.res + c.KG_PAX*(s.pd_ >= 0).float()
            return 1. + kg/c.M_CHASSI
        return 1. + c.WF*s.fuel/s.capf() + c.WR*s.res/c.RES_MAX
    def serv_ab(s, noite=None):
        """servicos ABERTOS no no: posto fecha a noite."""
        sv = s.serva[s.cidx, s.no]
        fech = noite; g = s.greve_()
        if g is not None: fech = g if fech is None else (fech | g)
        if fech is not None:
            sv = sv * torch.cat([(~fech).float()[:,None], torch.ones(s.B,4,device=DEV)],1)
        return sv
    def _spawn_polo(s):
        """(B,) sorteio de no ~ exp(-dist ao polo), para TODOS os mundos de uma
        vez. Gumbel-argmax == softmax-sampling, sem multinomial (que faz sync)."""
        d = s.DIa[s.cidx[:,None].expand(-1,s.n),
                  s.hot[:,None].expand(-1,s.n),
                  torch.arange(s.n, device=DEV)[None,:].expand(s.B,-1)]
        u = torch.rand(s.B, s.n, generator=s.gsim, device=DEV).clamp(min=1e-20)
        return (-d/3. - torch.log(-torch.log(u))).argmax(1)

    # [E42 mundo] destino do passageiro que CRUZA distrito
    def _spawn_destino(s, orig):
        """(B,) destino ~ 1/(1+d(orig,.)), nunca o proprio no, com no minimo
        `cfg.pax_cruza` da massa em OUTRO distrito. Tudo (B,n) na GPU, sorteio
        por Gumbel-argmax (multinomial faz sync). Usa o gerador g42: nao mexe
        no stream do mundo.

        Reescala: se a massa que ja cai fora do distrito for >= f, nao mexe;
        senao multiplica o de fora por f/P_fora e o de dentro por (1-f)/(1-P_fora)
        — a fracao fora fica EXATAMENTE f, sem tocar na forma 1/(1+d) dentro de
        cada lado."""
        n = s.n; f = s.cfg.pax_cruza
        arn = torch.arange(n, device=DEV)[None,:].expand(s.B,-1)
        d = s.DIa[s.cidx[:,None].expand(-1,n), orig[:,None].expand(-1,n), arn]
        w = (1./(1.+d))*(arn != orig[:,None]).float()      # ninguem pega taxi pra ficar parado
        dist = s.e15_dist[s.cidx]                          # (B,n) distrito de cada no
        fora = (dist != dist.gather(1, orig[:,None])).float()
        tot = w.sum(1, keepdim=True).clamp(min=1e-20)
        pf = (w*fora).sum(1, keepdim=True)/tot              # massa que ja cruza
        ef = (f/pf.clamp(min=1e-20)).clamp(min=1.)
        ed = ((1.-f)/(1.-pf).clamp(min=1e-20)).clamp(max=1.)
        w = w*(fora*ef + (1.-fora)*ed)
        u = torch.rand(s.B, n, generator=s.g42, device=DEV).clamp(min=1e-20)
        return (torch.log(w.clamp(min=1e-20)) - torch.log(-torch.log(u))).argmax(1)

    # resolve "qual cidade" por mundo
    def A_(s):    return s.Aa[s.cidx, s.no]
    def W_(s):    return s.Wa[s.cidx, s.no]
    def grp_(s):  return s.grpa[s.cidx, s.no]
    def tem_(s):  return s.tema[s.cidx, s.no]
    def serv_(s): return s.serva[s.cidx, s.no]
    def serv_need(s):
        """servico disponivel PONDERADO pela necessidade (posto so importa se falta combustivel)"""
        sv = s.serv_ab(s.noite_())
        nec = torch.stack([1-s.fuel/s.capf(), s.fome/100., s.fad/100.,
                           torch.maximum(1-s.pneu/100., s.temp/120.),
                           (s.dinh/90.).clamp(max=1.)], -1)
        paga = (s.dinh[:,None] >= s.CUSTO[None,:]).float()
        return sv*nec*paga, sv*paga
    def capf(s): return 100+35*s.up[:,0]
    def txp(s):  return 1./((1+.7*s.up[:,1])*(1+.5*s.up[:,7]))
    def txt(s):  return 1./(1+.7*s.up[:,2])
    def txo(s):  return 1./(1+.8*s.up[:,8])
    def vel(s):  return 1./(1+.3*s.up[:,3])
    def tar(s):  return 1.+.28*s.up[:,4]
    def obs(s):
        B, G = s.B, GMAX
        viz = s.A_(); val = viz >= 0; vz = viz.clamp(min=0)
        ce = s.cidx[:,None].expand(-1,G)
        # passageiro livre mais proximo
        dpo = s.DIa[s.cidx[:,None].expand(-1,NPX), s.no[:,None].expand(-1,NPX), s.po]
        noite = s.noite_()
        if noite is not None:
            # noite magra: so o passageiro do slot 0 esta acordado
            dorme = noite[:,None] & (s.ARNPX[None,:] > 0)
            dpo = torch.where(dorme, torch.full_like(dpo, 1e6), dpo)
        VIS_LIMITADA = s.cfg.mundo in ('cego','hotspot','mare')
        if VIS_LIMITADA:
            # VISAO LIMITADA: passageiro alem do raio nao existe para o taxi.
            # (ruas/semgps mantem visao global: cada mundo esconde UMA coisa so)
            dpo = torch.where(dpo <= s.cfg.raio, dpo, torch.full_like(dpo, 1e6))
        kb = dpo.argmin(1)
        po_alvo = s.po.gather(1, kb[:,None]).squeeze(1)
        alvo = torch.where(s.pd_>=0, s.pd_, po_alvo)
        dal = s.DIa[ce, vz, alvo[:,None].expand(-1,G)]
        if VIS_LIMITADA:
            # sem passageiro visivel e sem corrida: distancia CONSTANTE em todos
            # os vizinhos = zero informacao direcional. E o que abre espaco para
            # a memoria pagar (ou nao — mundo cego e o controle).
            ve = (dpo.min(1).values < 1e5) | (s.pd_ >= 0)
            dal = torch.where(ve[:,None], dal, torch.full_like(dal, 2*s.cfg.raio))
        cus = s.W_()
        if s.cfg.mundo == 'ruas' and not s.cfg.clarividente:
            # congestao dos vizinhos INVISIVEL: so se sente ao pisar no no.
            # A feature fica (I8), mas carrega zero informacao.
            cong = torch.zeros_like(cus)
        else:
            cong = torch.gather(s.npc, 1, vz)
        gs = s.grp_(); fn = torch.gather(s.fase, 1, s.no[:,None]).expand(-1,G)
        vd = ((gs.float()==fn) | (s.tem_()[:,None]==0)).float()*2-1
        ds = s.dsa[s.cidx[:,None,None].expand(-1,5,G),
                   s.AR5[None,:,None].expand(B,-1,G),
                   vz[:,None,:].expand(-1,5,-1)]              # (B,5,G)
        if s.cfg.mundo == 'semgps':
            # feature ZERADA (nao constante!): constante desloca movimento vs
            # servico e paralisa o perito — zero e contribuicao exata nula.
            ds = torch.zeros_like(ds)
        if s.RELOGIO:
            ang = s.hora()*(2*3.14159265/24.)
            hsin, hcos = torch.sin(ang), torch.cos(ang)
        else:
            hsin = hcos = torch.zeros_like(s.fuel)      # sem relogio: zero info
        est = torch.stack([s.fuel/s.capf(), s.fome/100, s.fad/100, s.pneu/100,
                           s.temp/120, s.oleo/100, (s.dinh/120).clamp(max=1.),
                           (s.pd_>=0).float(),
                           s.res/s.cfg.RES_MAX, hsin, hcos,
                           1. - s.vida/100.,
                           # [E15 features] e15_a = divida relativa, e15_b = preco local
                           # (fator do distrito ATUAL normalizado 0..1). Zero sem economia.
                           ((-s.dinh/s.cfg.LIMITE_DIVIDA).clamp(0., 1.) if s.cfg.economia
                            else torch.zeros_like(s.fuel)),
                           (s.e15_fatn.gather(1, s.e15_dist[s.cidx, s.no][:,None]).squeeze(1)
                            if s.cfg.economia else torch.zeros_like(s.fuel)),
                           # [E16 features] h/H_MAX de cada glandula: o cerebro SENTE o
                           # hormonio (nao o controla). Zero sem cfg.glandulas.
                           # [E42 mundo] os MESMOS dois slots viram `e_em_casa` e
                           # `e_aliq_local` quando ha moradia e nao ha glandulas
                           # (as duas linhas nunca rodam juntas; ver NOMES_F em rodar.py)
                           (s.h[:,0]/s.cfg.H_MAX) if s.cfg.glandulas else
                           ((s.e15_dist[s.cidx, s.no] == s.casa).float() if s.cfg.moradia
                            else torch.zeros_like(s.fuel)),
                           (s.h[:,1]/s.cfg.H_MAX) if (s.cfg.glandulas and s.cfg.GL_K > 1) else
                           (s.e42_aliqn.gather(1, s.e15_dist[s.cidx, s.no][:,None]).squeeze(1)
                            if s.cfg.moradia else torch.zeros_like(s.fuel))], -1)   # E12: reserva+hora; E13: dano
        F = torch.cat([(-dal/6.)[...,None], (-cus/4.)[...,None], (-cong/2.)[...,None],
                       vd[...,None], (-ds.permute(0,2,1)/6.),
                       est[:,None,:].expand(-1,G,-1),
                       s.UNS], -1)
        return F, val

NF = 1+1+1+1+5+16+1  # 26 features por candidato (ver NOMES_F em rodar.py)
                     # 4 slots reservados (E15 economia x2, E16 glandulas x2): zero ate serem usados
                     # E13 (2026-09-02): +e_dano (1-vida/100) — zero sem corpo
                     # E12 (2026-09-01): +reserva, +sin(hora), +cos(hora) — zero
                     # nos mundos sem relogio/reserva (contribuicao exata nula)

# blocos do genoma padrao NP=36 — usados na telemetria de alocacao
BLOCOS = {'features': (0, NF), 'servico': (NF, NF+6),
          'memoria': (NF+6, NF+12), 'corpo': (NF+12, NF+18)}

def alocacao(W, elite_n):
    """Como a POPULACAO distribui massa de peso por bloco, nesta geracao.
    E o dado que mostra o cerebro se organizando da ger 0 ao fim: bloco que a
    evolucao usa engorda |w|; bloco ignorado murcha ou vira ruido parado."""
    out = {}
    for nome, (a, b) in BLOCOS.items():
        if b <= W.shape[1]:
            out[nome] = round(float(W[:elite_n, a:b].abs().mean()), 4)
    return out

# ============================ PASSO ============================
def passo(m, esc):
    """esc: (B,) 0..GMAX-1 = vizinho | GMAX..GMAX+4 = servico
    Tudo mascarado, zero ramificacao dependente de dado (regra 1)."""
    c = m.cfg; B = m.B; m.t += 1
    m.tsem += 1; v = m.tsem >= c.per
    m.fase = torch.where(v, 1-m.fase, m.fase)
    m.tsem = torch.where(v, torch.zeros_like(m.tsem), m.tsem)
    m.temp = (m.temp-1.6).clamp(min=25.)
    # E12: relogio, noite, peso, reserva
    noite = m.noite_(); peso = m.peso_()
    # E13: corpo — morto nao age; ferido e lento e bebe mais
    viva = (m.vida > 0) if c.corpo else None
    saude = (1. + c.K_SAUDE*(1. - m.vida/100.)) if c.corpo else 1.
    if c.reserva:
        # MEIA-NOITE: sobra do tanque acima de NIVEL vira reserva (com perda de
        # armazenamento). So converte o que CABE; o resto fica no tanque.
        pos_prev = (m.t - 1 + m.fase_dia.long()) % c.dia
        pos_now  = (m.t + m.fase_dia.long()) % c.dia
        meia = (pos_now < pos_prev).float()
        if c.reserva_continua:   # E13f: acumula devagar, a cada passo, so a fracao da sobra
            sobra = (m.fuel - c.NIVEL).clamp(min=0) * c.reserva_continua
        else:
            sobra = (m.fuel - c.NIVEL).clamp(min=0) * meia
        cabe = (c.RES_MAX - m.res) / (1 - c.PERDA_ARMAZ)
        conv = torch.minimum(sobra, cabe)
        m.res = m.res + conv*(1 - c.PERDA_ARMAZ)
        m.fuel = m.fuel - conv
        m.n_conv += (conv > 0).float(); m.conv_soma += conv
        m.res_soma += m.res
    if m.RELOGIO:
        h = m.hora()
        h22 = ((h >= 22.) & (h < 22. + 24./c.dia)).float()   # 1 passo por dia
        m.fuel_22 += m.fuel*h22; m.n_22 += h22
    # entrega
    # [E16 glandulas: atualizar h e calcular multiplicadores (metab, sono, vel) — SO E16]
    if c.gl_regime:
        # REGIME OCULTO DO MUNDO (nao das glandulas): o combustivel fica caro/
        # barato por dia, com fase POR MUNDO. Vive fora do `if c.glandulas` de
        # proposito — senao o braco de referencia nao roda no mesmo mundo e a
        # comparacao vira placebo (foi o que aconteceu na 1a rodada da fase a).
        dia_ = (m.t.float() + m.fase_dia) / c.dia
        m.gl_reg = 1. + c.gl_regime*torch.cos(6.2831853*dia_/c.gl_regime_dias)
    if c.glandulas:
        # x = 6 DEFICITS (tonicos, continuos) + 4 EVENTOS do passo ANTERIOR
        # (fasicos: entregou/abasteceu/consertou/descansou). Ninguem da nome as
        # glandulas: quem correlaciona com o que e resultado da selecao.
        xd = torch.stack([(1. - m.fuel/m.capf()).clamp(0., 1.), m.fome/100., m.fad/100.,
                          1. - m.vida/100., m.temp/120., (m.dinh < 2.).float()], -1)
        inv = 1./m.tau                                    # (B,K)
        # deficit entra NORMALIZADO por 1/tau (regime permanente h* = Sigma a*x,
        # independente de tau) e evento entra como IMPULSO de ganho fixo: assim
        # tau governa so a MEMORIA da glandula, nao a amplitude (regra 15).
        drive = (m.G_a[:,:,:6]*xd[:,None,:]).sum(-1)*inv \
              + (m.G_a[:,:,6:]*m.ev[:,None,:]).sum(-1)*c.GL_GAMMA_EV
        m.h = (m.h*(1. - inv) + drive).clamp(0., c.H_MAX)
        # ganho_j = 1 + Sigma_k b_kj h_k, limitado por canal (N9: alavanca nova
        # x peso evoluido = co-adaptacao; o clamp e o que impede o 8.0 do EXP10)
        m.mult = torch.clamp(1. + (m.G_b*m.h[:,:,None]).sum(1), m.GL_LO, m.GL_HI)
        m.h_soma += m.h; m.mult_soma += m.mult; m.h_n = m.h_n + 1.
        if c.gl_censo:
            x = torch.cat([xd, m.ev], -1)                 # (B,10)
            m.h2_soma += m.h*m.h; m.x_soma += x; m.x2_soma += x*x
            m.hx_soma += m.h[:,:,None]*x[:,None,:]
    # [E16 fim]
    ch = (m.pd_>=0) & (m.no==m.pd_) & (m.rest<=0)
    if viva is not None: ch = ch & viva
    d = m.DIa[m.cidx, m.po_.clamp(min=0), m.pd_.clamp(min=0)]
    br = (c.base+c.km*d)*m.tar()
    # [E42 mundo] TARIFA pelo distrito de ORIGEM: base x distancia x multiplicador
    # de preco de onde o passageiro EMBARCOU (m.e15_dorig, gravado no embarque).
    # O imposto pela origem ja e do E15 e sai de `br` — nao se duplica nada aqui.
    if c.tarifa_distrito:
        br = br*m.e15_pmul.gather(1, m.e15_dorig[:,None]).squeeze(1)
    im = br*c.imposto
    m.ent += ch.float(); m.rec += br*ch.float(); m.imp += im*ch.float()
    m.dinh += (br-im)*ch.float()
    m.po_ = torch.where(ch, torch.full_like(m.po_,-1), m.po_)
    m.pd_ = torch.where(ch, torch.full_like(m.pd_,-1), m.pd_)
    livre = m.tpar<=0; m.tpar = (m.tpar-1).clamp(min=0)
    an_ = (m.rest>0) & livre; m.rest = torch.where(an_, m.rest-1, m.rest)
    cg = an_ & (m.rest<=0)
    m.no = torch.where(cg, m.indo.clamp(min=0), m.no)
    m.indo = torch.where(cg, torch.full_like(m.indo,-1), m.indo)
    m.fome = (m.fome+c.fome*peso).clamp(max=100)          # pesado = mais fome
    ap = m.fad>=95
    m.par_fad += ap.float()
    m.tpar = torch.where(ap, torch.full_like(m.tpar,12.), m.tpar)
    # [E42 mundo] DORMIR NA RUA nao repoe: a parada por fadiga so devolve o corpo
    # (fad 95+ -> 40) de dia OU dentro do distrito-casa. A noite e fora de casa o
    # ser perde os 12 passos e acorda do mesmo jeito — o descanso pago (hotel ou
    # casa) passa a ser a UNICA forma de zerar fadiga a noite.
    rep = ap
    if c.rua_nao_dorme and c.moradia and noite is not None:
        rep = ap & ((~noite) | (m.e15_dist[m.cidx, m.no] == m.casa))
        m.n_rua += (ap & (~rep)).float()
    m.fad  = torch.where(rep, torch.full_like(m.fad,40.), m.fad)
    pode = livre & (m.rest<=0) & (~ap)
    if viva is not None: pode = pode & viva
    sv = m.serv_ab(noite)
    # servicos (sem closures: compile-friendly)
    # [E15 economia: preco por distrito, imposto ao gastar, aluguel/agua a meia-noite, juros — SO E15]
    if c.economia:
        # (1) IMPOSTO AO RECEBER, PELA ORIGEM. A entrega acima ja debitou `c.imposto`
        # fixo (linha fora deste bloco); aqui corrige para a aliquota do distrito onde
        # o passageiro EMBARCOU (m.e15_dorig, gravado no embarque, no 2o bloco).
        # im_novo = br*aliq_origem = im_velho - corr  =>  dinh += corr, imp -= corr.
        alq_o = m.e15_aliq.gather(1, m.e15_dorig[:,None]).squeeze(1)
        corr = br*(c.imposto - alq_o)*ch.float()
        m.dinh = m.dinh + corr; m.imp = m.imp - corr
        m.imp_orig = m.imp_orig + br*alq_o*ch.float()
        rk_o = m.e15_rank.gather(1, m.e15_dorig[:,None])          # posto na tabela de precos
        m.ent_dist = m.ent_dist + (rk_o == m.ARD[None,:]).float()*ch.float()[:,None]
        # [E42 mundo] entregas que CRUZARAM distrito (quem entrega esta parado no
        # destino: m.no aqui e o no de destino da corrida que acabou de fechar)
        if c.moradia:
            m.ent_cruza = m.ent_cruza + ch.float()*(m.e15_dist[m.cidx, m.no] != m.e15_dorig).float()
        # (2) ALUGUEL + AGUA + JUROS a meia-noite. Mascara `meia` recalculada aqui:
        # nao depende do bloco da reserva (E12), que so existe com cfg.reserva.
        pos_prev = (m.t - 1 + m.fase_dia.long()) % c.dia
        meia = (((m.t + m.fase_dia.long()) % c.dia) < pos_prev).float()
        if viva is not None: meia = meia*viva.float()    # morto nao paga aluguel
        jur = m.dinh.clamp(max=0.)*c.JUROS*meia          # juros sobre o saldo NEGATIVO
        # [E42 mundo] o aluguel e do distrito da CASA (x ALUGUEL_D), nao de onde o
        # ser esta: morar no distrito caro custa ate 2x. Sem moradia, fator 1.0.
        alug = c.ALUGUEL*(m.e42_alug.gather(1, m.casa[:,None]).squeeze(1) if c.moradia else 1.)
        m.dinh = m.dinh + jur - (alug + c.AGUA)*meia
        m.juros_pago = m.juros_pago - jur
        m.aluguel_pago = m.aluguel_pago + (alug + c.AGUA)*meia
        # saldo ANTES das compras: o 2o bloco reconstroi a partir daqui porque a linha
        # da multa da pane termina em .clamp(min=0) e apagaria a divida todo passo.
        m.e15_d0 = m.dinh
    # [E15 fim]
    o1 = pode & (esc==GMAX+0) & (sv[:,0]>0) & (m.dinh>=2.)
    m.n_posto += o1.float(); m.t_pobre += (m.dinh < 2.).float()
    m.dinh = m.dinh - 2.*o1.float()
    m.fuel = torch.where(o1, torch.minimum(m.fuel + (m.capf() if m.cfg.eco2 else 30.), m.capf()), m.fuel)
    if c.com_agua:
        m.agua = torch.where(o1, torch.full_like(m.agua,100.), m.agua)  # posto enche o radiador
    if c.reserva and c.reserva_posto:
        # E13: gordura entra facil — o posto tambem enche a reserva (comer alem da conta)
        m.res = torch.where(o1, torch.minimum(m.res + c.reserva_posto*(1-c.PERDA_ARMAZ),
                                              torch.full_like(m.res, c.RES_MAX)), m.res)
    o2 = pode & (esc==GMAX+1) & (sv[:,1]>0) & (m.dinh>=3.)
    m.dinh = m.dinh - 3.*o2.float()
    m.fome = torch.where(o2, (m.fome-c.REFEICAO).clamp(min=0), m.fome)
    o3 = pode & (esc==GMAX+2) & (sv[:,2]>0)
    fsono = m.mult[:,3] if c.glandulas else 1.   # E16: canal 3 (sono) liberado; 1.0 sem glandulas
    m.fad = torch.where(o3, (m.fad-30.*fsono/peso).clamp(min=0), m.fad)   # pesado dorme pior
    if c.sono_bloco and noite is not None:
        # E13l: a noite, descansar vira SONO EM BLOCO ate as 6h — decisao do ser, nao roteiro
        ate6 = ((6. - m.hora()) % 24.) / 24. * c.dia
        bloco = o3 & noite
        m.tpar = torch.where(bloco, ate6.round().clamp(min=1.), m.tpar)
        m.fad = torch.where(bloco, torch.zeros_like(m.fad), m.fad)
        m.n_bloco += bloco.float()
    if c.sono_come:
        # E13: dormir custa caloria — do tanque, e se faltar, da gordura (com a perda)
        q  = c.sono_come*o3.float()
        q1 = torch.minimum(m.fuel, q); m.fuel = m.fuel - q1
        q2 = torch.minimum(m.res, (q-q1)/(1-m.perda)); m.res = m.res - q2
        m.sono_soma += q1 + q2*(1-m.perda)
    o4 = pode & (esc==GMAX+3) & (sv[:,3]>0) & (m.dinh>=10.)
    m.dinh = m.dinh - 10.*o4.float()
    m.pneu = torch.where(o4, torch.full_like(m.pneu,100.), m.pneu)
    m.oleo = torch.where(o4, torch.full_like(m.oleo,100.), m.oleo)
    m.temp = torch.where(o4, torch.full_like(m.temp,25.), m.temp)
    if c.corpo:
        m.vida = torch.where(o4, torch.minimum(m.vida + c.REPARO, torch.full_like(m.vida,100.)), m.vida)
        m.n_oficina += o4.float()
    o5 = pode & (esc==GMAX+4) & (sv[:,4]>0) & (m.dinh>=26.)
    m.dinh = m.dinh - 26.*o5.float()
    k = (m.up.sum(1) % 9).long()
    m.up[m.ARB, k] += o5.float(); m.melh += o5.float()
    serv_ok = o1|o2|o3|o4|o5
    # pegar passageiro (qualquer um dos NPX que esteja neste no)
    hit = (m.po == m.no[:,None])
    if noite is not None:
        hit = hit & ~(noite[:,None] & (m.ARNPX[None,:] > 0))   # dormindo: nao embarca
    tem = hit.any(1); ks = hit.float().argmax(1)
    pega = pode & (~serv_ok) & (m.pd_<0) & tem & (~m.recusa)   # [E38] arq pode RECUSAR passageiro (default False = identico)
    m.po_ = torch.where(pega, m.no, m.po_)
    m.pd_ = torch.where(pega, m.pd.gather(1, ks[:,None]).squeeze(1), m.pd_)
    # respawn incondicional-mascarado (o sorteio roda p/ todos, so aplica onde pegou)
    if c.mundo in ('hotspot','mare'):
        novo_po = m._spawn_polo()
    else:
        novo_po = torch.randint(0,m.n,(B,),generator=m.gsim,device=DEV)
    novo_pd = torch.randint(0,m.n,(B,),generator=m.gsim,device=DEV)
    # [E42 mundo] destino que CRUZA distrito. O randint acima segue sendo
    # consumido de proposito: o stream do mundo (npc, spawn de origem, avarias)
    # fica IDENTICO ao braco sem a flag — so o destino muda.
    if c.pax_cruza:
        novo_pd = m._spawn_destino(novo_po)
    ks1 = ks[:,None]
    m.po.scatter_(1, ks1, torch.where(pega, novo_po,
                   m.po.gather(1,ks1).squeeze(1))[:,None])
    m.pd.scatter_(1, ks1, torch.where(pega, novo_pd,
                   m.pd.gather(1,ks1).squeeze(1))[:,None])
    # dinamica OCULTA do mundo
    if c.mundo == 'hotspot':
        # o polo deriva: com prob `deriva` por passo, pula para um vizinho
        # (vizinho uniforme = argmax de U(0,1) mascarado nos validos)
        rw = torch.rand(B, generator=m.gsim, device=DEV) < c.deriva
        vzs = m.Aa[m.cidx, m.hot]                              # (B,GMAX)
        u = torch.rand(B, GMAX, generator=m.gsim, device=DEV)
        pk = torch.where(vzs>=0, u, torch.full_like(u,-1.)).argmax(1)
        novo = vzs.gather(1, pk[:,None]).squeeze(1)
        m.hot = torch.where(rw & (novo>=0), novo, m.hot)
    elif c.mundo == 'mare':
        # dois polos trocam com periodo fixo; a FASE e oculta
        m.tmare += 1
        vira = m.tmare >= c.per_mare
        h = m.hot; m.hot = torch.where(vira, m.polo2, h)
        m.polo2 = torch.where(vira, h, m.polo2)
        m.tmare = torch.where(vira, torch.zeros_like(m.tmare), m.tmare)
    # mover
    mv = pode & (~serv_ok) & (~pega) & (esc<GMAX)
    viz = m.A_(); sel = esc.clamp(max=GMAX-1)
    dst = torch.gather(viz,1,sel[:,None]).squeeze(1)
    val = mv & (dst>=0)
    wru = torch.gather(m.W_(),1,sel[:,None]).squeeze(1)
    npd = torch.gather(m.npc,1,dst.clamp(min=0)[:,None]).squeeze(1)
    cu = wru + npd                       # custo em TEMPO (rest, fadiga)
    if c.mundo == 'ruas':
        # engarrafamento gasta TEMPO, nao tanque: fisico paga so 30% do jam.
        # (sem isto, cronica forte = 20+ de fuel por travessia = morte em serie
        #  — o teto fisico batia no chao antes de qualquer memoria poder pagar)
        cuf = wru + .3*npd
    else:
        cuf = cu
    cuf = cuf*peso*saude                # pesado/ferido bebe mais (fuel/agua/calor)
    if c.glandulas: cuf = cuf*m.mult[:,2]   # E16: canal 2 (metabolismo PLENO: fuel/agua/calor/pneu/oleo)
    falta = val & (m.fuel < cuf*c.fuel)
    if c.reserva:
        # MOBILIZAR a reserva em vez de pane: para TPAR_MOB passos e perde
        # `perda` (lei oculta do mundo). Pane so quando a reserva zerou.
        mob = falta & (m.res > 0)
        q = torch.minimum(m.res, torch.full_like(m.res, c.MOB)) * mob.float()
        m.fuel = m.fuel + q*(1 - m.perda)
        m.res = m.res - q
        m.tpar = torch.where(mob, torch.full_like(m.tpar, c.TPAR_MOB), m.tpar)
        m.n_mob += mob.float()
        sf = falta & (~mob)
    else:
        mob = torch.zeros_like(falta); sf = falta
    m.avar += sf.float(); m.av_fuel += sf.float(); m.tpar = torch.where(sf, torch.full_like(m.tpar,18.), m.tpar)
    pf = c.pane_fuel if c.pane_fuel is not None else (5. if c.eco2 else 15.)
    if c.reboque:
        pf = (m.dposto[m.cidx, m.no]*c.fuel*1.25 + 2.).clamp(min=3.)
        m.fuel = torch.where(sf, pf, m.fuel)
    else:
        m.fuel = torch.where(sf, torch.full_like(m.fuel, pf), m.fuel)
    m.dinh = (m.dinh-c.pane_dinh*sf.float()).clamp(min=0)
    # [E15 economia: reboque cobra CALORIAS (gordura -> tanque) proporcional a d_posto — SO E15]
    if c.economia:
        # (3) IMPOSTO AO GASTAR: preco base x multiplicador do distrito ATUAL x (1+aliquota).
        # As linhas de compra (fora deste bloco) ja debitaram o preco BASE; aqui cobra-se
        # o fator inteiro reconstruindo o saldo a partir de m.e15_d0 — o que tambem desfaz
        # o .clamp(min=0) da multa da pane e deixa a DIVIDA existir.
        dn = m.e15_dist[m.cidx, m.no]                    # distrito do no atual
        fat = m.e15_fat.gather(1, dn[:,None]).squeeze(1)
        oo = torch.stack([o1,o2,o3,o4,o5], 1).float()
        gasto = (oo*m.CUSTO[None,:]).sum(1)              # descanso custa 0: nao paga imposto
        # [E42 mundo] HOTEL: descansar FORA do distrito-casa custa HOTEL (o preco
        # base entra no `gasto`, entao leva o fator do distrito e o imposto como
        # qualquer compra). Dentro de casa continua de graca — o aluguel ja foi pago.
        if c.moradia:
            em_casa = (dn == m.casa).float()
            fora_casa = oo[:,2]*(1. - em_casa)
            gasto = gasto + c.HOTEL*fora_casa
            m.n_hotel = m.n_hotel + fora_casa
            m.e42_hotel = m.e42_hotel + c.HOTEL*fora_casa*fat
            m.t_casa = m.t_casa + em_casa*(viva.float() if viva is not None else 1.)
        m.imp_gastar = m.imp_gastar + gasto*(fat-1.)
        # divida: piso em -LIMITE (nunca morre por dinheiro; o comercio e que nao fia —
        # os portoes `dinh>=preco` e `paga` do serv_need ja bloqueiam a compra no vermelho)
        m.dinh = (m.e15_d0 - gasto*fat - c.pane_dinh*sf.float()).clamp(min=-c.LIMITE_DIVIDA)
        vv = viva.float() if viva is not None else torch.ones_like(m.dinh)
        m.div_max = torch.maximum(m.div_max, (-m.dinh).clamp(min=0)*vv)
        m.t_divida = m.t_divida + (m.dinh < 0).float()*vv     # so conta enquanto vivo
        rk = m.e15_rank.gather(1, dn[:,None])                     # 0 = distrito mais barato
        m.t_dist = m.t_dist + (rk == m.ARD[None,:]).float()*vv[:,None]
        # (4) REBOQUE EM CALORIAS (N16): a pane cobra KCAL_REBOQUE x d_posto — gordura
        # primeiro (com a perda de mobilizacao), tanque depois. Nada em dinheiro.
        q = c.KCAL_REBOQUE*m.dposto[m.cidx, m.no]*sf.float()
        qr = torch.minimum(m.res, q/(1-m.perda)); m.res = m.res - qr
        fl = q - qr*(1-m.perda)                          # o que a gordura nao cobriu
        if c.KCAL_VIDA:
            # MOEDA CRUZADA: o resto vira dano, nao tanque (o tanque e o que leva ao posto)
            m.vida = (m.vida - c.KCAL_VIDA*fl).clamp(min=0)
            qf = torch.zeros_like(fl)
        else:
            qf = torch.minimum(m.fuel, fl); m.fuel = m.fuel - qf
        m.kcal_reb = m.kcal_reb + qr*(1-m.perda) + (fl if c.KCAL_VIDA else qf)
        # (5) EMBARQUE: grava o distrito de ORIGEM da corrida que comeca agora
        m.e15_dorig = torch.where(pega, dn, m.e15_dorig)
    # [E15 fim]
    rd = torch.rand(B, generator=m.gsim, device=DEV)
    val = val & (~mob)                  # mobilizando = parado este passo
    fu = val & (~sf) & (rd < ((1-m.pneu/100)-.45).clamp(min=0)*c.risco*m.txp())
    T_FURO, P_FURO = (30., 40.) if c.corpo else (15., 60.)   # E13: furo demora mais, pneu sai pior
    m.avar += fu.float(); m.av_furo += fu.float(); m.tpar = torch.where(fu, torch.full_like(m.tpar,T_FURO), m.tpar)
    m.pneu = torch.where(fu, torch.full_like(m.pneu,P_FURO), m.pneu)
    ol = val & (~sf) & (~fu) & (m.oleo<12) & (rd<.05)
    m.avar += ol.float(); m.av_oleo += ol.float(); m.tpar = torch.where(ol, torch.full_like(m.tpar,22.), m.tpar)
    m.oleo = torch.where(ol, torch.full_like(m.oleo,45.), m.oleo)
    qt = val & (~sf) & (~fu) & (~ol) & (m.temp>92)
    T_QT, TEMP_QT = (20., 92.) if c.corpo else (14., 40.)    # E13: motor quente DESLIGA e esfria sozinho (1.6/passo)
    m.avar += qt.float(); m.av_quente += qt.float(); m.tpar = torch.where(qt, torch.full_like(m.tpar,T_QT), m.tpar)
    m.temp = torch.where(qt, torch.full_like(m.temp,TEMP_QT), m.temp)
    gs = torch.gather(m.grp_(),1,sel[:,None]).squeeze(1).float()
    fn = torch.gather(m.fase,1,m.no[:,None]).squeeze(1)
    vd = (gs==fn) | (m.tem_()==0)
    an = val & (~sf) & (~fu) & (~ol) & (~qt) & vd
    m.indo = torch.where(an, dst, m.indo)
    fvel = m.mult[:,4] if c.glandulas else 1.    # E16: canal 4 (velocidade/tempo de viagem) liberado
    m.rest = torch.where(an, (cu*m.vel()*peso*saude*fvel).round().clamp(min=1), m.rest)  # pesado/ferido = lento
    m.fuel = m.fuel - cuf*c.fuel*an.float()
    # [E16 glandulas: custo calorico dos hormonios; sono limpa h — SO E16]
    if c.glandulas or c.gl_regime:
        # (a) METABOLISMO x REGIME: o consumo do passo ja saiu acima com fator
        #     1; aqui entra a DIFERENCA. So o TANQUE — pneu/oleo/calor usam
        #     `cuf` mais abaixo, FORA do bloco (doc 30 §3 lista a linha exata).
        #     O REGIME vale para todo mundo (inclusive o braco de referencia,
        #     senao a comparacao e placebo); o GANHO, so com glandulas.
        # metabolismo (canal 2) ja esta em `cuf` (liberado na linha do cuf); aqui SO o regime
        freg = m.gl_reg if c.gl_regime else 1.
        m.fuel = m.fuel - cuf*c.fuel*an.float()*(freg - 1.)
    if c.glandulas:
        # (b) SONO: canal 3 aplicado direto na linha do descanso (liberado pelo dono do lab.py).
        # (c) CUSTO CALORICO, TODO passo (parado tambem): gordura primeiro (com
        #     perda), depois tanque. E o que faz o TIMING valer: o beneficio so
        #     aparece andando, a conta chega sempre.
        q = c.KAPPA_H*m.h.sum(1)
        if viva is not None: q = q*viva.float()
        q2 = torch.minimum(m.res, q/(1. - m.perda)); m.res = m.res - q2
        q1 = (q - q2*(1. - m.perda)).clamp(min=0.)
        m.fuel = (m.fuel - q1).clamp(min=0.)
        m.h_custo += q
        # (d) SONO LIMPA: descansar corta o hormonio pela metade
        m.h_sono += .5*o3.float()*m.h.sum(1)
        m.h = torch.where(o3[:,None], m.h*.5, m.h)
        # (e) eventos DESTE passo — as glandulas leem no proximo (hormonio atrasa)
        m.ev = torch.stack([ch, o1, o4, o3], -1).float()
    # [E16 fim]
    m.fad  = (m.fad  + cu*c.fadiga*peso*an.float()).clamp(max=100)
    if noite is not None:
        m.par_noite += (noite & ~an & (m.rest<=0)).float()   # parado a noite
        m.ent_noite += (noite & ch).float()
    m.pneu = (m.pneu - cuf*c.pneu*m.txp()*an.float()).clamp(min=0)
    m.oleo = (m.oleo - cuf*c.oleo*m.txo()*an.float()).clamp(min=0)
    if c.corpo:
        # E13: avarias FEREM e rodar machucado fere por passo; vida<=0 = morte
        fer = (m.pneu < 30.) | (m.temp > 80.) | (m.oleo < 20.)
        dn = (c.D_PANE*sf.float() + c.D_FURO*fu.float() + c.D_OLEO*ol.float()
              + c.D_QUENTE*qt.float() + c.D_RODAR*(an & fer).float())
        if c.fome_mata:   # E19: fome fere (parado tambem) — inanicao; E25: nao fere durante a graca (infancia)
            gr = (m.t >= c.fome_gracia).float() if c.fome_gracia else 1.
            dn = dn + c.fome_mata*gr*((m.fome - c.FOME_CRIT)/(100. - c.FOME_CRIT)).clamp(0., 1.)
        if c.divida_mata and c.economia:   # E19: divida alem do limite = perde o carro
            dn = dn + 1000.*(m.dinh <= -c.LIMITE_DIVIDA).float()
        m.vida = (m.vida - dn).clamp(min=0); m.dano_soma += dn
    if getattr(c, 'fitness', 'padrao') == 'bemestar':   # [E41 B] bem-estar do passo: corpo inteiro, sem fome, com tanque, com dinheiro
        m.bem_soma += (m.vida > 0).float()*(m.vida/100. + (1. - m.fome/100.) + m.fuel/m.capf() + (m.dinh/100.).clamp(0., 1.))/4.
        m.t_vida += viva.float()
    if c.com_agua:
        # radiador: sem agua o motor esquenta MAIS — pela lei OCULTA k_agua
        # do mundo (a fisica que so se aprende vivendo, doc 24)
        m.agua = (m.agua - cuf*.6*an.float()).clamp(min=0)
        aquece = cuf*c.temp*m.txt()*(1 + m.k_agua*(1-m.agua/100.))
        m.temp = (m.temp + aquece*an.float()).clamp(max=120)
    else:
        m.temp = (m.temp + cuf*c.temp*m.txt()*an.float()).clamp(max=120)
    if c.mundo == 'ruas':
        # flutua EM TORNO da base cronica (AR-1): a estrutura persiste
        m.npc = (m.npc_base + (m.npc - m.npc_base)*.85
                 + (torch.rand(B,m.n,generator=m.gsim,device=DEV)-.5)*.20).clamp(min=0)
    else:
        m.npc = m.npc*.85 + torch.rand(B,m.n,generator=m.gsim,device=DEV)*(c.trafego*.45)
    return m

# ============================ CEREBROS ============================
# Contrato: extra() roda DENTRO do torch.compile — nao pode mutar tensor
# persistente IN-PLACE (scatter_/add_/index_put_ em atributo: o compile copia o
# tensor inteiro por passo — a diadica pagava 327 MB/passo por isso). REBIND
# (s.E = a*s.E + ...) e permitido: o dynamo rastreia setattr out-of-place.
# Mutacao in-place vive em atualizar(), que o loop chama FORA do grafo.
class Reativo:
    nome='reativo'; NP=NF+6+6+6   # I8: pesos mortos ate igualar 36
    def reset(s,m,W): pass
    def extra(s,m,W,viz): return 0.
    def atualizar(s,m): pass
class ReativoNoite(Reativo):
    """E14a: 2 genes de TIMING nos pesos mortos do Reativo (mesmo NP). g = [20h<=h<22h]*(1-fuel/cap):
    servico posto += W[NF+6]*g ; movimento += -W[NF+7]*d_posto(vizinho)*g (puxa a rota pro posto ao anoitecer)."""
    nome='reativo-noite'
    def _g(s, m):
        h = m.hora()
        return ((h >= 20.) & (h < 22.)).float() * (1. - m.fuel/m.capf())
    def extra(s,m,W,viz):
        dp = m.dposto[m.cidx[:,None].expand(-1, viz.shape[1]), viz]
        return -W[:,NF+7:NF+8]*dp*s._g(m)[:,None]
    def extra_serv(s, m):
        g = s._g(m); z = torch.zeros_like(g)
        return torch.stack([s.W[:,NF+6]*g, z, z, z, z], 1)
    def reset(s,m,W): s.W = W
class ReativoNoite24(ReativoNoite):
    """E14g controle: os mesmos 2 genes do ReativoNoite, sem hora — g = 1 - fuel/cap a qualquer hora."""
    nome='reativo-noite24'
    def _g(s, m):
        return 1. - m.fuel/m.capf()
class ReativoRuido(ReativoNoite):
    """E14g controle: os 2 genes multiplicam ruido uniforme por passo (alavanca sem informacao)."""
    nome='reativo-ruido'
    def _g(s, m):
        return torch.rand(m.B, generator=m.gsim, device=DEV)
class ReativoHora(Reativo):
    """E12b: o Reativo NAO tem alavanca pra "encher antes da noite": o score
    de servico e w*necessidade*disponivel, e hora/reserva (features de estado)
    so deslocam mover-vs-servir em bloco. Aqui os 12 pesos MORTOS do Reativo
    viram modulacao por hora e por reserva, POR SERVICO (mesmo NP: comparacao
    justa): ss += hsin*W[NF+6:NF+11] + hcos*W[NF+11:NF+16]
                 + e_res*(W[NF+16] no posto, W[NF+17] no descanso)."""
    nome='reativo-hora'
    def extra_serv(s, m):
        Wb = s.W
        ang = m.hora()*(2*3.14159265/24.)
        hs, hc = torch.sin(ang)[:,None], torch.cos(ang)[:,None]
        er = m.res/m.cfg.RES_MAX
        ss = hs*Wb[:,NF+6:NF+11] + hc*Wb[:,NF+11:NF+16]
        ss = ss + torch.stack([er*Wb[:,NF+16], torch.zeros_like(er),
                               er*Wb[:,NF+17], torch.zeros_like(er),
                               torch.zeros_like(er)], 1)
        return ss
    def reset(s,m,W): s.W = W
class BancoEMA:
    nome='banco EMA'; NP=NF+6+6+6
    def reset(s,m,W):
        s.al = torch.exp(-1/(2+30*(W[:,NF+9:NF+12].abs()+.1)))   # (B,3)
        s.E  = torch.zeros(m.B,3,m.n,device=DEV)
    def extra(s,m,W,viz):
        oc = torch.zeros(m.B,m.n,device=DEV); oc.scatter_(1,m.no[:,None],1.)
        a = s.al[:,:,None]
        s.E = a*s.E + (1-a)*oc[:,None,:]
        g = s.E.gather(2, viz[:,None,:].expand(-1,3,-1))         # (B,3,G)
        return torch.einsum('bk,bkg->bg', W[:,NF+6:NF+9], g)
    def atualizar(s,m): pass

class _JanelasDiadicas:
    """Historico de nos em janelas [2^j, 2^(j+1)) via RING BUFFER uint8.

    A versao antiga materializava (B, 2^j, G) por nivel POR PASSO (335 MB em
    B=524k); uma versao intermediaria com contagens (B,L,n) + scatter_add
    pagava 5,8 ms/passo so de atomics espalhados. Aqui: o compile funde
    comparacao+peso+reducao sobre (B,64,G) sem materializar nada — 1,3 ms.
    A media da janela j = soma de igualdades x (1/largura), identica em valor
    (teste de equivalencia em src/testes.py). Contador e tensor no device
    (regra 3: int python vira guard/recompile)."""
    L=6; N=64
    def reset(s, m):
        assert m.n <= 255, 'ring uint8: n>255 faria mod-256 silencioso'
        s.buf = torch.zeros(m.B, s.N, dtype=torch.uint8, device=DEV)
        s.pt  = torch.zeros((), dtype=torch.long, device=DEV)
        s.ARL = torch.arange(s.N, device=DEV)
        # nivel de cada lag k (janela j cobre lags [2^j, 2^(j+1)))
        lvl = [0]*s.N
        for k in range(1, s.N): lvl[k] = min(k.bit_length()-1, s.L-1)
        s.LVL = torch.tensor(lvl, device=DEV)
        # WL[p,k] = 1/largura da janela do lag k quando ha p itens no historico
        # (0 se o lag ainda nao existe: k >= p — mesmo corte do slice antigo)
        WL = torch.zeros(s.N+1, s.N)
        for p in range(s.N+1):
            for k in range(1, s.N):
                j = min(k.bit_length()-1, s.L-1)
                a, b = 2**j, min(2**(j+1), s.N)
                w = max(min(b, p) - a, 0)
                if a <= k < min(b, p) and w > 0:
                    WL[p, k] = 1./w
        s.WL = WL.to(DEV)
    def saida(s, m, viz, Wj):
        """(B,G): soma ponderada das frequencias por janela, ja x pesos Wj (B,L)."""
        lagpos = (s.pt-1-s.ARL) % s.N                       # posicao do lag k no ring
        hist = s.buf.gather(1, lagpos[None,:].expand(m.B,-1))          # (B,N)
        # index_select (nao indexacao por tensor 0-dim, que faz .item() -> sync)
        wl = s.WL.index_select(0, s.pt.clamp(max=s.N).reshape(1))      # (1,N)
        coef = Wj.gather(1, s.LVL[None,:].expand(m.B,-1)) * wl         # (B,N)
        eq = (hist[:,:,None] == viz[:,None,:].to(torch.uint8)).float() # (B,N,G)
        return (coef[:,:,None]*eq).sum(1)
    def push_no(s, m, no):
        s.buf.scatter_(1, (s.pt % s.N).reshape(1,1).expand(m.B,1),
                       no.to(torch.uint8)[:,None])
        s.pt = s.pt + 1

class Diadica:
    nome='diadica'; NP=NF+6+6+6; L=6
    def reset(s,m,W):
        s.jan = _JanelasDiadicas(); s.jan.reset(m)
    def extra(s,m,W,viz):
        out = s.jan.saida(m, viz, W[:,NF+6:NF+6+s.jan.L])
        # o no a empurrar e o de ANTES do passo (m.no e re-atribuido, nao mutado,
        # entao guardar a referencia preserva o valor pre-passo)
        s._no = m.no
        return out
    def atualizar(s,m):
        s.jan.push_no(m, s._no)
class Corpo:
    nome='corpo'; NP=NF+6+6+6
    def reset(s,m,W): pass
    def atualizar(s,m): pass
    def extra(s,m,W,viz):
        d = torch.stack([1-m.fuel/m.capf(), m.fome/100, m.fad/100,
                         1-m.pneu/100, m.temp/120],1)
        k = d.argmax(1); mp = m.MP[k]
        sel = m.dsa[m.cidx, mp].gather(1, viz)                   # (B,G)
        peso = W[m.ARB, NF+6+k]
        return (peso*d.max(1).values)[:,None]*(-sel/6.)
class Hibrido:
    nome='hibrido'; NP=NF+6+6+6; L=6
    def reset(s,m,W):
        s.jan = _JanelasDiadicas(); s.jan.reset(m)
    def extra(s,m,W,viz):
        out = s.jan.saida(m, viz, W[:,NF+6:NF+6+s.jan.L])
        s._no = m.no
        d = torch.stack([1-m.fuel/m.capf(), m.fome/100, m.fad/100,
                         1-m.pneu/100, m.temp/120],1)
        k = d.argmax(1); mp = m.MP[k]
        sel = m.dsa[m.cidx, mp].gather(1, viz)
        peso = W[m.ARB, NF+12+k]
        return out + (peso*d.max(1).values)[:,None]*(-sel/6.)
    def atualizar(s,m):
        s.jan.push_no(m, s._no)
class MemCusto:
    """EMA de congestao POR NO, escrita ao pisar, lida nos vizinhos.
    E a memoria que o mundo `ruas` exige: la a congestao dos vizinhos e
    invisivel e a estrutura e cronica — quem lembra desvia."""
    nome='mem custo'; NP=NF+6+6+6
    def reset(s,m,W):
        s.k = torch.sigmoid(W[:,NF+6:NF+7])          # taxa de escrita evoluida
        s.C = torch.zeros(m.B, m.n, device=DEV)      # congestao lembrada por no
    def extra(s,m,W,viz):
        s._obs = torch.gather(m.npc, 1, m.no[:,None])   # sentida AGORA, aqui
        s._no = m.no
        g = torch.gather(s.C, 1, viz)
        return W[:,NF+7:NF+8]*(-g)                   # evita vizinho lembrado como ruim
    def atualizar(s,m):
        atual = torch.gather(s.C, 1, s._no[:,None])
        s.C.scatter_(1, s._no[:,None], atual + s.k*(s._obs-atual))
class MapaServico:
    """Mapa APRENDIDO de servicos: grava onde ja viu posto/comida/etc ao passar,
    e puxa para o vizinho lembrado quando a necessidade aperta. E o `corpo` sem
    oraculo — a memoria que o mundo `semgps` exige."""
    nome='mapa servico'; NP=NF+6+6+6
    def reset(s,m,W):
        s.M = torch.zeros(m.B, 5, m.n, device=DEV)   # 1 = "ja vi este servico aqui"
    def extra(s,m,W,viz):
        s._sv = m.serv_(); s._no = m.no
        d = torch.stack([1-m.fuel/m.capf(), m.fome/100, m.fad/100,
                         1-m.pneu/100, m.temp/120],1)
        k = d.argmax(1); mp = m.MP[k]
        sel = s.M[m.ARB, mp].gather(1, viz)
        peso = W[m.ARB, NF+12+k]
        return (peso*d.max(1).values)[:,None]*sel
    def atualizar(s,m):
        no3 = s._no[:,None,None].expand(-1,5,1)
        cur = s.M.gather(2, no3)
        s.M.scatter_(2, no3, torch.maximum(cur, s._sv[:,:,None]))
class RotaCalculada:
    """E4 do doc 19: MemCusto + ORGAO CALCULISTA. A cada K passos roda
    Floyd-Warshall em lote sobre os custos LEMBRADOS (aresta + congestao
    memorizada do destino) e oferece a distancia-ciente-de-congestao como
    feature. O peso evoluido decide quanto confiar no orgao vs no GPS cru.
    Controle ja medido: memoria SEM calculo = teto 0 no mundo ruas."""
    nome='rota calculada'; NP=NF+6+6+6; K=16
    def reset(s,m,W):
        s.k = torch.sigmoid(W[:,NF+6:NF+7])          # taxa de escrita da memoria
        s.C = torch.zeros(m.B, m.n, device=DEV)      # congestao lembrada por no
        s.D = m.DIa[m.cidx].clone()                  # (B,n,n) comeca no GPS cru
        s.passos = 0
        s.ARN = torch.arange(m.n, device=DEV)
    def _recalcular(s, m):
        """caminho-minimo sobre o que o taxi LEMBRA (nao sobre o oraculo)."""
        n = m.n
        # aresta i->j = peso da rua + congestao lembrada de j
        A = m.Aa[m.cidx]; Wr = m.Wa[m.cidx]                       # (B,n,G)
        cd = s.C.gather(1, A.clamp(min=0).reshape(m.B,-1)).reshape(m.B,n,GMAX)
        custo = torch.where(A>=0, Wr + cd, torch.full_like(Wr, 1e6))
        D = torch.full((m.B,n,n), 1e6, device=DEV)
        D.scatter_(2, A.clamp(min=0), custo)
        D[:, s.ARN, s.ARN] = 0.
        for k in range(n):
            D = torch.minimum(D, D[:,:,k:k+1] + D[:,k:k+1,:])
        s.D = D
    def extra(s,m,W,viz):
        s._obs = torch.gather(m.npc, 1, m.no[:,None]); s._no = m.no
        # alvo igual ao obs(): destino da corrida, senao passageiro mais proximo
        dpo = m.DIa[m.cidx[:,None].expand(-1,NPX), m.no[:,None].expand(-1,NPX), m.po]
        kb = dpo.argmin(1)
        alvo = torch.where(m.pd_>=0, m.pd_, m.po.gather(1, kb[:,None]).squeeze(1))
        dor = s.D[m.ARB[:,None].expand(-1,GMAX), viz, alvo[:,None].expand(-1,GMAX)]
        g = torch.gather(s.C, 1, viz)
        return W[:,NF+7:NF+8]*(-g) + W[:,NF+8:NF+9]*(-dor.clamp(max=60.)/6.)
    def atualizar(s,m):
        atual = torch.gather(s.C, 1, s._no[:,None])
        s.C.scatter_(1, s._no[:,None], atual + s.k*(s._obs-atual))
        s.passos += 1
        if s.passos % s.K == 0:
            s._recalcular(m)
class SerVital:
    """E8 (docs 21): VIDA EM FASES. 5 orgaos nascem TODOS ligados; o bebe
    explora (temperatura alta) com custo subsidiado; na adolescencia (T_b,
    gene) poda-se por contribuicao medida; o adulto paga KAPPA por orgao
    ativo por passo. Genes extras: pesos dos 5 orgaos, fracao-de-infancia,
    T_bebe, T_adulto, limiar de poda.
    Orgaos: 1 mem-custo  2 mapa-servico  3 janelas diadicas  4 corpo(oraculo)
            5 rota calculada (FW sobre custos lembrados, compartilha C com 1).
    modo: 'direto' (adulto desde o nascimento) | 'sem_poda' | 'poda' |
          'poda_aleatoria' (mesma contagem, orgaos sorteados) | 'curta'
          (infancia 5%) | 'lesao' (E8b: lesoes ROTATIVAS na infancia — cada
          orgao desligado em janelas de 8 passos; poda CAUSAL: mantem so quem,
          ausente, piorou a taxa de fitness. Conserta o furo do E8: a
          contribuicao por |w*sinal| e MAGNITUDE e mantinha orgao inutil de
          sinal alto). T_REF fixa a infancia em passos ABSOLUTOS."""
    nome='ser vital'; NP=NF+6+6+6; K=16; KAPPA=5e-4; T_REF=600
    modo='poda'
    def reset(s,m,W):
        B=m.B
        s.wo = W[:, NF+6:NF+11]                          # (B,5) pesos dos orgaos
        fr = torch.sigmoid(W[:, NF+11])*.45+.05          # infancia = 5..50% de T_REF
        if s.modo=='curta':  fr = torch.full_like(fr, .05)
        if s.modo=='direto': fr = torch.zeros_like(fr)
        if s.modo=='lesao':
            # lesao precisa de ciclos completos de 6 janelas: minimo 2 ciclos
            fr = fr.clamp(min=6*2*8/s.T_REF)
        s.Tb = (fr*s.T_REF).round()                      # (B,) passos de infancia
        s.Tbebe   = torch.nn.functional.softplus(W[:, NF+12])
        s.Tadulto = torch.nn.functional.softplus(W[:, NF+13])*.3
        s.limiar  = torch.sigmoid(W[:, NF+14])*.5        # fracao de 1/5 uniforme
        s.mask = torch.ones(B, 5, device=DEV)            # orgaos ativos (nasce tudo)
        s.contrib = torch.zeros(B, 5, device=DEV)
        s.t = torch.zeros((), dtype=torch.long, device=DEV)
        # estados dos orgaos
        s.C = torch.zeros(B, m.n, device=DEV)            # congestao lembrada (1 e 5)
        s.M = torch.zeros(B, 5, m.n, device=DEV)         # mapa de servicos (2)
        s.jan = _JanelasDiadicas(); s.jan.reset(m)       # (3)
        s.WJ = torch.full((B, s.jan.L), 1./s.jan.L, device=DEV)
        s.D = m.DIa[m.cidx].clone()                      # rota lembrada (5)
        s.ARN = torch.arange(m.n, device=DEV)
        # gerador PROPRIO p/ sorteios da poda: nunca tocar o gsim do mundo
        # (o portao E8 pegou: um draw extra dessincroniza o mundo entre modos)
        s.gp = torch.Generator(device=DEV); s.gp.manual_seed(987654)
        # lesao: contabilidade causal (Δfitness por condicao: orgao o OFF / tudo ON)
        s.WJAN = 8
        s.AR5o = torch.arange(5, device=DEV)
        s.rate = torch.zeros(B, 6, device=DEV)
        s.rcnt = torch.zeros(B, 6, device=DEV)
        s._fit_prev = torch.zeros(B, device=DEV)
    def _sinais(s,m,viz):
        """(B,5,G) sinais dos 5 orgaos + contexto (need, carregando)."""
        d5 = torch.stack([1-m.fuel/m.capf(), m.fome/100, m.fad/100,
                          1-m.pneu/100, m.temp/120],1)
        k = d5.argmax(1); mp = m.MP[k]; need = d5.max(1).values
        dpo = m.DIa[m.cidx[:,None].expand(-1,NPX), m.no[:,None].expand(-1,NPX), m.po]
        alvo = torch.where(m.pd_>=0, m.pd_,
                           m.po.gather(1, dpo.argmin(1)[:,None]).squeeze(1))
        dor = s.D[m.ARB[:,None].expand(-1,GMAX), viz, alvo[:,None].expand(-1,GMAX)]
        sig = torch.stack([
            -torch.gather(s.C, 1, viz),                              # 1 mem custo
            need[:,None]*s.M[m.ARB, mp].gather(1, viz),              # 2 mapa
            s.jan.saida(m, viz, s.WJ),                               # 3 janelas
            need[:,None]*(-m.dsa[m.cidx, mp].gather(1, viz)/6.),     # 4 corpo
            -dor.clamp(max=60.)/6.,                                  # 5 rota
        ], 1)                                                        # (B,5,G)
        return sig, need, (m.pd_>=0).float()
    def _gate(s, need, carreg):
        return s.mask * s.wo
    def extra(s,m,W,viz):
        B=m.B
        sig, need, carreg = s._sinais(m, viz)
        gate = s._gate(need, carreg)
        if s.modo == 'lesao':
            # janela atual desliga UM orgao durante a infancia (rotativo);
            # janela 5 = tudo ligado (referencia causal)
            jan_i = (s.t // s.WJAN) % 6
            bebe_ = (s.t.float() < s.Tb).float()[:,None]
            les = 1. - bebe_*(s.AR5o == jan_i).float()[None,:]
            gate = gate * les
        s._absc = (s.mask * s.wo.abs()) * sig.abs().mean(2)          # contribuicao
        s._obs = torch.gather(m.npc, 1, m.no[:,None]); s._no = m.no
        s._sv = m.serv_()
        return torch.einsum('bo,bog->bg', gate, sig)
    def decidir(s, tudo, m):
        """softmax com temperatura POR FASE via Gumbel; T=0 == argmax exato."""
        bebe = (s.t < s.Tb).float()
        T = bebe*s.Tbebe + (1-bebe)*s.Tadulto
        u = torch.rand(tudo.shape, generator=m.gsim, device=DEV).clamp(min=1e-20)
        return (tudo + T[:,None]*(-torch.log(-torch.log(u)))).argmax(1)
    def atualizar(s,m):
        B=m.B
        # memorias dos orgaos
        atual = torch.gather(s.C, 1, s._no[:,None])
        s.C.scatter_(1, s._no[:,None], atual + 0.2*(s._obs-atual))
        no3 = s._no[:,None,None].expand(-1,5,1)
        s.M.scatter_(2, no3, torch.maximum(s.M.gather(2,no3), s._sv[:,:,None]))
        s.jan.push_no(m, s._no)
        s.contrib += s._absc
        if s.modo == 'lesao':
            # Δfitness deste passo cai no balde da condicao vigente (ANTES do t+1,
            # casando com a janela que o extra() usou)
            fit_now = m.ent - 0.3*m.avar
            d = fit_now - s._fit_prev; s._fit_prev = fit_now
            jan_i = (s.t // s.WJAN) % 6
            oh = (torch.arange(6, device=DEV) == jan_i).float()
            bebe_ = (s.t.float() < s.Tb).float()
            s.rate += (bebe_*d)[:,None]*oh[None,:]
            s.rcnt += bebe_[:,None]*oh[None,:]
        s.t = s.t + 1
        if int(s.t) % s.K == 0:                       # rota lembrada (barato, eager)
            n=m.n; A=m.Aa[m.cidx]; Wr=m.Wa[m.cidx]
            cd = s.C.gather(1, A.clamp(min=0).reshape(B,-1)).reshape(B,n,GMAX)
            custo = torch.where(A>=0, Wr+cd, torch.full_like(Wr,1e6))
            D = torch.full((B,n,n), 1e6, device=DEV)
            D.scatter_(2, A.clamp(min=0), custo); D[:, s.ARN, s.ARN]=0.
            for kk in range(n):
                D = torch.minimum(D, D[:,:,kk:kk+1]+D[:,kk:kk+1,:])
            s.D = D
        # ADOLESCENCIA: mundos que cruzam T_b AGORA decidem a poda
        cruza = (s.t.float() == s.Tb)
        if s.modo == 'lesao':
            # poda CAUSAL: mantem o orgao se a AUSENCIA dele piorou a taxa
            r = s.rate / s.rcnt.clamp(min=1.)
            r_on = r[:, 5:6]; r_off = r[:, :5]
            manter = (r_on - r_off > 0.02*r_on.abs() + 1e-4).float()
            s.mask = torch.where(cruza[:,None], manter, s.mask)
        elif s.modo in ('poda','poda_aleatoria','curta'):
            frac = s.contrib / (s.contrib.sum(1, keepdim=True)+1e-9)
            manter = (frac > s.limiar[:,None]*0.2).float()
            if s.modo == 'poda_aleatoria':
                # mesma CONTAGEM de sobreviventes, orgaos sorteados (controle)
                perm = torch.rand(B,5,generator=s.gp,device=DEV).argsort(1)
                manter = manter.gather(1, perm)
            s.mask = torch.where(cruza[:,None], manter, s.mask)
        # custo neural: so na fase adulta (infancia e subsidiada)
        adulto = (s.t.float() > s.Tb).float()
        uso = s._consumo(adulto)                      # unidades de consulta no passo
        if m.cfg.cerebro_come:
            # E12b: o cerebro COME calorias (tanque), nao fitness; infancia
            # segue subsidiada (os pais alimentam)
            m.fuel = (m.fuel - m.cfg.KAPPA_F * uso).clamp(min=0)
            pen = torch.zeros(B, device=DEV)
        else:
            pen = s.KAPPA * uso
        m.custo_neural = getattr(m, 'custo_neural', torch.zeros(B, device=DEV)) + pen
    def _consumo(s, adulto):
        return s.mask.sum(1) * adulto

class SerTalamo(SerVital):
    """E6 (doc 20): TALAMO dentro do ser — um gate POR ORGAO POR PASSO decide
    quem e consultado, lendo o contexto interno (necessidade dominante +
    carregando passageiro). Custo por CONSULTA, nao por orgao-vivo. Sem
    ontogenia (adulto desde o nascimento): isola o valor do ROTEAMENTO.
    Genes 36..50: (a,b,c) por orgao -> gate = sig(a + b*need + c*carreg).
    submodo: 'sempre' (gate=1, paga tudo) | 'talamo' (contextual) | 'cego'
    (so o bias a — aprende QUANTO consultar mas nao QUANDO; controle do
    refutado 'rotear por estatistica fixa')."""
    nome='talamo'; NP=NF+36; modo='direto'; submodo='talamo'; KAPPA_C=5e-4
    def reset(s,m,W):
        SerVital.reset(s,m,W)
        s.G3 = W[:, NF+18:NF+33].reshape(m.B,5,3)
        s.duty_soma = torch.zeros(m.B,5,device=DEV)
        s.duty_carr = torch.zeros(m.B,5,device=DEV)
        s.carr_soma = torch.zeros(m.B,device=DEV)
        s.passos_n = torch.zeros((),device=DEV)
    def _gate(s, need, carreg):
        if s.submodo == 'sempre':
            g = torch.ones_like(s.wo)
        elif s.submodo == 'cego':
            g = torch.sigmoid(s.G3[:,:,0])
        else:
            g = torch.sigmoid(s.G3[:,:,0] + s.G3[:,:,1]*need[:,None]
                              + s.G3[:,:,2]*carreg[:,None])
        s._g = g; s._carreg = carreg
        return g * s.wo
    def _consumo(s, adulto):
        # paga-se por CONSULTA (soma dos gates), a vida inteira (sem infancia)
        return s._g.sum(1)
    def atualizar(s,m):
        SerVital.atualizar(s,m)
        s.duty_soma += s._g
        s.duty_carr += s._g * s._carreg[:,None]
        s.carr_soma += s._carreg
        s.passos_n = s.passos_n + 1
class SerTalamoNoite(SerTalamo):
    """E13r: o portao do talamo tambem le a NOITE — gate = sig(a + b*need + c*carreg + d*noite).
    Genes NF+18..NF+38 (5 orgaos x 4). Zero-noite = SerTalamo (mundos sem relogio)."""
    nome='talamo-noite'; NP=NF+38
    def reset(s,m,W):
        SerTalamo.reset(s,m,W)
        s.G4 = W[:, NF+18:NF+38].reshape(m.B,5,4)
        s._noite = torch.zeros(m.B, device=DEV)
    def extra(s,m,W,viz):
        n = m.noite_()
        s._noite = n.float() if n is not None else torch.zeros(m.B, device=DEV)
        return SerTalamo.extra(s,m,W,viz)
    def _gate(s, need, carreg):
        g = torch.sigmoid(s.G4[:,:,0] + s.G4[:,:,1]*need[:,None]
                          + s.G4[:,:,2]*carreg[:,None] + s.G4[:,:,3]*s._noite[:,None])
        s._g = g; s._carreg = carreg
        return g * s.wo
class SerSono:
    """E9b (doc 24): o sono que APRENDE. De dia vive e GRAVA no buffer-
    hipocampo (features -> aquecimento observado); DORMINDO (descanso)
    consolida: resolve a lei do aquecimento por forma fechada e mistura com
    alfa(hora): 1.0 dormindo 20h-00h | 0.5 pos-meia-noite | 0.2 de dia.
    A lei k_agua e SORTEADA POR MUNDO (cfg.com_agua) — evolucao nao decora,
    so aprendizado em vida alcanca. A lei alimenta o PREVISOR: penaliza mover
    quando a previsao diz superaquecer e puxa pro posto quando o risco sobe.
    submodo: 'fixo' (alfa=0, nao aprende) | 'constante' (alfa=0.55, sono nao
    importa) | 'circadiano' (a tese).
    Genes: NF+6=w_risco, NF+7=w_posto, NF+8=hora preferida de dormir (o
    VOLANTE do horario — sem ele o circadiano sofria o castigo do alfa sem
    poder se adaptar), NF+9=forca do bonus de dormir."""
    nome='ser sono'; NP=NF+6+6+6; submodo='circadiano'; LAMB=1e-3
    def reset(s,m,W):
        B=m.B
        s.w1 = W[:, NF+6:NF+7]; s.w2 = W[:, NF+7:NF+8]
        s.hpref = torch.sigmoid(W[:, NF+8])*24.      # hora preferida de dormir
        s.gdorme = W[:, NF+9]                        # forca do bonus (0=inerte)
        s.A = torch.zeros(B,3,3,device=DEV)          # hipocampo: soma phi phi^T
        s.b = torch.zeros(B,3,device=DEV)            #            soma phi*alvo
        s.lei = torch.zeros(B,3,device=DEV)          # cortex: lei consolidada
        s.t = torch.zeros((),dtype=torch.long,device=DEV)
        s._prev = None
        s.sono_hora = torch.zeros(B,24,device=DEV)   # telemetria: sono por hora
        s.EYE = torch.eye(3,device=DEV)[None]
    def extra(s,m,W,viz):
        cus = m.W_()
        deficit = (1 - m.agua/100.)
        # previsao de aquecimento da PROXIMA rua, pela lei consolidada:
        # dtemp ~ lei0 + lei1*cu + lei2*cu*deficit
        prev = s.lei[:,0:1] + s.lei[:,1:2]*cus + s.lei[:,2:3]*cus*deficit[:,None]
        # risco LIMITADO (E9d): sem clamp, lei crescendo em vida x peso evoluido
        # explodia a penalidade e paralisava o ser (colapso 4.1 do E9c)
        risco = torch.relu(m.temp[:,None] + prev - 85.).clamp(max=6.)
        d_posto = m.dsa[m.cidx, 0].gather(1, viz)
        s._agua_prev = m.agua; s._temp_prev = m.temp; s._fad_prev = m.fad
        s._tpar_prev = m.tpar; s._no_prev = m.no; s._npc_prev = m.npc
        s._rest_prev = m.rest
        return -s.w1*risco + s.w2*(risco.mean(1,keepdim=True))*(-d_posto/6.)
    def extra_serv(s, m):
        """bonus no servico DESCANSO na janela de hora preferida (o relogio
        interno evoluivel — cos da o pico em hpref e o vale 12h depois)."""
        hora = ((s.t.float() + m.fase_dia) % m.cfg.dia) / m.cfg.dia * 24.
        jan = torch.cos(2*3.14159265*(hora - s.hpref)/24.)
        out = torch.zeros(m.B, 5, device=DEV)
        out[:, 2] = s.gdorme * jan
        return out
    def atualizar(s,m):
        c = m.cfg; B = m.B
        # 1) GRAVAR (dia): passos de LARGADA (rest 0 -> >0), sem avaria.
        # BUG PAGO (E9b): sem o rest_prev<=0, todo passo de viagem entrava com
        # dtemp=0 e afogava a regressao — corr 0.03 ate com dados ricos.
        partiu = (s._rest_prev <= 0) & (m.rest > 0) & (m.indo >= 0) \
                 & (m.tpar <= s._tpar_prev)
        dst = m.indo.clamp(min=0)
        A0 = m.Aa[m.cidx, s._no_prev]
        w_edge = (m.Wa[m.cidx, s._no_prev]*(A0==dst[:,None]).float()).sum(1)
        cu = w_edge + s._npc_prev.gather(1, dst[:,None]).squeeze(1)
        dtemp = (m.temp - s._temp_prev) + 1.6        # devolve o resfriamento fixo
        ok = (partiu & (s._temp_prev>26) & (m.temp<118)).float()
        phi = torch.stack([torch.ones_like(cu), cu,
                           cu*(1-s._agua_prev/100.)],1)     # (B,3)
        s.A += ok[:,None,None]*(phi[:,:,None]*phi[:,None,:])
        s.b += ok[:,None]*(phi*dtemp[:,None])
        # 2) CONSOLIDAR (sono): descansou agora (queda de fadiga do servico)
        dormiu = ((s._fad_prev - m.fad) > 5) & ((s._fad_prev - m.fad) < 35) \
                 & (m.tpar <= s._tpar_prev)
        hora24 = (((s.t.float() + m.fase_dia) % c.dia) / c.dia * 24).long()
        if s.submodo == 'fixo':
            alfa = torch.zeros(B, device=DEV)
        elif s.submodo == 'constante':
            alfa = torch.full((B,), .55, device=DEV)
        else:
            alfa = torch.where(hora24 >= 20, torch.full((B,),1.,device=DEV),
                   torch.where(hora24 < 6, torch.full((B,),.5,device=DEV),
                               torch.full((B,),.2,device=DEV)))
        theta = torch.linalg.solve(s.A + s.LAMB*s.EYE, s.b[:,:,None]).squeeze(2)
        s.lei = torch.where(dormiu[:,None],
                            s.lei + (alfa*dormiu.float())[:,None]*(theta - s.lei),
                            s.lei)
        s.sono_hora.scatter_add_(1, hora24[:,None], dormiu.float()[:,None])
        s.t = s.t + 1

ARQS = [Reativo, BancoEMA, Diadica, Corpo, Hibrido, MemCusto, MapaServico]
# RotaCalculada e SerVital ficam FORA das baterias padrao: sao o E4 e o E8
# do doc 19/21, com runners e controles proprios (src/e4_rota.py, e8_vida.py)

# ============================ RODAR / EVOLUIR ============================
def um_passo(m, a, Wb):
    """um tick completo: observar -> pontuar -> agir."""
    F, val = m.obs(); viz = m.A_().clamp(min=0)
    sc = torch.einsum('bgf,bf->bg', F, Wb[:,:NF]) + (a.extra(m, Wb, viz, F) if getattr(a, 'usa_F', False) else a.extra(m, Wb, viz))   # [auditoria 4] arq que reusa F nao recomputa obs()
    sc = sc.masked_fill(~val, -1e9)
    svn, sv = m.serv_need()
    ss = svn*Wb[:,NF:NF+5] + Wb[:,NF+5:NF+6]
    if hasattr(a, 'extra_serv'):        # arq pode influenciar servicos (ex.: sono)
        ss = ss + a.extra_serv(m)
    ss = ss.masked_fill(sv<=0, -1e9)
    tudo = torch.cat([sc, ss],1)
    # arqs com decisao propria (ex.: temperatura por fase da vida — SerVital)
    esc = a.decidir(tudo, m) if hasattr(a, 'decidir') else tudo.argmax(1)
    passo(m, esc)

# torch.compile e opcional (NM_COMPILE=0 desliga). Fallback silencioso p/ eager
# se o backend (triton) nao suportar a GPU. O ganho vem da fusao dos ~200
# kernels elementwise por passo.
_PASSO_C = None
_COMPILE_OK = None
_COMPILE_RUIM = set()      # [auditoria 5] nomes de arquitetura cujo compile falhou — fallback POR BRACO, nao global
def _passo_fn(arq=None):
    global _PASSO_C, _COMPILE_OK
    if os.environ.get('NM_COMPILE', '1') == '0' or DEV != 'cuda':
        return um_passo
    if _COMPILE_OK is False or (arq is not None and arq in _COMPILE_RUIM):
        return um_passo
    if _PASSO_C is None:
        try:
            import torch._dynamo
            torch._dynamo.config.cache_size_limit = 64
            _PASSO_C = torch.compile(um_passo, dynamic=False)
        except Exception:
            _COMPILE_OK = False
            return um_passo
    return _PASSO_C

def modo_execucao(arq=None):
    """'compile' ou 'eager' — gravar no JSON: compile e eager divergem por
    arredondamento (~1e-5 em fuel/temp), entao bateria com modo misto precisa
    ficar auditavel. arq: nome da arquitetura (fallback e por braco)."""
    if os.environ.get('NM_COMPILE', '1') == '0' or DEV != 'cuda' or _COMPILE_OK is False or (arq is not None and arq in _COMPILE_RUIM):
        return 'eager'
    return 'compile'

def rodar(Arq, W, cidades, cfg, T, seed, R=1):
    global _COMPILE_OK
    P = W.shape[0]; m = Lote(cidades, P, cfg, seed=seed, R=R)
    Wb = W[m.gidx]
    a = Arq(); a.reset(m, Wb)
    fn = _passo_fn(Arq.__name__)
    for t in range(T):
        try:
            fn(m, a, Wb)
        except Exception as e:
            # compile falha na 1a chamada de um grafo novo (arq/shape novos = t==0
            # desta rodada). O passo pode ter executado PELA METADE (subgrafos
            # anteriores ja mutaram m) — nunca re-executar por cima: reconstruir
            # a rodada inteira do zero em eager.
            if fn is not um_passo and t == 0:
                print(f'  [COMPILE FALHOU em {Arq.__name__} ({type(e).__name__}): SO esta arquitetura cai para eager; '
                      f'os outros bracos seguem compilados — modo gravado no JSON; nao compare bracos em modos diferentes]', flush=True)
                _COMPILE_RUIM.add(Arq.__name__)
                return rodar(Arq, W, cidades, cfg, T, seed, R=R)
            raise RuntimeError(
                f'passo falhou no meio da rodada (t={t}); estado possivelmente '
                f'parcial. Se foi torch.compile, rode com NM_COMPILE=0 — a '
                f'retomada por checkpoint e segura.') from e
        a.atualizar(m)     # mutacao de estado da memoria FORA do grafo compilado
    return m

def avaliar(Arq, W, cidades, cfg, T, seed=0, R=1):
    m = rodar(Arq, W, cidades, cfg, T, seed, R=R)
    # custo_neural: arq que paga por orgao ativo (SerVital) deposita aqui; 0 p/ demais
    modo = getattr(cfg, 'fitness', 'padrao')   # [E41] reguas alternativas (pedido do Leonardo 2026-09-03); 'padrao' = caminho original intocado
    morto = (m.vida <= 0).float()
    if modo == 'padrao':
        fit = m.ent - 0.3*m.avar - getattr(m, 'custo_neural', 0.)
        if cfg.pena_morte:
            if cfg.pena_prop:   # E27: quem morre no dia 1 perdeu quase a vida toda; no dia 4.9, quase nada
                fit = fit - cfg.pena_morte*morto*2.*(1. - m.t_vida/float(T)).clamp(0., 1.)
            else:
                fit = fit - cfg.pena_morte*morto
        return fit.view(W.shape[0], m.NC*m.R).mean(1)
    vivo = 1. - morto
    if modo == 'sobrevive':      # A: sobreviver primeiro; entre vivos, corpo inteiro + dinheiro; entregas so desempatam
        fit = vivo*(1. + m.vida/100. + (m.dinh/100.).clamp(0., 1.) + 0.05*m.ent) - cfg.pena_morte*morto
        return fit.view(W.shape[0], m.NC*m.R).mean(1)
    if modo == 'bemestar':       # B: bem-estar INTEGRAL ao longo da vida (acumulado em passo) + entregas como meio
        fit = m.bem_soma/float(T) + 0.05*m.ent - cfg.pena_morte*morto
        return fit.view(W.shape[0], m.NC*m.R).mean(1)
    if modo == 'pareto':         # C: 4 objetivos por genoma (media das vidas): vivo*vida, dinheiro, entregas, -avarias -> posto de nao-dominancia
        P = W.shape[0]; V = lambda x: x.view(P, m.NC*m.R).mean(1)
        ob = torch.stack([V(vivo*m.vida), V(m.dinh.clamp(min=0.)), V(m.ent), V(-m.avar)], 1)          # (P,4) maior = melhor
        return -pareto_posto(ob) + 1e-3*((ob - ob.min(0).values)/(ob.max(0).values - ob.min(0).values + 1e-9)).sum(1)
    raise ValueError(f'cfg.fitness desconhecido: {modo}')

def pareto_posto(ob):
    """posto de nao-dominancia (0 = frente de Pareto) por varredura O(P^2) na GPU. ob (P,k), maior = melhor."""
    P = ob.shape[0]
    ge = (ob[None, :, :] >= ob[:, None, :]).all(-1)          # ge[i,j]: j >= i em tudo
    gt = (ob[None, :, :] > ob[:, None, :]).any(-1)           # e estritamente melhor em algum
    dom = ge & gt                                              # dom[i,j]: j domina i
    posto = torch.zeros(P, device=ob.device); resta = torch.ones(P, dtype=torch.bool, device=ob.device)
    for r in range(64):
        nd = resta & ~(dom & resta[None, :]).any(1)           # nao dominado por ninguem que ainda resta
        if not bool(nd.any()): break
        posto[nd] = float(r); resta = resta & ~nd
        if not bool(resta.any()): break
    posto[resta] = 64.
    return posto

def evoluir(Arq, cidades, cfg, P=512, ger=25, T=1500, seed=0, elite=.15,
            verbose=True, R=1, ckpt=None, ckpt_cada=10):
    """ckpt: caminho .pt — salva populacao+RNG a cada `ckpt_cada` geracoes e
    RETOMA automaticamente se o arquivo existir (maquina pode cair no meio)."""
    g = torch.Generator(device=DEV); g.manual_seed(seed)
    W = torch.randn(P, Arq.NP, generator=g, device=DEV)*.8
    hist, snaps, it0 = [], [], 0
    # impressao digital da config: retomar com config DIFERENTE misturaria
    # populacoes/geracoes de corridas distintas num JSON que declara uma so
    cfg_id = f'P={P} ger={ger} T={T} R={R} seed={seed} elite={elite} NP={Arq.NP} arq={Arq.nome}'
    if ckpt and os.path.exists(ckpt):
        d = torch.load(ckpt, map_location=DEV, weights_only=True)
        if d.get('cfg_id') != cfg_id:
            raise SystemExit(
                f'CHECKPOINT DE OUTRA CONFIG:\n  ckpt:  {d.get("cfg_id")}\n'
                f'  agora: {cfg_id}\n  Use --do-zero para descartar, ou repita a config original.')
        W = d['W']; hist = d['hist']; snaps = d['snaps']; it0 = d['ger']+1
        g.set_state(d['rng'].cpu())
        if verbose:
            aviso = ' (evolucao ja concluida — vai direto para avaliacao)' if it0 >= ger else ''
            print(f'  [retomando {ckpt} da geracao {it0}{aviso}]')
    for it in range(it0, ger):
        f = avaliar(Arq, W, cidades, cfg, T, seed+it*13, R=R)
        o = f.argsort(descending=True); W = W[o]; f = f[o]
        hist.append(float(f[0]))
        ne = max(2, int(P*elite)); pais = W[:ne]
        idx = torch.randint(0, ne, (P-ne,), generator=g, device=DEV)
        fil = (pais[idx]+torch.randn(P-ne,Arq.NP,generator=g,device=DEV)*.3).clamp(-5,5)
        Wn = torch.cat([pais, fil])
        if it % 5 == 0:
            # snapshot da POPULACAO, nao so do melhor. Sem isto nao da para
            # distinguir "a populacao aprendeu" de "um sortudo puxou a curva" —
            # que foi exatamente o modo de falha do curriculo por melhor-individuo.
            q = torch.tensor([0., .25, .5, .75, 1.], device=DEV)
            snaps.append({
                'ger': it,
                'fit_percentis': [float(x) for x in torch.quantile(f, q)],
                'fit_media': float(f.mean()),
                # diversidade = desvio medio dos pesos na populacao. Se cai a
                # zero, virou monocultura e a evolucao parou de explorar.
                'diversidade': float(Wn.std(0).mean()),
                'diversidade_elite': float(Wn[:max(2, int(P*elite))].std(0).mean()),
                'alocacao_elite': alocacao(Wn, ne),
            })
        W = Wn
        if ckpt and (it % ckpt_cada == 0 or it == ger-1):
            tmp = ckpt + '.tmp'
            torch.save({'W': W, 'ger': it, 'hist': hist, 'snaps': snaps,
                        'rng': g.get_state(), 'cfg_id': cfg_id}, tmp)
            os.replace(tmp, ckpt)      # troca atomica: nunca fica ckpt corrompido
        if verbose and it % 5 == 0:
            vram = torch.cuda.max_memory_allocated()/1e9 if DEV=='cuda' else 0
            print(f'  ger {it:>3}  melhor {float(f[0]):>7.2f}  media {float(f.mean()):>7.2f}'
                  f'  div {snaps[-1]["diversidade"]:.3f}  VRAM {vram:.1f} GB', flush=True)
    return W[0], hist, snaps


def evoluir_sementes(Arq, cidades, cfg, P=512, ger=25, T=1500, seeds=(0,1,2),
                     elite=.15, verbose=True, R=1, cfg_gen=None, W0=None, sigma0=.2, avaliar_fn=None, paciencia=None, sigma_espinha=.05):
    """MEGA-LOTE de sementes: as S populacoes (uma por semente de evolucao)
    empilhadas num Lote so — B cresce S vezes e sai da regiao limitada por
    LANCAMENTO de kernel (VRAM vazia + GPU 'ocupada' = kernels pequenos).
    Selecao/mutacao POR BLOCO com um Generator por semente. NAO e bit-igual ao
    sequencial (o stream de mundos e por posicao no lote), mas os blocos sao
    estatisticamente iid e os MESMOS mundos pareiam as sementes entre si.
    Devolve {semente: (campeao, hist, snaps)}."""
    S = len(seeds); NPQ = Arq.NP
    gs = []
    Ws = []
    for sd in seeds:
        g = torch.Generator(device=DEV); g.manual_seed(sd)
        gs.append(g)
        if W0 is None:
            Ws.append(torch.randn(P, NPQ, generator=g, device=DEV)*.8)
        else:   # [E36] populacao nasce do campeao (genes novos = 0, desligados) + ruido sigma0: testa o INCREMENTO, nao a montagem
            base = W0[sd] if isinstance(W0, dict) else W0
            base = torch.as_tensor(base, dtype=torch.float32, device=DEV).flatten()
            w = torch.zeros(P, NPQ, device=DEV); w[:, :base.numel()] = base[None, :]
            ru = torch.randn(P, NPQ, generator=g, device=DEV)*sigma0
            ru[:, :base.numel()] *= sigma_espinha/max(sigma0, 1e-9)   # [CS 09-08] ruido cheio so nos genes NOVOS; a espinha copiada recebe sigma_espinha (era o modo de falha 'semeado contaminado')
            Ws.append(w + ru)
    W = torch.cat(Ws)                                  # (S*P, NP)
    hist = {sd: [] for sd in seeds}; snaps = {sd: [] for sd in seeds}
    ne = max(2, int(P*elite))
    for it in range(ger):
        # E20 curriculo (infancia protegida): cfg_gen(it, ger) -> cfg desta geracao (None = identidade)
        cfg_it = cfg_gen(it, ger) if cfg_gen is not None else cfg
        f = (avaliar_fn or avaliar)(Arq, W, cidades, cfg_it, T, seed=777000+it*13, R=R).view(S, P)   # [E43] avaliar_fn: outro simulador (campo.py)
        Wv = W.view(S, P, NPQ)
        novos = []
        for si, sd in enumerate(seeds):
            o = f[si].argsort(descending=True)
            Wb = Wv[si][o]; fb = f[si][o]
            hist[sd].append(float(fb[0]))
            idx = torch.randint(0, ne, (P-ne,), generator=gs[si], device=DEV)
            fil = (Wb[idx] + torch.randn(P-ne, NPQ, generator=gs[si],
                                         device=DEV)*.3).clamp(-5, 5)
            Wn = torch.cat([Wb[:ne], fil])
            if it % 5 == 0:
                q = torch.tensor([0., .25, .5, .75, 1.], device=DEV)
                snaps[sd].append({'ger': it,
                    'fit_percentis': [float(x) for x in torch.quantile(fb, q)],
                    'fit_media': float(fb.mean()),
                    'diversidade': float(Wn.std(0).mean()),
                    'alocacao_elite': alocacao(Wn, ne)})
            novos.append(Wn)
        W = torch.cat(novos)
        if verbose and it % 5 == 0:
            linha = ' '.join(f'{hist[sd][-1]:>8.2f}' for sd in seeds)
            print(f'  ger {it:>3} | {linha}   (melhor por semente)', flush=True)
        if paciencia and it >= paciencia:   # [E61d] parada antecipada: o melhor (media das sementes) nao subiu > 1 % em `paciencia` geracoes
            agora = sum(hist[sd][-1] for sd in seeds)/len(seeds); antes = sum(max(hist[sd][:-paciencia]) for sd in seeds)/len(seeds)
            if agora <= antes + 0.01*abs(antes) + 1e-6:
                if verbose: print(f'  parada antecipada na ger {it} (sem melhora em {paciencia} ger.)', flush=True)
                break
    Wv = W.view(S, P, NPQ)
    return {sd: (Wv[si][0], hist[sd], snaps[sd]) for si, sd in enumerate(seeds)}


def evoluir_juntas(arqs, cidades, cfg, P=512, ger=25, T=1500, seed=0, elite=.15,
                   verbose=True, R=1, ckpt=None, ckpt_cada=10):
    """Todas as arquiteturas evoluem NO MESMO RUN, geracao a geracao.

    Cada arq mantem seu proprio Generator semeado igual ao evoluir() isolado e
    os mundos de avaliacao ja sao os mesmos (seed+it*13) — o resultado por arq
    sai BIT A BIT igual ao sequencial (testes.py prova). O que muda: telemetria
    lado a lado por geracao, um checkpoint unico, uma VRAM por vez (as pops
    avaliam em sequencia dentro da geracao — pico igual ao de uma arq so)."""
    ests = {}
    for A in arqs:
        g = torch.Generator(device=DEV); g.manual_seed(seed)
        ests[A.nome] = dict(g=g, W=torch.randn(P, A.NP, generator=g, device=DEV)*.8,
                            hist=[], snaps=[])
    it0 = 0
    cfg_id = (f'JUNTAS P={P} ger={ger} T={T} R={R} seed={seed} elite={elite} '
              f'arqs={",".join(A.nome for A in arqs)}')
    if ckpt and os.path.exists(ckpt):
        d = torch.load(ckpt, map_location=DEV, weights_only=True)
        if d.get('cfg_id') != cfg_id:
            raise SystemExit(f'CHECKPOINT DE OUTRA CONFIG:\n  ckpt:  {d.get("cfg_id")}'
                             f'\n  agora: {cfg_id}\n  Use --do-zero ou repita a config.')
        for nome, e in ests.items():
            e['W'] = d['pops'][nome]; e['hist'] = d['hist'][nome]
            e['snaps'] = d['snaps'][nome]; e['g'].set_state(d['rng'][nome].cpu())
        it0 = d['ger']+1
        if verbose: print(f'  [retomando {ckpt} da geracao {it0}]')
    if verbose:
        print('  ger  | ' + ' '.join(f'{A.nome[:9]:>9}' for A in arqs) + '   (melhor da pop)')
    for it in range(it0, ger):
        linha = []
        for A in arqs:
            e = ests[A.nome]
            f = avaliar(A, e['W'], cidades, cfg, T, seed+it*13, R=R)
            o = f.argsort(descending=True); e['W'] = e['W'][o]; f = f[o]
            e['hist'].append(float(f[0]))
            ne = max(2, int(P*elite)); pais = e['W'][:ne]
            idx = torch.randint(0, ne, (P-ne,), generator=e['g'], device=DEV)
            fil = (pais[idx]+torch.randn(P-ne, A.NP, generator=e['g'], device=DEV)*.3).clamp(-5,5)
            Wn = torch.cat([pais, fil])
            if it % 5 == 0:
                q = torch.tensor([0., .25, .5, .75, 1.], device=DEV)
                e['snaps'].append({
                    'ger': it,
                    'fit_percentis': [float(x) for x in torch.quantile(f, q)],
                    'fit_media': float(f.mean()),
                    'diversidade': float(Wn.std(0).mean()),
                    'diversidade_elite': float(Wn[:ne].std(0).mean()),
                    'alocacao_elite': alocacao(Wn, ne)})
            e['W'] = Wn
            linha.append(f'{float(f[0]):>9.2f}')
        if ckpt and (it % ckpt_cada == 0 or it == ger-1):
            tmp = ckpt + '.tmp'
            torch.save({'cfg_id': cfg_id, 'ger': it,
                        'pops': {n: e['W'] for n, e in ests.items()},
                        'hist': {n: e['hist'] for n, e in ests.items()},
                        'snaps': {n: e['snaps'] for n, e in ests.items()},
                        'rng': {n: e['g'].get_state() for n, e in ests.items()}}, tmp)
            os.replace(tmp, ckpt)
        if verbose and it % 5 == 0:
            print(f'  {it:>4} | ' + ' '.join(linha), flush=True)
    return {n: (e['W'][0], e['hist'], e['snaps']) for n, e in ests.items()}
