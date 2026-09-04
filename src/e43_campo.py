"""E43: baterias no CAMPO (mundo continuo). Bracos: linear, reflexo, minimo-3. Presets triagem/honesto. --L tamanho do mapa.
Saidas: /media/llm-data/universe-runs/neuromod-lab-taxi/e43/. So GPU (TORCHINDUCTOR_COMPILE_THREADS=1 no ambiente)."""
import sys, os, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from campo import *
PRESETS = {'triagem': dict(P=1024, G=40, T_evo=1200, T_aval=1200, R=8, seeds=(0, 1, 2)),
           'honesto': dict(P=1024, G=120, T_evo=1200, T_aval=1200, R=16, seeds=(0, 1, 2, 3, 4)),
           'fumaca': dict(P=512, G=25, T_evo=1200, T_aval=1200, R=4, seeds=(0,))}
BRACOS = [('linear', Linear), ('reflexo', Reflexo), ('minimo 3 (d_alvo, d_posto, e_fuel)', fabrica_minimo(['d_alvo', 'd_posto', 'e_fuel']))]

def main(a):
    p = dict(PRESETS[a.preset]); os.makedirs(a.out, exist_ok=True)
    if a.seeds: p['seeds'] = tuple(a.seeds)
    if a.R: p['R'] = a.R
    if a.G: p['G'] = a.G
    cfg = CfgCampo(L=a.L, pena_morte=a.pena, fitness=a.fitness)
    treino = [gerar_mapa(s, L=a.L) for s in range(4)]; teste = [gerar_mapa(a.teste_seed + s, L=a.L) for s in range(3)]
    res = dict(preset=a.preset, L=a.L, fitness=a.fitness, pena=a.pena, NF=NF, S=S, bracos={})
    print(f'== E43 campo | {a.preset} L={a.L} regua={a.fitness} P={p["P"]} G={p["G"]} R={p["R"]} x{len(p["seeds"])} | pena {a.pena} ==', flush=True)
    for nome, A in BRACOS:
        if a.so and nome not in a.so: continue
        t1 = time.time(); W0 = None
        if a.init_from:
            J = json.load(open(a.init_from[0]))['bracos'][a.init_from[1]]['W']; W0 = {sd: J[str(sd)] for sd in p['seeds']}
        champs = evoluir(A, treino, cfg, P=p['P'], ger=p['G'], T=p['T_evo'], seeds=p['seeds'], R=p['R'], verbose=False, W0=W0)
        med = {}; por = {}
        for sd in p['seeds']:
            por[sd] = medidas(A, champs[sd][0], teste, cfg, T=p['T_aval'], seed=7777, R=1, copias=128)
        for k in por[p['seeds'][0]]: med[k] = sum(por[sd][k] for sd in p['seeds'])/len(p['seeds'])
        med['fit_por_semente'] = [round(por[sd]['fit'], 3) for sd in p['seeds']]; med['mortos_por_semente'] = [round(por[sd]['mortos'], 3) for sd in p['seeds']]
        med['W'] = {sd: [round(float(x), 5) for x in champs[sd][0]] for sd in p['seeds']}; med['segundos'] = round(time.time() - t1)
        res['bracos'][nome] = med
        print(f'  {nome:<36} NP {A.NP:3d} fit {med["fit"]:6.2f} {med["fit_por_semente"]} ent {med["ent"]:5.1f} mortos {med["mortos"]:.2f} {med["mortos_por_semente"]} '
              f'panes {med["panes"]:4.1f} fome {med["fome_fim"]:3.0f} agua {med["agua_fim"]:3.0f} dinh {med["dinh"]:4.0f} res {med["res"]:4.0f} L/abast {med["litros_por_abast"]:4.0f} abast {med["n_posto"]:4.1f} ({med["segundos"]}s)', flush=True)
        tmp = os.path.join(a.out, f'e43{a.tag}.json.tmp')
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, os.path.join(a.out, f'e43{a.tag}.json'))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='triagem', choices=tuple(PRESETS)); ap.add_argument('--L', type=float, default=400.)
    ap.add_argument('--fitness', default='sobrevive', choices=('padrao', 'sobrevive', 'bemestar')); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e43'); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None); ap.add_argument('--G', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--tag', default=''); ap.add_argument('--init-from', nargs=2, default=None)
    main(ap.parse_args())
