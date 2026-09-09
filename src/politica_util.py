"""Utilidades do juiz de politicas explicitas (doc 53): carregar com lista negra, involucro ciente da assinatura, medir, tracar."""
import os, re, json, inspect, argparse, hashlib
import torch; from campo import *; from e43_campo import aplica_cenario, alinha_semente
PROIBIDO = [r'\bimport\s+(?!torch\b|math\b)', r'\bfrom\s+(?!torch\b|math\b)', r'\b(os|sys|subprocess|open|exec|eval|__import__|compile|globals|locals|getattr|setattr)\s*\(', r'\.px\b', r'\.pxd\b', r'\.serv\[', r'\.serv_msk', r'\.g\b', r'\.dest\b']
def carrega(path):
    """devolve (classe involucrada, erro). Nunca levanta: erro vira string para o placar."""
    try:
        src = open(path).read()
        for pat in PROIBIDO:
            if re.search(pat, src): return None, f'padrao proibido {pat!r}'
        ns = {'torch': torch, 'math': __import__('math'), 'G': G, 'S': S, 'NF': NF, 'NOMES_OP': NOMES_OP, 'NOMES_CORPO': NOMES_CORPO, 'Linear': Linear, 'DEV': DEV}
        torch.set_default_device(DEV); exec(compile(src, path, 'exec'), ns)
        if 'fabrica' not in ns: return None, 'sem fabrica()'
        POL0 = ns['fabrica']()
    except Exception as e: return None, f'carga: {type(e).__name__}: {str(e)[:120]}'
    class POL:
        NP = Linear.NP
        def __init__(s): s.p = POL0() if isinstance(POL0, type) else POL0
        def _call(s, nome, *args):
            fn = getattr(s.p, nome, None)
            if fn is None: return None
            n = len([q for q in inspect.signature(fn).parameters.values() if q.default is inspect._empty and q.kind in (q.POSITIONAL_ONLY, q.POSITIONAL_OR_KEYWORD)])
            if n == len(args) + 1: return fn(s.p, *args)
            if n < len(args): return fn(*args[:n])
            return fn(*args)
        def reset(s, m, W): return s._call('reset', m, W)
        def extra(s, m, W, F):
            if hasattr(s.p, 'extra'): return s._call('extra', m, W, F)
            s.p.F = F; return torch.zeros(m.B, G, device=DEV)
        def decidir(s, tudo, m): return s._call('decidir', tudo, m)
        def atualizar(s, m): return s._call('atualizar', m)
    return POL, None
def mundo(cenario_path=None, nevoa=None):
    """[spec Mundo Vivo I1b] nevoa=None = hoje (onisciente); o cenario.json (mundo.nevoa) tambem chega aqui via aplica_cenario"""
    fl = argparse.Namespace(L=200., dias=10., fitness='riqueza', nevoa=float('inf'), npx=12, respawn=20., pax_cidade=False, ponto=0., dinh0=10., fome_passo=None, kcal_pane=8., guincho=0., fuel_pane=15., P=None, G=None, paciencia=None, R=None, seeds=None, so=None, mundo='distinto')
    cen = json.load(open(cenario_path)) if cenario_path else {}; ex = aplica_cenario(fl, cen)
    if nevoa is not None: fl.nevoa = float(nevoa)
    cfg = CfgCampo(L=fl.L, fitness=fl.fitness); cfg.horizonte = getattr(fl, 'horizonte', 'fixo'); cfg.w_trab = getattr(fl, 'w_trab', 1.); cfg.KCAL_PANE = fl.kcal_pane; cfg.dinh0 = fl.dinh0; cfg.GUINCHO = fl.guincho; cfg.FUEL_POS_PANE = fl.fuel_pane; cfg.nevoa = fl.nevoa; cfg.ponto = fl.ponto; cfg.NPX = fl.npx; cfg.respawn = fl.respawn; cfg.pax_cidade = fl.pax_cidade
    if fl.fome_passo is not None: cfg.fome_passo = fl.fome_passo
    for k in ('amp_preco', 'periodo_preco', 'tarifa_base', 'tarifa_km'):
        if ex.get(k) is not None: setattr(cfg, k, ex[k])
    teste = [gerar_mapa(1000 + s, L=fl.L, distinto=fl.mundo == 'distinto', perfis=ex['perfis'], K=ex['K'], ruas=ex['ruas']) for s in range(3)]
    chave = hashlib.md5(json.dumps(cen, sort_keys=True).encode()).hexdigest()[:8] if cen else 'base'
    return cfg, teste, int(240*fl.dias), chave
