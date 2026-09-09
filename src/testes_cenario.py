"""PORTAO do E71 (cenario por parametro): (1) cenarios/base.json aplicado == flags default: mapas BIT-IGUAIS (custo, servicos, centros,
demanda, aliq, pmul, alug) e cfg igual; (2) cenario alterado muda so o que pede (ruas 1/5, dois perfis, demanda nova)."""
import sys, os, json, argparse, copy; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from e43_campo import aplica_cenario
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def flags():
    a = argparse.Namespace(L=200., dias=10., fitness='riqueza', nevoa=float('inf'), npx=12, respawn=20., pax_cidade=False, ponto=0., dinh0=10., fome_passo=None, kcal_pane=8., guincho=0., fuel_pane=15., P=None, G=None, paciencia=None, R=None, seeds=None, so=None, mundo='distinto'); return a
cen = json.load(open(os.path.join(REPO, 'cenarios', 'base.json'))); a = flags(); ex = aplica_cenario(a, cen)
m0 = gerar_mapa(1000, L=200., distinto=True); m1 = gerar_mapa(1000, L=a.L, distinto=a.mundo == 'distinto', perfis=ex['perfis'], K=ex['K'], ruas=ex['ruas'])
igual = all(torch.equal(m0[k], m1[k]) for k in ('custo', 'centros', 'demanda', 'aliq', 'pmul', 'alug', 'campo_dist', 'fase_preco')) and all(torch.equal(m0['serv'][t], m1['serv'][t]) for t in TIPOS)
print('cenarios/base.json == defaults: mapas bit-iguais:', igual, '| flags iguais:', (a.L, a.dias, a.fitness, a.npx, a.respawn, a.pax_cidade, a.ponto, a.dinh0, a.kcal_pane, a.guincho, a.fuel_pane, a.P, a.G, a.paciencia, a.R, tuple(a.seeds)) == (200, 10, 'riqueza', 12, 20, False, 0, 10, 8, 0, 15, 1024, 120, 40, 4, (0, 1, 2, 3, 4)), flush=True)
c2 = copy.deepcopy(cen); c2['mundo']['ruas'] = {'dentro': 1, 'fora': 5}; c2['distritos'] = {'rico': {'pmul': 3.0, 'aliq': .4, 'alug': 4., 'dem': 5.0, 'dens': [1, 1, 1, 1, 1]}, 'pobre': {'pmul': .4, 'aliq': 0., 'alug': .5, 'dem': .1, 'dens': [.3, .3, .3, .3, 0]}}
c2['passageiros']['pax_cidade'] = True; c2['passageiros']['npx'] = 3; c2['mundo']['K'] = 4
b = flags(); ex2 = aplica_cenario(b, c2); m2 = gerar_mapa(1000, L=b.L, distinto=True, perfis=ex2['perfis'], K=ex2['K'], ruas=ex2['ruas'])
print('cenario alterado: custo max 5:', float(m2['custo'].max()) == 5., '| K=4:', m2['centros'].shape[0] == 4, '| demanda so {5, .1}:', set(round(float(x), 2) for x in m2['demanda']) <= {5.0, 0.1}, '| flags: npx 3 e pax_cidade:', (b.npx, b.pax_cidade) == (3, True), flush=True)
c3 = copy.deepcopy(cen); c3['passageiros']['tarifa_base'] = 7.; c3['mundo']['precos'] = {'amp': .1, 'periodo': 5}; ex3 = aplica_cenario(flags(), c3)
print('extras (tarifa_base 7, amp .1, periodo 5) chegam:', (ex3['tarifa_base'], ex3['amp_preco'], ex3['periodo_preco']) == (7., .1, 5), flush=True)
