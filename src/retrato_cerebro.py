"""E53 RETRATO DO CEREBRO (Leonardo: 'mediu o cerebro? como e ativo, distribuicao dos pesos, camadas lentas e rapidas, por tempo?').
Rastro tick a tick do campeao 'cerebro livre': estado das unidades LENTAS z_k (tau proprio), ativacao das RAPIDAS na opcao escolhida,
contribuicao de cada parte (linear / rapida / lenta) pra nota escolhida, corpo. + distribuicao dos pesos por bloco, tau por unidade,
o que cada unidade LE (correlacao com tanque/fome/agua/dinheiro/passageiro) e ablacao (sem rapida / sem lenta / so linear).
Uso: python src/retrato_cerebro.py <e43.json> "<braco>" <tag> [--L 200 --dias 10 --out DIR]"""
import sys, os, json, argparse, math
sys.path.insert(0, os.path.dirname(__file__))
import torch
from campo import *
from campo import _fit
from e43_campo import BRACOS
import completo as CP

def rastro(W, mapas, cfg, T, R=64, seed=1000, A=Cerebro):
    m = Campo(mapas, 1, cfg, seed=seed, R=R); Wb = W[None, :][m.gidx]; a = A(); a.reset(m, Wb); B = m.B
    rec = {k: [] for k in ('z', 'h', 'lin', 'rap', 'len', 'fuel', 'fome', 'agua', 'dinh', 'pax', 'vivo', 'esc', 'gate', 'mem', 'ref')}
    for t in range(T):
        F, val = m.obs()
        sc_lin = torch.einsum('bgf,bf->bg', F, Wb[:, :NF]); ex = a.extra(m, Wb, F)
        rap = torch.einsum('bgh,bh->bg', a.h, a.V); lent = ex - rap
        sc = sc_lin + ex; sc = sc - sc.mean(1, keepdim=True)
        svn, sv = m.serv_need(); ss = svn*Wb[:, NF:NF+S] + Wb[:, NF+S:NF+S+1] + a.extra_serv(m); ss = ss.masked_fill(sv <= 0, -1e9)
        esc = torch.cat([sc, ss], 1).argmax(1); g = esc.clamp(max=G - 1)
        rec['z'].append(a.z.clone()); rec['h'].append(a.h[torch.arange(B, device=DEV), g]); rec['esc'].append(esc.clone())
        if hasattr(a, '_gate'): rec['gate'].append(a._gate(m)); rec['mem'].append(a._mem(m)); rec['ref'].append(a._ativ().clone())
        rec['lin'].append(sc_lin.gather(1, g[:, None]).squeeze(1)); rec['rap'].append(rap.gather(1, g[:, None]).squeeze(1)); rec['len'].append(lent.gather(1, g[:, None]).squeeze(1))
        rec['fuel'].append(m.fuel.clone()); rec['fome'].append(m.fome.clone()); rec['agua'].append(m.agua.clone()); rec['dinh'].append(m.dinh.clone()); rec['pax'].append((m.pd_ >= 0).float()); rec['vivo'].append((m.vida > 0).float())
        m.passo(esc); a.atualizar(m)
    out = {k: torch.stack(v).cpu() for k, v in rec.items() if v}          # (T,B,...)
    return out, a, m

