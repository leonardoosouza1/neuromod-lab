"""Envelope para a fila: roda scripts/analise_campo.py (regua pareada por semente, teste t) com flags nomeadas (a fila nao passa posicional).
Uso: --alvo <json> --ref linear --metrica fit [--mais <json> ...]. So le JSON; segundos."""
import sys, os, runpy
args = sys.argv[1:]; alvo = args[args.index('--alvo') + 1]; resto = [x for i, x in enumerate(args) if x != '--alvo' and (i == 0 or args[i-1] != '--alvo')]
resto = [x for x in resto if x not in ('--out',) and not x.startswith('/media/llm-data/universe-runs/neuromod-lab-taxi/e7')] if '--out' in resto else resto
sys.argv = ['analise_campo.py', alvo] + resto; runpy.run_path(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts', 'analise_campo.py'), run_name='__main__')
