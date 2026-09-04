"""E41: a regua muda o que emerge — tres fitness alternativas (A sobrevive-primeiro, B bem-estar integral, C Pareto de 4 objetivos)
semeadas do campeao do E37 (5 postos), controle = E37b (regua padrao, mesmo pai + 60 ger.). Uso: --fitness sobrevive|bemestar|pareto"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e20_corpo_fala as E20
from e34_posto_denso import com_postos_extra
from reacoes import ReativoReacoes
if __name__ == '__main__':
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='honesto', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e41'); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true'); ap.add_argument('--init-from', nargs=2, default=None, metavar=('JSON', 'BRACO'))
    ap.add_argument('--extra', type=int, default=2); ap.add_argument('--fitness', default='sobrevive', choices=('padrao', 'sobrevive', 'bemestar', 'pareto'))
    a = ap.parse_args()
    _orig = E20.cfg_pacote
    def _cfg(**kw):
        c = _orig(**kw); c.fitness = a.fitness; return c
    E20.cfg_pacote = _cfg
    E20.gerar_cidade = lambda seed, **kw: com_postos_extra(seed, a.extra, **kw)
    E20.BRACOS = [(f'regua {a.fitness}, reacoes semeado, +{a.extra} postos', ReativoReacoes)]
    E20.OUT = a.out
    E20.main(a)
