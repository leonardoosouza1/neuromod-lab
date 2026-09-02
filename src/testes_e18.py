"""Testes do E18 (avaliação honesta + fila).

    NM_COMPILE=0 python src/testes_e18.py

1. tabela() com um JSON sintético (sem GPU).
2. avaliar_honesto() com Reativo + perito_W, T pequeno, 2 conjuntos de 1
   cidade cada, R=8 — sem erro e com as chaves certas.
3. scripts/fila.sh com dois comandos: roda em SEQUÊNCIA (não em paralelo) e
   gera os .done na ordem certa.
"""
import sys, os, subprocess, tempfile, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import Cfg, Reativo
from rodar import perito_W
from avaliacao import avaliar_honesto, tabela, resumo_para_painel


def test_tabela_sintetica():
    d = {
        'arq': 'reativo',
        'conjuntos': [1000, 2000],
        'n_cid': 3,
        'por_conjunto_medio': {
            1000: {'fit': 8.17, 'mortos': 0.17},
            2000: {'fit': 5.29, 'mortos': 0.27},
        },
        'media': {'fit': 6.73, 'mortos': 0.22},
        'fit_por_semente': {1000: {0: 8.0, 1: 8.3}, 2000: {0: 5.2, 1: 5.4}},
        'mortos_por_semente': {1000: {0: 0.16, 1: 0.18}, 2000: {0: 0.25, 1: 0.29}},
    }
    md = tabela([d])
    assert 'reativo' in md, md
    assert '6.73' in md and '0.220' in md, md   # media
    assert '8.170' in md and '5.290' in md, md  # por conjunto
    md2 = tabela([d], por_semente=True)
    assert '[8.00 8.30]' in md2 or '[8.00' in md2, md2
    r = resumo_para_painel([d])
    assert r['bracos'][0]['nome'] == 'reativo'
    assert r['bracos'][0]['fit'] == 6.73
    assert r['bracos'][0]['n_sementes'] == 2
    # combinado (rodar_bracos): chave 'bracos' com 2 entradas
    combinado = {'bracos': {'braço a': d, 'braço b': d}}
    md3 = tabela([combinado])
    assert 'braço a' in md3 and 'braço b' in md3, md3
    print('  tabela()/resumo_para_painel() em JSON sintético  OK')


def test_avaliar_honesto():
    W = perito_W(Reativo.NP)
    cfg = Cfg(1.0, mundo='base')
    aval = avaliar_honesto(Reativo, {0: W}, cfg, T=300, conjuntos=(5000, 6000), n_cid=1, R=8)
    for chave in ('conjuntos', 'n_cid', 'R', 'por_conjunto', 'por_conjunto_medio',
                  'media', 'fit_por_semente', 'mortos_por_semente'):
        assert chave in aval, f'falta chave {chave}'
    assert aval['conjuntos'] == [5000, 6000]
    assert set(aval['por_conjunto_medio'].keys()) == {5000, 6000}
    for base in (5000, 6000):
        assert 0 in aval['por_conjunto'][base]
        assert 'fit' in aval['por_conjunto_medio'][base]
        assert 'mortos' in aval['por_conjunto_medio'][base]
    assert 'fit' in aval['media'] and 'mortos' in aval['media']
    fmed = (aval['por_conjunto_medio'][5000]['fit'] + aval['por_conjunto_medio'][6000]['fit']) / 2
    assert abs(aval['media']['fit'] - round(fmed, 4)) < 1e-6
    print(f'  avaliar_honesto(Reativo, perito, T=300, R=8, 2 conjuntos x1 cidade): '
          f'fit médio {aval["media"]["fit"]:.2f} mortos {aval["media"]["mortos"]:.3f}  OK')


def test_fila_sequencial():
    tmp = tempfile.mkdtemp(prefix='e18_fila_')
    try:
        combinado = os.path.join(tmp, 'combinado.txt')
        fila_txt = os.path.join(tmp, 'minha_fila.txt')
        with open(fila_txt, 'w') as fh:
            fh.write(f'passo1 | echo 1 >> {combinado}\n')
            fh.write(f'passo2 | echo 2 >> {combinado}\n')
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scripts', 'fila.sh')
        r = subprocess.run(['bash', script, fila_txt, '--out', tmp], capture_output=True, text=True)
        assert r.returncode == 0, f'fila.sh saiu com {r.returncode}:\n{r.stdout}\n{r.stderr}'
        assert os.path.exists(os.path.join(tmp, 'passo1.done'))
        assert os.path.exists(os.path.join(tmp, 'passo2.done'))
        assert os.path.exists(os.path.join(tmp, 'minha_fila_TUDO.done'))
        with open(os.path.join(tmp, 'passo1.done')) as fh: assert fh.read().startswith('FIM status=0')
        with open(os.path.join(tmp, 'passo2.done')) as fh: assert fh.read().startswith('FIM status=0')
        # ordem: passo1 escreveu ANTES de passo2 (sequencial, nao paralelo)
        with open(combinado) as fh:
            conteudo = fh.read().split()
        assert conteudo == ['1', '2'], f'ordem errada: {conteudo}'
        # done na ordem certa (mtime nao regride)
        t1 = os.path.getmtime(os.path.join(tmp, 'passo1.done'))
        t2 = os.path.getmtime(os.path.join(tmp, 'passo2.done'))
        t3 = os.path.getmtime(os.path.join(tmp, 'minha_fila_TUDO.done'))
        assert t1 <= t2 <= t3, f'ordem dos .done errada: {t1} {t2} {t3}'
        print('  scripts/fila.sh roda 2 comandos em sequencia e gera .done na ordem certa  OK')
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    print('--- testes E18 ---')
    test_tabela_sintetica()
    test_avaliar_honesto()
    test_fila_sequencial()
    print('ok')