def blocos(W, A=Cerebro):
    b = {'linear (24 mov + 10 serv + bias)': W[:A.O_U], 'U rapida (entrada)': W[A.O_U:A.O_BU], 'V rapida (saida)': W[A.O_V:A.O_U2],
                      'U2 lenta (entrada)': W[A.O_U2:A.O_B2], 'tau lenta': W[A.O_TAU:A.O_M], 'M lenta (modula mov)': W[A.O_M:A.O_P], 'P lenta (servicos)': W[A.O_P:Cerebro.NP]}
    if hasattr(A, 'O_REF'):
        b.update({'reflexo (tau,w,v,theta)': W[A.O_REF:A.O_REF+4], 'talamo (5 grupos x a,b,c)': W[A.O_TAL:A.O_TAL+A.N_TAL], 'cortex (12 distritos x 4)': W[A.O_COR:A.O_COR+A.N_COR],
                  'hipocampo tau+ganho': W[A.O_HIP:A.O_HIP+2], 'hipocampo M_h (mem x sentido)': W[A.O_HIP+2:A.O_HIP+2+3*NF], 'hipocampo P_h (servicos)': W[A.O_HIP+2+3*NF:A.NP]})
    return {k: dict(n=int(v.numel()), abs_med=float(v.abs().mean()), abs_max=float(v.abs().max()), frac_grande=float((v.abs() > .5).float().mean()), q=[float(x) for x in v.float().quantile(torch.tensor([.1, .5, .9], device=v.device))]) for k, v in b.items()}

def corr(x, y):
    x = x - x.mean(); y = y - y.mean(); d = (x.norm()*y.norm()).clamp(min=1e-6); return float((x*y).sum()/d)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('json'); ap.add_argument('braco'); ap.add_argument('tag'); ap.add_argument('--L', type=float, default=200.); ap.add_argument('--dias', type=float, default=10.)
    ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e53'); a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
    J = json.load(open(a.json))['bracos'][a.braco]; T = int(240*a.dias); cfg = CfgCampo(L=a.L, fitness='bemestar'); A = dict(BRACOS)[a.braco]
    teste = [gerar_mapa(1000 + s, L=a.L) for s in range(3)]; R = {}
    for sd in sorted(J['W']):
        W = torch.tensor(J['W'][sd], device=DEV); rec, ag, m = rastro(W, teste[:1], cfg, T, A=A)
        vivo = rec['vivo'].bool(); tv = vivo.sum(0); b0 = int(tv.argmax())         # o ser que viveu mais
        eeg = {k: rec[k][:, b0].tolist() for k in ('lin', 'rap', 'len', 'fuel', 'fome', 'agua', 'dinh', 'pax', 'vivo')}
        eeg['z'] = rec['z'][:, b0].tolist(); eeg['h'] = rec['h'][:, b0].tolist(); eeg['esc'] = rec['esc'][:, b0].tolist()
        if 'gate' in rec: eeg['gate'] = rec['gate'][:, b0].tolist(); eeg['mem'] = rec['mem'][:, b0].tolist(); eeg['ref'] = rec['ref'][:, b0].tolist()
        # o que cada unidade lenta le: correlacao (ticks vivos, todos os seres)
        msk = vivo.flatten(); le = {}
        for k in range(Cerebro.K):
            zk = rec['z'][:, :, k].flatten()[msk]; le[f'z{k}'] = {v: round(corr(zk, rec[v].flatten()[msk]), 3) for v in ('fuel', 'fome', 'agua', 'dinh', 'pax')}
        for k in range(Cerebro.H):
            hk = rec['h'][:, :, k].flatten()[msk]; le[f'h{k}'] = {v: round(corr(hk, rec[v].flatten()[msk]), 3) for v in ('fuel', 'fome', 'agua', 'dinh', 'pax')}
        # peso de cada parte na decisao: desvio da contribuicao (ticks vivos)
        parte = {k: float(rec[k].flatten()[msk].std()) for k in ('lin', 'rap', 'len')}
        # ablacao
        abl = {}
        cortes = [('completo', ()), ('sem rapida (V=0)', ((Cerebro.O_V, Cerebro.O_U2),)), ('sem lenta (M=P=0)', ((Cerebro.O_M, Cerebro.NP),))]
        if hasattr(A, 'O_REF'):
            cortes += [('sem reflexo', ((A.O_REF+1, A.O_REF+3),)), ('sem talamo', ((A.O_TAL, A.O_TAL+A.N_TAL),)), ('sem cortex', ((A.O_COR, A.O_COR+A.N_COR),)), ('sem hipocampo', ((A.O_HIP+1, A.O_HIP+2),)),
                       ('so linear', ((Cerebro.O_V, Cerebro.O_U2), (Cerebro.O_M, Cerebro.NP), (A.O_REF+1, A.O_REF+3), (A.O_TAL, A.O_TAL+A.N_TAL), (A.O_COR, A.O_COR+A.N_COR), (A.O_HIP+1, A.O_HIP+2)))]
        else: cortes += [('so linear', ((Cerebro.O_V, Cerebro.O_U2), (Cerebro.O_M, Cerebro.NP)))]
        for nome, zera in cortes:
            Wa = W.clone()
            for i0, i1 in zera: Wa[i0:i1] = 0.
            med = medidas(A, Wa, teste, cfg, T=T, seed=7777, R=1, copias=128); abl[nome] = dict(mortos=med['mortos'], ent=med['ent'], panes=med['panes'])
        R[sd] = dict(eeg=eeg, le=le, parte=parte, blocos=blocos(W, A), tau=[float(x) for x in ag.tau[0]], ablacao=abl, ser=b0, t_vida=int(tv[b0]))
        print(f'seed {sd}: tau {[round(x,1) for x in R[sd]["tau"]]} | desvio das partes lin {parte["lin"]:.3f} rap {parte["rap"]:.3f} len {parte["len"]:.3f} | ablacao ' +
              ' · '.join(f'{k}: {v["mortos"]:.2f}/{v["panes"]:.1f}' for k, v in abl.items()), flush=True)
        for u, c in le.items(): print(f'   {u} le: ' + ' '.join(f'{v} {r:+.2f}' for v, r in c.items()), flush=True)
        for k, b in R[sd]['blocos'].items(): print(f'   {k:<32} n {b["n"]:4d} |w| med {b["abs_med"]:.2f} max {b["abs_max"]:.2f} >0.5: {100*b["frac_grande"]:.0f}%', flush=True)
    json.dump(R, open(os.path.join(a.out, f'retrato_cerebro{a.tag}.json'), 'w'))
    painel(R, os.path.join(a.out, f'retrato_cerebro{a.tag}.html'))

