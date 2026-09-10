"""[CS DERIVA §3-5: 'ler os pesos, nao so as metricas'] RETRATO de uma bateria (e43_*.json): para cada braco SerCompleto (NP 765/59x) e
semente, os genes que dizem o que o cerebro FAZ: portoes do talamo por grupo (necessidade 0 e .8), reflexo (w = empurrao ao posto, v =
liga abastecer, theta), ganho do hipocampo, |delta| max do cortex, dof por bloco. E a DELEGACAO talamo<->reflexo: correlacao entre o
portao de servicos e w sobre os genomas (CS: rho = -.76, n = 10 em e77). Roda na fila (segundos)."""
import sys, os, json, argparse, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import DEV, Linear, CfgCampo, dof_por_bloco; from completo import SerCompleto, NG, NOMES_G
ap = argparse.ArgumentParser(); ap.add_argument('--bateria', required=True); ap.add_argument('--out', default=None); a = ap.parse_args()
d = json.load(open(a.bateria)); A = SerCompleto; o_t, o_r, o_c, o_h = A.O_TAL, A.O_REF, A.O_COR, A.O_HIP; cfg = CfgCampo(L=200.)
def pear(x, y):
    n = len(x); mx, my = sum(x)/n, sum(y)/n; sx = math.sqrt(sum((v-mx)**2 for v in x)); sy = math.sqrt(sum((v-my)**2 for v in y)); return sum((p-mx)*(q-my) for p, q in zip(x, y))/(sx*sy) if sx > 0 and sy > 0 else float('nan')
def spear(x, y):
    r = lambda v: [sorted(v).index(t) for t in v]; return pear(r(x), r(y))
print(f'RETRATO {os.path.basename(a.bateria)}', flush=True); print(f'  {"braco":26} {"sem":>3} ' + ' '.join(f'{g[:7]:>7}' for g in NOMES_G) + f' {"soma":>5} {"serv@.8":>7} {"ref_w":>6} {"ref_v":>6} {"theta":>5} {"hip_g":>5} {"cor|d|":>6} {"dof":>5}', flush=True)
pontos = []; saida = {}
for nome, med in d['bracos'].items():
    if 'W' not in med: continue
    for sd, w in med['W'].items():
        W = torch.tensor(w, device=DEV)
        if W.numel() != A.NP: continue
        G3 = W[o_t:o_t+A.N_TAL].reshape(NG, 3); g0 = 2.*torch.sigmoid(G3[:, 0]); g8 = 2.*torch.sigmoid(G3[:, 0] + .8*G3[:, 1])
        rw, rv, th = float(W[o_r+1]), float(W[o_r+2]), float(torch.sigmoid(W[o_r+3])); hg = float(torch.tanh(W[o_h+1])); cd = float((.5*torch.tanh(W[o_c:o_c+A.N_COR])).abs().max()); dof = float((W[Linear.NP:].abs() > cfg.gene_min).float().mean())
        js = NOMES_G.index('servicos'); pontos.append((nome, float(g0[js]), rw)); saida[f'{nome}|{sd}'] = dict(gates_soma=float(g0.sum()), gates0=[float(x) for x in g0], gates8=[float(x) for x in g8], ref_w=rw, ref_v=rv, theta=th, hip_g=hg, cor_dmax=cd, dof=dof)
        print(f'  {nome[:26]:26} {str(sd):>3} ' + ' '.join(f'{float(x):7.2f}' for x in g0) + f' {float(g0.sum()):5.2f} {float(g8[js]):7.2f} {rw:6.2f} {rv:6.2f} {th:5.2f} {hg:5.2f} {cd:6.2f} {dof:5.2f}', flush=True)
if len(pontos) >= 4:
    xs = [p[1] for p in pontos]; ys = [p[2] for p in pontos]; print(f'  DELEGACAO (todos, n={len(pontos)}): corr(portao servicos, reflexo w) pearson {pear(xs, ys):+.2f} spearman {spear(xs, ys):+.2f}   (CS em e77: rho -.76)', flush=True)
    for nome in sorted(set(p[0] for p in pontos)):
        xs = [p[1] for p in pontos if p[0] == nome]; ys = [p[2] for p in pontos if p[0] == nome]
        if len(xs) >= 4: print(f'    dentro de {nome[:30]} (n={len(xs)}): pearson {pear(xs, ys):+.2f} spearman {spear(xs, ys):+.2f}', flush=True)
    saida['_delegacao'] = dict(n=len(pontos), pearson=pear([p[1] for p in pontos], [p[2] for p in pontos]), spearman=spear([p[1] for p in pontos], [p[2] for p in pontos]))
if a.out: os.makedirs(a.out, exist_ok=True); p = os.path.join(a.out, 'retrato_' + os.path.basename(a.bateria)); json.dump(saida, open(p, 'w'), indent=1); print('gravado', p, flush=True)
