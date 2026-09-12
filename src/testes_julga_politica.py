"""Testes da orquestração do juiz; simulador substituído, sem teste de física."""
import argparse
import ast
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from contextlib import redirect_stdout
import io
import hashlib
import math
import copy


class JuizTest(unittest.TestCase):
    def setUp(self):
        tree = ast.parse(Path(__file__).with_name('julga_politica.py').read_text())
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        class Vetor(list):
            def numel(self): return len(self)
        self.calls = []
        self.cfg = SimpleNamespace(horizonte='aberto', GUINCHO=10, FUEL_POS_PANE=5,
                                   KCAL_PANE=8, dinh0=10, nevoa=20, retina=None, regime=None)
        self.cfg_braco = SimpleNamespace(talamo_norm='fixo')
        self.arq = SimpleNamespace(NP=2)
        def mede(arq, w, cfg, mapas, T, seeds, copias):
            self.calls.append((arq, list(w), cfg, T, seeds, copias))
            return {'mortos': 0., 'rec': sum(w), 'rec_por_semente': [sum(w)] * len(seeds)}
        def manifesto(cfg, protocolo, mapas, flags, codigo):
            return {'cfg': vars(cfg), 'protocolo': protocolo, 'mapas': mapas,
                    'flags': flags, 'codigo': codigo,
                    'ambiente': {'NM_COMPILE': '0'}}
        def normaliza(v):
            if isinstance(v, dict): return {str(k): normaliza(x) for k, x in v.items()}
            if isinstance(v, (list, tuple)): return [normaliza(x) for x in v]
            return v
        def identidade_codigo(root): return {'commit': None, 'fontes_sha256': 'fake'}
        def hash_config(v): return hashlib.sha256(json.dumps(normaliza(v), sort_keys=True).encode()).hexdigest()
        self.ns = dict(argparse=argparse, json=json, os=os, __file__=str(Path(__file__).with_name('julga_politica.py')), DEV='cpu',
                       hashlib=hashlib, math=math, copy=copy,
                       torch=SimpleNamespace(tensor=lambda w, **kw: Vetor(w), zeros=lambda n, **kw: Vetor([0]*n)),
                       Linear=SimpleNamespace(NP=2),
                       mundo=lambda *a, **kw: (self.cfg, [], 7200, 'key'),
                       braco=lambda *a: (self.arq, self.cfg_braco),
                       manifesto=manifesto, normaliza=normaliza, hash_config=hash_config,
                       identidade_codigo=identidade_codigo,
                       carrega=lambda p: ('politica', None),
                       alinha_semente=lambda w, nomes: w,
                       mede=mede, traco=lambda *a, **kw: {}, linha=lambda *a: '')
        exec(compile(ast.Module(body=functions, type_ignores=[]), 'julga_politica', 'exec'), self.ns)

    def test_ids(self):
        selecionar = self.ns['seleciona_sementes']
        self.assertEqual(selecionar({'2': [], '7': []}, ['todas']), ['2', '7'])
        for ids in ([], ['0'], ['2', '2']):
            with self.assertRaises(ValueError): selecionar({'2': []}, ids)

    def run_juiz(self, args):
        with tempfile.TemporaryDirectory() as pasta:
            bateria = Path(pasta)/'campeoes.json'
            bateria.write_text(json.dumps({'bracos': {'linear': {'W': {'2': [1, 2], '7': [4, 5]}}}, 'nomes_f': ['a', 'b']}))
            (Path(pasta)/'fixture').write_text('')
            with redirect_stdout(io.StringIO()):
                politica = Path(pasta) / 'fixture'
                res = self.ns['main'](['--campeao', str(bateria), '--out', pasta,
                                       '--politica', str(politica), '--seeds', '19', '23'] + args)
            self.assertEqual(json.loads((Path(pasta)/'julga.json').read_text()), res)
            return res

    def test_todos_genomas_e_seeds_ambientais(self):
        res = self.run_juiz(['--seeds-evolucao', 'todas', '--W-politica', 'campeao'])
        self.assertEqual(res['seeds_evolucao'], ['2', '7'])
        self.assertEqual(res['seeds_ambientais'], [19, 23])
        self.assertNotIn('linear_campeao', res)
        self.assertEqual([c[1] for c in self.calls], [[1, 2], [1, 2], [4, 5], [4, 5]])
        self.assertEqual(self.calls[0][2].corte_vivos, 0.)
        self.assertFalse(self.calls[0][2].jardim_comum)
        self.assertEqual(self.calls[1][2].corte_vivos, 0.)
        self.assertFalse(self.calls[1][2].jardim_comum)
        self.assertTrue(all(c[3] == 7200 and c[4] == [19, 23] for c in self.calls))

    def test_legado_e_politica_zero(self):
        res = self.run_juiz(['--seeds-evolucao', '7'])
        self.assertEqual(res['linear_campeao']['rec'], 9)
        self.assertEqual(self.calls[1][1], [0, 0])

    def test_id_ausente_falha_antes_simulacao(self):
        with self.assertRaises(ValueError): self.run_juiz(['--seeds-evolucao', '0'])
        self.assertEqual(self.calls, [])

    def test_genoma_invalido_no_ultimo_falha_antes_de_medir(self):
        original = self.ns['json'].load
        def load(handle):
            dado = original(handle)
            if 'campeoes' in str(handle.name): dado['bracos']['linear']['W']['7'] = [4, float('nan')]
            return dado
        self.ns['json'].load = load
        try:
            with self.assertRaises(ValueError): self.run_juiz(['--seeds-evolucao', 'todas'])
            self.assertEqual(self.calls, [])
        finally:
            self.ns['json'].load = original

    def test_manifesto_muda_com_parametro(self):
        a = self.run_juiz(['--seeds-evolucao', '7'])
        b = self.run_juiz(['--seeds-evolucao', '7', '--nevoa', '3'])
        self.assertNotEqual(a['manifesto']['flags'], b['manifesto']['flags'])
        self.assertEqual(a['status'], 'concluido')

    def test_falha_no_traco_preserva_parcial(self):
        original = self.ns['traco']
        self.ns['traco'] = lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError('traco'))
        with tempfile.TemporaryDirectory() as pasta:
            bateria = Path(pasta) / 'campeoes.json'
            bateria.write_text(json.dumps({'bracos': {'linear': {'W': {'2': [1, 2]}}}, 'nomes_f': ['a', 'b']}))
            politica = Path(pasta) / 'fixture'; politica.write_text('')
            with self.assertRaises(RuntimeError):
                self.ns['main'](['--campeao', str(bateria), '--out', pasta,
                                 '--politica', str(politica), '--seeds-evolucao', '2'])
            parcial = json.loads((Path(pasta) / 'julga.json').read_text())
            self.assertEqual(parcial['status'], 'parcial')
            self.assertIn('campeao', parcial['por_semente_evolucao']['2'])
            self.assertIn('politica_res', parcial['por_semente_evolucao']['2'])
        self.ns['traco'] = original


if __name__ == '__main__': unittest.main()
