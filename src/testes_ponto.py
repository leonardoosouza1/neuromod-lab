"""PORTAO do E68 (ponto de taxi). Roda em DOIS processos: (A) NM_PONTO=0 grava posicoes; (B) NM_PONTO=1 com ponto=0 e a mesma semente
alinhada (zeros nos sentidos novos) tem de dar posicoes BIT-IGUAIS (mundo identico com a mecanica desligada). Depois, so em (B):
mecanica (parado em distrito de demanda alta pega passageiro; ponto=0 nunca), sentidos (e_demanda == demanda do distrito, e_espera
== ticks parados/100), alinhamento da semente, e sem sync no bilinear novo."""
import sys, os, subprocess, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'; os.environ.setdefault('NM_RISCO', '1')
import torch; from campo import *
OUT = '/media/llm-data/universe-runs/neuromod-lab-taxi/e68'; os.makedirs(OUT, exist_ok=True); IDENT = os.path.join(OUT, '_ident_pos.pt')
c = CfgCampo(L=200., fitness='riqueza'); mapas = [gerar_mapa(1000, L=200., distinto=True)]
g = torch.Generator(device=DEV); g.manual_seed(5)
if not PONTO:   # ---------- processo A: mundo velho
    W = torch.randn(64, Linear.NP, generator=g, device=DEV)*.5
    m = rodar(Linear, W, mapas, c, T=300, seed=3, R=2); torch.save({'W': W.cpu(), 'pos': m.pos.cpu(), 'dinh': m.dinh.cpu(), 'NP': Linear.NP}, IDENT)
    print(f'A: NF {NF} NP {Linear.NP} gravado', flush=True)
    r = subprocess.run([sys.executable, __file__] + sys.argv[1:], env={**os.environ, 'NM_PONTO': '1'}); sys.exit(r.returncode)
# ---------- processo B: mundo novo
d = torch.load(IDENT); Wv = d['W'].to(DEV); falta = Linear.NP - d['NP']; nf_velho = NF - falta
W = torch.cat([Wv[:, :nf_velho], torch.zeros(Wv.shape[0], falta, device=DEV), Wv[:, nf_velho:]], 1)
m = rodar(Linear, W, mapas, c, T=300, seed=3, R=2)
print(f'B: NF {NF} NP {Linear.NP} | identidade (ponto=0, sentidos novos com gene 0) pos bit-igual:', bool(torch.equal(m.pos.cpu(), d['pos'])), '| dinh:', bool(torch.equal(m.dinh.cpu(), d['dinh'])), flush=True)
# alinhamento: mesma conta do e43
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from e43_campo import alinha_semente
v = list(range(1, d['NP'] + 1)); a = alinha_semente(v); ok = a[:nf_velho] == [float(x) for x in v[:nf_velho]] and a[nf_velho:NF] == [0.]*falta and a[NF:] == [float(x) for x in v[nf_velho:]] and len(a) == Linear.NP
print('alinha_semente: zeros nos sentidos novos, servico intacto:', ok, flush=True)
# mecanica: todos param (esc = G-1) por 60 ticks; com ponto=30, centro pega quase sempre, periferia menos; com ponto=0 ninguem
def parados(ponto, T=60):
    cc = CfgCampo(L=200., fitness='riqueza'); cc.ponto = ponto; mm = Campo(mapas, 512, cc, seed=11, R=1); Wb = torch.zeros(mm.B, Linear.NP, device=DEV)
    a = Linear(); a.reset(mm, Wb); esc = torch.full((mm.B,), G - 1, dtype=torch.long, device=DEV)
    for t in range(T): mm.obs(); mm.passo(esc); a.atualizar(mm)
    return mm
m0 = parados(0.); m30 = parados(30.)
dist = m30.distrito(m30.pos); perfil = m30.perfil[m30.cidx, dist] if hasattr(m30, 'perfil') else None
tem = (m30.pd_ >= 0).float(); dem = m30.demanda[m30.cidx, dist]
alta = tem[dem >= 1.5].mean().item() if bool((dem >= 1.5).any()) else float('nan'); baixa = tem[dem <= .5].mean().item() if bool((dem <= .5).any()) else float('nan')
print(f'mecanica: ponto=0 parado quase nunca pega ({(m0.pd_ >= 0).float().mean().item():.2f} < .10; o resto e passageiro grampeado na BORDA do mapa, quirk antigo do _perto):', bool((m0.pd_ >= 0).float().mean().item() < .10), f'| ponto=30 em 60 ticks: demanda alta {alta:.2f} (esperado ~.98) vs baixa {baixa:.2f} (esperado ~.45):', alta > .85 and baixa < .7 and alta > baixa, flush=True)
# sentidos
F, _ = m30.obs(); NOP = len(NOMES_OP); kd = NOMES_CORPO.index('e_demanda'); ke = NOMES_CORPO.index('e_espera')
ed = F[:, G - 1, NOP + kd]; ee = F[:, G - 1, NOP + ke]; livre = m30.pd_ < 0
print('sentido e_demanda == demanda do distrito/2:', bool(torch.allclose(ed, dem/2.)), '| e_espera dos que nunca embarcaram == 60/100:', bool(torch.allclose(ee[livre], torch.full_like(ee[livre], .6))) if bool(livre.any()) else 'n/a', '| e_espera zera ao embarcar (<.6):', bool((ee[~livre] < .6).all()) if bool((~livre).any()) else 'n/a', flush=True)
# sem sync no bilinear novo com ponto ligado
BR = fabrica_bilinear(['e_risco', 'e_demanda', 'e_espera'], esc=1.); cc = CfgCampo(L=200., fitness='riqueza'); cc.ponto = 30.
mm = Campo(mapas, 32, cc, seed=1, R=2); Wb = (torch.randn(32, BR.NP, generator=g, device=DEV)*.5)[mm.gidx]; a = BR(); a.reset(mm, Wb)
for t in range(5): um_passo(mm, a, Wb); a.atualizar(mm)
torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode('error'); ok = True
try:
    for t in range(5): um_passo(mm, a, Wb); a.atualizar(mm)
except RuntimeError as e: ok = False
torch.cuda.set_sync_debug_mode('default'); print('SEM SYNC (bilinear risco+demanda+espera, ponto=30):', ok, '| NP', BR.NP, flush=True)
