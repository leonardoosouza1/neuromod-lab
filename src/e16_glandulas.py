"""E16 (doc 30): GLANDULAS EVOLUTIVAS — hormonios sem nome.

    python src/e16_glandulas.py [--fase a] [--P 512 --G 10 --T-evo 600] [--out DIR]

Mundo: o RECOMENDADO do E13f (massa + gordura continua .02 + reboque so no
corpo + cap 120), com pena por morte e R alto quando pedido (E14).
Bracos:
    reativo             referencia (glandulas desligadas)
    glandula K=2        duas glandulas sem nome
    glandula K=1        controle: um eixo so basta?
    reativo regime      referencia no mundo com REGIME oculto (combustivel caro/barato por dia)
    glandula K=2 regime a Tese do Corpo: com o otimo variando, a modulacao paga?
Telemetria: h medio por glandula, tau evoluido, custo calorico, quanto o sono
limpou, e as somas que a analise usa pra correlacao h x deficit / h x evento.
"""
import sys, os, time, argparse, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, NF, gerar_cidade, Cfg, Reativo, evoluir_sementes, rodar, modo_execucao
from glandulas import ser_glandular, ler_genes, NOMES_X, NG

PRESET = dict(P=512, G=10, T_evo=600, T_aval=1200, R=4, seeds=(0,))
OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e16'

# mundo recomendado do E13f (o _R do e13_corpo.py)
_R = dict(reserva=True, RES_MAX=120., pane_dinh=0., massa=True, peso=True)


def cfg_gl(glandulas=False, K=2, regime=0., regime_dias=2., kappa=None, H_MAX=None,
           escala_b=None, censo=True, continua=.02, pena_morte=0., sono_come=0., **kw):
    """Mundo-corpo recomendado (E13f) + as flags do E16."""
    c = Cfg(1.0, mundo='base')
    c.massa = True; c.reserva_continua = continua
    c.relogio = True; c.dia = 240; c.eco2 = True; c.pane_fuel = 15.
    c.fuel *= 0.5; c.reboque = True; c.pane_dinh = _R['pane_dinh']
    c.noite = True; c.corpo = True
    c.reserva = True; c.RES_MAX = _R['RES_MAX']; c.peso = True
    c.sono_come = sono_come; c.pena_morte = pena_morte
    c.glandulas = glandulas; c.GL_K = K
    c.gl_regime = regime; c.gl_regime_dias = regime_dias; c.gl_censo = censo
    if kappa is not None: c.KAPPA_H = kappa
    if H_MAX is not None: c.H_MAX = H_MAX
    if escala_b is not None: c.GL_ESCALA_B = escala_b
    for k, v in kw.items(): setattr(c, k, v)
    return c


def _corr(m):
    """corr(h_k, x_i) POR MUNDO, media dos mundos com variancia (zero sync no loop)."""
    if not m.cfg.gl_censo:
        return None
    n = float(m.h_n)
    hm = m.h_soma/n; xm = m.x_soma/n
    hv = (m.h2_soma/n - hm*hm).clamp(min=0).sqrt()
    xv = (m.x2_soma/n - xm*xm).clamp(min=0).sqrt()
    cov = m.hx_soma/n - hm[:, :, None]*xm[:, None, :]
    den = hv[:, :, None]*xv[:, None, :]
    r = torch.where(den > 1e-6, cov/den.clamp(min=1e-12), torch.full_like(cov, float('nan')))
    return torch.nanmean(r, 0)          # (K, 10)


def telemetria(m, T, A=None, w=None):
    f = lambda x: round(float(x.mean()), 3)
    d = dict(
        fit=f(m.ent - 0.3*m.avar), ent=f(m.ent), avar=f(m.avar),
        av_fuel=f(m.av_fuel), av_quente=f(m.av_quente),
        mortos=f((m.vida <= 0).float()), t_vida=f(m.t_vida/T), vida_fim=f(m.vida),
        dano=f(m.dano_soma), n_oficina=f(m.n_oficina), n_posto=f(m.n_posto),
        res_media=f(m.res_soma/T), n_mob=f(m.n_mob), par_fad=f(m.par_fad),
        dinh=f(m.dinh),
    )
    if m.cfg.glandulas:
        n = float(m.h_n)
        d['h_medio'] = [round(float(x), 4) for x in (m.h_soma/n).mean(0)]
        d['ganho_medio'] = {c: round(float(x), 4)
                            for c, x in zip(m.cfg.GL_CANAIS, (m.mult_soma/n).mean(0))}
        d['h_custo'] = f(m.h_custo)
        d['h_sono_limpou'] = f(m.h_sono)
        d['tau'] = [round(float(x), 1) for x in m.tau.mean(0)]
        r = _corr(m)
        if r is not None:
            d['corr'] = {f'h{k}': {nm: (None if torch.isnan(r[k, i]) else round(float(r[k, i]), 3))
                                   for i, nm in enumerate(NOMES_X)}
                         for k in range(r.shape[0])}
        if w is not None:
            tau, a, b = ler_genes(w.cpu(), K=m.cfg.GL_K, cfg=m.cfg)
            d['genes'] = {f'h{k}': dict(tau=round(float(tau[k]), 1),
                                        a={nm: round(float(a[k, i]), 3) for i, nm in enumerate(NOMES_X)},
                                        b={cn: round(float(b[k, j]), 3)
                                           for j, cn in enumerate(m.cfg.GL_CANAIS)})
                          for k in range(m.cfg.GL_K)}
    return d


