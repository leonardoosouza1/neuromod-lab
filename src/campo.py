"""E43 CAMPO (doc 44): mundo continuo na GPU. Posicao (x,y), 8 direcoes + ficar, servicos = pontos, distritos = regioes
(Voronoi), ruas/transito = campo de custo (textura), passageiros = pontos com destino. Corpo: gasolina, AGUA, fome, fadiga,
calor, vida, dinheiro, reserva. Litros escolhidos no posto. Tudo tensor; nada por passo na CPU; sem sync no laco.
Interface igual ao grafo: m.obs() -> (F (B,G,NF), val (B,G)); m.serv_need() -> (svn, sv) (B,S); esc < G move, esc >= G serve."""
import os, math, torch
os.environ.setdefault('TORCHINDUCTOR_COMPILE_THREADS', '1')   # [auditoria 16] sem pool de 17 processos de compilacao
from lab import DEV, evoluir_sementes

G = 9                                   # 8 direcoes + ficar
GR = 128                                # grade dos campos pre-computados (celula = L/128)
DIRS = torch.tensor([[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1],[0,0]], dtype=torch.float32)
DIRS = DIRS/DIRS.norm(dim=1, keepdim=True).clamp(min=1e-6); DIRS[8] = 0.
TIPOS = ['posto', 'comida', 'agua', 'descanso', 'oficina']                 # loja: v2
DENS = {'posto': 1/2500., 'comida': 1/2500., 'agua': 1/2000., 'descanso': 1/3000., 'oficina': 1/2000.}
# servicos (acoes G..G+S-1): posto x litros, agua x litros, comida, descanso, oficina
ACOES = [('posto', 25.), ('posto', 50.), ('posto', 75.), ('posto', 100.), ('posto', 150.), ('agua', 50.), ('agua', 100.),
         ('comida', 0.), ('descanso', 0.), ('oficina', 0.)]
S = len(ACOES)
NOMES_OP = ['d_alvo', 'd_posto', 'd_comida', 'd_agua', 'd_oficina', 'd_descanso', 'custo_frente', 'preco_frente', 'aliq_frente', 'casa_frente']
NOMES_CORPO = ['e_fuel', 'e_agua', 'e_fome', 'e_fadiga', 'e_calor', 'e_vida', 'e_dinheiro', 'e_reserva', 'e_tem_pax', 'h_sin', 'h_cos', 'e_noite', 'custo_aqui', 'bias']
NF = len(NOMES_OP) + len(NOMES_CORPO)   # 24
NOMES_F = NOMES_OP + NOMES_CORPO + [f'sv_{a[0]}{int(a[1]) if a[1] else ""}' for a in ACOES] + ['sv_bias']

class CfgCampo:
    def __init__(s, L=400., **kw):
        s.L = float(L); s.dia = 240; s.noite = True; s.vel = 1.0; s.vel_noite = .7
        s.NPX = 12; s.K = max(3, round(6*s.L/200.)); s.tex = 64; s.raio = 6.; s.raio_px = 45.; s.dinh0 = 20.; s.loja_no_posto = True   # nasce POBRE: com 100 vivia de poupanca 10 dias sem trabalhar
        s.fuel_passo = .15; s.agua_passo = .08; s.agua_calor = .12; s.fome_passo = .32; s.fad_passo = .15   # agua ~2 dias; gasolina ~250 passos
        s.calor_sobe = .15; s.calor_desce = .6      # sustentavel a ~70% de rodagem (0.15*1.85*.7 = .19 sobe vs .6*.3 = .18 esfria); direto: 30 -> 92 em ~220 passos
        s.CALOR_MAX = 92.; s.D_QUENTE = 6.; s.D_PANE = 6.; s.D_RODAR = .15
        s.fome_mata = .15; s.FOME_CRIT = 90.; s.agua_mata = .15; s.AGUA_CRIT = 10.; s.KCAL_PANE = 20.
        s.preco_L = .3; s.preco_agua = .05; s.preco_comida = 2.; s.HOTEL = 8.; s.preco_oficina = 10.; s.REPARO = 25.
        s.tarifa_base = 3.; s.tarifa_km = .25; s.aluguel = 4.; s.LIMITE_DIVIDA = 60.; s.PERDA_ARMAZ = .15; s.RES_MAX = 120.; s.perda_res = .02/240
        s.REFEICAO = 90.; s.pena_morte = 5.; s.fitness = 'sobrevive'
        for k, v in kw.items(): setattr(s, k, v)

def gerar_mapa(seed, L=400., K=None, tex=64):
    """tudo na GPU. devolve dict de tensores: custo (tex,tex), servicos {tipo: (N,2)}, centros (K,2), aliq/pmul/alug (K,)."""
    g = torch.Generator(device=DEV); g.manual_seed(int(seed)); K = K or max(3, round(6*L/200.))
    ru = torch.rand(1, 1, tex, tex, generator=g, device=DEV)
    k = torch.ones(1, 1, 7, 7, device=DEV)/49.
    for _ in range(3): ru = torch.nn.functional.conv2d(torch.nn.functional.pad(ru, (3, 3, 3, 3), mode='replicate'), k)
    ru = (ru - ru.min())/(ru.max() - ru.min() + 1e-9); custo = 1. + 2.*ru[0, 0]                     # [1,3]
    serv = {}
    for t in TIPOS:
        n = max(3, int(round(DENS[t]*L*L))); serv[t] = torch.rand(n, 2, generator=g, device=DEV)*L
    centros = torch.rand(K, 2, generator=g, device=DEV)*L
    aliq = .05 + .30*torch.rand(K, generator=g, device=DEV); pmul = .7 + .9*torch.rand(K, generator=g, device=DEV)
    alug = .5 + 1.5*torch.rand(K, generator=g, device=DEV)
    # campos pre-computados (grade GR x GR): distancia ao servico mais perto por tipo, e distrito da celula
    ax = (torch.arange(GR, device=DEV).float() + .5)*(L/GR); gy, gx = torch.meshgrid(ax, ax, indexing='ij'); cel = torch.stack([gx, gy], -1).view(-1, 2)   # (GR*GR,2) (x,y)
    campo_dist = (cel[:, None, :] - centros[None]).norm(dim=-1).argmin(1).view(GR, GR)                                        # (GR,GR) long
    return dict(L=L, custo=custo, serv=serv, centros=centros, aliq=aliq, pmul=pmul, alug=alug, seed=int(seed), campo_dist=campo_dist)

