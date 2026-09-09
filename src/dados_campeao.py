"""DADOS TICK A TICK do campeao evoluido (e opcionalmente de uma politica): quando abastece (nivel do tanque, dinheiro, litros), quando
come (fome), onde a pane acontece (distancia ao posto, tanque), intervalo entre corridas, fracao do tempo livre dentro do raio de um
servico, o que faz por hora do dia. Sai um markdown para os agentes (docs/agentes/dados_*.md) — dados, nao palpite."""
import sys, os, json, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from politica_util import *
ap = argparse.ArgumentParser(); ap.add_argument('--campeao', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e64/e43_busca8x_L200.json'); ap.add_argument('--politica', default=None)
ap.add_argument('--cenario', default=None); ap.add_argument('--B', type=int, default=96); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/agentes'); ap.add_argument('--md', default='/home/leonardo/projects/LLM/neuromod-lab/docs/agentes/dados_campeao.md'); ap.add_argument('--tag', default='')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
cfg, teste, T, _ = mundo(a.cenario)
def q(xs): 
    if len(xs) == 0: return 'n/a'
    t = torch.tensor(xs); return f'mediana {t.median():.1f} (p10 {t.quantile(.1):.1f}, p90 {t.quantile(.9):.1f}, n={len(xs)})'
def coleta(Arq, W, nome):
    m = Campo(teste, a.B, cfg, seed=7777, R=1); Wb = W[None, :].repeat(a.B, 1)[m.gidx]; ar = Arq(); ar.reset(m, Wb)
    ev = {k: [] for k in ('fuel_abast', 'dinh_abast', 'litros_abast', 'dposto_abast', 'fome_come', 'fuel_pane', 'dposto_pane', 'dt_corrida', 'hora_abast', 'hora_come', 'agua_bebe', 'vida_oficina')}
    ult_ent = torch.zeros(m.B, device=DEV); raio_livre = 0.; livre_t = 0.; hist_h = torch.zeros(24, 4, device=DEV)   # por hora: move, abast, come, corrida
    for t in range(T):
        F, val = m.obs(); n0 = (m.n_posto.clone(), m.n_come.clone(), m.av_fuel.clone(), m.ent.clone(), m.n_agua.clone() if hasattr(m, 'n_agua') else None, m.n_oficina.clone()); fuel0 = m.fuel.clone(); fome0 = m.fome.clone(); dinh0 = m.dinh.clone(); agua0 = m.agua.clone(); vida0 = m.vida.clone(); dposto0 = m._dist[:, 0].clone(); lit0 = m.litros.clone(); h = int(m.hora()) % 24
        sc = torch.einsum('bgf,bf->bg', F, Wb[:, :NF]) + ar.extra(m, Wb, F); sc = sc - sc.mean(1, keepdim=True); svn, sv = m.serv_need(); ss = (svn*Wb[:, NF:NF+S] + Wb[:, NF+S:NF+S+1]).masked_fill(sv <= 0, -1e9); tudo = torch.cat([sc, ss], 1)
        esc = ar.decidir(tudo, m) if hasattr(ar, 'decidir') else tudo.argmax(1); esc = esc.long().clamp(0, G + S - 1); vivo = m.vida > 0; livre = vivo & (m.pd_ < 0) & (m.tpar <= 0)
        raio_livre += float((livre & (m._dist.min(1).values <= cfg.raio)).float().sum()); livre_t += float(livre.float().sum())
        m.passo(esc); ar.atualizar(m)
        ab = (m.n_posto > n0[0]) & vivo; co = (m.n_come > n0[1]) & vivo; pa = (m.av_fuel > n0[2]); en = (m.ent > n0[3]); of = (m.n_oficina > n0[5]) & vivo
        ev['fuel_abast'] += fuel0[ab].tolist(); ev['dinh_abast'] += dinh0[ab].tolist(); ev['litros_abast'] += (m.litros - lit0)[ab].tolist(); ev['dposto_abast'] += dposto0[ab].tolist(); ev['hora_abast'] += [h]*int(ab.sum())
        ev['fome_come'] += fome0[co].tolist(); ev['hora_come'] += [h]*int(co.sum()); ev['fuel_pane'] += fuel0[pa].tolist(); ev['dposto_pane'] += dposto0[pa].tolist(); ev['vida_oficina'] += vida0[of].tolist()
        ev['dt_corrida'] += (t - ult_ent[en]).tolist(); ult_ent[en] = t; ev['agua_bebe'] += agua0[(m.agua > agua0 + 5) & vivo].tolist()
        hist_h[h, 0] += float(((esc < G - 1) & vivo).float().sum()); hist_h[h, 1] += float(ab.float().sum()); hist_h[h, 2] += float(co.float().sum()); hist_h[h, 3] += float(en.float().sum())
    mortos = float((m.vida <= 0).float().mean()); vv = float(m.t_vida.mean())/240.
    L = [f'## {nome}: mortos {mortos:.2f}, vida media {vv:.1f} dias, {float(m.ent.mean()):.1f} corridas, {float(m.n_come.mean()):.1f} refeicoes, {float(m.n_posto.mean()):.1f} abastecidas, {float(m.av_fuel.mean()):.1f} panes, {float(m.n_oficina.mean()):.1f} oficinas (B={a.B}, 3 mapas de teste)',
         f'- ABASTECE quando o tanque esta em: {q(ev["fuel_abast"])} L (de 100); com dinheiro {q(ev["dinh_abast"])}; compra {q(ev["litros_abast"])} L; a {q(ev["dposto_abast"])} u do posto no tick anterior',
         f'- COME quando a fome esta em: {q(ev["fome_come"])} (de 100; morre a 90+)', f'- BEBE quando a agua esta em: {q(ev["agua_bebe"])} (de 100; morre abaixo de 10)',
         f'- PANE acontece com tanque {q(ev["fuel_pane"])} L e a {q(ev["dposto_pane"])} u do posto mais perto', f'- OFICINA com vida {q(ev["vida_oficina"])}',
         f'- Intervalo entre corridas entregues: {q(ev["dt_corrida"])} ticks (1 tick = 6 min)', f'- Tempo LIVRE (sem passageiro, nao preso) dentro do raio de algum servico: {100*raio_livre/max(livre_t,1):.1f} %',
         '- Por hora do dia (0-23): movimentos | abastecidas | refeicoes | corridas: ' + ' '.join(f'{h}:{int(hist_h[h,0])}/{int(hist_h[h,1])}/{int(hist_h[h,2])}/{int(hist_h[h,3])}' for h in range(24))]
    return '\n'.join(L)
J = json.load(open(a.campeao))['bracos']['linear']['W']; Wc = torch.tensor(alinha_semente(J['0']), device=DEV)
md = ['# Dados tick a tick (gerados por dados_campeao.py) — o que o campeao evoluido FAZ, medido, nao imaginado', '', coleta(Linear, Wc, 'CAMPEAO evoluido (linear q8, semente 0)')]
if a.politica:
    POL, erro = carrega(a.politica); md.append('')
    md.append(coleta(POL, torch.zeros(Linear.NP, device=DEV), f'POLITICA {os.path.basename(a.politica)}') if not erro else f'## politica: ERRO {erro}')
open(a.md, 'w').write('\n'.join(md) + '\n'); print('\n'.join(md), flush=True)
