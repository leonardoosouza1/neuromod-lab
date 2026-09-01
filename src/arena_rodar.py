"""CLI da arena: portao (simetria + porte), smoke, evolucao por torneio."""
import sys, os, json, time, argparse, torch
sys.path.insert(0, os.path.dirname(__file__))
from lab import gerar_cidade, ARQS, NF, DEV
from rodar import perito_W
from arena import CfgArena, rodar_arena

def portao(n_cid=120, K=6, M=48, T=800):
    """1) PORTE: politica identica nas 7 arqs -> resultado IDENTICO.
       2) SIMETRIA: K peritos iguais no mesmo mundo -> media por assento ~igual
          (se o assento 0 ganhar sempre, a ordem de resolucao esta viciada)."""
    print('--- portao da ARENA ---')
    cids=[gerar_cidade(s,n=n_cid) for s in range(3)]
    cfg=CfgArena(n_cid=n_cid,K=K)
    vals=[]
    for Arq in ARQS:
        W=perito_W(36)[None,:].repeat(M*K,1)
        grupos=torch.arange(M*K,device=DEV).view(M,K)
        m=rodar_arena(Arq,W,grupos,cids,cfg,T,seed=5)
        e=float(m.ent.mean()); vals.append(e)
        assento=m.ent.view(M,K).mean(0)
        mortos=float((m.viva<1).float().mean())
        print(f"  {Arq.nome:<14} entregas/ser {e:5.2f}  mortes {mortos*100:4.1f}%  "
              f"assentos {[round(float(x),2) for x in assento]}")
    sp=max(vals)-min(vals)
    print(f"  spread entre arqs: {sp:.4f} ' + ('PASSOU' if sp<.05 else 'FALHOU'))" if False else
          f"  spread entre arqs: {sp:.4f}  {'PASSOU' if sp<1e-3 else 'FALHOU: bug de porte'}")
    return sp<1e-3

def evoluir_arena(Arq, cids, cfg, P=512, ger=30, T=800, seed=0, M=None, elite=.15):
    """torneio: cada geracao sorteia grupos de K; fitness = desempenho no mundo
    COMPARTILHADO, medias sobre os mundos que o genoma jogou."""
    g=torch.Generator(device=DEV); g.manual_seed(seed)
    K=cfg.K; M=M or (P//K)*2                       # cada genoma joga ~2 mundos/ger
    W=torch.randn(P,36,generator=g,device=DEV)*.8
    hist=[]
    for it in range(ger):
        perm=torch.cat([torch.randperm(P,generator=g,device=DEV) for _ in range(M*K//P+1)])[:M*K]
        grupos=perm.view(M,K)
        m=rodar_arena(Arq,W,grupos,cids,cfg,T,seed=seed+it*13)
        fit_b=m.ent-.3*m.avar+ .001*torch.where(m.morte_t<0, float(T), m.morte_t)  # sobreviver vale
        f=torch.zeros(P,device=DEV); cnt=torch.zeros(P,device=DEV)
        f.scatter_add_(0,perm,fit_b); cnt.scatter_add_(0,perm,torch.ones_like(fit_b))
        f=f/cnt.clamp(min=1)
        o=f.argsort(descending=True); W=W[o]; f=f[o]
        hist.append(float(f[:max(2,int(P*.15))].mean()))
        ne=max(2,int(P*elite))
        idx=torch.randint(0,ne,(P-ne,),generator=g,device=DEV)
        fil=(W[idx]+torch.randn(P-ne,36,generator=g,device=DEV)*.3).clamp(-5,5)
        W=torch.cat([W[:ne],fil])
        if it%5==0:
            print(f'  ger {it:>3}  elite {hist[-1]:6.2f}  div {float(W.std(0).mean()):.3f}',flush=True)
    return W[0], hist

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--portao',action='store_true')
    ap.add_argument('--smoke',action='store_true')
    ap.add_argument('--evolui',action='store_true')
    ap.add_argument('--arq',default='reativo')
    ap.add_argument('-P',type=int,default=512); ap.add_argument('-G',type=int,default=30)
    ap.add_argument('-n',type=int,default=120); ap.add_argument('-K',type=int,default=6)
    ap.add_argument('--seed',type=int,default=0)
    a=ap.parse_args()
    if a.portao: portao(n_cid=a.n,K=a.K)
    if a.smoke:
        cids=[gerar_cidade(0,n=a.n)]
        cfg=CfgArena(n_cid=a.n,K=a.K)
        POR={A.nome:A for A in ARQS}
        W=torch.randn(24,36,device=DEV)*.5
        m=rodar_arena(POR['reativo'],W,torch.arange(24,device=DEV).view(4,6),cids,cfg,300,seed=1)
        print(f'smoke ok: entregas {float(m.ent.mean()):.2f} mortes {float((m.viva<1).sum()):.0f}/24')
    if a.evolui:
        POR={A.nome:A for A in ARQS}
        cids=[gerar_cidade(s,n=a.n) for s in range(4)]
        cfg=CfgArena(n_cid=a.n,K=a.K)
        t0=time.time()
        w,h=evoluir_arena(POR[a.arq],cids,cfg,P=a.P,ger=a.G,seed=a.seed)
        json.dump(dict(arq=a.arq,n=a.n,K=a.K,P=a.P,G=a.G,seed=a.seed,hist=h,
                       pesos=[round(float(x),4) for x in w]),
                  open(f'resultados/arena-{a.arq}-s{a.seed}.json','w'))
        print(f'{time.time()-t0:.0f}s -> resultados/arena-{a.arq}-s{a.seed}.json')
