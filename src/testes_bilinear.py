"""portao do E58: M=0 == Linear bit a bit; corpo NAO muda direcao no Linear (prova do achado); no Bilinear muda; sem sync."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *
c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000, L=200.)]; os.environ['NM_COMPILE'] = '0'
Wl = torch.randn(16, Linear.NP, device=DEV)*.5; Wb = torch.zeros(16, Bilinear.NP, device=DEV); Wb[:, :Linear.NP] = Wl
m1 = rodar(Linear, Wl, mapas, c, T=300, seed=3, R=2); m2 = rodar(Bilinear, Wb, mapas, c, T=300, seed=3, R=2)
print('bilinear M=0 == linear:', float((m1.pos-m2.pos).abs().max()) == 0.0, '| NP', Bilinear.NP, flush=True)
# prova do achado: no Linear, mudar os pesos do CORPO (colunas 10..NF-1 do movimento) nao muda NADA nas posicoes
Wc = Wl.clone(); Wc[:, len(NOMES_OP):NF] += torch.randn(16, NF - len(NOMES_OP), device=DEV)*3.
m3 = rodar(Linear, Wc, mapas, c, T=300, seed=3, R=2); print('linear: pesos do corpo no movimento sao INVISIVEIS (pos iguais):', float((m1.pos-m3.pos).abs().max()) == 0.0, flush=True)
Wb2 = Wb.clone(); Wb2[:, Linear.NP:] = torch.randn(16, Bilinear.NP - Linear.NP, device=DEV)*.5
m4 = rodar(Bilinear, Wb2, mapas, c, T=300, seed=3, R=2); print('bilinear: M != 0 muda a direcao:', float((m1.pos-m4.pos).abs().max()) > 1., flush=True)
BA = fabrica_bilinear(['e_autonomia', 'e_consumo']); print('bilinear autonomia+consumo NP', BA.NP, flush=True)
m = Campo(mapas, 32, c, seed=1, R=2); W = (torch.randn(32, Bilinear.NP, device=DEV)*.5)[m.gidx]; a = Bilinear(); a.reset(m, W)
for t in range(5): um_passo(m, a, W); a.atualizar(m)
torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode("error"); ok = True
try:
    for t in range(5): um_passo(m, a, W); a.atualizar(m)
except RuntimeError as e: ok = False
torch.cuda.set_sync_debug_mode("default"); print('SEM SYNC' if ok else 'SYNC!', flush=True)
