"""E12 (doc 26): energia em DOIS compartimentos + peso no chassi — vale a pena?

    python src/e12_reserva.py [--fase a|b|todas] [--out DIR]

Mundo NOITE: base + relogio 24h (dia=240 passos) + noite 22h-6h (posto FECHADO,
so 1 dos 6 passageiros acordado). Sem noite magra a energia nunca morde
(N13: av_fuel=0 no base) e a reserva nao teria trabalho — regra 1 (teto antes).

Fase A (reativo, 4 bracos por CONFIG do mundo, mesmo genoma NP=NF+18):
    dia          relogio sem noite, sem reserva   -> referencia: quanto a noite custa
    noite        noite, sem reserva               -> TETO da reserva = panes que ela evitaria
    reserva      noite + reserva SEM peso         -> seguro gratis (limite superior)
    reserva+peso noite + reserva + peso no chassi -> o design de verdade
Fase B (cerebro come calorias): talamo vs sempre no mundo noite+reserva+peso
    com custo_neural saindo do TANQUE (KAPPA_F) em vez do fitness.

Preset rapido (mega-lote 3 sementes): P=1024 G=20 T_evo=600 (2.5 dias) R=4,
avaliacao T=1200 (5 dias) em 3 cidades novas. Telemetria por vida: panes de
fuel, mobilizacoes, conversoes a meia-noite, reserva media, tanque as 22h,
entregas a noite, passos parado a noite.
"""
import sys, os, time, argparse, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import (DEV, NF, gerar_cidade, Cfg, Reativo, ReativoHora, Corpo, SerTalamo,
                 evoluir_sementes, rodar, modo_execucao)

PRESET = dict(P=1024, G=20, T_evo=600, T_aval=1200, R=4, seeds=(0,1,2))
# v3 (apos v2): a reserva ficou OCIOSA (res~4/60, conv/dia 6, fuel22 nao sobe).
# Duas suspeitas: G=20/2.5 dias nao da tempo de aprender "encher antes da
# noite" (precisa ler h_sin/h_cos); ou NIVEL=50 alto demais pra dinamica do
# tanque (fuel22 ~33). Preset longo = 5 midnights no treino + braco NIVEL=30.
PRESET_LONGO = dict(P=1024, G=60, T_evo=1200, T_aval=1200, R=4, seeds=(0,1,2))
OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi'

def cfg_noite(noite=True, reserva=False, peso=False, cerebro_come=False, NIVEL=None, rico=False, reboque=False,
              sobra=False, WF=None, WR=None, greve=0):
    c = Cfg(1.0, mundo='base')
    if NIVEL is not None: c.NIVEL = NIVEL
    if WF is not None: c.WF = WF
    if WR is not None: c.WR = WR
    c.reboque = reboque
    if rico: c.pane_dinh = 0.   # v4: pane sem multa em dinheiro — tira a pobreza do caminho
    if sobra: c.fuel *= 0.5     # v7: mundo COM sobra — no padrao o tanque nunca passa de ~35 as 22h
    c.greve = greve             # v9: posto fecha o dia inteiro a cada `greve` dias (escassez rara e grande)
    c.relogio = True; c.dia = 240; c.eco2 = True   # posto enche o tanque: sem isto nao ha sobra a meia-noite
    c.pane_fuel = 15.   # eco2 puro (pane=5) mata o mundo: espiral de panes (v1: ent 0.3, todos os bracos)
    c.noite = noite; c.reserva = reserva; c.peso = peso
    c.cerebro_come = cerebro_come
    return c

def telemetria(m, T):
    dias = T / m.cfg.dia
    f = lambda x: round(float(x.mean()), 3)
    return dict(
        fit=f(m.ent - 0.3*m.avar - getattr(m,'custo_neural',0.)),
        ent=f(m.ent), avar=f(m.avar), av_fuel=f(m.av_fuel), av_quente=f(m.av_quente),
        n_mob=f(m.n_mob), n_conv=f(m.n_conv), conv_por_dia=f(m.conv_soma/dias),
        res_media=f(m.res_soma/T), fuel_22=f(m.fuel_22/m.n_22.clamp(min=1)),
        ent_noite=f(m.ent_noite), par_noite_frac=f(m.par_noite/(T*8/24.)),
        par_fad=f(m.par_fad), dinh=f(m.dinh), fuel_final=f(m.fuel), res_final=f(m.res),
        n_posto=f(m.n_posto), pobre_frac=f(m.t_pobre/T),
    )

