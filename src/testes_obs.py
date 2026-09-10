"""[reprojeto CS docs/70] PORTAO do obs() rapido: mesma configuracao, obs_rapido=False (caminho de sempre) vs True, Linear e SerCompleto,
T=300, B=2048: pos/vida/fome/fuel/agua/dinh IGUAIS bit a bit (torch.equal); e ms por tique dos dois caminhos. Roda com e sem NM_RETINA
(o daemon passa o env). Exit 1 se algo diferir."""
import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('NM_COMPILE', '0')
import torch; from campo import *; from completo import SerCompleto
mapas = [gerar_mapa(1000, L=200., distinto=True), gerar_mapa(1001, L=200., distinto=True)]; g = torch.Generator(device=DEV); g.manual_seed(5)
falhas = []
for Arq, nome in ((Linear, 'Linear'), (SerCompleto, 'SerCompleto')):
    W = torch.randn(1024, Arq.NP, generator=g, device=DEV)*.3; W[:, :Linear.NP] = torch.randn(1024, Linear.NP, generator=g, device=DEV)*.5
    res = {}
    for rap in (False, True):
        c = CfgCampo(L=200., fitness='riqueza'); c.obs_rapido = rap; c.retina = dict(RETINA_PADRAO) if RETINA else None
        torch.cuda.synchronize(); t0 = time.time(); m = rodar(Arq, W, mapas, c, T=300, seed=3, R=1); torch.cuda.synchronize(); dt = (time.time() - t0)/300*1000.
        res[rap] = (m, dt)
    m0, m1 = res[False][0], res[True][0]; ig = {k: torch.equal(getattr(m0, k), getattr(m1, k)) for k in ('pos', 'vida', 'fome', 'fuel', 'agua', 'dinh')}
    ok = all(ig.values()); falhas += [] if ok else [nome]
    print(f'  {nome:12} B {m0.B} retina {RETINA}: lento {res[False][1]:.2f} ms/tique -> rapido {res[True][1]:.2f} ms/tique ({res[False][1]/max(res[True][1],1e-9):.2f}x) | identidade {ig}', 'OK' if ok else 'FALHOU', flush=True)
print('PORTAO OBS', 'ok' if not falhas else f'FALHOU em {falhas}', flush=True); sys.exit(0 if not falhas else 1)
