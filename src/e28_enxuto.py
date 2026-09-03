"""E28: genoma enxuto vs completo vs minimo-3, honesto (doc 28 §7, predicao 21). Reusa o runner do e20."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e20_corpo_fala as E20
from lab import Reativo
from enxuto import ReativoEnxuto
from minimo import fabrica
E20.BRACOS = [('direto (Reativo, 44 genes)', Reativo), ('enxuto (32 genes)', ReativoEnxuto),
              ('minimo 3 (d_alvo, d_posto, e_fuel)', fabrica(['d_alvo', 'd_posto', 'e_fuel']))]
E20.OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e28'
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='honesto', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default=E20.OUT); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true')
    E20.main(ap.parse_args())
