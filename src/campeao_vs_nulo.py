"""[CS DERIVA §2-3 — regra 'dof sempre contra a deriva'] Le um JSON de bateria (e43_*.json) e o JSON da deriva nula e imprime, por braco e
semente: dof dos genes novos (fracao |w| > gene_min alem da espinha), fracao do cortex na trava (|amp*tanh(w)| > .8*amp) e a geracao do
NULO em que a deriva pura teria o mesmo valor (interpolacao). Campeao com dof/trava ABAIXO do nulo na sua geracao efetiva = selecao
podando/segurando; igual ao nulo = deriva, nao selecao. Roda na fila (segundos)."""
import sys, os, json, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import DEV, Linear; from completo import SerCompleto
ap = argparse.ArgumentParser(); ap.add_argument('--bateria', required=True); ap.add_argument('--nulo', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e72/deriva_nula_s0.0_e0.0.json'); ap.add_argument('--gene-min', type=float, default=.5); ap.add_argument('--cortex-amp', type=float, default=.5); ap.add_argument('--out', default=None); a = ap.parse_args()
d = json.load(open(a.bateria)); nulo = json.load(open(a.nulo))['marcos']; gens = sorted(int(k) for k in nulo); o = SerCompleto.O_COR; nc = SerCompleto.N_COR
def ger_do_nulo(chave, v):
    xs = [(g, nulo[str(g)][chave]) for g in gens]
    for (g0, v0), (g1, v1) in zip(xs, xs[1:]):
        if v0 <= v <= v1: return g0 + (g1 - g0)*(v - v0)/max(v1 - v0, 1e-9)
    return float('inf') if v > xs[-1][1] else 0.
print(f'CAMPEAO vs NULO: {os.path.basename(a.bateria)} | nulo {os.path.basename(a.nulo)} | gene_min {a.gene_min} amp {a.cortex_amp}', flush=True)
print(f'  {"braco":38} {"sem":>4} {"NP":>4} {"ger_ef":>6} {"dof_novos":>9} {"=nulo@ger":>9} {"trava":>6} {"=nulo@ger":>9}', flush=True); saida = {}
for nome, med in d['bracos'].items():
    if 'W' not in med: continue
    ge = med.get('ger_efetiva', {})
    for sd, w in med['W'].items():
        W = torch.tensor(w, device=DEV); NPw = W.numel(); novos = W[Linear.NP:]; dof = float((novos.abs() > a.gene_min).float().mean()) if novos.numel() else float('nan')
        trava = float(((a.cortex_amp*torch.tanh(W[o:o+nc])).abs() > .8*a.cortex_amp).float().mean()) if NPw >= o + nc else float('nan')
        gd = ger_do_nulo('dof_novos', dof) if novos.numel() else float('nan'); gt = ger_do_nulo('cortex_trava', trava) if NPw >= o + nc else float('nan')
        saida[f'{nome}|{sd}'] = dict(NP=NPw, ger_efetiva=ge.get(str(sd)), dof_novos=dof, dof_ger_nulo=gd, cortex_trava=trava, trava_ger_nulo=gt)
        print(f'  {nome[:38]:38} {str(sd):>4} {NPw:>4} {str(ge.get(str(sd), "?")):>6} {dof:9.3f} {gd:9.1f} {trava:6.3f} {gt:9.1f}', flush=True)
print('  nulo de referencia: ' + ' | '.join(f'ger {g}: dof {nulo[str(g)]["dof_novos"]:.2f} trava {nulo[str(g)]["cortex_trava"]:.2f}' for g in gens if g in (10, 20, 30, 45, 60)), flush=True)
if a.out: os.makedirs(a.out, exist_ok=True); p = os.path.join(a.out, 'campeao_vs_nulo_' + os.path.basename(a.bateria)); json.dump(saida, open(p, 'w'), indent=1); print('gravado', p, flush=True)
