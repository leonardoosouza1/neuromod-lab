"""CLONE POR FORMA FECHADA de uma politica EXPLICITA num cerebro Linear (degrau 3 da analise externa 09/09; pred 122/134).
Coleta estados ao longo da trajetoria da propria politica (mapas de TREINO), Y = escolha dela (one-hot; servico indisponivel = -1e9),
Phi = features do Linear (F por opcao + [svn, 1]); W* por ridge (resolver de base_fechada); fidelidade = % de estados em que o clone
decide igual; depois mede o clone no mundo do juiz (mapas de teste) e grava W em formato --init-from (bracos.clone.W[semente])."""
import sys, os, json, time, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from politica_util import *; from base_fechada import resolver, fidelidade
ap = argparse.ArgumentParser(); ap.add_argument('--politica', required=True); ap.add_argument('--cenario', default=None); ap.add_argument('--P', type=int, default=2, help='seres por mapa x16 (P=2 -> 128 seres)')
ap.add_argument('--T', type=int, default=2400); ap.add_argument('--lam', type=float, default=1e-2); ap.add_argument('--seeds', type=int, nargs='*', default=[7777, 7778, 7779])
ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/agentes'); ap.add_argument('--tag', default='')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
cfg, teste, T, chave = mundo(a.cenario); treino = [gerar_mapa(s, L=cfg.L, distinto=True) for s in range(4)]
POL, erro = carrega(a.politica); assert not erro, erro
m = Campo(treino, a.P, cfg, seed=11, R=16); B = m.B; Wz = torch.zeros(B, Linear.NP, device=DEV); pol = POL(); pol.reset(m, Wz); Phis, Ys = [], []; t0 = time.time()
print(f'== clone | {os.path.basename(a.politica)} | coleta {B} seres x {a.T} ticks em 4 mapas de treino ==', flush=True)
for t in range(a.T):
    F, val = m.obs(); sc = pol.extra(m, Wz, F); svn, sv = m.serv_need(); ss = torch.zeros(B, S, device=DEV).masked_fill(sv <= 0, -1e9); tudo = torch.cat([sc, ss], 1)
    esc = pol.decidir(tudo, m).long().clamp(0, G + S - 1)
    Y = torch.zeros(B, G + S, device=DEV); Y[torch.arange(B, device=DEV), esc] = 1.; Y[:, G:] = Y[:, G:].masked_fill(sv <= 0, -1e9)
    if t % 4 == 0: Phis.append((F.detach(), torch.cat([svn, torch.ones(B, 1, device=DEV)], 1).detach())); Ys.append(Y.detach())
    m.passo(esc); pol.atualizar(m)
    if t % 800 == 0: print(f'  passo {t} {time.time()-t0:.0f}s vivos {float((m.vida > 0).float().mean()):.2f} ent {float(m.ent.mean()):.1f}', flush=True)
n = sum(y.shape[0] for y in Ys); print(f'  {n} estados coletados; politica no treino: mortos {float((m.vida <= 0).float().mean()):.2f} ent {float(m.ent.mean()):.1f}', flush=True)
W = resolver(Phis, Ys, lam=a.lam); fid = fidelidade(Phis, Ys, W); print(f'ridge lam {a.lam}: fidelidade do clone linear = {100*fid:.1f} % dos estados (movimento+servico) | |W| {float(W.abs().mean()):.2f}', flush=True)
Fm = torch.cat([p[0] for p in Phis]); Ym = torch.cat([y[:, :G] for y in Ys]); scm = torch.einsum('bgf,f->bg', Fm, W[:NF]); scm = scm - scm.mean(1, keepdim=True)
mov = Ym.argmax(1) < G; fid_mov = float((scm.argmax(1)[mov] == Ym.argmax(1)[mov]).float().mean()); print(f'  fidelidade so no MOVIMENTO (estados em que a politica moveu): {100*fid_mov:.1f} %', flush=True)
med = mede(Linear, W, cfg, teste, T, a.seeds); print('  ' + linha('CLONE linear no mundo do juiz', med), flush=True)
J = dict(politica=a.politica, cenario=a.cenario, fidelidade=fid, fidelidade_mov=fid_mov, n_estados=n, lam=a.lam, clone=med, bracos={'clone': {'W': {str(s): [round(float(x), 5) for x in W] for s in range(5)}, 'mortos': med['mortos']}})
json.dump(J, open(os.path.join(a.out, f'clone{a.tag}.json'), 'w'), indent=1); print('gravado', os.path.join(a.out, f'clone{a.tag}.json'), flush=True)
