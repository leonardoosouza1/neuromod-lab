"""E33: pane mais cara (D_PANE 6 -> 12 / 20) com o reflexo de emergencia: o preco da pane muda o portao evoluido?
Uso: --dpane 12. Reusa o runner do e20 (MUNDO sobrescrito)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e20_corpo_fala as E20
from reacoes import ReativoReacoes
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='triagem', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e33'); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true')
    ap.add_argument('--dpane', type=float, default=12.)
    a = ap.parse_args()
    E20.MUNDO = dict(E20.MUNDO, D_PANE=a.dpane)
    E20.BRACOS = [(f'reacoes, pane custa {a.dpane:.0f}', ReativoReacoes)]
    E20.OUT = a.out
    E20.main(a)
