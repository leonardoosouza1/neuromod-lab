import torch, numpy as np, json, time, os
from datetime import datetime
DEV = 'cuda' if torch.cuda.is_available() else 'cpu'

GMAX = 5    # grau maximo de um no
NPX  = 6    # passageiros disponiveis por mundo

# ============================ CIDADES ============================
def gerar_cidade(seed, n=26):
    r = np.random.default_rng(seed); pos = []
    while len(pos) < n:
        p = r.random(2)*12
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
    for t, (a,b) in enumerate([(0,3),(3,6),(6,8),(8,12),(12,14)]):
        for i in idx[a:b]: serv[i,t] = 1.0
    grp = np.zeros((n,GMAX), dtype=np.int64); tem = np.zeros(n, dtype=np.float32)
    for i in range(n):
        if len(adj[i]) >= 3:
            tem[i] = 1.0
            for k, j in enumerate(adj[i]):
                ang = np.arctan2(*(pos[j]-pos[i])[::-1]) % np.pi
                grp[i,k] = 0 if ang < np.pi/2 else 1
    return dict(n=n, A=A, W=W, DI=DI, serv=serv, grp=grp, tem=tem)

class Cfg:
    def __init__(s, d=1.0, trafego=.35, imposto=.18):
        s.fuel=.70+1.4*d; s.pneu=.18+.9*d; s.temp=1.6+4.*d; s.fome=.07+.25*d
        s.fadiga=.45+1.2*d; s.risco=.02+.12*d; s.oleo=.25+.7*d
        s.per=max(int(round(16-6*d)),6); s.base=6.; s.km=2.6
        s.trafego=trafego; s.imposto=imposto

# ============================ MUNDO EM LOTE ============================
class Lote:
    """B = P genomas x NC cidades, tudo num tensor so."""
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
        s.imp=torch.zeros(B,device=DEV); s.avar=torch.zeros(B,device=DEV)
        s.melh=torch.zeros(B,device=DEV)
        s.fase=ri(2,(B,n)).float(); s.tsem=ri(cfg.per,(B,n)).float()
        s.npc=torch.rand(B,n,generator=g,device=DEV)*cfg.trafego*2
        s.po=ri(n,(B,NPX)); s.pd=ri(n,(B,NPX)); s.t=0
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
        custo = torch.tensor([2.,3.,0.,10.,26.], device=DEV)
        paga = (s.dinh[:,None] >= custo[None,:]).float()
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
        kb = dpo.argmin(1)
        po_alvo = s.po.gather(1, kb[:,None]).squeeze(1)
        alvo = torch.where(s.pd_>=0, s.pd_, po_alvo)
        dal = s.DIa[ce, vz, alvo[:,None].expand(-1,G)]
        cus = s.W_(); cong = torch.gather(s.npc, 1, vz)
        gs = s.grp_(); fn = torch.gather(s.fase, 1, s.no[:,None]).expand(-1,G)
        vd = ((gs.float()==fn) | (s.tem_()[:,None]==0)).float()*2-1
        ds = s.dsa[s.cidx[:,None,None].expand(-1,5,G),
                   torch.arange(5,device=DEV)[None,:,None].expand(B,-1,G),
                   vz[:,None,:].expand(-1,5,-1)]              # (B,5,G)
        est = torch.stack([s.fuel/s.capf(), s.fome/100, s.fad/100, s.pneu/100,
                           s.temp/120, s.oleo/100, (s.dinh/120).clamp(max=1.),
                           (s.pd_>=0).float()], -1)
        F = torch.cat([(-dal/6.)[...,None], (-cus/4.)[...,None], (-cong/2.)[...,None],
                       vd[...,None], (-ds.permute(0,2,1)/6.),
                       est[:,None,:].expand(-1,G,-1),
                       torch.ones(B,G,1,device=DEV)], -1)
        return F, val

NF = 1+1+1+1+5+8+1   # 18 features por candidato (ver NOMES_F em rodar.py)

