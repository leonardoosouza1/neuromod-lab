"""portao da fusao das matmuls do completo: mesma conta que a versao por partes (referencia reimplementada aqui), tolerancia float."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *; from completo import *
os.environ['NM_COMPILE'] = '0'; c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000, L=200., distinto=True)]
def extra_ref(s, m, W, F):
    sc = Cerebro.extra(s, m, W, F)
    gf = s._gate(m).gather(1, s.IDXG); sc = sc + torch.einsum('bgf,bf->bg', F, W[:, :NF]*(gf - 1.))
    mem = s._mem(m); delta = s.DLT.gather(1, s.dn[:, None, None].expand(-1, 1, len(IDX_CORTEX))).squeeze(1)
    sc = sc + torch.einsum('bgf,bf->bg', F.index_select(2, s.IDXC), W[:, s.IDXC]*delta)
    Wm = torch.einsum('bk,bkf->bf', mem, s.M_h)*Cerebro.ESC; sc = sc + torch.einsum('bgf,bf->bg', F, Wm)
    a = s._ativ(); return sc - (s.w*a)[:, None]*F[:, :, 1]
m = Campo(mapas, 64, c, seed=1, R=2); W = (torch.randn(64, SerCompleto.NP, device=DEV)*.8)[m.gidx]; a = SerCompleto(); a.reset(m, W)
worst = 0.
for t in range(200):
    F, _ = m.obs(); e1 = a.extra(m, W, F); e2 = extra_ref(a, m, W, F); worst = max(worst, float((e1 - e2).abs().max()))
    um_passo(m, a, W); a.atualizar(m)
print(f'fusao vs referencia: max |dif| da nota = {worst:.2e} (escala das notas ~{float(e1.abs().mean()):.1f}) {"OK" if worst < 1e-3*max(1., float(e1.abs().mean())) else "FALHOU"}', flush=True)
