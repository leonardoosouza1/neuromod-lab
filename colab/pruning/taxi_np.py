"""Teste da hipotese da PODA no dominio do taxi.

Cerebro = W (pesos) * M (mascara de conexoes ligadas/desligadas).
Tres estrategias de evolucao:
  gerar    — muta todos os pesos (o padrao)
  podar    — nasce denso, mutacao so' DESLIGA
  desenvolv— cronograma: explode -> poda -> consolida  (imita o cerebro)
"""
import numpy as np, heapq, time

GMAX = 5
NPX  = 6

def gerar_cidade(seed, n=24):
    r = np.random.default_rng(seed); pos = []
    while len(pos) < n:
        p = r.random(2)*11
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
    serv = np.zeros((n,5), dtype=np.float32)
    for t,(a,b) in enumerate([(0,3),(3,6),(6,8),(8,11),(11,13)]):
        for i in idx[a:b]: serv[i,t] = 1.0
    grp = np.zeros((n,GMAX), dtype=np.int64); tem = np.zeros(n, dtype=np.float32)
    for i in range(n):
        if len(adj[i]) >= 3:
            tem[i] = 1.0
            for k, j in enumerate(adj[i]):
                grp[i,k] = 0 if (np.arctan2(*(pos[j]-pos[i])[::-1]) % np.pi) < np.pi/2 else 1
    ds = np.stack([DI[:, serv[:,j]>0].min(1) if (serv[:,j]>0).any()
                   else np.full(n,20.,np.float32) for j in range(5)])
    return dict(n=n, A=A, W=W, DI=DI, serv=serv, grp=grp, tem=tem, ds=ds)

class Cfg:
    def __init__(s, d=1.0, trafego=.35, imposto=.18):
        s.fuel=.70+1.4*d; s.pneu=.18+.9*d; s.temp=1.6+4.*d; s.fome=.07+.25*d
        s.fadiga=.45+1.2*d; s.risco=.02+.12*d; s.oleo=.25+.7*d
        s.per=max(int(round(16-6*d)),6); s.base=6.; s.km=2.6
        s.trafego=trafego; s.imposto=imposto

NF = 18   # features por candidato

class Lote:
    """B mundos em paralelo, numa cidade."""
    def __init__(s, cid, B, cfg, seed=0):
        s.c=cid; s.cfg=cfg; s.B=B; s.n=cid['n']
        r = np.random.default_rng(seed); s.r = r
        n = s.n
        s.no=r.integers(0,n,B); s.indo=np.full(B,-1); s.rest=np.zeros(B)
        s.tpar=np.zeros(B); s.fuel=np.full(B,85.); s.fome=np.full(B,10.)
        s.fad=np.full(B,10.); s.pneu=np.full(B,100.); s.temp=np.full(B,25.)
        s.oleo=np.full(B,100.); s.dinh=np.full(B,60.); s.up=np.zeros((B,9))
        s.po_=np.full(B,-1); s.pd_=np.full(B,-1)
        s.ent=np.zeros(B); s.avar=np.zeros(B)
        s.fase=r.integers(0,2,(B,n)).astype(float)
        s.tsem=r.integers(0,cfg.per,(B,n)).astype(float)
        s.npc=r.random((B,n))*cfg.trafego*2
        s.po=r.integers(0,n,(B,NPX)); s.pd=r.integers(0,n,(B,NPX))
    def capf(s): return 100+35*s.up[:,0]
    def txp(s):  return 1./((1+.7*s.up[:,1])*(1+.5*s.up[:,7]))
    def txt(s):  return 1./(1+.7*s.up[:,2])
    def txo(s):  return 1./(1+.8*s.up[:,8])
    def vel(s):  return 1./(1+.3*s.up[:,3])
    def tar(s):  return 1.+.28*s.up[:,4]
    def obs(s):
        c=s.c; B=s.B; G=GMAX
        viz=c['A'][s.no]; val=viz>=0; vz=np.clip(viz,0,None)
        dpo=c['DI'][s.no[:,None], s.po]
        po_alvo=np.take_along_axis(s.po, dpo.argmin(1)[:,None],1).squeeze(1)
        alvo=np.where(s.pd_>=0, s.pd_, po_alvo)
        dal=c['DI'][vz, alvo[:,None]]
        cus=c['W'][s.no]; cong=np.take_along_axis(s.npc,vz,1)
        gs=c['grp'][s.no]; fn=np.take_along_axis(s.fase,s.no[:,None],1)
        vd=((gs==fn)|(c['tem'][s.no][:,None]==0)).astype(float)*2-1
        dsv=c['ds'][:,vz]                       # (5,B,G)
        est=np.stack([s.fuel/s.capf(), s.fome/100, s.fad/100, s.pneu/100,
                      s.temp/120, s.oleo/100, np.minimum(s.dinh/120,1.),
                      (s.pd_>=0).astype(float)],-1)
        F=np.concatenate([(-dal/6.)[...,None],(-cus/4.)[...,None],(-cong/2.)[...,None],
                          vd[...,None],(-dsv.transpose(1,2,0)/6.),
                          np.repeat(est[:,None,:],G,1),
                          np.ones((B,G,1))],-1)
        return F, val
    def serv_need(s):
        sv=s.c['serv'][s.no]
        nec=np.stack([1-s.fuel/s.capf(), s.fome/100., s.fad/100.,
                      np.maximum(1-s.pneu/100., s.temp/120.),
                      np.minimum(s.dinh/90.,1.)],-1)
        custo=np.array([2.,3.,0.,10.,26.])
        paga=(s.dinh[:,None]>=custo[None,:]).astype(float)
        return sv*nec*paga, sv*paga

