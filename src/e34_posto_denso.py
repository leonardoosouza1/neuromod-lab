"""E34: geometria — +k postos nos nos mais longe (em saltos) dos postos existentes. Wrapper no gerador; lab.py intocado.
Comida segue o posto (comida_no_posto). Uso: --extra 2."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import e20_corpo_fala as E20
from lab import Reativo, gerar_cidade as _gerar
from reacoes import ReativoReacoes

def saltos(A, fontes):
    n = A.shape[0]; d = np.full(n, 10**6); fila = list(fontes)
    for f in fontes: d[f] = 0
    while fila:
        i = fila.pop(0)
        for j in A[i]:
            if j >= 0 and d[j] > d[i] + 1: d[j] = d[i] + 1; fila.append(j)
    return d

def com_postos_extra(seed, k=2, **kw):
    c = _gerar(seed, **kw); serv = c['serv']
    for _ in range(k):
        d = saltos(c['A'], np.flatnonzero(serv[:, 0] > 0)); i = int(np.argmax(d)); serv[i, 0] = 1.0
    return c

if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='triagem', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e34'); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true'); ap.add_argument('--init-from', nargs=2, default=None, metavar=('JSON', 'BRACO'))
    ap.add_argument('--extra', type=int, default=2)
    a = ap.parse_args()
    E20.gerar_cidade = lambda seed, **kw: com_postos_extra(seed, a.extra, **kw)
    E20.BRACOS = [(f'direto, +{a.extra} postos', Reativo), (f'reacoes, +{a.extra} postos', ReativoReacoes)]
    E20.OUT = a.out
    E20.main(a)
