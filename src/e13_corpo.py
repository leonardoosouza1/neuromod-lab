"""E13 (doc 27): CORPO = CARRO — dano real, morte, gordura facil, sono que come.

    python src/e13_corpo.py [--preset rapido|longo] [--out DIR]

Mundo: E12-v8 (fuel x0.5, reboque, noite 22-6h) + pane_dinh 20 + cfg.corpo.
Bracos (Reativo, mesmo genoma NP=NF+18):
    noite s+r          sem corpo (ancora: quanto o corpo custa)
    corpo              dano + morte
    corpo reserva      + reserva so da meia-noite, com peso (I=10: pela lei ~0)
    corpo res-posto    + posto tambem enche a reserva (I~54 >= f.S: pela lei paga)
    corpo res-posto sono  + dormir custa 5 de fuel
Telemetria por vida: mortos, t_vida, vida_fim, dano, oficina, avarias por causa.
"""
import sys, os, time, argparse, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, NF, gerar_cidade, Cfg, Reativo, ReativoHora, Corpo, SerTalamo, evoluir_sementes, rodar, modo_execucao

PRESET = dict(P=1024, G=20, T_evo=600, T_aval=1200, R=4, seeds=(0,1,2))
PRESET_LONGO = dict(P=1024, G=60, T_evo=1200, T_aval=1200, R=4, seeds=(0,1,2))
OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi'

def cfg_corpo(corpo=True, reserva=False, reserva_posto=0., sono_come=0., peso=None, noite=True, RES_MAX=None, pane_dinh=20.,
              WF=None, WR=None, massa=False, continua=0., KG_RES=None, KG_PAX=None, cerebro_come=False, greve=0,
              sono_bloco=False):
    c = Cfg(1.0, mundo='base')
    c.sono_bloco = sono_bloco
    c.massa = massa; c.reserva_continua = continua
    if KG_RES is not None: c.KG_RES = KG_RES
    if KG_PAX is not None: c.KG_PAX = KG_PAX
    c.cerebro_come = cerebro_come; c.greve = greve
    if RES_MAX is not None: c.RES_MAX = RES_MAX
    if WF is not None: c.WF = WF
    if WR is not None: c.WR = WR
    c.relogio = True; c.dia = 240; c.eco2 = True; c.pane_fuel = 15.
    c.fuel *= 0.5; c.reboque = True; c.pane_dinh = pane_dinh
    c.noite = noite; c.corpo = corpo
    c.reserva = reserva; c.reserva_posto = reserva_posto; c.sono_come = sono_come
    c.peso = reserva if peso is None else peso
    return c

def telemetria(m, T):
    f = lambda x: round(float(x.mean()), 3)
    return dict(
        fit=f(m.ent - 0.3*m.avar), ent=f(m.ent), avar=f(m.avar),
        av_fuel=f(m.av_fuel), av_furo=f(m.av_furo), av_oleo=f(m.av_oleo), av_quente=f(m.av_quente),
        mortos=f((m.vida <= 0).float()), t_vida=f(m.t_vida/T), vida_fim=f(m.vida), dano=f(m.dano_soma),
        n_oficina=f(m.n_oficina), n_posto=f(m.n_posto), pobre_frac=f(m.t_pobre/T), dinh=f(m.dinh),
        n_mob=f(m.n_mob), conv_por_dia=f(m.conv_soma/(T/m.cfg.dia)), res_media=f(m.res_soma/T),
        sono=f(m.sono_soma), par_fad=f(m.par_fad), fuel_22=f(m.fuel_22/m.n_22.clamp(min=1)),
        n_bloco=f(m.n_bloco), par_noite_frac=f(m.par_noite/(T*8/24.)), ent_noite=f(m.ent_noite),
    )

def braco(A, cfg, treino, teste, p):
    champs = evoluir_sementes(A, treino, cfg, P=p['P'], ger=p['G'], T=p['T_evo'],
                              seeds=p['seeds'], R=p['R'], verbose=False)
    por_sem = []
    for sd in p['seeds']:
        m = rodar(A, champs[sd][0][None,:].repeat(128,1), teste, cfg, T=p['T_aval'], seed=7777)
        por_sem.append(telemetria(m, p['T_aval']))
    med = {k: round(sum(d[k] for d in por_sem)/len(por_sem), 3) for k in por_sem[0]}
    med['fit_por_semente'] = [d['fit'] for d in por_sem]
    med['mortos_por_semente'] = [d['mortos'] for d in por_sem]
    med['hist'] = {sd: champs[sd][1] for sd in p['seeds']}
    med['W'] = {sd: [round(float(x), 5) for x in champs[sd][0]] for sd in p['seeds']}   # campeao (diagnostico)
    return med

