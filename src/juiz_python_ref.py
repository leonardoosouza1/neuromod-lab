"""[pred 174] referencia do JUIZ em Python nas MESMAS condicoes do juiz Rust (taxi_evolve --G 0): mundo v0 sem retina/regime/custo,
corpo/passageiros do cenario (dinh0 10, guincho 10, fuel_pos_pane 5, kcal_pane 8, respawn 20, ponto 0), regua vida, horizonte aberto
T_max 7200, mapa gerar_mapa(1000) (o mesmo do traco), campeao linear e64 alinhado por nome (e_demanda/e_espera = 0), 128 copias,
semente 7777. Tambem com o campeao + N(0, .05) na espinha (o G=0 do Rust devolve a copia 0 da populacao semeada, que tem esse ruido)."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *
N = '/media/llm-data/universe-runs/neuromod-lab-taxi'; cen = json.load(open('/home/leonardo/projects/LLM/neuromod-lab/cenarios/mundoA_seres.json'))
c = CfgCampo(L=200., fitness='vida'); co = cen['corpo']; c.dinh0 = co['dinh0']; c.fome_passo = co['fome_passo']; c.KCAL_PANE = co['kcal_pane']; c.GUINCHO = co['guincho']; c.FUEL_POS_PANE = co['fuel_pos_pane']
px = cen['passageiros']; c.NPX = px['npx']; c.respawn = px['respawn']; c.pax_cidade = px['pax_cidade']; c.ponto = px['ponto']; c.tarifa_base = px['tarifa_base']; c.tarifa_km = px['tarifa_km']; c.horizonte = 'aberto'; c.T_max = 7200; c.w_trab = 1.0
assert NF == 29 and Linear.NP == 40, (NF, Linear.NP)
mapa = gerar_mapa(1000, L=200., distinto=True); J = json.load(open(f'{N}/e82/campeao_e64_linear_40.json')); W = torch.tensor(J['bracos']['linear']['W']['0'], device=DEV)
g = torch.Generator(device=DEV); g.manual_seed(0); Wr = W + torch.randn(40, generator=g, device=DEV)*.05
for rot, w in (('campeao exato', W), ('campeao + N(0,.05)', Wr)):
    med = medidas(Linear, w, [mapa], c, T=7200, seed=7777, R=1, copias=128)
    print(f"  Python juiz ({rot}): fit {med['fit']:.3f} | mortos {med['mortos']:.2f} | ent {med['ent']:.2f} | t_vida {med['t_vida']['media']:.2f} d (mediana {med['t_vida']['mediana']:.2f}, p10 {med['t_vida']['p10']:.2f}, p90 {med['t_vida']['p90']:.2f}) | rec {med['rec']:.1f}", flush=True)
print('  Rust juiz (G=0, copia 0 semeada): fit 4.198 | mortos 1.00 | ent 12.27 | t_vida 3.82 d (mediana 3.36, p10 1.56, p90 6.65) | rec 114.4', flush=True)
