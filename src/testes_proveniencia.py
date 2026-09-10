"""Regressões do contrato experimental, executáveis sem GPU."""
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from proveniencia import manifesto, hash_config, valores_por_semente, valida_comparacao


class ProvenienciaTest(unittest.TestCase):
    def setUp(self):
        self.m = manifesto(SimpleNamespace(custo_gene=0., nevoa=float('inf')),
                           {'seeds': [1, 2]}, {}, {}, {'commit': 'abc'})
        self.a = dict(seeds=[1, 2], fit_por_semente=[10., 20.], manifesto=self.m)

    def test_hash_config_efetiva(self):
        m = copy.deepcopy(self.m)
        m['cfg']['custo_gene'] = .1
        self.assertNotEqual(hash_config(m), hash_config(self.m))
        json.dumps(self.m, allow_nan=False)

    def test_ids_invalidos(self):
        for seeds, values in (([1, 1], [1, 2]), ([1], [1, 2]), ([1, 2], [1, float('nan')])):
            with self.assertRaises(ValueError):
                valores_por_semente(dict(seeds=seeds, fit_por_semente=values), 'fit_por_semente')
        with self.assertRaises(ValueError):
            valores_por_semente(dict(fit_por_semente=[1, 2]), 'fit_por_semente')

    def test_diferencas_explicitas(self):
        b = copy.deepcopy(self.a)
        b['manifesto']['cfg']['custo_gene'] = .1
        with self.assertRaises(ValueError): valida_comparacao(self.a, b)
        valida_comparacao(self.a, b, ['cfg.custo_gene'])
        with self.assertRaises(ValueError): valida_comparacao(self.a, {})
        valida_comparacao(self.a, {}, legado=True)

    def test_cli_alinha_ids_e_rejeita_incompativeis(self):
        caminho = Path(__file__).resolve().parents[1] / 'scripts/analise_campo.py'
        spec = importlib.util.spec_from_file_location('analise', caminho)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        b = copy.deepcopy(self.a)
        b.update(seeds=[2, 1], fit_por_semente=[22., 11.])
        b['manifesto']['protocolo']['seeds'] = [2, 1]
        with tempfile.TemporaryDirectory() as pasta:
            p = Path(pasta) / 'resultado.json'
            p.write_text(json.dumps(dict(bracos=dict(linear=self.a, teste=b))))
            out = io.StringIO()
            with redirect_stdout(out): mod.analisa(str(p), metrica='fit')
            self.assertIn('+1.500', out.getvalue())
            self.assertIn('+7.853', out.getvalue())  # IC da diferença [1,2], não [12,-9]
            with self.assertRaises(ValueError): mod.analisa(str(p), ref='inexistente', metrica='fit')
            b['seeds'] = [2, 3]
            p.write_text(json.dumps(dict(bracos=dict(linear=self.a, teste=b))))
            with self.assertRaises(ValueError): mod.analisa(str(p), metrica='fit')

    def test_runner_tempos_e_backend_sem_simulacao(self):
        import torch
        from unittest.mock import patch
        with patch.object(torch.cuda, 'is_available', return_value=False):
            import e43_campo as runner
            medidas = dict(fit=1.123456789, ent=1., mortos=0., panes=0., fome_fim=0.,
                           agua_fim=0., dinh=0., res=0., litros_por_abast=0., n_posto=0.,
                           dof=0., metab=0.)

            def evolui(A, *args, seeds, **kw):
                return {sd: (torch.zeros(A.NP), [1], None) for sd in kw.get('pops', seeds)}

            for conjunto in (False, True):
                with tempfile.TemporaryDirectory() as pasta:
                    args = runner.parser().parse_args(['--out', pasta, '--so', 'linear',
                                                       '--seeds', '1', '2', '--motor', 'hip'])
                    args.seres_juntos = conjunto
                    args.otim = 'ga' if conjunto else 'es'
                    with patch.object(runner, 'gerar_mapa', return_value={}), \
                         patch.object(runner, 'medidas', return_value=medidas), \
                         patch.object(runner, 'evoluir', side_effect=evolui), \
                         patch.object(runner.lab, 'evoluir_es', side_effect=evolui), \
                         patch.object(runner, 'relogio', side_effect=map(float, range(30))), \
                         patch.object(runner, 'identidade_codigo', return_value={'commit': 'test'}), \
                         redirect_stdout(io.StringIO()):
                        runner.main(args)
                    d = json.loads((Path(pasta) / 'e43.json').read_text())
                    b = d['bracos']['linear']
                    self.assertEqual(b['motor'], 'torch')
                    self.assertEqual(b['fit_por_semente'], [1.123456789] * 2)
                    self.assertEqual(b['tempos']['avaliacao_s'], 1.)
                    self.assertEqual(b['tempos']['evolucao_s'], None if conjunto else 1.)
                    self.assertEqual(d['tempos']['evolucao_conjunta_s'], 1. if conjunto else 0.)
                    self.assertEqual(b['config_hash'], hash_config(b['manifesto']))


if __name__ == '__main__':
    # [10/09 opus ciclo 3] o daemon da fila SEMPRE acrescenta `--out <dir>`; unittest.main() parseia sys.argv e morre
    # com exit 2 ANTES de rodar um teste — foi o que aconteceu com g0a (0 s, 'unrecognized arguments: --out') e a fila
    # seguiu adiante: portao VERDE FALSO. Descarta os flags do runner e roda os testes.
    import sys
    for _f in ('--out', '--tag'):
        while _f in sys.argv:
            _i = sys.argv.index(_f); del sys.argv[_i:_i + 2]
    unittest.main()
