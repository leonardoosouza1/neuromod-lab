"""E29c: log so nos sinais do corpo (Weber-Fechner onde faz sentido; distancias lineares). Reusa o runner do e20."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e20_corpo_fala as E20
from quimico import ReativoLogCorpo
E20.BRACOS = [('log corpo (Weber-Fechner so no corpo)', ReativoLogCorpo)]
E20.OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e29'
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='triagem', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default=E20.OUT); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true'); ap.add_argument('--init-from', nargs=2, default=None, metavar=('JSON', 'BRACO'))
    E20.main(ap.parse_args())
