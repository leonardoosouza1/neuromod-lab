"""E4 (doc 19 §4): calculo-como-orgao paga onde peso puro nao alcanca?

    python src/e4_rota.py            # escala media, 3 sementes (~15 min)
    python src/e4_rota.py --forte    # escala de bateria (1 semente)

Mundo `ruas` (congestao cronica invisivel). Controle ja medido (PREDICOES):
memoria sem calculo = teto 0. Braços:
    reativo          sem memoria, sem calculo        (piso)
    mem custo        memoria SEM calculo             (controle, ~= reativo)
    rota calculada   memoria + Floyd-Warshall lembrado (a tese)
Predicao registrada em PREDICOES.md ANTES desta rodada.
"""
import sys, os, json, argparse, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import (DEV, gerar_cidade, Cfg, Reativo, MemCusto, RotaCalculada,
                 evoluir_juntas, rodar)
from rodar import perito_W

BRACOS = [Reativo, MemCusto, RotaCalculada]


def portao(cids, cfg):
    print('--- portao E4 (3 bracos, politica identica) ---')
    vals = []
    for A in BRACOS:
        W = perito_W(A.NP)[None,:].repeat(16,1)
        m = rodar(A, W, cids, cfg, T=1200, seed=1, R=2)
        vals.append(m.ent.mean().item())
        print(f'  {A.nome:<15} {vals[-1]:6.2f}')
    ok = max(vals)-min(vals) < 0.05
    print(f"  {'PASSOU' if ok else 'FALHOU'} (spread {max(vals)-min(vals):.3f})")
    return ok


def main(P, G, R, tevo, taval, sementes, n=26):
    treino = [gerar_cidade(s, n=n) for s in range(4)]
    teste  = [gerar_cidade(1000+s, n=n) for s in range(3)]
    cfg = Cfg(1.0, mundo='ruas'); cfg.cron_alto = 3.5
    if not portao(treino[:2], cfg):
        sys.exit('portao falhou')
    res = {A.nome: [] for A in BRACOS}
    pesos_orgao = []
    for sd in sementes:
        t0 = time.time()
        champs = evoluir_juntas(BRACOS, treino, cfg, P=P, ger=G, T=tevo,
                                seed=sd, R=R, verbose=(sd==sementes[0]))
        for A in BRACOS:
            w = champs[A.nome][0]
            m = rodar(A, w[None,:].repeat(256,1), teste, cfg, T=taval, seed=7777)
            res[A.nome].append(round(float(m.ent.mean()), 2))
        from lab import NF
        wrc = champs['rota calculada'][0]
        pesos_orgao.append(dict(leitura_mem=round(float(wrc[NF+7]),3),
                                confianca_orgao=round(float(wrc[NF+8]),3)))
        print(f'semente {sd} ({time.time()-t0:.0f}s): ' +
              ' | '.join(f'{k} {v[-1]}' for k, v in res.items()) +
              f' | orgao w={pesos_orgao[-1]["confianca_orgao"]}', flush=True)
    print('\n=== E4 — resultado ===')
    for k, v in res.items():
        med = sum(v)/len(v); amp = max(v)-min(v)
        print(f'  {k:<15} media {med:6.2f}  amp {amp:.2f}  {v}')
    print(f'  pesos do orgao por semente: {pesos_orgao}')
    saida = '/media/llm-data/universe-runs/neuromod-lab-taxi/e4_rota.json'
    json.dump(dict(res=res, pesos_orgao=pesos_orgao,
                   config=dict(P=P, G=G, R=R, tevo=tevo, taval=taval,
                               sementes=list(sementes), n=n, cron_alto=3.5)),
              open(saida, 'w'))
    print('salvo:', saida)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--forte', action='store_true')
    a = ap.parse_args()
    if a.forte:
        main(P=8192, G=100, R=8, tevo=600, taval=1500, sementes=[0])
    else:
        main(P=2048, G=60, R=4, tevo=400, taval=1200, sementes=[0,1,2])