OBRAS_MAX = 16                          # slots livres por tipo e por mapa para o prefeito construir
def _empilha(mapas, chave):
    xs = [m[chave] for m in mapas]; n = max(x.shape[0] for x in xs) + OBRAS_MAX
    out = torch.zeros(len(xs), n, 2, device=DEV); msk = torch.zeros(len(xs), n, dtype=torch.bool, device=DEV)
    for i, x in enumerate(xs): out[i, :x.shape[0]] = x; msk[i, :x.shape[0]] = True
    return out, msk

class Campo:
    def __init__(s, mapas, P, cfg, seed=0, R=1):
        s.cfg = c = cfg; s.NC = len(mapas); s.R = R; s.P = P; B = s.B = P*s.NC*R; s.L = float(mapas[0]['L'])
        s.cidx = torch.arange(s.NC, device=DEV).repeat_interleave(R).repeat(P)           # (B,)
        s.gidx = torch.arange(P, device=DEV).repeat_interleave(s.NC*R)
        g = torch.Generator(device=DEV); g.manual_seed(int(seed)); s.g = g
        s.custo_tex = torch.stack([m['custo'] for m in mapas])                              # (NC,tex,tex)
        s.campo_dist = torch.stack([m['campo_dist'] for m in mapas])                        # (NC,GR,GR)
        s.serv = {}; s.serv_msk = {}
        for t in TIPOS: s.serv[t], s.serv_msk[t] = _empilha([{'p': m['serv'][t]} for m in mapas], 'p')
        s.centros = torch.stack([m['centros'] for m in mapas]); s.K = s.centros.shape[1]      # (NC,K,2)
        s.aliq = torch.stack([m['aliq'] for m in mapas]); s.pmul = torch.stack([m['pmul'] for m in mapas]); s.alug = torch.stack([m['alug'] for m in mapas])
        s.fase = torch.rand(s.NC, generator=g, device=DEV)[s.cidx]*c.dia
        s.dirs = DIRS.to(DEV)
        # estado
        s.pos = torch.rand(B, 2, generator=g, device=DEV)*s.L
        s.casa = s.distrito(s.pos)
        s.fuel = torch.full((B,), 85., device=DEV); s.agua = torch.full((B,), 85., device=DEV); s.fome = torch.full((B,), 10., device=DEV)
        s.fad = torch.full((B,), 10., device=DEV); s.calor = torch.full((B,), 30., device=DEV); s.vida = torch.full((B,), 100., device=DEV)
        s.dinh = torch.full((B,), c.dinh0, device=DEV); s.res = torch.zeros(B, device=DEV); s.tpar = torch.zeros(B, device=DEV)
        s.ent = torch.zeros(B, device=DEV); s.rec = torch.zeros(B, device=DEV); s.avar = torch.zeros(B, device=DEV); s.av_fuel = torch.zeros(B, device=DEV)
        s.n_posto = torch.zeros(B, device=DEV); s.litros = torch.zeros(B, device=DEV); s.n_oficina = torch.zeros(B, device=DEV); s.n_come = torch.zeros(B, device=DEV)
        s.dano_soma = torch.zeros(B, device=DEV); s.t_vida = torch.zeros(B, device=DEV); s.bem_soma = torch.zeros(B, device=DEV)
        s.px = s._perto(s.pos, c.NPX); s.pxd = s._destino(s.px)   # passageiros privados por ser, nascem perto
        s.pd_ = torch.full((B,), -1., device=DEV); s.dest = torch.zeros(B, 2, device=DEV); s.orig_d = torch.zeros(B, dtype=torch.long, device=DEV); s.emb = torch.zeros(B, 2, device=DEV)
        s.px_ok = torch.ones(B, c.NPX, dtype=torch.bool, device=DEV)   # [E44 v2] demanda: slot de passageiro ativo; tarifa alta = reaparece devagar
        s.t = torch.zeros((), dtype=torch.long, device=DEV)
        s.recusa = torch.zeros(B, dtype=torch.bool, device=DEV); s.ARB = torch.arange(B, device=DEV)
        s.n_agua = torch.zeros(B, device=DEV); s.parado_dia = torch.zeros(B, device=DEV); s.imp = torch.zeros(B, device=DEV); s.subs = torch.zeros(B, device=DEV)   # [E44] sentidos do prefeito; subs = subsidio pago
        s.pref_mult = torch.ones(s.NC, 6, device=DEV)     # [E44] alavancas do prefeito por mapa: aliq, p_fuel, p_agua, p_comida, aluguel, tarifa (1 = mapa)
    # --- geometria
    def custo_em(s, p):                       # p (B,...,2) -> custo (B,...)
        ix = (p[..., 0]/s.L*(s.cfg.tex - 1)).round().long().clamp(0, s.cfg.tex - 1); iy = (p[..., 1]/s.L*(s.cfg.tex - 1)).round().long().clamp(0, s.cfg.tex - 1)
        ci = s.cidx.view(-1, *([1]*(p.dim()-2))).expand(p.shape[:-1])
        return s.custo_tex[ci, iy, ix]
    def _cel(s, p):                              # indices de grade (iy, ix) e cidx expandido
        ix = (p[..., 0]/s.L*GR).long().clamp(0, GR - 1); iy = (p[..., 1]/s.L*GR).long().clamp(0, GR - 1)
        ci = s.cidx.view(-1, *([1]*(p.dim()-2))).expand(p.shape[:-1]); return ci, iy, ix
    def distrito(s, p):                        # (B,...,2) -> (B,...) long  [campo pre-computado]
        ci, iy, ix = s._cel(p); return s.campo_dist[ci, iy, ix]
    def d_serv(s, t, p):                        # EXATA (so na posicao atual, p (B,2)): raio de uso do servico
        ci = s.cidx; pts = s.serv[t][ci]; msk = s.serv_msk[t][ci]
        d = (p[:, None, :] - pts).norm(dim=-1).masked_fill(~msk, 1e9); return d.min(-1).values
    def _perto_todos(s, p):                      # ponto mais perto e distancia, por tipo (ordem TIPOS): (B,5,2), (B,5) — 5 varreduras por passo, nao 15
        ci = s.cidx; ar = torch.arange(p.shape[0], device=DEV); P = []; D = []
        for t in TIPOS:
            pts = s.serv[t][ci]; msk = s.serv_msk[t][ci]
            d = (p[:, None, :] - pts).norm(dim=-1).masked_fill(~msk, 1e9); k = d.argmin(-1)
            P.append(pts[ar, k]); D.append(d[ar, k])
        return torch.stack(P, 1), torch.stack(D, 1)
    def _perto(s, p, n):                        # n pontos por ser num anel [8, raio_px] em volta de p (B,2) -> (B,n,2)
        B = p.shape[0]; ang = torch.rand(B, n, generator=s.g, device=DEV)*2*math.pi; r = 8. + (s.cfg.raio_px - 8.)*torch.rand(B, n, generator=s.g, device=DEV)
        return (p[:, None, :] + torch.stack([r*torch.cos(ang), r*torch.sin(ang)], -1)).clamp(0., s.L)
    def _destino(s, po):                        # destino do passageiro: prob ~ 1/(1+d) via ruido, >=30% outro distrito (aprox: raio aleatorio grande)
        B, N, _ = po.shape
        ang = torch.rand(B, N, generator=s.g, device=DEV)*2*math.pi
        r = s.L*(.05 + .45*torch.rand(B, N, generator=s.g, device=DEV)**2)                  # concentra perto, cauda longa
        d = po + torch.stack([r*torch.cos(ang), r*torch.sin(ang)], -1)
        return d.clamp(0., s.L)
    def construir(s, t, quer):                  # [E44] abre 1 ponto do tipo t (posicao aleatoria) nos mapas com quer=True, no proximo slot livre
        NC = s.NC; msk = s.serv_msk[t]; livre = (~msk).float(); tem = livre.sum(1) > 0
        k = livre.argmax(1); faz = quer & tem; ar = torch.arange(NC, device=DEV)
        if not hasattr(s, 'g_pref'): s.g_pref = torch.Generator(device=DEV); s.g_pref.manual_seed(99991 + s.NC)   # gerador PROPRIO (semente fixa, sem ler tensor): nao consome o fluxo do mundo
        novo = torch.rand(NC, 2, generator=s.g_pref, device=DEV)*s.L
        s.serv[t][ar, k] = torch.where(faz[:, None], novo, s.serv[t][ar, k]); s.serv_msk[t][ar, k] = msk[ar, k] | faz
    def hora(s):  return ((s.t.float() + s.fase) % s.cfg.dia)/s.cfg.dia*24.
    def noite_(s):
        h = s.hora(); return (h >= 22.) | (h < 6.)
    def capf(s):  return torch.full_like(s.fuel, 100.)
    def alvo(s):                                # (B,2) destino se carrega, senao passageiro mais perto
        dpx = (s.px - s.pos[:, None, :]).norm(dim=-1); k = dpx.argmin(1)
        po = s.px[torch.arange(s.B, device=DEV), k]
        return torch.where((s.pd_ >= 0)[:, None], s.dest, po)
    # --- sentidos
    def obs(s):
        c = s.cfg; nv = s.noite_(); v = torch.where(nv, c.vel_noite, c.vel)
        pn = (s.pos[:, None, :] + v[:, None, None]*s.dirs[None, :, :]).clamp(0., s.L)          # (B,G,2)
        alvo = s.alvo(); esc = 1./c.vel                                                        # [G3] distancias em unidades andadas (o terreno nao sequestra o volante)
        F = [ (pn - alvo[:, None, :]).norm(dim=-1)*esc ]
        # distancia EXATA de cada opcao ao ponto mais perto (achado na posicao atual, UMA vez por passo; serv_ab/passo reusam) [G7]
        s._ptos, s._dist = s._perto_todos(s.pos)                                                # (B,5,2), (B,5) na ordem TIPOS
        for j in (0, 1, 2, 4, 3):
            F.append((pn - s._ptos[:, j][:, None, :]).norm(dim=-1)*esc)
        F.append(s.custo_em(pn)); dn = s.distrito(pn); ci = s.cidx[:, None].expand(-1, G)
        F.append(s.pmul[ci, dn]); F.append(s.aliq[ci, dn]); F.append((dn == s.casa[:, None]).float())
        Fop = torch.stack(F, -1)                                                                 # (B,G,10)
        h = s.hora()*2*math.pi/24.
        corpo = torch.stack([s.fuel/100., s.agua/100., s.fome/100., s.fad/100., s.calor/120., s.vida/100., (s.dinh/150.).clamp(-1., 1.), s.res/c.RES_MAX,
                             (s.pd_ >= 0).float(), torch.sin(h), torch.cos(h), nv.float(), s.custo_em(s.pos), torch.ones_like(s.fuel)], -1)   # (B,14)
        Fo = torch.cat([Fop, corpo[:, None, :].expand(-1, G, -1)], -1)
        val = torch.ones(s.B, G, dtype=torch.bool, device=DEV)
        return Fo, val
    def serv_ab(s):
        c = s.cfg; nv = s.noite_(); perto = {t: s._dist[:, j] <= c.raio for j, t in enumerate(TIPOS)}   # [G7] reusa a varredura do obs()
        if c.loja_no_posto:   # posto tem loja: vende comida e agua (o ser passa no posto 5x/vida e quase nunca num ponto de comida) — licao do grafo (comida_no_posto)
            perto['comida'] = perto['comida'] | perto['posto']; perto['agua'] = perto['agua'] | perto['posto'] | perto['comida']
        ci = s.cidx; d = s.distrito(s.pos); pm = s.pmul[ci, d]
        cols = []
        for t, q in ACOES:
            ok = perto[t]
            if t == 'posto': ok = ok & ~nv
            cols.append(ok.float())
        return torch.stack(cols, 1), pm
    def custos(s, pm):                            # custo em dinheiro de cada acao (B,S)
        c = s.cfg; casa = (s.distrito(s.pos) == s.casa).float(); pf = s.pref_mult[s.cidx]   # (B,6)
        cs = []
        for t, q in ACOES:
            if t == 'posto': cs.append(c.preco_L*q*pm*pf[:, 1])
            elif t == 'agua': cs.append(c.preco_agua*q*pm*pf[:, 2])
            elif t == 'comida': cs.append(c.preco_comida*pm*pf[:, 3])
            elif t == 'descanso': cs.append((1. - casa)*c.HOTEL*pm)
            else: cs.append(c.preco_oficina*pm)
        return torch.stack(cs, 1)
    def serv_need(s):
        sv, pm = s.serv_ab(); cs = s.custos(pm); paga = (s.dinh[:, None] >= cs).float()
        cabe = (100. - s.fuel); sobra_res = (s.cfg.RES_MAX - s.res).clamp(min=0.)
        nec_posto = [torch.minimum(torch.full_like(cabe, q), cabe)/100. + (torch.minimum(torch.full_like(cabe, q) - cabe, sobra_res).clamp(min=0.)/100.)*.5 for q in (25., 50., 75., 100., 150.)]
        nec = torch.stack(nec_posto + [torch.minimum(torch.full_like(cabe, q), 100. - s.agua)/100. for q in (50., 100.)] + [s.fome/100., s.fad/100., (1 - s.vida/100.)], 1)   # [G4]
        return sv*nec*paga, sv*paga
    # --- fisica
    def passo(s, esc):
        c = s.cfg; B = s.B; s.t += 1
        vivo = s.vida > 0; livre = (s.tpar <= 0) & vivo; s.tpar = (s.tpar - 1).clamp(min=0)
        nv = s.noite_(); v = torch.where(nv, c.vel_noite, c.vel)
        mov = livre & (esc < G) & (esc != G - 1)
        d = s.dirs[esc.clamp(max=G-1)]                                       # (B,2)
        cu = s.custo_em(s.pos); peso = 1. + .15*(s.pd_ >= 0).float() + .002*s.res
        falta = mov & (s.fuel < c.fuel_passo*cu*peso)                         # pane: nao consegue andar
        pane = falta
        mov = mov & ~falta
        s.pos = (s.pos + mov[:, None].float()*v[:, None]*d).clamp(0., s.L)
        marcha = livre & ~mov                                                    # [G2] parado com motor ligado: marcha lenta gasta 1/3
        s.fuel = (s.fuel - c.fuel_passo*cu*peso*mov.float() - c.fuel_passo*.33*marcha.float()).clamp(min=0.)
        s.calor = (s.calor + c.calor_sobe*cu*mov.float() - c.calor_desce*(~mov).float()).clamp(25., 120.)
        s.agua = (s.agua - c.agua_passo*vivo.float() - c.agua_calor*(s.calor > 60.).float()*vivo.float()).clamp(min=0.)
        s.fome = (s.fome + c.fome_passo*vivo.float()).clamp(max=100.); s.fad = (s.fad + c.fad_passo*mov.float() - .1*(~mov).float()).clamp(0., 100.)
        exausto = livre & (s.fad >= 95.); s.tpar = torch.where(exausto, torch.full_like(s.tpar, 12.), s.tpar); s.fad = torch.where(exausto, torch.full_like(s.fad, 40.), s.fad); s.avar += exausto.float()   # [G6] fadiga para o taxi
        s.res = (s.res*(1. - c.perda_res)).clamp(min=0.)
        # pane: reboque ate o posto mais perto, cobra calorias da reserva -> vida
        s.avar += pane.float(); s.av_fuel += pane.float(); s.tpar = torch.where(pane, torch.full_like(s.tpar, 18.), s.tpar)
        ci = s.cidx; posto_pos = s._ptos[:, 0]                                    # [auditoria 7] posto mais perto ja calculado no obs() (quem entra em pane nao moveu)
        s.pos = torch.where(pane[:, None], posto_pos, s.pos); s.fuel = torch.where(pane, torch.full_like(s.fuel, 15.), s.fuel)
        kcal = torch.minimum(s.res, torch.full_like(s.res, c.KCAL_PANE)); s.res = s.res - kcal*pane.float()
        dn = c.D_PANE*pane.float() + (c.KCAL_PANE - kcal)*pane.float()
        # calor: desliga
        qt = livre & (s.calor > c.CALOR_MAX); s.avar += qt.float(); s.tpar = torch.where(qt, torch.full_like(s.tpar, 10.), s.tpar)
        s.calor = torch.where(qt, torch.full_like(s.calor, 60.), s.calor); dn = dn + c.D_QUENTE*qt.float() + c.D_RODAR*(mov & (s.calor > 80.)).float()
        # servicos
        sv, pm = s.serv_ab(); cs = s.custos(pm); pode = livre & (esc >= G)
        k = (esc - G).clamp(0, S - 1); onehot = torch.nn.functional.one_hot(k, S).float()*pode[:, None].float()*sv
        paga = (s.dinh[:, None] >= cs).float(); usa = onehot*paga                                  # (B,S)
        s.dinh = s.dinh - (usa*cs).sum(1)
        pf_ = s.pref_mult[ci]; base_ = torch.stack([cs[:, k]/pf_[:, {'posto': 1, 'agua': 2, 'comida': 3}.get(ACOES[k][0], 0)] if ACOES[k][0] in ('posto', 'agua', 'comida') else cs[:, k] for k in range(S)], 1)
        s.subs = s.subs + (usa*(base_ - cs)).sum(1)                                                  # [E44 v2] caixa paga subsidio (mult<1) ou recebe sobretaxa (mult>1)
        litros = usa[:, 0]*25. + usa[:, 1]*50. + usa[:, 2]*75. + usa[:, 3]*100. + usa[:, 4]*150.
        abast = litros > 0; s.n_posto += abast.float(); s.litros += litros
        novo = s.fuel + litros; sobra = (novo - 100.).clamp(min=0.); s.fuel = novo.clamp(max=100.)
        s.res = (s.res + sobra*(1. - c.PERDA_ARMAZ)).clamp(max=c.RES_MAX)
        s.agua = (s.agua + usa[:, 5]*50. + usa[:, 6]*100.).clamp(max=100.); s.n_agua += ((usa[:, 5] + usa[:, 6]) > 0).float()
        come = usa[:, 7] > 0; s.fome = torch.where(come, (s.fome - c.REFEICAO).clamp(min=0.), s.fome); s.n_come += come.float()
        desc = usa[:, 8] > 0; s.fad = torch.where(desc, torch.minimum(s.fad, torch.full_like(s.fad, 40.)), s.fad); s.tpar = torch.where(desc, torch.full_like(s.tpar, 12.), s.tpar)   # [G6] descanso nunca aumenta fadiga
        ofi = usa[:, 9] > 0; s.vida = torch.where(ofi, (s.vida + c.REPARO).clamp(max=100.), s.vida); s.calor = torch.where(ofi, torch.full_like(s.calor, 25.), s.calor); s.n_oficina += ofi.float()
        # passageiros: embarque (raio) e entrega
        dpx = (s.px - s.pos[:, None, :]).norm(dim=-1).masked_fill(~s.px_ok, 1e9); kx = dpx.argmin(1); ar = s.ARB
        pega = livre & (s.pd_ < 0) & (dpx[ar, kx] <= c.raio) & ~s.recusa & ~pode
        s.dest = torch.where(pega[:, None], s.pxd[ar, kx], s.dest); s.emb = torch.where(pega[:, None], s.pos, s.emb)
        s.orig_d = torch.where(pega, s.distrito(s.pos), s.orig_d); s.pd_ = torch.where(pega, torch.ones_like(s.pd_), s.pd_)
        novo_px = s._perto(s.pos, 1)[:, 0]; novo_d = s._destino(novo_px[:, None, :])[:, 0]
        s.px[ar, kx] = torch.where(pega[:, None], novo_px, s.px[ar, kx]); s.pxd[ar, kx] = torch.where(pega[:, None], novo_d, s.pxd[ar, kx])
        s.px_ok[ar, kx] = s.px_ok[ar, kx] & ~pega                                                   # slot usado fica inativo
        volta = torch.rand(B, c.NPX, generator=s.g, device=DEV) < (1./(20.*s.pref_mult[ci, 5]))[:, None]   # elasticidade: tarifa x2 = espera 2x
        s.px_ok = s.px_ok | volta
        cheg = livre & (s.pd_ >= 0) & ((s.pos - s.dest).norm(dim=-1) <= c.raio)
        pf = s.pref_mult[ci]; aliq = (s.aliq[ci, s.orig_d]*pf[:, 0]).clamp(0., .6)
        dist = (s.dest - s.emb).norm(dim=-1); bruta = (c.tarifa_base + c.tarifa_km*dist)*s.pmul[ci, s.orig_d]*pf[:, 5]; tarifa = bruta*(1. - aliq)
        s.dinh = s.dinh + tarifa*cheg.float(); s.rec += tarifa*cheg.float(); s.imp += bruta*aliq*cheg.float(); s.ent += cheg.float(); s.pd_ = torch.where(cheg, -torch.ones_like(s.pd_), s.pd_)
        # aluguel a meia-noite (distrito-casa)
        meia = ((s.t.float() + s.fase) % c.dia) < 1.; alug_base = c.aluguel*s.alug[ci, s.casa]; s.dinh = s.dinh - alug_base*s.pref_mult[ci, 4]*meia.float()*vivo.float()
        s.subs = s.subs + alug_base*(1. - s.pref_mult[ci, 4])*meia.float()*vivo.float()
        s.parado_dia = (s.parado_dia + (~mov & livre).float())*(1. - meia.float())
        # dano por fome / sede / divida
        dn = dn + c.fome_mata*((s.fome - c.FOME_CRIT)/(100. - c.FOME_CRIT)).clamp(0., 1.) + c.agua_mata*((c.AGUA_CRIT - s.agua)/c.AGUA_CRIT).clamp(0., 1.)
        s.dinh = s.dinh.clamp(min=-c.LIMITE_DIVIDA); dn = dn + 2.0*((-s.dinh)/c.LIMITE_DIVIDA).clamp(0., 1.)**2   # [G5] divida fere gradualmente; no limite 2/passo
        s.vida = (s.vida - dn*vivo.float()).clamp(min=0.); s.dano_soma += dn*vivo.float(); s.t_vida += vivo.float()
        if c.fitness == 'bemestar':
            s.bem_soma += vivo.float()*(s.vida/100. + (1. - s.fome/100.) + s.fuel/100. + s.agua/100. + (s.dinh/100.).clamp(0., 1.))/5.

