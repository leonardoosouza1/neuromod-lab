"""[porta para o Universe] TRACO DE REFERENCIA: exporta tudo que a reimplementacao em Rust precisa para reproduzir o mundo do taxi
sem o RNG do torch: o MAPA (textura de custo, pontos de servico por tipo, centros/perfis dos distritos, campo de distrito), o GENOMA
(campeao linear e64 alinhado por nome), o estado inicial de cada ser (berco, corpo, vagas de passageiro com destino) e o traco por
tique (pos, acao, fuel, fome, agua, dinh, vida, calor, fad, res, pd_) com passageiros SEM respawn e sem ponto — assim a trajetoria e'
deterministica dado o genoma, e o Rust pode comparar tique a tique (tolerancia float). GPU, segundos. Saida: e81/traco_ref.json"""
import sys, os, json, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from e43_campo import alinha_semente
ap = argparse.ArgumentParser(); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e81'); ap.add_argument('--B', type=int, default=16); ap.add_argument('--T', type=int, default=2400); ap.add_argument('--seed-mapa', type=int, default=1000)
ap.add_argument('--campeao', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e64/e43_busca8x_L200.json'); a = ap.parse_args()
mapa = gerar_mapa(a.seed_mapa, L=200., distinto=True); J = json.load(open(a.campeao)); Jw = J['bracos']['linear']['W']; W = torch.tensor(alinha_semente(Jw[sorted(Jw)[0]], J.get('nomes_f')), device=DEV)[None, :].repeat(a.B, 1)
c = CfgCampo(L=200., fitness='vida'); c.respawn = 1e9; c.ponto = 0.; c.grava_acoes = True; c.horizonte = 'fixo'
m = Campo([mapa], a.B, c, seed=7, R=1); Wb = W[m.gidx]; ar = Linear(); ar.reset(m, Wb)
ini = dict(pos=m.pos.tolist(), fuel=m.fuel.tolist(), fome=m.fome.tolist(), agua=m.agua.tolist(), dinh=m.dinh.tolist(), vida=m.vida.tolist(), calor=m.calor.tolist(), fad=m.fad.tolist(), res=m.res.tolist(), fase=m.fase.tolist(), px=m.px.tolist(), pxd=m.pxd.tolist(), px_ok=m.px_ok.tolist(), casa=m.casa.tolist())
m.GRAVA = True; m.acoes = torch.full((a.T, m.B), -1, dtype=torch.long, device=DEV); m.traj = torch.zeros(a.T, m.B, 7, device=DEV); extra = torch.zeros(a.T, m.B, 4, device=DEV)
for t in range(a.T):
    um_passo(m, ar, Wb); ar.atualizar(m); extra[t] = torch.stack([m.calor, m.fad, m.res, m.pd_.float()], 1)
def T(x): return x.tolist() if hasattr(x, 'tolist') else x
saida = dict(L=200., seed_mapa=a.seed_mapa, B=a.B, T=a.T, dia=c.dia, nomes_f=NOMES_F, nomes_op=NOMES_OP, nomes_corpo=NOMES_CORPO, acoes=[list(x) for x in ACOES], tipos=TIPOS, G=G, S=S,
             cfg={k: (v if isinstance(v, (int, float, str, bool, type(None))) else str(v)) for k, v in vars(c).items()},
             mapa=dict(custo=T(mapa['custo']), serv={t: T(mapa['serv'][t]) for t in TIPOS}, centros=T(mapa['centros']), aliq=T(mapa['aliq']), pmul=T(mapa['pmul']), alug=T(mapa['alug']), demanda=T(mapa.get('demanda')), campo_dist=T(mapa['campo_dist']), perfis=[str(p) for p in mapa.get('perfis', [])] if isinstance(mapa.get('perfis'), (list, tuple)) else str(mapa.get('perfis'))),
             genoma=W[0].tolist(), inicial=ini, acoes_por_tique=m.acoes.tolist(), traco=m.traj.tolist(), traco_extra=extra.tolist(), t_vida=m.t_vida.tolist(), rec=m.rec.tolist())
os.makedirs(a.out, exist_ok=True); p = os.path.join(a.out, 'traco_ref.json'); json.dump(saida, open(p, 'w')); print(f'traco de referencia: B {a.B} T {a.T} | t_vida {[round(x/240., 2) for x in m.t_vida.tolist()]} d | rec {[round(x, 1) for x in m.rec.tolist()]} | gravado {p} ({os.path.getsize(p)//1024} KB)', flush=True)
