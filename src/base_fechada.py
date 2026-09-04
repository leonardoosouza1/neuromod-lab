"""E45 BASE FECHADA (ideia do Leonardo, 2026-09-04): W_base por formula fechada (ridge) a partir de um PROFESSOR de utilidade
de um passo, no campo. Politica linear/bilinear = nota Phi.W  =>  W* = (Phi^T Phi + lambda I)^-1 Phi^T Y. A evolucao nasce
de W_base + ruido e so aprende o que o professor nao ve (horizonte, noite, poupanca, distrito).
Professor (por opcao g, tudo em forma fechada a partir de obs() e do estado): utilidade = ganho esperado um passo a frente em
(vida, fome, agua, tanque, dinheiro), com pesos fixos; servicos: utilidade do que compram; movimento: reducao ponderada das
distancias ao que FALTA. Y e a utilidade centrada por linha (argmax e invariante a deslocamento)."""
import sys, os, json, time, argparse
os.environ.setdefault('TORCHINDUCTOR_COMPILE_THREADS', '1')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch
from campo import *

def utilidade_professor(m, F):
    """(B,G+S): utilidade de um passo de cada opcao. Movimento: -sum_k need_k * d_k(g) (necessidade guia); servicos: o que resolvem."""
    B = m.B; c = m.cfg
    need = torch.stack([1. - m.fuel/100., 1. - m.agua/100., m.fome/100., .35 + .5*(1. - (m.dinh/60.).clamp(0., 1.))], 1)   # tanque, agua, fome, alvo (mais quando pobre)
    need = need.clamp(min=0.)**2                                                                            # concavo: o que falta MUITO manda
    D = F.index_select(2, torch.tensor([1, 3, 2, 0], device=DEV))                                            # d_posto, d_agua, d_comida, d_alvo (B,G,4)
    dD = D - D[:, G-1:G, :]                                                                                  # variacao da distancia vs FICAR (opcao 8): ~ -1..+1 por passo
    u_mov = -(dD*need[:, None, :]).sum(-1)/need.sum(1, keepdim=True).clamp(min=1e-3) - .1*(F[:, :, 6] - F[:, G-1:G, 6])   # media ponderada pela necessidade; custo a frente
    u_mov = u_mov - .2*(torch.arange(G, device=DEV) == G-1).float()[None, :]*(need[:, :3].sum(1, keepdim=True) < .3).float()   # ficar parado sem necessidade e ruim (marcha lenta)
    svn, sv = m.serv_need(); pm = m.serv_ab()[1]; cs = m.custos(pm)
    cabe = (100. - m.fuel); res_ok = (c.RES_MAX - m.res).clamp(min=0.)
    ganho = torch.stack([torch.minimum(torch.full_like(cabe, q), cabe)/100. + .3*torch.minimum((q - cabe).clamp(min=0.), res_ok)/100. for q in (25., 50., 75., 100., 150.)] +
                        [torch.minimum(torch.full_like(cabe, q), 100. - m.agua)/100. for q in (50., 100.)] +
                        [torch.minimum(torch.full_like(cabe, c.REFEICAO), m.fome)/100., (m.fad/100.)**2, ((100. - m.vida)/100.)**2], 1)   # (B,S)
    peso = torch.tensor([3., 3., 3., 3., 3., 3., 3., 4., 1., 2.], device=DEV)                                     # tanque, agua, comida, fadiga, oficina
    escasso = 3./(m.dinh.clamp(min=2.) + 3.)                                                                   # v3: dinheiro curto = comprar doi (quebrar mata por divida)
    u_srv = ganho*peso[None, :]*need_srv(m) - cs*escasso[:, None]*.5 - 8.*(sv <= 0).float()                    # caro pesa pela escassez; indisponivel e proibido
    U = torch.cat([u_mov, u_srv], 1)
    return U

def need_srv(m):
    """multiplica o ganho do servico pela necessidade AO QUADRADO (so vale a pena quando falta)"""
    B = m.B
    n = torch.stack([(1. - m.fuel/100.)]*5 + [(1. - m.agua/100.)]*2 + [m.fome/100., m.fad/100., (1. - m.vida/100.)], 1).clamp(min=0.)
    return n**2 + .05

