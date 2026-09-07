"""E43: baterias no CAMPO (mundo continuo). Bracos: linear, reflexo, minimo-3. Presets triagem/honesto. --L tamanho do mapa.
Saidas: /media/llm-data/universe-runs/neuromod-lab-taxi/e43/. So GPU (TORCHINDUCTOR_COMPILE_THREADS=1 no ambiente)."""
import sys, os, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from campo import *
from completo import SerCompleto, SemTalamo, SemCortex, SemHipocampo, SemReflexo, SemLivre, SoCamadas
PRESETS = {'triagem': dict(P=1024, G=40, T_evo=1200, T_aval=1200, R=8, seeds=(0, 1, 2)),
           'honesto': dict(P=1024, G=120, T_evo=1200, T_aval=1200, R=16, seeds=(0, 1, 2, 3, 4)),
           'fumaca': dict(P=512, G=25, T_evo=1200, T_aval=1200, R=4, seeds=(0,))}
BRACOS = [('linear', Linear), ('reflexo', Reflexo), ('produto (need x dist, portao)', Produto), ('modos gaussianos K=3', Modos), ('produto trend (olho multi-escala)', ProdutoTrend), ('reflexo 2 raizes (histerese)', ReflexoRaizes), ('reflexo alcance (km ate esvaziar)', ReflexoAlcance), ('cerebro livre (rapida+lenta, sem pista)', Cerebro), ('COMPLETO (talamo+cortex+hipocampo+reflexo+livre)', SerCompleto), ('completo sem talamo', SemTalamo), ('completo sem cortex', SemCortex), ('completo sem hipocampo', SemHipocampo), ('completo sem reflexo', SemReflexo), ('completo sem livre (so camadas)', SoCamadas), ('minimo 3 (d_alvo, d_posto, e_fuel)', fabrica_minimo(['d_alvo', 'd_posto', 'e_fuel'])), ('minimo 4 (+autonomia)', fabrica_minimo(['d_alvo', 'd_posto', 'e_fuel', 'e_autonomia']))]

def main(a):
    p = dict(PRESETS[a.preset]); os.makedirs(a.out, exist_ok=True)
    p['T_evo'] = p['T_aval'] = int(240*a.dias)          # vida em dias (5 dias = viver de poupanca e otimo; 10 obriga a trabalhar)
    if a.seeds: p['seeds'] = tuple(a.seeds)
    if a.R: p['R'] = a.R
    if a.G: p['G'] = a.G
    cfg = CfgCampo(L=a.L, pena_morte=a.pena, fitness=a.fitness, loja_no_posto=not a.sem_loja); cfg.custo_gene = a.custo_gene; cfg.KCAL_PANE = a.kcal_pane
    treino = [gerar_mapa(s, L=a.L, distinto=a.mundo == 'distinto') for s in range(4)]; teste = [gerar_mapa(a.teste_seed + s, L=a.L, distinto=a.mundo == 'distinto') for s in range(3)]
    res = dict(preset=a.preset, L=a.L, fitness=a.fitness, pena=a.pena, NF=NF, S=S, bracos={})
    print(f'== E43 campo | {a.preset} L={a.L} dias={a.dias} regua={a.fitness} P={p["P"]} G={p["G"]} R={p["R"]} x{len(p["seeds"])} | pena {a.pena} ==', flush=True)
    for nome, A in BRACOS:
        if a.so and nome not in a.so: continue
        t1 = time.time(); W0 = None
        if a.init_from:
            J = json.load(open(a.init_from[0]))['bracos'][a.init_from[1]]['W']; W0 = {sd: J[str(sd)] for sd in p['seeds']}
        champs = evoluir(A, treino, cfg, P=p['P'], ger=p['G'], T=p['T_evo'], seeds=p['seeds'], R=p['R'], verbose=True, W0=W0)
        med = {}; por = {}
        for sd in p['seeds']:
            por[sd] = medidas(A, champs[sd][0], teste, cfg, T=p['T_aval'], seed=7777, R=1, copias=128)
        for k in por[p['seeds'][0]]: med[k] = sum(por[sd][k] for sd in p['seeds'])/len(p['seeds'])
        med['fit_por_semente'] = [round(por[sd]['fit'], 3) for sd in p['seeds']]; med['mortos_por_semente'] = [round(por[sd]['mortos'], 3) for sd in p['seeds']]
        med['W'] = {sd: [round(float(x), 5) for x in champs[sd][0]] for sd in p['seeds']}; med['segundos'] = round(time.time() - t1)
        res['bracos'][nome] = med
        print(f'  {nome:<36} NP {A.NP:3d} fit {med["fit"]:6.2f} {med["fit_por_semente"]} ent {med["ent"]:5.1f} mortos {med["mortos"]:.2f} {med["mortos_por_semente"]} '
              f'panes {med["panes"]:4.1f} fome {med["fome_fim"]:3.0f} agua {med["agua_fim"]:3.0f} dinh {med["dinh"]:4.0f} res {med["res"]:4.0f} L/abast {med["litros_por_abast"]:4.0f} abast {med["n_posto"]:4.1f} dof {med["dof"]:4.0f} metab {med["metab"]:.2f} ({med["segundos"]}s)', flush=True)
        tmp = os.path.join(a.out, f'e43{a.tag}.json.tmp')
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, os.path.join(a.out, f'e43{a.tag}.json'))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='triagem', choices=tuple(PRESETS)); ap.add_argument('--L', type=float, default=400.)
    ap.add_argument('--fitness', default='sobrevive', choices=('padrao', 'sobrevive', 'bemestar')); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e43'); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None); ap.add_argument('--G', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--tag', default=''); ap.add_argument('--dias', type=float, default=10.); ap.add_argument('--sem-loja', action='store_true', help='servicos SEPARADOS: comida/agua nao vendidas no posto (E47)'); ap.add_argument('--init-from', nargs=2, default=None); ap.add_argument('--kcal-pane', type=float, default=20., help='[E56c] calorias que a pane cobra da reserva (falta vira dano); 20 = pane mata, 8 = pane doi'); ap.add_argument('--mundo', default='padrao', choices=('padrao', 'distinto'), help='[E56] distinto = ruas + distritos com perfil + precos que mudam'); ap.add_argument('--custo-gene', type=float, default=0., help='[E55] fome x (1 + custo*dof/100): cada gene ligado alem da espinha custa calorias')
    main(ap.parse_args())
