"""[chunks] portao + benchmark da varredura por grade: erro (grade vs exata) em posicoes aleatorias e tempo por tick em lote grande."""
import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *; from campo import _passo_fn
mapas = [gerar_mapa(s, L=200., distinto=True) for s in range(4)]
c = CfgCampo(L=200.); c.varredura = 'grade'; m = Campo(mapas, 2048, c, seed=1, R=8); B = m.B
p = torch.rand(B, 2, device=DEV)*200.
Pg, Dg = m._perto_grade(p); Pe, De = m._perto_exata(p); err = (Dg - De)
print(f'B={B}: erro grade-exata: max {float(err.max()):.3f} u | p99 {float(err.quantile(.99)):.3f} | fracao com erro > 0.1 u: {float((err > .1).float().mean()):.4f}', flush=True)
for nome, fn in (('exata', m._perto_exata), ('grade', m._perto_grade)):
    fn(p); torch.cuda.synchronize(); t0 = time.time()
    for _ in range(50): fn(p)
    torch.cuda.synchronize(); print(f'varredura {nome}: {(time.time()-t0)/50*1000:.2f} ms por tick (B={B})', flush=True)
for var in ('exata', 'grade'):
    c2 = CfgCampo(L=200.); c2.varredura = var; m2 = Campo(mapas, 2048, c2, seed=1, R=8); W = torch.randn(2048, Linear.NP, device=DEV)*.5; Wb = W[m2.gidx]; a = Linear(); a.reset(m2, Wb)
    import campo; campo._PASSO_C = None; campo._COMPILE_OK = None; fn = _passo_fn()
    for _ in range(3): fn(m2, a, Wb)
    torch.cuda.synchronize(); t0 = time.time()
    for _ in range(100): fn(m2, a, Wb)
    torch.cuda.synchronize(); print(f'passo completo ({var}, compilado): {(time.time()-t0)/100*1000:.2f} ms por tick (B={m2.B})', flush=True)
