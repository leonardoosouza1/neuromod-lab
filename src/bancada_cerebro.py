"""[CS BANCADA-CEREBRO] PORTAO DE CAPACIDADE por bloco, sem evolucao: B genomas aleatorios (uniforme +-amp), mundo distinto L=200, corpo
posto a mao em escassez, 5 passos, e a contribuicao de cada bloco na nota de movimento (a._blk, 9 opcoes): DIRIGE = desvio entre as
9 opcoes (o que o argmax ve), DESLOCA = |media entre opcoes| (descartada pelo G1: sc - sc.mean), MUDA = fracao de seres cuja opcao de
movimento escolhida muda ao tirar o bloco. Tambem soma dos portoes do talamo e faixa de (1+delta) do cortex. GPU, segundos.
Uso: --hip-esc 1.0 / --cortex-amp 2 / --talamo-norm fixo para ver o que cada conserto muda ANTES de gastar bateria."""
import sys, os, json, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from campo import um_passo; from completo import SerCompleto, NG, NOMES_G, nomes_genes_completos
ap = argparse.ArgumentParser(); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e72'); ap.add_argument('--B', type=int, default=2048); ap.add_argument('--amp', type=float, default=1.5)
ap.add_argument('--hip-esc', type=float, default=None); ap.add_argument('--cortex-amp', type=float, default=.5); ap.add_argument('--talamo-norm', default=''); ap.add_argument('--tag', default=''); a = ap.parse_args()
mapas = [gerar_mapa(1000, L=200., distinto=True)]; g = torch.Generator(device=DEV); g.manual_seed(5)
W = (torch.rand(a.B, SerCompleto.NP, generator=g, device=DEV)*2. - 1.)*a.amp
c = CfgCampo(L=200., fitness='riqueza'); c.medir_ativ = True; c.hip_esc = a.hip_esc; c.cortex_amp = a.cortex_amp; c.talamo_norm = a.talamo_norm or False
m = Campo(mapas, a.B, c, seed=3, R=1); Wb = W[m.gidx]; ar = SerCompleto(); ar.reset(m, Wb)
u = lambda lo, hi: lo + (hi - lo)*torch.rand(a.B, generator=g, device=DEV)
m.fuel = u(0., 30.); m.fome = u(40., 90.); m.agua = u(30., 90.); m.dinh = u(-20., 20.)
ar.MEM = torch.randn(ar.MEM.shape, generator=g, device=DEV)*.5
for _ in range(5): um_passo(m, ar, Wb)
F, _ = m.obs(); esp = torch.einsum('bgf,bf->bg', F, Wb[:, :NF]); ext = ar.extra(m, Wb, F); tot = esp + ext; blk = dict(ar._blk); blk['espinha'] = esp
gen = {'espinha': Linear.NP}
for n in nomes_genes_completos(): gen[n[:3]] = gen.get(n[:3], 0) + 1
esc0 = tot.argmax(1); res = {}
print(f'BANCADA: B {a.B} amp +-{a.amp} hip_esc {a.hip_esc} cortex_amp {a.cortex_amp} talamo_norm {a.talamo_norm or "off"}', flush=True)
print(f'  {"bloco":8} {"dirige":>8} {"desloca":>8} {"dir/tot":>8} {"muda acao":>10} {"dir/gene":>10}', flush=True)
for b, v in blk.items():
    d = float(v.std(1).mean()); s_ = float(v.mean(1).abs().mean()); muda = float(((tot - v).argmax(1) != esc0).float().mean()) if b != 'espinha' else float('nan'); ng = gen.get(b)
    res[b] = dict(dirige=d, desloca=s_, muda=muda, genes=ng); print(f'  {b:8} {d:8.4f} {s_:8.3f} {d/max(d+s_,1e-9):8.3f} {muda:10.3f} {(d/ng if ng else float("nan")):10.5f}', flush=True)
gs = ar._gate(m).sum(1); dl = 1. + ar.DLT; res['portoes_soma'] = dict(min=float(gs.min()), mediana=float(gs.median()), max=float(gs.max())); res['cortex_1_mais_delta'] = dict(min=float(dl.min()), max=float(dl.max()), inverte=float((dl < 0).float().mean()))
print(f'  soma dos portoes: min {float(gs.min()):.2f} mediana {float(gs.median()):.2f} max {float(gs.max()):.2f} (NG {NG}) | cortex 1+delta [{float(dl.min()):.2f}, {float(dl.max()):.2f}] inverte {float((dl < 0).float().mean()):.3f}', flush=True)
os.makedirs(a.out, exist_ok=True); p = os.path.join(a.out, f'bancada{a.tag}.json'); json.dump(dict(args=vars(a), res=res), open(p, 'w'), indent=1); print('gravado', p, flush=True)