def um_passo(m, a, Wb):
    F, val = m.obs()
    sc = torch.einsum('bgf,bf->bg', F, Wb[:, :NF]) + a.extra(m, Wb, F)
    sc = sc - sc.mean(1, keepdim=True)                                              # [G1] sem modo comum: o vies de servico e o unico arbitro mover-vs-servir
    svn, sv = m.serv_need(); ss = svn*Wb[:, NF:NF+S] + Wb[:, NF+S:NF+S+1]
    if hasattr(a, 'extra_serv'): ss = ss + a.extra_serv(m)
    ss = ss.masked_fill(sv <= 0, -1e9)
    tudo = torch.cat([sc, ss], 1)
    esc = a.decidir(tudo, m) if hasattr(a, 'decidir') else tudo.argmax(1)
    m.passo(esc)

class Linear:
    nome = 'linear-campo'; NP = NF + S + 1
    def reset(s, m, W): s.W = W
    def extra(s, m, W, F): return torch.zeros(m.B, G, device=DEV)
    def atualizar(s, m): pass

class Reflexo(Linear):
    """reflexo de emergencia do E29b, no campo: especie sede-de-gasolina c=1-fuel/100 (tau), portao theta, empurra pro posto (-w*a*d_posto por opcao)
    e ganho de servico no posto (v*a). Genes: tau, w, v, portao (nascem: tau rapido, w=0, v=0, portao 0.5) -> genes 0 == Linear."""
    nome = 'reflexo-campo'; NP = Linear.NP + 4
    def reset(s, m, W):
        s.W = W; o = Linear.NP; s.tau = 1. + 200.*torch.sigmoid(W[:, o] - 4.); s.w = W[:, o+1]; s.v = W[:, o+2]; s.theta = torch.sigmoid(W[:, o+3])
        s.c = torch.zeros(m.B, device=DEV)
    def _ativ(s): return (s.c - s.theta).clamp(min=0.)
    def extra(s, m, W, F):
        a = s._ativ()
        return -(s.w*a)[:, None]*F[:, :, 1]                         # F[...,1] = d_posto apos a opcao
    def extra_serv(s, m):
        a = s._ativ(); z = torch.zeros(m.B, S, device=DEV); z[:, :5] = (s.v*a)[:, None]; return z
    def atualizar(s, m):
        s.c = s.c + ((1. - m.fuel/100.) - s.c)/s.tau

