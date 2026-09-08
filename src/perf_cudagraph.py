"""[perfil 09-08] 159 lancamentos/passo no Linear (~2.4 ms so de custo fixo em 4.3): testa torch.compile mode='reduce-overhead' (CUDA/HIP graphs)
contra o default, B=65k, Linear e COMPLETO. Identidade das posicoes entre os modos = portao."""
import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, torch._dynamo; from campo import *; import campo; from completo import SerCompleto
mapas = [gerar_mapa(s, L=200., distinto=True) for s in range(4)]; c = CfgCampo(L=200.)
for A in (Linear, SerCompleto):
    res = {}
    for modo in ('default', 'reduce-overhead', 'max-autotune-no-cudagraphs'):
        torch._dynamo.reset(); torch._dynamo.config.cache_size_limit = 64
        try: fn = torch.compile(um_passo, dynamic=False, mode=modo)
        except Exception as e: print(f'{A.__name__} {modo}: compile falhou {type(e).__name__}', flush=True); continue
        m = Campo(mapas, 2048, c, seed=1, R=8); torch.manual_seed(0); W = torch.randn(2048, A.NP, device=DEV)*.5; Wb = W[m.gidx]; a = A(); a.reset(m, Wb)
        try:
            t0 = time.time()
            for _ in range(5): fn(m, a, Wb); a.atualizar(m)
            torch.cuda.synchronize(); tc = time.time() - t0; t0 = time.time()
            for _ in range(100): fn(m, a, Wb); a.atualizar(m)
            torch.cuda.synchronize(); dt = (time.time() - t0)/100*1000
        except Exception as e: print(f'{A.__name__} {modo}: rodar falhou {type(e).__name__}: {str(e)[:120]}', flush=True); continue
        res[modo] = (dt, m.pos.clone()); print(f'{A.__name__:<12} {modo:<28} compile {tc:5.1f}s | {dt:6.2f} ms/passo (B={m.B})', flush=True)
    if 'default' in res:
        for modo, (dt, pos) in res.items():
            if modo != 'default': print(f'   identidade {modo} vs default: max dif pos {float((pos - res["default"][1]).abs().max()):.2e}', flush=True)
