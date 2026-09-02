"""Avaliacao pos-evolucao da arena.
A) SELF-PLAY: 6 clones do mesmo genoma, cidades held-out -> metrica comparavel.
B) TORNEIO MISTO: 2 assentos por arquitetura NO MESMO mundo -> quem vence a
   disputa de verdade (frequencia-dependente, e o que o Leonardo pediu pra ver).
"""
import sys, os, json, torch
sys.path.insert(0, os.path.dirname(__file__))
from lab import gerar_cidade, DEV
from arena import CfgArena, Mundo, rodar_arena, passo_arena, ARQS_A as ARQS, NF, POR_A as POR

class Mista:
    """roda varias arquiteturas no MESMO mundo: extra() de cada uma calculada,
    linha b usa a do assento dele. Estados de memoria de todas vivem juntos."""
    def __init__(s, classes, assento):     # assento: (B,) idx em classes
        s.insts=[C() for C in classes]; s.assento=assento
    def reset(s,m,W):
        for a in s.insts: a.reset(m,W)
    def extra(s,m,W,viz):
        outs=[a.extra(m,W,viz) for a in s.insts]
        E=torch.zeros_like(outs[0]) if torch.is_tensor(outs[0]) else None
        for k,o in enumerate(outs):
            ok=(s.assento==k)[:,None]
            if torch.is_tensor(o): E=torch.where(ok,o,E if E is not None else o*0)
        return E if E is not None else 0.
    def atualizar(s,m):
        for a in s.insts:
            if hasattr(a,'atualizar'): a.atualizar(m)

def carrega():
    G={}
    for f in os.listdir('resultados'):
        if f.startswith('arena-') and f.endswith('.json'):
            d=json.load(open('resultados/'+f))
            G[(d['arq'],d['seed'])]=torch.tensor(d['pesos'],device=DEV)
    return G

def selfplay(G, M=256, T=1500):
    cids=[gerar_cidade(1000+s,n=120) for s in range(4)]
    cfg=CfgArena(n_cid=120,K=6)
    print(f"A) SELF-PLAY   {'arq':<12}{'sem':>4}{'entregas':>9}{'mortes%':>8}{'pane':>6}")
    res={}
    for (arq,sd),w in sorted(G.items()):
        W=w[None,:].repeat(M*6,1)
        m=rodar_arena(POR[arq],W,torch.arange(M*6,device=DEV).view(M,6),cids,cfg,T,seed=99)
        e=float(m.ent.mean()); mo=float((m.viva<1).float().mean())*100
        res[f"{arq}|{sd}"]=dict(ent=round(e,3),mortes=round(mo,1),
                                pane=round(float(m.av_fuel.mean()),2))
        print(f"   {'':<11}{arq:<12}{sd:>4}{e:>9.2f}{mo:>8.1f}{res[f'{arq}|{sd}']['pane']:>6}")
    return res

def torneio(G, M=256, T=1500):
    cids=[gerar_cidade(1000+s,n=120) for s in range(4)]
    cfg=CfgArena(n_cid=120,K=6)
    nomes=['reativo','banco EMA','mem custo']
    print(f"\nB) TORNEIO MISTO (2 assentos cada, mesmo mundo, {M} mundos x 3 sementes)")
    tot={n:[] for n in nomes}; mor={n:[] for n in nomes}
    for sd in (0,1,2):
        Wl=[]; classes=[POR[n] for n in nomes]
        for n in nomes: Wl.append(G[(n,sd)])
        # assentos: [0,0,1,1,2,2] embaralhados por mundo p/ tirar vicio de posicao
        base=torch.tensor([0,0,1,1,2,2],device=DEV)
        g=torch.Generator(device=DEV); g.manual_seed(sd)
        perm=torch.stack([base[torch.randperm(6,generator=g,device=DEV)] for _ in range(M)])
        assento=perm.reshape(-1)                     # (M*6,)
        Wpop=torch.stack(Wl)                         # (3,36)
        Wb=Wpop[assento]
        mista=Mista(classes,assento)
        m=Mundo(cids,M,cfg,seed=777+sd)
        mista.reset(m,Wb)
        for t in range(T):
            F,val=m.obs(); viz=m.A_().clamp(min=0)
            sc=torch.einsum('bgf,bf->bg',F,Wb[:,:NF])+mista.extra(m,Wb,viz)
            sc=sc.masked_fill(~val,-1e9)
            svn,sv=m.serv_need()
            ss=(svn*Wb[:,NF:NF+5]+Wb[:,NF+5:NF+6]).masked_fill(sv<=0,-1e9)
            esc=torch.cat([sc,ss],1).argmax(1)
            esc=torch.where(m.viva>0,esc,torch.zeros_like(esc))
            passo_arena(m,esc)
            mista.atualizar(m)
        for k,n in enumerate(nomes):
            sel=assento==k
            tot[n].append(float(m.ent[sel].mean()))
            mor[n].append(float((m.viva[sel]<1).float().mean())*100)
    print(f"   {'arq':<12}{'entregas por semente':<28}{'mortes%':>22}")
    res={}
    for n in nomes:
        res[n]=dict(ent=[round(x,2) for x in tot[n]], mortes=[round(x,1) for x in mor[n]])
        print(f"   {n:<12}{str(res[n]['ent']):<28}{str(res[n]['mortes']):>22}")
    return res

if __name__=='__main__':
    G=carrega()
    a=selfplay(G); b=torneio(G)
    json.dump(dict(selfplay=a,torneio=b),open('resultados/arena_aval.json','w'))
    print('\n-> resultados/arena_aval.json')
