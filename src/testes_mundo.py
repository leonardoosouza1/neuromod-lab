"""portao do E56: distinto=False == mundo antigo bit a bit; distinto=True tem ruas, perfis, servicos por distrito, precos que mudam por dia, demanda por distrito."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, math; from campo import *
os.environ['NM_COMPILE'] = '0'; c = CfgCampo(L=200., fitness='bemestar')
m0 = gerar_mapa(1000, L=200.); m1 = gerar_mapa(1000, L=200.)
W = torch.randn(16, Linear.NP, device=DEV)*.5
a = rodar(Linear, W, [m0], c, T=300, seed=3, R=2); b = rodar(Linear, W, [m1], c, T=300, seed=3, R=2)
print('padrao == antes bit a bit:', float((a.pos-b.pos).abs().max()) == 0.0, '| amp_preco', a.amp_preco, flush=True)
d = gerar_mapa(1000, L=200., distinto=True)
rua = float((d['custo'] == 1.).float().mean()); print(f"distinto: fracao de rua {rua:.2f} (0.15-0.6) | perfis {d['perfil'].tolist()} | pmul {d['pmul'].tolist()} | demanda {d['demanda'].tolist()}", flush=True)
print('servicos por tipo:', {t: int(v.shape[0]) for t, v in d['serv'].items()}, flush=True)
md = Campo([d], 8, c, seed=1, R=2); p0 = md.pmul.clone(); md.obs()
for t in range(int(c.dia*1.5)): md.obs(); md.passo(torch.full((md.B,), G-1, device=DEV))
print('precos mudaram apos 1 dia:', bool((md.pmul - p0).abs().max() > .05), '| max var', round(float((md.pmul/md.pmul0 - 1.).abs().max()), 2), '(<= 0.5)', flush=True)
ok = 0.15 <= rua <= 0.6 and bool((md.pmul - p0).abs().max() > .05); print('PORTAO E56', 'ok' if ok else 'FALHOU', flush=True)
