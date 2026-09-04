"""RETRATO do ser (E40): avaliacao expansiva de um campeao — pesos, ativacao, trajetorias, juizo, diversidade.
Nao muda a evolucao: so olha. Gera JSON + painel HTML por campeao.
Uso: [POSTOS_EXTRA=2] NM_COMPILE=0 python src/retrato.py <json> "<braco>" <Arq> <tag> [--out DIR]
"""
import sys, os, json, math, argparse
import torch
from lab import Reativo, Lote, um_passo, gerar_cidade, DEV, NF, GMAX
from rodar import NOMES_F
from e19_pacote import cfg_pacote
from reacoes import ReativoReacoes, ReativoReacoesTopUp, ReativoReacoesRecusa
ARQS = {'Reativo': Reativo, 'ReativoReacoes': ReativoReacoes, 'ReativoReacoesTopUp': ReativoReacoesTopUp, 'ReativoReacoesRecusa': ReativoReacoesRecusa}
NOMES_S = ['posto', 'comida', 'descanso', 'oficina', 'loja']

def cidades_teste(seed0=1000):
    if os.environ.get('POSTOS_EXTRA'):
        from e34_posto_denso import com_postos_extra
        return [com_postos_extra(seed0 + s, int(os.environ['POSTOS_EXTRA'])) for s in range(3)]
    return [gerar_cidade(seed0 + s) for s in range(3)]

def q(x, ps=(.1, .25, .5, .75, .9)):
    x = x.float().flatten(); return [float(x.quantile(p)) for p in ps] if x.numel() else [float('nan')]*len(ps)

def rastro(A, W, teste, c, T=1200, R=64, seed=1000):
    """roda 1 genoma em NC*R vidas e grava o rastro passo a passo (na GPU; um .cpu() so no fim)."""
    m = Lote(teste, 1, c, seed=seed, R=R); Wb = W[None, :][m.gidx]; a = A(); a.reset(m, Wb)
    B, G = m.B, GMAX
    tr = {k: torch.zeros(T, B, device=DEV) for k in ('fuel', 'fome', 'vida', 'dinh', 'pax', 'acao', 'reflexo', 'come_vence', 'faminto_comida', 'noite')}
    for t in range(T):
        F, val = m.obs(); viz = m.A_().clamp(min=0)
        sc = torch.einsum('bgf,bf->bg', F, Wb[:, :NF]) + a.extra(m, Wb, viz); sc = sc.masked_fill(~val, -1e9)
        svn, sv = m.serv_need(); ss = svn*Wb[:, NF:NF+5] + Wb[:, NF+5:NF+6]
        if hasattr(a, 'extra_serv'): ss = ss + a.extra_serv(m)
        ss = ss.masked_fill(sv <= 0, -1e9); tudo = torch.cat([sc, ss], 1)
        esc = a.decidir(tudo, m) if hasattr(a, 'decidir') else tudo.argmax(1)
        vivo = m.vida > 0; parado = (m.rest <= 0) & (m.tpar <= 0)
        tr['fuel'][t] = m.fuel/m.capf(); tr['fome'][t] = m.fome/100.; tr['vida'][t] = m.vida/100.; tr['dinh'][t] = m.dinh
        tr['pax'][t] = (m.pd_ >= 0).float(); tr['acao'][t] = torch.where(parado & vivo, esc.float(), torch.full_like(esc, -1.).float())
        if hasattr(a, '_ativ'): tr['reflexo'][t] = (a._ativ()[:, 0] > 0).float()
        fam = (m.fome >= 70) & (sv[:, 1] > 0) & parado & vivo
        tr['faminto_comida'][t] = fam.float(); tr['come_vence'][t] = (fam & (esc == G+1)).float()
        nv = m.noite_(); tr['noite'][t] = nv.float() if nv is not None else 0.
        um_passo(m, a, Wb); a.atualizar(m)   # como em rodar()
    fim = dict(ent=m.ent.clone(), vida=m.vida.clone(), dinh=m.dinh.clone(), res=m.res.clone(), panes=m.av_fuel.clone(), oficina=m.n_oficina.clone(), cidx=m.cidx.clone())
    return {k: v.cpu() for k, v in tr.items()}, {k: v.cpu() for k, v in fim.items()}, G

