"""E51c DIAGNOSTICO: onde vai o TEMPO do oraculo (morre 1.00 com 10 entregas) versus o campeao evoluido minimo-3 (0.58, 27 entregas).
Orcamento de ticks por estado (trabalhando / trancado em posto-comida-agua-oficina / parado por pane-exaustao / noite / com passageiro),
serie diaria (entregas, dinheiro, gasolina, fome, vivos) e causa dominante na hora da morte. Tudo tensor, 10 syncs (1 por dia)."""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(__file__))
import torch
from campo import *
from oraculo_campo import fabrica_oraculo, VARIANTES
from e43_campo import BRACOS

def tracar(Arq, W, mapas, cfg, T, copias=128, seed=7777):
    m = Campo(mapas, copias, cfg, seed=seed, R=1); Wb = W[None, :].repeat(copias, 1)[m.gidx]; a = Arq(); a.reset(m, Wb); fn = _passo_fn()
    B = m.B; z = lambda: torch.zeros(B, device=DEV)
    c = dict(mov=z(), parado=z(), noite=z(), pax=z(), alvo=torch.zeros(B, 5, device=DEV), vivo=z())
    morte = torch.zeros(B, 4, device=DEV)   # fome, sede, divida, outro
    dias = []
    for t in range(T):
        p0 = m.pos.clone(); v0 = m.vida > 0
        try: fn(m, a, Wb)
        except Exception:
            if t == 0: fn = um_passo; fn(m, a, Wb)
            else: raise
        a.atualizar(m)
        vivo = (m.vida > 0).float(); c['vivo'] += vivo
        c['mov'] += ((m.pos - p0).norm(dim=-1) > 1e-6).float()*vivo; c['parado'] += (m.tpar > 0).float()*vivo
        c['noite'] += m.noite_().float()*vivo; c['pax'] += (m.pd_ >= 0).float()*vivo
        if hasattr(a, 'alvo'): c['alvo'] += torch.nn.functional.one_hot(a.alvo + 1, 5).float()*vivo[:, None]
        morreu = v0 & (m.vida <= 0)
        causa = torch.stack([m.fome >= 90., m.agua <= 10., m.dinh < 0., torch.ones_like(m.fome, dtype=torch.bool)], 1).float()
        morte += morreu[:, None].float()*causa
        if (t + 1) % 240 == 0:
            dias.append(dict(dia=(t + 1)//240, vivos=float(vivo.mean()), ent=float(m.ent.mean()), dinh=float(m.dinh.mean()), fuel=float(m.fuel.mean()),
                             fome=float(m.fome.mean()), agua=float(m.agua.mean()), abast=float(m.n_posto.mean()), come=float(m.n_come.mean()), panes=float(m.av_fuel.mean())))
    tv = c['vivo'].clamp(min=1.)
    orc = {k: float((c[k]/tv).mean()) for k in ('mov', 'parado', 'noite', 'pax')}
    orc['alvo'] = [round(float(x), 3) for x in (c['alvo']/tv[:, None]).mean(0)]   # [trabalhando, posto, comida, agua, oficina]
    n_m = morte.sum(0)[3].clamp(min=1.)
    return orc, dias, [round(float(x), 2) for x in morte.sum(0)/n_m], float((m.vida <= 0).float().mean()), float(m.ent.mean())

def main(a):
    T = int(240*a.dias); teste = [gerar_mapa(1000 + s, L=a.L) for s in range(3)]
    cfg = CfgCampo(L=a.L, fitness='bemestar', loja_no_posto=not a.sem_loja)
    J = json.load(open(a.campeao))['bracos']; nomeM = 'minimo 3 (d_alvo, d_posto, e_fuel)'
    ArqM = dict(BRACOS)[nomeM]; WM = torch.tensor(J[nomeM]['W'][sorted(J[nomeM]['W'])[0]], device=DEV)
    casos = [('campeao minimo-3', ArqM, WM)] + [(f'oraculo {v}', fabrica_oraculo(nome=v, **VARIANTES[v]), torch.zeros(Linear.NP, device=DEV)) for v in a.variantes]
    out = {}
    for nome, Arq, W in casos:
        orc, dias, causa, mortos, ent = tracar(Arq, W, teste, cfg, T, copias=a.copias)
        out[nome] = dict(orcamento=orc, dias=dias, causa_morte=causa, mortos=mortos, ent=ent)
        print(f'== {nome}: mortos {mortos:.2f} ent {ent:.1f} | orcamento de ticks (vivo): anda {orc["mov"]:.2f} parado(pane/exausto) {orc["parado"]:.2f} noite {orc["noite"]:.2f} c/passageiro {orc["pax"]:.2f}'
              f' | alvo [trab, posto, comida, agua, oficina] {orc["alvo"]} | morte [fome, sede, divida, total] {causa}', flush=True)
        for d in dias: print(f"   dia {d['dia']:2d} vivos {d['vivos']:.2f} ent {d['ent']:5.1f} dinh {d['dinh']:6.1f} fuel {d['fuel']:5.1f} fome {d['fome']:5.1f} agua {d['agua']:5.1f} abast {d['abast']:4.1f} come {d['come']:4.1f} panes {d['panes']:4.1f}", flush=True)
    os.makedirs(a.out, exist_ok=True); json.dump(out, open(os.path.join(a.out, f'e51c_diag{a.tag}.json'), 'w'), indent=1)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--L', type=float, default=200.); ap.add_argument('--dias', type=float, default=10.); ap.add_argument('--copias', type=int, default=128)
    ap.add_argument('--sem-loja', action='store_true'); ap.add_argument('--variantes', nargs='*', default=['base', 'tarde_rico'])
    ap.add_argument('--campeao', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e43/e43_triagem_L200_10d.json')
    ap.add_argument('--tag', default=''); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e51')
    main(ap.parse_args())
