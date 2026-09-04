"""E42 (doc 42): CIDADE GRANDE — mais mundo e mais corpo pro cerebro.

Gerador/wrapper de cidade grande (n=104 por padrao; 250 e 500 pedidos pelo
Leonardo em 2026-09-03) + preset `cfg_cidade_grande`. Tudo o que muda no
`lab.py` esta atras de flag com default = comportamento atual (blocos
`[E42 mundo]`); aqui so se MONTA a configuracao.

O que a cidade grande acrescenta:
  1. n nos (104/250/500), grafo CONEXO e d_posto <= 6 SALTOS (senao +postos,
     como o E34 — sem isso a cidade grande mata por geometria, nao por merito);
  2. D distritos espaciais (D = round(6*sqrt(n/104)): 6 / 9 / 13), com
     aliquota em [.05,.35], multiplicador de preco em [0.7,1.6] e multiplicador
     de aluguel em [0.5,2.0] sorteados da SEED DA TABELA (deterministico);
  3. passageiro que CRUZA distrito: destino ~ 1/(1+d) com no minimo 30 % da
     massa em outro distrito (cfg.pax_cruza) e tarifa x multiplicador de preco
     do distrito de ORIGEM (cfg.tarifa_distrito);
  4. MORADIA: m.casa = distrito de nascimento; descanso no distrito-casa e
     como hoje, fora custa HOTEL (x fator de preco do distrito); dormir na rua
     a noite nao repoe fadiga (cfg.rua_nao_dorme); sentidos novos `e_em_casa`
     e `e_aliq_local` nos slots reservados (ex-h_gl0/h_gl1).

DECISAO DECLARADA (desvio da spec §2.2): a TABELA de precos e por RODADA
(cfg), nao por cidade. A cfg e a mesma para as 4 cidades de treino e as 3 de
teste (tamanhos diferentes), entao uma tabela (NC,D) nao caberia num cfg unico.
O que varia por cidade/mundo e QUAL distrito recebe cada linha da tabela — isso
ja e sorteado POR MUNDO pelo E15 (`dist_sorteia`), que e a lei oculta: a
geografia do preco nao se decora entre episodios.

    NM_COMPILE=0 python src/cidade_grande.py        # testes (identidade, sync, fumaca)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from lab import GMAX, gerar_cidade as _gerar
from e19_pacote import cfg_pacote

N_PADRAO   = 104
MAX_SALTOS = 6
OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e42'


# ------------------------------------------------------------------ geometria
def n_distritos(n):
    """D = round(6*sqrt(n/104)): 104->6, 250->9, 500->13. Densidade de
    distritos ~ constante por area (a cidade cresce em area, nao em lista)."""
    return max(3, int(round(6*(n/104.)**0.5)))


def saltos(A, fontes):
    """BFS multi-fonte em SALTOS (nao em custo). Igual ao e34."""
    n = A.shape[0]; d = np.full(n, 10**6); fila = list(fontes)
    for f in fontes: d[f] = 0
    while fila:
        i = fila.pop(0)
        for j in A[i]:
            if j >= 0 and d[j] > d[i] + 1:
                d[j] = d[i] + 1; fila.append(int(j))
    return d


def componentes(A):
    """(n_componentes, rotulo por no)."""
    n = A.shape[0]; lab = -np.ones(n, dtype=np.int64); c = 0
    for s in range(n):
        if lab[s] >= 0: continue
        pilha = [s]; lab[s] = c
        while pilha:
            i = pilha.pop()
            for j in A[i]:
                if j >= 0 and lab[j] < 0:
                    lab[j] = c; pilha.append(int(j))
        c += 1
    return c, lab


def _adj_de(A):
    return [sorted(int(j) for j in A[i] if j >= 0) for i in range(A.shape[0])]


def _reconstruir(c, adj):
    """Refaz A/W/DI/grp/tem a partir da adjacencia (MESMA regra do
    lab.gerar_cidade). So roda se alguma aresta foi acrescentada."""
    pos = c['pos']; n = len(adj)
    D = np.hypot(pos[:,None,0]-pos[None,:,0], pos[:,None,1]-pos[None,:,1])
    np.fill_diagonal(D, 1e9)
    adj = [sorted(a)[:GMAX] for a in adj]
    A = np.full((n,GMAX), -1, dtype=np.int64)
    W = np.zeros((n,GMAX), dtype=np.float32)
    for i in range(n):
        for k, j in enumerate(adj[i]):
            A[i,k] = j; W[i,k] = max(1, round(D[i,j]/1.5))
    DI = np.full((n,n), 1e6, dtype=np.float32); np.fill_diagonal(DI, 0)
    for i in range(n):
        for k, j in enumerate(adj[i]): DI[i,j] = W[i,k]
    for k in range(n): DI = np.minimum(DI, DI[:,k:k+1] + DI[k:k+1,:])
    grp = np.zeros((n,GMAX), dtype=np.int64); tem = np.zeros(n, dtype=np.float32)
    for i in range(n):
        if len(adj[i]) >= 3:
            tem[i] = 1.0
            for k, j in enumerate(adj[i]):
                ang = np.arctan2(*(pos[j]-pos[i])[::-1]) % np.pi
                grp[i,k] = 0 if ang < np.pi/2 else 1
    c = dict(c); c.update(A=A, W=W, DI=DI, grp=grp, tem=tem)
    return c


def conectar(c):
    """Garante grafo CONEXO: liga cada componente ao no mais proximo do resto
    (respeitando GMAX). Em 60 sementes de n=104/250/500 nunca foi preciso — a
    verificacao fica porque DI de componentes separadas vale 1e6 e isso
    envenenaria TODA feature de distancia sem barulho nenhum."""
    nc, lab = componentes(c['A'])
    if nc == 1: return c, 0
    pos = c['pos']; adj = [set(a) for a in _adj_de(c['A'])]
    D = np.hypot(pos[:,None,0]-pos[None,:,0], pos[:,None,1]-pos[None,:,1])
    np.fill_diagonal(D, 1e9)
    add = 0
    while nc > 1:
        alvo = lab == lab[0]                     # componente que ja "existe"
        fora = ~alvo
        Dm = np.where(alvo[:,None] & fora[None,:], D, 1e9)
        # nao estourar o grau maximo
        cheio = np.array([len(a) >= GMAX for a in adj])
        Dm = np.where(cheio[:,None] | cheio[None,:], 1e9, Dm)
        i, j = np.unravel_index(int(np.argmin(Dm)), Dm.shape)
        if Dm[i, j] >= 1e9:                      # todos cheios: abre espaco no maior grau
            i = int(np.argmax([len(a) if alvo[k] else -1 for k, a in enumerate(adj)]))
            j = int(np.argmin(np.where(fora, D[i], 1e9)))
            adj[i].discard(max(adj[i], key=lambda x: D[i, x]))
        adj[i].add(int(j)); adj[j].add(int(i)); add += 1
        A2 = np.full((len(adj), GMAX), -1, dtype=np.int64)
        for k, a in enumerate(adj):
            for q, v in enumerate(sorted(a)[:GMAX]): A2[k, q] = v
        nc, lab = componentes(A2)
    return _reconstruir(c, [sorted(a) for a in adj]), add


def postos_ate(c, max_saltos=MAX_SALTOS, teto=64):
    """+1 posto no no MAIS LONGE (em saltos) enquanto alguem estiver a mais de
    `max_saltos` de um posto. Mesma ideia do E34, so que por criterio e nao por
    contagem: a cidade grande tem de ser sobrevivivel em qualquer semente."""
    serv = c['serv']; add = 0
    for _ in range(teto):
        d = saltos(c['A'], np.flatnonzero(serv[:,0] > 0))
        if d.max() <= max_saltos: break
        serv[int(np.argmax(d)), 0] = 1.0; add += 1
    return c, add


def gerar_cidade_grande(seed, n=N_PADRAO, max_saltos=MAX_SALTOS, **kw):
    """gerar_cidade(seed, n) + conexo + d_posto <= max_saltos saltos.
    numpy no HOST, fora do laco (0.02 s em n=104, 0.31 s em n=500)."""
    c = _gerar(seed, n=n, **kw)
    c, n_arestas = conectar(c)
    c, n_postos = postos_ate(c, max_saltos)
    c['e42'] = dict(seed=seed, n=n, arestas_add=n_arestas, postos_add=n_postos,
                    hop_posto_max=int(saltos(c['A'], np.flatnonzero(c['serv'][:,0] > 0)).max()),
                    postos=int((c['serv'][:,0] > 0).sum()))
    return c


# ------------------------------------------------------------------ distritos
def particao_distritos(pos, D):
    """MESMO k-means determinista do Lote (semente por ponto-mais-distante + 8
    Lloyd). Aqui so para diagnostico/telemetria — quem particiona de verdade e
    o lab.py."""
    p = pos
    ce = [int(np.argmax(((p - p.mean(0))**2).sum(1)))]
    for _ in range(D-1):
        dd = np.min(np.stack([((p - p[k])**2).sum(1) for k in ce]), 0)
        ce.append(int(np.argmax(dd)))
    C = p[ce].copy()
    for _ in range(8):
        lb = np.argmin(((p[:,None,:] - C[None,:,:])**2).sum(2), 1)
        for k in range(D):
            mk = lb == k
            if mk.any(): C[k] = p[mk].mean(0)
    return np.argmin(((p[:,None,:] - C[None,:,:])**2).sum(2), 1)


def _estratos(r, lo, hi, D):
    """D sorteios ESTRATIFICADOS em [lo,hi] (um por faixa de 1/D), embaralhados.
    Uniforme puro com D=6 sorteou aluguel medio 1.55 (nenhum distrito barato):
    o custo MEDIO da cidade virava sorte da semente e contaminaria a comparacao
    com o mundo do E20. Estratificado, a media e o meio da faixa em qualquer D
    e a HETEROGENEIDADE — que e o ponto dos distritos — fica garantida."""
    u = (np.arange(D) + r.random(D))/D
    return lo + (hi - lo)*r.permutation(u)


def tabela_distritos(D, seed=0):
    """(aliq, pmul, alug) por LINHA da tabela, ORDENADAS por fator de preco
    crescente (linha 0 = distrito mais barato — e o que o `e15_rank` da
    telemetria do E15 significa). Deterministico pela seed."""
    r = np.random.default_rng(seed + 4242)
    aliq = _estratos(r, .05, .35, D)          # media .20 (= o meio do E15)
    pmul = _estratos(r, .70, 1.60, D)         # media 1.15
    alug = _estratos(r, .50, 2.00, D)         # media 1.25
    o = np.argsort(pmul*(1.+aliq))            # 0 = mais barato para gastar
    f = lambda v: tuple(round(float(x), 4) for x in v[o])
    return f(aliq), f(pmul), f(alug)


# --------------------------------------------------------------------- preset
def cfg_cidade_grande(n=N_PADRAO, D=None, seed_tabela=0, moradia=True, hotel=8.,
                      pax_cruza=.30, tarifa_distrito=True, rua_nao_dorme=True,
                      fome=.15, refeicao=90., comida_no_posto=True, **kw):
    """cfg_pacote(fome=.15, refeicao=90., comida_no_posto=True) — o mundo do
    E19d/E20 — + cidade grande (n nos, D distritos com tabela sorteada) +
    moradia. Passar moradia=False/pax_cruza=0/tarifa_distrito=False devolve o
    mundo do E20 com D distritos (util como controle)."""
    D = n_distritos(n) if D is None else D
    aliq, pmul, alug = tabela_distritos(D, seed_tabela)
    c = cfg_pacote(fome=fome, refeicao=refeicao, comida_no_posto=comida_no_posto,
                   D=D, aliq=aliq, pmul=pmul, **kw)
    c.n_cidade = n                      # so documental (o gerador e quem decide)
    c.ALUGUEL_D = alug
    c.moradia = bool(moradia); c.HOTEL = hotel
    c.pax_cruza = float(pax_cruza)
    c.tarifa_distrito = bool(tarifa_distrito)
    c.rua_nao_dorme = bool(rua_nao_dorme)
    return c


def resumo_cidade(c, D):
    """nos por distrito (para o doc: a particao nao pode sair degenerada)."""
    lb = particao_distritos(c['pos'], D)
    d = dict(c.get('e42', {}))
    d.update(n=int(c['n']), D=D,
             nos_por_distrito=[int((lb == k).sum()) for k in range(D)])
    return d


def telemetria_grande(m, T):
    """telemetria do E19/E20 + o que a cidade grande acrescenta."""
    from e19_pacote import telemetria as _tel
    d = _tel(m, T)
    f = lambda x: round(float(x.mean()), 3)
    if getattr(m.cfg, 'economia', False):
        d.update(div_frac=f(m.t_divida/T), div_max=f(m.div_max),
                 imp_receber=f(m.imp_orig), imp_gastar=f(m.imp_gastar),
                 aluguel_agua=f(m.aluguel_pago), renda_bruta=f(m.rec))
    if getattr(m.cfg, 'moradia', False):
        d.update(casa_frac=f(m.t_casa/T), n_hotel=f(m.n_hotel),
                 hotel_pago=f(m.e42_hotel), n_rua=f(m.n_rua),
                 ent_cruza=f(m.ent_cruza),
                 cruza_frac=round(float(m.ent_cruza.sum()/m.ent.sum().clamp(min=1.)), 3))
    return d


# ---------------------------------------------------------------------- testes
def _testes():
    import torch
    from lab import DEV, Cfg, Reativo, rodar, um_passo, Lote
    from rodar import perito_W
    from e19_pacote import cfg_pacote as _cfgp

    print('--- E42 cidade grande: testes ---')
    # 1. geometria
    for n in (104, 500):
        D = n_distritos(n)
        for sd in (0, 1, 1000, 1026):
            c = gerar_cidade_grande(sd, n=n)
            r = resumo_cidade(c, D)
            assert componentes(c['A'])[0] == 1, f'n={n} seed={sd}: grafo desconexo'
            assert r['hop_posto_max'] <= MAX_SALTOS, f'n={n} seed={sd}: {r}'
            assert float(c['DI'].max()) < 1e5, f'n={n} seed={sd}: DI infinito'
            assert min(r['nos_por_distrito']) >= 1
        print(f'  n={n:>3} D={D:<2} conexo, d_posto<=6 saltos, distritos nao-vazios '
              f'(seed 1026: {resumo_cidade(gerar_cidade_grande(1026, n=n), D)})  OK')

    # 2. IDENTIDADE: as flags novas desligadas nao mudam nada (bit a bit)
    teste = [gerar_cidade_grande(1000+s, n=104) for s in range(2)]
    W = perito_W(Reativo.NP)[None,:].repeat(32,1)
    off = _cfgp(fome=.15, refeicao=90., comida_no_posto=True, D=6,
                aliq=(.1,.15,.2,.25,.3,.35), pmul=(.7,.8,1.,1.2,1.4,1.6))
    on = cfg_cidade_grande(n=104, moradia=False, pax_cruza=0., tarifa_distrito=False,
                           rua_nao_dorme=False, D=6)
    on.ALIQ = off.ALIQ; on.PMUL = off.PMUL; on.ALUGUEL_D = None
    a = rodar(Reativo, W, teste, off, T=400, seed=7777)
    b = rodar(Reativo, W, teste, on,  T=400, seed=7777)
    for k in ('ent','avar','av_fuel','dinh','fuel','vida','rec','res','fome','fad'):
        x, y = getattr(a, k), getattr(b, k)
        assert torch.equal(x, y), f'IDENTIDADE quebrada em {k}: {float(x.mean())} vs {float(y.mean())}'
    print('  flags E42 desligadas == mundo do E20 com D=6 (bit a bit, 10 campos)  OK')

    # 3. as flags LIGADAS mudam o mundo (senao o teste 2 nao prova nada)
    cfg = cfg_cidade_grande(n=104)
    c = rodar(Reativo, W, teste, cfg, T=400, seed=7777)
    assert not torch.equal(c.ent, a.ent), 'cidade grande == controle: flags inertes'
    assert float(c.n_hotel.sum()) + float(c.t_casa.sum()) > 0
    assert torch.isfinite(c.dinh).all() and torch.isfinite(c.fuel).all()
    print(f'  moradia LIGADA muda o mundo (ent {float(a.ent.mean()):.2f} -> '
          f'{float(c.ent.mean()):.2f}; hotel {float(c.n_hotel.mean()):.2f}; '
          f'casa_frac {float((c.t_casa/400).mean()):.2f})  OK')

    # 4. SEM SYNC no laco quente (o portao que pega .item()/if tensor escondido)
    if DEV == 'cuda':
        for n in (104, 500):
            cids = [gerar_cidade_grande(s, n=n) for s in range(2)]
            cfg = cfg_cidade_grande(n=n)
            m = Lote(cids, 4, cfg, seed=1, R=1)
            Wb = perito_W(Reativo.NP)[None,:].repeat(m.B,1)
            ar = Reativo(); ar.reset(m, Wb)
            for _ in range(5): um_passo(m, ar, Wb); ar.atualizar(m)
            torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode('error')
            try:
                for _ in range(10): um_passo(m, ar, Wb); ar.atualizar(m)
                torch.cuda.synchronize()
            finally:
                torch.cuda.set_sync_debug_mode('default')
            print(f'  n={n:>3}: 10 passos sem NENHUM sync CPU<->GPU  OK')
    print('ok')


if __name__ == '__main__':
    _testes()