def passo(m, esc):
    c=m.cfg; C=m.c; B=m.B; r=m.r
    m.tsem+=1; v=m.tsem>=c.per
    m.fase=np.where(v,1-m.fase,m.fase); m.tsem=np.where(v,0,m.tsem)
    m.temp=np.maximum(m.temp-1.6,25.)
    ch=(m.pd_>=0)&(m.no==m.pd_)&(m.rest<=0)
    if ch.any():
        d=C['DI'][np.clip(m.po_,0,None), np.clip(m.pd_,0,None)]
        br=(c.base+c.km*d)*m.tar()
        m.ent+=ch; m.dinh+=(br*(1-c.imposto))*ch
        m.po_=np.where(ch,-1,m.po_); m.pd_=np.where(ch,-1,m.pd_)
    livre=m.tpar<=0; m.tpar=np.maximum(m.tpar-1,0)
    an_=(m.rest>0)&livre; m.rest=np.where(an_,m.rest-1,m.rest)
    cg=an_&(m.rest<=0)
    m.no=np.where(cg,np.clip(m.indo,0,None),m.no); m.indo=np.where(cg,-1,m.indo)
    m.fome=np.minimum(m.fome+c.fome,100)
    ap=m.fad>=95
    m.tpar=np.where(ap,12.,m.tpar); m.fad=np.where(ap,40.,m.fad)
    pode=livre&(m.rest<=0)&(~ap)
    sv=C['serv'][m.no]
    def faz(i,cu,ef):
        ok=pode&(esc==GMAX+i)&(sv[:,i]>0)&(m.dinh>=cu)
        m.dinh=m.dinh-cu*ok; ef(ok); return ok
    o1=faz(0,2.,lambda ok: setattr(m,'fuel',np.where(ok,np.minimum(m.fuel+30,m.capf()),m.fuel)))
    o2=faz(1,3.,lambda ok: setattr(m,'fome',np.where(ok,np.maximum(m.fome-45,0),m.fome)))
    o3=faz(2,0.,lambda ok: setattr(m,'fad', np.where(ok,np.maximum(m.fad-30,0),m.fad)))
    def chk(ok):
        m.pneu=np.where(ok,100.,m.pneu); m.oleo=np.where(ok,100.,m.oleo)
        m.temp=np.where(ok,25.,m.temp)
    o4=faz(3,10.,chk)
    o5=pode&(esc==GMAX+4)&(sv[:,4]>0)&(m.dinh>=26.)
    if o5.any():
        m.dinh=m.dinh-26.*o5
        k=(m.up.sum(1)%9).astype(int)
        m.up[np.arange(B),k]+=o5
    so=o1|o2|o3|o4|o5
    hit=(m.po==m.no[:,None]); tem=hit.any(1); ks=hit.argmax(1)
    pega=pode&(~so)&(m.pd_<0)&tem
    m.po_=np.where(pega,m.no,m.po_)
    m.pd_=np.where(pega,np.take_along_axis(m.pd,ks[:,None],1).squeeze(1),m.pd_)
    if pega.any():
        ib=np.where(pega)[0]
        m.po[ib,ks[ib]]=r.integers(0,m.n,len(ib))
        m.pd[ib,ks[ib]]=r.integers(0,m.n,len(ib))
    mv=pode&(~so)&(~pega)&(esc<GMAX)
    viz=C['A'][m.no]; sel=np.clip(esc,0,GMAX-1)
    dst=np.take_along_axis(viz,sel[:,None],1).squeeze(1)
    val=mv&(dst>=0)
    cu=np.take_along_axis(C['W'][m.no],sel[:,None],1).squeeze(1)
    cu=cu+np.take_along_axis(m.npc,np.clip(dst,0,None)[:,None],1).squeeze(1)
    sf=val&(m.fuel<cu*c.fuel)
    m.avar+=sf; m.tpar=np.where(sf,18.,m.tpar); m.fuel=np.where(sf,15.,m.fuel)
    m.dinh=np.maximum(m.dinh-12*sf,0)
    rd=r.random(B)
    fu=val&(~sf)&(rd<np.maximum((1-m.pneu/100)-.45,0)*c.risco*m.txp())
    m.avar+=fu; m.tpar=np.where(fu,15.,m.tpar); m.pneu=np.where(fu,60.,m.pneu)
    ol=val&(~sf)&(~fu)&(m.oleo<12)&(rd<.05)
    m.avar+=ol; m.tpar=np.where(ol,22.,m.tpar); m.oleo=np.where(ol,45.,m.oleo)
    qt=val&(~sf)&(~fu)&(~ol)&(m.temp>92)
    m.avar+=qt; m.tpar=np.where(qt,14.,m.tpar); m.temp=np.where(qt,40.,m.temp)
    gs=np.take_along_axis(C['grp'][m.no],sel[:,None],1).squeeze(1)
    fn=np.take_along_axis(m.fase,m.no[:,None],1).squeeze(1)
    vd=(gs==fn)|(C['tem'][m.no]==0)
    an=val&(~sf)&(~fu)&(~ol)&(~qt)&vd
    m.indo=np.where(an,dst,m.indo)
    m.rest=np.where(an,np.maximum(np.round(cu*m.vel()),1),m.rest)
    m.fuel=m.fuel-cu*c.fuel*an
    m.fad=np.minimum(m.fad+cu*c.fadiga*an,100)
    m.pneu=np.maximum(m.pneu-cu*c.pneu*m.txp()*an,0)
    m.oleo=np.maximum(m.oleo-cu*c.oleo*m.txo()*an,0)
    m.temp=np.minimum(m.temp+cu*c.temp*m.txt()*an,120)
    m.npc=m.npc*.85+r.random((B,m.n))*(c.trafego*.45)

NPAR = NF+6   # reativo: 18 features + 5 servicos + bias

def rodar(Wef, cid, cfg, T, seed):
    """Wef: (P, NPAR) ja' com a mascara aplicada"""
    P=Wef.shape[0]; m=Lote(cid,P,cfg,seed=seed)
    for t in range(T):
        F,val=m.obs()
        s=np.einsum('bgf,bf->bg',F,Wef[:,:NF])
        s=np.where(val,s,-1e9)
        svn,sv=m.serv_need()
        ss=svn*Wef[:,NF:NF+5]+Wef[:,NF+5:NF+6]
        ss=np.where(sv>0,ss,-1e9)
        passo(m,np.concatenate([s,ss],1).argmax(1))
    return m

def avaliar(W, M, cidades, cfg, T, seed=0):
    Wef=W*M
    f=np.zeros(len(W))
    for ci,cid in enumerate(cidades):
        m=rodar(Wef,cid,cfg,T,seed+ci*97)
        f+=m.ent-0.3*m.avar
    return f/len(cidades)
