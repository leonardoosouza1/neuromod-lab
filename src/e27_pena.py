"""E27: pena por morte FIXA vs PROPORCIONAL a vida perdida (doc 28 §7). Reusa o runner do e20.
    python src/e27_pena.py --preset triagem --pena 5 --prop"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e20_corpo_fala as E20
from lab import Reativo, ReativoNoite24
E20.BRACOS = [('direto (Reativo)', Reativo), ('noite24', ReativoNoite24)]
E20.OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e27'
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='triagem', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default=E20.OUT); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true'); ap.add_argument('--init-from', nargs=2, default=None, metavar=('JSON', 'BRACO'))
    ap.add_argument('--prop', action='store_true', help='pena proporcional a vida perdida')
    a = ap.parse_args()
    E20.MUNDO = dict(fome=.15, refeicao=90., comida_no_posto=True, pena_prop=a.prop)
    E20.main(a)
