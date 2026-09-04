"""Painel HTML do retrato (E40): le retrato_<tag>.json e escreve retrato_<tag>.html (SVG inline, sem libs)."""
import sys, json, math, html
R = json.load(open(sys.argv[1])); out = sys.argv[2]
S = R['sementes']; sds = sorted(S, key=int); G = R['genes']
COR = ['#0E7C86', '#C8401F', '#B8851F', '#5B6ABF', '#2E7D4F']
def svg_linhas(series, w=640, h=200, ymin=0, ymax=1, faixa=None, rotulo=''):
    """series: lista de (nome, xs, ys, cor); faixa: (xs, lo, hi, cor) opcional."""
    P = 34; X = lambda x: P + (x/max(1, series[0][1][-1]))*(w-2*P); Y = lambda y: h-P - ((y-ymin)/(ymax-ymin))*(h-2*P)
    s = [f'<svg viewBox="0 0 {w} {h}" class="chart">']
    for k in range(5):
        y = ymin + (ymax-ymin)*k/4; s.append(f'<line x1="{P}" x2="{w-P}" y1="{Y(y):.1f}" y2="{Y(y):.1f}" stroke="var(--line)"/><text x="{P-4}" y="{Y(y)+4:.1f}" text-anchor="end" font-size="10" fill="var(--ink2)">{y:.2g}</text>')
    for d in range(1, 5): s.append(f'<line x1="{X(d*240):.1f}" x2="{X(d*240):.1f}" y1="{P}" y2="{h-P}" stroke="var(--line)" stroke-dasharray="3 3"/>')
    if faixa:
        xs, lo, hi, cor = faixa; pts = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in zip(xs, lo)) + ' ' + ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in zip(reversed(xs), reversed(hi)))
        s.append(f'<polygon points="{pts}" fill="{cor}" opacity=".15"/>')
    for nome, xs, ys, cor in series:
        pts = ' '.join(f'{X(x):.1f},{Y(y):.1f}' for x, y in zip(xs, ys) if not (isinstance(y, float) and math.isnan(y)))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{cor}" stroke-width="2"/>')
    s.append(f'<text x="{P}" y="14" font-size="12" fill="var(--ink2)">{html.escape(rotulo)}</text></svg>'); return ''.join(s)
def barras(nomes, vals, cores, w=900, h=None, rot=''):
    n = len(nomes); h = h or 16*n + 30; vmax = max(abs(v) for v in vals) or 1; X0 = 200
    s = [f'<svg viewBox="0 0 {w} {h}" class="chart"><line x1="{X0+(w-X0-20)/2:.0f}" x2="{X0+(w-X0-20)/2:.0f}" y1="10" y2="{h-10}" stroke="var(--ink2)"/>']
    for i, (nm, v, c) in enumerate(zip(nomes, vals, cores)):
        y = 20 + 16*i; mid = X0 + (w-X0-20)/2; L = (v/vmax)*(w-X0-20)/2
        s.append(f'<text x="{X0-6}" y="{y+4}" text-anchor="end" font-size="11" fill="var(--ink)">{html.escape(nm)}</text><rect x="{min(mid, mid+L):.1f}" y="{y-6}" width="{abs(L):.1f}" height="12" fill="{c}"/><text x="{mid+L+(4 if L>=0 else -4):.1f}" y="{y+4}" font-size="10" text-anchor="{"start" if L>=0 else "end"}" fill="var(--ink2)">{v:+.2f}</text>')
    s.append('</svg>'); return ''.join(s)
