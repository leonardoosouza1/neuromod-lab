"""JUIZ de UMA politica explicita (agentes) — usa politica_util (mundo do juiz definido num lugar so; revisao 09-09 apagou a copia).
Imprime os parametros do mundo na 1a linha; campeao evoluido como referencia; autopsia + traco."""
import sys, os, json, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from politica_util import *
ap = argparse.ArgumentParser(); ap.add_argument('--politica', required=True); ap.add_argument('--cenario', default=None); ap.add_argument('--nevoa', type=float, default=None); ap.add_argument('--campeao', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e64/e43_busca8x_L200.json')
ap.add_argument('--copias', type=int, default=128); ap.add_argument('--seeds', type=int, nargs='*', default=[7777, 7778, 7779, 7780, 7781]); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/agentes'); ap.add_argument('--tag', default='')
ap.add_argument('--braco', default='linear', help='[10/09 CS docs/87 §1] braco da bateria --campeao usado como referencia (rotulo de BRACOS, ex. "COMPLETO (talamo+cortex+hipocampo+reflexo+livre)"): classe e ajustes vem de politica_util.braco; a chave linear_campeao no JSON fica pelo nome (compatibilidade) e res["braco"] diz qual e')
ap.add_argument('--W-politica', default='zero', choices=('zero', 'campeao'), help='[10/09 pred 179b] W que entra no um_passo junto com a politica: zero (hoje: o `tudo` do decidir e zero, a politica so ve F) | campeao (o `tudo` vira a nota do campeao linear: politicas que FILTRAM a decisao do campeao, ex. sem FICAR)')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
cfg, teste, T, chave = mundo(a.cenario, nevoa=a.nevoa)
print(f'== juiz de politica | {os.path.basename(a.politica)} | cenario {a.cenario or "base"} | mundo: L {cfg.L} dias {T/240:.0f} regua {cfg.fitness} guincho {cfg.GUINCHO} fuel_pane {cfg.FUEL_POS_PANE} kcal_pane {cfg.KCAL_PANE} dinh0 {cfg.dinh0} nevoa {cfg.nevoa} retina {bool(cfg.retina)} regime {bool(cfg.regime)} | {len(a.seeds)} sementes x {a.copias} copias x 3 mapas ==', flush=True)
POL, erro = carrega(a.politica)
if erro: raise SystemExit(f'POLITICA RECUSADA: {erro}')
Jd = json.load(open(a.campeao)); ArqC, cfgC = braco(Jd, a.braco, cfg); Wc = torch.tensor(alinha_semente(Jd['bracos'][a.braco]['W']['0']), device=DEV); Wz = torch.zeros(Linear.NP, device=DEV)   # [10/09 CS docs/87 §1] --braco: o campeao de referencia pode ser um cerebro (SerCompleto etc.), nao so o linear
if a.braco != 'linear' and a.W_politica == 'campeao': raise SystemExit('--W-politica campeao so com --braco linear (o W do cerebro nao e o `tudo` de uma politica linear)')
res = dict(politica=a.politica, cenario=a.cenario, mundo=dict(guincho=cfg.GUINCHO, fuel_pane=cfg.FUEL_POS_PANE, kcal_pane=cfg.KCAL_PANE, dinh0=cfg.dinh0, nevoa=cfg.nevoa, retina=cfg.retina, regime=cfg.regime))
res['braco'] = a.braco; res['linear_campeao'] = mede(ArqC, Wc, cfgC, teste, T, a.seeds, a.copias); print('  ' + linha(f'campeao {a.braco[:20]} (q8)', res['linear_campeao']), flush=True)
Wp = Wc if a.W_politica == 'campeao' else Wz; res['W_politica'] = a.W_politica   # [10/09 pred 179b] sem isto, apagar uma coluna de `tudo` = 'direcao 0 sempre'
tr = traco(POL, Wp, cfg, teste); res['politica_res'] = mede(POL, Wp, cfg, teste, T, a.seeds, a.copias); res['traco'] = tr; print('  ' + linha('politica do agente', res['politica_res'], tr), flush=True)
res['dif_mortos'] = res['politica_res']['mortos'] - res['linear_campeao']['mortos']
json.dump(res, open(os.path.join(a.out, f'julga{a.tag}.json'), 'w'), indent=1); print(f"dif mortos (politica - linear) {res['dif_mortos']:+.3f}", flush=True)
