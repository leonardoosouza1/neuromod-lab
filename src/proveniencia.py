"""Manifestos e validação de resultados; sem dependência de GPU."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess


def normaliza(valor):
    if isinstance(valor, float) and not math.isfinite(valor):
        return str(valor)
    if isinstance(valor, dict):
        return {str(k): normaliza(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple)):
        return [normaliza(v) for v in valor]
    return valor


def hash_config(valor):
    return hashlib.sha256(json.dumps(normaliza(valor), sort_keys=True,
                                    allow_nan=False).encode()).hexdigest()


def identidade_codigo(raiz):
    raiz = Path(raiz)
    arquivos = {}
    for pasta in ('src', 'scripts'):
        for p in sorted((raiz / pasta).rglob('*')):
            if p.is_file() and p.suffix in ('.py', '.cu', '.hip'):
                arquivos[str(p.relative_to(raiz))] = hashlib.sha256(p.read_bytes()).hexdigest()
    try:
        commit = subprocess.check_output(['git', '-C', str(raiz), 'rev-parse', 'HEAD'],
                                         stderr=subprocess.DEVNULL, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        commit = None
    return dict(commit=commit, fontes_sha256=hash_config(arquivos))


def manifesto(cfg, protocolo, mapas, flags, codigo):
    return normaliza(dict(cfg=vars(cfg), protocolo=protocolo, mapas=mapas,
                         flags=flags, codigo=codigo,
                         ambiente={k: os.environ.get(k, '1' if k == 'NM_COMPILE' else '0')
                                   for k in ('NM_RISCO', 'NM_PONTO', 'NM_RETINA', 'NM_REGIME', 'NM_COMPILE')}))


def valores_por_semente(braco, chave):
    seeds = braco.get('seeds')
    valores = braco[chave]
    if seeds is None:
        raise ValueError('faltam IDs de sementes; nao e seguro inferir pela posicao')
    ids = [str(s) for s in seeds]
    if len(ids) != len(valores) or len(set(ids)) != len(ids):
        raise ValueError('sementes duplicadas ou quantidade diferente das metricas')
    if len(ids) < 2 or not all(isinstance(v, (int, float)) and math.isfinite(v) for v in valores):
        raise ValueError('teste pareado exige >=2 sementes e metricas finitas')
    return dict(zip(ids, valores))


def diferencas(a, b, prefixo=''):
    if isinstance(a, dict) and isinstance(b, dict):
        saida = []
        for k in sorted(a.keys() | b.keys()):
            caminho = f'{prefixo}.{k}' if prefixo else k
            if k not in a or k not in b:
                saida.append(caminho)
            else:
                saida.extend(diferencas(a[k], b[k], caminho))
        return saida
    return [] if a == b else [prefixo]


def valida_comparacao(a, b, variar=(), legado=False):
    ma, mb = a.get('manifesto'), b.get('manifesto')
    if ma is None or mb is None:
        if not legado:
            raise ValueError('resultado sem manifesto; use --legado para assumir comparabilidade')
        return
    # Ordem de sementes não altera o protocolo; IDs são verificados separadamente.
    ma, mb = json.loads(json.dumps(ma)), json.loads(json.dumps(mb))
    for m in (ma, mb):
        m['protocolo'].pop('seeds', None)
    difs = [d for d in diferencas(ma, mb)
            if not any(d == v or d.startswith(v + '.') for v in variar)]
    if difs:
        raise ValueError('diferencas nao declaradas (--variar): ' + ', '.join(difs))