# --- genes
med = G['media']; cons = G['consistencia_sinal']; nomes = (G['nomes'] + [f'g{i}' for i in range(len(G['nomes']), len(med))])[:len(med)]
ordem = sorted(range(len(nomes)), key=lambda i: -abs(med[i]))
cores = ['var(--gas)' if cons[i] >= .99 else ('var(--peso)' if cons[i] >= .8 else 'var(--morte)') for i in ordem]
genes_svg = barras([nomes[i] for i in ordem], [med[i] for i in ordem], cores)
# --- sobrevivencia / trajetorias
dias = [0, 1, 2, 3, 4]
sob = svg_linhas([(f's{sd}', [0]+[d*240+239 for d in dias], [1.0]+S[sd]['sobrevivencia_por_dia'], COR[int(sd) % 5]) for sd in sds], ymin=0.5, ymax=1, rotulo='vivos ao fim de cada dia (5 sementes)')
def traj(k, rot, ymax=1):
    sd0 = sds[0]; g = S[sd0]['grade']; series = []; 
    for sd in sds: series.append((f's{sd}', S[sd]['grade'], [t[2] for t in S[sd]['traj'][k]], COR[int(sd) % 5]))
    fx = (g, [t[1] for t in S[sd0]['traj'][k]], [t[3] for t in S[sd0]['traj'][k]], COR[0])
    return svg_linhas(series, faixa=fx, ymin=0, ymax=ymax, rotulo=rot)
trajs = ''.join(f'<div class="card">{traj(k, r, ym)}</div>' for k, r, ym in (('fuel', 'tanque (fração) · mediana por semente · faixa 25–75 % da s0', 1), ('fome', 'fome (fração)', 1), ('vida', 'vida (fração)', 1), ('dinh', 'dinheiro', 160)))
# --- tabela de juizo
def row(sd):
    s = S[sd]; ot = s['orcamento_tempo']
    return f"<tr><td>s{sd}</td><td class=n>{s['mortos']:.2f}</td><td class=n>{s['entregas']:.1f}</td><td class=n>{s['panes']:.1f}</td><td class=n>{s['reflexo_disparos']:.1f} · {s['reflexo_ativo_frac']:.0%}</td><td class=n>{s['come_vence_quando_faminto']:.0%}</td><td class=n>{s['frac_tempo_com_passageiro']:.0%}</td><td class=n>{s['passos_por_viagem']:.0f}</td><td class=n>{ot['andando']:.0%} / {ot['posto']+ot['comida']+ot['descanso']+ot['oficina']+ot['loja']:.1%} / {ot['parado_esperando']:.0%}</td><td class=n>{s['quase_mortes']:.0%}</td><td class=n>{s['dinheiro_fim'][2]:.0f}</td><td class=n>{' '.join(f'{m:.2f}' for m in s['mortos_por_cidade'])}</td></tr>"
