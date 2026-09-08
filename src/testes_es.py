"""portao do E65 (ES): (1) converge numa quadratica conhecida; (2) deterministico; (3) orcamento = S*(P+1) avaliacoes/ger;
(4) campeao devolvido foi AVALIADO (fitness igual ao hist); (5) roda no campo (Linear, P=32, 2 ger) com --otim es."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, lab; from lab import DEV; from campo import *
class A: NP = 8
ws = torch.linspace(-2, 2, 8, device=DEV); n_av = []
def av(Arq, W, cidades, cfg, T, seed=0, R=1): n_av.append(W.shape[0]); return -((W - ws)**2).sum(1)
r1 = lab.evoluir_es(A, None, None, P=256, ger=80, T=1, seeds=(0, 1), verbose=False, avaliar_fn=av, W0=torch.zeros(8), sigma_es=.1, lr=.3)
r2 = lab.evoluir_es(A, None, None, P=256, ger=80, T=1, seeds=(0, 1), verbose=False, avaliar_fn=av, W0=torch.zeros(8), sigma_es=.1, lr=.3)
err = max(float((r1[sd][0] - ws).abs().max()) for sd in r1); print(f'converge quadratica (erro max {err:.3f} < .25):', err < .25, flush=True)
print('deterministico:', all(torch.equal(r1[sd][0], r2[sd][0]) and r1[sd][1] == r2[sd][1] for sd in r1), flush=True)
print('orcamento S*(P+1) por ger:', set(n_av) == {2*(256+1)}, flush=True)
print('campeao avaliado (fit == max hist):', all(abs(float(av(A, r1[sd][0][None], 0, 0, 0)[0]) - max(r1[sd][1])) < 1e-4 for sd in r1), flush=True)
print('sobe monotono no inicio (hist[0] < hist[20]):', all(r1[sd][1][0] < r1[sd][1][20] for sd in r1), flush=True)
c = CfgCampo(L=200., fitness='riqueza'); mapas = [gerar_mapa(1000, L=200.)]; os.environ['NM_COMPILE'] = '0'
r = lab.evoluir_es(Linear, mapas, c, P=32, ger=2, T=120, seeds=(0,), verbose=False, avaliar_fn=avaliar, R=1)
print('campo Linear P=32 2 ger: hist', [round(x, 3) for x in r[0][1]], '| NP', r[0][0].numel() == Linear.NP, flush=True)
