"""portao do E54: completo com genes de saida 0 == Linear bit a bit (entradas aleatorias); cada parte desligada == transparente; sem sync; partes vivas com genes."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *; from completo import *
c = CfgCampo(L=200., fitness='bemestar'); mapas = [gerar_mapa(1000, L=200.)]; os.environ['NM_COMPILE'] = '0'
A = SerCompleto; Wl = torch.randn(16, Linear.NP, device=DEV)*.5; Wc = torch.randn(16, A.NP, device=DEV)*.8; Wc[:, :Linear.NP] = Wl
Wc[:, A.O_V:A.O_U2] = 0.; Wc[:, A.O_M:A.NP] = 0.                          # saidas do livre, reflexo (w,v: nao zerados ainda), talamo, cortex, hipocampo
Wc[:, A.O_REF+1:A.O_REF+3] = 0.; Wc[:, A.O_TAL:A.O_TAL+A.N_TAL] = 0.; Wc[:, A.O_COR:A.O_COR+A.N_COR] = 0.; Wc[:, A.O_HIP+1] = 0.
m1 = rodar(Linear, Wl, mapas, c, T=300, seed=3, R=2); m2 = rodar(A, Wc, mapas, c, T=300, seed=3, R=2)
print('completo transparente == linear:', float((m1.pos-m2.pos).abs().max())==0.0, '| NP', A.NP, flush=True)
Wr = torch.randn(16, A.NP, device=DEV)*.8; Wr[:, :Linear.NP] = Wl
for nome, P, blocos in (('sem-talamo', SemTalamo, [(A.O_TAL, A.O_TAL+A.N_TAL)]), ('sem-cortex', SemCortex, [(A.O_COR, A.O_COR+A.N_COR)]), ('sem-hipocampo', SemHipocampo, [(A.O_HIP+1, A.O_HIP+2)]),
                        ('sem-reflexo', SemReflexo, [(A.O_REF+1, A.O_REF+3)]), ('sem-livre', SemLivre, [(A.O_V, A.O_U2), (A.O_M, A.NP)])):
    Wz = Wr.clone()
    for i0, i1 in blocos: Wz[:, i0:i1] = 0.
    ma = rodar(P, Wr, mapas, c, T=200, seed=3, R=2); mb = rodar(A, Wz, mapas, c, T=200, seed=3, R=2)
    print(f'{nome:<14} desligado == genes zerados: {float((ma.pos-mb.pos).abs().max())==0.0}', flush=True)
m = Campo(mapas, 32, c, seed=1, R=2); Wb = (torch.randn(32, A.NP, device=DEV)*.8)[m.gidx]; a = A(); a.reset(m, Wb)
for t in range(300): um_passo(m, a, Wb); a.atualizar(m)
at = a.ativacao(m); print('partes vivas: gates', [round(float(at[f'talamo_{k}'].mean()), 2) for k in NOMES_G], '| mem_renda', round(float(at['mem_renda_abs'].mean()), 3), 'mem_espera', round(float(at['mem_espera_abs'].mean()), 3),
      '| reflexo frac', round(float(at['reflexo_frac'].mean()), 2), '| z', [round(float(at[f'lenta_z{k}'].mean()), 2) for k in range(A.K)], flush=True)
torch.cuda.synchronize(); torch.cuda.set_sync_debug_mode("error"); ok = True
try:
    for t in range(5): um_passo(m, a, Wb); a.atualizar(m)
except RuntimeError as e: ok = False
torch.cuda.set_sync_debug_mode("default"); print('SEM SYNC' if ok else 'SYNC!', flush=True)
