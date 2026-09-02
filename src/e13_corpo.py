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
from lab import DEV, NF, gerar_cidade, Cfg, Reativo, evoluir_sementes, rodar, modo_execucao

PRESET = dict(P=1024, G=20, T_evo=600, T_aval=1200, R=4, seeds=(0,1,2))
PRESET_LONGO = dict(P=1024, G=60, T_evo=1200, T_aval=1200, R=4, seeds=(0,1,2))
OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi'

def cfg_corpo(corpo=True, reserva=False, reserva_posto=0., sono_come=0., peso=None, noite=True):
    c = Cfg(1.0, mundo='base')
    c.relogio = True; c.dia = 240; c.eco2 = True; c.pane_fuel = 15.
    c.fuel *= 0.5; c.reboque = True; c.pane_dinh = 20.
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
    return med

BRACOS = [('noite s+r',            dict(corpo=False)),
          ('corpo',                dict()),
          ('corpo reserva',        dict(reserva=True)),
          ('corpo res-posto',      dict(reserva=True, reserva_posto=20.)),
          ('corpo res-posto sono', dict(reserva=True, reserva_posto=20., sono_come=5.))]

def main(preset, out, so=None):
    p = PRESET if preset == 'rapido' else PRESET_LONGO
    sufixo = '' if preset == 'rapido' else '_longo'
    treino = [gerar_cidade(s) for s in range(4)]
    teste  = [gerar_cidade(1000+s) for s in range(3)]
    res = dict(preset=p, modo=modo_execucao(), NF=NF, bracos={})
    t0 = time.time()
    print(f'== E13 corpo | P={p["P"]} G={p["G"]} T={p["T_evo"]} R={p["R"]} x{len(p["seeds"])} sementes ==', flush=True)
    for nome, kw in BRACOS:
        if so and nome not in so: continue
        t1 = time.time()
        r = braco(Reativo, cfg_corpo(**kw), treino, teste, p)
        r['segundos'] = round(time.time()-t1)
        res['bracos'][nome] = r
        print(f'  {nome:<22} fit {r["fit"]:6.2f} {r["fit_por_semente"]} ent {r["ent"]:5.1f} '
              f'mortos {r["mortos"]:.2f} {r["mortos_por_semente"]} t_vida {r["t_vida"]:.2f} vida_fim {r["vida_fim"]:5.1f} '
              f'dano {r["dano"]:5.1f} | panes {r["av_fuel"]:4.1f} furos {r["av_furo"]:3.1f} quente {r["av_quente"]:4.1f} '
              f'oficina {r["n_oficina"]:4.1f} posto {r["n_posto"]:4.1f} pobre {r["pobre_frac"]:.2f} | '
              f'res~ {r["res_media"]:4.1f} mob {r["n_mob"]:.2f} sono {r["sono"]:4.0f} ({r["segundos"]}s)', flush=True)
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
    a = ap.parse_args()
    main(a.preset, a.out, a.so)
