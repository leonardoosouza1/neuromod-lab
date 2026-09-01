"""Bateria RAPIDA de validacao (~10 min): mega-lote de sementes + params leves.

    python src/rapido.py <experimento> [--mundo M]

Experimentos:
    e8        vida em fases (poda vs direto) — reproduz o achado do E8
    talamo    tálamo vs sempre vs cego vs poda
    sono      fixo vs constante vs circadiano (agua no radiador)
    <arq>     qualquer arquitetura solta vs reativo (baseline)

Preset LEVE (validado que separa o sinal do E8): P=1024, G=25, T_evo=350,
R=4, 3 sementes em MEGA-LOTE (as 3 populacoes num Lote so -> 2x). Nao substitui
a bateria cheia; serve pra decidir SE vale a pena rodar cheio.
"""
import sys, os, time, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import (DEV, NF, gerar_cidade, Cfg, ARQS, SerVital, SerTalamo, SerSono,
                 evoluir_sementes, rodar)

PRESET = dict(P=1024, G=25, T_evo=350, T_aval=1200, R=4, seeds=(0,1,2))

def variantes(exp):
    if exp == 'e8':
        return [type(f'V_{m}', (SerVital,), {'modo': m, 'nome': f'vida:{m}'})
                for m in ('direto','poda','curta')]
    if exp == 'talamo':
        return ([type(f'T_{s}', (SerTalamo,), {'submodo': s, 'nome': f'tal:{s}'})
                 for s in ('sempre','talamo','cego')]
                + [type('V_curta',(SerVital,),{'modo':'curta','NP':54,'nome':'poda:curta'})])
    if exp == 'sono':
        return [type(f'S_{m}', (SerSono,), {'submodo': m, 'nome': f'sono:{m}'})
                for m in ('fixo','constante','circadiano')]
    por = {A.nome: A for A in ARQS}
    if exp in por:
        return [ARQS[0], por[exp]]         # reativo baseline + a arq pedida
    sys.exit(f'experimento desconhecido: {exp}')

def main(exp, mundo):
    p = PRESET
    cfg = Cfg(1.0, mundo=mundo)
    if mundo == 'ruas': cfg.cron_alto = 3.5
    if exp == 'sono': cfg.com_agua = True; cfg.dia = 350
    treino = [gerar_cidade(s) for s in range(4)]
    teste  = [gerar_cidade(1000+s) for s in range(3)]
    arqs = variantes(exp)
    print(f'== RAPIDO {exp} mundo={mundo} | P={p["P"]} G={p["G"]} '
          f'T={p["T_evo"]} R={p["R"]} x{len(p["seeds"])} sementes (mega-lote) ==')
    t0 = time.time(); linhas = {}
    for A in arqs:
        champs = evoluir_sementes(A, treino, cfg, P=p['P'], ger=p['G'],
                                  T=p['T_evo'], seeds=p['seeds'], R=p['R'],
                                  verbose=False)
        vals = []
        for sd in p['seeds']:
            w = champs[sd][0]
            m = rodar(A, w[None,:].repeat(128,1), teste, cfg, T=p['T_aval'], seed=7777)
            f = (m.ent - 0.3*m.avar - getattr(m,'custo_neural',0.)).mean()
            vals.append(round(float(f),2))
        linhas[A.nome] = vals
        print(f'  {A.nome:<16} {sum(vals)/len(vals):6.2f}  amp {max(vals)-min(vals):.2f}  {vals}',
              flush=True)
    print(f'\nordem (fitness):')
    for k,v in sorted(linhas.items(), key=lambda x:-sum(x[1])/len(x[1])):
        print(f'  {k:<16} {sum(v)/len(v):6.2f}')
    print(f'TOTAL {time.time()-t0:.0f}s')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('exp')
    ap.add_argument('--mundo', default='base')
    a = ap.parse_args()
    main(a.exp, a.mundo)
