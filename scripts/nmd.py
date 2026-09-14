#!/usr/bin/env python3
"""nmd.py — daemon de baterias do neuromod-lab. Roda NO HOST (onde a GPU existe) e
executa pedidos que aparecem numa pasta compartilhada. É o canal entre a sessão do
Claude Science (que não alcança /dev/kfd) e a RX 6750 XT.

    python3 nmd.py                      # começa a atender
    python3 nmd.py --uma-vez            # atende o que está na fila e sai
    touch <spool>/PARE                  # para de aceitar novos (termina o atual)

MODELO DE SEGURANÇA — leia antes de subir
  O spool é um diretório em disco: quem escreve nele manda trabalho para a sua GPU.
  Por isso o daemon NUNCA executa string de comando. Ele recebe um pedido declarativo
  (script + argumentos tipados), valida contra uma LISTA BRANCA e reconstrói o argv
  ele mesmo, com subprocess sem shell. O que não está na lista é recusado e o pedido
  vai para `recusados/` com o motivo. Nada de `rm`, nada de caminho fora da base,
  nada de env fora da lista, um job por vez (nunca dois na GPU).

PEDIDO (JSON em <spool>/pedidos/<id>.json)
  {"id":"e63c", "script":"e43_campo", "out":"e63",
   "env":{"NM_RISCO":"1"},
   "args":{"preset":"honesto","G":120,"R":8,"seeds":[0,1,2,3,4],"L":200,"dias":15,
           "fitness":"riqueza","mundo":"distinto","nevoa":25,
           "so":["linear","bilinear risco (esc 3)"],"tag":"_e63_nev_25"}}

RESPOSTA
  <spool>/estado/<id>.json    heartbeat: fase, pid, geração corrente, melhor fitness
                              por semente, braço em curso, segundos, e no fim o
                              estado final + caminho dos JSONs de resultado
  <spool>/log/<id>.log        stdout+stderr da bateria
  <spool>/feitos/<id>.json    o pedido, arquivado, quando termina
"""
import argparse, hashlib, json, os, re, shutil, signal, subprocess, sys, threading, time
from datetime import datetime, timezone

REPO  = '/home/leonardo/projects/LLM/neuromod-lab'
PY    = '/home/leonardo/projects/LLM/.venv-rocm/bin/python'
BASE  = '/media/llm-data/universe-runs/neuromod-lab-taxi'
SPOOL = os.path.join(BASE, '_nmd')

SCRIPTS = {'rodar', 'e43_campo', 'e44_prefeito', 'diag_oraculo', 'autopsia', 'testes_campo', 'testes_bilinear', 'testes_completo', 'perf_varredura', 'perf_perfil',
           'retrato_cerebro', 'base_fechada', 'ablacao_mem', 'testes', 'testes_sentidos'}
ENVS    = {'NM_REGIME', 'NM_RETINA', 'NM_PONTO', 'NM_RISCO', 'NM_COMPILE', 'HSA_OVERRIDE_GFX_VERSION', 'OMP_NUM_THREADS',
           'TORCHINDUCTOR_COMPILE_THREADS', 'MKL_NUM_THREADS'}
FLAG    = re.compile(r'^[A-Za-z][A-Za-z0-9-]{0,24}$')          # nome de flag
VALOR   = re.compile(r'^[\w .,()+=/-]{1,120}$')          # valor textual: sem metacaractere de shell
LIVRE   = re.compile(r'e4[0-9]_campo\.py|e44_prefeito\.py|diag_oraculo\.py')   # o que conta como "GPU ocupada"
# [12/09] parallel slots: scripts that leave the GPU mostly idle (gpu_evolve: ~0.4 CPU core, GPU waiting on host
# readbacks, 28 W) may run several at once. Loaded from _nmd/parallel.json ({"script": slots}); hot-reload like the
# whitelist. Anything not listed keeps the historical rule: one process on the GPU at a time.
PARALLEL = {'universe_run': 4}

