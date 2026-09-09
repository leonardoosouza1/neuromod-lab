"""[spec Mundo Vivo §4] PORTAO DO MUNDO: roda os portoes da casa contra um cenario.json e imprime PASSOU/FALHOU. Nenhuma bateria
entra na fila sem esta tabela verde. Portoes: identidade (testes_campo), determinismo (testes.py), sensibilidade+escala (testes_sentidos),
bloco (testes_bloco), vida (testes_vida), banda de controle (linear evoluido em fumaca no cenario: mortos em [0.40, 0.80]).
Perito (rodar.py --perito) e oraculo (diag_oraculo) nao aceitam cenario ainda: rodam no mundo padrao e sao informativos."""
import sys, os, re, json, subprocess, time, argparse
SRC = os.path.dirname(os.path.abspath(__file__)); PY = sys.executable
ap = argparse.ArgumentParser(); ap.add_argument('--cenario', default=os.path.join(os.path.dirname(SRC), 'cenarios', 'base.json')); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/portao'); ap.add_argument('--banda', type=float, nargs=2, default=[.40, .80])
ap.add_argument('--so', nargs='*', default=None); ap.add_argument('--tag', default=''); a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
ENV = {**os.environ, 'NM_RISCO': '1', 'NM_PONTO': '1', 'NM_COMPILE': os.environ.get('NM_COMPILE', '1')}
_cen = json.load(open(a.cenario)) if os.path.exists(a.cenario) else {}
if (_cen.get('mundo') or {}).get('retina'): ENV['NM_RETINA'] = '1'   # [revisao 09-09] o portao roda com as flags que o cenario pede
if (_cen.get('mundo') or {}).get('regime'): ENV['NM_REGIME'] = '1'
if a.so and 'escala' in a.so and 'sensibilidade' not in a.so: a.so = list(a.so) + ['sensibilidade']   # escala le o log do sensibilidade
def roda(args, timeout=1800):
    t0 = time.time(); r = subprocess.run([PY] + args, capture_output=True, text=True, env=ENV, timeout=timeout, cwd=SRC); out = (r.stdout + '\n' + r.stderr); return out, r.returncode, time.time() - t0
def julga(nome, out, rc, regras):
    """regras: lista de (padrao_regex, deve_existir). PASSOU se rc==0, sem Traceback, e todas as regras batem."""
    if rc != 0 or 'Traceback' in out: return False, 'erro de execucao'
    for pat, deve in regras:
        if bool(re.search(pat, out)) != deve: return False, f'regra {pat!r}'
    return True, ''
PORTOES = [
 ('identidade',     ['testes_campo.py'],     [(r'genes 0 == Linear \(compile\): True', True), (r'SEM SYNC', True), (r'SYNC!', False)]),
 ('determinismo',   ['testes.py'],           [(r'FALHOU|AssertionError', False)]),
 ('sensibilidade',  ['testes_sentidos.py'],  [(r'PORTAO SENTIDOS ok', True), (r'achado 84\): True', True)]),
 ('escala',         None,                    [(r'muda \d+% das decisoes OK', True), (r'muda \d+% das decisoes FALHOU', False)]),   # mesmo log do sensibilidade
 ('bloco',          ['testes_bloco.py'],     [(r'test_dof_bloco_soma: OK', True)]),
 ('vida',           ['testes_vida.py'],      [(r'FALHOU', False), (r'test_teto_avisa: .*OK', True)]),
 ('perito',         ['rodar.py', '--perito'], [(r'FALHOU|AssertionError', False)]),
]
res = {}; logs = {}
for nome, args, regras in PORTOES:
    if a.so and nome not in a.so: continue
    if args is None: out, rc, dt = logs.get('sensibilidade', ('', 1, 0.))
    else: out, rc, dt = roda([os.path.join(SRC, args[0])] + args[1:]); logs[nome] = (out, rc, dt)
    ok, mot = julga(nome, out, rc, regras); res[nome] = dict(passou=ok, motivo=mot, segundos=round(dt)); print(f'  {nome:<14} {"PASSOU" if ok else "FALHOU"} {mot} ({dt:.0f}s)', flush=True)
# banda de controle: linear evoluido em fumaca (P512, G25, 3 sementes) no cenario -> mortos medio
if not a.so or 'banda' in a.so:
    tag = f'_portao{a.tag}'; out, rc, dt = roda([os.path.join(SRC, 'e43_campo.py'), '--preset', 'fumaca', '--seeds', '0', '1', '2', '--so', 'linear', '--cenario', a.cenario, '--tag', tag, '--out', a.out], timeout=3600)
    m = re.search(r'^\s*linear\s+NP\s+\d+.*?mortos\s+(\d\.\d+)', out, re.M | re.S); mortos = float(m.group(1)) if m else None
    ok = mortos is not None and a.banda[0] <= mortos <= a.banda[1]; res['banda_controle'] = dict(passou=ok, mortos=mortos, banda=a.banda, segundos=round(dt))
    print(f'  {"banda_controle":<14} {"PASSOU" if ok else "FALHOU"} linear mortos {mortos} (banda {a.banda}) ({dt:.0f}s)', flush=True)
verde = all(r['passou'] for r in res.values()); json.dump(dict(cenario=a.cenario, portoes=res, verde=verde), open(os.path.join(a.out, f'portao{a.tag}.json'), 'w'), indent=1)
print(f'== PORTAO DO MUNDO: {"VERDE — pode enfileirar" if verde else "VERMELHO — nao enfileirar"} | {a.cenario} ==', flush=True)
