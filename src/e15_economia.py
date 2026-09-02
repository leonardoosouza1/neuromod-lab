"""E15 (doc 29): ECONOMIA REAL — dinheiro compra tudo, distritos, imposto pela
origem da corrida, reboque em CALORIAS, divida com juros.

    python src/e15_economia.py [--preset rapido|longo] [--fase a|b|c] [--out DIR]

Mundo base = o recomendado do E13 (`cfg_corpo(continua=.02, **_R)`: massa,
gordura continua 2%, reboque so no corpo, pane_dinh=0) + `cfg.economia`:
  - D=3 distritos por particao espacial; aliquota (.10/.20/.30) e multiplicador
    de preco (0.8/1.0/1.3) PAREADOS e sorteados por MUNDO (lei oculta);
  - imposto ao RECEBER pela aliquota do distrito de ORIGEM da corrida;
  - imposto ao GASTAR: preco base x multiplicador x (1+aliquota) do no ATUAL;
  - ALUGUEL + AGUA todo dia a meia-noite;
  - divida ate -LIMITE com juros diarios (nunca morte por dinheiro);
  - reboque cobra KCAL_REBOQUE x d_posto de gordura (depois tanque), e a pane
    fere 3 de vida em vez de 6 (senao punia tres vezes).

Bracos (fase a): corpo (sem economia) | economia | economia rico (aluguel 3) |
economia pobre (aluguel 10) | economia sem juros.
"""
import sys, os, time, argparse, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import (DEV, NF, gerar_cidade, Reativo, ReativoNoite, ReativoNoite24,
                 evoluir_sementes, rodar, modo_execucao)
from e13_corpo import cfg_corpo, _R

PRESET       = dict(P=1024, G=20, T_evo=600,  T_aval=1200, R=4, seeds=(0,1,2))
PRESET_LONGO = dict(P=1024, G=60, T_evo=1200, T_aval=1200, R=4, seeds=(0,1,2))
OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e15'


def cfg_e15(economia=True, aluguel=6., agua=2., juros=.05, kcal=1.0, limite=60.,
            aliq=None, pmul=None, sorteia=True, D=3, D_pane=3., imposto=None,
            kcal_vida=0., **kw):
    """mundo recomendado do E13 + economia. pane_dinh ja e 0 em _R (N16)."""
    c = cfg_corpo(continua=.02, **{**_R, **kw})
    if imposto is not None: c.imposto = imposto
    if economia:
        c.economia = True
        c.ALUGUEL = aluguel; c.AGUA = agua; c.JUROS = juros
        c.KCAL_REBOQUE = kcal; c.KCAL_VIDA = kcal_vida; c.LIMITE_DIVIDA = limite
        c.D_DIST = D; c.dist_sorteia = sorteia
        if aliq is not None: c.ALIQ = aliq
        if pmul is not None: c.PMUL = pmul
        c.pane_dinh = 0.       # reboque cobra CALORIAS; multa em dinheiro = N16
        c.D_PANE = D_pane      # a pane ja cobra caloria: nao pode ferir 6 tambem
    return c


