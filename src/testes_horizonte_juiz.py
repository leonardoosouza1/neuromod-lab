"""Contrato de orquestração de mundo(): sem executar mapas ou kernels."""
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import unittest


class HorizonteJuizTest(unittest.TestCase):
    def test_horizonte_retornado_igual_configurado(self):
        # Extrai a função real para testar o contrato sem importar módulos GPU.
        source = Path(__file__).with_name('politica_util.py').read_text()
        function = next(n for n in ast.parse(source).body
                        if isinstance(n, ast.FunctionDef) and n.name == 'mundo')
        for horizonte, teto, dias, esperado in (
            ('aberto', 7200, 10, 7200), ('aberto', None, 10, 7200),
            ('fixo', 7200, 10, 2400), ('fixo', None, 2, 480),
        ):
            with self.subTest(horizonte=horizonte, teto=teto, dias=dias):
                def aplicar(flags, cenario):
                    flags.horizonte, flags.T_max, flags.dias = horizonte, teto, dias
                    return dict(perfis=None, K=None, ruas=None)

                namespace = dict(
                    json=json, hashlib=hashlib,
                    parser=lambda: SimpleNamespace(parse_args=lambda _: SimpleNamespace()),
                    aplica_cenario=aplicar,
                    cfg_de_flags=lambda flags, extras, T: SimpleNamespace(T_max=T),
                    gerar_mapa=lambda seed, **kwargs: seed,
                )
                exec(compile(ast.Module(body=[function], type_ignores=[]), 'politica_util.mundo', 'exec'), namespace)
                cfg, mapas, T, _ = namespace['mundo']()
                self.assertEqual((T, cfg.T_max), (esperado, esperado))
                self.assertEqual(mapas, [1000, 1001, 1002])


if __name__ == '__main__':
    unittest.main()