def painel(R, out):
    sd = sorted(R)[0]; r = R[sd]; e = r['eeg']; T = len(e['fuel']); K = Cerebro.K; H = Cerebro.H
    dados = json.dumps(dict(e=e, tau=r['tau'], le=r['le'], abl=r['ablacao'], parte=r['parte'], blocos=r['blocos'], t_vida=r['t_vida']))
    h = '''<title>EEG do Cérebro Livre</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>:root{--bg:#f6f4ee;--ink:#1d1b17;--mute:#6b665c;--line:#d9d4c8;--card:#fdfcf8;--amb:#c9780f;--slate:#3f5f8a;--red:#b8362b;--hun:#7f8f3a;--thi:#3f8a8a;--grid:#ebe7dd;--vio:#7a4e9e}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#15140f;--ink:#efeae0;--mute:#a49d90;--line:#37342c;--card:#1d1b16;--amb:#e6a23a;--slate:#7fa0cf;--red:#e0645a;--hun:#a5b75c;--thi:#5fb0b0;--grid:#2a2822;--vio:#b58ad8}}
:root[data-theme="dark"]{--bg:#15140f;--ink:#efeae0;--mute:#a49d90;--line:#37342c;--card:#1d1b16;--amb:#e6a23a;--slate:#7fa0cf;--red:#e0645a;--hun:#a5b75c;--thi:#5fb0b0;--grid:#2a2822;--vio:#b58ad8}
body{background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans",system-ui,sans-serif;font-size:15px;line-height:1.5;margin:0}main{max-width:1100px;margin:0 auto;padding:32px 20px 64px}
h1{font-family:"Bricolage Grotesque",sans-serif;font-weight:700;font-size:clamp(28px,4.5vw,42px);line-height:1.05;margin:0 0 8px;text-wrap:balance}h2{font-family:"Bricolage Grotesque",sans-serif;font-weight:600;font-size:21px;margin:36px 0 4px}
.eyebrow{font-family:"IBM Plex Mono",monospace;font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--mute)}p{max-width:70ch;margin:6px 0 10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}canvas{width:100%;height:auto;display:block}.wrap{overflow-x:auto}
table{border-collapse:collapse;font-family:"IBM Plex Mono",monospace;font-size:12.5px;font-variant-numeric:tabular-nums}td,th{padding:4px 10px;border-bottom:1px solid var(--line);text-align:right}th:first-child,td:first-child{text-align:left}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-family:"IBM Plex Mono",monospace;font-size:12.5px;margin:8px 0}.sw{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-1px;margin-right:5px}</style>
<main><div class="eyebrow">neuromod-lab · E53 cérebro livre · campeão semente ''' + str(sd) + ''' · o ser que viveu mais (''' + str(r['t_vida']) + ''' ticks)</div>
<h1>O cérebro do ser, tick a tick</h1>
<p>Camada lenta: três unidades com o próprio tempo (τ ≈ ''' + ', '.join(f'{x:.0f}' for x in r['tau']) + ''' ticks). Camada rápida: quatro unidades que leem os sentidos da opção escolhida. Embaixo, quanto cada parte pesou na decisão e o corpo. Faixas escuras = noite.</p>
<div class="card wrap"><canvas id="eeg" width="1060" height="1000"></canvas></div>
<h2>O que cada unidade lê</h2><p>Correlação da ativação com o corpo, sobre todos os seres e ticks vivos. Perto de zero = não lê aquilo.</p><div class="card wrap" id="le"></div>
<h2>Quanto cada parte vale</h2><p>Ablação no teste (3 mapas × 128 cópias): zerar a saída da camada e medir mortos e panes.</p><div class="card wrap" id="abl"></div>
<h2>Distribuição dos pesos por bloco</h2><div class="card wrap" id="blocos"></div></main>
<script>const D=''' + dados + '''; const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
(function(){const c=document.getElementById('eeg'),g=c.getContext('2d'),W=c.width,H=c.height,L=70,R=10; const e=D.e,T=e.fuel.length; const x=t=>L+t/(T-1)*(W-L-R);
const rows=[]; for(let k=0;k<e.z[0].length;k++) rows.push({n:'lenta z'+k+' τ'+Math.round(D.tau[k]),v:e.z.map(a=>a[k]),c:'--vio'});
for(let k=0;k<e.h[0].length;k++) rows.push({n:'rápida h'+k,v:e.h.map(a=>a[k]),c:'--slate'});
if(e.gate){const gn=['rota','servicos','corpo','economia','tempo']; for(let k=0;k<e.gate[0].length;k++) rows.push({n:'tálamo '+gn[k],v:e.gate.map(a=>a[k]),c:'--hun'}); const mn=['renda','espera','gasto']; for(let k=0;k<e.mem[0].length;k++) rows.push({n:'hipocampo '+mn[k],v:e.mem.map(a=>a[k]),c:'--thi'}); rows.push({n:'reflexo',v:e.ref,c:'--red'});}
rows.push({n:'parte linear',v:e.lin,c:'--ink'},{n:'parte rápida',v:e.rap,c:'--slate'},{n:'parte lenta',v:e.len,c:'--vio'},{n:'tanque',v:e.fuel,c:'--amb'},{n:'fome',v:e.fome,c:'--hun'},{n:'dinheiro',v:e.dinh,c:'--thi'},{n:'passageiro',v:e.pax,c:'--mute'});
const rh=(H-30)/rows.length; g.fillStyle=css('--grid'); for(let d=0;d<10;d++){const t0=d*240+22*10, t1=Math.min(T,d*240+240+6*10); if(t0<T) g.fillRect(x(t0),0,x(Math.min(t1,T-1))-x(t0),H-30);}
g.fillStyle=css('--mute'); g.font='11px IBM Plex Mono'; g.textAlign='center'; for(let d=0;d<10;d++) g.fillText('dia '+(d+1),x(d*240+120),H-10);
const tv=D.t_vida; rows.forEach((r,i)=>{const y0=i*rh+4,h=rh-8; let mn=Math.min(...r.v),mx=Math.max(...r.v); if(mx-mn<1e-9){mx=mn+1;} const y=v=>y0+h-(v-mn)/(mx-mn)*h;
 g.strokeStyle=css('--line'); g.beginPath(); g.moveTo(L,y0+h); g.lineTo(W-R,y0+h); g.stroke(); g.strokeStyle=css(r.c); g.lineWidth=1.2; g.beginPath(); for(let t=0;t<Math.min(T,tv);t++){t?g.lineTo(x(t),y(r.v[t])):g.moveTo(x(t),y(r.v[t]));} g.stroke();
 g.fillStyle=css('--ink'); g.textAlign='right'; g.font='11.5px IBM Plex Mono'; g.fillText(r.n,L-6,y0+h/2+4); g.fillStyle=css('--mute'); g.font='10px IBM Plex Mono'; g.textAlign='left'; g.fillText(mx.toFixed(2),W-R-40,y0+9); g.fillText(mn.toFixed(2),W-R-40,y0+h-1);});
 if(tv<T){g.strokeStyle=css('--red'); g.setLineDash([4,3]); g.beginPath(); g.moveTo(x(tv),0); g.lineTo(x(tv),H-30); g.stroke(); g.setLineDash([]); g.fillStyle=css('--red'); g.textAlign='left'; g.fillText('morte',x(tv)+4,12);}})();
(function(){const vs=['fuel','fome','agua','dinh','pax']; let t='<table><tr><th>unidade</th>'+vs.map(v=>'<th>'+v+'</th>').join('')+'</tr>'; for(const [u,c] of Object.entries(D.le)){t+='<tr><td>'+u+'</td>'+vs.map(v=>{const r=c[v]; const a=Math.min(1,Math.abs(r)*1.4); return `<td style="background:${r>0?'rgba(201,120,15,'+a+')':'rgba(63,95,138,'+a+')'}">${r.toFixed(2)}</td>`;}).join('')+'</tr>';} document.getElementById('le').innerHTML=t+'</table>';})();
(function(){let t='<table><tr><th>configuração</th><th>mortos</th><th>entregas</th><th>panes</th></tr>'; for(const [k,v] of Object.entries(D.abl)) t+=`<tr><td>${k}</td><td>${v.mortos.toFixed(2)}</td><td>${v.ent.toFixed(1)}</td><td>${v.panes.toFixed(1)}</td></tr>`; t+='</table><p style="font-size:13px;color:var(--mute)">Desvio-padrão da contribuição de cada parte na nota escolhida: linear '+D.parte.lin.toFixed(3)+' · rápida '+D.parte.rap.toFixed(3)+' · lenta '+D.parte.len.toFixed(3)+'</p>'; document.getElementById('abl').innerHTML=t;})();
(function(){let t='<table><tr><th>bloco</th><th>genes</th><th>|w| médio</th><th>|w| máx</th><th>&gt;0.5</th><th>p10 / p50 / p90</th></tr>'; for(const [k,b] of Object.entries(D.blocos)) t+=`<tr><td>${k}</td><td>${b.n}</td><td>${b.abs_med.toFixed(2)}</td><td>${b.abs_max.toFixed(2)}</td><td>${Math.round(100*b.frac_grande)}%</td><td>${b.q.map(v=>v.toFixed(2)).join(' / ')}</td></tr>`; document.getElementById('blocos').innerHTML=t+'</table>';})();
</script>'''
    open(out, 'w').write(h)

if __name__ == '__main__': main()
