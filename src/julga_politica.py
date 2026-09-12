"""JUIZ de UMA politica explicita (agentes) — usa politica_util (mundo do juiz definido num lugar so; revisao 09-09 apagou a copia).
Imprime os parametros do mundo na 1a linha; campeao evoluido como referencia; autopsia + traco."""
import sys, os, json, argparse, hashlib, math, copy; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from politica_util import *
from proveniencia import manifesto, normaliza, hash_config, identidade_codigo

def parser():
    ap = argparse.ArgumentParser(); ap.add_argument('--politica', required=True); ap.add_argument('--cenario', default=None); ap.add_argument('--nevoa', type=float, default=None); ap.add_argument('--campeao', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e64/e43_busca8x_L200.json')
    ap.add_argument('--copias', type=int, default=128); ap.add_argument('--seeds', type=int, nargs='*', default=[7777, 7778, 7779, 7780, 7781]); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/agentes'); ap.add_argument('--tag', default='')
    ap.add_argument('--braco', default='linear', help='[10/09 CS docs/87 §1] braco da bateria --campeao usado como referencia (rotulo de BRACOS, ex. "COMPLETO (talamo+cortex+hipocampo+reflexo+livre)"): classe e ajustes vem de politica_util.braco; a chave linear_campeao no JSON fica pelo nome (compatibilidade) e res["braco"] diz qual e')
    ap.add_argument('--W-politica', default='zero', choices=('zero', 'campeao'), help='[10/09 pred 179b] W que entra no um_passo junto com a politica: zero (hoje: o `tudo` do decidir e zero, a politica so ve F) | campeao (o `tudo` vira a nota do campeao linear: politicas que FILTRAM a decisao do campeao, ex. sem FICAR)')
    ap.add_argument('--seeds-evolucao', nargs='+', default=['0'], help='IDs dos campeoes ou todas; --seeds continua sendo sementes ambientais')
    return ap


def seleciona_sementes(pesos, pedidos):
    ids = sorted(pesos) if pedidos == ['todas'] else list(pedidos)
    if not ids or len(ids) != len(set(ids)):
        raise ValueError('IDs evolutivos vazios ou duplicados')
    ausentes = [s for s in ids if s not in pesos]
    if ausentes:
        raise ValueError('sementes evolutivas ausentes: ' + ', '.join(ausentes))
    return ids


def _valida_genomas(pesos, ids, nomes_f, expected_np):
    """Alinha e valida a bateria inteira antes de tocar no simulador."""
    alinhados = {}
    for sd in ids:
        w = alinha_semente(pesos[sd], nomes_f)
        if len(w) != expected_np:
            raise ValueError(f'genoma {sd}: NP {len(w)} != {expected_np}')
        if not all(math.isfinite(float(x)) for x in w):
            raise ValueError(f'genoma {sd}: pesos nao finitos')
        alinhados[sd] = w
    return alinhados


def _salva(destino, res):
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    temporario = destino + '.tmp'
    with open(temporario, 'w') as arquivo:
        json.dump(normaliza(res), arquivo, indent=1, allow_nan=False)
        arquivo.flush()
        os.fsync(arquivo.fileno())
    os.replace(temporario, destino)


def _cfg_efetivo(cfg):
    c = copy.copy(cfg)
    c.corte_vivos = 0.
    c.jardim_comum = False
    return c


def main(argv=None):
    a = parser().parse_args(argv)
    if a.copias < 1 or not a.seeds or len(a.seeds) != len(set(a.seeds)):
        raise ValueError('copias deve ser positivo e sementes ambientais distintas, nao vazias')
    if a.braco != 'linear' and a.W_politica == 'campeao':
        raise ValueError('--W-politica campeao so com --braco linear')
    with open(a.campeao) as arquivo:
        bateria = json.load(arquivo)
    pesos = bateria['bracos'][a.braco]['W']
    ids = seleciona_sementes(pesos, a.seeds_evolucao)
    cfg, teste, T, chave = mundo(a.cenario, nevoa=a.nevoa)
    ArqC, cfgC = braco(bateria, a.braco, cfg)
    with open(a.politica) as arquivo:
        fonte_politica = arquivo.read()
    try:
        POL, erro = carrega(a.politica, fonte=fonte_politica)
    except TypeError:
        # Compatibilidade com uma politica_util antiga durante a transicao.
        POL, erro = carrega(a.politica)
    if erro:
        raise ValueError(f'POLITICA RECUSADA: {erro}')
    ids = list(ids)
    pesos_alinhados = _valida_genomas(pesos, ids, bateria.get('nomes_f'), ArqC.NP)
    os.makedirs(a.out, exist_ok=True)
    destino = os.path.join(a.out, f'julga{a.tag}.json')
    cfg_ref = _cfg_efetivo(cfgC)
    cfg_pol = _cfg_efetivo(cfg)
    mapas = dict(seeds=[1000, 1001, 1002], configs=dict(cenario=a.cenario, chave=chave))
    protocolo = dict(T=T, copias=a.copias, seeds=list(a.seeds), seed_traco=a.seeds[0],
                     seeds_evolucao=ids, W_politica=a.W_politica,
                     cfg_referencia=vars(cfg_ref), cfg_politica=vars(cfg_pol))
    codigo = identidade_codigo(os.path.dirname(os.path.dirname(__file__)))
    manifesto_res = manifesto(cfg_pol, protocolo, mapas,
                              dict(argv=list(argv or []), braco=a.braco), codigo)
    manifesto_res.update(cfg_referencia=normaliza(vars(cfg_ref)), cfg_politica=normaliza(vars(cfg_pol)),
                         nomes_f=list(bateria.get('nomes_f') or []), fontes=codigo,
                         hash_politica=hashlib.sha256(fonte_politica.encode()).hexdigest(),
                         hash_cenario=hashlib.sha256(json.dumps((json.load(open(a.cenario)) if a.cenario else {}), sort_keys=True).encode()).hexdigest(),
                         W_campeoes=normaliza({sd: pesos_alinhados[sd] for sd in ids}),
                         W_campeoes_hash=hash_config({sd: pesos_alinhados[sd] for sd in ids}),
                         schema_version=2)
    res = dict(politica=a.politica, cenario=a.cenario, braco=a.braco,
               W_politica=a.W_politica, seeds_evolucao=ids,
               seeds_ambientais=a.seeds, copias=a.copias, T=T,
               horizonte=cfg.horizonte, campeao=a.campeao,
               mundo=dict(guincho=cfg.GUINCHO, fuel_pane=cfg.FUEL_POS_PANE,
                          kcal_pane=cfg.KCAL_PANE, dinh0=cfg.dinh0,
                          nevoa=cfg.nevoa, retina=cfg.retina, regime=cfg.regime),
               por_semente_evolucao={}, status='parcial', manifesto=manifesto_res)
    Wz = torch.zeros(Linear.NP, device=DEV)
    _salva(destino, res)
    try:
        for sd in ids:
            Wc = torch.tensor(pesos_alinhados[sd], device=DEV)
            Wp = Wc if a.W_politica == 'campeao' else Wz
            registro = {}
            referencia = mede(ArqC, Wc, cfg_ref, teste, T, a.seeds, a.copias)
            registro['campeao'] = referencia
            res['por_semente_evolucao'][sd] = registro
            _salva(destino, res)
            politica = mede(POL, Wp, cfg_pol, teste, T, a.seeds, a.copias)
            registro['politica_res'] = politica
            _salva(destino, res)
            registro['traco'] = traco(POL, Wp, cfg_pol, teste, T=T, B=a.copias, seed=a.seeds[0])
            registro['dif_mortos'] = politica['mortos'] - referencia['mortos']
            _salva(destino, res)
            print(f'semente evolutiva {sd} | ' + linha('campeao', referencia), flush=True)
            print('  ' + linha('politica', politica, registro['traco']), flush=True)
    except Exception:
        res['status'] = 'parcial'
        _salva(destino, res)
        raise
    # Campos antigos apenas quando há um campeão: nunca ocultar uma agregação.
    if len(ids) == 1:
        unico = res['por_semente_evolucao'][ids[0]]
        res.update(linear_campeao=unico['campeao'], politica_res=unico['politica_res'],
                   traco=unico['traco'], dif_mortos=unico['dif_mortos'])
    res['status'] = 'concluido'
    _salva(destino, res)
    return res


if __name__ == '__main__':
    main()