def parallel_slots(script):
    """Max concurrent instances of `script`, or 0 when the script is EXCLUSIVE (not listed in
    parallel.json / PARALLEL): an exclusive job needs an empty GPU and blocks everything else.
    Listed scripts coexist with each other (e.g. 4 gpu_evolve + 1 torch fly test) — 14/09."""
    global PARALLEL
    pj = os.path.join(SPOOL, 'parallel.json')
    if os.path.exists(pj):
        try: PARALLEL = {str(k): int(v) for k, v in json.load(open(pj)).items()}
        except Exception as ex: print(f'[nmd] parallel.json ignored: {ex}', flush=True)
    return int(PARALLEL.get(script, 0))


def can_start(script, running):
    """Scheduling rule (pure, unit-testable): `running` = list of running script names."""
    slots = parallel_slots(script)
    if not running: return True
    if slots <= 0: return False                                  # exclusive: wait for an empty GPU
    if any(parallel_slots(r) <= 0 for r in running): return False   # an exclusive job holds the GPU
    return sum(1 for r in running if r == script) < slots

def agora(): return datetime.now(timezone.utc).isoformat(timespec='seconds')

def valida(p):
    """Devolve (argv, env, out_dir) ou levanta ValueError com o motivo."""
    global SCRIPTS
    wl = os.path.join(SPOOL, 'whitelist.json')                      # [09-08] hot-reload: politica editavel sem reiniciar o daemon
    if os.path.exists(wl):
        try: SCRIPTS = set(json.load(open(wl)))
        except Exception: pass
    ev = os.path.join(SPOOL, 'envs.json')   # [09-09] lista de env tambem editavel sem reiniciar (F3/F4 exigiram 2 reinicios)
    if os.path.exists(ev):
        try: ENVS.update(json.load(open(ev)))
        except Exception: pass
    if not isinstance(p, dict):                    raise ValueError('pedido não é objeto')
    pid = str(p.get('id', '')).strip()
    if not re.fullmatch(r'[\w-]{1,40}', pid):      raise ValueError('id inválido')
    sc = p.get('script')
    if sc not in SCRIPTS:                          raise ValueError(f'script fora da lista branca: {sc!r}')
    sub = str(p.get('out', 'nmd'))
    if not re.fullmatch(r'[\w-]{1,40}', sub):      raise ValueError('out inválido (só nome de subpasta)')
    out = os.path.join(BASE, sub)

    env = dict(os.environ)
    for k, v in (p.get('env') or {}).items():
        if k not in ENVS:                          raise ValueError(f'env fora da lista branca: {k}')
        if not re.fullmatch(r'[\w./-]{1,80}', str(v)): raise ValueError(f'valor de env inválido: {k}')
        env[k] = str(v)
    env.setdefault('HSA_OVERRIDE_GFX_VERSION', '10.3.0')
    env.setdefault('TORCHINDUCTOR_COMPILE_THREADS', '1')

    argv = [PY, os.path.join(REPO, 'src', sc + '.py')]
    for k, v in (p.get('args') or {}).items():
        k = str(k)
        if not FLAG.fullmatch(k):                  raise ValueError(f'flag inválida: {k!r}')
        argv.append('--' + k)
        vs = v if isinstance(v, (list, tuple)) else [v]
        if v is True: argv.pop(); argv.append('--' + k); continue          # flag booleana
        for x in vs:
            if isinstance(x, bool):                raise ValueError('bool em lista')
            if isinstance(x, (int, float)):        argv.append(repr(x) if isinstance(x, float) else str(x)); continue
            x = str(x)
            if not VALOR.fullmatch(x):             raise ValueError(f'valor inválido em --{k}: {x!r}')
            if x.startswith('-'):                  raise ValueError(f'valor parece flag em --{k}: {x!r}')
            argv.append(x)
    argv += ['--out', out]
    return argv, env, out

def ocupado():
    r = subprocess.run(['pgrep', '-af', 'python'], capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if LIVRE.search(l) and 'nmd.py' not in l]

def escreve(caminho, d):
    tmp = caminho + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, caminho)                    # atômico: o leitor nunca vê meio arquivo