tab = '<table><tr><th>semente</th><th>mortos</th><th>entregas</th><th>panes</th><th>reflexo: disparos/vida · tempo ativo</th><th>comer vence (faminto sobre comida)</th><th>tempo c/ passageiro</th><th>passos por viagem</th><th>andando / servindo / esperando</th><th>quase-mortes</th><th>dinheiro fim (mediana)</th><th>mortos por cidade</th></tr>' + ''.join(row(sd) for sd in sds) + '</table>'
# --- fingerprint
D = G['dist_fingerprint']; fp = '<table><tr><th></th>' + ''.join(f'<th>s{sd}</th>' for sd in sds) + '</tr>' + ''.join(f'<tr><td>s{sds[i]}</td>' + ''.join(f'<td class=n>{D[i][j]:.2f}</td>' for j in range(len(sds))) + '</tr>' for i in range(len(sds))) + '</table>'
page = f"""<title>Retrato · {html.escape(R['tag'])}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#EDF0F3;--panel:#FFFFFF;--ink:#1A2129;--ink2:#4A5560;--line:#D3D9DF;--gas:#0E7C86;--morte:#C8401F;--peso:#B8851F;--mono:'IBM Plex Mono',ui-monospace,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#12161B;--panel:#1B2129;--ink:#E8ECF0;--ink2:#A7B1BB;--line:#2E3740;--gas:#3FB2BC;--morte:#E8674A;--peso:#D8A33C}}}}
:root[data-theme="dark"]{{--bg:#12161B;--panel:#1B2129;--ink:#E8ECF0;--ink2:#A7B1BB;--line:#2E3740;--gas:#3FB2BC;--morte:#E8674A;--peso:#D8A33C}}
body{{background:var(--bg);color:var(--ink);font:15px/1.5 'IBM Plex Sans',system-ui,sans-serif;margin:0}} main{{max-width:1040px;margin:0 auto;padding:28px 20px 60px}}
h1,h2{{font-family:'Barlow Condensed','Arial Narrow',sans-serif;margin:0;text-wrap:balance}} h1{{font-size:50px;line-height:1}} h2{{font-size:26px;margin-top:36px;padding-top:14px;border-top:2px solid var(--ink)}}
p{{max-width:70ch}} .card{{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:14px 16px;margin-top:12px}} .chart{{width:100%;height:auto;display:block}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:14px}} @media (max-width:760px){{.grid2{{grid-template-columns:1fr}} h1{{font-size:38px}}}}
table{{border-collapse:collapse;width:100%;font-size:13px}} th,td{{padding:6px 7px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}} th{{font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink2);font-weight:500}} td.n{{font-family:var(--mono);text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}} .wrap{{overflow-x:auto}}
.eyebrow{{font-family:var(--mono);font-size:12px;color:var(--ink2);text-transform:uppercase;letter-spacing:.1em}} .leg span{{display:inline-block;margin-right:14px;font-size:12px;color:var(--ink2)}} .sw{{display:inline-block;width:11px;height:11px;border-radius:2px;vertical-align:-1px;margin-right:4px}}
</style>
<main>
<div class="eyebrow">neuromod-lab · retrato do ser · {html.escape(R['arq'])} · {html.escape(R['braco'])} · runner: fit {R['fit_runner']} mortos {R['mortos_runner']}</div>
<h1>Retrato · {html.escape(R['tag'])}</h1>
<p>Cinco linhagens do mesmo experimento, 192 vidas cada, olhadas por dentro: o que os genes dizem, quando o reflexo acorda, como o corpo caminha ao longo dos cinco dias, e o que o ser escolhe quando está faminto com passageiro a bordo. Nada aqui muda a evolução — é só olhar.</p>
<h2>1 · Genes (média das 5 sementes, ordenados por força)</h2>
<p>Barra à direita = puxa a favor; à esquerda = contra. Cor: <span class="sw" style="background:var(--gas)"></span>mesmo sinal nas 5 sementes (mecanismo) · <span class="sw" style="background:var(--peso)"></span>4 de 5 · <span class="sw" style="background:var(--morte)"></span>sinal varia (ruído co-adaptado). Esparsidade (|w| &lt; 0.1): {G['esparsidade']:.0%} · entropia normalizada da magnitude: {G['entropia_norm']:.2f} · os 8 mais fortes: {html.escape(', '.join(G['top']))}.</p>
<div class="card wrap">{genes_svg}</div>
<h2>2 · Sobreviver</h2>
<div class="card">{sob}<div class="leg">{''.join(f'<span><span class="sw" style="background:{COR[int(sd)%5]}"></span>s{sd}</span>' for sd in sds)}</div></div>
<h2>3 · O corpo ao longo dos cinco dias</h2>
<div class="grid2">{trajs}</div>
<h2>4 · Ativação e juízo</h2>
<p>"Reflexo" = quantas vezes por vida o portão do tanque abre e que fração do tempo vivo fica aberto. "Comer vence" = quando está parado sobre comida com fome ≥ 70, em que fração das vezes a decisão é comer (o resto é seguir viagem). Tempo com passageiro, tamanho médio da viagem em passos, orçamento de tempo, quase-mortes (vida &lt; 20 e recuperou), dinheiro no fim, e mortos por cidade (1000 · 1001 · 1002).</p>
<div class="card wrap">{tab}</div>
<h2>5 · As cinco linhagens são cinco soluções?</h2>
<p>Distância de fingerprint por posto (1 − correlação da ordem de importância dos genes; 0 = mesma solução, 1 = sem relação).</p>
<div class="card wrap">{fp}</div>
</main>"""
open(out, 'w').write(page); print('html', out, len(page))
