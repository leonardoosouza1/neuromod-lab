"""E25b: curiosidade na infancia (eps-exploracao de servicos) + aprender a ouvir (doc 38, pred 25)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e20_corpo_fala as E20
from lab import Reativo
from aprender_ouvir import fabrica
E20.MUNDO = dict(fome=.15, refeicao=90., comida_no_posto=True, fome_gracia=480)
E20.BRACOS = [('surdo + curioso eps.2 (eta=0)',    fabrica(2, eta_fixa=0., explora=0., eps_infancia=.2)),
              ('aprende eta=.1 + curioso eps.2',   fabrica(2, eta_fixa=.1, explora=0., eps_infancia=.2)),
              ('aprende eta=.3 + curioso eps.4',   fabrica(2, eta_fixa=.3, explora=0., eps_infancia=.4))]
E20.OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e25'
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='triagem', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default=E20.OUT); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true'); ap.add_argument('--init-from', nargs=2, default=None, metavar=('JSON', 'BRACO'))
    E20.main(ap.parse_args())