BRACOS = [('noite s+r',            dict(corpo=False)),
          ('corpo',                dict()),
          ('corpo reserva',        dict(reserva=True)),
          ('corpo res-posto',      dict(reserva=True, reserva_posto=20.)),
          ('corpo res-posto sono', dict(reserva=True, reserva_posto=20., sono_come=5.))]
# E13b: decomposicao peso x reserva x cap (o peso .10/.30 ferve o motor no mundo corpo)
BRACOS_B = [('corpo peso',                 dict(peso=True)),
            ('corpo reserva s/peso',       dict(reserva=True, peso=False)),
            ('corpo res-posto s/peso',     dict(reserva=True, reserva_posto=20., peso=False)),
            ('corpo res-posto s/peso R120',dict(reserva=True, reserva_posto=20., peso=False, RES_MAX=120.)),
            ('corpo res-posto peso R120',  dict(reserva=True, reserva_posto=20., peso=True, RES_MAX=120.))]
# E13c: armadilha de pobreza — o reboque de 20 dinh transforma a 1a pane em sentenca
BRACOS_C = [('R120 reboque 8',  dict(reserva=True, reserva_posto=20., peso=False, RES_MAX=120., pane_dinh=8.)),
            ('R120 reboque 0',  dict(reserva=True, reserva_posto=20., peso=False, RES_MAX=120., pane_dinh=0.))]
# E13d: calibracao do peso na config vencedora (reboque 0, cap 120)
_V = dict(reserva=True, reserva_posto=20., RES_MAX=120., pane_dinh=0.)
BRACOS_E = [('vencedor peso .10/.30', dict(peso=True, **_V))]   # E13e: rodar com --arq hora|corpo
# E13f: RECOMENDADO — cap 120, reboque so no corpo, peso por MASSA, gordura CONTINUA (sem posto, sem lote)
_R = dict(reserva=True, RES_MAX=120., pane_dinh=0., massa=True, peso=True)
BRACOS_F = [('recomendado (taxa .02)',   dict(continua=.02, **_R)),
            ('recomendado taxa .05',     dict(continua=.05, **_R)),
            ('recomendado sem peso',     dict(continua=.02, **{**_R, 'peso': False})),
            ('recomendado sem gordura',  dict(reserva=False, RES_MAX=120., pane_dinh=0., massa=True, peso=True))]
# E13g: de onde vem o custo do peso por massa (passageiro? gordura? taxa?)
BRACOS_G = [('recomendado taxa .01',     dict(continua=.01, **_R)),
            ('recomendado pax 0kg',      dict(continua=.02, KG_PAX=0., **_R)),
            ('recomendado gordura 1.5kg',dict(continua=.02, KG_RES=1.5, **_R))]
# E13h: vida longa (usar --T-aval 2400 e --teste-seed 2000)
BRACOS_H = [('recomendado (taxa .02)',   dict(continua=.02, **_R))]
# E13i: replicacao "a dor ensina" (usar --seeds 0 1 2 3 4)
BRACOS_I = [('noite s+r', dict(corpo=False)), ('corpo', dict())]
# E13j: sono come + cerebro come no recomendado (talamo via --arq talamo|sempre)
BRACOS_J = [('recomendado sono 5',      dict(continua=.02, sono_come=5., **_R)),
            ('recomendado cerebro come',dict(continua=.02, cerebro_come=True, **_R))]
# E13k: greve (fome rara) no recomendado — a gordura continua cobre?
BRACOS_K = [('recomendado greve4',             dict(continua=.02, greve=4, **_R)),
            ('recomendado sem gordura greve4',  dict(reserva=False, RES_MAX=120., pane_dinh=0., massa=True, peso=True, greve=4))]
