"""E44 PREFEITO (doc 45): um por mapa. Sente agregados da cidade uma vez por dia (tensores, sem sync), mexe em alavancas por
distrito (aliquota, preco da gasolina/agua/comida, aluguel, tarifa) e CONSTROI servicos com o caixa. Pago por bem-estar da
cidade (regua B agregada), caixa como restricao. Nasce fazendo NADA (regra 17). Co-evolucao: ver evoluir_com_prefeito."""
import math, torch
from lab import DEV
import campo as C

SENT = ['mortos', 'm_fome', 'm_sede', 'm_pane', 'm_divida', 'fome', 'agua', 'fuel', 'vida', 'dinh', 'quebrados', 'ent_dia', 'uso_posto', 'uso_agua', 'uso_comida', 'parado', 'caixa', 'dia', 'bias']
NS = len(SENT)
ALAV = ['aliq', 'p_fuel', 'p_agua', 'p_comida', 'aluguel', 'tarifa', 'constroi_agua', 'constroi_comida', 'constroi_posto']
NA = len(ALAV)
class Prefeito:
    """genes: W (NS x NA) + memoria de ontem (NS) -> NP = NS*NA + NS. Alavancas sao MULTIPLICADORES em torno do mapa (exp(tanh(.)*log 2)):
    x0.5 .. x2 por dia, acumulando; construir = probabilidade sigmoid(.) de abrir um ponto no distrito com pior sentido, pagando do caixa."""
    NP = NS*NA + NS
    def __init__(s, m, Wp, custo_obra=60.):
        s.m = m; s.NC = m.NC; s.Wp = Wp                       # (NC, NP)
        s.W = Wp[:, :NS*NA].view(s.NC, NS, NA); s.Wmem = Wp[:, NS*NA:]
        s.ontem = torch.zeros(s.NC, NS, device=DEV); s.caixa = torch.zeros(s.NC, device=DEV); s.custo_obra = custo_obra
        s.mult = torch.ones(s.NC, 6, device=DEV)              # multiplicadores acumulados por alavanca continua (por mapa; v1 sem distrito)
        s.mortos_ontem = torch.zeros(s.NC, device=DEV); s.ent_ontem = torch.zeros(s.NC, device=DEV)
        s.obras = torch.zeros(s.NC, 3, device=DEV); s.hist = []
        s.imp_ontem = torch.zeros(s.NC, device=DEV)
    def sentir(s, dia):
        m = s.m; ci = m.cidx; NC = s.NC
        def media(x): return torch.zeros(NC, device=DEV).index_add_(0, ci, x)/torch.zeros(NC, device=DEV).index_add_(0, ci, torch.ones_like(x)).clamp(min=1)
        vivo = (m.vida > 0).float(); morto = 1. - vivo
        fome_m = morto*(m.fome >= 90).float(); sede_m = morto*(m.agua <= 10).float(); pane_m = morto*(m.av_fuel > 0).float(); div_m = morto*(m.dinh <= -50).float()
        ent_dia = m.ent - s.ent_ontem[ci]
        X = torch.stack([media(morto), media(fome_m), media(sede_m), media(pane_m), media(div_m), media(m.fome)/100., media(m.agua)/100., media(m.fuel)/100., media(m.vida)/100.,
                         media(m.dinh.clamp(-100., 200.))/100., media((m.dinh < 5.).float()), media(ent_dia), media(m.n_posto)/5., media(m.n_agua)/5., media(m.n_come)/5.,
                         media(m.parado_dia)/240., s.caixa/200., torch.full((NC,), dia/5., device=DEV), torch.ones(NC, device=DEV)], 1)   # (NC,NS)
        s.ent_ontem = torch.zeros(NC, device=DEV).index_add_(0, ci, m.ent)/torch.zeros(NC, device=DEV).index_add_(0, ci, torch.ones_like(m.ent)).clamp(min=1)
        return X
    def agir(s, dia):
        m = s.m; X = s.sentir(dia)
        u = torch.einsum('cs,csa->ca', X, s.W) + torch.einsum('cs,cs->c', s.ontem, s.Wmem)[:, None]*0.   # (NC,NA)  (memoria: v2)
        s.ontem = X
        passo = torch.exp(torch.tanh(u[:, :6])*math.log(2.)/4.)          # ate x1.19 por dia (acumula ate x0.5..x2 em ~4 dias)
        s.mult = (s.mult*passo).clamp(.5, 2.)
        m.pref_mult = s.mult                                             # o campo le: aliq, p_fuel, p_agua, p_comida, aluguel, tarifa
        # construir: sigmoid(u) > .5 e caixa >= custo -> abre 1 ponto do tipo, num distrito sorteado ponderado pela pior carencia (v1: uniforme)
        for k, t in enumerate(('agua', 'comida', 'posto')):
            quer = (torch.sigmoid(u[:, 6+k]) > .5) & (s.caixa >= s.custo_obra)
            s.caixa = s.caixa - s.custo_obra*quer.float(); s.obras[:, k] += quer.float()
            m.construir(t, quer)
        s.hist.append((int(dia), s.mult.detach().clone(), s.obras.detach().clone()))
    N_REF = 16.        # [E44 v2] caixa PER CAPITA: a cidade e de 16 taxis; P*R copias do mesmo genoma nao sao 2048 contribuintes
    def receita(s, imposto_total):
        """imposto arrecadado no mapa desde ontem entra no caixa, MENOS o subsidio pago (mult<1) — tudo normalizado per capita"""
        m = s.m; ci = m.cidx; n_por_mapa = torch.zeros(s.NC, device=DEV).index_add_(0, ci, torch.ones_like(imposto_total)).clamp(min=1)
        tot = torch.zeros(s.NC, device=DEV).index_add_(0, ci, imposto_total - m.subs)*(s.N_REF/n_por_mapa)
        s.caixa = s.caixa + (tot - s.imp_ontem); s.imp_ontem = tot
    def fitness(s):
        """bem-estar agregado da cidade (regua B) — o prefeito e pago por isso; caixa e restricao, nao objetivo"""
        m = s.m; ci = m.cidx; NC = s.NC
        def media(x): return torch.zeros(NC, device=DEV).index_add_(0, ci, x)/torch.zeros(NC, device=DEV).index_add_(0, ci, torch.ones_like(x)).clamp(min=1)
        morto = (m.vida <= 0).float()
        return media(m.bem_soma/1200. + 0.05*m.ent - 5.*morto + morto*m.t_vida/1200.)

