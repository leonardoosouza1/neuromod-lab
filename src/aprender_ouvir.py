"""E22 (doc 38): o cerebro aprende a OUVIR os hormonios em vida — plasticidade gateada por recompensa.
Corpo = glandulas do E20 com codigo herdado (h0 = fome, h1 = sede de gasolina), tau rapido.
Cerebro: Gserv (K x 5, hormonio -> servico) comeca em ZERO e muda em vida:
    dG[k,p] = eta * h_k(passo anterior) * [usou servico p] * r ,  r = recompensa do passo
    r = +1 entregou, +0.5 comeu/abasteceu (necessidade caiu), -1 pane, -0.1*dano de vida; decaimento lambda.
Genes: eta (sigmoide * ETA_MAX) e lambda (decaimento). Tudo em atualizar() (in-place, fora do grafo);
extra()/extra_serv() puras. hebb_puro=True: r = 1 sempre (controle: correlacao sem causa)."""
import torch
from lab import Reativo, NF, DEV, GMAX
from corpo_fala import fabrica as fabrica_corpo, _sinais, _feat_corpo, IDX_CORPO, NX, NH

def fabrica(K=2, eta_max=.2, hebb_puro=False, eta_fixa=None, nome=None, explora=3., eps_infancia=0.):
    """explora: desvio da inicializacao ALEATORIA (por vida, nao herdada) de Gserv — sem ela o servico
    nunca e escolhido pela primeira vez e a regra nunca dispara (perito eta=.1: 0 refeicoes, 100 % de fome)."""
    Base = fabrica_corpo(K, prior_corpo=True)          # corpo nasce falando; Gserv do genoma sera IGNORADO
    class SerAprendeOuvir(Base):
        NP = Base.NP + 2                                # + eta, lambda
        def reset(s, m, W):
            Base.reset(s, m, W)
            B = m.B; o = Base.NP
            s.eta = (torch.sigmoid(W[:, o])*eta_max) if eta_fixa is None else torch.full((B,), eta_fixa, device=DEV)
            s.lam = 1. - 0.01*torch.sigmoid(W[:, o+1])  # decaimento por passo (0.99..1.0)
            # nasce SURDO mas curioso: Gserv aleatorio pequeno POR VIDA (nao herdado) -> tenta servicos,
            # a recompensa esculpe. Com explora=0 e eta=0 e identico ao corpo-nasce-falando.
            s.Gserv = (torch.randn(B, K, 5, generator=m.gsim, device=DEV)*explora) if explora > 0 else torch.zeros(B, K, 5, device=DEV)
            s.Gmov = torch.zeros(B, K, device=DEV)
            s.h_prev = torch.zeros(B, K, device=DEV)
            s.ent_prev = m.ent.clone(); s.fome_prev = m.fome.clone(); s.fuel_prev = m.fuel.clone()
            s.pane_prev = m.av_fuel.clone(); s.vida_prev = m.vida.clone(); s.no_prev = m.no.clone()
            s.r_soma = torch.zeros(B, device=DEV); s.dG_soma = torch.zeros(B, device=DEV)
        def decidir(s, tudo, m):
            """E25b: curiosidade de verdade — na infancia (t < fome_gracia), com prob. eps escolhe um servico
            DISPONIVEL ao acaso (tenta comer/abastecer/descansar sem saber por que). Fora da infancia: argmax."""
            esc = tudo.argmax(1)
            if eps_infancia <= 0.: return esc
            _, svpaga = m.serv_need()                                  # (B,5) disponivel e pagavel
            u = torch.rand(m.B, 5, generator=m.gsim, device=DEV)
            alea = GMAX + torch.where(svpaga > 0, u, torch.full_like(u, -1.)).argmax(1)
            tem = (svpaga > 0).any(1)
            sorteio = torch.rand(m.B, generator=m.gsim, device=DEV) < eps_infancia
            inf = (m.t < m.cfg.fome_gracia) if m.cfg.fome_gracia else torch.zeros_like(tem)
            return torch.where(sorteio & tem & inf, alea, esc)
        def atualizar(s, m):
            # 1) recompensa do passo que acabou de acontecer
            if hebb_puro:
                r = torch.ones(m.B, device=DEV)
            else:
                r = ((m.ent - s.ent_prev) + 0.5*((s.fome_prev - m.fome) > 30).float()
                     + 0.5*((m.fuel - s.fuel_prev) > 20).float() - (m.av_fuel - s.pane_prev)
                     - 0.1*(s.vida_prev - m.vida).clamp(min=0))
            # 2) qual servico foi usado neste passo (inferido pelo efeito: comeu / abasteceu / descansou / consertou)
            usou = torch.stack([((m.fuel - s.fuel_prev) > 20).float(), ((s.fome_prev - m.fome) > 30).float(),
                                torch.zeros_like(r), torch.zeros_like(r), torch.zeros_like(r)], 1)   # (B,5)
            # 3) regra: dG = eta * h_prev (k) x usou (p) x r
            dG = s.eta[:, None, None]*s.h_prev[:, :, None]*usou[:, None, :]*r[:, None, None]
            s.Gserv = (s.Gserv*s.lam[:, None, None] + dG).clamp(-20., 20.)
            s.r_soma += r; s.dG_soma += dG.abs().sum((1, 2))
            # 4) estado pro proximo passo
            s.ent_prev = m.ent.clone(); s.fome_prev = m.fome.clone(); s.fuel_prev = m.fuel.clone()
            s.pane_prev = m.av_fuel.clone(); s.vida_prev = m.vida.clone()
            s.h_prev = s.h.clone()
            Base.atualizar(s, m)                        # atualiza h (rede do corpo)
    SerAprendeOuvir.nome = nome or ('aprende-ouvir' + ('-hebb' if hebb_puro else '') + (f'-eta{eta_fixa}' if eta_fixa is not None else '') + (f'-eps{eps_infancia}' if eps_infancia else ''))
    SerAprendeOuvir.K = K
    return SerAprendeOuvir
