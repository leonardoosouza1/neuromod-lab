"""RETRATO no CAMPO (E43): rastro passo a passo de um campeao (JSON do e43) -> JSON + painel HTML.
Mapa de calor das posicoes, trajetorias do corpo, litros escolhidos, reserva, orcamento de acoes, causa da morte, genes.
Uso: TORCHINDUCTOR_COMPILE_THREADS=1 NM_COMPILE=0 python src/retrato_campo.py <e43.json> "<braco>" <tag> [--out DIR]"""
import sys, os, json, math, html, argparse
import torch
from campo import *

def q(x, ps=(.1, .25, .5, .75, .9)):
    x = x.float().flatten(); return [float(x.quantile(p)) for p in ps] if x.numel() else [float('nan')]*len(ps)

def rastro(A, W, mapas, cfg, T=1200, R=64, seed=1000):
    m = Campo(mapas, 1, cfg, seed=seed, R=R); Wb = W[None, :][m.gidx]; a = A(); a.reset(m, Wb); B = m.B
    tr = {k: torch.zeros(T, B, device=DEV) for k in ('fuel', 'agua', 'fome', 'vida', 'dinh', 'res', 'pax', 'acao', 'reflexo', 'calor')}
    heat = torch.zeros(m.NC, 32, 32, device=DEV)
    for t in range(T):
        F, val = m.obs(); sc = torch.einsum('bgf,bf->bg', F, Wb[:, :NF]) + a.extra(m, Wb, F)
        svn, sv = m.serv_need(); ss = svn*Wb[:, NF:NF+S] + Wb[:, NF+S:NF+S+1]
        if hasattr(a, 'extra_serv'): ss = ss + a.extra_serv(m)
        ss = ss.masked_fill(sv <= 0, -1e9); esc = torch.cat([sc, ss], 1).argmax(1)
        vivo = m.vida > 0
        for k, v in (('fuel', m.fuel), ('agua', m.agua), ('fome', m.fome), ('vida', m.vida), ('dinh', m.dinh), ('res', m.res), ('calor', m.calor)): tr[k][t] = v
        tr['pax'][t] = (m.pd_ >= 0).float(); tr['acao'][t] = torch.where(vivo, esc.float(), torch.full_like(esc, -1.).float())
        if hasattr(a, '_ativ'): tr['reflexo'][t] = (a._ativ() > 0).float()
        ix = (m.pos[:, 0]/m.L*32).long().clamp(0, 31); iy = (m.pos[:, 1]/m.L*32).long().clamp(0, 31)
        heat.index_put_((m.cidx, iy, ix), vivo.float(), accumulate=True)
        um_passo(m, a, Wb); a.atualizar(m)
    fim = dict(ent=m.ent, vida=m.vida, dinh=m.dinh, res=m.res, panes=m.av_fuel, litros=m.litros, n_posto=m.n_posto, n_come=m.n_come, oficina=m.n_oficina, cidx=m.cidx, t_vida=m.t_vida, fome=m.fome, agua=m.agua)
    return {k: v.cpu() for k, v in tr.items()}, {k: v.cpu() for k, v in fim.items()}, heat.cpu(), m