def mede(Arq, W, cfg, teste, T, seeds, copias=128):
    r = {k: [] for k in ('mortos', 'ent', 'rec', 'panes', 'fome_fim', 'n_come', 'n_posto', 'dinh_fim', 'agua_fim', 'dia_morte', 'c_fome', 'c_sede', 'c_divida', 'c_dano', 'n_oficina')}
    for sd in seeds:
        m = rodar(Arq, W[None, :].repeat(copias, 1), teste, cfg, T, sd, R=1); morto = m.vida <= 0; nm = morto.float().sum().clamp(min=1.)
        r['mortos'].append(float(morto.float().mean())); r['ent'].append(float(m.ent.mean())); r['rec'].append(float(m.rec.mean())); r['panes'].append(float(m.av_fuel.mean())); r['fome_fim'].append(float(m.fome.mean()))
        r['n_come'].append(float(m.n_come.mean())); r['n_posto'].append(float(m.n_posto.mean())); r['n_oficina'].append(float(m.n_oficina.mean())); r['dinh_fim'].append(float(m.dinh.mean())); r['agua_fim'].append(float(m.agua.mean()))
        r['dia_morte'].append(float((m.t_vida[morto]/240.).mean()) if bool(morto.any()) else 10.)
        fome = morto & (m.fome >= cfg.FOME_CRIT); sede = morto & (m.agua <= cfg.AGUA_CRIT); div = morto & (m.dinh < -cfg.LIMITE_DIVIDA)
        r['c_fome'].append(float(fome.float().sum()/nm)); r['c_sede'].append(float(sede.float().sum()/nm)); r['c_divida'].append(float(div.float().sum()/nm)); r['c_dano'].append(float((morto & ~fome & ~sede & ~div).float().sum()/nm))
    med = {k: sum(v)/len(v) for k, v in r.items()}; med['mortos_por_seed'] = [round(x, 3) for x in r['mortos']]
    for k, v in r.items(): med[k + '_por_semente'] = [round(x, 4) for x in v]   # [spec I1c] regua pareada (analise_campo.py) sobre o placar
    return med
def traco(Arq, W, cfg, teste, T=2400, B=64):
    """histograma das escolhas na vida inteira + 'ficar' separado em NO RAIO de um servico (funcional) vs FORA (desperdicio)"""
    m = Campo(teste, B, cfg, seed=7777, R=1); Wb = W[None, :].repeat(B, 1)[m.gidx]; ar = Arq(); ar.reset(m, Wb); cont = torch.zeros(G + S, device=DEV); fic_raio = 0.; fic_fora = 0.
    for t in range(T):
        F, val = m.obs(); sc = torch.einsum('bgf,bf->bg', F, Wb[:, :NF]) + ar.extra(m, Wb, F); sc = sc - sc.mean(1, keepdim=True)
        svn, sv = m.serv_need(); ss = (svn*Wb[:, NF:NF+S] + Wb[:, NF+S:NF+S+1]).masked_fill(sv <= 0, -1e9); tudo = torch.cat([sc, ss], 1)
        esc = ar.decidir(tudo, m) if hasattr(ar, 'decidir') else tudo.argmax(1); esc = esc.long().clamp(0, G + S - 1); vivo = m.vida > 0
        fic = (esc == G - 1) & vivo; perto = m._dist.min(1).values <= cfg.raio; fic_raio += float((fic & perto).float().sum()); fic_fora += float((fic & ~perto).float().sum())
        cont += torch.bincount(esc[vivo], minlength=G + S).float(); m.passo(esc); ar.atualizar(m)
    tot = float(cont.sum()); f = (cont/max(tot, 1.)).tolist(); nomes = [f'{t}{int(q) if q else ""}' for t, q in ACOES]
    d = {'mover': sum(f[:G - 1]), 'ficar_no_raio': fic_raio/max(tot, 1.), 'ficar_fora': fic_fora/max(tot, 1.)}; d.update({nomes[k]: f[G + k] for k in range(S)})
    return d
def linha(nome, med, tr=None):
    s = (f"{nome[:34]:<34} mortos {med['mortos']:.2f} {med['mortos_por_seed']} ent {med['ent']:5.1f} renda {med['rec']:5.0f} panes {med['panes']:4.1f} refeicoes {med['n_come']:4.1f} abast {med['n_posto']:4.1f} oficina {med['n_oficina']:3.1f} "
         f"| dia {med['dia_morte']:.1f}: fome {100*med['c_fome']:.0f}% sede {100*med['c_sede']:.0f}% divida {100*med['c_divida']:.0f}% dano {100*med['c_dano']:.0f}% | fim: fome {med['fome_fim']:.0f} agua {med['agua_fim']:.0f} $ {med['dinh_fim']:.0f}")
    if tr: s += ' | traco: ' + ' '.join(f'{k} {v:.2f}' for k, v in tr.items() if v > 0.005)
    return s
