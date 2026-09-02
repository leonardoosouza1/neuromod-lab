"""E18 (doc 28 §1, doc 00-NEGATIVOS regras 13/14): avaliação HONESTA como
módulo reutilizável — R vidas/genoma alto, 5+ sementes, várias cidades nunca
vistas no treino, e tabela automática. Sem depender de `e13_corpo.py` (a
função `telemetria` é uma CÓPIA da de lá, não um import — ver doc 32).

Uso típico (um runner e15/e16/e17-like):

    from avaliacao import evoluir_e_avaliar, tabela
    res = evoluir_e_avaliar(Reativo, cfg, seeds=(0,1,2,3,4), R=16,
                             out_dir=OUT, nome='e18_exemplo')
    print(tabela([res]))

Regra 13 (mortalidade só conta com n>=5 sementes) e regra 14 (evento raro
precisa ser visível no fitness — R>=1/p^2 vidas por genoma; ~16 pra p~0.18-0.25
neste laboratório) — ver doc 00-NEGATIVOS.md N17/N18. Regra do doc 27 §6.5:
cidades 1000+ rendem ~30% otimistas sozinhas — reportar sempre a média de
vários conjuntos de cidades (o padrão do dia usa 1000+ e 2000+, 3 cidades
cada = "média de 6 cidades").
"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import gerar_cidade, evoluir_sementes, rodar, modo_execucao


# ============================ TELEMETRIA (cópia da de e13_corpo.py) ============================
def telemetria(m, T):
    """Cópia EXATA da `telemetria` de e13_corpo.py (mesmos campos). Copiada,
    não importada — E18 não deve depender de e13_corpo.py (doc 28 §2: cada
    agente só edita seus próprios arquivos)."""
    f = lambda x: round(float(x.mean()), 3)
    return dict(
        fit=f(m.ent - 0.3*m.avar), ent=f(m.ent), avar=f(m.avar),
        av_fuel=f(m.av_fuel), av_furo=f(m.av_furo), av_oleo=f(m.av_oleo), av_quente=f(m.av_quente),
        mortos=f((m.vida <= 0).float()), t_vida=f(m.t_vida/T), vida_fim=f(m.vida), dano=f(m.dano_soma),
        n_oficina=f(m.n_oficina), n_posto=f(m.n_posto), pobre_frac=f(m.t_pobre/T), dinh=f(m.dinh),
        n_mob=f(m.n_mob), conv_por_dia=f(m.conv_soma/(T/m.cfg.dia)), res_media=f(m.res_soma/T),
        sono=f(m.sono_soma), par_fad=f(m.par_fad), fuel_22=f(m.fuel_22/m.n_22.clamp(min=1)),
        n_bloco=f(m.n_bloco), par_noite_frac=f(m.par_noite/(T*8/24.)), ent_noite=f(m.ent_noite),
    )


# ============================ AVALIAÇÃO HONESTA ============================
def avaliar_honesto(Arq, W_por_semente, cfg, T=1200, conjuntos=(1000, 2000), n_cid=3, R=128,
                     seed=7777, verbose=False):
    """Roda cada campeão (1 política por semente de evolução) em cada
    CONJUNTO de cidades nunca vistas no treino (n_cid cidades por conjunto,
    seeds `base..base+n_cid-1`; R réplicas por campeão/cidade). Devolve
    telemetria por conjunto (média entre sementes) e a MÉDIA HONESTA entre
    conjuntos — a "média de 6 cidades" do doc 27 §6.5, generalizada pra
    len(conjuntos)*n_cid cidades.

    `W_por_semente`: {semente: tensor (NP,)} — ex.: `{sd: champs[sd][0] for
    sd in seeds}`, saída de `evoluir_sementes`. Também aceita tensores já
    replicados (P, NP): nesse caso usa como está (sem repetir por R).

    Devolve dict:
      conjuntos, n_cid, R
      por_conjunto        {conjunto: {semente: telemetria}}
      por_conjunto_medio  {conjunto: telemetria média entre sementes}
      media               telemetria média entre conjuntos (a média honesta)
      fit_por_semente     {conjunto: {semente: fit}}
      mortos_por_semente  {conjunto: {semente: mortos}}   (mortos = fração com vida<=0)
    """
    seeds = list(W_por_semente.keys())
    if not seeds:
        raise ValueError('W_por_semente vazio')
    por_conjunto = {}
    por_conjunto_medio = {}
    for base in conjuntos:
        cidades = [gerar_cidade(base + s) for s in range(n_cid)]
        por_sem = {}
        for sd in seeds:
            w = W_por_semente[sd]
            W = w[None, :].repeat(R, 1) if w.dim() == 1 else w
            m = rodar(Arq, W, cidades, cfg, T=T, seed=seed)
            por_sem[sd] = telemetria(m, T)
        por_conjunto[base] = por_sem
        chaves = list(next(iter(por_sem.values())).keys())
        por_conjunto_medio[base] = {
            k: round(sum(por_sem[sd][k] for sd in seeds) / len(seeds), 4) for k in chaves
        }
        if verbose:
            med = por_conjunto_medio[base]
            print(f'    conjunto {base}+: fit {med["fit"]:6.2f}  mortos {med["mortos"]:.3f}', flush=True)
    chaves = list(por_conjunto_medio[conjuntos[0]].keys())
    media = {
        k: round(sum(por_conjunto_medio[c][k] for c in conjuntos) / len(conjuntos), 4) for k in chaves
    }
    return dict(
        conjuntos=list(conjuntos), n_cid=n_cid, R=R,
        por_conjunto=por_conjunto,
        por_conjunto_medio=por_conjunto_medio,
        media=media,
        fit_por_semente={c: {sd: por_conjunto[c][sd]['fit'] for sd in seeds} for c in conjuntos},
        mortos_por_semente={c: {sd: por_conjunto[c][sd]['mortos'] for sd in seeds} for c in conjuntos},
    )


def evoluir_e_avaliar(Arq, cfg, P=1024, G=60, T_evo=1200, seeds=(0, 1, 2, 3, 4), R=16,
                       treino=None, T_aval=1200, conjuntos=(1000, 2000), n_cid=3, R_aval=128,
                       out_dir=None, nome=None, verbose=False):
    """Padrão HONESTO (doc 28 E18; regras 13/14 do doc 00-NEGATIVOS): evolui
    com R vidas/genoma (default 16) e 5 sementes, depois avalia cada campeão
    em cidades nunca vistas (`avaliar_honesto`). Se `out_dir` e `nome` forem
    dados, salva um JSON (escrita atômica, mesmo padrão do e13) com a
    avaliação + `W` e `hist` dos campeões — o suficiente pra `tabela()` e
    `resumo_para_painel()` lerem depois, e pra continuar uma linha de
    investigação sem reevoluir.

    `treino`: lista de cidades de treino; default = 4 cidades (seeds 0..3),
    igual ao e13_corpo.
    """
    if treino is None:
        treino = [gerar_cidade(s) for s in range(4)]
    t0 = time.time()
    champs = evoluir_sementes(Arq, treino, cfg, P=P, ger=G, T=T_evo, seeds=seeds, R=R, verbose=verbose)
    W_por_semente = {sd: champs[sd][0] for sd in seeds}
    aval = avaliar_honesto(Arq, W_por_semente, cfg, T=T_aval, conjuntos=conjuntos, n_cid=n_cid,
                            R=R_aval, verbose=verbose)
    res = dict(
        arq=Arq.nome, modo=modo_execucao(),
        preset=dict(P=P, G=G, T_evo=T_evo, seeds=list(seeds), R=R, T_aval=T_aval, R_aval=R_aval),
        segundos=round(time.time() - t0),
        **aval,
        hist={sd: champs[sd][1] for sd in seeds},
        W={sd: [round(float(x), 5) for x in champs[sd][0]] for sd in seeds},   # campeão (diagnóstico)
    )
    if out_dir and nome:
        os.makedirs(out_dir, exist_ok=True)
        tmp = os.path.join(out_dir, f'{nome}.json.tmp')
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, os.path.join(out_dir, f'{nome}.json'))
    return res


# ============================ TABELA / PAINEL ============================
def _ck(d, k):
    """Lê `d[k]` tolerando chaves viradas string por um round-trip de JSON
    (dict de int vira dict de str ao salvar/carregar)."""
    return d[k] if k in d else d[str(k)]


def _normalizar(jsons):
    if isinstance(jsons, (str, dict)):
        return [jsons]
    return list(jsons)


def _carregar(j):
    if isinstance(j, dict):
        return j, None
    with open(j) as fh:
        d = json.load(fh)
    return d, os.path.splitext(os.path.basename(j))[0]


def _linhas(d, origem):
    """Um JSON pode ser (a) o resultado de 1 braço (evoluir_e_avaliar /
    avaliar_honesto, com 'media' no topo) ou (b) vários braços combinados
    (rodar_bracos, com 'bracos': {nome: resultado})."""
    if 'bracos' in d:
        return [(nome, r, origem) for nome, r in d['bracos'].items()]
    rotulo = d.get('nome') or d.get('arq') or origem or 'braço'
    return [(rotulo, d, origem)]


def tabela(jsons, colunas=('fit', 'mortos'), por_semente=False):
    """Markdown: 1 linha por braço, colunas = cada coluna de `colunas` por
    conjunto de cidades + a média honesta entre conjuntos. `jsons`: caminho
    (ou lista de caminhos) de JSON no formato de `evoluir_e_avaliar` /
    `avaliar_honesto`, ou o combinado de `rodar_bracos` (chave 'bracos'); dá
    pra passar dicts já carregados também. `por_semente=True` acrescenta,
    ao lado de cada valor, os números individuais de cada semente entre
    colchetes (regra 13: sempre olhar a dispersão entre sementes, não só a
    média)."""
    jsons = _normalizar(jsons)
    linhas = []
    for j in jsons:
        d, origem = _carregar(j)
        linhas.extend(_linhas(d, origem))
    if not linhas:
        return '(sem dados)'
    conjuntos = linhas[0][1]['conjuntos']
    # cabeçalho em markdown simples: "coluna·conjunto+" (ex.: fit·1000+) e "coluna·média"
    cab = ['braço'] + [f'{col}·{c}+' for col in colunas for c in conjuntos] + [f'{col}·média' for col in colunas]
    linhas_md = ['| ' + ' | '.join(cab) + ' |', '|' + '---|' * len(cab)]
    multi_origem = len({origem for _, _, origem in linhas if origem}) > 1
    for nome, r, origem in linhas:
        rotulo = f'{nome} ({origem})' if origem and multi_origem else nome
        cel = [rotulo]
        for col in colunas:
            for c in r['conjuntos']:
                v = _ck(r['por_conjunto_medio'], c)[col]
                s = f'{v:.3f}' if isinstance(v, float) else str(v)
                if por_semente:
                    chave = {'fit': 'fit_por_semente', 'mortos': 'mortos_por_semente'}.get(col)
                    if chave and chave in r:
                        psem = _ck(r[chave], c)
                        s += ' [' + ' '.join(f'{x:.2f}' for x in psem.values()) + ']'
                cel.append(s)
        for col in colunas:
            v = r['media'][col]
            cel.append(f'{v:.3f}' if isinstance(v, float) else str(v))
        linhas_md.append('| ' + ' | '.join(cel) + ' |')
    return '\n'.join(linhas_md)


def resumo_para_painel(jsons):
    """Resumo compacto (nome, fit, mortos — média honesta e por conjunto —
    n_sementes) por braço, pronto pra virar entrada de um painel tipo
    docs/painel-27-corpo-carro.html (que hoje edita arrays `d = [[...]]` à
    mão; isto poupa a conta, não substitui a curadoria visual)."""
    jsons = _normalizar(jsons)
    bracos = []
    for j in jsons:
        d, origem = _carregar(j)
        for nome, r, _ in _linhas(d, origem):
            conjuntos = r['conjuntos']
            fps = _ck(r['fit_por_semente'], conjuntos[0])
            bracos.append(dict(
                nome=nome, origem=origem,
                fit=r['media']['fit'], mortos=r['media']['mortos'],
                fit_por_conjunto={c: _ck(r['por_conjunto_medio'], c)['fit'] for c in conjuntos},
                mortos_por_conjunto={c: _ck(r['por_conjunto_medio'], c)['mortos'] for c in conjuntos},
                n_sementes=len(fps),
            ))
    return dict(bracos=bracos)
