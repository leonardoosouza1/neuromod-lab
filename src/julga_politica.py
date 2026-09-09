"""JUIZ de politica explicita (doc 53): carrega politica.py de um agente (lista negra antes do exec), roda em 3 mundos de TESTE x 128 copias
x 5 sementes de avaliacao e imprime mortos/entregas/renda/panes ao lado do campeao linear medido igual. Nunca avalia pelo que o agente diz."""
import sys, os, json, argparse, re; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from e43_campo import aplica_cenario, alinha_semente
ap = argparse.ArgumentParser(); ap.add_argument('--politica', required=True); ap.add_argument('--cenario', default=None); ap.add_argument('--campeao', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e64/e43_busca8x_L200.json')
ap.add_argument('--copias', type=int, default=128); ap.add_argument('--seeds', type=int, nargs='*', default=[7777, 7778, 7779, 7780, 7781]); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/agentes'); ap.add_argument('--tag', default='')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
src = open(a.politica).read()
PROIBIDO = [r'\bimport\s+(?!torch\b|math\b)', r'\bfrom\s+(?!torch\b|math\b)', r'\b(os|sys|subprocess|open|exec|eval|__import__|compile|globals|locals|getattr|setattr)\s*\(', r'\.px\b', r'\.pxd\b', r'\.serv\[', r'\.serv_msk', r'\.g\b', r'\.dest\b']
for pat in PROIBIDO:
    if re.search(pat, src): raise SystemExit(f'POLITICA RECUSADA: padrao proibido {pat!r}')
ns = {'torch': torch, 'math': __import__('math'), 'G': G, 'S': S, 'NF': NF, 'NOMES_OP': NOMES_OP, 'NOMES_CORPO': NOMES_CORPO, 'Linear': Linear, 'DEV': DEV}
exec(compile(src, a.politica, 'exec'), ns); assert 'fabrica' in ns, 'politica.py precisa definir fabrica() -> classe com reset/extra/decidir/atualizar'
POL0 = ns['fabrica']()
import inspect
class POL:   # invólucro por COMPOSICAO, ciente da assinatura: agentes copiaram 'reset(s, m, W)' como 'def reset(self, s, m, W)' -> passa o proprio objeto como s
    NP = Linear.NP
    def __init__(s): s.p = POL0() if isinstance(POL0, type) else POL0
    def _call(s, nome, *args):
        fn = getattr(s.p, nome, None)
        if fn is None: return None
        n = len([q for q in inspect.signature(fn).parameters.values() if q.default is inspect._empty and q.kind in (q.POSITIONAL_ONLY, q.POSITIONAL_OR_KEYWORD)])
        if n == len(args) + 1: return fn(s.p, *args)      # def f(self, s, ...): s = o proprio objeto
        if n < len(args): return fn(*args[:n])            # def reset(self, m): sem W
        return fn(*args)
    def reset(s, m, W): return s._call('reset', m, W)
    def extra(s, m, W, F):
        if hasattr(s.p, 'extra'): return s._call('extra', m, W, F)
        s.p.F = F; return torch.zeros(m.B, G, device=DEV)
    def decidir(s, tudo, m): return s._call('decidir', tudo, m)
    def atualizar(s, m): return s._call('atualizar', m)
fl = argparse.Namespace(L=200., dias=10., fitness='riqueza', nevoa=float('inf'), npx=12, respawn=20., pax_cidade=False, ponto=0., dinh0=10., fome_passo=None, kcal_pane=8., guincho=0., fuel_pane=15., P=None, G=None, paciencia=None, R=None, seeds=None, so=None, mundo='distinto')
cen = json.load(open(a.cenario)) if a.cenario else {}; ex = aplica_cenario(fl, cen)
cfg = CfgCampo(L=fl.L, fitness=fl.fitness); cfg.KCAL_PANE = fl.kcal_pane; cfg.dinh0 = fl.dinh0; cfg.GUINCHO = fl.guincho; cfg.FUEL_POS_PANE = fl.fuel_pane; cfg.nevoa = fl.nevoa; cfg.ponto = fl.ponto; cfg.NPX = fl.npx; cfg.respawn = fl.respawn; cfg.pax_cidade = fl.pax_cidade
if fl.fome_passo is not None: cfg.fome_passo = fl.fome_passo
for k in ('amp_preco', 'periodo_preco', 'tarifa_base', 'tarifa_km'):
    if ex.get(k) is not None: setattr(cfg, k, ex[k])
teste = [gerar_mapa(1000 + s, L=fl.L, distinto=fl.mundo == 'distinto', perfis=ex['perfis'], K=ex['K'], ruas=ex['ruas']) for s in range(3)]; T = int(240*fl.dias)
J = json.load(open(a.campeao))['bracos']['linear']['W']; Wc = torch.tensor(alinha_semente(J['0']), device=DEV)
def mede(Arq, W, nome):
    r = {k: [] for k in ('mortos', 'ent', 'rec', 'panes', 'fome_fim', 'n_come', 'n_posto', 'dinh_fim', 'agua_fim', 'vida_vivos')}
    for sd in a.seeds:
        m = rodar(Arq, W[None, :].repeat(a.copias, 1), teste, cfg, T, sd, R=1)
        r['mortos'].append(float((m.vida <= 0).float().mean())); r['ent'].append(float(m.ent.mean())); r['rec'].append(float(m.rec.mean())); r['panes'].append(float(m.av_fuel.mean())); r['fome_fim'].append(float(m.fome.mean()))
        r['n_come'].append(float(m.n_come.mean())); r['n_posto'].append(float(m.n_posto.mean())); r['dinh_fim'].append(float(m.dinh.mean())); r['agua_fim'].append(float(m.agua.mean())); r['vida_vivos'].append(float(m.vida[m.vida > 0].mean()) if bool((m.vida > 0).any()) else 0.)
    med = {k: sum(v)/len(v) for k, v in r.items()}; med['por_seed'] = {k: [round(x, 3) for x in v] for k, v in r.items()}
    print(f"  {nome:<28} mortos {med['mortos']:.2f} {med['por_seed']['mortos']} ent {med['ent']:5.1f} renda {med['rec']:5.0f} panes {med['panes']:4.1f} | AUTOPSIA: refeicoes {med['n_come']:4.1f} abastecidas {med['n_posto']:4.1f} fome_fim {med['fome_fim']:3.0f} agua_fim {med['agua_fim']:3.0f} dinheiro_fim {med['dinh_fim']:4.0f} (fome 100 = morreu de fome; refeicoes 0 = nunca comprou comida; dinheiro < 0 = divida)", flush=True); return med
print(f'== juiz de politica | {os.path.basename(a.politica)} | cenario {a.cenario or "base(default)"} | {len(a.seeds)} sementes x {a.copias} copias x 3 mapas ==', flush=True)
def traco(Arq, W, T=240):   # histograma das ESCOLHAS nos primeiros T ticks: mostra o mecanismo (parado? comprando? andando?)
    m = Campo(teste, 64, cfg, seed=7777, R=1); Wb = W[None, :].repeat(64, 1)[m.gidx]; ar = Arq(); ar.reset(m, Wb); cont = torch.zeros(G + S, device=DEV); dist = 0.
    for t in range(T):
        F, val = m.obs(); sc = torch.einsum('bgf,bf->bg', F, Wb[:, :NF]) + ar.extra(m, Wb, F); sc = sc - sc.mean(1, keepdim=True)
        svn, sv = m.serv_need(); ss = (svn*Wb[:, NF:NF+S] + Wb[:, NF+S:NF+S+1]).masked_fill(sv <= 0, -1e9); tudo = torch.cat([sc, ss], 1)
        esc = ar.decidir(tudo, m) if hasattr(ar, 'decidir') else tudo.argmax(1); esc = esc.long().clamp(0, G + S - 1); p0 = m.pos.clone(); m.passo(esc); ar.atualizar(m)
        cont += torch.bincount(esc, minlength=G + S).float(); dist += float((m.pos - p0).norm(dim=-1).mean())
    f = (cont/cont.sum()).tolist(); nomes = ['mover']*(G - 1) + ['ficar'] + [f'{t}{int(q) if q else ""}' for t, q in ACOES]
    agg = {'mover': sum(f[:G - 1]), 'ficar': f[G - 1]}; agg.update({nomes[G + k]: f[G + k] for k in range(S)})
    print('  TRACO 240 ticks (fracao das escolhas): ' + ' '.join(f'{k} {v:.2f}' for k, v in agg.items() if v > 0.005) + f' | deslocamento medio/tick {dist/T:.2f} u', flush=True)
res = dict(politica=a.politica, cenario=a.cenario, predicao=cen.get('predicao'))
res['linear_campeao'] = mede(Linear, Wc, 'linear campeao (q8)'); traco(POL, torch.zeros(Linear.NP, device=DEV)); res['politica_res'] = mede(POL, torch.zeros(Linear.NP, device=DEV), 'politica do agente')
res['dif_mortos'] = res['politica_res']['mortos'] - res['linear_campeao']['mortos']
json.dump(res, open(os.path.join(a.out, f'julga{a.tag}.json'), 'w'), indent=1); print(f"dif mortos (politica - linear) {res['dif_mortos']:+.3f}", flush=True)
