"""Contrato do carregador: independência de estado, sem simulação/GPU."""
import ast
import copy
import inspect
from pathlib import Path
import re
from types import SimpleNamespace
import unittest
from unittest.mock import mock_open, patch


class EstadoPoliticaTest(unittest.TestCase):
    def test_instancias_independentes(self):
        tree = ast.parse(Path(__file__).with_name('politica_util.py').read_text())
        nodes = [n for n in tree.body if
                 (isinstance(n, ast.FunctionDef) and n.name == 'carrega') or
                 (isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PROIBIDO' for t in n.targets))]
        ns = dict(re=re, copy=copy, inspect=inspect, DEV='cpu', G=9, S=10, NF=29,
                  NOMES_OP=[], NOMES_CORPO=[], Linear=SimpleNamespace(NP=40),
                  torch=SimpleNamespace(set_default_device=lambda _: None))
        exec(compile(ast.Module(body=nodes, type_ignores=[]), 'carrega', 'exec'), ns)
        for retorno in ('P', 'P()'):
            src = 'def fabrica():\n    class P:\n        def __init__(self): self.mem = []\n    return ' + retorno + '\n'
            with self.subTest(retorno=retorno), patch('builtins.open', mock_open(read_data=src)):
                cls, erro = ns['carrega']('fixture')
                self.assertIsNone(erro)
                a, b = cls(), cls()
                a.p.mem.append(3)
                self.assertEqual(b.p.mem, [])
                self.assertIsNot(a.p, b.p)
            with patch('builtins.open', side_effect=AssertionError('não reler fonte')):
                cls, erro = ns['carrega']('fixture', fonte=src)
                self.assertIsNone(erro)


if __name__ == '__main__': unittest.main()
