"""JUIZ de UMA politica explicita (agentes) — usa politica_util (mundo do juiz definido num lugar so; revisao 09-09 apagou a copia).
Imprime os parametros do mundo na 1a linha; campeao evoluido como referencia; autopsia + traco."""
import sys, os, json, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from politica_util import *
ap = argparse.ArgumentParser(); ap.add_argument('--politica', required=True); ap.add_argument('--cenario', default=None); ap.add_argument('--nevoa', type=float, default=None); ap.add_argument('--campeao', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e64/e43_busca8x_L200.json')
ap.add_argument('--copias', type=int, default=128); ap.add_argument('--seeds', type=int, nargs='*', default=[7777, 7778, 7779, 7780, 7781]); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/agentes'); ap.add_argument('--tag', default='')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
cfg, teste, T, chave = mundo(a.cenario, nevoa=a.nevoa)
print(f'== juiz de politica | {os.path.basename(a.politica)} | cenario {a.cenario or "base"} | mundo: L {cfg.L} dias {T/240:.0f} regua {cfg.fitness} guincho {cfg.GUINCHO} fuel_pane {cfg.FUEL_POS_PANE} kcal_pane {cfg.KCAL_PANE} dinh0 {cfg.dinh0} nevoa {cfg.nevoa} retina {bool(cfg.retina)} regime {bool(cfg.regime)} | {len(a.seeds)} sementes x {a.copias} copias x 3 mapas ==', flush=True)
POL, erro = carrega(a.politica)
if erro: raise SystemExit(f'POLITICA RECUSADA: {erro}')
J = json.load(open(a.campeao))['bracos']['linear']['W']; Wc = torch.tensor(alinha_semente(J['0']), device=DEV); Wz = torch.zeros(Linear.NP, device=DEV)
res = dict(politica=a.politica, cenario=a.cenario, mundo=dict(guincho=cfg.GUINCHO, fuel_pane=cfg.FUEL_POS_PANE, kcal_pane=cfg.KCAL_PANE, dinh0=cfg.dinh0, nevoa=cfg.nevoa, retina=cfg.retina, regime=cfg.regime))
res['linear_campeao'] = mede(Linear, Wc, cfg, teste, T, a.seeds, a.copias); print('  ' + linha('linear campeao (q8)', res['linear_campeao']), flush=True)
tr = traco(POL, Wz, cfg, teste); res['politica_res'] = mede(POL, Wz, cfg, teste, T, a.seeds, a.copias); res['traco'] = tr; print('  ' + linha('politica do agente', res['politica_res'], tr), flush=True)
res['dif_mortos'] = res['politica_res']['mortos'] - res['linear_campeao']['mortos']
json.dump(res, open(os.path.join(a.out, f'julga{a.tag}.json'), 'w'), indent=1); print(f"dif mortos (politica - linear) {res['dif_mortos']:+.3f}", flush=True)
