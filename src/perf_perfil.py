"""PERFIL do passo compilado (Leonardo 09-08: 'veja o perfil'): os kernels mais caros por tempo de GPU em B=65k, 50 passos,
Linear e COMPLETO. Diz se o custo esta em muitos kernels pequenos (-> kernel HIP fundido paga) ou em uma operacao (-> conserto local)."""
import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *; from campo import _passo_fn; from completo import SerCompleto
from torch.profiler import profile, ProfilerActivity
mapas = [gerar_mapa(s, L=200., distinto=True) for s in range(4)]; c = CfgCampo(L=200.)
for A in (Linear, SerCompleto):
    import campo; campo._PASSO_C = None; campo._COMPILE_OK = None
    m = Campo(mapas, 2048, c, seed=1, R=8); W = torch.randn(2048, A.NP, device=DEV)*.5; Wb = W[m.gidx]; a = A(); a.reset(m, Wb); fn = _passo_fn()
    for _ in range(5): fn(m, a, Wb); a.atualizar(m)
    torch.cuda.synchronize(); t0 = time.time()
    with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=False) as prof:
        for _ in range(50): fn(m, a, Wb); a.atualizar(m)
        torch.cuda.synchronize()
    dt = (time.time() - t0)/50*1000
    ka = prof.key_averages()
    tot = sum(k.device_time_total for k in ka if k.device_time_total > 0)
    print(f'\n===== {A.__name__} B={m.B}: {dt:.2f} ms/passo | kernels distintos {sum(1 for k in ka if k.device_time_total > 0)} | tempo GPU total por passo {tot/50/1000:.2f} ms', flush=True)
    top = sorted([k for k in ka if k.device_time_total > 0], key=lambda k: -k.device_time_total)[:15]
    print(f"{'kernel':<70} {'ms/passo':>9} {'%':>6} {'chamadas/passo':>15}")
    for k in top: print(f'{k.key[:70]:<70} {k.device_time_total/50/1000:>9.3f} {100*k.device_time_total/tot:>6.1f} {k.count/50:>15.1f}', flush=True)
    n_launch = sum(k.count for k in ka if k.device_time_total > 0)/50
    print(f'lancamentos de kernel por passo: {n_launch:.0f}  (cada ~10-20 us de custo fixo = {n_launch*0.015:.2f} ms so de lancamento)', flush=True)
