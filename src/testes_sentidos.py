"""PORTAO DE SENSIBILIDADE (Leonardo, 2026-09-07: 'valide melhor'): para cada arquitetura, cada sentido de ENTRADA tem de poder
mudar a DIRECAO (posicoes) e/ou o SERVICO (acoes >= G). Perturba so os genes ligados ao sentido e mede se as posicoes/escolhas mudam.
Teria pego em 30 s o achado 84 (no Linear, os 16 sentidos do corpo sao invisiveis na direcao). Sai uma matriz sentido x arquitetura."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *; from completo import SerCompleto
os.environ['NM_COMPILE'] = '0'; c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000, L=200., distinto=True)]
NOP = len(NOMES_OP)
def roda(A, W, T=240):
    m = Campo(mapas, W.shape[0], c, seed=3, R=2); Wb = W[m.gidx]; a = A(); a.reset(m, Wb); escs = []
    for t in range(T):
        F, val = m.obs(); sc = torch.einsum('bgf,bf->bg', F, Wb[:, :NF]) + a.extra(m, Wb, F); sc = sc - sc.mean(1, keepdim=True)
        svn, sv = m.serv_need(); ss = svn*Wb[:, NF:NF+S] + Wb[:, NF+S:NF+S+1]
        if hasattr(a, 'extra_serv'): ss = ss + a.extra_serv(m)
        ss = ss.masked_fill(sv <= 0, -1e9); esc = torch.cat([sc, ss], 1).argmax(1); escs.append(esc); m.passo(esc); a.atualizar(m)
    return m.pos.clone(), torch.stack(escs)
def genes_do_sentido(A, k):
    """indices de genes que leem o sentido k (coluna k de F): coluna k do movimento linear + colunas k das matrizes extras conhecidas."""
    idx = [k]
    if hasattr(A, 'O_M') and hasattr(A, 'K') and hasattr(A, 'O_U'):      # Cerebro/completo: U (H x NF) e M (K x NF)
        H, K = A.H, A.K; idx += [A.O_U + h*NF + k for h in range(H)] + [A.O_M + j*NF + k for j in range(K)]
        if k >= NOP: idx += [A.O_U2 + j*A.NC_ + (k - NOP) for j in range(K)]                          # U2 le so o corpo
    if hasattr(A, 'O_HIP'): idx += [A.O_HIP + 2 + j*NF + k for j in range(3)]                         # hipocampo M_h
    if A.__name__ in ('Bilinear',) or 'bilinear' in getattr(A, 'nome', ''):
        M0 = Linear.NP; nc = getattr(A, 'IDX', None)
        if k >= NOP:
            ks = [k - NOP] if nc is None else ([int((nc == (k - NOP)).nonzero()[0])] if bool((nc == (k - NOP)).any()) else [])
            for kk in ks: idx += [M0 + kk*NOP + f for f in range(NOP)]
        else:
            nk = A.NC_ if nc is None else int(nc.numel()); idx += [M0 + kk*NOP + k for kk in range(nk)]
    return [i for i in idx if i < A.NP]
ARQS = [('Linear', Linear), ('Bilinear', Bilinear), ('Bilinear auto+cons', fabrica_bilinear(['e_autonomia', 'e_consumo'])), ('Reflexo', Reflexo), ('Completo', SerCompleto)]
print(f"{'sentido':<14}" + ''.join(f"{n[:14]:>16}" for n, _ in ARQS), flush=True); invisiveis = {}
for k, nome in enumerate(NOMES_F[:NF]):
    linha = f"{nome:<14}"
    for n, A in ARQS:
        torch.manual_seed(0); W = torch.randn(12, A.NP, device=DEV)*.5
        p0, e0 = roda(A, W); Wk = W.clone(); g = genes_do_sentido(A, k)
        Wk[:, g] += torch.randn(12, len(g), device=DEV)*3.
        p1, e1 = roda(A, Wk); dpos = float((p0 - p1).abs().max()); dserv = float(((e0 >= G) != (e1 >= G)).float().mean())
        tag = ('dir' if dpos > 1. else '---') + ('/srv' if dserv > .005 else '/---'); linha += f"{tag:>16}"
        if dpos <= 1. and dserv <= .005: invisiveis.setdefault(n, []).append(nome)
    print(linha, flush=True)
for n, ls in invisiveis.items(): print(f"INVISIVEL em {n}: {ls}", flush=True)
esperado_linear = set(NOMES_CORPO) - {'bias'}
print('PORTAO SENTIDOS', 'ok' if not invisiveis.get('Bilinear') and not invisiveis.get('Completo') else 'FALHOU (Bilinear/Completo com sentido invisivel)', '| Linear corpo invisivel na direcao (achado 84):', set(invisiveis.get('Linear', [])) >= esperado_linear - {'e_tem_pax'}, flush=True)