def braco(A, cfg, treino, teste, p):
    champs = evoluir_sementes(A, treino, cfg, P=p['P'], ger=p['G'], T=p['T_evo'],
                              seeds=p['seeds'], R=p['R'], verbose=False)
    por_sem = []
    for sd in p['seeds']:
        w = champs[sd][0]
        m = rodar(A, w[None, :].repeat(64, 1), teste, cfg, T=p['T_aval'], seed=7777)
        por_sem.append(telemetria(m, p['T_aval'], A, w))
        del m
    num = [k for k, v in por_sem[0].items() if isinstance(v, (int, float))]
    med = {k: round(sum(d[k] for d in por_sem)/len(por_sem), 3) for k in num}
    for k in por_sem[0]:
        if k not in num: med[k] = por_sem[0][k]
    med['fit_por_semente'] = [d['fit'] for d in por_sem]
    med['mortos_por_semente'] = [d['mortos'] for d in por_sem]
    med['hist'] = {sd: champs[sd][1] for sd in p['seeds']}
    med['W'] = {sd: [round(float(x), 5) for x in champs[sd][0]] for sd in p['seeds']}
    return med


A_REF = Reativo
A_K2 = ser_glandular(2)
A_K1 = ser_glandular(1)

BRACOS = [
    ('reativo',             A_REF, dict()),
    ('glandula K=2',        A_K2,  dict(glandulas=True, K=2)),
    ('glandula K=1',        A_K1,  dict(glandulas=True, K=1)),
    ('reativo regime',      A_REF, dict(regime=.35)),
    ('glandula K=2 regime', A_K2,  dict(glandulas=True, K=2, regime=.35)),
    # o preco do hormonio e o suspeito numero 1 se as glandulas ficarem inertes
    ('glandula K=2 kappa.05', A_K2, dict(glandulas=True, K=2, regime=.35, kappa=.05)),
]
# fase b: U invertido na escala dos ganhos (predicao 3)
BRACOS_B = [
    ('glandula b=0.10', A_K2, dict(glandulas=True, K=2, regime=.35, escala_b=.10)),
    ('glandula b=0.25', A_K2, dict(glandulas=True, K=2, regime=.35, escala_b=.25)),
    ('glandula b=1.00', A_K2, dict(glandulas=True, K=2, regime=.35, escala_b=1.00)),
    ('glandula b=4.00', A_K2, dict(glandulas=True, K=2, regime=.35, escala_b=4.00)),
]
# fase c: o sono passa a pagar? (dormir custa 5 de fuel, como no E13j)
BRACOS_C = [
    ('reativo sono5',      A_REF, dict(sono_come=5.)),
    ('glandula K=2 sono5', A_K2,  dict(glandulas=True, K=2, sono_come=5.)),
]
FASES = dict(a=BRACOS, b=BRACOS_B, c=BRACOS_C)


def main(out, fase='a', so=None, P=None, G=None, T_evo=None, T_aval=None, R=None,
         seeds=None, teste_seed=1000, tag=''):
    p = dict(PRESET)
    for k, v in dict(P=P, G=G, T_evo=T_evo, T_aval=T_aval, R=R).items():
        if v: p[k] = v
    if seeds: p['seeds'] = tuple(seeds)
    treino = [gerar_cidade(s) for s in range(4)]
    teste = [gerar_cidade(teste_seed + s) for s in range(3)]
    res = dict(preset=p, modo=modo_execucao(), NF=NF, fase=fase, bracos={}, teste_seed=teste_seed)
    os.makedirs(out, exist_ok=True)
    alvo = os.path.join(out, f'e16_glandulas_{fase}{("_"+tag) if tag else ""}.json')
    t0 = time.time()
    print(f'== E16 glandulas | fase {fase} | P={p["P"]} G={p["G"]} T={p["T_evo"]} '
          f'T_aval={p["T_aval"]} R={p["R"]} x{len(p["seeds"])} sementes | {modo_execucao()} ==', flush=True)
    for nome, A, kw in FASES[fase]:
        if so and nome not in so: continue
        t1 = time.time()
        r = braco(A, cfg_gl(**kw), treino, teste, p)
        r['segundos'] = round(time.time() - t1)
        r['arq'] = A.nome
        res['bracos'][nome] = r
        linha = (f'  {nome:<20} fit {r["fit"]:6.2f} {r["fit_por_semente"]} ent {r["ent"]:5.1f} '
                 f'mortos {r["mortos"]:.2f} panes {r["av_fuel"]:4.1f} quente {r["av_quente"]:4.1f} '
                 f'posto {r["n_posto"]:4.1f} res~ {r["res_media"]:4.1f}')
        if 'h_medio' in r:
            linha += (f' | h {r["h_medio"]} tau {r["tau"]} custo {r["h_custo"]:.1f} '
                      f'sono_limpou {r["h_sono_limpou"]:.1f} ganhos '
                      + ' '.join(f'{k[:4]} {v:.2f}' for k, v in r['ganho_medio'].items()))
        print(linha + f' ({r["segundos"]}s)', flush=True)
        tmp = alvo + '.tmp'
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, alvo)
    print(f'TOTAL {time.time()-t0:.0f}s -> {alvo}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--fase', default='a', choices=tuple(FASES))
    ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--P', type=int, default=None)
    ap.add_argument('--G', type=int, default=None)
    ap.add_argument('--T-evo', type=int, default=None)
    ap.add_argument('--T-aval', type=int, default=None)
    ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None)
    ap.add_argument('--teste-seed', type=int, default=1000)
    ap.add_argument('--tag', default='')
    a = ap.parse_args()
    main(a.out, a.fase, a.so, a.P, a.G, a.T_evo, a.T_aval, a.R, a.seeds, a.teste_seed, a.tag)