def resumo(tr, fim, heat, T):
    vivo = tr['vida'] > 0; B = vivo.shape[1]; morto = fim['vida'] <= 0
    sob = [float(vivo[min(T-1, d*240+239)].float().mean()) for d in range(5)]
    ac = tr['acao']; passos = vivo.float().sum(0).clamp(min=1)
    orc = {'andando': float((((ac >= 0) & (ac < G-1)).float().sum(0)/passos).mean()), 'parado': float(((ac == G-1).float().sum(0)/passos).mean())}
    for k, (t, qtd) in enumerate(ACOES): orc[f'{t}{int(qtd) if qtd else ""}'] = float(((ac == G+k).float().sum(0)/passos).mean())
    # causa da morte: estado no ultimo passo vivo
    tm = (vivo.float().sum(0).long() - 1).clamp(min=0); ar = torch.arange(B)
    fome_m = tr['fome'][tm, ar]; agua_m = tr['agua'][tm, ar]; fuel_m = tr['fuel'][tm, ar]; dinh_m = tr['dinh'][tm, ar]
    causa = {}
    if morto.any():
        causa = dict(fome90=float((fome_m[morto] >= 90).float().mean()), sede10=float((agua_m[morto] <= 10).float().mean()), tanque=float((fuel_m[morto] <= 1).float().mean()), divida=float((dinh_m[morto] <= -50).float().mean()),
                     dia=q(fim['t_vida'][morto]/240.), dinheiro=q(dinh_m[morto]))
    grade = list(range(0, T, 25))
    traj = {k: [q(tr[k][t][vivo[t]]) if vivo[t].any() else [float('nan')]*5 for t in grade] for k in ('fuel', 'agua', 'fome', 'vida', 'dinh', 'res', 'calor')}
    lit = fim['litros']/fim['n_posto'].clamp(min=1)
    return dict(mortos=float(morto.float().mean()), sobrevivencia_por_dia=sob, entregas=float(fim['ent'].mean()), panes=float(fim['panes'].mean()),
                dinheiro_fim=q(fim['dinh']), reserva_fim=q(fim['res']), litros_por_abast=q(lit[fim['n_posto'] > 0]) if bool((fim['n_posto'] > 0).any()) else None, abastecimentos=float(fim['n_posto'].mean()),
                refeicoes=float(fim['n_come'].mean()), oficina=float(fim['oficina'].mean()), orcamento=orc, reflexo_ativo=float((tr['reflexo']*vivo).sum(0).div(passos).mean()),
                tempo_com_pax=float((tr['pax']*vivo).sum(0).div(passos).mean()), causa_morte=causa, traj=traj, grade=grade,
                mortos_por_mapa=[float(morto[fim['cidx'] == ci].float().mean()) for ci in range(int(fim['cidx'].max()) + 1)], heat=(heat/heat.amax(dim=(1, 2), keepdim=True).clamp(min=1)).tolist())

def genes(Ws):
    Wt = torch.tensor(Ws); m = Wt.mean(0); sd = Wt.std(0) if Wt.shape[0] > 1 else torch.zeros_like(m); cons = (torch.sign(Wt) == torch.sign(m)[None]).float().mean(0)
    n = len(m); nomes = (NOMES_F + ['tau', 'w_sede', 'v_sede', 'portao'])[:n]; nomes += [f'g{i}' for i in range(len(nomes), n)]
    return dict(nomes=nomes, media=m.tolist(), sd=sd.tolist(), consistencia_sinal=cons.tolist(), esparsidade=float((Wt.abs() < .1).float().mean()))

