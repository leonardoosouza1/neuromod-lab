"""E6 (doc 20): o TALAMO dentro do ser paga? Roteamento por passo vs poda estatica.

    python src/e6_talamo.py

Bracos (todos NP=54, I8):
    sempre       todos os orgaos consultados todo passo (paga 5k/passo)  [teto de info]
    talamo       gate contextual sig(a + b*need + c*carregando) por orgao
    cego         gate so com bias (QUANTO consultar, nunca QUANDO)       [controle]
    poda_curta   E8 campeao: infancia 5% + poda estatica                 [estatico]
Predicoes em PREDICOES.md ANTES de rodar. Mundo: ruas (orgao util conhecido).
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, NF, gerar_cidade, Cfg, SerVital, SerTalamo, evoluir_juntas, rodar, Lote, um_passo

def bracos():
    B = [type('T_sempre', (SerTalamo,), {'submodo':'sempre', 'nome':'talamo:sempre'}),
         type('T_talamo', (SerTalamo,), {'submodo':'talamo', 'nome':'talamo:contextual'}),
         type('T_cego',   (SerTalamo,), {'submodo':'cego',   'nome':'talamo:cego'}),
         type('V_curta',  (SerVital,),  {'modo':'curta', 'NP':54, 'nome':'poda:curta'})]
    return B

def portao(cids, cfg):
    print('--- portao E6 (4 bracos, genes zerados) ---')
    vals=[]
    for A in bracos():
        W = torch.zeros(16, A.NP, device=DEV)
        W[:,0]=4.0; W[:,NF:NF+5]=torch.tensor([20.,14.,10.,18.,3.],device=DEV); W[:,NF+5]=-4.0
        W[:,NF+12]=-20.; W[:,NF+13]=-20.
        m = rodar(A, W, cids, cfg, T=1200, seed=1, R=2)
        vals.append(m.ent.mean().item()); print(f'  {A.nome:<18} {vals[-1]:6.2f}')
    ok = max(vals)-min(vals) < .05
    print(f"  {'PASSOU' if ok else 'FALHOU'} (spread {max(vals)-min(vals):.3f})")
    return ok

def main():
    treino=[gerar_cidade(s) for s in range(4)]
    teste =[gerar_cidade(1000+s) for s in range(3)]
    cfg=Cfg(1.0, mundo='ruas'); cfg.cron_alto=3.5
    if not portao(treino[:2], cfg): sys.exit('portao E6 falhou')
    ARQS_E6 = bracos()
    res={A.nome: dict(fit=[], ent=[], duty=[], delta_carr=[]) for A in ARQS_E6}
    for sd in (0,1,2):
        t0=time.time()
        champs = evoluir_juntas(ARQS_E6, treino, cfg, P=2048, ger=60, T=600,
                                seed=sd, R=4, verbose=(sd==0))
        for A in ARQS_E6:
            w = champs[A.nome][0]
            m = rodar(A, w[None,:].repeat(256,1), teste, cfg, T=1500, seed=7777)
            fit=(m.ent-0.3*m.avar-getattr(m,'custo_neural',0.)).mean()
            res[A.nome]['fit'].append(round(float(fit),2))
            res[A.nome]['ent'].append(round(float(m.ent.mean()),2))
            if issubclass(A, SerTalamo):
                mL=Lote(teste[:1],64,cfg,seed=4242,R=1)
                Wb=w[None,:].repeat(mL.B,1); ai=A(); ai.reset(mL,Wb)
                for _ in range(1500): um_passo(mL, ai, Wb); ai.atualizar(mL)
                duty=(ai.duty_soma/ai.passos_n).mean(0)
                r_carr=(ai.duty_carr.sum(0)/ai.carr_soma.sum().clamp(min=1))
                res[A.nome]['duty'].append([round(float(x),2) for x in duty])
                res[A.nome]['delta_carr'].append(
                    [round(float(a-b),3) for a,b in zip(r_carr, duty)])
        print(f'semente {sd} ({time.time()-t0:.0f}s): ' +
              ' | '.join(f"{k.split(':')[1]} {v['fit'][-1]}" for k,v in res.items()), flush=True)
    print('\n=== E6 — fitness (entregas − avarias − custo por consulta) ===')
    for k,v in sorted(res.items(), key=lambda x:-sum(x[1]['fit'])/3):
        print(f"  {k:<20} media {sum(v['fit'])/3:6.2f}  {v['fit']}  entregas {v['ent']}")
        if v['duty']:
            print(f"      duty por orgao [memC,mapa,jan,corpo,rota]: {v['duty']}")
            print(f"      Δconsulta carregando (rota deve ser >0): {v['delta_carr']}")
    json.dump(res, open('/media/llm-data/universe-runs/neuromod-lab-taxi/e6_talamo.json','w'))
    print('salvo: /media/llm-data/universe-runs/neuromod-lab-taxi/e6_talamo.json')

if __name__=='__main__':
    main()