def resumo_semente(tr, fim, G, T):
    vivo = tr['vida'] > 0; B = vivo.shape[1]
    dia = torch.arange(T)//240
    sobrev = [float(vivo[min(T-1, d*240+239)].float().mean()) for d in range(5)]
    morto = fim['vida'] <= 0; t_morte = torch.where(morto, (vivo.float().sum(0)), torch.full((B,), float(T)))
    par = tr['acao']; mov = ((par >= 0) & (par < G)).float().sum(0); serv = [((par == G+k).float().sum(0)) for k in range(5)]
    passos_vivos = vivo.float().sum(0).clamp(min=1)
    pax = tr['pax']; embarques = ((pax[1:] > pax[:-1]).float().sum(0))
    viagem = pax.sum(0)/embarques.clamp(min=1)
    quase = ((tr['vida'] < .2).any(0) & (fim['vida'] > 40)).float().mean()
    fam = tr['faminto_comida'].sum(0); come = tr['come_vence'].sum(0)
    grade = list(range(0, T, 25))
    traj = {k: [q(tr[k][t][vivo[t]]) if vivo[t].any() else [float('nan')]*5 for t in grade] for k in ('fuel', 'fome', 'vida', 'dinh')}
    return dict(
        mortos=float(morto.float().mean()), sobrevivencia_por_dia=sobrev, dia_morte=q(t_morte[morto]/240) if morto.any() else None,
        entregas=float(fim['ent'].mean()), entregas_por_dia_vivo=float((fim['ent']/(passos_vivos/240)).mean()),
        dinheiro_fim=q(fim['dinh']), reserva_fim=q(fim['res']), panes=float(fim['panes'].mean()), oficina=float(fim['oficina'].mean()),
        orcamento_tempo=dict(andando=float((mov/passos_vivos).mean()), **{NOMES_S[k]: float((serv[k]/passos_vivos).mean()) for k in range(5)},
                             parado_esperando=float((1 - (mov + sum(serv))/passos_vivos).mean())),
        reflexo_ativo_frac=float((tr['reflexo']*vivo).sum(0).div(passos_vivos).mean()), reflexo_disparos=float(((tr['reflexo'][1:] > tr['reflexo'][:-1]).float().sum(0)).mean()),
        come_vence_quando_faminto=float(come.sum()/fam.sum().clamp(min=1)), oportunidades_comer=float(fam.mean()),
        embarques=float(embarques.mean()), passos_por_viagem=float(viagem.mean()), frac_tempo_com_passageiro=float((pax*vivo).sum(0).div(passos_vivos).mean()),
        quase_mortes=float(quase), andando_noite=float(((tr['noite'] > 0) & (par >= 0) & (par < G)).float().sum(0).div(passos_vivos).mean()),
        mortos_por_cidade=[float(morto[fim['cidx'] == ci].float().mean()) for ci in range(3)], traj=traj, grade=grade)

def genes(Ws, nomes):
    Wt = torch.tensor(Ws); m = Wt.mean(0); sd = Wt.std(0) if Wt.shape[0] > 1 else torch.zeros_like(m)
    sinal = (torch.sign(Wt) == torch.sign(m)[None, :]).float().mean(0)
    absw = Wt.abs(); esparso = float((absw < .1).float().mean())
    p = absw.mean(0); p = p/p.sum(); H = float(-(p*(p + 1e-12).log()).sum()); Hmax = math.log(len(p))
    ranks = Wt.abs().argsort(1).argsort(1).float()
    S = Wt.shape[0]; dist = [[float(1 - torch.corrcoef(torch.stack([ranks[i], ranks[j]]))[0, 1]) for j in range(S)] for i in range(S)]
    return dict(nomes=nomes, media=m.tolist(), sd=sd.tolist(), consistencia_sinal=sinal.tolist(), esparsidade=esparso, entropia_norm=H/Hmax,
                dist_fingerprint=dist, top=[nomes[i] for i in absw.mean(0).argsort(descending=True)[:8].tolist()])

def nomes_genes(A):
    base = list(NOMES_F)                         # 44 nomes do Reativo (features + servicos + vies + mem + corpo)
    extra = {'ReativoReacoes': ['tau_sede', 'tau_fome', 'w_sede', 'w_fome', 'v_sede', 'v_fome', 'portao'],
             'ReativoReacoesTopUp': ['tau_sede', 'tau_fome', 'w_sede', 'w_fome', 'v_sede', 'v_fome', 'portao', 'portao_abastecer'],
             'ReativoReacoesRecusa': ['tau_sede', 'tau_fome', 'w_sede', 'w_fome', 'v_sede', 'v_fome', 'portao', 'recusa_fome']}.get(A.__name__, [])
    n = (base + extra)[:A.NP]
    return n + [f'g{i}' for i in range(len(n), A.NP)]

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('json'); ap.add_argument('braco'); ap.add_argument('arq'); ap.add_argument('tag')
    ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/retratos'); ap.add_argument('--T', type=int, default=1200); ap.add_argument('--R', type=int, default=64)
    a = ap.parse_args(); A = ARQS[a.arq]; os.makedirs(a.out, exist_ok=True)
    J = json.load(open(a.json))['bracos'][a.braco]; c = cfg_pacote(fome=.15, refeicao=90., comida_no_posto=True); teste = cidades_teste()
    R = dict(tag=a.tag, arq=a.arq, braco=a.braco, fit_runner=J['fit'], mortos_runner=J['mortos'], sementes={})
    Ws = []
    for sd, W in J['W'].items():
        Wt = torch.tensor(W, device=DEV); Ws.append(W)
        tr, fim, G = rastro(A, Wt, teste, c, T=a.T, R=a.R); R['sementes'][sd] = resumo_semente(tr, fim, G, a.T)
        s = R['sementes'][sd]; print(f"  s{sd}: mortos {s['mortos']:.2f} entregas {s['entregas']:.1f} reflexo ativo {s['reflexo_ativo_frac']:.1%} ({s['reflexo_disparos']:.1f} disparos/vida) come-vence {s['come_vence_quando_faminto']:.0%} tempo c/ pax {s['frac_tempo_com_passageiro']:.0%} quase-mortes {s['quase_mortes']:.0%}", flush=True)
    R['genes'] = genes(Ws, nomes_genes(A))
    path = os.path.join(a.out, f'retrato_{a.tag}.json'); json.dump(R, open(path, 'w'), indent=1); print('gravado', path)

if __name__ == '__main__': main()
