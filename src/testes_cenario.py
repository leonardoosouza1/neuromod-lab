"""PORTAO do E71 (cenario por parametro): (1) cenarios/base.json aplicado == flags default: mapas BIT-IGUAIS (custo, servicos, centros,
demanda, aliq, pmul, alug) e cfg igual; (2) cenario alterado muda so o que pede (ruas 1/5, dois perfis, demanda nova);
(3) [10/09 astra/a4] o juiz (politica_util.mundo) recebe corpo + cerebro do cenario e braco() resolve rotulo -> classe + ajuste.
[10/09 astra] REPROVA com exit 1: antes so imprimia True/False (portao que nunca reprovava)."""
import sys, os, json, argparse, copy; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from e43_campo import aplica_cenario, BRACOS; from politica_util import mundo, braco; from completo import SerCompleto
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OK = []
def chk(rotulo, **conds):
    OK.extend(bool(v) for v in conds.values()); print(rotulo + ': ' + ' | '.join(f'{k} {bool(v)}' for k, v in conds.items()), flush=True)
def flags():
    a = argparse.Namespace(L=200., dias=10., fitness='riqueza', nevoa=float('inf'), npx=12, respawn=20., pax_cidade=False, ponto=0., dinh0=10., fome_passo=None, kcal_pane=8., guincho=0., fuel_pane=15., P=None, G=None, paciencia=None, R=None, seeds=None, so=None, mundo='distinto'); return a
