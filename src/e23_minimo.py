"""E23: equacao minima que sobrevive (doc 37 §4). Reusa o runner do e20.
    python src/e23_minimo.py --preset triagem --pena 5"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e20_corpo_fala as E20
from lab import Reativo
from minimo import fabrica

K5  = ['d_alvo', 'd_posto', 'd_comida', 'e_fuel', 'e_fome']
K10 = K5 + ['custo_rua', 'congestao', 'e_dinheiro', 'e_temp', 'e_tem_pax']
E20.BRACOS = [('direto (Reativo, 26 termos)', Reativo),
              ('minimo 5 termos',            fabrica(K5)),
              ('minimo 10 termos',           fabrica(K10)),
              ('minimo 3 (d_alvo, d_posto, e_fuel)', fabrica(['d_alvo', 'd_posto', 'e_fuel']))]
E20.OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e23'
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='triagem', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default=E20.OUT); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true')
    E20.main(ap.parse_args())
