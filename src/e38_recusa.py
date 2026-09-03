"""E38: recusa de passageiro por fome (mecanica nova do mundo, gene nasce quase desligado), mundo +2 postos, semeado do campeao do E37.
Controle = E37b (mesmo pai + 60 ger. sem o gene): 9.20 / 0.15 / panes 3.7."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e20_corpo_fala as E20
from e34_posto_denso import com_postos_extra
from reacoes import ReativoReacoesRecusa
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='honesto', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e38'); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true'); ap.add_argument('--init-from', nargs=2, default=None, metavar=('JSON', 'BRACO'))
    ap.add_argument('--extra', type=int, default=2)
    a = ap.parse_args()
    E20.gerar_cidade = lambda seed, **kw: com_postos_extra(seed, a.extra, **kw)
    E20.BRACOS = [(f'reacoes + recusa por fome semeado, +{a.extra} postos', ReativoReacoesRecusa)]
    E20.OUT = a.out
    E20.main(a)
