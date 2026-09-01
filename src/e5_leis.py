"""E5-leis (doc 19 nivel 3): pesos DESCOBREM as formulas do proprio corpo?

    python src/e5_leis.py

SINDy caseiro: biblioteca de termos candidatos + solve fechado (ridge) + poda
pela Lei do Garimpo. Gabarito conhecido (nos escrevemos o mundo):
    andar:  d_fuel = -c.fuel * custo          (c.fuel = 2.1)
    andar:  d_fad  = +c.fadiga * custo        (c.fadiga = 1.65)
    sempre: d_fome = +c.fome                  (c.fome = 0.32)
Se a regressao recuperar termo E coeficiente, "pesos acham formula" fica
provado no nosso chao. Predicao: acha os 3, com os termos errados podados.
"""
import sys, os, torch
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lab import DEV, GMAX, NF, gerar_cidade, Cfg, Lote, Reativo, um_passo

torch.manual_seed(0)
cids = [gerar_cidade(s) for s in range(3)]
cfg = Cfg(1.0)
m = Lote(cids, 256, cfg, seed=11, R=2)          # B=1536 taxis observados
W = torch.randn(m.B, Reativo.NP, device=DEV)*.8  # politicas variadas = dados ricos
a = Reativo(); a.reset(m, W)

X, ALVOS = [], {'d_fuel': [], 'd_fad': [], 'd_fome': []}
for t in range(400):
    antes = dict(fuel=m.fuel.clone(), fad=m.fad.clone(), fome=m.fome.clone(),
                 no=m.no.clone(), tpar=m.tpar.clone(), rest=m.rest.clone(),
                 dinh=m.dinh.clone(), npc=m.npc.clone())
    um_passo(m, a, W); a.atualizar(m)
    partiu = (m.indo >= 0) & (antes['rest'] <= 0) & (m.rest > 0)
    # custo VERDADEIRO da rua tomada (aresta + congestao pre-passo do destino).
    # 1a versao usava rest/vel = round(cu) e ERROU por atenuacao: erro de
    # medida NA ENTRADA da regressao puxa o coeficiente pro zero e vaza o
    # resto pra constante — licao registrada p/ o solve-em-vida (doc 19 §3).
    dst = m.indo.clamp(min=0)
    A0 = m.Aa[m.cidx, antes['no']]
    w_edge = (m.Wa[m.cidx, antes['no']] * (A0 == dst[:,None]).float()).sum(1)
    cu_obs = w_edge + antes['npc'].gather(1, dst[:,None]).squeeze(1)
    cu_obs = torch.where(partiu, cu_obs, torch.zeros_like(cu_obs))
    # amostras LIMPAS: andou agora, sem avaria (tpar nao saltou), sem servico
    ok = partiu & (m.tpar <= antes['tpar']) & (m.dinh == antes['dinh'])
    # biblioteca de termos candidatos (o certo E os errados, pra poda provar valor)
    termos = torch.stack([
        torch.ones_like(cu_obs),          # 1        (constante)
        cu_obs,                           # custo    <- certo p/ fuel e fadiga
        cu_obs**2,                        # custo^2  (errado)
        antes['fome']/100.,               # fome     (errado)
        antes['fuel']/100.,               # fuel     (errado)
        m.npc.gather(1, antes['no'][:,None]).squeeze(1),  # congestao local (errado)
    ], 1)
    X.append(termos[ok])
    ALVOS['d_fuel'].append((m.fuel-antes['fuel'])[ok])
    ALVOS['d_fad'].append((m.fad-antes['fad'])[ok])
    # fome: vale em TODO passo sem comer e longe do teto
    ok2 = (m.fome > antes['fome']) & (antes['fome'] < 95)
    ALVOS['d_fome'].append(torch.stack([torch.ones_like(cu_obs), cu_obs*0+antes['fome']/100.],1)[ok2])

NOMES = ['1', 'custo', 'custo^2', 'fome', 'fuel', 'congestao']
GABARITO = {'d_fuel': ('custo', -cfg.fuel), 'd_fad': ('custo', cfg.fadiga)}
X = torch.cat(X)
print(f'{X.shape[0]:,} amostras limpas de movimento\n')

def garimpo_solve(Phi, y, nomes, passes=3):
    """ridge fechado + poda iterativa: |coef| < limiar do garimpo -> fora."""
    keep = list(range(Phi.shape[1]))
    for _ in range(passes):
        P = Phi[:, keep]
        w = torch.linalg.solve(P.T@P + 1e-4*torch.eye(len(keep), device=DEV), P.T@y)
        res = y - P@w
        sig = res.std()
        contrib = (w.abs()*P.abs().mean(0))
        corte = sig * (2*torch.log(torch.tensor(float(len(keep))))).sqrt() / len(y)**.5
        novos = [k for k, c in zip(keep, contrib) if c > corte]
        if novos == keep or not novos: break
        keep = novos
    return {nomes[k]: round(float(wi), 4) for k, wi in zip(keep, w)}

for alvo, (termo_certo, coef_certo) in GABARITO.items():
    y = torch.cat(ALVOS[alvo])
    achado = garimpo_solve(X, y, NOMES)
    ok = termo_certo in achado and abs(achado.get(termo_certo, 0) - coef_certo) < 0.05*abs(coef_certo)
    print(f'{alvo}: gabarito {termo_certo} x {coef_certo:+.2f}')
    print(f'  descoberto: {achado}   {"ACHOU A LEI" if ok else "ERROU"}')

