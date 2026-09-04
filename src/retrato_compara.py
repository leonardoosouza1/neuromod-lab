"""Compara N retratos lado a lado (reguas / arquiteturas / mundos) num painel HTML. Uso: retrato_compara.py OUT.html r1.json r2.json ..."""
import sys, json, html, statistics as st
out = sys.argv[1]; Rs = [json.load(open(p)) for p in sys.argv[2:]]
def med(R, k): return st.mean(s[k] for s in R['sementes'].values())
def medq(R, k, i=2): return st.mean(s[k][i] for s in R['sementes'].values())
def fp_med(R):
    D = R['genes']['dist_fingerprint']; n = len(D); v = [D[i][j] for i in range(n) for j in range(n) if i < j]; return st.mean(v) if v else 0.
def tpax(R): return med(R, 'frac_tempo_com_passageiro')
def andando(R): return st.mean(s['orcamento_tempo']['andando'] for s in R['sementes'].values())
rows = []
for R in Rs:
    G = R['genes']; n = G['nomes']; m = G['media']; top = sorted(range(len(m)), key=lambda i: -abs(m[i]))[:6]
    rows.append(f"<tr><td><b>{html.escape(R['tag'])}</b><br><small>{html.escape(R['braco'])}</small></td>"
                f"<td class=n>{med(R,'mortos'):.2f}</td><td class=n>{med(R,'entregas'):.1f}</td><td class=n>{med(R,'panes'):.1f}</td>"
                f"<td class=n>{medq(R,'dinheiro_fim'):.0f}</td><td class=n>{tpax(R):.0%}</td><td class=n>{med(R,'passos_por_viagem'):.0f}</td>"
                f"<td class=n>{med(R,'come_vence_quando_faminto'):.0%}</td><td class=n>{med(R,'reflexo_disparos'):.1f} · {med(R,'reflexo_ativo_frac'):.0%}</td>"
                f"<td class=n>{andando(R):.0%}</td><td class=n>{med(R,'quase_mortes'):.0%}</td><td class=n>{fp_med(R):.2f}</td><td class=n>{G['esparsidade']:.0%} · {G['entropia_norm']:.2f}</td>"
                f"<td><small>{html.escape(', '.join(f'{n[i]} {m[i]:+.1f}' for i in top))}</small></td></tr>")
# sobrevivencia por dia (media das sementes) em barras
def sob(R): return [st.mean(s['sobrevivencia_por_dia'][d] for s in R['sementes'].values()) for d in range(5)]
COR = ['#0E7C86', '#C8401F', '#B8851F', '#5B6ABF', '#2E7D4F', '#7A4E9E']
w, h, P = 760, 220, 34; X = lambda d: P + d*(w-2*P)/4; Y = lambda y: h-P - ((y-.5)/.5)*(h-2*P)
svg = [f'<svg viewBox="0 0 {w} {h}" class="chart">'] + [f'<line x1="{P}" x2="{w-P}" y1="{Y(y):.1f}" y2="{Y(y):.1f}" stroke="var(--line)"/><text x="{P-4}" y="{Y(y)+4:.1f}" text-anchor="end" font-size="10" fill="var(--ink2)">{y:.1f}</text>' for y in (.5,.6,.7,.8,.9,1.)]
for i, R in enumerate(Rs):
    pts = ' '.join(f'{X(d):.1f},{Y(v):.1f}' for d, v in enumerate(sob(R))); svg.append(f'<polyline points="{pts}" fill="none" stroke="{COR[i%6]}" stroke-width="2.5"/>')
svg.append(''.join(f'<text x="{X(d):.0f}" y="{h-P+14}" text-anchor="middle" font-size="10" fill="var(--ink2)">dia {d+1}</text>' for d in range(5)) + '</svg>')
leg = ''.join(f'<span><span class="sw" style="background:{COR[i%6]}"></span>{html.escape(R["tag"])}</span>' for i, R in enumerate(Rs))
page = f"""<title>Réguas lado a lado</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;700&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{--bg:#EDF0F3;--panel:#FFFFFF;--ink:#1A2129;--ink2:#4A5560;--line:#D3D9DF;--gas:#0E7C86;--morte:#C8401F;--mono:'IBM Plex Mono',ui-monospace,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#12161B;--panel:#1B2129;--ink:#E8ECF0;--ink2:#A7B1BB;--line:#2E3740;--gas:#3FB2BC;--morte:#E8674A}}}}
:root[data-theme="dark"]{{--bg:#12161B;--panel:#1B2129;--ink:#E8ECF0;--ink2:#A7B1BB;--line:#2E3740;--gas:#3FB2BC;--morte:#E8674A}}
body{{background:var(--bg);color:var(--ink);font:15px/1.5 'IBM Plex Sans',system-ui,sans-serif;margin:0}} main{{max-width:1100px;margin:0 auto;padding:28px 20px 60px}}
h1,h2{{font-family:'Barlow Condensed','Arial Narrow',sans-serif;margin:0;text-wrap:balance}} h1{{font-size:48px;line-height:1}} h2{{font-size:24px;margin-top:30px;padding-top:12px;border-top:2px solid var(--ink)}}
p{{max-width:72ch}} .card{{background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:14px 16px;margin-top:12px}} .chart{{width:100%;height:auto;display:block}}
table{{border-collapse:collapse;width:100%;font-size:13px}} th,td{{padding:6px 7px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}} th{{font-family:var(--mono);font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--ink2);font-weight:500}} td.n{{font-family:var(--mono);text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}} .wrap{{overflow-x:auto}}
.leg span{{display:inline-block;margin-right:14px;font-size:12px;color:var(--ink2)}} .sw{{display:inline-block;width:11px;height:11px;border-radius:2px;vertical-align:-1px;margin-right:4px}}
</style>
<main><h1>Réguas lado a lado</h1>
<p>Mesmo pai (campeão do reflexo, 5 postos, 120 gerações), mesmo mundo, 60 gerações a mais em cada régua. O que muda não é a nota — é o que o ser vira. Cada linha resume 5 linhagens × 192 vidas.</p>
<h2>Sobreviver, dia a dia</h2><div class="card">{''.join(svg)}<div class="leg">{leg}</div></div>
<h2>O ser que cada régua produz</h2>
<div class="card wrap"><table><tr><th>régua</th><th>mortos</th><th>entregas</th><th>panes</th><th>dinheiro fim</th><th>tempo c/ passageiro</th><th>passos/viagem</th><th>comer vence (faminto)</th><th>reflexo disparos · ativo</th><th>tempo andando</th><th>quase-mortes</th><th>fingerprint médio (diversidade)</th><th>esparsidade · entropia</th><th>genes mais fortes</th></tr>{''.join(rows)}</table></div>
</main>"""
open(out, 'w').write(page); print('html', out)
