"""Autopsia: roda um campeao (W do JSON do runner) nas cidades de teste e registra o ESTADO no instante da morte.
Uso: NM_COMPILE=0 python src/autopsia.py <json> "<braco>" <seed_do_W> [Arq=Reativo|ReativoReacoes]"""
import sys, json, torch
from lab import Reativo, Lote, um_passo, gerar_cidade, DEV
from e19_pacote import cfg_pacote
from reacoes import ReativoReacoes
from lab import GMAX
FORCA = float(sys.argv[5]) if len(sys.argv) > 5 else 0.   # fome a partir da qual COMER e forcado (0 = desligado)
def _decidir(s, tudo, m):
    esc = tudo.argmax(1)
    if FORCA:
        _, sv = m.serv_need()
        forca = (m.fome >= FORCA) & (sv[:, 1] > 0) & (m.dinh >= 3.)
        esc = torch.where(forca, torch.full_like(esc, GMAX+1), esc)
    return esc
class ReativoF(Reativo): decidir = _decidir
class ReacoesF(ReativoReacoes): decidir = _decidir
ARQS = {'Reativo': ReativoF, 'ReativoReacoes': ReacoesF}
path, braco, sd = sys.argv[1], sys.argv[2], sys.argv[3]; A = ARQS[sys.argv[4] if len(sys.argv) > 4 else 'Reativo']
W = torch.tensor(json.load(open(path))['bracos'][braco]['W'][sd], device=DEV)[None, :]
c = cfg_pacote(fome=.15, refeicao=90., comida_no_posto=True)
teste = [gerar_cidade(1000 + s) for s in range(3)]
m = Lote(teste, 1, c, seed=1000, R=64); Wb = W[m.gidx]; a = A(); a.reset(m, Wb)
T = 1200; vivo = torch.ones(m.B, dtype=torch.bool, device=DEV); reg = []
passou = torch.zeros(m.B, device=DEV); comeu = torch.zeros(m.B, device=DEV); passou_pax = torch.zeros(m.B, device=DEV)
from lab import NF
gap_pax=[]; gap_solo=[]; venceu=torch.zeros(2, device=DEV); conta=torch.zeros(2, device=DEV)
for t in range(T):
    fome0 = m.fome.clone()
    if t % 4 == 0:   # placar comer vs andar (so leitura; obs() e pura)
        F, val = m.obs(); viz = m.A_().clamp(min=0)
        sc = torch.einsum('bgf,bf->bg', F, Wb[:, :NF]) + a.extra(m, Wb, viz); sc = sc.masked_fill(~val, -1e9)
        svn, sv = m.serv_need(); ss = svn*Wb[:, NF:NF+5] + Wb[:, NF+5:NF+6]
        if hasattr(a, 'extra_serv'): ss = ss + a.extra_serv(m)
        aqui = (fome0 >= 70) & vivo & (sv[:, 1] > 0) & (m.rest <= 0) & (m.tpar <= 0)
        gap = ss[:, 1] - sc.max(1).values
        pax = (m.pd_ >= 0)
        for k, sel in enumerate((aqui & ~pax, aqui & pax)):
            if bool(sel.any()):
                (gap_solo if k == 0 else gap_pax).append(gap[sel]); venceu[k] += (gap[sel] > 0).float().sum(); conta[k] += sel.float().sum()
    um_passo(m, a, Wb)
    tem_comida = m.serva[m.cidx, m.no][:, 1] > 0
    fam = (fome0 >= 70) & vivo & (m.rest <= 0) & (m.tpar <= 0)
    passou += (fam & tem_comida).float(); passou_pax += (fam & tem_comida & (m.pd_ >= 0)).float()
    comeu += (fam & (m.fome < fome0 - 30)).float()
    novo = vivo & (m.vida <= 0)
    if bool(novo.any()):
        i = novo.nonzero().squeeze(1)
        reg.append(torch.stack([torch.full_like(m.fome[i], float(t)), m.fome[i], m.dinh[i], m.fuel[i],
                                m.dsa[m.cidx[i], 1, m.no[i]], m.dsa[m.cidx[i], 0, m.no[i]], (m.pd_[i] >= 0).float()], 1))
        vivo &= ~novo
R = torch.cat(reg) if reg else torch.zeros(0, 7, device=DEV)
n = R.shape[0]; print(f'{A.nome} | {braco} s{sd}: mortos {n}/{m.B} = {n/m.B:.2f}')
if n:
    fome_c = (R[:, 1] >= 90).float(); pane_c = (R[:, 3] <= 0.5).float()
    print(f'  causa: fome>=90 em {fome_c.mean():.0%}, tanque vazio em {pane_c.mean():.0%}, ambos {((fome_c*pane_c).mean()):.0%}, nenhum {((1-fome_c)*(1-pane_c)).mean():.0%}')
    q = lambda x: f'mediana {x.median():.1f} [{x.quantile(.25):.1f}, {x.quantile(.75):.1f}]'
    print(f'  dia da morte: {q(R[:,0]/240)}   fome: {q(R[:,1])}   dinheiro: {q(R[:,2])}   tanque: {q(R[:,3])}')
    print(f'  distancia a COMIDA ao morrer: {q(R[:,4])}   ao posto: {q(R[:,5])}   com passageiro: {R[:,6].mean():.0%}')
    print(f'  dos que morrem de fome: dinheiro {q(R[fome_c>0,2])} · d_comida {q(R[fome_c>0,4])} · com passageiro {R[fome_c>0,6].mean():.0%}')
    mortos_i = ~vivo
    print(f'  FAMINTOS (fome>=70) em no com comida: mortos passaram {passou[mortos_i].mean():.1f} vezes/vida (com passageiro {passou_pax[mortos_i].mean():.1f}) e comeram {comeu[mortos_i].mean():.1f}; vivos passaram {passou[vivo].mean():.1f} (com pax {passou_pax[vivo].mean():.1f}) e comeram {comeu[vivo].mean():.1f}')
    for k, g in ((0, gap_solo), (1, gap_pax)):
        if g:
            g = torch.cat(g); print(f'  PLACAR comer − melhor andar ({"SEM" if k==0 else "COM"} passageiro, faminto sobre comida): mediana {g.median():+.2f} [{g.quantile(.25):+.2f}, {g.quantile(.75):+.2f}] · comer vence em {venceu[k]/conta[k]:.0%} de {int(conta[k])} amostras')
    print(f'  genes: w_comer {float(Wb[0, NF+1]):+.2f}  vies_serv {float(Wb[0, NF+5]):+.2f}  w_posto {float(Wb[0, NF]):+.2f}')
v = vivo
print(f'  vivos no fim: fome {q(m.fome[v])}  dinheiro {q(m.dinh[v])}  d_comida agora {q(m.dsa[m.cidx[v],1,m.no[v]])}')