# ============================ PASSO ============================
def passo(m, esc):
    """esc: (B,) 0..GMAX-1 = vizinho | GMAX..GMAX+4 = servico"""
    c = m.cfg; B = m.B; m.t += 1
    m.tsem += 1; v = m.tsem >= c.per
    m.fase = torch.where(v, 1-m.fase, m.fase)
    m.tsem = torch.where(v, torch.zeros_like(m.tsem), m.tsem)
    m.temp = (m.temp-1.6).clamp(min=25.)
    # entrega
    ch = (m.pd_>=0) & (m.no==m.pd_) & (m.rest<=0)
    if ch.any():
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
    m.tpar = torch.where(ap, torch.full_like(m.tpar,12.), m.tpar)
    m.fad  = torch.where(ap, torch.full_like(m.fad,40.), m.fad)
    pode = livre & (m.rest<=0) & (~ap)
    sv = m.serv_()
    def faz(i, cu, ef):
        ok = pode & (esc==GMAX+i) & (sv[:,i]>0) & (m.dinh>=cu)
        m.dinh = m.dinh - cu*ok.float(); ef(ok); return ok
    o1 = faz(0, 2., lambda ok: setattr(m,'fuel', torch.where(ok, torch.minimum(m.fuel+30, m.capf()), m.fuel)))
    o2 = faz(1, 3., lambda ok: setattr(m,'fome', torch.where(ok, (m.fome-45).clamp(min=0), m.fome)))
    o3 = faz(2, 0., lambda ok: setattr(m,'fad',  torch.where(ok, (m.fad-30).clamp(min=0), m.fad)))
    def chk(ok):
        m.pneu = torch.where(ok, torch.full_like(m.pneu,100.), m.pneu)
        m.oleo = torch.where(ok, torch.full_like(m.oleo,100.), m.oleo)
        m.temp = torch.where(ok, torch.full_like(m.temp,25.), m.temp)
    o4 = faz(3, 10., chk)
    o5 = pode & (esc==GMAX+4) & (sv[:,4]>0) & (m.dinh>=26.)
    if o5.any():
        m.dinh = m.dinh - 26.*o5.float()
        k = (m.up.sum(1) % 9).long()
        m.up[torch.arange(B,device=DEV), k] += o5.float(); m.melh += o5.float()
    serv_ok = o1|o2|o3|o4|o5
    # pegar passageiro (qualquer um dos NPX que esteja neste no)
    hit = (m.po == m.no[:,None]); tem = hit.any(1); ks = hit.float().argmax(1)
    pega = pode & (~serv_ok) & (m.pd_<0) & tem
    m.po_ = torch.where(pega, m.no, m.po_)
    m.pd_ = torch.where(pega, m.pd.gather(1, ks[:,None]).squeeze(1), m.pd_)
    if pega.any():
        ib = pega.nonzero(as_tuple=True)[0]
        m.po[ib, ks[ib]] = torch.randint(0,m.n,(len(ib),),generator=m.gsim,device=DEV)
        m.pd[ib, ks[ib]] = torch.randint(0,m.n,(len(ib),),generator=m.gsim,device=DEV)
    # mover
    mv = pode & (~serv_ok) & (~pega) & (esc<GMAX)
    viz = m.A_(); sel = esc.clamp(max=GMAX-1)
    dst = torch.gather(viz,1,sel[:,None]).squeeze(1)
    val = mv & (dst>=0)
    cu = torch.gather(m.W_(),1,sel[:,None]).squeeze(1)
    cu = cu + torch.gather(m.npc,1,dst.clamp(min=0)[:,None]).squeeze(1)
    sf = val & (m.fuel < cu*c.fuel)
    m.avar += sf.float(); m.tpar = torch.where(sf, torch.full_like(m.tpar,18.), m.tpar)
    m.fuel = torch.where(sf, torch.full_like(m.fuel,15.), m.fuel)
    m.dinh = (m.dinh-12*sf.float()).clamp(min=0)
    rd = torch.rand(B, generator=m.gsim, device=DEV)
    fu = val & (~sf) & (rd < ((1-m.pneu/100)-.45).clamp(min=0)*c.risco*m.txp())
    m.avar += fu.float(); m.tpar = torch.where(fu, torch.full_like(m.tpar,15.), m.tpar)
    m.pneu = torch.where(fu, torch.full_like(m.pneu,60.), m.pneu)
    ol = val & (~sf) & (~fu) & (m.oleo<12) & (rd<.05)
    m.avar += ol.float(); m.tpar = torch.where(ol, torch.full_like(m.tpar,22.), m.tpar)
    m.oleo = torch.where(ol, torch.full_like(m.oleo,45.), m.oleo)
    qt = val & (~sf) & (~fu) & (~ol) & (m.temp>92)
    m.avar += qt.float(); m.tpar = torch.where(qt, torch.full_like(m.tpar,14.), m.tpar)
    m.temp = torch.where(qt, torch.full_like(m.temp,40.), m.temp)
    gs = torch.gather(m.grp_(),1,sel[:,None]).squeeze(1).float()
    fn = torch.gather(m.fase,1,m.no[:,None]).squeeze(1)
    vd = (gs==fn) | (m.tem_()==0)
    an = val & (~sf) & (~fu) & (~ol) & (~qt) & vd
    m.indo = torch.where(an, dst, m.indo)
    m.rest = torch.where(an, (cu*m.vel()).round().clamp(min=1), m.rest)
    m.fuel = m.fuel - cu*c.fuel*an.float()
    m.fad  = (m.fad  + cu*c.fadiga*an.float()).clamp(max=100)
    m.pneu = (m.pneu - cu*c.pneu*m.txp()*an.float()).clamp(min=0)
    m.oleo = (m.oleo - cu*c.oleo*m.txo()*an.float()).clamp(min=0)
    m.temp = (m.temp + cu*c.temp*m.txt()*an.float()).clamp(max=120)
    m.npc = m.npc*.85 + torch.rand(B,m.n,generator=m.gsim,device=DEV)*(c.trafego*.45)
    return m

