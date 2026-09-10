"""[10/09 seres no mesmo lote] PORTAO: (1) um ser sozinho em cfg.seres (mascara 1, ajustes padrao) == caminho de sempre bit a bit (SerCompleto);
(2) ser 'linear' (genes extras travados) rodado como SerCompleto == Linear bit a bit; (3) ser 'sem hipocampo' == classe SemHipocampo bit a bit
(custo 0); (4) hip_esc=1 por ser == cfg.hip_esc=1 bit a bit; (5) lote misto (linear + COMPLETO + sem hip) roda e a populacao do linear
tem genes extras exatamente zero apos evoluir com mascara (2 geracoes, P=8). Exit 1 se falhar."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from completo import SerCompleto, SemHipocampo; from e43_campo import _ser_entrada
mapas = [gerar_mapa(1000, L=200., distinto=True)]; g = torch.Generator(device=DEV); g.manual_seed(5); B = 64
W = torch.randn(B, SerCompleto.NP, generator=g, device=DEV)*.3; W[:, :Linear.NP] = torch.randn(B, Linear.NP, generator=g, device=DEV)*.5
def cfg(**kw):
    c = CfgCampo(L=200., fitness='riqueza')
    for k, v in kw.items(): setattr(c, k, v)
    return c
def igual(m0, m1): return all(torch.equal(getattr(m0, k), getattr(m1, k)) for k in ('pos', 'vida', 'fome', 'fuel', 'dinh'))
ok = []
e1, k1 = _ser_entrada('COMPLETO', 'COMPLETO (talamo+cortex+hipocampo+reflexo+livre)', SerCompleto, {})
m0 = rodar(SerCompleto, W, mapas, cfg(), T=200, seed=3, R=1); m1 = rodar(SerCompleto, W*k1, mapas, cfg(seres=dict(P=B, lista=[e1])), T=200, seed=3, R=1); r = igual(m0, m1); ok.append(r); print('(1) COMPLETO sozinho em seres == de sempre:', r, flush=True)
e2, k2 = _ser_entrada('linear', 'linear', Linear, {})
m0 = rodar(Linear, W[:, :Linear.NP].contiguous(), mapas, cfg(), T=200, seed=3, R=1); m1 = rodar(SerCompleto, W*k2, mapas, cfg(seres=dict(P=B, lista=[e2])), T=200, seed=3, R=1); r = igual(m0, m1); ok.append(r); print('(2) ser linear (SerCompleto mascarado) == Linear:', r, '| genes extras zero:', bool(((W*k2)[:, Linear.NP:] == 0).all()), flush=True)
e3, k3 = _ser_entrada('sem hip', 'completo sem hipocampo', SemHipocampo, {})
m0 = rodar(SemHipocampo, W*k3, mapas, cfg(), T=200, seed=3, R=1); m1 = rodar(SerCompleto, W*k3, mapas, cfg(seres=dict(P=B, lista=[e3])), T=200, seed=3, R=1); r = igual(m0, m1); ok.append(r); print('(3) ser sem hipocampo == classe SemHipocampo:', r, '| genes hip zerados:', int((k3 == 0).sum()), flush=True)
e4, k4 = _ser_entrada('hip1', 'COMPLETO (talamo+cortex+hipocampo+reflexo+livre)', SerCompleto, {'hip_esc': 1.0})
m0 = rodar(SerCompleto, W, mapas, cfg(hip_esc=1.), T=200, seed=3, R=1); m1 = rodar(SerCompleto, W, mapas, cfg(seres=dict(P=B, lista=[e4])), T=200, seed=3, R=1); r = igual(m0, m1); ok.append(r); print('(4) hip_esc=1 por ser == cfg.hip_esc=1:', r, flush=True)
import lab; ents = [e2, e1, e3]; msks = [k2, k1, k3]; pops = [(sd, j) for sd in (0, 1) for j in range(3)]; masc = torch.stack([msks[j] for _, j in pops]); c5 = cfg(seres=dict(P=8, lista=ents))
ch = lab.evoluir_sementes(SerCompleto, mapas, c5, P=8, ger=2, T=120, seeds=(0, 1), R=1, verbose=False, avaliar_fn=avaliar, pops=pops, mascaras=masc, sigma_mut=.1)
r = set(ch.keys()) == set(pops) and bool((ch[(0, 0)][0][Linear.NP:] == 0).all()) and bool((ch[(1, 0)][0][Linear.NP:] == 0).all()) and bool((ch[(0, 1)][0][Linear.NP:] != 0).any()); ok.append(r)
print('(5) lote misto 3 seres x 2 sementes evolui; linear fica so espinha, COMPLETO tem genes extras:', r, '| chaves', sorted(ch.keys())[:3], flush=True)
print('PORTAO SERES', 'ok' if all(ok) else 'FALHOU', flush=True); sys.exit(0 if all(ok) else 1)