def telemetria(m, T):
    f = lambda x: round(float(x.mean()), 3)
    d = dict(
        fit=f(m.ent - 0.3*m.avar), ent=f(m.ent), avar=f(m.avar),
        av_fuel=f(m.av_fuel), av_furo=f(m.av_furo), av_oleo=f(m.av_oleo), av_quente=f(m.av_quente),
        mortos=f((m.vida <= 0).float()), t_vida=f(m.t_vida/T), vida_fim=f(m.vida), dano=f(m.dano_soma),
        n_oficina=f(m.n_oficina), n_posto=f(m.n_posto), pobre_frac=f(m.t_pobre/T), dinh=f(m.dinh),
        n_mob=f(m.n_mob), conv_por_dia=f(m.conv_soma/(T/m.cfg.dia)), res_media=f(m.res_soma/T),
        par_fad=f(m.par_fad), fuel_22=f(m.fuel_22/m.n_22.clamp(min=1)),
        par_noite_frac=f(m.par_noite/(T*8/24.)), ent_noite=f(m.ent_noite),
        renda_bruta=f(m.rec),
    )
    if m.cfg.economia:
        d.update(
            imp_receber=f(m.imp_orig), imp_gastar=f(m.imp_gastar),
            aluguel_agua=f(m.aluguel_pago), juros=f(m.juros_pago),
            div_max=f(m.div_max), div_frac=f(m.t_divida/T), kcal_reboque=f(m.kcal_reb),
            # razao das MEDIAS (nao media das razoes: quem morre cedo tem rec~0 e
            # a razao explode — foi o 814138 da 1a rodada)
            carga_fiscal=round(float((m.imp_orig+m.imp_gastar+m.aluguel_pago+m.juros_pago).mean()
                                     / max(float(m.rec.mean()), 1e-6)), 3),
            t_dist=[round(float(x), 1) for x in m.t_dist.mean(0)],   # por POSTO de preco: [barato, medio, caro]
            ent_dist=[round(float(x), 2) for x in m.ent_dist.mean(0)],
            div_max_p=[round(float(x), 1) for x in torch.quantile(
                m.div_max, torch.tensor([0., .25, .5, .75, 1.], device=m.div_max.device))],
        )
    else:
        d.update(imp_receber=0., imp_gastar=0., aluguel_agua=0., juros=0., div_max=0.,
                 div_frac=0., kcal_reboque=0., carga_fiscal=0., t_dist=[], ent_dist=[],
                 div_max_p=[])
    return d


def braco(A, cfg, treino, teste, p):
    champs = evoluir_sementes(A, treino, cfg, P=p['P'], ger=p['G'], T=p['T_evo'],
                              seeds=p['seeds'], R=p['R'], verbose=False)
    por_sem = []
    for sd in p['seeds']:
        m = rodar(A, champs[sd][0][None, :].repeat(128, 1), teste, cfg,
                  T=p['T_aval'], seed=7777)
        por_sem.append(telemetria(m, p['T_aval']))
    med = {k: (round(sum(d[k] for d in por_sem)/len(por_sem), 3)
               if isinstance(por_sem[0][k], (int, float))
               else [round(sum(d[k][i] for d in por_sem)/len(por_sem), 2)
                     for i in range(len(por_sem[0][k]))])
           for k in por_sem[0]}
    med['fit_por_semente'] = [d['fit'] for d in por_sem]
    med['mortos_por_semente'] = [d['mortos'] for d in por_sem]
    med['div_frac_por_semente'] = [d['div_frac'] for d in por_sem]
    med['hist'] = {sd: champs[sd][1] for sd in p['seeds']}
    med['W'] = {sd: [round(float(x), 5) for x in champs[sd][0]] for sd in p['seeds']}
    return med


# fase a: o essencial pedido pelo Leonardo
BRACOS = [('corpo (sem economia)', dict(economia=False)),
          ('economia',             dict()),
          ('economia rico',        dict(aluguel=3.)),
          ('economia pobre',       dict(aluguel=10.)),
          ('economia sem juros',   dict(juros=0.))]
# fase b: decomposicao — de onde vem o custo da economia
BRACOS_B = [('economia so imposto',   dict(aluguel=0., agua=0.)),
            ('economia so aluguel',   dict(aliq=(.18, .18, .18), pmul=(1., 1., 1.))),
            ('economia kcal 0',       dict(kcal=0.)),
            ('economia kcal 3',       dict(kcal=3.)),
            # moeda cruzada: gordura paga o guincho, o resto vira VIDA (nunca o tanque)
            ('economia reboque so gordura', dict(kcal_vida=1.)),
            ('economia so gordura kcal 3',  dict(kcal=3., kcal_vida=1.))]