# ============================ CEREBROS ============================
class Reativo:
    nome='reativo'; NP=NF+6
    def reset(s,m,W): pass
    def extra(s,m,W,viz): return 0.
class BancoEMA:
    nome='banco EMA'; NP=NF+6+6
    def reset(s,m,W):
        s.al = torch.exp(-1/(2+30*(W[:,NF+9:NF+12].abs()+.1)))   # (B,3)
        s.E  = torch.zeros(m.B,3,m.n,device=DEV)
    def extra(s,m,W,viz):
        oc = torch.zeros(m.B,m.n,device=DEV); oc.scatter_(1,m.no[:,None],1.)
        a = s.al[:,:,None]
        s.E = a*s.E + (1-a)*oc[:,None,:]
        g = torch.stack([torch.gather(s.E[:,k],1,viz) for k in range(3)],1)
        return torch.einsum('bk,bkg->bg', W[:,NF+6:NF+9], g)
class Diadica:
    nome='diadica'; NP=NF+6+6; L=6
    def reset(s,m,W):
        s.buf = torch.zeros(m.B,2**s.L,dtype=torch.long,device=DEV)
        s.out = torch.zeros(m.B,GMAX,device=DEV); s.p=0
    def extra(s,m,W,viz):
        s.out.zero_()
        N = s.buf.shape[1]
        if s.p > 0:
            hist = torch.roll(s.buf, shifts=-(s.p % N), dims=1).flip(1)
            valido = min(s.p, N)
            for j in range(s.L):
                a, b = 2**j, min(2**(j+1), N)
                if a < valido:
                    jan = hist[:, a:min(b, valido)]
                    if jan.shape[1] > 0:
                        s.out += W[:,NF+6+j:NF+7+j]*(jan[:,:,None]==viz[:,None,:]).float().mean(1)
        s.buf[:, s.p % N] = m.no; s.p += 1
        return s.out
class Corpo:
    nome='corpo'; NP=NF+6+6
    def reset(s,m,W): pass
    def extra(s,m,W,viz):
        d = torch.stack([1-m.fuel/m.capf(), m.fome/100, m.fad/100,
                         1-m.pneu/100, m.temp/120],1)
        k = d.argmax(1); mp = torch.tensor([0,1,2,3,3],device=DEV)[k]
        ds = torch.stack([m.dsa[m.cidx, j, :].gather(1,viz) for j in range(4)],1)
        sel = ds[torch.arange(m.B,device=DEV), mp]
        peso = W[torch.arange(m.B,device=DEV), NF+6+k]
        return (peso*d.max(1).values)[:,None]*(-sel/6.)
