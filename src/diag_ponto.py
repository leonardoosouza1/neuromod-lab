"""[E68 diag] ONDE VAI O TEMPO do campeao no mundo com ponto de taxi: fracao dos ticks vivos andando / ESPERANDO livre (parado, sem
passageiro, sem estar preso) / preso (pane, exausto, servico) / com passageiro; onde espera (demanda alta >= 1.5 vs baixa <= .5);
embarques que VIERAM pelo ponto vs achados rodando; ticks de espera por embarque. Roda em mundos de TESTE (mesmos do e43)."""
import sys, os, json, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import *; from e43_campo import BRACOS, alinha_semente
ap = argparse.ArgumentParser(); ap.add_argument('--campeao', required=True); ap.add_argument('--bracos', nargs='+', default=['linear']); ap.add_argument('--ponto', type=float, default=30.)
ap.add_argument('--seeds', type=int, nargs='*', default=[0, 1, 2, 3, 4]); ap.add_argument('--copias', type=int, default=128); ap.add_argument('--teste-seed', type=int, default=1000)
ap.add_argument('--L', type=float, default=200.); ap.add_argument('--dias', type=float, default=10.); ap.add_argument('--fitness', default='riqueza'); ap.add_argument('--mundo', default='distinto')
ap.add_argument('--kcal-pane', type=float, default=8.); ap.add_argument('--dinh0', type=float, default=10.); ap.add_argument('--guincho', type=float, default=0.); ap.add_argument('--fuel-pane', type=float, default=15.)
ap.add_argument('--pax-cidade', action='store_true'); ap.add_argument('--npx', type=int, default=12); ap.add_argument('--respawn', type=float, default=20.); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e68'); ap.add_argument('--tag', default='')
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
cfg = CfgCampo(L=a.L, fitness=a.fitness); cfg.KCAL_PANE = a.kcal_pane; cfg.dinh0 = a.dinh0; cfg.GUINCHO = a.guincho; cfg.FUEL_POS_PANE = a.fuel_pane; cfg.ponto = a.ponto; cfg.NPX = a.npx; cfg.respawn = a.respawn; cfg.pax_cidade = a.pax_cidade
teste = [gerar_mapa(a.teste_seed + s, L=a.L, distinto=a.mundo == 'distinto') for s in range(3)]; T = int(240*a.dias)
J = json.load(open(a.campeao))['bracos']; ARQ = dict(BRACOS); res = {}
print(f'== diag_ponto | campeao {os.path.basename(a.campeao)} | mundo ponto={a.ponto} | {len(a.seeds)} sementes x {a.copias} copias x 3 mapas | T={T} ==', flush=True)
for nome in a.bracos:
    A = ARQ[nome]; acc = {k: 0. for k in ('vivo', 'mov', 'esp', 'esp_alta', 'esp_baixa', 'preso', 'pax', 'emb')}; mortos = []; ents = []; recs = []; vems = []
    for sd in a.seeds:
        w = J[nome]['W'][str(sd)]; W = torch.tensor(alinha_semente(w) if len(w) < A.NP else w, device=DEV)
        assert W.numel() == A.NP, f'{nome}: {W.numel()} genes != NP {A.NP}'
        m = Campo(teste, a.copias, cfg, seed=7777, R=1); Wb = W[None, :].repeat(a.copias, 1)[m.gidx]; ar = A(); ar.reset(m, Wb)
        for t in range(T):
            p0 = m.pos.clone(); pd0 = m.pd_.clone(); um_passo(m, ar, Wb); ar.atualizar(m)
            vivo = m.vida > 0; moved = (m.pos - p0).norm(dim=-1) > 1e-6; preso = m.tpar > 0; pax = m.pd_ >= 0
            esp = vivo & ~moved & ~preso & ~pax; dem = m.demanda[m.cidx, m.distrito(m.pos)]
            acc['vivo'] += float(vivo.float().sum()); acc['mov'] += float((moved & vivo).float().sum()); acc['esp'] += float(esp.float().sum())
            acc['esp_alta'] += float((esp & (dem >= 1.5)).float().sum()); acc['esp_baixa'] += float((esp & (dem <= .5)).float().sum())
            acc['preso'] += float((preso & vivo).float().sum()); acc['pax'] += float((pax & vivo).float().sum()); acc['emb'] += float((pax & (pd0 < 0)).float().sum())
        mortos.append(float((m.vida <= 0).float().mean())); ents.append(float(m.ent.mean())); recs.append(float(m.rec.mean())); vems.append(float(m.n_vem.mean()))
    B = a.copias*3; v = acc['vivo']; nB = len(a.seeds)*B
    r = dict(mortos=sum(mortos)/len(mortos), ent=sum(ents)/len(ents), rec=sum(recs)/len(recs), anda=acc['mov']/v, espera=acc['esp']/v, espera_alta=acc['esp_alta']/v, espera_baixa=acc['esp_baixa']/v,
             preso=acc['preso']/v, com_pax=acc['pax']/v, embarques_por_ser=acc['emb']/nB, via_ponto_por_ser=sum(vems)/len(vems), ticks_vivos_por_ser=v/nB)
    r['fracao_via_ponto'] = r['via_ponto_por_ser']/max(r['embarques_por_ser'], 1e-9); r['ticks_espera_por_embarque_ponto'] = (acc['esp']/nB)/max(r['via_ponto_por_ser'], 1e-9)
    res[nome] = r
    print(f"  {nome[:40]:<40} mortos {r['mortos']:.2f} ent {r['ent']:4.1f} renda {r['rec']:5.0f} | do tempo vivo: anda {r['anda']:.2f}  ESPERA livre {r['espera']:.2f} (demanda alta {r['espera_alta']:.2f} / baixa {r['espera_baixa']:.2f})  preso {r['preso']:.2f}  com passageiro {r['com_pax']:.2f} | embarques/ser {r['embarques_por_ser']:4.1f}, vieram pelo ponto {r['via_ponto_por_ser']:4.1f} ({100*r['fracao_via_ponto']:.0f} %), ticks de espera por embarque no ponto {r['ticks_espera_por_embarque_ponto']:5.0f}", flush=True)
json.dump(dict(campeao=a.campeao, ponto=a.ponto, res=res), open(os.path.join(a.out, f'diag_ponto{a.tag}.json'), 'w'), indent=1); print('ok', flush=True)
