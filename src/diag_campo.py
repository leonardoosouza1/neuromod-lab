"""Diagnostico do campo: campeao do JSON, 192 vidas de N dias; t_vida, refeicoes, agua, abastecimentos, estado na morte; e variante 'comer forcado'.
Uso: python src/diag_campo.py <e43.json> "<braco>" [dias]"""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import torch, campo as C
from campo import *
J = json.load(open(sys.argv[1])); b = J['bracos'][sys.argv[2]]; dias = float(sys.argv[3]) if len(sys.argv) > 3 else 10.; T = int(240*dias)
L = float(J['L']); cfg = CfgCampo(L=L, fitness=J.get('fitness', 'bemestar')); mapas = [gerar_mapa(1000+s, L=L) for s in range(3)]
A = {'linear': Linear, 'reflexo': Reflexo}.get(sys.argv[2].split(' ')[0], Produto)
W = torch.tensor(b['W'][sorted(b['W'])[0]], device=DEV)
class ComeForcado(A):
    LIM = 60.
    def decidir(s, tudo, m):
        esc = tudo.argmax(1); _, sv = m.serv_need()
        forca = (m.fome >= s.LIM) & (sv[:, 7] > 0) & (m.dinh >= 3.)
        return torch.where(forca, torch.full_like(esc, G+7), esc)
for nome, Arq in (('campeao', A), ('campeao + comer forcado (fome>=60)', ComeForcado)):
    m = rodar(Arq, W[None, :].repeat(64, 1), mapas, cfg, T=T, seed=5, R=1)
    morto = m.vida <= 0
    print(f'{nome:<36} mortos {float(morto.float().mean()):.2f} t_vida {float(m.t_vida.mean()):5.0f}/{T} ent {float(m.ent.mean()):5.1f} come {float(m.n_come.mean()):4.1f} agua {float(m.n_agua.mean()):4.1f} abast {float(m.n_posto.mean()):4.1f} panes {float(m.av_fuel.mean()):3.1f} avar {float(m.avar.mean()):4.1f} | fim: fome {float(m.fome.mean()):3.0f} agua {float(m.agua.mean()):3.0f} fuel {float(m.fuel.mean()):3.0f} dinh {float(m.dinh.mean()):4.0f} res {float(m.res.mean()):3.0f} vida {float(m.vida.mean()):3.0f}', flush=True)
    if morto.any():
        print(f'    mortos: fome>=90 {float((m.fome[morto]>=90).float().mean()):.0%} agua<=10 {float((m.agua[morto]<=10).float().mean()):.0%} dinh<3 {float((m.dinh[morto]<3).float().mean()):.0%} dano_soma medio {float(m.dano_soma[morto].mean()):.0f}', flush=True)
# distancia media a comida no mapa e raio
mm = Campo(mapas, 1, cfg, seed=1, R=64); pts, d = mm._perto_todos(mm.pos); print('distancia media inicial a comida/agua/posto:', [round(float(d[:, j].mean()), 1) for j in (1, 2, 0)], '| raio', cfg.raio, '| pontos de comida por mapa', mapas[0]['serv']['comida'].shape[0])
