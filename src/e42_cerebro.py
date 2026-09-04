"""E42 (doc 43): cerebro em CAMADAS vs o pai (reacoes). Reusa o runner do E20.

    # fumaca (P=256 G=10 T=600, 1 semente) — o que o doc 43 reporta
    NM_COMPILE=1 nice -n 5 python src/e42_cerebro.py --preset fumaca
    # triagem/honesto (depois do merge, na fila)
    python src/e42_cerebro.py --preset triagem [--ablacoes] [--init-from JSON BRACO]

Mundo: o pacote final do E19 (fome .15, refeicao 90, comida no posto) — o mesmo
em que o campeao atual (reacoes) foi medido. A cidade GRANDE (n=104, D=6) entra
quando o agente MUNDO fizer merge: `SerCamadas` le cfg.D no reset e ja cobre 6
distritos com genes zerados.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
import e20_corpo_fala as E20
from lab import DEV, Lote, um_passo, gerar_cidade
from reacoes import ReativoReacoes
from camadas import SerCamadas, SemTalamo, SemCortex, SemHipocampo, SoHipocampo
from e19_pacote import cfg_pacote

OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e42'
# fumaca do doc 41 §1: "validacao rapida (fumaca + 1 semente curta)". P=256, G=10,
# T=600, 1 semente, R=4 -> B = 256*4*4 = 4096 mundos (VRAM < 1 GB; GPU compartilhada).
PRESET_FUMACA = dict(P=256, G=10, T_evo=600, T_aval=600, R=4, seeds=(0,))
BASE = [('reacoes (pai)', ReativoReacoes), ('ser camadas', SerCamadas)]
ABLACOES = [('camadas sem talamo', SemTalamo), ('camadas sem cortex', SemCortex),
            ('camadas sem hipocampo', SemHipocampo), ('camadas so hipocampo', SoHipocampo)]
ARQS = dict(BASE + ABLACOES)


def rodar_com_ser(A, W, cids, cfg, T, seed=7777, R=1):
    """como lab.rodar, mas devolve TAMBEM o ser (pra ler ativacao()). Eager de
    proposito: e telemetria de 1 campeao, nao caminho quente de bateria."""
    m = Lote(cids, W.shape[0], cfg, seed=seed, R=R); Wb = W[m.gidx]
    a = A(); a.reset(m, Wb)
    for _ in range(T):
        um_passo(m, a, Wb); a.atualizar(m)
    return m, a


def relatorio_ativacao(origem, destino, bracos, cfg, teste, T, R=1, rep=128):
    """ativacao() media do campeao de cada braco que tenha a camada (sem sync no laco:
    um unico float() por chave, DEPOIS dos T passos). Reescreve o JSON com a
    telemetria por camada dentro, ja com o nome do E42."""
    J = json.load(open(origem))
    print('\n--- ativacao media do campeao (fumaca) ---', flush=True)
    for nome, A in bracos:
        if not hasattr(A, 'ativacao'): continue
        for sd, w in J['bracos'][nome]['W'].items():
            W = torch.tensor(w, device=DEV)[None, :].repeat(rep, 1)
            m, a = rodar_com_ser(A, W, teste, cfg, T, R=R)
            at = {k: round(float(v.mean()), 4) for k, v in a.ativacao().items()}
            J['bracos'][nome].setdefault('ativacao', {})[sd] = at
            print(f'  {nome} s{sd}:', flush=True)
            for k, v in at.items(): print(f'      {k:<38} {v:>9.4f}')
            del m, a
    tmp = destino + '.tmp'
    with open(tmp, 'w') as fh: json.dump(J, fh, indent=1)
    os.replace(tmp, destino)
    if os.path.exists(origem) and origem != destino: os.remove(origem)
    print(f'  (gravado em {destino})', flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--preset', default='fumaca', choices=('fumaca', 'triagem', 'honesto'))
    ap.add_argument('--out', default=OUT); ap.add_argument('--so', nargs='*', default=None)
    ap.add_argument('--seeds', type=int, nargs='*', default=None)
    ap.add_argument('--R', type=int, default=None)
    ap.add_argument('--teste-seed', type=int, default=1000)
    ap.add_argument('--pena', type=float, default=5.)
    ap.add_argument('--tag', default=''); ap.add_argument('--curriculo', action='store_true')
    ap.add_argument('--init-from', nargs=2, default=None, metavar=('JSON', 'BRACO'))
    ap.add_argument('--ablacoes', action='store_true', help='inclui os 4 controles por camada')
    ap.add_argument('--sem-ativacao', action='store_true', dest='sem_ativacao')
    a = ap.parse_args()

    E20.BRACOS = BASE + (ABLACOES if a.ablacoes else [])
    E20.OUT = a.out
    if a.preset == 'fumaca':
        E20.PRESET_TRIAGEM = PRESET_FUMACA; a.preset = 'triagem'
    a.tag = a.tag or '_fumaca'
    E20.main(a)

    if not a.sem_ativacao:
        p = dict(E20.PRESET_TRIAGEM if a.preset == 'triagem' else E20.PRESET)
        if a.seeds: p['seeds'] = tuple(a.seeds)
        teste = [gerar_cidade(a.teste_seed + s) for s in range(3)]
        relatorio_ativacao(os.path.join(a.out, f'e20{a.tag}.json'),
                           os.path.join(a.out, f'e42{a.tag}.json'),
                           [b for b in E20.BRACOS if not a.so or b[0] in a.so],
                           cfg_pacote(**E20.MUNDO), teste, p['T_aval'])


if __name__ == '__main__':
    main()