# E13l: sono em bloco a noite (rodar com --arq reativo e --arq hora)
BRACOS_L = [('recomendado sono bloco', dict(continua=.02, sono_bloco=True, **_R))]
BRACOS_D = [('vencedor peso .03/.10', dict(peso=True, WF=.03, WR=.10, **_V)),
            ('vencedor peso .05/.15', dict(peso=True, WF=.05, WR=.15, **_V)),
            ('vencedor peso .10/.30', dict(peso=True, **_V))]

def main(preset, out, so=None, fase='a', arq='reativo', T_aval=None, teste_seed=1000, seeds=None, tag=''):
    p = dict(PRESET if preset == 'rapido' else PRESET_LONGO)
    if T_aval: p['T_aval'] = T_aval
    if seeds: p['seeds'] = tuple(seeds)
    sufixo = '' if preset == 'rapido' else '_longo'
    if arq in ('talamo','sempre'):
        A0 = type(f'T_{arq}', (SerTalamo,), {'submodo': arq, 'nome': f'tal:{arq}'})
    else:
        A0 = {'reativo': Reativo, 'hora': ReativoHora, 'corpo': Corpo}[arq]
    if arq != 'reativo': sufixo += '_' + arq
    if tag: sufixo += '_' + tag
    bracos = {'a': BRACOS, 'b': BRACOS_B, 'c': BRACOS_C, 'd': BRACOS_D, 'e': BRACOS_E, 'f': BRACOS_F,
              'g': BRACOS_G, 'h': BRACOS_H, 'i': BRACOS_I, 'j': BRACOS_J, 'k': BRACOS_K, 'l': BRACOS_L}[fase]
    if fase != 'a': sufixo += '_' + fase
    treino = [gerar_cidade(s) for s in range(4)]
    teste  = [gerar_cidade(teste_seed+s) for s in range(3)]
    res = dict(preset=p, modo=modo_execucao(), NF=NF, bracos={}, teste_seed=teste_seed)
    t0 = time.time()
    print(f'== E13 corpo | P={p["P"]} G={p["G"]} T={p["T_evo"]} T_aval={p["T_aval"]} R={p["R"]} x{len(p["seeds"])} sementes | teste {teste_seed}+ ==', flush=True)
    for nome, kw in bracos:
        if so and nome not in so: continue
        t1 = time.time()
        r = braco(A0, cfg_corpo(**kw), treino, teste, p)
        r['segundos'] = round(time.time()-t1)
        res['bracos'][nome] = r
        print(f'  {nome:<22} fit {r["fit"]:6.2f} {r["fit_por_semente"]} ent {r["ent"]:5.1f} '
              f'mortos {r["mortos"]:.2f} {r["mortos_por_semente"]} t_vida {r["t_vida"]:.2f} vida_fim {r["vida_fim"]:5.1f} '
              f'dano {r["dano"]:5.1f} | panes {r["av_fuel"]:4.1f} furos {r["av_furo"]:3.1f} quente {r["av_quente"]:4.1f} '
              f'oficina {r["n_oficina"]:4.1f} posto {r["n_posto"]:4.1f} pobre {r["pobre_frac"]:.2f} | '
              f'res~ {r["res_media"]:4.1f} mob {r["n_mob"]:.2f} sono {r["sono"]:4.0f} bloco {r["n_bloco"]:.1f} par_noite {r["par_noite_frac"]:.2f} ({r["segundos"]}s)', flush=True)
        os.makedirs(out, exist_ok=True)
        tmp = os.path.join(out, f'e13_corpo{sufixo}.json.tmp')
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, os.path.join(out, f'e13_corpo{sufixo}.json'))
    print(f'TOTAL {time.time()-t0:.0f}s')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='rapido', choices=('rapido','longo'))
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--fase', default='a', choices=tuple('abcdefghijkl'))
    ap.add_argument('--T-aval', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000)
    ap.add_argument('--seeds', type=int, nargs='*', default=None)
    ap.add_argument('--tag', default='')
    ap.add_argument('--arq', default='reativo', choices=('reativo','hora','corpo','talamo','sempre'))
    a = ap.parse_args()
    main(a.preset, a.out, a.so, a.fase, a.arq, a.T_aval, a.teste_seed, a.seeds, a.tag)
