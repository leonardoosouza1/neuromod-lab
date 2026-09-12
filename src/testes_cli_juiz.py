"""CLI real: dois campeões, duas cópias, três ticks; exige GPU, sem mocks."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    import torch
    assert torch.cuda.is_available(), 'smoke exige GPU real'
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ, NM_COMPILE='0', NM_RISCO='1', NM_PONTO='1',
               NM_RETINA='0', NM_REGIME='0', HSA_OVERRIDE_GFX_VERSION='10.3.0')
    with tempfile.TemporaryDirectory() as pasta:
        p = Path(pasta)
        (p/'cenario.json').write_text(json.dumps({'mundo': {'L': 200, 'dias': .0125,
                                                         'horizonte': 'fixo', 'regua': 'vida'}}))
        (p/'campeoes.json').write_text(json.dumps({'bracos': {'linear': {'W': {
            '2': [0.] * 40, '7': [.1] * 40}}}}))
        cmd = [sys.executable, str(root/'src/julga_politica.py'), '--cenario', str(p/'cenario.json'),
               '--campeao', str(p/'campeoes.json'), '--politica', str(root/'politicas/linear_sem_ficar.py'),
               '--W-politica', 'campeao', '--seeds-evolucao', 'todas', '--seeds', '19',
               '--copias', '2', '--out', pasta]
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=90)
        assert result.returncode == 0, result.stderr
        d = json.loads((p/'julga.json').read_text())
        assert d['T'] == 3 and d['seeds_evolucao'] == ['2', '7']
        assert set(d['por_semente_evolucao']) == {'2', '7'}
        for registro in d['por_semente_evolucao'].values():
            assert len(registro['campeao']['fit_por_semente']) == 1
            assert registro['politica_res']['frac_teto'] == 1.
            assert registro['traco']['ficar_no_raio'] + registro['traco']['ficar_fora'] == 0.
        assert 'linear_campeao' not in d
    print('testes_cli_juiz: CLI real na GPU, dois campeões, passou')


if __name__ == '__main__': main()