cen = json.load(open(os.path.join(REPO, 'cenarios', 'base.json'))); a = flags(); ex = aplica_cenario(a, cen)
m0 = gerar_mapa(1000, L=200., distinto=True); m1 = gerar_mapa(1000, L=a.L, distinto=a.mundo == 'distinto', perfis=ex['perfis'], K=ex['K'], ruas=ex['ruas'])
igual = all(torch.equal(m0[k], m1[k]) for k in ('custo', 'centros', 'demanda', 'aliq', 'pmul', 'alug', 'campo_dist', 'fase_preco')) and all(torch.equal(m0['serv'][t], m1['serv'][t]) for t in TIPOS)
chk('cenarios/base.json == defaults', mapas_bit_iguais=igual, flags_iguais=(a.L, a.dias, a.fitness, a.npx, a.respawn, a.pax_cidade, a.ponto, a.dinh0, a.kcal_pane, a.guincho, a.fuel_pane, a.P, a.G, a.paciencia, a.R, tuple(a.seeds)) == (200, 10, 'riqueza', 12, 20, False, 0, 10, 8, 0, 15, 1024, 120, 40, 4, (0, 1, 2, 3, 4)))
c2 = copy.deepcopy(cen); c2['mundo']['ruas'] = {'dentro': 1, 'fora': 5}; c2['distritos'] = {'rico': {'pmul': 3.0, 'aliq': .4, 'alug': 4., 'dem': 5.0, 'dens': [1, 1, 1, 1, 1]}, 'pobre': {'pmul': .4, 'aliq': 0., 'alug': .5, 'dem': .1, 'dens': [.3, .3, .3, .3, 0]}}
c2['passageiros']['pax_cidade'] = True; c2['passageiros']['npx'] = 3; c2['mundo']['K'] = 4
b = flags(); ex2 = aplica_cenario(b, c2); m2 = gerar_mapa(1000, L=b.L, distinto=True, perfis=ex2['perfis'], K=ex2['K'], ruas=ex2['ruas'])
chk('cenario alterado', custo_max_5=float(m2['custo'].max()) == 5., K4=m2['centros'].shape[0] == 4, demanda_so_5_e_01=set(round(float(x), 2) for x in m2['demanda']) <= {5.0, 0.1}, npx3_e_pax_cidade=(b.npx, b.pax_cidade) == (3, True))
c3 = copy.deepcopy(cen); c3['passageiros']['tarifa_base'] = 7.; c3['mundo']['precos'] = {'amp': .1, 'periodo': 5}; ex3 = aplica_cenario(flags(), c3)
chk('extras (tarifa_base 7, amp .1, periodo 5) chegam', ok=(ex3['tarifa_base'], ex3['amp_preco'], ex3['periodo_preco']) == (7., .1, 5))
# (3) juiz no MESMO mundo da evolucao: mundoB (custo_gene .3 modo ativacao, basal .15, ativ_centrada) e o ser 'COMPLETO talamo fixo'
cB, _, _, _ = mundo(os.path.join(REPO, 'cenarios', 'mundoB_conta_justa.json'))
chk('mundo() recebe corpo/cerebro do cenario', custo_gene=cB.custo_gene == .3, custo_modo=cB.custo_modo == 'ativacao', custo_basal=cB.custo_basal == .15, ativ_centrada=cB.ativ_centrada is True, gene_min=cB.gene_min == .5)
fake = {'bracos': {'COMPLETO talamo fixo': {'ser': {'nome': 'COMPLETO (talamo+cortex+hipocampo+reflexo+livre)', 'cerebro': {'talamo_norm': 'fixo'}}}, 'linear': {}}}
A1, c1 = braco(fake, 'COMPLETO talamo fixo', cB); A2, c2_ = braco(fake, 'linear', cB)
chk('braco() resolve rotulo -> classe + ajuste', talamo_fixo_e_SerCompleto=A1 is SerCompleto, talamo_norm_fixo=c1.talamo_norm == 'fixo', cfg_original_intacto=cB.talamo_norm is False, linear_e_Linear=A2 is Linear and c2_.talamo_norm is False)
# gene_min do cenario chega ao cfg da bateria (e43 main): antes era aceito e ignorado
c4 = copy.deepcopy(cen); c4.setdefault('corpo', {})['gene_min'] = .7; f4 = flags(); aplica_cenario(f4, c4)
chk('gene_min do cenario aplicado', flag_recebe=getattr(f4, 'gene_min', None) == .7, e43_copia_para_cfg='cfg.gene_min = float(getattr(a, \'gene_min\', cfg.gene_min))' in open(os.path.join(REPO, 'src', 'e43_campo.py')).read())
# (4) [10/09 astra] cfg do e43 (cfg_de_flags) vs cfg do juiz (mundo()) para o MESMO cenario: diferencas listadas; os campos do cenario tem de bater
from e43_campo import parser, cfg_de_flags
cenB = os.path.join(REPO, 'cenarios', 'mundoB_conta_justa.json'); fa = parser().parse_args(['--preset', 'fumaca', '--cenario', cenB]); fa._explicit = {'preset', 'cenario'}; exB = aplica_cenario(fa, json.load(open(cenB)))
TB = int(fa.T_max or 240*30) if fa.horizonte == 'aberto' else int(240*fa.dias); cE = cfg_de_flags(fa, exB, TB)
def _eq(x, y): return bool(torch.equal(x, y)) if torch.is_tensor(x) and torch.is_tensor(y) else x == y
dif = {k: (getattr(cE, k, '<ausente>'), getattr(cB, k, '<ausente>')) for k in sorted(set(vars(cE)) | set(vars(cB))) if not _eq(getattr(cE, k, None), getattr(cB, k, None))}
print(f'cfg e43 (cfg_de_flags) vs cfg do juiz (mundo()) no mundoB: {len(dif)} campos diferentes: {dif}', flush=True)
chk('cfg do juiz == cfg do e43 nos campos do cenario', **{k: _eq(getattr(cE, k, None), getattr(cB, k, None)) for k in ('L', 'fitness', 'T_max', 'horizonte', 'custo_gene', 'custo_modo', 'custo_basal', 'ativ_centrada', 'gene_min', 'NPX', 'respawn', 'pax_cidade', 'dinh0', 'fome_passo', 'KCAL_PANE', 'GUINCHO', 'FUEL_POS_PANE', 'retina', 'regime', 'reproducao', 'amp_preco', 'periodo_preco', 'w_trab', 'nevoa', 'ponto')})
assert all(OK), f'testes_cenario REPROVADO: {OK}'; print('testes_cenario: todos passaram', flush=True)