RE_GER  = re.compile(r'^\s*ger\s+(\d+)\s*\|\s*(.*?)\s*\(melhor')
RE_ARM  = re.compile(r'^\s{2}(\S.*?)\s{2,}NP\s+(\d+)')

def sha256_of(path):
    try:
        h = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(1 << 20), b''): h.update(chunk)
        return h.hexdigest()
    except OSError: return None

def git_head(repo):
    try: return subprocess.run(['git', '-C', repo, 'rev-parse', '--short=12', 'HEAD'], capture_output=True, text=True, timeout=10).stdout.strip() or None
    except Exception: return None

UNIVERSE = os.path.expanduser('~/projects/LLM/Universe')

def manifest(ped, argv, env, out):
    """[12/09, handbook] one manifest.json per run: what actually ran (commit, binary/script SHA-256, exact command,
    env subset, seeds) — written BEFORE the process starts, so a crash still leaves the record."""
    script = argv[1] if len(argv) > 1 else None
    m = dict(id=ped['id'], written=agora(), script=script, script_sha256=sha256_of(script) if script else None,
             lab_commit=git_head(REPO), command=argv, env={k: env[k] for k in sorted(env) if k in ENVS}, out=out,
             args=ped.get('args', {}))
    if '--bin' in argv:
        b = os.path.join(UNIVERSE, 'target', 'release', argv[argv.index('--bin') + 1])
        m.update(binary=b, binary_sha256=sha256_of(b), universe_commit=git_head(UNIVERSE),
                 binary_mtime=datetime.fromtimestamp(os.path.getmtime(b), timezone.utc).isoformat(timespec='seconds') if os.path.exists(b) else None)
    a = ped.get('args', {}) or {}
    m['seeds'] = {k: a[k] for k in a if 'seed' in k or k in ('sementes', 'semente')}
    escreve(os.path.join(out, 'manifest.json'), m)
    return m

