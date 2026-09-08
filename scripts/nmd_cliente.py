"""nmd_cliente.py — lado do Claude Science: deposita pedido no spool e lê o que voltou.
Só stdlib. Não roda bateria nenhuma aqui; só escreve e lê arquivos na pasta compartilhada.

    import nmd_cliente as nmd
    nmd.pedir('e63c', 'e43_campo', out='e63', env={'NM_RISCO':'1'}, preset='honesto',
              G=120, R=8, seeds=[0,1,2,3,4], L=200, dias=15, fitness='riqueza',
              mundo='distinto', nevoa=25, so=['linear','bilinear risco (esc 3)'], tag='_e63_nev_25')
    nmd.estado('e63c')       # heartbeat: fase, geração, melhor por semente, braços prontos
    nmd.fila()               # o que está pendente / rodando / feito
    nmd.resultado('e63c')    # carrega os JSONs de resultado que a bateria gravou
"""
import json, os, time

SPOOL = '/media/llm-data/universe-runs/neuromod-lab-taxi/_nmd'

def _p(*a): return os.path.join(SPOOL, *a)

def pedir(id, script, out='nmd', env=None, **args):
    """Escreve <spool>/pedidos/<id>.json. Sobrescrever um id pendente é permitido; um id já
    FEITO deve receber outro nome, senão o estado antigo é sobrescrito e a trilha se perde."""
    os.makedirs(_p('pedidos'), exist_ok=True)
    ped = dict(id=id, script=script, out=out, env=env or {}, args=args)
    tmp = _p('pedidos', id + '.json.tmp')
    with open(tmp, 'w', encoding='utf-8') as f: json.dump(ped, f, ensure_ascii=False, indent=1)
    os.replace(tmp, _p('pedidos', id + '.json'))     # atômico: o daemon nunca lê meio pedido
    return ped

def estado(id):
    c = _p('estado', id + '.json')
    return json.load(open(c, encoding='utf-8')) if os.path.exists(c) else {'fase': 'inexistente', 'id': id}

def fila():
    def ls(d): return sorted(f[:-5] for f in os.listdir(_p(d))) if os.path.isdir(_p(d)) else []
    return dict(pendentes=ls('pedidos'), feitos=ls('feitos'), recusados=ls('recusados'),
                estados={i: estado(i).get('fase') for i in ls('estado')})

def log(id, linhas=20):
    c = _p('log', id + '.log')
    return ''.join(open(c, encoding='utf-8', errors='replace').readlines()[-linhas:]) if os.path.exists(c) else ''

def resultado(id):
    """Carrega os JSONs que a bateria gravou (o campo `resultados` do estado)."""
    return {os.path.basename(c): json.load(open(c, encoding='utf-8'))
            for c in estado(id).get('resultados', []) if os.path.exists(c)}

def esperar(id, limite_s=1800, intervalo=30):
    """Só para uso interativo curto; para bateria longa, olhe estado() em turnos separados."""
    t0 = time.time()
    while time.time() - t0 < limite_s:
        e = estado(id)
        if e.get('fase') in ('terminou', 'recusado', 'erro'): return e
        time.sleep(intervalo)
    return estado(id)
