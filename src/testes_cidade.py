"""PORTAO do E70 (passageiro na cidade). (1) flag off = bit-igual a referencia gravada por testes_ponto (processo A, mesmo W/mundo/T);
(2) flag on: distrito do passageiro ~ demanda; (3) passageiro mais perto fica mais longe para quem esta em demanda baixa;
(4) reposicao segue a demanda do LUGAR do passageiro; (5) sem sync."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'; os.environ.setdefault('NM_RISCO', '1')
import torch; from campo import *
IDENT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e68/_ident_pos.pt'
c = CfgCampo(L=200., fitness='riqueza'); mapas = [gerar_mapa(1000, L=200., distinto=True)]
d = torch.load(IDENT); W = d['W'].to(DEV); assert W.shape[1] == Linear.NP, f'referencia com NP {W.shape[1]} != {Linear.NP} (env NM_PONTO?)'
m = rodar(Linear, W, mapas, c, T=300, seed=3, R=2)
print('identidade (pax_cidade off) pos bit-igual a referencia:', bool(torch.equal(m.pos.cpu(), d['pos'])), '| dinh:', bool(torch.equal(m.dinh.cpu(), d['dinh'])), flush=True)
cc = CfgCampo(L=200., fitness='riqueza'); cc.pax_cidade = True; mm = Campo(mapas, 1024, cc, seed=11, R=1)
dpx = mm.distrito(mm.px); K = mm.demanda.shape[1]; share = torch.stack([(dpx == k).float().mean() for k in range(K)]); dem = mm.demanda[0]; w = dem/dem.sum()
corr = float(torch.corrcoef(torch.stack([share, w]))[0, 1])
print(f'distrito do passageiro ~ demanda: corr {corr:.2f} > .8:', corr > .8, '| share por distrito', [round(float(x), 2) for x in share], 'demanda', [round(float(x), 2) for x in w], flush=True)
dser = mm.demanda[mm.cidx, mm.distrito(mm.pos)]; dn = (mm.px - mm.pos[:, None, :]).norm(dim=-1).min(1).values
alta = float(dn[dser >= 1.5].mean()); baixa = float(dn[dser <= .5].mean())
print(f'passageiro mais perto: ser em demanda alta {alta:.0f} u vs baixa {baixa:.0f} u (alta < baixa):', alta < baixa, flush=True)
mm.px_ok[:] = False; a = Linear(); Wz = torch.zeros(mm.B, Linear.NP, device=DEV); a.reset(mm, Wz); esc = torch.full((mm.B,), G - 1, dtype=torch.long, device=DEV)
for t in range(40): mm.obs(); mm.passo(esc); a.atualizar(mm)
ok = mm.px_ok.float(); dslot = mm.demanda[mm.cidx[:, None].expand(-1, cc.NPX), mm.distrito(mm.px)]
r_alta = float(ok[dslot >= 1.5].mean()); r_baixa = float(ok[dslot <= .5].mean())
print(f'reposicao ~ demanda do LUGAR do passageiro: slots em demanda alta reativados {r_alta:.2f} vs baixa {r_baixa:.2f} (alta > baixa):', r_alta > r_baixa, flush=True)
m2 = Campo(mapas, 32, cc, seed=1, R=2); Wb = (torch.randn(32, Linear.NP, device=DEV)*.5)[m2.gidx]; a2 = Linear(); a2.reset(m2, Wb)
for t in range(5): um_passo(m2, a2, Wb); a2.atualizar(m2)
torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode('error'); ok2 = True
try:
    for t in range(5): um_passo(m2, a2, Wb); a2.atualizar(m2)
except RuntimeError as e: ok2 = False
torch.cuda.set_sync_debug_mode('default'); print('SEM SYNC (pax_cidade):', ok2, flush=True)
