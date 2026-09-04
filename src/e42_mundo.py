"""E42 (doc 42): a CIDADE GRANDE — direto x reacoes x minimo-3 (molde do e34).

Mesmo runner do E20 (mundo do pacote E19d), trocando o gerador de cidade por
`cidade_grande.gerar_cidade_grande` (n nos, conexo, d_posto <= 6 saltos) e a
cfg por `cidade_grande.cfg_cidade_grande` (D distritos, moradia, hotel,
passageiro que cruza distrito, tarifa pelo distrito de origem). O teste-seed
(1000+) gera cidades grandes pela MESMA regra.

    export TORCHINDUCTOR_COMPILE_THREADS=1 OMP_NUM_THREADS=4 MKL_NUM_THREADS=4
    # fumaca (o que rodou no doc 42):
    nice -n 5 python src/e42_mundo.py --preset triagem --P 256 --G 10 \
        --T-evo 600 --R 1 --seeds 0 --n 104 --tag _fumaca104
    # bateria honesta: SO depois do merge, na fila (scripts/fila2.sh)
    nice -n 5 python src/e42_mundo.py --preset honesto --n 104

Predicao 49 (doc 42, registrada ANTES de qualquer bateria): na cidade grande o
minimo-3 perde >= 1.0 de fit pro cerebro completo.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e20_corpo_fala as E20
from lab import Reativo
from reacoes import ReativoReacoes
from minimo import fabrica
from cidade_grande import (gerar_cidade_grande, cfg_cidade_grande, telemetria_grande,
                           n_distritos, resumo_cidade, tabela_distritos, OUT)

MIN3 = ['d_alvo', 'd_posto', 'e_fuel']

if __name__ == '__main__':
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument('--preset', default='triagem', choices=('triagem', 'honesto'))
    ap.add_argument('--out', default=OUT); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None); ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000); ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true')
    ap.add_argument('--init-from', nargs=2, default=None, metavar=('JSON', 'BRACO'))
    ap.add_argument('--n', type=int, default=104, help='nos por cidade (104 | 250 | 500)')
    ap.add_argument('--D', type=int, default=None, help='distritos (default: round(6*sqrt(n/104)))')
    ap.add_argument('--P', type=int, default=None); ap.add_argument('--G', type=int, default=None)
    ap.add_argument('--T-evo', type=int, default=None); ap.add_argument('--T-aval', type=int, default=None)
    ap.add_argument('--sem-moradia', action='store_true', help='controle: cidade grande SEM moradia/hotel')
    a = ap.parse_args()

    D = a.D or n_distritos(a.n)
    # o gerador e a cfg da rodada (o E20.main chama os dois pelos nomes do modulo)
    E20.gerar_cidade = lambda seed, **kw: gerar_cidade_grande(seed, n=a.n, **kw)
    E20.cfg_pacote = lambda **kw: cfg_cidade_grande(n=a.n, D=D, moradia=not a.sem_moradia,
                                                    pax_cruza=0. if a.sem_moradia else .30,
                                                    tarifa_distrito=not a.sem_moradia,
                                                    rua_nao_dorme=not a.sem_moradia, **kw)
    E20.MUNDO = dict(fome=.15)          # o resto do pacote ja e default do cfg_cidade_grande
    E20.telemetria = telemetria_grande
    E20.BRACOS = [('direto (Reativo)',   Reativo),
                  ('reacoes',            ReativoReacoes),
                  ('minimo 3 (d_alvo, d_posto, e_fuel)', fabrica(MIN3))]
    E20.OUT = a.out
    if a.P or a.G or a.T_evo or a.T_aval:   # fumaca: presets menores sem tocar no E20
        for nome, p in (('PRESET', E20.PRESET), ('PRESET_TRIAGEM', E20.PRESET_TRIAGEM)):
            for k, v in (('P', a.P), ('G', a.G), ('T_evo', a.T_evo), ('T_aval', a.T_aval)):
                if v: p[k] = v

    aliq, pmul, alug = tabela_distritos(D, 0)
    cids = [gerar_cidade_grande(s, n=a.n) for s in range(1)]
    print(f'== E42 cidade grande | n={a.n} D={D} | {resumo_cidade(cids[0], D)}', flush=True)
    print(f'   aliquotas {aliq}\n   precos    {pmul}\n   aluguel   {alug}', flush=True)
    E20.main(a)
