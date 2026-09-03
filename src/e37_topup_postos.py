"""E37: mundo com +2 postos, semeado do campeao do E34 — controle (reacoes) vs reacoes + portao de abastecer.
Evolucao cumulativa: nasce do melhor pai no melhor mundo."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e20_corpo_fala as E20
from e34_posto_denso import com_postos_extra
from reacoes import ReativoReacoes, ReativoReacoesTopUp
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='triagem', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e37'); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true'); ap.add_argument('--init-from', nargs=2, default=None, metavar=('JSON', 'BRACO'))
    ap.add_argument('--extra', type=int, default=2)
    a = ap.parse_args()
    E20.gerar_cidade = lambda seed, **kw: com_postos_extra(seed, a.extra, **kw)
    E20.BRACOS = [(f'controle: reacoes semeado, +{a.extra} postos', ReativoReacoes), (f'reacoes + abastecer semeado, +{a.extra} postos', ReativoReacoesTopUp)]
    E20.OUT = a.out
    E20.main(a)
