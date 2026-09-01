"""Grava UM mundo da arena tick a tick: 6 taxis (2 por arquitetura) disputando.
E o desenho que o Leonardo pediu: a briga, quem corta caminho, quem espera,
quem morre. Usa o torneio misto do arena_aval."""
import json, sys, os, torch
sys.path.insert(0,'src')
from lab import gerar_cidade, ARQS, NF, DEV
from arena import CfgArena, Mundo, passo_arena
from arena_aval import Mista, carrega, POR

def grava(T=1500, seed=31):
    G=carrega()
    nomes=['reativo','banco EMA','mem custo']
    cid=gerar_cidade(1000,n=120)
    cfg=CfgArena(n_cid=120,K=6)
    assento=torch.tensor([0,1,2,0,1,2],device=DEV)     # intercalado
    Wb=torch.stack([G[(nomes[int(k)],0)] for k in assento])
    mista=Mista([POR[n] for n in nomes],assento)
    m=Mundo([cid],1,cfg,seed=seed)
    mista.reset(m,Wb)
    fr=[]
    for t in range(T):
        F,val=m.obs(); viz=m.A_().clamp(min=0)
        sc=torch.einsum('bgf,bf->bg',F,Wb[:,:NF])+mista.extra(m,Wb,viz)
        sc=sc.masked_fill(~val,-1e9)
        svn,sv=m.serv_need()
        ss=(svn*Wb[:,NF:NF+5]+Wb[:,NF+5:NF+6]).masked_fill(sv<=0,-1e9)
        esc=torch.cat([sc,ss],1).argmax(1)
        esc=torch.where(m.viva>0,esc,torch.zeros_like(esc))
        passo_arena(m,esc); mista.atualizar(m)
        fr.append(dict(t=t,
            no=[int(x) for x in m.no], viva=[int(x) for x in m.viva],
            rest=[round(float(x),0) for x in m.rest],
            par=[round(float(x),0) for x in m.tpar],
            pd_=[int(x) for x in m.pd_], ent=[int(x) for x in m.ent],
            fuel=[round(float(x),0) for x in m.fuel],
            fome=[round(float(x),0) for x in m.fome],
            dinh=[round(float(x),0) for x in m.dinh],
            po=[int(x) for x in m.po[0]],
            dens=[round(float(x),0) for x in m.dens[0].topk(5).values]))
    out=dict(nomes=nomes, assento=[int(x) for x in assento], T=T,
             cidade=dict(pos=[[round(float(x),2) for x in p] for p in cid['pos']],
                         A=cid['A'].tolist(), serv=cid['serv'].tolist()),
             frames=fr,
             final=dict(ent=[int(x) for x in m.ent], viva=[int(x) for x in m.viva],
                        morte_t=[int(x) for x in m.morte_t]))
    json.dump(out,open('resultados/replay_arena.json','w'))
    print('entregas finais por assento:',out['final']['ent'],
          '| vivos:',out['final']['viva'])
    print('->',os.path.getsize('resultados/replay_arena.json')//1024,'KB')

if __name__=='__main__': grava()
