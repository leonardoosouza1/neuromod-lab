"""ARENA — o mundo vira DISPUTA (pedido do Leonardo, 2026-09-01).

O que muda em relacao ao lab.py (que fica intacto, como referencia):
  . cidade GRANDE (n=120 default)
  . K taxis no MESMO mundo, disputando os MESMOS passageiros
  . congestao CAUSADA pelos taxis: densidade por no vira custo de transito
  . servico com CAPACIDADE 1: segundo taxi na bomba ESPERA (fila real)
  . visao LOCAL (raio): sem oraculo global de passageiro; ds de servico some
  . MORTE: fuel<=0 sem dinheiro pro guincho = fim do episodio para o ser
  . fitness individual no mundo compartilhado -> selecao por vencer a disputa

Mesma interface de 18 features do lab.py: as arquiteturas rodam SEM MUDANCA.
Mesmas regras de perf (zero sync no loop quente, mascaras, sem tensor novo).
"""
import torch, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from lab import DEV, GMAX, gerar_cidade
NF = 18   # CONGELADO: a arena tem layout proprio de 18 features. O lab.py vivo
          # e editado por outra sessao (NF virou 21 em 2026-09-01 21:27) — a
          # arena nao pode depender dele, senao os genomas salvos viram lixo.

# ---- arquiteturas congeladas (copiadas do lab.py em 2026-09-01, NF=18) ----
class Reativo:
    nome='reativo'; NP=NF+6+6+6
    def reset(s,m,W): pass
    def extra(s,m,W,viz): return 0.
    def atualizar(s,m): pass
class BancoEMA:
    nome='banco EMA'; NP=NF+6+6+6
    def reset(s,m,W):
        s.al = torch.exp(-1/(2+30*(W[:,NF+9:NF+12].abs()+.1)))
        s.E  = torch.zeros(m.B,3,m.n,device=DEV)
    def extra(s,m,W,viz):
        oc = torch.zeros(m.B,m.n,device=DEV); oc.scatter_(1,m.no[:,None],1.)
        a = s.al[:,:,None]
        s.E = a*s.E + (1-a)*oc[:,None,:]
        g = s.E.gather(2, viz[:,None,:].expand(-1,3,-1))
        return torch.einsum('bk,bkg->bg', W[:,NF+6:NF+9], g)
    def atualizar(s,m): pass
class MemCusto:
    nome='mem custo'; NP=NF+6+6+6
    def reset(s,m,W):
        s.k = torch.sigmoid(W[:,NF+6:NF+7]); s.C = torch.zeros(m.B, m.n, device=DEV)
    def extra(s,m,W,viz):
        s._obs = torch.gather(m.npc, 1, m.no[:,None]); s._no = m.no
        return W[:,NF+7:NF+8]*(-torch.gather(s.C, 1, viz))
    def atualizar(s,m):
        atual = torch.gather(s.C, 1, s._no[:,None])
        s.C.scatter_(1, s._no[:,None], atual + s.k*(s._obs-atual))
ARQS_A = [Reativo, BancoEMA, MemCusto]
POR_A = {A.nome: A for A in ARQS_A}

def perito_W(NP=36):
    w = torch.zeros(NP, device=DEV)
    w[0]=4.0; w[1]=0.6; w[2]=0.8; w[3]=1.2
    w[4]=1.2; w[5]=.10; w[6]=.05; w[7]=.60; w[8]=.05
    w[NF:NF+5] = torch.tensor([20.,14.,10.,18.,3.], device=DEV); w[NF+5] = -4.0
    return w

NPX_A = 18          # passageiros por mundo (cidade grande, mais gente)

class CfgArena:
    def __init__(s, n_cid=120, K=6, raio=7., d=1.0, imposto=.18):
        s.n_cid=n_cid; s.K=K; s.raio=raio; s.imposto=imposto
        s.fuel=.70+1.4*d; s.pneu=.18+.9*d; s.temp=1.6+4.*d; s.fome=.07+.25*d
        s.fadiga=.45+1.2*d; s.risco=.02+.12*d; s.oleo=.25+.7*d
        s.per=max(int(round(16-6*d)),6); s.base=6.; s.km=2.6
        # eco2 ja embutida: posto enche o tanque; pane da 5 e cobra guincho
        s.guincho=12.; s.cong_taxi=.9   # custo extra por taxi-vizinho no no

