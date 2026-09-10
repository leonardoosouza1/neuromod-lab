"""[revisor 09-09] as flags novas sob torch.compile == eager, UMA POR VEZ (bissecao) e todas juntas: rodar() compilado vs laco eager
identico. Tolerancia = a de testes_campo (empates de argmax: <= 3 seres em 64). Sai com exit 1 se qualquer flag falhar e diz QUAL."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch; from campo import *; from completo import SerCompleto
mapas = [gerar_mapa(1000, L=200., distinto=True)]
g = torch.Generator(device=DEV); g.manual_seed(5); W = torch.randn(64, SerCompleto.NP, generator=g, device=DEV)*.3; W[:, :Linear.NP] = torch.randn(64, Linear.NP, generator=g, device=DEV)*.5
FLAGS = {'nenhuma': {}, 'temp_decisao': dict(temp_decisao=.3), 'talamo_fixo': dict(talamo_norm='fixo'), 'canais': dict(custo_canais=('fome', 'agua', 'calor'), custo_gene=.3, custo_basal=.15),
         'disparo': dict(custo_gene=.3, custo_modo='disparo'), 'cortex_amp': dict(cortex_amp=2.), 'hip_esc': dict(hip_esc=1.),
         'todas': dict(temp_decisao=.3, talamo_norm='fixo', custo_canais=('fome', 'agua', 'calor'), custo_gene=.3, custo_modo='disparo', custo_basal=.15, cortex_amp=2., hip_esc=1.)}
def roda(kw):
    c = CfgCampo(L=200., fitness='riqueza')
    for k, v in kw.items(): setattr(c, k, v)
    mc = rodar(SerCompleto, W, mapas, c, T=200, seed=3, R=2)
    me = Campo(mapas, 64, c, seed=3, R=2); Wb = W[me.gidx]; a = SerCompleto(); a.reset(me, Wb)
    for t in range(200): um_passo(me, a, Wb); a.atualizar(me)
    dif = int(((mc.pos - me.pos).abs().max(1).values > 1e-6).sum()); dm = float((mc.metab - me.metab).abs().max()); return dif, dm, float((mc.vida - me.vida).abs().max())
falhas = []
for nome, kw in FLAGS.items():
    dif, dm, dv = roda(kw); ok = dif <= 3 and dm < 1e-5; falhas += [] if ok else [nome]
    print(f'  {nome:14} compilado vs eager: seres com pos diferente {dif:3d}/128 (tolerancia 3) | max dif metab {dm:.1e} vida {dv:.2e}', 'OK' if ok else 'FALHOU', flush=True)
print('PORTAO BRAINSTORM COMPILE', 'ok' if not falhas else f'FALHOU em {falhas}', flush=True); sys.exit(0 if not falhas else 1)