def fabrica_minimo(permitidas):
    """politica minima: so os sentidos listados (por nome de NOMES_F) — os outros pesos sao zerados no reset."""
    idx = [NOMES_F.index(n) for n in permitidas]
    class Minimo(Linear):
        nome = f'minimo-{len(idx)}'
        def reset(s, m, W):
            msk = torch.zeros(NF, device=DEV); msk[idx] = 1.; s.msk = msk; s.W = W
        def extra(s, m, W, F):
            return -torch.einsum('bgf,bf->bg', F, W[:, :NF]*(1. - s.msk)[None, :])   # cancela os sentidos proibidos
    return Minimo

_PASSO_C = None; _COMPILE_OK = None
def _passo_fn():
    """[auditoria 1] torch.compile do passo do campo: 16.3 -> 2.3 ms/passo @65k; identidade compile x eager provada bit a bit. NM_COMPILE=0 desliga."""
    global _PASSO_C, _COMPILE_OK
    if os.environ.get('NM_COMPILE', '1') == '0' or DEV != 'cuda' or _COMPILE_OK is False: return um_passo
    if _PASSO_C is None:
        try:
            import torch._dynamo; torch._dynamo.config.cache_size_limit = 64
            _PASSO_C = torch.compile(um_passo, dynamic=False)
        except Exception:
            _COMPILE_OK = False; return um_passo
    return _PASSO_C