def braco(A, cfg, treino, teste, p):
    champs = evoluir_sementes(A, treino, cfg, P=p['P'], ger=p['G'], T=p['T_evo'],
                              seeds=p['seeds'], R=p['R'], verbose=False)
    por_sem = []
    for sd in p['seeds']:
        w = champs[sd][0]
        m = rodar(A, w[None,:].repeat(128,1), teste, cfg, T=p['T_aval'], seed=7777)
        por_sem.append(telemetria(m, p['T_aval']))
    med = {k: round(sum(d[k] for d in por_sem)/len(por_sem), 3) for k in por_sem[0]}
    med['fit_por_semente'] = [d['fit'] for d in por_sem]
    med['hist'] = {sd: champs[sd][1][-1] for sd in p['seeds']}
    return med

def main(fase, out, preset='rapido', arq='reativo'):
    p = PRESET if preset == 'rapido' else PRESET_LONGO
    sufixo = '' if preset == 'rapido' else '_longo'
    A0 = {'reativo': Reativo, 'hora': ReativoHora, 'corpo': Corpo}[arq]
    if arq != 'reativo': sufixo += '_' + arq
    if fase in ('rico','reboque','sobra','greve'): sufixo += '_' + fase
    treino = [gerar_cidade(s) for s in range(4)]
    teste  = [gerar_cidade(1000+s) for s in range(3)]
    res = dict(preset=p, modo=modo_execucao(), NF=NF, bracos={})
    t0 = time.time()
    print(f'== E12 reserva | P={p["P"]} G={p["G"]} T={p["T_evo"]} R={p["R"]} '
          f'x{len(p["seeds"])} sementes | dia=240 noite=22h-6h ==', flush=True)
    if fase in ('a','todas','rico','reboque','sobra','greve'):
        bracos = [('base',         Cfg(1.0, mundo='base')),   # ancora: mundo dos E6/E8/N13
                  ('dia',          cfg_noite(noite=False)),
                  ('noite',        cfg_noite()),
                  ('reserva',      cfg_noite(reserva=True)),
                  ('reserva+peso', cfg_noite(reserva=True, peso=True))]
        if preset != 'rapido':   # longo: so o que decide, + NIVEL=30 (mais gordura se forma)
            bracos = bracos[2:] + [('reserva+peso N30', cfg_noite(reserva=True, peso=True, NIVEL=30.))]
        if fase == 'reboque':    # v6: pane devolve so a racao ate o posto (mata o "posto gratis lento")
            bracos = [('dia reboque',          cfg_noite(noite=False, reboque=True)),
                      ('noite reboque',        cfg_noite(reboque=True)),
                      ('reserva reboque',      cfg_noite(reserva=True, reboque=True)),
                      ('reserva+peso reboque', cfg_noite(reserva=True, peso=True, reboque=True))]
        if fase == 'rico':       # v4: mesmo trio, pane sem multa (pobre_frac era 0.36-0.46)
            bracos = [('noite rico',        cfg_noite(rico=True)),
                      ('reserva rico',      cfg_noite(reserva=True, rico=True)),
                      ('reserva+peso rico', cfg_noite(reserva=True, peso=True, rico=True))]
        if fase == 'sobra':      # v7: fuel x0.5 -> a gordura FORMA (res~17); pares justos c/ e s/ peso
            bracos = [('noite sobra',             cfg_noite(sobra=True)),
                      ('reserva sobra',           cfg_noite(reserva=True, sobra=True)),
                      ('noite+peso sobra',        cfg_noite(peso=True, sobra=True)),
                      ('reserva+peso sobra',      cfg_noite(reserva=True, peso=True, sobra=True)),
                      ('reserva+peso meio sobra', cfg_noite(reserva=True, peso=True, sobra=True, WF=.05, WR=.15)),
                      ('noite+peso meio sobra',   cfg_noite(peso=True, sobra=True, WF=.05))]
        if fase == 'greve':      # v9: escassez RARA e GRANDE (posto fecha 1 dia em 4), sem pane gratis, com sobra
            G = dict(sobra=True, reboque=True, noite=False)
            bracos = [('dia s+r',              cfg_noite(**G)),
                      ('greve4',               cfg_noite(greve=4, **G)),
                      ('greve4 reserva',       cfg_noite(greve=4, reserva=True, **G)),
                      ('greve4 reserva N30',   cfg_noite(greve=4, reserva=True, NIVEL=30., **G)),
                      ('greve4 reserva+peso',  cfg_noite(greve=4, reserva=True, peso=True, **G)),
                      ('greve4 res+peso N30',  cfg_noite(greve=4, reserva=True, peso=True, NIVEL=30., **G)),
                      ('greve4 peso',          cfg_noite(greve=4, peso=True, **G)),                  # ancora justa (so tanque pesa)
                      ('greve4 peso meio',     cfg_noite(greve=4, peso=True, WF=.05, **G)),
                      ('greve4 res+peso meio N30', cfg_noite(greve=4, reserva=True, peso=True, NIVEL=30., WF=.05, WR=.15, **G))]
            if preset == 'rapido' and os.environ.get('E12_SO_ANCORAS'):
                bracos = bracos[6:]
        for nome, cfg in bracos:
            t1 = time.time()
            r = braco(A0, cfg, treino, teste, p)
            r['segundos'] = round(time.time()-t1)
            res['bracos'][nome] = r
            print(f'  {nome:<14} fit {r["fit"]:6.2f} {r["fit_por_semente"]}  '
                  f'ent {r["ent"]:5.1f} av_fuel {r["av_fuel"]:.2f} mob {r["n_mob"]:.2f} '
                  f'conv/dia {r["conv_por_dia"]:.1f} res~ {r["res_media"]:.1f} '
                  f'fuel22 {r["fuel_22"]:.0f} ent_noite {r["ent_noite"]:.1f} '
                  f'par_noite {r["par_noite_frac"]:.2f} posto {r["n_posto"]:.1f} '
                  f'pobre {r["pobre_frac"]:.2f}  ({r["segundos"]}s)', flush=True)
            if nome.startswith('noite') or nome == 'greve4':
                # TETO da reserva (regra 1): cada pane custa 18 passos parado + 0.3
                # de avaria; 18 passos valem (taxa de entrega * 18) entregas
                taxa = r['ent'] / p['T_aval']
                teto = r['av_fuel'] * (18*taxa + 0.3)
                res['teto_reserva'] = round(teto, 3)
                print(f'  >> TETO da reserva no mundo noite: {teto:.2f} de fitness '
                      f'({r["av_fuel"]:.2f} panes/vida x (18 passos x {taxa:.3f} ent/passo + 0.3))',
                      flush=True)
            salvar(res, out, sufixo)
    if fase in ('b','todas'):
        cfg = cfg_noite(reserva=True, peso=True, cerebro_come=True)
        for sub in ('sempre','talamo'):
            A = type(f'T_{sub}', (SerTalamo,), {'submodo': sub, 'nome': f'tal:{sub}'})
            t1 = time.time()
            r = braco(A, cfg, treino, teste, p)
            r['segundos'] = round(time.time()-t1)
            res['bracos'][f'come:{sub}'] = r
            print(f'  come:{sub:<9} fit {r["fit"]:6.2f} {r["fit_por_semente"]}  '
                  f'ent {r["ent"]:5.1f} av_fuel {r["av_fuel"]:.2f} mob {r["n_mob"]:.2f} '
                  f'res~ {r["res_media"]:.1f} fuel22 {r["fuel_22"]:.0f}  ({r["segundos"]}s)',
                  flush=True)
            salvar(res, out, sufixo)
    print(f'TOTAL {time.time()-t0:.0f}s')

def salvar(res, out, sufixo=''):
    os.makedirs(out, exist_ok=True)
    tmp = os.path.join(out, f'e12_reserva{sufixo}.json.tmp')
    with open(tmp, 'w') as f: json.dump(res, f, indent=1)
    os.replace(tmp, os.path.join(out, f'e12_reserva{sufixo}.json'))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--fase', default='todas')
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--preset', default='rapido', choices=('rapido','longo'))
    ap.add_argument('--arq', default='reativo', choices=('reativo','hora','corpo'))
    a = ap.parse_args()
    main(a.fase, a.out, a.preset, a.arq)
