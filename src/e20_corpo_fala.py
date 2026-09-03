"""E20: o corpo fala — gargalo de K hormonios entre corpo e cerebro (doc 36).
    python src/e20_corpo_fala.py --preset triagem|honesto [--so ...] [--pena 5]
Mundo: pacote final do E19 (economia gordura->vida, fome .15, refeicao 90, comida no posto)."""
import sys, os, time, argparse, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, NF, gerar_cidade, Reativo, evoluir_sementes, rodar, modo_execucao
from corpo_fala import fabrica
import e15_economia as E15
from e19_pacote import cfg_pacote, PRESET, PRESET_TRIAGEM, telemetria

OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e20'
MUNDO = dict(fome=.15, refeicao=90., comida_no_posto=True)
BRACOS = [('direto (Reativo)',   Reativo),
          ('corpo fala K=2',     fabrica(2)),
          ('corpo fala K=1',     fabrica(1)),
          ('corpo fala K=4',     fabrica(4)),
          ('redundante K=2',     fabrica(2, redundante=True)),
          # triagem 2: codigo herdado
          ('K=2 corpo nasce falando',        fabrica(2, prior_corpo=True)),
          ('K=2 corpo fala + cerebro ouve',  fabrica(2, prior_corpo=True, prior_cerebro=True)),
          ('K=2 so cerebro ouve',            fabrica(2, prior_cerebro=True))]

import copy
def curriculo_fome(cfg, alvo, frac=.6, inicio=.03):
    """infancia protegida: fome fere `inicio` na geracao 0 e sobe linearmente ate `alvo` em frac*ger."""
    def cfg_gen(it, ger):
        c = copy.copy(cfg); t = min(1., it/max(1., frac*ger))
        c.fome_mata = inicio + (alvo - inicio)*t
        return c
    return cfg_gen

def main(a):
    E15.PENA = a.pena
    p = dict(PRESET_TRIAGEM if a.preset == 'triagem' else PRESET)
    if a.seeds: p['seeds'] = tuple(a.seeds)
    if a.R: p['R'] = a.R
    treino = [gerar_cidade(s) for s in range(4)]; teste = [gerar_cidade(a.teste_seed + s) for s in range(3)]
    res = dict(preset=p, modo=modo_execucao(), NF=NF, pena=a.pena, mundo=MUNDO, bracos={})
    os.makedirs(a.out, exist_ok=True); t0 = time.time()
    print(f'== E20 corpo fala | {a.preset} P={p["P"]} G={p["G"]} R={p["R"]} x{len(p["seeds"])} | pena {a.pena} ==', flush=True)
    for nome, A in BRACOS:
        if a.so and nome not in a.so: continue
        t1 = time.time(); cfg = cfg_pacote(**MUNDO)
        cg = curriculo_fome(cfg, MUNDO['fome']) if a.curriculo else None
        champs = evoluir_sementes(A, treino, cfg, P=p['P'], ger=p['G'], T=p['T_evo'], seeds=p['seeds'], R=p['R'], verbose=False, cfg_gen=cg)
        por = []; hm = []
        for sd in p['seeds']:
            m = rodar(A, champs[sd][0][None, :].repeat(128, 1), teste, cfg, T=p['T_aval'], seed=7777)
            por.append(telemetria(m, p['T_aval']))
        med = {k: round(sum(d[k] for d in por)/len(por), 3) for k in por[0]}
        med['fit_por_semente'] = [d['fit'] for d in por]; med['mortos_por_semente'] = [d['mortos'] for d in por]
        med['W'] = {sd: [round(float(x), 5) for x in champs[sd][0]] for sd in p['seeds']}
        med['segundos'] = round(time.time() - t1); res['bracos'][nome] = med
        print(f'  {nome:<20} NP {A.NP:3d} fit {med["fit"]:6.2f} {med["fit_por_semente"]} ent {med["ent"]:5.1f} mortos {med["mortos"]:.2f} {med["mortos_por_semente"]} '
              f'fome_fim {med["fome_fim"]:4.0f} panes {med["av_fuel"]:4.1f} posto {med["n_posto"]:4.1f} ({med["segundos"]}s)', flush=True)
        tmp = os.path.join(a.out, f'e20{a.tag}.json.tmp')
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, os.path.join(a.out, f'e20{a.tag}.json'))
    print(f'TOTAL {time.time()-t0:.0f}s')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='triagem', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default=OUT); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default='')
    ap.add_argument('--curriculo', action='store_true', help='infancia protegida: fome_mata sobe de .03 ate o alvo em 60%% das geracoes')
    main(ap.parse_args())