class Hibrido:
    nome='hibrido'; NP=NF+6+6+6; L=6
    def reset(s,m,W):
        s.buf = torch.zeros(m.B,2**s.L,dtype=torch.long,device=DEV)
        s.out = torch.zeros(m.B,GMAX,device=DEV); s.p=0
    def extra(s,m,W,viz):
        s.out.zero_()
        N = s.buf.shape[1]
        if s.p > 0:
            hist = torch.roll(s.buf, shifts=-(s.p % N), dims=1).flip(1)
            valido = min(s.p, N)
            for j in range(s.L):
                a, b = 2**j, min(2**(j+1), N)
                if a < valido:
                    jan = hist[:, a:min(b, valido)]
                    if jan.shape[1] > 0:
                        s.out += W[:,NF+6+j:NF+7+j]*(jan[:,:,None]==viz[:,None,:]).float().mean(1)
        s.buf[:, s.p % N] = m.no; s.p += 1
        d = torch.stack([1-m.fuel/m.capf(), m.fome/100, m.fad/100,
                         1-m.pneu/100, m.temp/120],1)
        k = d.argmax(1); mp = torch.tensor([0,1,2,3,3],device=DEV)[k]
        ds = torch.stack([m.dsa[m.cidx, j, :].gather(1,viz) for j in range(4)],1)
        sel = ds[torch.arange(m.B,device=DEV), mp]
        peso = W[torch.arange(m.B,device=DEV), NF+12+k]
        return s.out + (peso*d.max(1).values)[:,None]*(-sel/6.)
ARQS = [Reativo, BancoEMA, Diadica, Corpo, Hibrido]

# ============================ RODAR / EVOLUIR ============================
def rodar(Arq, W, cidades, cfg, T, seed, R=1):
    P = W.shape[0]; m = Lote(cidades, P, cfg, seed=seed, R=R)
    Wb = W[m.gidx]
    a = Arq(); a.reset(m, Wb)
    for t in range(T):
        F, val = m.obs(); viz = m.A_().clamp(min=0)
        s = torch.einsum('bgf,bf->bg', F, Wb[:,:NF]) + a.extra(m, Wb, viz)
        s = s.masked_fill(~val, -1e9)
        svn, sv = m.serv_need()
        ss = (svn*Wb[:,NF:NF+5] + Wb[:,NF+5:NF+6]).masked_fill(sv<=0, -1e9)
        passo(m, torch.cat([s, ss],1).argmax(1))
    return m

def avaliar(Arq, W, cidades, cfg, T, seed=0, R=1):
    m = rodar(Arq, W, cidades, cfg, T, seed, R=R)
    return (m.ent - 0.3*m.avar).view(W.shape[0], m.NC*m.R).mean(1)

def evoluir(Arq, cidades, cfg, P=512, ger=25, T=1500, seed=0, elite=.15, verbose=True, R=1):
    g = torch.Generator(device=DEV); g.manual_seed(seed)
    W = torch.randn(P, Arq.NP, generator=g, device=DEV)*.8
    hist, snaps = [], []
    for it in range(ger):
        f = avaliar(Arq, W, cidades, cfg, T, seed+it*13, R=R)
        o = f.argsort(descending=True); W = W[o]; f = f[o]
        hist.append(float(f[0]))
        ne = max(2, int(P*elite)); pais = W[:ne]
        idx = torch.randint(0, ne, (P-ne,), generator=g, device=DEV)
        fil = (pais[idx]+torch.randn(P-ne,Arq.NP,generator=g,device=DEV)*.3).clamp(-5,5)
        W = torch.cat([pais, fil])
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
                'diversidade': float(W.std(0).mean()),
                'diversidade_elite': float(W[:max(2, int(P*elite))].std(0).mean()),
            })
        if verbose and it % 5 == 0:
            vram = torch.cuda.max_memory_allocated()/1e9 if DEV=='cuda' else 0
            print(f'  ger {it:>3}  melhor {float(f[0]):>7.2f}  media {float(f.mean()):>7.2f}'
                  f'  div {snaps[-1]["diversidade"]:.3f}  VRAM {vram:.1f} GB')
    return W[0], hist, snaps
