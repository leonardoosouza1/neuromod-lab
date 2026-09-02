"""E18 (doc 28 §1, doc 32-avaliacao.md): argparse comum + laço de braços pros
runners e15/e16/e17 (e qualquer um novo) migrarem com pouca mudança do
padrão do e13_corpo.py. Não importa de e13_corpo.py (E18 não toca nesse
arquivo) — só de `lab.py` (via avaliacao.py) e `avaliacao.py`.

Uso típico (um `src/e1X_*.py` novo):

    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from lab import Reativo, gerar_cidade
    from runner_comum import criar_parser, rodar_bracos

    def cfg_algumacoisa(minha_flag=False):
        c = Cfg(1.0, mundo='base')
        c.algo = minha_flag
        return c

    BRACOS = [('braço a', dict(minha_flag=False)),
              ('braço b', dict(minha_flag=True))]

    if __name__ == '__main__':
        ap = criar_parser(default_out=OUT)
        ap.set_defaults(tag='e1X_algumacoisa')      # nome do JSON de saída
        # runner-specific (opcional, ex.: qual arquitetura/fase/braços rodar):
        ap.add_argument('--arq', default='reativo', choices=('reativo', 'minhaarq'))
        args = ap.parse_args()
        Arq = {'reativo': Reativo, 'minhaarq': MinhaArq}[args.arq]
        rodar_bracos(BRACOS, Arq, cfg_algumacoisa, args)

Ver docs/32-avaliacao.md pra por quê do padrão (regras 13/14) e o custo em
tempo por preset.
"""
import sys, os, time, argparse, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from avaliacao import evoluir_e_avaliar

OUT_PADRAO = '/media/llm-data/universe-runs/neuromod-lab-taxi/e18'

# P fixo em 1024 nos 3 presets (igual ao e13_corpo) — não é flag de CLI hoje;
# se algum runner precisar variar, sobrescreva PRESETS[...]['P'] antes de
# chamar rodar_bracos, ou passe pelas próprias flags do runner.
PRESETS = {
    'rapido':  dict(P=1024, G=20, T_evo=600,  T_aval=1200, R=4,  seeds=(0, 1, 2)),
    'longo':   dict(P=1024, G=60, T_evo=1200, T_aval=1200, R=4,  seeds=(0, 1, 2)),
    # HONESTO (doc 28 E18 / regras 13-14 do doc 00-NEGATIVOS): R=16 vidas por
    # genoma (evento raro visível no fitness) e 5 sementes (mortalidade só
    # conta com n>=5). É o padrão pra qualquer bateria com morte/evento raro.
    'honesto': dict(P=1024, G=60, T_evo=1200, T_aval=1200, R=16, seeds=(0, 1, 2, 3, 4)),
}


def criar_parser(default_out=OUT_PADRAO, descricao=None):
    """Parser comum. Runners podem `ap.add_argument(...)` mais flags depois
    (ex.: --arq, --fase, --so) — mesmo padrão do argparse do e13_corpo."""
    ap = argparse.ArgumentParser(description=descricao)
    ap.add_argument('--preset', default='rapido', choices=tuple(PRESETS))
    ap.add_argument('--seeds', type=int, nargs='*', default=None,
                     help='sementes de evolução (default: as do preset)')
    ap.add_argument('--R', type=int, default=None,
                     help='vidas por genoma na evolução (default: as do preset; honesto=16)')
    ap.add_argument('--teste-seed', dest='teste_seed', type=int, nargs='*', default=[1000, 2000],
                     help='conjuntos de cidades de avaliação, por seed-base (default 1000 2000 '
                          '= a "média de 6 cidades" do doc 27 §6.5 com n_cid=3)')
    ap.add_argument('--T-aval', dest='T_aval', type=int, default=None,
                     help='passos por vida na avaliação honesta (default: o do preset)')
    ap.add_argument('--G', type=int, default=None, help='gerações (default: as do preset)')
    ap.add_argument('--T-evo', dest='T_evo', type=int, default=None,
                     help='passos por vida durante a evolução (default: o do preset)')
    ap.add_argument('--tag', default='', help='nome do JSON de saída (sem .json)')
    ap.add_argument('--out', default=default_out)
    return ap


def _preset_efetivo(args):
    p = dict(PRESETS[args.preset])
    if args.seeds: p['seeds'] = tuple(args.seeds)
    if args.R: p['R'] = args.R
    if args.G: p['G'] = args.G
    if args.T_evo: p['T_evo'] = args.T_evo
    if args.T_aval: p['T_aval'] = args.T_aval
    return p


def rodar_bracos(bracos, Arq, cfg_fn, args, treino=None, n_cid=3, verbose=False):
    """Roda cada (nome, kwargs) de `bracos` — kwargs vira `cfg_fn(**kwargs)`
    — no padrão honesto (avaliacao.evoluir_e_avaliar): evolui com
    P/G/T_evo/R/seeds do preset (sobrescrito pelas flags de `args`) e avalia
    nos conjuntos de `--teste-seed` (n_cid cidades cada). Salva UM JSON
    combinado em `{args.out}/{args.tag or Arq.nome}.json` (escrita atômica,
    incremental por braço — igual ao main() do e13_corpo), com a mesma forma
    que `avaliacao.tabela()` e `avaliacao.resumo_para_painel()` esperam
    (chave 'bracos': {{nome: resultado de evoluir_e_avaliar}}).

    Devolve o dict `res` completo (mesmo que foi salvo).
    """
    p = _preset_efetivo(args)
    conjuntos = tuple(args.teste_seed) if args.teste_seed else (1000, 2000)
    nome_saida = args.tag or getattr(Arq, 'nome', 'saida')
    os.makedirs(args.out, exist_ok=True)
    caminho = os.path.join(args.out, f'{nome_saida}.json')
    res = dict(preset=p, arq=getattr(Arq, 'nome', str(Arq)), conjuntos=list(conjuntos),
               n_cid=n_cid, bracos={})
    print(f'== {nome_saida} | P={p["P"]} G={p["G"]} T={p["T_evo"]} T_aval={p["T_aval"]} '
          f'R={p["R"]} x{len(p["seeds"])} sementes | cidades {conjuntos} x{n_cid} ==', flush=True)
    t0 = time.time()
    for nome, kwargs in bracos:
        t1 = time.time()
        cfg = cfg_fn(**kwargs)
        r = evoluir_e_avaliar(Arq, cfg, P=p['P'], G=p['G'], T_evo=p['T_evo'], seeds=p['seeds'],
                               R=p['R'], treino=treino, T_aval=p['T_aval'], conjuntos=conjuntos,
                               n_cid=n_cid, verbose=verbose)
        r['segundos'] = round(time.time() - t1)
        res['bracos'][nome] = r
        med = r['media']
        print(f'  {nome:<28} fit {med["fit"]:6.2f}  mortos {med["mortos"]:.3f}  '
              f'ent {med["ent"]:5.1f}  panes {med["av_fuel"]:4.1f}  ({r["segundos"]}s)', flush=True)
        tmp = caminho + '.tmp'
        with open(tmp, 'w') as fh: json.dump(res, fh, indent=1)
        os.replace(tmp, caminho)
    print(f'TOTAL {time.time()-t0:.0f}s -> {caminho}', flush=True)
    return res