def painel(R, out):
    S_ = R['sementes']; sds = sorted(S_, key=int); COR = ['#0E7C86', '#C8401F', '#B8851F', '#5B6ABF', '#2E7D4F']
    def linhas(k, rot, ymax):
        w, h, P = 640, 200, 34; sd0 = sds[0]; g = S_[sd0]['grade']; X = lambda x: P + x/g[-1]*(w-2*P); Y = lambda y: h-P-(y/ymax)*(h-2*P)
        s = [f'<svg viewBox="0 0 {w} {h}" class="chart"><text x="{P}" y="14" font-size="12" fill="var(--ink2)">{html.escape(rot)}</text>']
        for d in range(1, 5): s.append(f'<line x1="{X(d*240):.0f}" x2="{X(d*240):.0f}" y1="{P}" y2="{h-P}" stroke="var(--line)" stroke-dasharray="3 3"/>')
        for sd in sds:
            pts = ' '.join(f'{X(x):.1f},{Y(min(ymax, max(0, t[2]))):.1f}' for x, t in zip(S_[sd]['grade'], S_[sd]['traj'][k]) if not math.isnan(t[2]))
            s.append(f'<polyline points="{pts}" fill="none" stroke="{COR[int(sd)%5]}" stroke-width="2"/>')
        return ''.join(s) + '</svg>'
    def heat_svg(sd, ci=0):
        H = S_[sd]['heat'][ci]; n = len(H); cs = 8
        cells = ''.join(f'<rect x="{x*cs}" y="{(n-1-y)*cs}" width="{cs}" height="{cs}" fill="rgb({int(255-200*H[y][x])},{int(255-120*H[y][x])},{int(255-40*H[y][x])})"/>' for y in range(n) for x in range(n))
        return f'<svg viewBox="0 0 {n*cs} {n*cs}" class="chart" style="max-width:260px">{cells}</svg>'
    def row(sd):
        s = S_[sd]; o = s['orcamento']; c = s['causa_morte']; lit = s['litros_por_abast']
        return (f"<tr><td>s{sd}</td><td class=n>{s['mortos']:.2f}</td><td class=n>{s['entregas']:.1f}</td><td class=n>{s['panes']:.1f}</td><td class=n>{s['abastecimentos']:.1f}</td>"
                f"<td class=n>{(lit[2] if lit else float('nan')):.0f}</td><td class=n>{s['reserva_fim'][2]:.0f}</td><td class=n>{s['dinheiro_fim'][2]:.0f}</td><td class=n>{s['refeicoes']:.1f}</td>"
                f"<td class=n>{o['andando']:.0%} / {o['parado']:.0%}</td><td class=n>{s['tempo_com_pax']:.0%}</td><td class=n>{s['reflexo_ativo']:.0%}</td>"
                f"<td class=n>{(c.get('fome90', 0)):.0%} / {(c.get('sede10', 0)):.0%} / {(c.get('tanque', 0)):.0%} / {(c.get('divida', 0)):.0%}</td></tr>")
    tab = '<table><tr><th>semente</th><th>mortos</th><th>entregas</th><th>panes</th><th>abastecimentos</th><th>litros por parada (mediana)</th><th>reserva fim</th><th>dinheiro fim</th><th>refeições</th><th>andando / parado</th><th>tempo c/ passageiro</th><th>reflexo ativo</th><th>morte: fome / sede / tanque / dívida</th></tr>' + ''.join(row(sd) for sd in sds) + '</table>'
    Gn = R['genes']; med = Gn['media']; cons = Gn['consistencia_sinal']; nomes = Gn['nomes']; ordem = sorted(range(len(med)), key=lambda i: -abs(med[i]))[:18]
    gen = '<table><tr><th>gene</th><th>média</th><th>mesmo sinal nas sementes</th></tr>' + ''.join(f'<tr><td>{html.escape(nomes[i])}</td><td class=n>{med[i]:+.2f}</td><td class=n>{cons[i]:.0%}</td></tr>' for i in ordem) + '</table>'
    heats = ''.join(f'<div><div class="eyebrow">s{sd} · mapa de teste 0 · onde viveu</div>{heat_svg(sd)}</div>' for sd in sds)
    page = f"""<title>Retrato no campo · {html.escape(R['tag'])}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>:root{{--bg:#EDF0F3;--panel:#FFFFFF;--ink:#1A2129;--ink2:#4A5560;--line:#D3D9DF;--mono:'IBM Plex Mono',ui-monospace,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#12161B;--panel:#1B2129;--ink:#E8ECF0;--ink2:#A7B1BB;--line:#2E3740}}}} :root[data-theme="dark"]{{--bg:#12161B;--panel:#1B2129;--ink:#E8ECF0;--ink2:#A7B1BB;--line:#2E3740}}
body{{background:var(--bg);color:var(--ink);font:15px/1.5 'IBM Plex Sans',system-ui,sans-serif;margin:0}} main{{max-width:1100px;margin:0 auto;padding:28px 20px 60px}}
h1,h2{{font-family:'Barlow Condensed','Arial Narrow',sans-serif;margin:0;text-wrap:balance}} h1{{font-size:46px;line-height:1}} h2{{font-size:24px;margin-top:30px;padding-top:12px;border-top:2px solid var(--ink)}}
p{{max-width:72ch}} .card{{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:14px 16px;margin-top:12px}} .chart{{width:100%;height:auto;display:block}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}} table{{border-collapse:collapse;width:100%;font-size:13px}} th,td{{padding:6px 7px;border-bottom:1px solid var(--line);text-align:left}} th{{font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink2);font-weight:500}} td.n{{font-family:var(--mono);text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}} .wrap{{overflow-x:auto}} .eyebrow{{font-family:var(--mono);font-size:11px;color:var(--ink2);text-transform:uppercase;letter-spacing:.1em}}</style>
<main><div class="eyebrow">neuromod-lab · campo contínuo · L={R['L']} · régua {html.escape(R['fitness'])} · {html.escape(R['braco'])}</div><h1>Retrato no campo · {html.escape(R['tag'])}</h1>
<p>Cinco linhagens, 192 vidas cada num mapa nunca visto. Onde o ser viveu, como o corpo caminhou (gasolina, água, fome, vida, dinheiro, reserva), quantos litros escolhe por parada, e do que morre.</p>
<h2>Onde viveu</h2><div class="card grid">{heats}</div>
<h2>O corpo ao longo dos cinco dias (mediana por semente)</h2><div class="grid">{''.join(f'<div class="card">{linhas(k, r, ym)}</div>' for k, r, ym in (('fuel','gasolina',100),('agua','água',100),('fome','fome',100),('vida','vida',100),('dinh','dinheiro',200),('res','reserva (gordura)',120)))}</div>
<h2>Juízo</h2><div class="card wrap">{tab}</div>
<h2>Genes mais fortes (média das sementes)</h2><div class="card wrap">{gen}</div></main>"""
    open(out, 'w').write(page)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('json'); ap.add_argument('braco'); ap.add_argument('tag'); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/retratos'); ap.add_argument('--T', type=int, default=1200)
    a = ap.parse_args(); J = json.load(open(a.json)); b = J['bracos'][a.braco]; L = float(J['L']); cfg = CfgCampo(L=L, fitness=J.get('fitness', 'sobrevive'), pena_morte=J.get('pena', 5.))
    A = {'linear': Linear, 'reflexo': Reflexo, 'produto': Produto, 'modos': Modos}.get(a.braco.split(' ')[0], None) or fabrica_minimo(['d_alvo', 'd_posto', 'e_fuel'])
    mapas = [gerar_mapa(1000 + s, L=L) for s in range(3)]; R = dict(tag=a.tag, braco=a.braco, L=L, fitness=cfg.fitness, sementes={})
    for sd, W in b['W'].items():
        tr, fim, heat, m = rastro(A, torch.tensor(W, device=DEV), mapas, cfg, T=a.T); R['sementes'][sd] = resumo(tr, fim, heat, a.T)
        s = R['sementes'][sd]; print(f"  s{sd}: mortos {s['mortos']:.2f} ent {s['entregas']:.1f} abast {s['abastecimentos']:.1f} litros {s['litros_por_abast'] and round(s['litros_por_abast'][2])} res {s['reserva_fim'][2]:.0f} parado {s['orcamento']['parado']:.0%}", flush=True)
    R['genes'] = genes(list(b['W'].values())); os.makedirs(a.out, exist_ok=True)
    jp = os.path.join(a.out, f'retrato_campo_{a.tag}.json'); json.dump(R, open(jp, 'w')); hp = jp[:-5] + '.html'; painel(R, hp); print('gravado', jp, hp)

if __name__ == '__main__': main()