def modo_execucao():
    return 'eager' if (os.environ.get('NM_COMPILE', '1') == '0' or DEV != 'cuda' or _COMPILE_OK is False) else 'compile'

def rodar(Arq, W, mapas, cfg, T, seed, R=1):
    global _COMPILE_OK
    m = Campo(mapas, W.shape[0], cfg, seed=seed, R=R); Wb = W[m.gidx]; a = Arq(); a.reset(m, Wb); fn = _passo_fn()
    for t in range(T):
        try: fn(m, a, Wb)
        except Exception as e:
            if fn is not um_passo and t == 0:
                print(f'  [campo: compile falhou ({type(e).__name__}); refazendo em eager]', flush=True); _COMPILE_OK = False
                return rodar(Arq, W, mapas, cfg, T, seed, R=R)
            raise
        a.atualizar(m)
    return m

def _fit(m, cfg, T):
    morto = (m.vida <= 0).float(); vivo = 1. - morto
    tarde = morto*(0.5*m.t_vida/float(T) + 0.05*m.ent + 0.02*(m.n_come + m.n_agua + m.n_posto).clamp(max=10.))   # [G2] gradiente entre mortos que a PEDRA nao maximiza
    if cfg.fitness == 'sobrevive':
        fit = vivo*(1. + m.vida/100. + (m.dinh/100.).clamp(0., 1.) + 0.05*m.ent + 0.5*m.res/cfg.RES_MAX) - cfg.pena_morte*morto + tarde
    elif cfg.fitness == 'bemestar':
        fit = m.bem_soma/float(T) + 0.05*m.ent - cfg.pena_morte*morto + tarde
    else:   # padrao (entregas)
        fit = m.ent - 0.3*m.avar - cfg.pena_morte*morto + tarde
    return fit

