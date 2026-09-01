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
        s.fuel=.70+1.4*d; s.pneu=.18+.9*d; s.temp=1.6+4.*d; s.fome=.07+.25*d
        s.fadiga=.45+1.2*d; s.risco=.02+.12*d; s.oleo=.25+.7*d
        s.per=max(int(round(16-6*d)),6); s.base=6.; s.km=2.6
        s.trafego=trafego; s.imposto=imposto
        # ECO-FUEL V2 (opt-in): posto enche o TANQUE (nao +30) e pane vira
        # punicao real (fuel=5, mal da pra rastejar ao posto). Predicao
        # registrada em PREDICOES.md antes de rodar. Default False: nao
        # contamina baterias em andamento.
        s.eco2=False

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
        ds = []
        for c in range(NC):
            linha = []
            for j in range(5):
                m = cidades[c]['serv'][:,j] > 0
                linha.append(s.DIa[c][:, torch.tensor(m, device=DEV)].min(1).values
                             if m.any() else torch.full((n,), 20., device=DEV))
            ds.append(torch.stack(linha))
        s.dsa = torch.stack(ds)                       # (NC,5,n)
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
    def _spawn_polo(s):
        """(B,) sorteio de no ~ exp(-dist ao polo), para TODOS os mundos de uma
        vez. Gumbel-argmax == softmax-sampling, sem multinomial (que faz sync)."""
        d = s.DIa[s.cidx[:,None].expand(-1,s.n),
                  s.hot[:,None].expand(-1,s.n),
                  torch.arange(s.n, device=DEV)[None,:].expand(s.B,-1)]
        u = torch.rand(s.B, s.n, generator=s.gsim, device=DEV).clamp(min=1e-20)
        return (-d/3. - torch.log(-torch.log(u))).argmax(1)

    # resolve "qual cidade" por mundo
    def A_(s):    return s.Aa[s.cidx, s.no]
    def W_(s):    return s.Wa[s.cidx, s.no]
    def grp_(s):  return s.grpa[s.cidx, s.no]
    def tem_(s):  return s.tema[s.cidx, s.no]
    def serv_(s): return s.serva[s.cidx, s.no]
    def serv_need(s):
        """servico disponivel PONDERADO pela necessidade (posto so importa se falta combustivel)"""
        sv = s.serva[s.cidx, s.no]
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
        est = torch.stack([s.fuel/s.capf(), s.fome/100, s.fad/100, s.pneu/100,
                           s.temp/120, s.oleo/100, (s.dinh/120).clamp(max=1.),
                           (s.pd_>=0).float()], -1)
        F = torch.cat([(-dal/6.)[...,None], (-cus/4.)[...,None], (-cong/2.)[...,None],
                       vd[...,None], (-ds.permute(0,2,1)/6.),
                       est[:,None,:].expand(-1,G,-1),
                       s.UNS], -1)
        return F, val

