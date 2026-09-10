"""[CS JARDIM-COMUM §5: comparar DECISOES, nao so desfechos] Dois bracos (campeoes de uma bateria e43_*.json, mesma semente) rodam nos
MESMOS blocos do jardim comum (berco, passageiros, destinos iguais) com gravacao de acoes por tique. Por bloco: concordancia de acao
(fracao dos tiques em que escolhem a mesma opcao, enquanto ambos vivos), tique da 1a divergencia e o ESTADO do ser de referencia nesse
tique (fome, gasolina, agua, dinheiro, posicao, vida), quem viveu mais (pareado). Histograma de acoes por braco (estrategia). GPU."""
import sys, os, json, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from politica_util import mundo, braco; from e43_campo import BRACOS
ap = argparse.ArgumentParser(); ap.add_argument('--bateria', required=True); ap.add_argument('--ref', default='linear'); ap.add_argument('--bracos', nargs='*', default=None); ap.add_argument('--seeds', type=int, nargs='*', default=None)
ap.add_argument('--R', type=int, default=8); ap.add_argument('--T', type=int, default=None); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e72'); a = ap.parse_args()
d = json.load(open(a.bateria)); cfg, teste, T0, chave = mundo(d.get('cenario')); T = a.T or (int(cfg.T_max) if getattr(cfg, 'horizonte', 'fixo') == 'aberto' else T0)
cfg.jardim_comum = True; cfg.grava_acoes = True; bracos = a.bracos or [b for b in d['bracos'] if b != a.ref and 'W' in d['bracos'][b]]; seeds = a.seeds or [int(s) for s in d['bracos'][a.ref]['W']]
NOMES = NOMES_OP[:G] if len(NOMES_OP) >= G else [f'mov{i}' for i in range(G)]; NOMES = [f'm{i}' for i in range(G)] + list(ACOES) if 'ACOES' in globals() else [f'op{i}' for i in range(G + S)]
def roda(nome, sd):
    W = torch.tensor(d['bracos'][nome]['W'][str(sd)], device=DEV)[None, :]; A_, c_ = braco(d, nome, cfg); m = rodar(A_, W, teste, c_, T, seed=7777, R=a.R); return m
print(f'TRAJETORIA {os.path.basename(a.bateria)} | ref {a.ref} vs {bracos} | sementes {seeds} | jardim NC {len(teste)} x R {a.R} = {len(teste)*a.R} blocos | T {T}', flush=True)
saida = {}; saida_med = {}
for nome in bracos:
    conc = []; tdiv = []; est = []; vive = []; hist_r = torch.zeros(G + S, device=DEV); hist_b = torch.zeros(G + S, device=DEV)
    for sd in seeds:
        mr = roda(a.ref, sd); mb = roda(nome, sd); NBk = mr.B
        vivos = (mr.traj[:, :, 6] > 0) & (mb.traj[:, :, 6] > 0); ig = (mr.acoes == mb.acoes) & vivos
        c = ig.float().sum(0)/vivos.float().sum(0).clamp(min=1.); conc += c.tolist()
        dif = (~ig) & vivos; td = torch.where(dif.any(0), dif.float().argmax(0), torch.full((NBk,), T, device=DEV)); tdiv += td.tolist()
        idx = td.clamp(max=T-1); est += mr.traj[idx, torch.arange(NBk, device=DEV)].tolist(); vive += (mb.t_vida > mr.t_vida).float().tolist()
        for m_, h in ((mr, hist_r), (mb, hist_b)):
            ac = m_.acoes[(m_.traj[:, :, 6] > 0)]; h += torch.bincount(ac[ac >= 0], minlength=G + S).float()
        for m_, k in ((mr, 'ref'), (mb, 'braco')):
            viv = m_.traj[:, :, 6] > 0; n = viv.float().sum(0).clamp(min=1.); mu = (m_.traj[:, :, 4:6]*viv[:, :, None]).sum(0)/n[:, None]
            raio = ((((m_.traj[:, :, 4:6] - mu[None])**2).sum(-1)*viv).sum(0)/n).sqrt(); parado = ((m_.acoes == G - 1) & viv).float().sum(0)/n
            medidas_k = saida_med.setdefault(nome, {}).setdefault(k, dict(raio=[], parado=[])); medidas_k['raio'] += raio.tolist(); medidas_k['parado'] += parado.tolist()
    e = torch.tensor(est); hist_r = hist_r/hist_r.sum(); hist_b = hist_b/hist_b.sum()
    print(f'  {a.ref} vs {nome[:30]}: concordancia media {sum(conc)/len(conc):.3f} | 1a divergencia mediana {sorted(tdiv)[len(tdiv)//2]} tiques (p10 {sorted(tdiv)[len(tdiv)//10]}) | {nome[:20]} vive mais em {100*sum(vive)/len(vive):.0f} % dos blocos', flush=True)
    print(f'    estado do {a.ref} na divergencia (media): fome {e[:, 0].mean():.0f} gasolina {e[:, 1].mean():.0f} agua {e[:, 2].mean():.0f} dinheiro {e[:, 3].mean():.0f} vida {e[:, 6].mean():.0f}', flush=True)
    top = sorted(range(G + S), key=lambda i: -abs(float(hist_b[i] - hist_r[i])))[:4]
    print('    opcoes onde a estrategia mais difere (fracao do tempo, ref -> braco): ' + ', '.join(f'op{i}: {float(hist_r[i]):.3f}->{float(hist_b[i]):.3f}' for i in top), flush=True)
    mk = saida_med[nome]; print(f"    [CS docs/69] raio de acao (desvio da posicao na vida): ref {sum(mk['ref']['raio'])/len(mk['ref']['raio']):.1f} m -> braco {sum(mk['braco']['raio'])/len(mk['braco']['raio']):.1f} m | fracao parada (FICAR): ref {sum(mk['ref']['parado'])/len(mk['ref']['parado']):.3f} -> braco {sum(mk['braco']['parado'])/len(mk['braco']['parado']):.3f}", flush=True)
    saida[nome] = dict(concordancia=conc, t_divergencia=tdiv, estado_div=est, vive_mais=vive, hist_ref=hist_r.tolist(), hist_braco=hist_b.tolist(), raio_parado=saida_med[nome])
os.makedirs(a.out, exist_ok=True); p = os.path.join(a.out, 'trajetoria_' + os.path.basename(a.bateria)); json.dump(dict(ref=a.ref, seeds=seeds, R=a.R, T=T, res=saida), open(p, 'w'), indent=1); print('gravado', p, flush=True)
