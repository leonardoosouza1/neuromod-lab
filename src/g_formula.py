"""F0 do PRD v2 (docs/16): o ganho G em forma fechada, ANTES de simular.

    python src/g_formula.py

1. Reproduz a tabela de docs/06 §3.3 (exp08) — se nao bater, a teoria esta
   errada e nada mais importa (06 §10 passo 1, INEGOCIAVEL).
2. Valida P(K) contra simulacao real de EMA num processo OU (GPU).
3. Calcula G do mundo `turnos` proposto no PRD.

Formulas (docs/06 §3):
    P(K) = [(1-K)^2 Q + K^2 R] / [1 - (1-K)^2 rho^2],  Q = sigma_s^2 (1-rho^2)
    J_fixo  = min_K sum_c pi_c P(K;c)
    J_adapt = sum_c pi_c min_K P(K;c)
    G = (J_fixo - J_adapt)/J_fixo          tau* = 1/K*
"""
import torch
DEV = 'cuda' if torch.cuda.is_available() else 'cpu'
KS = torch.linspace(1e-3, 1., 4000, device=DEV)


def P(K, rho, R, sig2=1.0):
    Q = sig2*(1-rho**2)
    return ((1-K)**2*Q + K**2*R) / (1 - (1-K)**2*rho**2)


def G(regimes, pis=None):
    """regimes: lista de (rho, R). Devolve (G, tau* por regime)."""
    n = len(regimes)
    pis = pis or [1./n]*n
    curvas = torch.stack([P(KS, rho, R) for rho, R in regimes])      # (n,K)
    j_fixo = (torch.tensor(pis, device=DEV)[:,None]*curvas).sum(0).min()
    mins = curvas.min(1)
    j_adapt = sum(p*m for p, m in zip(pis, mins.values))
    taus = [round(1./KS[i].item(), 1) for i in mins.indices]
    return float((j_fixo-j_adapt)/j_fixo), taus


def simular_ema(rho, R, sig2=1.0, T=200_000, B=256, seed=0):
    """MSE real de uma EMA com taxa K rastreando um OU — valida P(K)."""
    g = torch.Generator(device=DEV); g.manual_seed(seed)
    q = (sig2*(1-rho**2))**.5
    s = torch.zeros(B, device=DEV); h = torch.zeros(B, len(KS), device=DEV)
    K = KS[None, :]
    mse = torch.zeros(len(KS), device=DEV)
    for t in range(T):
        s = rho*s + q*torch.randn(B, generator=g, device=DEV)
        y = s + R**.5*torch.randn(B, generator=g, device=DEV)
        h = (1-K)*h + K*y[:, None]
        if t > 200:                                   # descarta transiente
            mse += ((h - s[:, None])**2).mean(0)
    return mse/(T-201)


if __name__ == '__main__':
    print('=== 1. tabela docs/06 §3.3 (alvo entre parenteses) ===')
    rho0, R0 = 0.9, 0.1     # base do exp08 (inferida; ver verificacao abaixo)
    casos = [
        ('estacionario        (G= 0.0%, tau [1.7,1.7])', [(rho0, R0), (rho0, R0)]),
        ('ruido 2x            (G= 1.7%)',               [(rho0, R0), (rho0, 2*R0)]),
        ('ruido 10x           (G=12.5%)',               [(rho0, R0), (rho0, 10*R0)]),
        ('ruido 100x          (G=25.6%, tau [1.1,4.2])',[(rho0, R0), (rho0, 100*R0)]),
        ('persist .99 vs .70  (G=21.2%, tau [2.8,1.2])',[(0.99, R0), (0.70, R0)]),
        ('ambos juntos        (G= 1.2%)',               [(0.99, R0), (0.70, 100*R0)]),
    ]
    for nome, regs in casos:
        g_, taus = G(regs)
        print(f'  {nome:<48} -> G={g_*100:5.1f}%  tau*={taus}')

    print('\n=== 2. P(K) vs simulacao de EMA real (3 pontos) ===')
    for rho, R in [(0.9, 0.1), (0.9, 10*0.1), (0.99, 0.1)]:
        mse = simular_ema(rho, R)
        ki = mse.argmin()
        teoria = P(KS, rho, R)
        ki_t = teoria.argmin()
        print(f'  rho={rho} R={R}: K* sim {KS[ki]:.3f} vs teoria {KS[ki_t]:.3f} | '
              f'MSE* sim {mse[ki]:.4f} vs teoria {teoria[ki_t]:.4f}')

    print('\n=== 3. mundo `turnos` do PRD (dia/noite) ===')
    # dia: sinal (onde ha passageiro) persistente e bem observado (denso: ve varios)
    # noite: mesmo processo, observacao 8x mais ruidosa (escasso: quase nao ve)
    for nome, regs in [
        ('turnos ruido 8x',  [(0.9, 0.1), (0.9, 0.8)]),
        ('turnos ruido 25x', [(0.9, 0.1), (0.9, 2.5)]),
    ]:
        g_, taus = G(regs)
        veredito = 'VALE' if g_ > 0.15 else ('marginal' if g_ > 0.05 else 'NAO VALE')
        print(f'  {nome:<20} -> G={g_*100:5.1f}%  tau*={taus}  [{veredito}]')
