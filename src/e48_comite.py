"""E48: comite = modos gaussianos com inercia, nascido dos 4 campeoes da triagem (linear, reflexo, produto, minimo-3 — parte linear deles)."""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import e43_campo as E43
from campo import *
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('json'); ap.add_argument('--preset', default='triagem', choices=tuple(E43.PRESETS)); ap.add_argument('--L', type=float, default=200.); ap.add_argument('--dias', type=float, default=10.)
    ap.add_argument('--fitness', default='bemestar'); ap.add_argument('--pena', type=float, default=5.); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e48'); ap.add_argument('--tag', default='')
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None); ap.add_argument('--G', type=int, default=None); ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--init-from', nargs=2, default=None); ap.add_argument('--sem-loja', action='store_true')
    a = ap.parse_args(); J = json.load(open(a.json))['bracos']
    nomes = ['linear', 'reflexo', 'produto (need x dist, portao)', 'minimo 3 (d_alvo, d_posto, e_fuel)']
    seeds = tuple(a.seeds) if a.seeds else E43.PRESETS[a.preset]['seeds']
    W0 = {sd: W0_comite([J[n]['W'][str(sd)] for n in nomes]) for sd in seeds}      # comite nasce dos 4 campeoes da mesma semente
    E43.BRACOS = [('comite (4 campeoes, inercia)', Comite), ('modos K=3 do zero (controle)', Modos)]
    class A: pass
    args = A(); args.__dict__.update(preset=a.preset, L=a.L, dias=a.dias, fitness=a.fitness, pena=a.pena, out=a.out, tag=a.tag, seeds=list(seeds), R=a.R, G=a.G, teste_seed=a.teste_seed, so=a.so, init_from=None, sem_loja=a.sem_loja)
    # injeta W0 so no braco do comite
    _evoluir = E43.evoluir
    def evoluir_w0(Arq, *xs, **kw):
        if Arq is Comite: kw['W0'] = W0; kw['sigma0'] = .2
        return _evoluir(Arq, *xs, **kw)
    E43.evoluir = evoluir_w0
    E43.main(args)
