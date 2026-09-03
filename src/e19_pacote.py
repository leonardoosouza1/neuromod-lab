"""E19 (doc 35): PACOTE DE DENTES em deixa-um-de-fora.

Buraco achado (2026-09-02): um ser que nao faz nada por 5 dias termina com vida 100,
fome 100 e fit 0 — parar era de graca e seguro, e foi o atrator de 3 colapsos.
Pacote = economia (reboque gordura->vida) + fome mata + divida mata + cerebro com
produto de LIMIAR. Bracos: pacote completo e pacote menos cada peca; o que piorar, sai.

    python src/e19_pacote.py --seeds 0 1 2 3 4 --R 16 --pena 5 [--so "pacote" ...]
"""
import sys, os, time, argparse, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, NF, gerar_cidade, Reativo, evoluir_sementes, rodar, modo_execucao
from produtos import ReativoProduto, ReativoProdutoLimiar
import e15_economia as E15
from e15_economia import cfg_e15

OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e19'
PRESET = dict(P=1024, G=60, T_evo=1200, T_aval=1200, R=16, seeds=(0,1,2,3,4))
# triagem (Leonardo 2026-09-03: "40 min e muito"): R=8, G=40, 3 sementes ~ 2.5 min/braco.
# Serve pra ver se a feature FUNCIONA e a direcao; mortalidade (sigma ~7 pp) so decide no honesto.
PRESET_TRIAGEM = dict(P=1024, G=40, T_evo=1200, T_aval=1200, R=8, seeds=(0,1,2))

def cfg_pacote(economia=True, fome=.5, divida=True, refeicao=45., comida_no_posto=False, fome_gracia=0, **kw):
    c = cfg_e15(economia=economia, **kw)      # reboque gordura->vida e o default novo
    c.fome_mata = fome; c.divida_mata = divida; c.REFEICAO = refeicao; c.comida_no_posto = comida_no_posto
    c.fome_gracia = fome_gracia
    return c

BRACOS = [('pacote',            ReativoProdutoLimiar, dict()),
          ('pacote - fome',     ReativoProdutoLimiar, dict(fome=0.)),
          ('pacote - divida',   ReativoProdutoLimiar, dict(divida=False)),
          ('pacote - limiar',   ReativoProduto,       dict()),
          ('pacote - produto',  Reativo,              dict()),
          ('pacote - economia', ReativoProdutoLimiar, dict(economia=False)),
          # e19b: a fome a 0.5/passo matou 96 % (deserto evolutivo: todo mundo morre antes de
          # aprender a comer; fome sobe 0.32/passo, refeicao -45). Dentes mais suaves:
          ('pacote fome .15',   ReativoProdutoLimiar, dict(fome=.15)),
          ('pacote fome .10',   ReativoProdutoLimiar, dict(fome=.10)),
          ('pacote fome .15 reativo', Reativo,        dict(fome=.15)),
          # e19c: o lado da COMIDA — refeicao de 90 (1/dia basta) com fome .15
          ('pacote ref90 fome .15',         ReativoProdutoLimiar, dict(fome=.15, refeicao=90.)),
          ('pacote ref90 fome .15 reativo', Reativo,              dict(fome=.15, refeicao=90.)),
          ('pacote ref90 fome .15 - economia', ReativoProdutoLimiar, dict(fome=.15, refeicao=90., economia=False)),
          # e19d: o POSTO vende comida (diagnostico: 2 refeicoes/vida, peso de d_comida ~0, 3 nos com comida)
          ('pacote posto-comida reativo', Reativo,              dict(fome=.15, refeicao=90., comida_no_posto=True)),
          ('pacote posto-comida limiar',  ReativoProdutoLimiar, dict(fome=.15, refeicao=90., comida_no_posto=True)),
          ('pacote posto-comida ref45 reativo', Reativo,        dict(fome=.15, refeicao=45., comida_no_posto=True))]

def telemetria(m, T):
    f = lambda x: round(float(x.mean()), 3)
    return dict(fit=f(m.ent - 0.3*m.avar), ent=f(m.ent), avar=f(m.avar), av_fuel=f(m.av_fuel),
                av_quente=f(m.av_quente), mortos=f((m.vida <= 0).float()), t_vida=f(m.t_vida/T),
                vida_fim=f(m.vida), dano=f(m.dano_soma), fome_fim=f(m.fome), n_posto=f(m.n_posto),
                n_oficina=f(m.n_oficina), pobre_frac=f(m.t_pobre/T), dinh=f(m.dinh), res_media=f(m.res_soma/T))

def main(a):
    E15.PENA = a.pena
    p = dict(PRESET_TRIAGEM if a.preset == 'triagem' else PRESET); 
    if a.seeds: p['seeds'] = tuple(a.seeds)
    if a.R: p['R'] = a.R
    treino = [gerar_cidade(s) for s in range(4)]
    teste = [gerar_cidade(a.teste_seed + s) for s in range(3)]
    res = dict(preset=p, modo=modo_execucao(), NF=NF, teste_seed=a.teste_seed, pena=a.pena, bracos={})
    os.makedirs(a.out, exist_ok=True); t0 = time.time()
    print(f'== E19 pacote | P={p["P"]} G={p["G"]} R={p["R"]} x{len(p["seeds"])} sementes | pena {a.pena} | teste {a.teste_seed}+ ==', flush=True)
    for nome, A, kw in BRACOS:
        if a.so and nome not in a.so: continue
        t1 = time.time(); cfg = cfg_pacote(**kw)
        champs = evoluir_sementes(A, treino, cfg, P=p['P'], ger=p['G'], T=p['T_evo'], seeds=p['seeds'], R=p['R'], verbose=False)
        por = []
        for sd in p['seeds']:
            m = rodar(A, champs[sd][0][None, :].repeat(128, 1), teste, cfg, T=p['T_aval'], seed=7777)
            por.append(telemetria(m, p['T_aval']))
        med = {k: round(sum(d[k] for d in por)/len(por), 3) for k in por[0]}
        med['fit_por_semente'] = [d['fit'] for d in por]; med['mortos_por_semente'] = [d['mortos'] for d in por]
        med['W'] = {sd: [round(float(x), 5) for x in champs[sd][0]] for sd in p['seeds']}
        med['segundos'] = round(time.time() - t1); res['bracos'][nome] = med
        print(f'  {nome:<20} fit {med["fit"]:6.2f} {med["fit_por_semente"]} ent {med["ent"]:5.1f} mortos {med["mortos"]:.2f} {med["mortos_por_semente"]} '
              f'panes {med["av_fuel"]:4.1f} quente {med["av_quente"]:3.1f} vida_fim {med["vida_fim"]:5.1f} fome_fim {med["fome_fim"]:4.0f} '
              f'posto {med["n_posto"]:4.1f} pobre {med["pobre_frac"]:.2f} dinh {med["dinh"]:6.1f} ({med["segundos"]}s)', flush=True)
        tmp = os.path.join(a.out, f'e19_pacote{a.tag}.json.tmp')
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, os.path.join(a.out, f'e19_pacote{a.tag}.json'))
    print(f'TOTAL {time.time()-t0:.0f}s')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=OUT); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default='')
    ap.add_argument('--preset', default='honesto', choices=('honesto','triagem'))
    main(ap.parse_args())
