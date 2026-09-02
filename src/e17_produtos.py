"""E17 (doc 31): cerebro com PRODUTOS — bateria.

    python src/e17_produtos.py --arq reativo noite24 produto produto_full
    python src/e17_produtos.py --P 512 --G 10 --T-evo 600 --R 4 --seeds 0 --tag fumaca

Mundo: o recomendado do E13f (`cfg_corpo(continua=.02, **_R)` = massa, gordura
continua 2%, cap 120, reboque so no corpo) + `pena_morte=5` — a config em que
E14g/h mediram a alavanca bilinear. Avaliacao: 128 replicas x 3 cidades de
teste (`teste_seed`+0..2), como em e13_corpo.braco.

Bracos (um por arquitetura, mesmo mundo):
    reativo        politica linear pura                 (ancora de baixo)
    noite24        1 produto fuel x d_posto (E14g)      (referencia: 0.12 mortos)
    produto        5 produtos nec_p x d_p + 2 de hora   (E17)
    produto_full   60 produtos estado x distancia       (busca vs expressividade)

O JSON guarda `W` por semente (campeao), que e o que `analise_produtos.py` le.
"""
import sys, os, time, argparse, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import NF, gerar_cidade, Reativo, ReativoNoite24, modo_execucao
from e13_corpo import cfg_corpo, braco, _R
from produtos import ReativoProduto, ReativoProdutoFull

OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e17'
PRESET = dict(P=1024, G=20, T_evo=600, T_aval=1200, R=4, seeds=(0, 1, 2))
PRESET_LONGO = dict(P=1024, G=60, T_evo=1200, T_aval=1200, R=16, seeds=(0, 1, 2, 3, 4))

ARQS = {'reativo': Reativo, 'noite24': ReativoNoite24,
        'produto': ReativoProduto, 'produto_full': ReativoProdutoFull}
# kwargs do mundo: o recomendado do E13f + a morte visivel no objetivo (E14b)
MUNDO = dict(continua=.02, pena_morte=5., **_R)


def main(a):
    p = dict(PRESET if a.preset == 'rapido' else PRESET_LONGO)
    for k, v in (('P', a.P), ('G', a.G), ('T_evo', a.T_evo), ('T_aval', a.T_aval), ('R', a.R)):
        if v: p[k] = v
    if a.seeds: p['seeds'] = tuple(a.seeds)
    cfg = cfg_corpo(**MUNDO)
    treino = [gerar_cidade(s) for s in range(4)]
    teste = [gerar_cidade(a.teste_seed+s) for s in range(3)]
    sufixo = ('' if a.preset == 'rapido' else '_longo') + (('_'+a.tag) if a.tag else '')
    res = dict(preset={k: list(v) if isinstance(v, tuple) else v for k, v in p.items()},
               modo=modo_execucao(), NF=NF, mundo=MUNDO, teste_seed=a.teste_seed,
               bracos={}, NP={}, base0={})
    os.makedirs(a.out, exist_ok=True)
    caminho = os.path.join(a.out, f'e17_produtos{sufixo}.json')
    t0 = time.time()
    print(f'== E17 produtos | P={p["P"]} G={p["G"]} T={p["T_evo"]} T_aval={p["T_aval"]} '
          f'R={p["R"]} x{len(p["seeds"])} sementes | teste {a.teste_seed}+ | {modo_execucao()} ==', flush=True)
    for nome in a.arq:
        A = ARQS[nome]
        t1 = time.time()
        r = braco(A, cfg, treino, teste, p)
        r['segundos'] = round(time.time()-t1)
        res['bracos'][nome] = r
        res['NP'][nome] = A.NP
        res['base0'][nome] = getattr(A, 'B0', None)
        print(f'  {nome:<14} NP {A.NP:>3}  fit {r["fit"]:6.2f} {r["fit_por_semente"]} '
              f'mortos {r["mortos"]:.3f} {r["mortos_por_semente"]} ent {r["ent"]:5.1f} '
              f'panes {r["av_fuel"]:4.1f} posto {r["n_posto"]:4.1f} oficina {r["n_oficina"]:4.1f} '
              f'vida_fim {r["vida_fim"]:5.1f} ({r["segundos"]}s)', flush=True)
        tmp = caminho + '.tmp'
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, caminho)
    print(f'TOTAL {time.time()-t0:.0f}s -> {caminho}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='rapido', choices=('rapido', 'longo'))
    ap.add_argument('--out', default=OUT)
    ap.add_argument('--arq', nargs='*', default=['reativo', 'noite24', 'produto', 'produto_full'],
                    choices=tuple(ARQS))
    ap.add_argument('--P', type=int, default=None)
    ap.add_argument('--G', type=int, default=None)
    ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--T-evo', type=int, dest='T_evo', default=None)
    ap.add_argument('--T-aval', type=int, dest='T_aval', default=None)
    ap.add_argument('--teste-seed', type=int, default=1000)
    ap.add_argument('--seeds', type=int, nargs='*', default=None)
    ap.add_argument('--tag', default='')
    main(ap.parse_args())
