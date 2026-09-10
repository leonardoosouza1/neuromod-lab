"""Envelope para a fila: roda scripts/analise_campo.py (regua pareada por semente, teste t) com flags nomeadas (a fila nao passa posicional).
Uso: --alvo <json> --ref linear --metrica fit [--mais <json> ...]. So le JSON; segundos."""
import sys, os, runpy
args = sys.argv[1:]; alvo = args[args.index('--alvo') + 1]; resto = [x for i, x in enumerate(args) if x != '--alvo' and (i == 0 or args[i-1] != '--alvo')]
if '--out' in resto: i = resto.index('--out'); resto = resto[:i] + resto[i + 2:]
# [10/09 astra] tira SO o par --out <dir>; antes descartava QUALQUER caminho e7* (o --mais da comparacao sumia em silencio)
sys.argv = ['analise_campo.py', alvo] + resto; runpy.run_path(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts', 'analise_campo.py'), run_name='__main__')
