"""E9b (doc 24): o sono que APRENDE — consolidacao circadiana da lei da agua.

    python src/e9_sono.py

Mundo: base + agua de radiador; a lei k_agua e SORTEADA POR MUNDO (evolucao
nao decora — so aprendizado em vida). Bracos (SerSono):
    fixo        alfa=0    — nao consolida nunca (so evolucao)      [controle]
    constante   alfa=.55  — consolida igual em qualquer hora       [controle]
    circadiano  alfa=1.0 dormindo 20h-00h | .5 pos-meia-noite | .2 de dia
Predicoes em PREDICOES.md ANTES de rodar. Metricas: fitness, curva de
entregas POR DIA (aprendizado em vida), corr(lei aprendida, k_agua verdadeiro),
histograma do sono por hora (rotina).
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, NF, gerar_cidade, Cfg, SerSono, evoluir_juntas, rodar, Lote, um_passo

DIA = 480

def cfg_agua():
    c = Cfg(1.0, mundo='base'); c.com_agua = True; c.dia = DIA
    return c

def bracos():
    return [type(f'S_{mo}', (SerSono,), {'submodo': mo, 'nome': f'sono:{mo}'})
            for mo in ('fixo','constante','circadiano')]

def portao(cids):
    print('--- portao E9b (3 bracos, genes zerados) ---')
    vals=[]
    for A in bracos():
        W = torch.zeros(16, A.NP, device=DEV)
        W[:,0]=4.0; W[:,NF:NF+5]=torch.tensor([20.,14.,10.,18.,3.],device=DEV); W[:,NF+5]=-4.0
        m = rodar(A, W, cids, cfg_agua(), T=1200, seed=1, R=2)
        vals.append(m.ent.mean().item()); print(f'  {A.nome:<16} {vals[-1]:6.2f}')
    ok = max(vals)-min(vals) < .05
    print(f"  {'PASSOU' if ok else 'FALHOU'} (spread {max(vals)-min(vals):.3f})")
    return ok

def main():
    treino=[gerar_cidade(s) for s in range(4)]
    teste =[gerar_cidade(1000+s) for s in range(3)]
    if not portao(treino[:2]): sys.exit('portao E9b falhou')
    ARQS9 = bracos()
    res={A.nome: dict(fit=[], ent_dia=[], corr_lei=[], sono=[]) for A in ARQS9}
    for sd in (0,1,2):
        t0=time.time()
        champs = evoluir_juntas(ARQS9, treino, cfg_agua(), P=1024, ger=60, T=1440,
                                seed=sd, R=4, verbose=(sd==0))
        for A in ARQS9:
            w = champs[A.nome][0]
            # avaliacao longa (6 dias) com telemetria detalhada
            cfg = cfg_agua()
            mL = Lote(teste, 96, cfg, seed=7777, R=1)
            Wb = w[None,:].repeat(mL.B,1); ai = A(); ai.reset(mL, Wb)
            marcos=[]
            for t in range(6*DIA):
                um_passo(mL, ai, Wb); ai.atualizar(mL)
                if (t+1) % DIA == 0: marcos.append(mL.ent.clone())
            fit=float((mL.ent-0.3*mL.avar).mean())
            por_dia=[round(float(marcos[0].mean()),2)] + \
                    [round(float((marcos[i]-marcos[i-1]).mean()),2) for i in range(1,6)]
            # a lei aprendida bate com a verdade oculta do mundo?
            lei2 = ai.lei[:,2]; verdade = cfg.temp * mL.k_agua
            vx = lei2 - lei2.mean(); vy = verdade - verdade.mean()
            corr = float((vx*vy).sum()/(vx.norm()*vy.norm()+1e-9))
            sono = ai.sono_hora.sum(0); sono = (sono/sono.sum().clamp(min=1)).cpu()
            res[A.nome]['fit'].append(round(fit,2))
            res[A.nome]['ent_dia'].append(por_dia)
            res[A.nome]['corr_lei'].append(round(corr,3))
            res[A.nome]['sono'].append([round(float(x),3) for x in sono])
        print(f'semente {sd} ({time.time()-t0:.0f}s): ' + ' | '.join(
            f"{k.split(':')[1]} fit {v['fit'][-1]} corr {v['corr_lei'][-1]}"
            for k,v in res.items()), flush=True)
    print('\n=== E9b — o sono que aprende ===')
    for k,v in sorted(res.items(), key=lambda x:-sum(x[1]['fit'])/3):
        print(f"  {k:<18} fit {sum(v['fit'])/3:6.2f} {v['fit']}")
        print(f"      entregas por dia (aprendizado em vida): {v['ent_dia']}")
        print(f"      corr(lei aprendida, k_agua oculto): {v['corr_lei']}")
    json.dump(res, open('/media/llm-data/universe-runs/neuromod-lab-taxi/e9_sono.json','w'))
    print('salvo: /media/llm-data/universe-runs/neuromod-lab-taxi/e9_sono.json')

if __name__=='__main__':
    main()
