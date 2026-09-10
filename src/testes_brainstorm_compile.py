"""[revisor 09-09] as 6 flags novas (temp_decisao com torch.rand no passo, talamo_norm por string em _gate, custo_canais no corpo, disparo,
cortex_amp, hip_esc) sob torch.compile == eager: rodar() compilado vs laco eager identico, todas as flags LIGADAS ao mesmo tempo.
Tolerancia = a de testes_campo (empates de argmax: <= 3 seres em 64)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *; from completo import SerCompleto
c = CfgCampo(L=200., fitness='riqueza'); c.temp_decisao = .3; c.talamo_norm = 'fixo'; c.custo_canais = ('fome', 'agua', 'calor'); c.custo_gene = .3; c.custo_modo = 'disparo'; c.custo_basal = .15; c.cortex_amp = 2.; c.hip_esc = 1.
mapas = [gerar_mapa(1000, L=200., distinto=True)]
g = torch.Generator(device=DEV); g.manual_seed(5); W = torch.randn(64, SerCompleto.NP, generator=g, device=DEV)*.3; W[:, :Linear.NP] = torch.randn(64, Linear.NP, generator=g, device=DEV)*.5
mc = rodar(SerCompleto, W, mapas, c, T=200, seed=3, R=2)
me = Campo(mapas, 64, c, seed=3, R=2); Wb = W[me.gidx]; a = SerCompleto(); a.reset(me, Wb)
for t in range(200): um_passo(me, a, Wb); a.atualizar(me)
dif = int(((mc.pos - me.pos).abs().max(1).values > 1e-6).sum()); B = mc.pos.shape[0]; ok = dif <= 3 and float((mc.metab - me.metab).abs().max()) < 1e-5
print(f'flags novas (temp .3, talamo fixo, 3 canais, disparo, cortex 2, hip 1): compilado vs eager: seres com pos diferente {dif}/{B} (tolerancia 3) | max dif pos {float((mc.pos-me.pos).abs().max()):.2e} vida {float((mc.vida-me.vida).abs().max()):.2e} metab {float((mc.metab-me.metab).abs().max()):.2e}', 'OK' if ok else 'FALHOU', flush=True)
sys.exit(0 if ok else 1)