def coletar(mapas, cfg, n_est=200_000, T=1200, seed=11, W_pro=None):
    """estados de rastros: politica do professor (argmax da utilidade) com ruido; devolve Phi (N,NP_lin) e Y (N,G+S) centrado."""
    P = max(1, n_est//(len(mapas)*16*T)) or 1
    m = Campo(mapas, P, cfg, seed=seed, R=16); B = m.B
    g = torch.Generator(device=DEV); g.manual_seed(seed)
    Phis, Ys = [], []
    t0 = time.time()
    for t in range(T):
        if t % 400 == 0: print(f'  [professor] passo {t}/{T} {time.time()-t0:.0f}s vivos {float((m.vida>0).float().mean()):.2f} ent {float(m.ent.mean()):.1f}', flush=True)
        F, val = m.obs()
        if W_pro is not None:      # clonagem: Y = notas do campeao linear (movimento centrado + servico), como um_passo as calcula
            Wb = W_pro[None, :].expand(B, -1); sc = torch.einsum('bgf,bf->bg', F, Wb[:, :NF]); sc = sc - sc.mean(1, keepdim=True)
            svn_, sv_ = m.serv_need(); ss = (svn_*Wb[:, NF:NF+S] + Wb[:, NF+S:NF+S+1]).masked_fill(sv_ <= 0, -1e9); U = torch.cat([sc, ss], 1)
        else:
            U = utilidade_professor(m, F)
        svn, sv = m.serv_need()
        # Phi da politica linear: features por opcao (B,G,NF) + servicos (B,S) com need*sv e bias
        Phi_mov = F                                                                       # (B,G,NF)
        Phi_srv = torch.cat([svn, torch.ones(B, 1, device=DEV)], 1)                       # (B,S+1)
        if t % 4 == 0:
            Phis.append((Phi_mov.detach(), Phi_srv.detach())); Ys.append(U.detach())
        esc = (U + .15*torch.randn(B, G + S, generator=g, device=DEV)).argmax(1)        # professor com ruido pequeno (as diferencas por opcao sao ~0.1-1)
        m.passo(esc)
    return Phis, Ys, m

def resolver(Phis, Ys, lam=1e-2):
    """ridge separado: movimento (NF genes: Y_mov centrado por linha ~ F.W) e servicos (S+1 genes: Y_srv ~ [svn,1].W)."""
    Fm = torch.cat([p[0] for p in Phis]).reshape(-1, NF); Ym = torch.cat([y[:, :G] for y in Ys])
    Ym = (Ym - Ym.mean(1, keepdim=True)).reshape(-1)
    A = Fm.T @ Fm + lam*torch.eye(NF, device=DEV); Wm = torch.linalg.solve(A, Fm.T @ Ym)
    Fs = torch.cat([p[1] for p in Phis]); Ys_ = torch.cat([y[:, G:] for y in Ys])
    # servicos: nota_k = svn_k * w_k + b  -> resolver w_k por coluna (diagonal) e b comum: minimos quadrados por coluna
    ws = []
    for k in range(S):
        x = Fs[:, k]; y = Ys_[:, k]; msk = x > 0
        ws.append(float(((x[msk]*y[msk]).sum())/((x[msk]*x[msk]).sum() + lam)) if bool(msk.any()) else 0.)
    b = float((Ys_ - Fs[:, :S]*torch.tensor(ws, device=DEV)[None, :]).mean())
    W = torch.cat([Wm, torch.tensor(ws, device=DEV), torch.tensor([b], device=DEV)])
    # escala comum: notas de movimento (centradas) e de servico precisam competir na mesma unidade -> normaliza pelo desvio de Y_mov
    return W

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--L', type=float, default=200.); ap.add_argument('--dias', type=float, default=10.); ap.add_argument('--fitness', default='bemestar')
    ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e45'); ap.add_argument('--tag', default=''); ap.add_argument('--G', type=int, default=25); ap.add_argument('--seeds', type=int, nargs='*', default=[0])
    ap.add_argument('--professor', nargs=2, default=None, metavar=('JSON', 'BRACO'), help='clonagem: campeao evoluido como professor (Y = notas dele)')
    a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); T = int(240*a.dias)
    cfg = CfgCampo(L=a.L, fitness=a.fitness); treino = [gerar_mapa(s, L=a.L) for s in range(4)]; teste = [gerar_mapa(1000 + s, L=a.L) for s in range(3)]
    W_pro = None
    if a.professor:
        Jp = json.load(open(a.professor[0]))['bracos'][a.professor[1]]; W_pro = torch.tensor(Jp['W'][sorted(Jp['W'])[0]], device=DEV)[:Linear.NP].clone()
        if a.professor[1].startswith('minimo'):     # o minimo-3 ZERA os sentidos proibidos ao decidir: clonar exige a mesma mascara nos pesos crus
            perm = [NOMES_F.index(n) for n in ('d_alvo', 'd_posto', 'e_fuel')]; msk = torch.zeros(NF, device=DEV); msk[perm] = 1.; W_pro[:NF] = W_pro[:NF]*msk
        print(f'professor = campeao {a.professor[1]} (clonagem de comportamento)', flush=True)
    t0 = time.time(); Phis, Ys, m_pro = coletar(treino, cfg, T=T, W_pro=W_pro)
    print(f'== E45 base fechada | L={a.L} dias={a.dias} | professor: {sum(p[0].shape[0] for p in Phis)} estados em {time.time()-t0:.0f}s | professor puro: mortos {float((m_pro.vida<=0).float().mean()):.2f} ent {float(m_pro.ent.mean()):.1f} come {float(m_pro.n_come.mean()):.1f} abast {float(m_pro.n_posto.mean()):.1f}', flush=True)
    if float((m_pro.vida <= 0).float().mean()) >= .8:
        print('PROFESSOR MORRE (>= 0.8): base nao ajustada — corrigir o professor antes de julgar a ideia (clausula da predicao 62)', flush=True); return
    t0 = time.time(); W = resolver(Phis, Ys); print(f'ridge: {time.time()-t0:.1f}s | |W| {float(W.abs().mean()):.2f}', flush=True)
    med = medidas(Linear, W, teste, cfg, T=T, seed=7777, R=1, copias=128)
    print(f"  base fechada sozinha (linear)         fit {med['fit']:6.2f} mortos {med['mortos']:.2f} ent {med['ent']:5.1f} panes {med['panes']:4.1f} fome {med['fome_fim']:3.0f} agua {med['agua_fim']:3.0f} dinh {med['dinh']:4.0f} L/abast {med['litros_por_abast']:4.0f} abast {med['n_posto']:4.1f}", flush=True)
    res = dict(L=a.L, dias=a.dias, fitness=a.fitness, W_base=[round(float(x), 5) for x in W], base=med, bracos={})
    for nome, W0 in (('do zero', None), ('semeado da base', {sd: W for sd in a.seeds})):
        t1 = time.time(); champs = evoluir(Linear, treino, cfg, P=512, ger=a.G, T=T, seeds=tuple(a.seeds), R=4, verbose=False, W0=W0, sigma0=.2)
        por = {sd: medidas(Linear, champs[sd][0], teste, cfg, T=T, seed=7777, R=1, copias=128) for sd in a.seeds}
        med = {k: sum(por[sd][k] for sd in a.seeds)/len(a.seeds) for k in por[a.seeds[0]]}; med['W'] = {sd: [round(float(x), 5) for x in champs[sd][0]] for sd in a.seeds}; med['segundos'] = round(time.time() - t1)
        res['bracos'][nome] = med
        print(f"  {nome:<36} G={a.G} fit {med['fit']:6.2f} mortos {med['mortos']:.2f} ent {med['ent']:5.1f} panes {med['panes']:4.1f} fome {med['fome_fim']:3.0f} agua {med['agua_fim']:3.0f} dinh {med['dinh']:4.0f} abast {med['n_posto']:4.1f} ({med['segundos']}s)", flush=True)
        json.dump(res, open(os.path.join(a.out, f'e45{a.tag}.json'), 'w'), indent=1)

if __name__ == '__main__': main()