def avaliar(Arq, W, mapas, cfg, T, seed=0, R=1):
    m = rodar(Arq, W, mapas, cfg, T, seed, R=R)
    return _fit(m, cfg, T).view(W.shape[0], m.NC*m.R).mean(1)

def evoluir(Arq, mapas, cfg, **kw):
    return evoluir_sementes(Arq, mapas, cfg, avaliar_fn=avaliar, **kw)

def medidas(Arq, W, mapas, cfg, T=1200, seed=7777, R=1, copias=128):
    m = rodar(Arq, W[None, :].repeat(copias, 1), mapas, cfg, T, seed, R=R); morto = (m.vida <= 0).float()
    med = dict(fit=float(_fit(m, cfg, T).mean()), mortos=float(morto.mean()), ent=float(m.ent.mean()),
               panes=float(m.av_fuel.mean()), fome_fim=float(m.fome.mean()), agua_fim=float(m.agua.mean()), dinh=float(m.dinh.mean()), res=float(m.res.mean()),
               litros_por_abast=float((m.litros/m.n_posto.clamp(min=1)).mean()), n_posto=float(m.n_posto.mean()), n_come=float(m.n_come.mean()), oficina=float(m.n_oficina.mean()),
               vida_vivos=float(m.vida[m.vida > 0].mean()) if bool((m.vida > 0).any()) else 0.)
    return med


