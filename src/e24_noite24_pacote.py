"""E24: o produto tanque x d_posto (ReativoNoite24) no mundo com dentes (doc 35, predicao 17).
    python src/e24_noite24_pacote.py --preset honesto --pena 5"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e20_corpo_fala as E20
from lab import Reativo, ReativoNoite24
E20.BRACOS = [('direto (Reativo)', Reativo), ('noite24 (tanque x d_posto)', ReativoNoite24)]
E20.OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e24'
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='honesto', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default=E20.OUT); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true')
    E20.main(ap.parse_args())