# fase c: os distritos importam? (lei oculta vs fixa vs cidade plana)
BRACOS_C = [('economia distritos fixos', dict(sorteia=False)),
            ('economia sem distritos',   dict(aliq=(.20, .20, .20), pmul=(1.03, 1.03, 1.03))),
            ('economia D=1',             dict(D=1, aliq=(.20,), pmul=(1.03,)))]

FASES = {'a': BRACOS, 'b': BRACOS_B, 'c': BRACOS_C}
ARQS = {'reativo': Reativo, 'noite': ReativoNoite, 'noite24': ReativoNoite24}


def main(preset, out, so=None, fase='a', arq='reativo', T_aval=None, teste_seed=1000,
         seeds=None, tag='', G=None, T_evo=None, R=None, P=None):
    p = dict(PRESET if preset == 'rapido' else PRESET_LONGO)
    for k, v in (('T_aval', T_aval), ('R', R), ('G', G), ('T_evo', T_evo), ('P', P)):
        if v: p[k] = v
    if seeds: p['seeds'] = tuple(seeds)
    A0 = ARQS[arq]
    sufixo = '' if preset == 'rapido' else '_longo'
    if arq != 'reativo': sufixo += '_' + arq
    if fase != 'a': sufixo += '_' + fase
    if tag: sufixo += '_' + tag
    treino = [gerar_cidade(s) for s in range(4)]
    teste  = [gerar_cidade(teste_seed+s) for s in range(3)]
    res = dict(preset=p, modo=modo_execucao(), NF=NF, arq=arq, bracos={}, teste_seed=teste_seed)
    t0 = time.time()
    print(f'== E15 economia | {arq} | P={p["P"]} G={p["G"]} T={p["T_evo"]} '
          f'T_aval={p["T_aval"]} R={p["R"]} x{len(p["seeds"])} sementes | teste {teste_seed}+ ==',
          flush=True)
    for nome, kw in FASES[fase]:
        if so and nome not in so: continue
        t1 = time.time()
        r = braco(A0, cfg_e15(**kw), treino, teste, p)
        r['segundos'] = round(time.time()-t1)
        res['bracos'][nome] = r
        print(f'  {nome:<22} fit {r["fit"]:6.2f} {r["fit_por_semente"]} ent {r["ent"]:5.1f} '
              f'mortos {r["mortos"]:.2f} {r["mortos_por_semente"]} | panes {r["av_fuel"]:4.1f} '
              f'quente {r["av_quente"]:4.1f} posto {r["n_posto"]:4.1f} oficina {r["n_oficina"]:4.1f} '
              f'res~ {r["res_media"]:4.1f} | bruta {r["renda_bruta"]:6.1f} imp_r {r["imp_receber"]:5.1f} '
              f'imp_g {r["imp_gastar"]:5.1f} alug {r["aluguel_agua"]:5.1f} jur {r["juros"]:4.1f} '
              f'carga {r["carga_fiscal"]:.2f} | div_max {r["div_max"]:5.1f} div_frac {r["div_frac"]:.2f} '
              f'pobre {r["pobre_frac"]:.2f} kcal {r["kcal_reboque"]:5.1f} ({r["segundos"]}s)', flush=True)
        os.makedirs(out, exist_ok=True)
        tmp = os.path.join(out, f'e15_economia{sufixo}.json.tmp')
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, os.path.join(out, f'e15_economia{sufixo}.json'))
    print(f'TOTAL {time.time()-t0:.0f}s')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='rapido', choices=('rapido', 'longo'))
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--fase', default='a', choices=tuple('abc'))
    ap.add_argument('--arq', default='reativo', choices=tuple(ARQS))
    ap.add_argument('--P', type=int, default=None)
    ap.add_argument('--G', type=int, default=None)
    ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--T-evo', type=int, default=None)
    ap.add_argument('--T-aval', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000)
    ap.add_argument('--seeds', type=int, nargs='*', default=None)
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    main(a.preset, a.out, a.so, a.fase, a.arq, a.T_aval, a.teste_seed, a.seeds,
         a.tag, a.G, a.T_evo, a.R, a.P)