NF = 1+1+1+1+5+8+1   # 18 features por candidato (ver NOMES_F em rodar.py)

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
    # entrega
    ch = (m.pd_>=0) & (m.no==m.pd_) & (m.rest<=0)
    d = m.DIa[m.cidx, m.po_.clamp(min=0), m.pd_.clamp(min=0)]
    br = (c.base+c.km*d)*m.tar(); im = br*c.imposto
    m.ent += ch.float(); m.rec += br*ch.float(); m.imp += im*ch.float()
    m.dinh += (br-im)*ch.float()
    m.po_ = torch.where(ch, torch.full_like(m.po_,-1), m.po_)
    m.pd_ = torch.where(ch, torch.full_like(m.pd_,-1), m.pd_)
    livre = m.tpar<=0; m.tpar = (m.tpar-1).clamp(min=0)
    an_ = (m.rest>0) & livre; m.rest = torch.where(an_, m.rest-1, m.rest)
    cg = an_ & (m.rest<=0)
    m.no = torch.where(cg, m.indo.clamp(min=0), m.no)
    m.indo = torch.where(cg, torch.full_like(m.indo,-1), m.indo)
    m.fome = (m.fome+c.fome).clamp(max=100)
    ap = m.fad>=95
    m.par_fad += ap.float()
    m.tpar = torch.where(ap, torch.full_like(m.tpar,12.), m.tpar)
    m.fad  = torch.where(ap, torch.full_like(m.fad,40.), m.fad)
    pode = livre & (m.rest<=0) & (~ap)
    sv = m.serv_()
    # servicos (sem closures: compile-friendly)
    o1 = pode & (esc==GMAX+0) & (sv[:,0]>0) & (m.dinh>=2.)
    m.dinh = m.dinh - 2.*o1.float()
    m.fuel = torch.where(o1, torch.minimum(m.fuel + (m.capf() if m.cfg.eco2 else 30.), m.capf()), m.fuel)
    o2 = pode & (esc==GMAX+1) & (sv[:,1]>0) & (m.dinh>=3.)
    m.dinh = m.dinh - 3.*o2.float()
    m.fome = torch.where(o2, (m.fome-45).clamp(min=0), m.fome)
    o3 = pode & (esc==GMAX+2) & (sv[:,2]>0)
    m.fad = torch.where(o3, (m.fad-30).clamp(min=0), m.fad)
    o4 = pode & (esc==GMAX+3) & (sv[:,3]>0) & (m.dinh>=10.)
    m.dinh = m.dinh - 10.*o4.float()
    m.pneu = torch.where(o4, torch.full_like(m.pneu,100.), m.pneu)
    m.oleo = torch.where(o4, torch.full_like(m.oleo,100.), m.oleo)
    m.temp = torch.where(o4, torch.full_like(m.temp,25.), m.temp)
    o5 = pode & (esc==GMAX+4) & (sv[:,4]>0) & (m.dinh>=26.)
    m.dinh = m.dinh - 26.*o5.float()
    k = (m.up.sum(1) % 9).long()
    m.up[m.ARB, k] += o5.float(); m.melh += o5.float()
    serv_ok = o1|o2|o3|o4|o5
    # pegar passageiro (qualquer um dos NPX que esteja neste no)
    hit = (m.po == m.no[:,None]); tem = hit.any(1); ks = hit.float().argmax(1)
    pega = pode & (~serv_ok) & (m.pd_<0) & tem
    m.po_ = torch.where(pega, m.no, m.po_)
    m.pd_ = torch.where(pega, m.pd.gather(1, ks[:,None]).squeeze(1), m.pd_)
    # respawn incondicional-mascarado (o sorteio roda p/ todos, so aplica onde pegou)
    if c.mundo in ('hotspot','mare'):
        novo_po = m._spawn_polo()
    else:
        novo_po = torch.randint(0,m.n,(B,),generator=m.gsim,device=DEV)
    novo_pd = torch.randint(0,m.n,(B,),generator=m.gsim,device=DEV)
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
    sf = val & (m.fuel < cuf*c.fuel)
    m.avar += sf.float(); m.av_fuel += sf.float(); m.tpar = torch.where(sf, torch.full_like(m.tpar,18.), m.tpar)
    m.fuel = torch.where(sf, torch.full_like(m.fuel, 5. if m.cfg.eco2 else 15.), m.fuel)
    m.dinh = (m.dinh-12*sf.float()).clamp(min=0)
    rd = torch.rand(B, generator=m.gsim, device=DEV)
    fu = val & (~sf) & (rd < ((1-m.pneu/100)-.45).clamp(min=0)*c.risco*m.txp())
    m.avar += fu.float(); m.av_furo += fu.float(); m.tpar = torch.where(fu, torch.full_like(m.tpar,15.), m.tpar)
    m.pneu = torch.where(fu, torch.full_like(m.pneu,60.), m.pneu)
    ol = val & (~sf) & (~fu) & (m.oleo<12) & (rd<.05)
    m.avar += ol.float(); m.av_oleo += ol.float(); m.tpar = torch.where(ol, torch.full_like(m.tpar,22.), m.tpar)
    m.oleo = torch.where(ol, torch.full_like(m.oleo,45.), m.oleo)
    qt = val & (~sf) & (~fu) & (~ol) & (m.temp>92)
    m.avar += qt.float(); m.av_quente += qt.float(); m.tpar = torch.where(qt, torch.full_like(m.tpar,14.), m.tpar)
    m.temp = torch.where(qt, torch.full_like(m.temp,40.), m.temp)
    gs = torch.gather(m.grp_(),1,sel[:,None]).squeeze(1).float()
    fn = torch.gather(m.fase,1,m.no[:,None]).squeeze(1)
    vd = (gs==fn) | (m.tem_()==0)
    an = val & (~sf) & (~fu) & (~ol) & (~qt) & vd
    m.indo = torch.where(an, dst, m.indo)
    m.rest = torch.where(an, (cu*m.vel()).round().clamp(min=1), m.rest)
    m.fuel = m.fuel - cuf*c.fuel*an.float()
    m.fad  = (m.fad  + cu*c.fadiga*an.float()).clamp(max=100)
    m.pneu = (m.pneu - cuf*c.pneu*m.txp()*an.float()).clamp(min=0)
    m.oleo = (m.oleo - cuf*c.oleo*m.txo()*an.float()).clamp(min=0)
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
          (infancia 5%). T_REF fixa a infancia em passos ABSOLUTOS."""
    nome='ser vital'; NP=NF+6+6+6; K=16; KAPPA=5e-4; T_REF=600
    modo='poda'
    def reset(s,m,W):
        B=m.B
        s.wo = W[:, NF+6:NF+11]                          # (B,5) pesos dos orgaos
        fr = torch.sigmoid(W[:, NF+11])*.45+.05          # infancia = 5..50% de T_REF
        if s.modo=='curta':  fr = torch.full_like(fr, .05)
        if s.modo=='direto': fr = torch.zeros_like(fr)
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
    def extra(s,m,W,viz):
        B=m.B
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
        gate = s.mask * s.wo
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
        if s.modo in ('poda','poda_aleatoria','curta'):
            frac = s.contrib / (s.contrib.sum(1, keepdim=True)+1e-9)
            manter = (frac > s.limiar[:,None]*0.2).float()
            if s.modo == 'poda_aleatoria':
                # mesma CONTAGEM de sobreviventes, orgaos sorteados (controle)
                perm = torch.rand(B,5,generator=s.gp,device=DEV).argsort(1)
                manter = manter.gather(1, perm)
            s.mask = torch.where(cruza[:,None], manter, s.mask)
        # custo neural: so na fase adulta (infancia e subsidiada)
        adulto = (s.t.float() > s.Tb).float()
        pen = s.KAPPA * s.mask.sum(1) * adulto
        m.custo_neural = getattr(m, 'custo_neural', torch.zeros(B, device=DEV)) + pen

ARQS = [Reativo, BancoEMA, Diadica, Corpo, Hibrido, MemCusto, MapaServico]
# RotaCalculada e SerVital ficam FORA das baterias padrao: sao o E4 e o E8
# do doc 19/21, com runners e controles proprios (src/e4_rota.py, e8_vida.py)

# ============================ RODAR / EVOLUIR ============================
def um_passo(m, a, Wb):
    """um tick completo: observar -> pontuar -> agir."""
    F, val = m.obs(); viz = m.A_().clamp(min=0)
    sc = torch.einsum('bgf,bf->bg', F, Wb[:,:NF]) + a.extra(m, Wb, viz)
    sc = sc.masked_fill(~val, -1e9)
    svn, sv = m.serv_need()
    ss = (svn*Wb[:,NF:NF+5] + Wb[:,NF+5:NF+6]).masked_fill(sv<=0, -1e9)
    tudo = torch.cat([sc, ss],1)
    # arqs com decisao propria (ex.: temperatura por fase da vida — SerVital)
    esc = a.decidir(tudo, m) if hasattr(a, 'decidir') else tudo.argmax(1)
    passo(m, esc)

# torch.compile e opcional (NM_COMPILE=0 desliga). Fallback silencioso p/ eager
# se o backend (triton) nao suportar a GPU. O ganho vem da fusao dos ~200
# kernels elementwise por passo.
_PASSO_C = None
_COMPILE_OK = None
def _passo_fn():
    global _PASSO_C, _COMPILE_OK
    if os.environ.get('NM_COMPILE', '1') == '0' or DEV != 'cuda':
        return um_passo
    if _COMPILE_OK is False:
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

def modo_execucao():
    """'compile' ou 'eager' — gravar no JSON: compile e eager divergem por
    arredondamento (~1e-5 em fuel/temp), entao bateria com modo misto precisa
    ficar auditavel."""
    if os.environ.get('NM_COMPILE', '1') == '0' or DEV != 'cuda' or _COMPILE_OK is False:
        return 'eager'
    return 'compile'

def rodar(Arq, W, cidades, cfg, T, seed, R=1):
    global _COMPILE_OK
    P = W.shape[0]; m = Lote(cidades, P, cfg, seed=seed, R=R)
    Wb = W[m.gidx]
    a = Arq(); a.reset(m, Wb)
    fn = _passo_fn()
    for t in range(T):
        try:
            fn(m, a, Wb)
        except Exception as e:
            # compile falha na 1a chamada de um grafo novo (arq/shape novos = t==0
            # desta rodada). O passo pode ter executado PELA METADE (subgrafos
            # anteriores ja mutaram m) — nunca re-executar por cima: reconstruir
            # a rodada inteira do zero em eager.
            if fn is not um_passo and t == 0:
                print(f'  [compile falhou ({type(e).__name__}); refazendo esta '
                      f'rodada em eager — modo gravado no JSON]', flush=True)
                _COMPILE_OK = False
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
    fit = m.ent - 0.3*m.avar - getattr(m, 'custo_neural', 0.)
    return fit.view(W.shape[0], m.NC*m.R).mean(1)

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
