"""PORTAO DE IMPORTACAO (roda na GPU pela fila, nunca em CPU — regra do Leonardo 09/09): importa todos os modulos editados e confere os objetos
que as edicoes deveriam ter criado, com as flags de sentido do ambiente. Substitui qualquer 'import em CPU para verificar'."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts', 'agentes'))
os.environ['NM_COMPILE'] = '0'
import torch; import campo, completo, e43_campo, politica_util
from campo import *
ok = True
def chk(nome, cond):
    global ok; ok &= bool(cond); print(f'  {nome}: {"OK" if cond else "FALHOU"}', flush=True)
c = CfgCampo(L=200.)
chk('cfg novos (retina/regime/reproducao/custo_basal/horizonte)', all(hasattr(c, k) for k in ('retina', 'regime', 'reproducao', 'custo_basal', 'custo_modo', 'horizonte', 'T_max', 'w_trab', 'amostra_ativ')))
chk('padroes', bool(RETINA_PADRAO) and bool(REGIME_PADRAO) and bool(REPRODUCAO_PADRAO))
chk('GRUPOS cobrem NF', sum(len(ix) for _, ix in completo.GRUPOS) == NF and sorted(i for _, ix in completo.GRUPOS for i in ix) == list(range(NF)))
chk('nomes_genes_completos == NP - Linear.NP', len(completo.nomes_genes_completos()) == completo.SerCompleto.NP - Linear.NP)
chk('Cerebro.nomes_genes', len(campo.Cerebro.nomes_genes()) == campo.Cerebro.NP - Linear.NP)
chk('SemRapida/SemLenta', completo.SemRapida.liga.get('rapida') is False and completo.SemLenta.liga.get('lenta') is False)
chk('BRACOS com sem rapida/lenta', any('sem rapida' in n for n, _ in e43_campo.BRACOS) and any('sem lenta' in n for n, _ in e43_campo.BRACOS))
chk('_LAYOUTS 37..40', sorted(e43_campo._LAYOUTS) == [37, 38, 39, 40] and len(e43_campo.alinha_semente([1.]*38)) == Linear.NP)
chk('IDX_LAYOUT29 (se retina/regime)', (not (RETINA or REGIME)) or int(politica_util.IDX_LAYOUT29.numel()) == 29)
chk('rodar tem cobra_ativ/medir_ativ; e43 tem hash/dispositivo/custo-basal', all(k in open(campo.__file__).read() for k in ('cobra_ativ', 'medir_ativ')) and all(k in open(e43_campo.__file__).read() for k in ('cenario_hash', 'dispositivo', '--custo-basal')))
m = Campo([gerar_mapa(1000, L=200., distinto=True)], 8, c, seed=1, R=1); F, _ = m.obs(); chk('obs() colunas == NF', F.shape[-1] == NF)
import json as _json, dimensiona
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
chk('juiz nao corta: medidas zera corte_vivos', 'cfg_m.corte_vivos = 0.' in open(campo.__file__).read())
chk('dimensiona: constantes espelhadas == codigo', (dimensiona.CAIXAS_MAX, dimensiona.TICKS_DIA, dimensiona.RETINA_R_DIA, dimensiona.RAIO_PX) == (completo.DMAX, c.dia, RETINA_PADRAO['R_dia'], c.raio_px) and dimensiona.TAU_MAX_TICKS == 201 and '1. + 200.*torch.sigmoid' in open(campo.__file__).read())
_cen = {n: _json.load(open(os.path.join(REPO, 'cenarios', f'mundo{n}_{s}.json'))) for n, s in (('A', 'seres'), ('B', 'conta_justa'), ('C', 'cidade_da_vida'))}
_r = {n: dimensiona.razoes(v) for n, v in _cen.items()}
chk('dimensiona: Mundo A e B reprovam nas 3 razoes', all(set(_r[n]['fora']) == set(dimensiona.ORDEM) for n in ('A', 'B')))
chk('dimensiona: Mundo C so amostras_por_caixa fora', _r['C']['fora'] == ['amostras_por_caixa'])
chk('dimensiona: C mede 92 de lado e 3+ ciclos por vida', _r['C']['constantes']['L'] == 92. and _r['C']['razoes']['ciclos_por_vida']['valor'] >= 3. and _r['C']['razoes']['cidade_ao_alcance']['valor'] >= .50)
print('\n'.join(dimensiona.linhas(_r['C'])), flush=True)
print('PORTAO IMPORT', 'VERDE' if ok else 'VERMELHO', '| NF', NF, 'flags', dict(RISCO=RISCO, PONTO=PONTO, RETINA=RETINA, REGIME=REGIME), flush=True); sys.exit(0 if ok else 1)
