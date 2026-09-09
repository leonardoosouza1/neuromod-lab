"""[spec §0.3] ONDE o cerebro completo sincroniza CPU<->GPU dentro do passo: roda um_passo+atualizar com set_sync_debug_mode('error') e
warnings como excecao, imprimindo o traceback da PRIMEIRA operacao sincronizante (o portao testes_completo so diz 'SYNC!')."""
import sys, os, traceback, warnings; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from completo import SerCompleto
c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000, L=200.)]; g = torch.Generator(device=DEV); g.manual_seed(7)
for A in (Linear, Cerebro, SerCompleto):
    m = Campo(mapas, 32, c, seed=1, R=2); Wb = (torch.randn(32, A.NP, generator=g, device=DEV)*.5)[m.gidx]; a = A(); a.reset(m, Wb)
    for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
    torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode('error'); ok = True
    try:
        for t in range(3): um_passo(m, a, Wb); a.atualizar(m)
    except RuntimeError as e:
        ok = False; tb = traceback.extract_tb(sys.exc_info()[2]); fr = [f for f in tb if 'neuromod-lab/src' in f.filename]
        print(f'{A.__name__}: SYNC em {fr[-1].filename.split("/")[-1]}:{fr[-1].lineno} -> {fr[-1].line[:120]}', flush=True); print('  erro:', str(e)[:160], flush=True)
    torch.cuda.set_sync_debug_mode('default'); print(f'{A.__name__}: {"SEM SYNC" if ok else "SYNC!"}', flush=True)