def evoluir_prefeitos(Wp, fit, g, elite=.5, sigma=.3):
    """selecao entre mapas: os NC prefeitos competem; metade melhor sobrevive, a outra metade nasce de mutacao dos melhores."""
    NC = Wp.shape[0]; o = fit.argsort(descending=True); ne = max(1, int(NC*elite))
    Wb = Wp[o]; idx = torch.randint(0, ne, (NC - ne,), generator=g, device=DEV)
    fil = (Wb[idx] + torch.randn(NC - ne, Wp.shape[1], generator=g, device=DEV)*sigma).clamp(-5, 5)
    return torch.cat([Wb[:ne], fil])


def coevoluir(Arq, mapas, cfg, P=512, ger=25, T=1200, seeds=(0,), R=4, Wp0=None, cada=5, elite_p=.5, sigma_p=.3, verbose=False, W0=None):
    """2 populacoes: seres (evoluir_sementes do lab, avaliados com o prefeito de cada mapa agindo) e prefeitos (um por mapa,
    selecionados entre mapas a cada `cada` geracoes pelo bem-estar da propria cidade). Devolve (campeoes dos seres, Wp final, historico)."""
    from lab import evoluir_sementes
    NC = len(mapas); g = torch.Generator(device=DEV); g.manual_seed(4242)
    est = {'Wp': Wp0 if Wp0 is not None else torch.zeros(NC, Prefeito.NP, device=DEV), 'fit_pref': torch.zeros(NC, device=DEV), 'n': 0, 'hist': []}
    def avaliar_fn(A, W, cid, c, T_, seed=0, R_=1, R=None):
        R_ = R if R is not None else R_
        m, pref = C.rodar_com_prefeito(A, W, cid, c, T_, seed, R=R_, Wp=est['Wp'], prefeito_cls=Prefeito)
        est['fit_pref'] = est['fit_pref'] + pref.fitness(); est['n'] += 1
        est['ultimo'] = pref
        return C._fit(m, c, T_).view(W.shape[0], m.NC*m.R).mean(1)
    def cfg_gen(it, ger_):
        if it > 0 and it % cada == 0 and est['n'] > 0:
            f = est['fit_pref']/est['n']; est['hist'].append((it, f.tolist(), est['ultimo'].mult.tolist(), est['ultimo'].obras.tolist()))
            est['Wp'] = evoluir_prefeitos(est['Wp'], f, g, elite=elite_p, sigma=sigma_p); est['fit_pref'] = torch.zeros(NC, device=DEV); est['n'] = 0
        return cfg
    champs = evoluir_sementes(Arq, mapas, cfg, P=P, ger=ger, T=T, seeds=seeds, R=R, verbose=verbose, cfg_gen=cfg_gen, avaliar_fn=avaliar_fn, W0=W0)
    return champs, est['Wp'], est['hist']
