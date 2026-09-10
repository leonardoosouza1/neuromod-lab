#!/usr/bin/env python3
"""analise_campo.py — regua honesta PAREADA para as baterias do campo (E43/E44).

Cada braco de uma bateria roda com as MESMAS sementes de evolucao (--seeds 0 1 2 3 4).
O JSON guarda `mortos_por_semente` e `fit_por_semente`. Comparar so as MEDIAS joga fora
o pareamento: a variancia entre sementes entra duas vezes. Este script:

  1. compara cada braco com um braco de referencia pela DIFERENCA por semente
     (t pareado + IC95 de Student);
  2. estima a DP entre sementes e o menor efeito detectavel (MDE) do protocolo,
     pareado e nao pareado, para 80 % de poder e alfa .05 bilateral;
  3. valida IDs de sementes e diferenças declaradas de configuração.

O IC de Student depende das hipóteses do teste; n pequeno não as garante.
MDE é uma aproximação de planejamento; p-valores não corrigem múltiplos testes.

USO
  python analise_campo.py RESULTADO.json [--ref linear] [--metrica mortos]
  python analise_campo.py DIR/            # varre todos os e43_*.json do diretorio
"""
import argparse, glob, json, os, sys
import numpy as np
from scipy import stats
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
from proveniencia import valores_por_semente, valida_comparacao

def mde(sd_dif, n, poder=.80, alfa=.05):
    """menor efeito detectavel (mesma unidade da metrica) para um teste pareado."""
    return (stats.t.ppf(1 - alfa/2, n-1) + stats.t.ppf(poder, n-1)) * sd_dif / np.sqrt(n)

def carrega(caminho):
    with open(caminho) as arquivo:
        d = json.load(arquivo)
    bracos = {}
    for nome, v in d.get('bracos', {}).items():
        bracos[nome] = v
    return d, bracos

def analisa(caminho, ref=None, metrica='mortos', mais=(), variar=(), legado=False):
    d, bracos = carrega(caminho)
    for outro in mais:   # [E65] bracos de OUTROS arquivos (mesmas sementes/mundos de teste) entram pareados, com o nome do arquivo
        tag = os.path.basename(outro).replace('e43', '').replace('.json', '')
        for nome, v in carrega(outro)[1].items(): bracos[f'{nome} @{tag}'] = v
    chave = f'{metrica}_por_semente'
    tem = {k: valores_por_semente(v, chave) for k, v in bracos.items() if chave in v}
    if legado:
        print('AVISO: modo legado assume comparabilidade onde falta manifesto; IDs continuam obrigatorios.')
    if not tem:
        print(f'{os.path.basename(caminho)}: sem {chave}'); return
    if ref is not None and ref not in tem:
        raise ValueError(f'referencia inexistente: {ref}')
    if ref is None:
        ref = 'linear' if 'linear' in tem else list(tem)[0]
    ids = sorted(tem[ref])
    x = np.array([tem[ref][sd] for sd in ids]); n = len(x)
    alinhados = {ref: x}
    for nome, valores in tem.items():
        if nome == ref: continue
        if set(valores) != set(ids):
            raise ValueError(f'{nome}: conjunto de sementes diferente da referencia')
        valida_comparacao(bracos[ref], bracos[nome], variar, legado)
        alinhados[nome] = np.array([valores[sd] for sd in ids])
    if variar:
        print('Diferencas autorizadas: ' + ', '.join(variar))
    print(f'\n=== {os.path.basename(caminho)}  |  metrica={metrica}  ref={ref}  n={n} ===')
    print(f'{"braco":42s} {"media":>7s} {"DP sem.":>8s} {"dif":>8s} {"IC95":>18s} {"p":>8s}')
    print(f'{ref:42s} {x.mean():7.3f} {x.std(ddof=1):8.3f}')
    for nome, y in alinhados.items():
        if nome == ref: continue
        if len(y) != n:
            print(f'{nome:42s} {y.mean():7.3f} {y.std(ddof=1):8.3f}   (n={len(y)} != {n}: nao pareavel)'); continue
        dif = y - x
        t, p = stats.ttest_rel(y, x)
        lo, hi = stats.t.interval(.95, n-1, loc=dif.mean(), scale=stats.sem(dif)) if dif.std(ddof=1) > 0 else (dif.mean(), dif.mean())
        flag = ''
        print(f'{nome:42s} {y.mean():7.3f} {y.std(ddof=1):8.3f} {dif.mean():+8.3f} [{lo:+7.3f},{hi:+7.3f}] {p:8.4f}{flag}')
    # regua do protocolo: DP da diferenca pareada mediana entre todos os pares
    difs = [np.std(a-b, ddof=1) for i, a in enumerate(alinhados.values()) for b in list(alinhados.values())[i+1:] if len(a) == len(b)]
    if difs:
        sd = float(np.median(difs))
        print(f'\nregua deste protocolo (DP da diferenca pareada = {sd:.3f}):')
        for k in (3, 5, 8, 12):
            print(f'  n={k:2d}: detecta diferenca >= {mde(sd, k):.3f}')

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('alvo'); ap.add_argument('--ref', default=None)
    ap.add_argument('--metrica', default='mortos', choices=['mortos', 'fit', 'panes', 'ent', 'dinh', 'res'])
    ap.add_argument('--mais', nargs='*', default=(), help='[E65] outros JSONs com as MESMAS sementes: bracos entram pareados')
    ap.add_argument('--variar', nargs='*', default=(), help='caminhos do manifesto cuja diferenca e intencional, ex.: cfg.custo_gene flags.custo_gene')
    ap.add_argument('--legado', action='store_true', help='assume comparabilidade de resultados antigos sem manifesto; exige IDs de sementes')
    a = ap.parse_args()
    alvos = sorted(glob.glob(os.path.join(a.alvo, 'e4*.json'))) if os.path.isdir(a.alvo) else [a.alvo]
    try:
        for c in alvos: analisa(c, a.ref, a.metrica, a.mais, a.variar, a.legado)
    except ValueError as erro:
        ap.error(str(erro))
