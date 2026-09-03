"""E25: infancia individual — a fome nao fere nos primeiros `fome_gracia` passos de cada vida (doc 38, pred 18).
    python src/e25_infancia.py --preset triagem --pena 5"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e20_corpo_fala as E20
from lab import Reativo
from corpo_fala import fabrica as fabrica_corpo
from aprender_ouvir import fabrica
E20.MUNDO = dict(fome=.15, refeicao=90., comida_no_posto=True, fome_gracia=480)
E20.BRACOS = [('direto (Reativo)',                 Reativo),
              ('surdo (corpo fala, eta=0)',        fabrica(2, eta_fixa=0., explora=0.)),
              ('aprende a ouvir eta=.1',           fabrica(2, eta_fixa=.1)),
              ('teto: codigo herdado dos 2 lados', fabrica_corpo(2, prior_corpo=True, prior_cerebro=True))]
E20.OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e25'
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='triagem', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default=E20.OUT); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true')
    E20.main(ap.parse_args())