class Mundo:
    """M mundos x K taxis. Estado por-taxi tem shape (M*K,); por-mundo, (M,...).
    wid[b] = mundo do taxi b. Passageiros/semaforo/servico vivem no MUNDO."""
    def __init__(s, cidades, M, cfg, seed=0):
        s.cfg=cfg; K=cfg.K; s.M=M; s.K=K; s.B=B=M*K
        NC=len(cidades); s.NC=NC
        n=cidades[0]['n']; s.n=n
        st=lambda k,dt=torch.float32: torch.stack(
            [torch.tensor(c[k],device=DEV,dtype=dt) for c in cidades])
        s.Aa=st('A',torch.long); s.Wa=st('W'); s.DIa=st('DI')
        s.serva=st('serv'); s.grpa=st('grp',torch.long); s.tema=st('tem')
        s.cidm=torch.arange(NC,device=DEV).repeat(M//NC+1)[:M]   # cidade por mundo
        s.wid=torch.arange(M,device=DEV).repeat_interleave(K)    # mundo por taxi
        s.cidx=s.cidm[s.wid]
        g=torch.Generator(device=DEV); g.manual_seed(seed); s.g=g
        s.gsim=torch.Generator(device=DEV); s.gsim.manual_seed(seed+999983)
        ri=lambda hi,sh: torch.randint(0,hi,sh,generator=g,device=DEV)
        # ---- taxis ----
        s.no=ri(n,(B,)); s.indo=torch.full((B,),-1,dtype=torch.long,device=DEV)
        s.rest=torch.zeros(B,device=DEV); s.tpar=torch.zeros(B,device=DEV)
        s.fuel=torch.full((B,),85.,device=DEV); s.fome=torch.full((B,),10.,device=DEV)
        s.fad=torch.full((B,),10.,device=DEV); s.pneu=torch.full((B,),100.,device=DEV)
        s.temp=torch.full((B,),25.,device=DEV); s.oleo=torch.full((B,),100.,device=DEV)
        s.dinh=torch.full((B,),60.,device=DEV); s.up=torch.zeros(B,9,device=DEV)
        s.po_=torch.full((B,),-1,dtype=torch.long,device=DEV)
        s.pd_=torch.full((B,),-1,dtype=torch.long,device=DEV)
        s.ent=torch.zeros(B,device=DEV); s.avar=torch.zeros(B,device=DEV)
        s.rec=torch.zeros(B,device=DEV); s.viva=torch.ones(B,device=DEV)
        s.morte_t=torch.full((B,),-1.,device=DEV)
        s.fome_t=torch.zeros(B,device=DEV)   # ticks seguidos faminto
        s.morte_causa=torch.zeros(B,device=DEV)  # 0 viva, 1 pane, 2 fome
        s.av_fuel=torch.zeros(B,device=DEV)
        # ---- mundo compartilhado ----
        s.po=ri(n,(M,NPX_A)); s.pd=ri(n,(M,NPX_A))
        s.fase=ri(2,(M,n)).float(); s.tsem=ri(cfg.per,(M,n)).float()
        s.dens=torch.zeros(M,n,device=DEV)      # densidade de taxi por no
        s.t=torch.zeros((),dtype=torch.long,device=DEV)
        s.ARB=torch.arange(B,device=DEV); s.ARM=torch.arange(M,device=DEV)
        s.CUSTO=torch.tensor([2.,3.,0.,10.,26.],device=DEV)
        s.MP=torch.tensor([0,1,2,3,3],device=DEV)
        # compat com as arquiteturas do lab.py:
        #   dsa neutro (oraculo de servico NAO existe na arena — mesmo espirito
        #   do semgps); npc = densidade de taxi (congestao REAL, e o que MemCusto
        #   deve aprender a lembrar); gidx = indice do genoma no lote.
        s.dsa=torch.zeros(NC,5,n,device=DEV)
        s.gidx=torch.arange(B,device=DEV)
        s.UNS=torch.ones(B,GMAX,1,device=DEV)
    @property
    def npc(s): return s.dens[s.wid]*s.cfg.cong_taxi
    def capf(s): return 100+35*s.up[:,0]
    def txp(s): return 1./((1+.7*s.up[:,1])*(1+.5*s.up[:,7]))
    def txt(s): return 1./(1+.7*s.up[:,2])
    def txo(s): return 1./(1+.8*s.up[:,8])
    def vel(s): return 1./(1+.3*s.up[:,3])
    def tar(s): return 1.+.28*s.up[:,4]
    def A_(s): return s.Aa[s.cidx, s.no]
    def W_(s): return s.Wa[s.cidx, s.no]
    def grp_(s): return s.grpa[s.cidx, s.no]
    def tem_(s): return s.tema[s.cidx, s.no]
    def serv_(s): return s.serva[s.cidx, s.no]
    def serv_need(s):
        sv=s.serva[s.cidx, s.no]
        nec=torch.stack([1-s.fuel/s.capf(), s.fome/100., s.fad/100.,
                         torch.maximum(1-s.pneu/100., s.temp/120.),
                         (s.dinh/90.).clamp(max=1.)],-1)
        paga=(s.dinh[:,None] >= s.CUSTO[None,:]).float()
        return sv*nec*paga, sv*paga
    def obs(s):
        B,G,K=s.B,GMAX,s.K
        viz=s.A_(); val=viz>=0; vz=viz.clamp(min=0)
        ce=s.cidx[:,None].expand(-1,G)
        # passageiro mais proximo DENTRO DO RAIO (visao local; sem oraculo)
        dpo=s.DIa[s.cidx[:,None].expand(-1,NPX_A), s.no[:,None].expand(-1,NPX_A),
                  s.po[s.wid]]
        dpo=torch.where(dpo<=s.cfg.raio, dpo, torch.full_like(dpo,1e6))
        kb=dpo.argmin(1)
        po_alvo=s.po[s.wid].gather(1,kb[:,None]).squeeze(1)
        alvo=torch.where(s.pd_>=0, s.pd_, po_alvo)
        dal=s.DIa[ce, vz, alvo[:,None].expand(-1,G)]
        ve=(dpo.min(1).values<1e5)|(s.pd_>=0)
        dal=torch.where(ve[:,None], dal, torch.full_like(dal, 2*s.cfg.raio))
        cus=s.W_()
        # CONGESTAO REAL: densidade de OUTROS taxis no vizinho
        cong=torch.gather(s.dens[s.wid],1,vz)*s.cfg.cong_taxi
        gs=s.grp_(); fn=torch.gather(s.fase[s.wid],1,s.no[:,None]).expand(-1,G)
        vd=((gs.float()==fn)|(s.tem_()[:,None]==0)).float()*2-1
        # ds de servico: SEM oraculo — so ve servico no PROPRIO vizinho (0/1 -> dist 0 ou teto)
        sv_viz=s.serva[ce.reshape(-1), vz.reshape(-1)].reshape(B,G,5)
        ds=torch.where(sv_viz>0, torch.zeros_like(sv_viz), torch.full_like(sv_viz,12.))
        est=torch.stack([s.fuel/s.capf(), s.fome/100, s.fad/100, s.pneu/100,
                         s.temp/120, s.oleo/100, (s.dinh/120).clamp(max=1.),
                         (s.pd_>=0).float()],-1)
        F=torch.cat([(-dal/6.)[...,None],(-cus/4.)[...,None],(-cong/2.)[...,None],
                     vd[...,None],(-ds/6.),
                     est[:,None,:].expand(-1,G,-1), s.UNS],-1)
        return F, val

def passo_arena(m, esc):
    c=m.cfg; B=m.B; M=m.M; n=m.n; m.t+=1
    viva=m.viva>0
    m.tsem+=1; v=m.tsem>=c.per
    m.fase=torch.where(v,1-m.fase,m.fase); m.tsem=torch.where(v,torch.zeros_like(m.tsem),m.tsem)
    m.temp=(m.temp-1.6).clamp(min=25.)
    # densidade de taxi por no (para congestao do PROXIMO tick)
    m.dens.zero_()
    m.dens.scatter_add_(1, (m.wid*0+m.no).view(M,m.K),  # (M,K) nos por mundo
                        viva.view(M,m.K).float())
    # entrega
    ch=(m.pd_>=0)&(m.no==m.pd_)&(m.rest<=0)&viva
    d=m.DIa[m.cidx, m.po_.clamp(min=0), m.pd_.clamp(min=0)]
    br=(c.base+c.km*d)*m.tar(); im=br*c.imposto
    m.ent+=ch.float(); m.rec+=br*ch.float(); m.dinh+=(br-im)*ch.float()
    m.po_=torch.where(ch,torch.full_like(m.po_,-1),m.po_)
    m.pd_=torch.where(ch,torch.full_like(m.pd_,-1),m.pd_)
    livre=(m.tpar<=0)&viva; m.tpar=(m.tpar-1).clamp(min=0)
    an_=(m.rest>0)&livre; m.rest=torch.where(an_,m.rest-1,m.rest)
    cg=an_&(m.rest<=0)
    m.no=torch.where(cg,m.indo.clamp(min=0),m.no)
    m.indo=torch.where(cg,torch.full_like(m.indo,-1),m.indo)
    m.fome=(m.fome+c.fome*viva.float()).clamp(max=100)
    # FOME MATA: parado nao e gratis. 60 ticks com fome cravada = morte.
    # (a licao vida-ganha do Universe: vida dada faz a populacao rastejar)
    faminto=(m.fome>=99.5)&viva
    m.fome_t=torch.where(faminto, m.fome_t+1, torch.zeros_like(m.fome_t))
    morre_fome=(m.fome_t>=60.)&viva
    m.viva=torch.where(morre_fome, torch.zeros_like(m.viva), m.viva)
    m.morte_causa=torch.where(morre_fome, torch.full_like(m.morte_causa,2.), m.morte_causa)
    m.morte_t=torch.where(morre_fome, m.t.float().expand_as(m.morte_t), m.morte_t)
    ap=(m.fad>=95)&viva
    m.tpar=torch.where(ap,torch.full_like(m.tpar,12.),m.tpar)
    m.fad=torch.where(ap,torch.full_like(m.fad,40.),m.fad)
    pode=livre&(m.rest<=0)&(~ap)
    sv=m.serv_()
    # FILA REAL: capacidade 1 por servico/no/mundo. Quem quer servico disputa;
    # ordem aleatoria por tick (Gumbel) decide; perdedor NAO age neste tick.
    quer=(esc>=GMAX)&pode
    sidx=(esc-GMAX).clamp(min=0,max=4)
    chave=m.wid*(n*5)+m.no*5+sidx                       # vaga unica mundo/no/servico
    pri=torch.rand(B,generator=m.gsim,device=DEV)
    melhor=torch.full((M*n*5,),-1.,device=DEV)
    melhor.scatter_reduce_(0,chave,torch.where(quer,pri,torch.full_like(pri,-1.)),reduce='amax')
    ganhou=quer&(pri>=melhor.gather(0,chave)-1e-9)
    def faz(i,cu,ef):
        ok=ganhou&(sidx==i)&(sv[:,i]>0)&(m.dinh>=cu)
        m.dinh=m.dinh-cu*ok.float(); ef(ok); return ok
    o1=faz(0,2.,lambda ok: setattr(m,'fuel',torch.where(ok,m.capf(),m.fuel)))  # ENCHE (eco2)
    o2=faz(1,3.,lambda ok: setattr(m,'fome',torch.where(ok,(m.fome-45).clamp(min=0),m.fome)))
    o3=faz(2,0.,lambda ok: setattr(m,'fad',torch.where(ok,(m.fad-30).clamp(min=0),m.fad)))
    def chk(ok):
        m.pneu=torch.where(ok,torch.full_like(m.pneu,100.),m.pneu)
        m.oleo=torch.where(ok,torch.full_like(m.oleo,100.),m.oleo)
        m.temp=torch.where(ok,torch.full_like(m.temp,25.),m.temp)
    o4=faz(3,10.,chk)
    o5=ganhou&(sidx==4)&(sv[:,4]>0)&(m.dinh>=26.)
    m.dinh=m.dinh-26.*o5.float()
    k9=(m.up.sum(1)%9).long()
    m.up[m.ARB,k9]+=o5.float()
    serv_ok=o1|o2|o3|o4|o5
    # DISPUTA DE PASSAGEIRO: por no, um taxi leva (Gumbel de novo)
    po_w=m.po[m.wid]                                    # (B,NPX)
    hit=(po_w==m.no[:,None]); tem=hit.any(1); ks=hit.float().argmax(1)
    querp=pode&(~quer)&(m.pd_<0)&tem
    chp=m.wid*n+m.no
    mp=torch.full((M*n,),-1.,device=DEV)
    prp=torch.rand(B,generator=m.gsim,device=DEV)
    mp.scatter_reduce_(0,chp,torch.where(querp,prp,torch.full_like(prp,-1.)),reduce='amax')
    pega=querp&(prp>=mp.gather(0,chp)-1e-9)
    m.po_=torch.where(pega,m.no,m.po_)
    pd_novo=m.pd[m.wid].gather(1,ks[:,None]).squeeze(1)
    m.pd_=torch.where(pega,pd_novo,m.pd_)
    # respawn no MUNDO (mascarado, sem sync)
    marca=torch.zeros(M*NPX_A,device=DEV)
    marca.scatter_add_(0, m.wid*NPX_A+ks, pega.float())
    novo_po=torch.randint(0,n,(M,NPX_A),generator=m.gsim,device=DEV)
    novo_pd=torch.randint(0,n,(M,NPX_A),generator=m.gsim,device=DEV)
    mk=(marca.view(M,NPX_A)>0)
    m.po=torch.where(mk,novo_po,m.po); m.pd=torch.where(mk,novo_pd,m.pd)
    # mover
    mv=pode&(~quer)&(~pega)&(esc<GMAX)
    viz=m.A_(); sel=esc.clamp(max=GMAX-1)
    dst=torch.gather(viz,1,sel[:,None]).squeeze(1)
    valm=mv&(dst>=0)
    cu=torch.gather(m.W_(),1,sel[:,None]).squeeze(1)
    cu=cu+torch.gather(m.dens[m.wid],1,dst.clamp(min=0)[:,None]).squeeze(1)*c.cong_taxi
    sf=valm&(m.fuel<cu*c.fuel)
    m.avar+=sf.float(); m.av_fuel+=sf.float()
    m.tpar=torch.where(sf,torch.full_like(m.tpar,18.),m.tpar)
    m.fuel=torch.where(sf,torch.full_like(m.fuel,5.),m.fuel)
    # MORTE: pane sem dinheiro pro guincho
    morre=sf&(m.dinh<c.guincho)
    m.viva=torch.where(morre,torch.zeros_like(m.viva),m.viva)
    m.morte_causa=torch.where(morre,torch.full_like(m.morte_causa,1.),m.morte_causa)
    m.morte_t=torch.where(morre,m.t.float().expand_as(m.morte_t),m.morte_t)
    m.dinh=(m.dinh-c.guincho*sf.float()).clamp(min=0)
    rd=torch.rand(B,generator=m.gsim,device=DEV)
    fu=valm&(~sf)&(rd<((1-m.pneu/100)-.45).clamp(min=0)*c.risco*m.txp())
    m.avar+=fu.float(); m.tpar=torch.where(fu,torch.full_like(m.tpar,15.),m.tpar)
    m.pneu=torch.where(fu,torch.full_like(m.pneu,60.),m.pneu)
    ol=valm&(~sf)&(~fu)&(m.oleo<12)&(rd<.05)
    m.avar+=ol.float(); m.tpar=torch.where(ol,torch.full_like(m.tpar,22.),m.tpar)
    m.oleo=torch.where(ol,torch.full_like(m.oleo,45.),m.oleo)
    qt=valm&(~sf)&(~fu)&(~ol)&(m.temp>92)
    m.avar+=qt.float(); m.tpar=torch.where(qt,torch.full_like(m.tpar,14.),m.tpar)
    m.temp=torch.where(qt,torch.full_like(m.temp,40.),m.temp)
    gs=torch.gather(m.grp_(),1,sel[:,None]).squeeze(1).float()
    fn=torch.gather(m.fase[m.wid],1,m.no[:,None]).squeeze(1)
    vd=(gs==fn)|(m.tem_()==0)
    an=valm&(~sf)&(~fu)&(~ol)&(~qt)&vd
    m.indo=torch.where(an,dst,m.indo)
    m.rest=torch.where(an,(cu*m.vel()).round().clamp(min=1),m.rest)
    m.fuel=m.fuel-cu*c.fuel*an.float()
    m.fad=(m.fad+cu*c.fadiga*an.float()).clamp(max=100)
    m.pneu=(m.pneu-cu*c.pneu*m.txp()*an.float()).clamp(min=0)
    m.oleo=(m.oleo-cu*c.oleo*m.txo()*an.float()).clamp(min=0)
    m.temp=(m.temp+cu*c.temp*m.txt()*an.float()).clamp(max=120)
    return m

def rodar_arena(Arq, Wpop, grupos, cidades, cfg, T, seed):
    """grupos: (M,K) indices em Wpop — quem joga contra quem em cada mundo."""
    M,K=grupos.shape
    m=Mundo(cidades,M,cfg,seed=seed)
    Wb=Wpop[grupos.reshape(-1)]
    a=Arq(); a.reset(m,Wb)
    for t in range(T):
        F,val=m.obs(); viz=m.A_().clamp(min=0)
        sc=torch.einsum('bgf,bf->bg',F,Wb[:,:NF])+a.extra(m,Wb,viz)
        sc=sc.masked_fill(~val,-1e9)
        svn,sv=m.serv_need()
        ss=(svn*Wb[:,NF:NF+5]+Wb[:,NF+5:NF+6]).masked_fill(sv<=0,-1e9)
        tudo=torch.cat([sc,ss],1)
        esc=a.decidir(tudo,m) if hasattr(a,'decidir') else tudo.argmax(1)
        esc=torch.where(m.viva>0, esc, torch.zeros_like(esc))   # morto nao age
        passo_arena(m,esc)
        if hasattr(a,'atualizar'): a.atualizar(m)
    return m