class Produto(Linear):
    """politica bilinear (E17/E29b no campo): nota da opcao g = linear + sum_k -w_k * relu(need_k - theta_k) * d_k(g).
    needs: fuel, agua, fome (deficits) e 'alvo' (sempre 1). Genes: w (4) e theta (3, sigmoid) -> 7. Genes 0 == Linear (w=0)."""
    nome = 'produto-campo'; NP = Linear.NP + 7
    IDX_D = torch.tensor([1, 3, 2, 0], device=DEV)          # d_posto, d_agua, d_comida, d_alvo (tensor: sem sync) [G8]
    def reset(s, m, W):
        s.W = W; o = Linear.NP; s.w = W[:, o:o+4]; s.theta = torch.sigmoid(W[:, o+4:o+7])
    def extra(s, m, W, F):
        need = torch.stack([1. - m.fuel/100., 1. - m.agua/100., m.fome/100.], 1)            # (B,3)
        a = (need - s.theta).clamp(min=0.)                                                 # portao por necessidade
        g = torch.cat([a, torch.ones(m.B, 1, device=DEV)], 1)*s.w                          # (B,4)
        D = F.index_select(2, s.IDX_D)                                                     # (B,G,4)
        return -(D*g[:, None, :]).sum(-1)


def rodar_com_prefeito(Arq, W, mapas, cfg, T, seed, R=1, Wp=None, prefeito_cls=None):
    """como rodar(), mas com um prefeito por mapa agindo a cada dia (t % dia == 0). Wp=None -> identico a rodar()."""
    m = Campo(mapas, W.shape[0], cfg, seed=seed, R=R); Wb = W[m.gidx]; a = Arq(); a.reset(m, Wb); fn = _passo_fn()
    pref = prefeito_cls(m, Wp) if Wp is not None else None
    for t in range(T):
        if pref is not None and t > 0 and t % cfg.dia == 0:
            pref.receita(m.imp); pref.agir(t//cfg.dia)
        fn(m, a, Wb); a.atualizar(m)
    return m, pref


class Modos(Linear):
    """E46 MODOS GAUSSIANOS (ideia do Leonardo: 'gaussiana com 3 direcoes; depende de onde voce observa'): K gaussianas no espaco
    das necessidades (tanque, agua, fome, dinheiro, tem_pax) com centro mu_k, largura por eixo (3 eixos principais: log-sigma) e um
    VETOR DE PESOS DE MOVIMENTO proprio dW_k. nota(g) = F.W + sum_k r_k(x) * F.dW_k, r = softmax das log-densidades * ganho.
    Nasce == Linear: dW=0 (regra 17). Genes: K*(5 centro + 3 sigma + NF pesos) + 1 ganho."""
    nome = 'modos-campo'; K = 3; NEED = 5
    NP = Linear.NP + K*(NEED + 3 + NF) + 1
    def reset(s, m, W):
        s.W = W; o = Linear.NP; K = s.K; n = s.NEED
        s.mu = W[:, o:o+K*n].view(-1, K, n)*.5 + .5                          # centros ~ [0,1] (genes 0 -> centro 0.5)
        o += K*n; s.ls = W[:, o:o+K*3].view(-1, K, 3)                          # log-sigma dos 3 eixos (0 -> sigma 1)
        o += K*3; s.dW = W[:, o:o+K*NF].view(-1, K, NF)                        # pesos de movimento por modo (0 -> identico ao linear)
        o += K*NF; s.ganho = torch.nn.functional.softplus(W[:, o] + 1.)         # ganho da mistura
    def _x(s, m):
        return torch.stack([m.fuel/100., m.agua/100., m.fome/100., (m.dinh/100.).clamp(0., 1.), (m.pd_ >= 0).float()], 1)   # (B,5)
    def extra(s, m, W, F):
        x = s._x(m)                                                            # (B,5)
        d = x[:, None, :] - s.mu                                                # (B,K,5)
        # 3 eixos: (fuel,agua) / (fome,dinh) / (pax) — cada eixo com sua largura
        q = (d[..., 0]**2 + d[..., 1]**2)*torch.exp(-2*s.ls[..., 0]) + (d[..., 2]**2 + d[..., 3]**2)*torch.exp(-2*s.ls[..., 1]) + d[..., 4]**2*torch.exp(-2*s.ls[..., 2])
        r = torch.softmax(-.5*q, 1)*s.ganho[:, None]                           # (B,K) responsabilidade de cada modo
        Wm = torch.einsum('bk,bkf->bf', r, s.dW)                                # (B,NF) pesos extras "vistos de onde o ser esta"
        return torch.einsum('bgf,bf->bg', F, Wm)
    def ativacao(s, m):
        x = s._x(m); d = x[:, None, :] - s.mu
        q = (d[..., 0]**2 + d[..., 1]**2)*torch.exp(-2*s.ls[..., 0]) + (d[..., 2]**2 + d[..., 3]**2)*torch.exp(-2*s.ls[..., 1]) + d[..., 4]**2*torch.exp(-2*s.ls[..., 2])
        return torch.softmax(-.5*q, 1)


class Comite(Modos):
    """E48 COMITE (Leonardo: 'rodar todos os tipos de cerebro num ser'; 'andar 4 ticks pra comida e depois voltar pra agua'):
    Modos gaussianos com K modos e INERCIA — a responsabilidade e um EMA com tau (gene): o ser se compromete a um modo por trechos.
    Os dW_k nascem dos campeoes (W_k - W_media) via W0; genes de portao/tau nascem em 0 (tau -> 1 = sem inercia = Modos)."""
    nome = 'comite-campo'; K = 4; NEED = 5
    NP = Linear.NP + K*(NEED + 3 + NF) + 1 + 1          # + tau
    def reset(s, m, W):
        Modos.reset(s, m, W); s.tau = 1. + 30.*torch.sigmoid(W[:, -1] - 3.)   # gene 0 -> tau 1.4 (quase sem inercia); gene 4 -> ~23 ticks
        s.r = torch.full((m.B, s.K), 1./s.K, device=DEV)
    def _resp(s, m):
        x = s._x(m); d = x[:, None, :] - s.mu
        q = (d[..., 0]**2 + d[..., 1]**2)*torch.exp(-2*s.ls[..., 0]) + (d[..., 2]**2 + d[..., 3]**2)*torch.exp(-2*s.ls[..., 1]) + d[..., 4]**2*torch.exp(-2*s.ls[..., 2])
        return torch.softmax(-.5*q, 1)
    def extra(s, m, W, F):
        Wm = torch.einsum('bk,bkf->bf', s.r*s.ganho[:, None], s.dW)          # usa a responsabilidade COM inercia (estado)
        return torch.einsum('bgf,bf->bg', F, Wm)
    def atualizar(s, m):
        s.r = s.r + (s._resp(m) - s.r)/s.tau[:, None]                         # in-place fora do grafo: compromisso por trechos
    def ativacao(s, m): return s.r

def W0_comite(campeoes):
    """monta o genoma inicial do comite a partir de K campeoes lineares (NP=Linear.NP): parte linear = media; dW_k = W_k - media."""
    Wk = torch.stack([torch.as_tensor(w, dtype=torch.float32, device=DEV)[:Linear.NP] for w in campeoes]); K = Wk.shape[0]
    med = Wk.mean(0); W = torch.zeros(Comite.NP, device=DEV); W[:Linear.NP] = med
    o = Linear.NP + K*Comite.NEED + K*3
    W[o:o+K*NF] = (Wk[:, :NF] - med[:NF]).reshape(-1)                        # so os pesos de MOVIMENTO diferem por modo (servicos ficam na media)
    return W


class ProdutoTrend(Produto):
    """E49 OLHO MULTI-ESCALA (Leonardo: saci-trader M1/M5/M15/M30 = banco de tau): cada necessidade e vista em 3 escalas
    (agora, media de 64 passos, media de 512) e entra no produto como need_ef = need + a*(need - e64) + b*(e64 - e512).
    a,b = genes por necessidade (3 needs -> 6 genes), nascem em 0 == Produto. EMAs atualizadas in-place em atualizar()."""
    nome = 'produto-trend'; NP = Produto.NP + 6
    def reset(s, m, W):
        Produto.reset(s, m, W); o = Produto.NP; s.a = W[:, o:o+3]; s.b = W[:, o+3:o+6]
        s.e64 = s._need(m).clone(); s.e512 = s.e64.clone()
    def _need(s, m): return torch.stack([1. - m.fuel/100., 1. - m.agua/100., m.fome/100.], 1)
    def extra(s, m, W, F):
        need = s._need(m); need_ef = need + s.a*(need - s.e64) + s.b*(s.e64 - s.e512)
        a = (need_ef - s.theta).clamp(min=0.)
        g = torch.cat([a, torch.ones(m.B, 1, device=DEV)], 1)*s.w
        D = F.index_select(2, s.IDX_D)
        return -(D*g[:, None, :]).sum(-1)
    def atualizar(s, m):
        n = s._need(m); s.e64 = s.e64 + (n - s.e64)/64.; s.e512 = s.e512 + (n - s.e512)/512.
    def ativacao(s, m):
        n = s._need(m); return torch.cat([n - s.e64, s.e64 - s.e512], 1)


class ReflexoRaizes(Reflexo):
    """E50 REFLEXO COM DUAS RAIZES (Leonardo: 'Bhaskara da dois resultados'): a parabola a(c - r1)(c - r2) e negativa ENTRE as
    raizes. Liga quando a sede c passa de r2 (= portao theta), e so DESLIGA quando c cai abaixo de r1 = theta - largura
    (histerese/termostato). Gene extra = largura (softplus(g - 4): nasce ~0 => r1 = r2 = theta == Reflexo bit a bit).
    Estado 'ligado' atualizado em atualizar() (fora do grafo)."""
    nome = 'reflexo-raizes'; NP = Reflexo.NP + 1
    def reset(s, m, W):
        Reflexo.reset(s, m, W); s.larg = torch.nn.functional.softplus(W[:, -1] - 4.)   # largura da banda entre as raizes
        s.ligado = torch.zeros(m.B, device=DEV)
    def _ativ(s):
        # intensidade: quando ligado, a ativacao vale (c - r1) (continua positiva ate cruzar r1); quando desligado, (c - r2)+
        return torch.where(s.ligado > 0, (s.c - (s.theta - s.larg)).clamp(min=0.), (s.c - s.theta).clamp(min=0.))
    def atualizar(s, m):
        Reflexo.atualizar(s, m)
        r1 = s.theta - s.larg; r2 = s.theta
        s.ligado = torch.where(s.c > r2, torch.ones_like(s.ligado), torch.where(s.c < r1, torch.zeros_like(s.ligado), s.ligado))