def executa(ped, argv, env, out):
    pid = ped['id']; est = os.path.join(SPOOL, 'estado', pid + '.json')
    logp = os.path.join(SPOOL, 'log', pid + '.log'); t0 = time.time()
    os.makedirs(out, exist_ok=True)
    try: manifest(ped, argv, env, out)
    except Exception as ex: print(f'[nmd] manifest failed for {pid}: {ex!r}', flush=True)
    e = dict(id=pid, fase='rodando', inicio=agora(), argv=argv[1:], out=out,
             geracao=None, melhor_por_semente=None, bracos_prontos=[], segundos=0)
    escreve(est, e)
    with open(logp, 'w', encoding='utf-8') as lg:
        pr = subprocess.Popen(argv, cwd=os.path.join(REPO, 'src'), env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        e['pid'] = pr.pid; escreve(est, e)
        ult = 0
        for linha in pr.stdout:
            lg.write(linha); lg.flush()
            m = RE_GER.match(linha)
            if m:
                e['geracao'] = int(m.group(1))
                e['melhor_por_semente'] = [float(x) for x in m.group(2).split()]
            m = RE_ARM.match(linha)
            if m: e['bracos_prontos'].append(m.group(1).strip())
            if time.time() - ult > 20:                       # heartbeat a cada 20 s
                e['segundos'] = round(time.time() - t0); escreve(est, e); ult = time.time()
        rc = pr.wait()
    e.update(fase='terminou', fim=agora(), segundos=round(time.time() - t0), exit_code=rc,
             ok=(rc == 0), resultados=sorted(
                 os.path.join(out, f) for f in os.listdir(out)
                 if f.endswith('.json') and os.path.getmtime(os.path.join(out, f)) >= t0))
    escreve(est, e)
    return e

def atende(uma_vez=False, intervalo=5):
    for d in ('pedidos', 'estado', 'log', 'feitos', 'recusados'):
        os.makedirs(os.path.join(SPOOL, d), exist_ok=True)
    print(f'[nmd] atendendo {SPOOL}/pedidos  (PARE para encerrar)', flush=True)
    running = {}                       # file name -> dict(thread, ped, script, result)

    def reap():
        for name in list(running):
            r = running[name]
            if r['thread'].is_alive(): continue
            e = r['result'].get('e')
            cam = os.path.join(SPOOL, 'pedidos', name)
            if os.path.exists(cam): shutil.move(cam, os.path.join(SPOOL, 'feitos', name))
            if e: print(f'[nmd] {r["ped"]["id"]} terminou exit={e["exit_code"]} em {e["segundos"]}s', flush=True)
            del running[name]

    def start(name, ped, argv, env, out):
        result = {}
        def alvo():
            try: result['e'] = executa(ped, argv, env, out)
            except Exception as ex:
                escreve(os.path.join(SPOOL, 'estado', ped['id'] + '.json'),
                        dict(id=ped['id'], fase='erro', erro=repr(ex), quando=agora())); result['e'] = None
        t = threading.Thread(target=alvo, name=ped['id'], daemon=True); t.start()
        running[name] = dict(thread=t, ped=ped, script=ped.get('script'), result=result)
        print(f'[nmd] rodando {ped["id"]} ({len(running)} em paralelo): {" ".join(argv[1:])[:150]}', flush=True)

    while True:
        reap()
        if os.path.exists(os.path.join(SPOOL, 'PARE')) and not running:
            print('[nmd] PARE encontrado, saindo', flush=True); return
        fila = [f for f in sorted(os.listdir(os.path.join(SPOOL, 'pedidos'))) if f.endswith('.json') and f not in running]
        if not fila:
            if uma_vez and not running: return
            time.sleep(intervalo); continue
        # [14/09] no head-of-line blocking: the first pedido (alphabetical) whose script can coexist with what is
        # running starts; an exclusive pedido waits for an empty GPU and may be overtaken by coexisting ones.
        picked = None
        for name in fila:
            cam = os.path.join(SPOOL, 'pedidos', name)
            try: ped = json.load(open(cam, encoding='utf-8'))
            except Exception as ex:
                shutil.move(cam, os.path.join(SPOOL, 'recusados', name))
                escreve(os.path.join(SPOOL, 'recusados', name + '.motivo'), dict(motivo=f'json ilegível: {ex}')); continue
            try: argv, env, out = valida(ped)
            except ValueError as ex:
                shutil.move(cam, os.path.join(SPOOL, 'recusados', name))
                escreve(os.path.join(SPOOL, 'estado', str(ped.get('id', 'sem-id')) + '.json'),
                        dict(id=ped.get('id'), fase='recusado', motivo=str(ex), quando=agora()))
                print(f'[nmd] RECUSADO {name}: {ex}', flush=True); continue
            if can_start(ped.get('script'), [r['script'] for r in running.values()]):
                picked = (name, ped, argv, env, out); break
        if picked is None:
            time.sleep(intervalo); continue
        name, ped, argv, env, out = picked
        viva = ocupado()
        if viva:
            print(f'[nmd] GPU ocupada ({len(viva)} bateria(s)), esperando', flush=True)
            escreve(os.path.join(SPOOL, 'estado', ped['id'] + '.json'),
                    dict(id=ped['id'], fase='esperando-gpu', ocupada_por=viva[:3], quando=agora()))
            if uma_vez and not running: return
            time.sleep(intervalo * 4); continue
        start(name, ped, argv, env, out)
        if uma_vez:
            while running: reap(); time.sleep(1)
            return

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--uma-vez', action='store_true'); ap.add_argument('--spool', default=None)
    ap.add_argument('--repo', default=None); ap.add_argument('--py', default=None); ap.add_argument('--base', default=None)
    a = ap.parse_args()
    if a.spool: SPOOL = a.spool
    if a.repo:  REPO  = a.repo
    if a.py:    PY    = a.py
    if a.base:  BASE  = a.base
    signal.signal(signal.SIGINT, lambda *_: sys.exit('\n[nmd] interrompido'))
    atende(a.uma_vez)
