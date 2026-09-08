"""E44: prefeito co-evoluido (doc 45). Bracos: produto sem prefeito | produto + prefeito (coevolucao). Saidas em e44/."""
import sys, os, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from campo import *
from prefeito import Prefeito, coevoluir, SENT, ALAV
from e43_campo import PRESETS

def main(a):
    from e43_campo import BRACOS; ARQ = dict(BRACOS).get(a.arq, Produto); print(f'ser: {a.arq} -> {ARQ.__name__} NP {ARQ.NP}', flush=True)
    p = dict(PRESETS[a.preset]); os.makedirs(a.out, exist_ok=True)
    p['T_evo'] = p['T_aval'] = int(240*a.dias)          # vida em dias (5 dias = viver de poupanca e otimo; 10 obriga a trabalhar)
    if a.seeds: p['seeds'] = tuple(a.seeds)
    if a.G: p['G'] = a.G
    cfg = CfgCampo(L=a.L, pena_morte=a.pena, fitness=a.fitness); cfg.KCAL_PANE = a.kcal_pane; cfg.dinh0 = a.dinh0; cfg.GUINCHO = a.guincho; cfg.FUEL_POS_PANE = a.fuel_pane
    treino = [gerar_mapa(s, L=a.L, distinto=a.mundo == 'distinto') for s in range(4)]; teste = [gerar_mapa(a.teste_seed + s, L=a.L, distinto=a.mundo == 'distinto') for s in range(3)]
    res = dict(preset=a.preset, L=a.L, fitness=a.fitness, pena=a.pena, sentidos=SENT, alavancas=ALAV, bracos={})
    print(f'== E44 prefeito | {a.preset} L={a.L} dias={a.dias} regua={a.fitness} P={p["P"]} G={p["G"]} R={p["R"]} x{len(p["seeds"])} ==', flush=True)
    for nome, com_pref in (('produto sem prefeito', False), ('produto + prefeito (coevolucao)', True)):
        if a.so and nome not in a.so: continue
        t1 = time.time()
        if com_pref:
            champs, Wp, hist = coevoluir(ARQ, treino, cfg, P=p['P'], ger=p['G'], T=p['T_evo'], seeds=p['seeds'], R=p['R'], cada=a.cada)
        else:
            champs = evoluir(ARQ, treino, cfg, P=p['P'], ger=p['G'], T=p['T_evo'], seeds=p['seeds'], R=p['R'], verbose=True); Wp = None; hist = []
        por = {}
        for sd in p['seeds']:
            # avaliacao nos mapas de teste: SEM prefeito (o ser sozinho, mundo padrao) e, se houver, COM o prefeito campeao do treino (mapa 0) aplicado ao teste
            por[sd] = medidas(ARQ, champs[sd][0], teste, cfg, T=p['T_aval'], seed=7777, R=1, copias=128)
            if Wp is not None:
                m, pref = rodar_com_prefeito(ARQ, champs[sd][0][None, :].repeat(128, 1), teste, cfg, p['T_aval'], 7777, R=1, Wp=Wp[:1].repeat(3, 1), prefeito_cls=Prefeito)
                por[sd].update(mortos_com_pref=float((m.vida <= 0).float().mean()), ent_com_pref=float(m.ent.mean()), mult_final=pref.mult[0].tolist(), obras=pref.obras.sum(0).tolist(), caixa=pref.caixa.tolist())
        med = {k: (sum(por[sd][k] for sd in p['seeds'])/len(p['seeds']) if isinstance(por[p['seeds'][0]][k], float) else por[p['seeds'][0]][k]) for k in por[p['seeds'][0]]}
        med['mortos_por_semente'] = [round(por[sd]['mortos'], 3) for sd in p['seeds']]; med['W'] = {sd: [round(float(x), 5) for x in champs[sd][0]] for sd in p['seeds']}
        med['Wp'] = Wp.tolist() if Wp is not None else None; med['hist_prefeito'] = hist; med['segundos'] = round(time.time() - t1)
        res['bracos'][nome] = med
        extra = f" | com prefeito no teste: mortos {med.get('mortos_com_pref', float('nan')):.2f} ent {med.get('ent_com_pref', float('nan')):.1f} mult {[round(x, 2) for x in med.get('mult_final', [])]} obras {med.get('obras', [])}" if com_pref else ''
        print(f'  {nome:<34} fit {med["fit"]:6.2f} mortos {med["mortos"]:.2f} {med["mortos_por_semente"]} ent {med["ent"]:5.1f} panes {med["panes"]:4.1f} fome {med["fome_fim"]:3.0f} agua {med["agua_fim"]:3.0f} dinh {med["dinh"]:4.0f} L/abast {med["litros_por_abast"]:4.0f} ({med["segundos"]}s){extra}', flush=True)
        tmp = os.path.join(a.out, f'e44{a.tag}.json.tmp')
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, os.path.join(a.out, f'e44{a.tag}.json'))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='fumaca', choices=tuple(PRESETS)); ap.add_argument('--L', type=float, default=200.)
    ap.add_argument('--fitness', default='bemestar', choices=('padrao', 'sobrevive', 'bemestar', 'riqueza')); ap.add_argument('--pena', type=float, default=5.); ap.add_argument('--cada', type=int, default=5)
    ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e44'); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--G', type=int, default=None); ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--tag', default=''); ap.add_argument('--dias', type=float, default=10.); ap.add_argument('--arq', default='produto (need x dist, portao)', help='braco do e43 usado como ser'); ap.add_argument('--mundo', default='padrao', choices=('padrao', 'distinto')); ap.add_argument('--guincho', type=float, default=0., help='[E61b] preco do guincho na pane'); ap.add_argument('--fuel-pane', type=float, default=15., help='[E61b] litros com que o guincho deixa o ser no posto'); ap.add_argument('--dinh0', type=float, default=20., help='dinheiro inicial (10 = pobre de verdade: 5 refeicoes)'); ap.add_argument('--kcal-pane', type=float, default=20.)
    main(ap.parse_args())
