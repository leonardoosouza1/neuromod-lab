"""E17: leitura dos genes de produto + ablacao causal do campeao.

    python src/analise_produtos.py [JSON] [--arq produto] [--replicas 128]
                                   [--sem-ablacao] [--top 12]

Faz duas coisas, nesta ordem:

1. CONVERGENCIA — imprime o gene de cada produto por semente e marca os que
   convergem: mesmo SINAL em >= 4/5 sementes (ou >= 80% das disponiveis) e
   |mediana| acima do limiar. E o criterio usado no E14g (doc 27 6.20), onde
   os dois genes do Noite24 deram 3.7 e 0.3 em 5/5.

2. ABLACAO — zera um produto por vez no campeao (a semente de melhor fit) e
   reavalia em `--replicas` replicas x 3 cidades, T=T_aval, seed 7777 (a mesma
   avaliacao do braco). Reporta delta de mortos e de fitness contra o campeao
   intacto. Uso != contribuicao (regra 4 dos NEGATIVOS): so a lesao diz se o
   gene faz alguma coisa.

Sinal (ReativoProdutoFull): os produtos entram NEGADOS e os estados sao as
features de obs() como elas sao (e_fuel = ENCHIMENTO). "Aproxime-se do posto
quando o tanque esta baixo" e portanto W[fuel x posto] < 0 no Full e
W[pr_posto] > 0 no ReativoProduto. A coluna `sentido` traduz.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from lab import DEV, NF, gerar_cidade, Reativo, ReativoNoite24, rodar
from e13_corpo import cfg_corpo
from produtos import ReativoProduto, ReativoProdutoFull

PAD = '/media/llm-data/universe-runs/neuromod-lab-taxi/e17/e17_produtos.json'
ARQS = {'reativo': Reativo, 'noite24': ReativoNoite24,
        'produto': ReativoProduto, 'produto_full': ReativoProdutoFull}


def genes_de(nome):
    """(indices, nomes, sinal_bom) do bloco de produto de cada arquitetura."""
    if nome == 'produto':
        A = ReativoProduto
        return list(range(A.B0, A.B0+7)), A.NOMES, +1
    if nome == 'produto_full':
        A = ReativoProdutoFull
        return list(range(A.B0, A.B0+60)), A.NOMES, -1
    if nome == 'noite24':
        return [NF+6, NF+7], ['sv_posto', 'rota_posto'], +1
    return [], [], +1


def convergencia(Ws, idx, nomes, limiar=.5, top=None):
    """Ws: {semente: lista de pesos}. Devolve linhas ordenadas por |mediana|."""
    sems = sorted(Ws)
    linhas = []
    for i, g in enumerate(idx):
        v = [Ws[s][g] for s in sems]
        t = torch.tensor(v)
        med = float(t.median())
        pos = int((t > 0).sum()); neg = int((t < 0).sum())
        conc = max(pos, neg)                      # sementes com o sinal dominante
        ok = conc >= max(2, int(round(.8*len(v)))) and abs(med) > limiar
        linhas.append(dict(nome=nomes[i], idx=g, v=v, med=med,
                           conc=f'{conc}/{len(v)}', converge=ok))
    linhas.sort(key=lambda d: -abs(d['med']))
    return linhas if top is None else linhas[:top]


def _tel(m, P, blocos):
    """medias por genoma-bloco: (n_blocos,) fit e mortos."""
    v = lambda x: x.view(P, -1).mean(1).view(blocos, -1).mean(1)
    return v(m.ent - .3*m.avar), v((m.vida <= 0).float())


def ablacao(A, W0, cfg, teste, T, replicas, idx, nomes, seed=7777, chunk=4096):
    """campeao intacto + um variante por gene zerado + tudo zerado."""
    variantes = [W0] + [W0.clone().index_fill_(0, torch.tensor([g], device=DEV), 0.)
                        for g in idx]
    if len(idx) > 1:
        variantes.append(W0.clone().index_fill_(0, torch.tensor(idx, device=DEV), 0.))
    rot = ['(intacto)'] + [f'-{n}' for n in nomes] + (['-TODOS'] if len(idx) > 1 else [])
    fits, mortos = [], []
    passo = max(1, chunk//replicas)
    for a in range(0, len(variantes), passo):
        blocos = variantes[a:a+passo]
        W = torch.stack(blocos).repeat_interleave(replicas, 0)
        m = rodar(A, W, teste, cfg, T=T, seed=seed)
        f, mo = _tel(m, W.shape[0], len(blocos))
        fits += [float(x) for x in f]; mortos += [float(x) for x in mo]
    return rot, fits, mortos


def main(a):
    d = json.load(open(a.arquivo))
    p = d['preset']; cfg = cfg_corpo(**d['mundo'])
    teste = [gerar_cidade(d['teste_seed']+s) for s in range(3)]
    T = p['T_aval']
    alvos = a.arq or [k for k in d['bracos'] if genes_de(k)[0]]
    for nome in alvos:
        if nome not in d['bracos']:
            print(f'-- {nome}: ausente no JSON'); continue
        br = d['bracos'][nome]; A = ARQS[nome]
        idx, nomes, bom = genes_de(nome)
        Ws = {int(s): w for s, w in br['W'].items()}
        sems = sorted(Ws)
        print(f'\n== {nome} (NP={A.NP}, {len(idx)} produtos, {len(sems)} sementes) '
              f'fit {br["fit"]:.2f} mortos {br["mortos"]:.3f} ==')
        print(f'  sinal "bom" (ir ao servico quando precisa) = {"+" if bom > 0 else "-"}')
        linhas = convergencia(Ws, idx, nomes, a.limiar, a.top)
        cab = '  '.join(f's{s}' for s in sems)
        print(f'  {"gene":<18}{"mediana":>9}{"sinal":>7}  {cab}')
        n_conv = 0
        for L in linhas:
            n_conv += L['converge']
            vs = '  '.join(f'{x:+.2f}' for x in L['v'])
            marca = 'OK' if L['converge'] else ''
            print(f'  {L["nome"]:<18}{L["med"]:>+9.2f}{L["conc"]:>7}  {vs}  {marca}')
        tot = sum(1 for L in convergencia(Ws, idx, nomes, a.limiar) if L['converge'])
        print(f'  convergem (|med|>{a.limiar}, sinal em >=80% das sementes): {tot}/{len(idx)}')
        if a.sem_ablacao or not idx:
            continue
        # fit_por_semente segue a ORDEM de preset['seeds'] (nao a ordenada)
        ordem_sem = [int(x) for x in p['seeds']]
        campeao = ordem_sem[max(range(len(ordem_sem)),
                                key=lambda i: br['fit_por_semente'][i])]
        W0 = torch.tensor(Ws[campeao], device=DEV, dtype=torch.float32)
        gi = [L['idx'] for L in linhas] if a.top else idx
        gn = [L['nome'] for L in linhas] if a.top else nomes
        print(f'  -- ablacao do campeao (semente {campeao}, {a.replicas} replicas x '
              f'{len(teste)} cidades, T={T}) --')
        rot, fits, mortos = ablacao(A, W0, cfg, teste, T, a.replicas, gi, gn)
        f0, m0 = fits[0], mortos[0]
        ordem = sorted(range(len(rot)), key=lambda i: -(mortos[i]-m0))
        print(f'  {"variante":<20}{"fit":>7}{"dfit":>8}{"mortos":>8}{"dmortos":>9}')
        for i in ([0] + [j for j in ordem if j]):
            print(f'  {rot[i]:<20}{fits[i]:>7.2f}{fits[i]-f0:>+8.2f}'
                  f'{mortos[i]:>8.3f}{mortos[i]-m0:>+9.3f}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('arquivo', nargs='?', default=PAD)
    ap.add_argument('--arq', nargs='*', default=None)
    ap.add_argument('--replicas', type=int, default=128)
    ap.add_argument('--limiar', type=float, default=.5)
    ap.add_argument('--top', type=int, default=None, help='so os N maiores |mediana| (Full)')
    ap.add_argument('--sem-ablacao', action='store_true')
    main(ap.parse_args())
