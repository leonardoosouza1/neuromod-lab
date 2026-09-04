"""portao do E53: saidas 0 (V=M=P) == Linear bit a bit com U/U2 aleatorios; banco de tau com gene 0 ~ 4.6/24/101; z se move; sem sync."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *
c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000, L=200.)]; os.environ['NM_COMPILE'] = '0'
Wl = torch.randn(16, Linear.NP, device=DEV)*.5; Wc = torch.randn(16, Cerebro.NP, device=DEV)*.8; Wc[:, :Linear.NP] = Wl
Wc[:, Cerebro.O_V:Cerebro.O_U2] = 0.; Wc[:, Cerebro.O_M:Cerebro.NP] = 0.
m1 = rodar(Linear, Wl, mapas, c, T=300, seed=3, R=2); m2 = rodar(Cerebro, Wc, mapas, c, T=300, seed=3, R=2)
print('cerebro transparente == linear:', float((m1.pos-m2.pos).abs().max())==0.0, '| NP', Cerebro.NP, flush=True)
m = Campo(mapas, 32, c, seed=1, R=2); Wb = torch.zeros(32, Cerebro.NP, device=DEV)[m.gidx]; a = Cerebro(); a.reset(m, Wb)
print('banco de tau (gene 0):', [round(float(x), 1) for x in a.tau[0]], flush=True)
Wb = (torch.randn(32, Cerebro.NP, device=DEV)*.8)[m.gidx]; a = Cerebro(); a.reset(m, Wb)
for t in range(50): um_passo(m, a, Wb); a.atualizar(m)
print('z apos 50 ticks: media', round(float(a.z.mean()), 3), 'max', round(float(a.z.max()), 3), '(tem de ser > 0)', flush=True)
torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode("error"); ok = True
try:
    for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
except RuntimeError as e: ok = False
torch.cuda.set_sync_debug_mode("default"); print('SEM SYNC' if ok else 'SYNC!', flush=True)
