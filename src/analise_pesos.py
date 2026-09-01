"""Vitalidade de pesos EXATA — responde "o modelo usa quanto do cerebro?".

    python src/analise_pesos.py resultados/resultado-taxi-base-s2-*.json

A paisagem da bateria avalia cada ponto em mundos DIFERENTES -> ruido ~5
entregas engole a curvatura (pesos mortos aparecem "vivos"). Aqui: avaliacao
PAREADA — P=1 com semente fixa = exatamente os mesmos mundos para todos os
pontos. Peso morto da range EXATAMENTE 0. Custa ~2 min por arquitetura.
"""
import sys, os, json, glob, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import DEV, NF, gerar_cidade, Cfg, ARQS, avaliar

BLOCO = ['features']*18 + ['servico']*6 + ['memoria']*6 + ['corpo']*6
NOMES = (['d_alvo','custo_rua','congestao','semaforo',
          'd_posto','d_comida','d_descanso','d_oficina','d_loja',
          'e_fuel','e_fome','e_fadiga','e_pneu','e_temp','e_oleo',
          'e_dinheiro','e_tem_pax','bias']
         + ['sv_posto','sv_comida','sv_descanso','sv_oficina','sv_loja','sv_bias']
         + [f'mem_{i}' for i in range(6)] + [f'corpo_{i}' for i in range(6)])


def vitalidade(Arq, w, cfg, cidades, T=600, R=8, passos=7, raio=1.5, seed=4321):
    """range EXATO de fitness ao perturbar cada peso, mundos pareados."""
    base = avaliar(Arq, w[None,:], cidades, cfg, T, seed=seed, R=R).item()
    rngs = []
    for i in range(len(w)):
        vals = []
        for d in torch.linspace(-raio, raio, passos):
            if abs(float(d)) < 1e-9:
                vals.append(base); continue
            wp = w.clone(); wp[i] += float(d)
            vals.append(avaliar(Arq, wp[None,:], cidades, cfg, T, seed=seed, R=R).item())
        rngs.append(max(vals)-min(vals))
    return rngs, base


def analisar(caminho, mundo=None, n_cid=3, limiar=0.05):
    d = json.load(open(caminho))
    mundo = mundo or d['config'].get('mundo') or caminho.split('taxi-')[1].split('-s')[0]
    cfg = Cfg(1.0, trafego=.35, imposto=.18, mundo=mundo)
    cidades = [gerar_cidade(1000+s) for s in range(n_cid)]
    print(f'== {os.path.basename(caminho)} (mundo {mundo}) ==')
    print(f'{"arq":<13}{"features":>9}{"servico":>9}{"memoria":>9}{"corpo":>7}'
          f'{"total":>8}  top-3 criticos')
    res = {}
    for A in ARQS:
        if A.nome not in d['resultados']: continue
        w = torch.tensor(d['resultados'][A.nome]['pesos_finais'], device=DEV)
        rngs, base = vitalidade(A, w, cfg, cidades)
        viv = {}
        for b in ['features','servico','memoria','corpo']:
            idx = [i for i,x in enumerate(BLOCO) if x==b]
            viv[b] = (sum(1 for i in idx if rngs[i] > limiar), len(idx))
        tot = sum(1 for r in rngs if r > limiar)
        top = sorted(range(len(rngs)), key=lambda i:-rngs[i])[:3]
        tops = ', '.join(f'{NOMES[i]}({rngs[i]:.1f})' for i in top)
        linha = ''.join(f'{viv[b][0]:>4}/{viv[b][1]:<4}'
                        for b in ['features','servico','memoria','corpo'])
        print(f'{A.nome:<13}{linha}{tot:>4}/36  {tops}', flush=True)
        res[A.nome] = dict(ranges=[round(r,3) for r in rngs], fit_base=round(base,3))
    return res


if __name__ == '__main__':
    alvo = sys.argv[1] if len(sys.argv)>1 else 'resultados/resultado-taxi-base-s2-*.json'
    todos = {}
    for f in sorted(glob.glob(alvo)):
        todos[os.path.basename(f)] = analisar(f)
    saida = '/media/llm-data/universe-runs/neuromod-lab-taxi/vitalidade.json'
    json.dump(todos, open(saida,'w'))
    print('salvo:', saida)
