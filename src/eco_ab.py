"""A/B do ECO-FUEL V2 (predicoes em PREDICOES.md). Evolucao SEPARADA por braco
(a politica otima muda com a economia — evoluir junto seria sabotar um lado)."""
import sys, json, torch; sys.path.insert(0,'src')
from lab import gerar_cidade, Cfg, evoluir, rodar, ARQS, DEV
POR={A.nome:A for A in ARQS}
treino=[gerar_cidade(s) for s in range(8)]; teste=[gerar_cidade(1000+s) for s in range(6)]
print(f"{'braço':<10}{'arq':<12}{'sem.':>5}{'entregas':>9}{'pane':>6}{'parado?':>9}")
res={}
for eco in (False,True):
    for nome in ('reativo','banco EMA','hibrido'):
        for sd in (0,1,2):
            cfg=Cfg(1.0); cfg.eco2=eco
            w,h,_=evoluir(POR[nome],treino,cfg,2048,60,600,seed=sd,R=8,verbose=False)
            m=rodar(POR[nome],w[None,:].repeat(512,1),teste,cfg,1500,seed=7777,R=1)
            e=float(m.ent.mean()); pf=float(m.av_fuel.mean())
            res[f"{eco}|{nome}|{sd}"]=dict(ent=e,pane=pf)
            print(f"{'eco2' if eco else 'atual':<10}{nome:<12}{sd:>5}{e:>9.2f}{pf:>6.1f}")
json.dump(res,open('resultados/eco_ab.json','w'))
