"""E42 (doc 43): CEREBRO EM CAMADAS — talamo, cortex e hipocampo sobre o ReativoReacoes.

`SerCamadas` NASCE bit a bit igual ao pai (ReativoReacoes): as tres camadas sao
transparentes com os genes novos em ZERO, para QUALQUER genoma (nao so o do perito).

  1 TALAMO   atencao por GRUPO de sentidos. 5 grupos sobre as 26 features de obs():
             rota / servicos / corpo / economia / tempo. Cada grupo tem um portao
             gate_g = 2*sigmoid(a_g + b_g*necessidade_dominante + c_g*carregando);
             com genes 0 -> gate = 2*0.5 = 1.0 EXATO (multiplica por 1 = nao faz nada).
             O bloco de features do grupo e multiplicado por gate_g ANTES do produto
             com W. Implementado em extra() como DIFERENCA — (F*gate - F) @ W — pra
             nao precisar tocar em `um_passo`.  15 genes.
  2 CORTEX   politica por contexto de DISTRITO: w_ef = w*(1 + delta_{d,f}) para
             f em {d_alvo, d_posto, custo_rua, e_preco_local} e d = distrito atual.
             delta = 0.5*tanh(gene) (gene 0 -> 0 EXATO; teto |delta| = 0.5, regra 5:
             limitar a alavanca — o EXP10 morreu de ganho 8.0). 6 distritos x 4
             features = 24 genes. Tambem via extra(), somando F*w*delta.
  3 HIPOCAMPO memoria por distrito: 6 x 3 slots EMA de (renda da ultima corrida com
             origem no distrito, fracao de tempo parado sem passageiro, dinheiro pago
             em servicos no distrito). Atualizados IN-PLACE em atualizar() (fora do
             grafo), com eventos detectados por DIFERENCA de estado do Lote. Os 3
             valores do distrito ATUAL entram como sentidos nos slots mem_0..2, cujos
             pesos JA existem no Reativo (W[:, NF+6:NF+9], mortos por construcao ate
             aqui). 2 genes: tau (sigmoide, nasce rapido como em reacoes.py) e um
             GANHO mestre = tanh(gene) (gene 0 -> 0 EXATO). O ganho existe porque
             mem_0..2 sao genes VELHOS: sem ele, um genoma aleatorio com peso de
             memoria nao-nulo deixaria de ser identico ao pai (regra 17).
  4 GLANDULAS  fase 2 — ver docs/43-ser-camadas.md §5 (corpo_fala nasce CANCELANDO as
             features do corpo: e um gargalo por construcao, incompativel com
             "nasce transparente"; e o E20 mostrou que sem prior 97 % morrem).

Contrato do lab (docs/41 §1): extra()/extra_serv() sao PURAS (nao mutam nem `m` nem
`s`), toda mutacao in-place vive em atualizar(), e nao ha nenhum sync CPU<->GPU
(sem .item()/float()/if-em-tensor) no caminho quente.
"""
import torch
from lab import NF, DEV, GMAX, NPX
from reacoes import ReativoReacoes

# ---- grupos de sentidos: indices das 26 features de obs() (ver NOMES_F em rodar.py) ----
GRUPOS = [
    ('rota',     [0, 1, 2, 3]),                       # d_alvo custo_rua congestao semaforo
    ('servicos', [4, 5, 6, 7, 8]),                    # d_posto d_comida d_descanso d_oficina d_loja
    ('corpo',    [9, 10, 11, 12, 13, 14, 20]),        # e_fuel..e_oleo + e_dano
    ('economia', [15, 17, 21, 22]),                   # e_dinheiro e_reserva e_divida e_preco_local
    ('tempo',    [16, 18, 19, 23, 24, 25]),           # e_tem_pax h_sin h_cos h_gl0 h_gl1 bias
]
NOMES_G = [g for g, _ in GRUPOS]
NG = len(GRUPOS)
assert sorted(i for _, ids in GRUPOS for i in ids) == list(range(NF)), 'grupos nao cobrem as 26 features'
_IG = [0]*NF
for _gi, (_gn, _ids) in enumerate(GRUPOS):
    for _i in _ids: _IG[_i] = _gi

# features-chave que o cortex modula (na ordem do doc 41 §3.2)
IDX_CORTEX = [0, 4, 1, 22]          # d_alvo, d_posto, custo_rua, e_preco_local
NOMES_C = ['d_alvo', 'd_posto', 'custo_rua', 'e_preco_local']
DMAX = 6                            # distritos cobertos pelos genes do cortex (D<6 = linhas mortas)
NOMES_M = ['mem_renda', 'mem_espera', 'mem_preco']

ESC_DELTA = 0.5                     # teto de |delta| do cortex
ESC_RENDA = 50.                     # normalizacao dos slots (mesma escala das features de obs)
ESC_PRECO = 30.


def _need(m):
    """(B,) necessidade DOMINANTE — mesma definicao do SerVital/SerTalamo (lab.py)."""
    d5 = torch.stack([1. - m.fuel/m.capf(), m.fome/100., m.fad/100.,
                      1. - m.pneu/100., m.temp/120.], 1)
    return d5.max(1).values


class SerCamadas(ReativoReacoes):
    nome = 'ser-camadas'
    O_TAL = ReativoReacoes.NP           # 51 .. 65  (5 grupos x [a, b, c])
    N_TAL = NG*3
    O_COR = O_TAL + N_TAL               # 66 .. 89  (6 distritos x 4 features)
    N_COR = DMAX*len(IDX_CORTEX)
    O_HIP = O_COR + N_COR               # 90 (tau), 91 (ganho)
    N_HIP = 2
    NP = O_HIP + N_HIP                  # 92

    # --------------------------------------------------------------- nascimento
    def reset(s, m, W):
        super().reset(m, W)             # tau/w/v/theta/c do reflexo (ReativoReacoes)
        B = m.B; c = m.cfg
        # talamo
        s.G3 = W[:, s.O_TAL:s.O_TAL+s.N_TAL].reshape(B, NG, 3)
        s.IDXG = torch.tensor(_IG, device=DEV)[None, :]                # (1,NF)
        # cortex
        s.DLT = ESC_DELTA*torch.tanh(W[:, s.O_COR:s.O_COR+s.N_COR].reshape(B, DMAX, len(IDX_CORTEX)))
        s.IDXC = torch.tensor(IDX_CORTEX, device=DEV)                  # (4,)
        # hipocampo
        s.tau_h = 1. + 200.*torch.sigmoid(W[:, s.O_HIP:s.O_HIP+1] - 4.)   # (B,1) gene 0 -> ~4.6 passos
        s.g_hip = torch.tanh(W[:, s.O_HIP+1:s.O_HIP+2])                   # (B,1) gene 0 -> 0 EXATO
        s.MEM = torch.zeros(B, DMAX, 3, device=DEV)
        s.Wmem = W[:, NF+6:NF+9]                                          # pesos mem_0..2 (ja existiam)
        s.eco = bool(c.economia)
        s.D = min(DMAX, int(getattr(c, 'D', getattr(c, 'D_DIST', 3))))
        s.ZL = torch.zeros(B, dtype=torch.long, device=DEV)
        s.ARD6 = torch.arange(DMAX, device=DEV)[None, :]                  # (1,6)
        # estado anterior (detector de eventos; tudo lido/escrito FORA do grafo)
        s._rec = m.rec.clone(); s._dinh = m.dinh.clone()
        s._dorig = s._dist(m)
        # telemetria por camada (ativacao())
        s.gate_soma = torch.zeros(B, NG, device=DEV)
        s.delta_soma = torch.zeros(B, device=DEV)
        s.reflexo_soma = torch.zeros(B, device=DEV)
        s.mem_toque = torch.zeros(B, DMAX, device=DEV)
        s.n_pass = torch.zeros((), device=DEV)

    # --------------------------------------------------------------- utilitarios
    def _dist(s, m):
        """(B,) distrito do no atual (0 quando nao ha economia: um distrito so)."""
        if not s.eco: return s.ZL
        return m.e15_dist[m.cidx, m.no].clamp(max=DMAX-1)

    def _gate(s, m):
        """(B,NG) portao do talamo. Genes 0 -> 2*sigmoid(0) = 1.0 exato."""
        need = _need(m); carreg = (m.pd_ >= 0).float()
        return 2.*torch.sigmoid(s.G3[:, :, 0] + s.G3[:, :, 1]*need[:, None]
                                + s.G3[:, :, 2]*carreg[:, None])

    def _delta(s, m, dn):
        """(B,4) modulacao do cortex no distrito dn. Genes 0 -> 0 exato."""
        return s.DLT.gather(1, dn[:, None, None].expand(-1, 1, len(IDX_CORTEX))).squeeze(1)

    # --------------------------------------------------------------- decisao (PURA)
    def extra(s, m, W, viz):
        base = super().extra(m, W, viz)                      # reflexo do pai (B,G)
        F, _ = m.obs()                                       # obs() e pura: recomputar da o MESMO F
        dn = s._dist(m)
        # 1) TALAMO: (F*gate - F) @ W = F @ (W*(gate-1))
        gf = s._gate(m).gather(1, s.IDXG.expand(m.B, -1))     # (B,NF) portao por feature
        sc = torch.einsum('bgf,bf->bg', F, W[:, :NF]*(gf - 1.))
        # 2) CORTEX: + F[.,IDXC] @ (W[IDXC]*delta_d)  (composicao ADITIVA com o talamo)
        sc = sc + torch.einsum('bgf,bf->bg', F.index_select(2, s.IDXC),
                               W[:, s.IDXC]*s._delta(m, dn))
        # 3) HIPOCAMPO: os 3 slots do distrito ATUAL nos pesos mem_0..2 (constante em G,
        #    como qualquer feature de estado — desloca mover-vs-servir, nao a direcao)
        mem = s.MEM.gather(1, dn[:, None, None].expand(-1, 1, 3)).squeeze(1)   # (B,3)
        hip = s.g_hip*(mem*s.Wmem).sum(1, keepdim=True)                        # (B,1)
        return base + sc + hip

    # --------------------------------------------------------------- estado (FORA do grafo)
    def atualizar(s, m):
        super().atualizar(m)                                  # especies lentas do reflexo
        dn = s._dist(m)                                       # distrito ONDE o passo aconteceu
        # --- eventos por DIFERENCA de estado ---
        renda = (m.rec - s._rec)/ESC_RENDA                    # corrida entregue: m.rec subiu
        ev_ent = (renda > 0).float()
        espera = ((m.pd_ < 0) & (m.rest <= 0) & (m.tpar <= 0)).float()   # parado sem passageiro
        if s.eco:
            pago = (m.e15_d0 - m.dinh).clamp(min=0.)/ESC_PRECO   # e15_d0 = saldo antes das compras
        else:
            pago = (s._dinh - m.dinh).clamp(min=0.)/ESC_PRECO
        ev_pago = (pago > 0).float()
        x = torch.stack([renda, espera, pago], 1)                        # (B,3)
        gate = torch.stack([ev_ent, torch.ones_like(espera), ev_pago], 1)  # (B,3) so atualiza no evento
        # renda vai pro distrito de ORIGEM da corrida; espera/preco, pro distrito atual
        oh_o = (s.ARD6 == s._dorig[:, None]).float()[:, :, None]         # (B,6,1)
        oh_n = (s.ARD6 == dn[:, None]).float()[:, :, None]
        oh = torch.cat([oh_o, oh_n.expand(-1, -1, 2)], 2)                # (B,6,3)
        a = (1./s.tau_h)[:, :, None]                                     # (B,1,1)
        s.MEM.add_(oh*gate[:, None, :]*a*(x[:, None, :] - s.MEM))
        # --- telemetria por camada ---
        s.gate_soma += s._gate(m)
        s.delta_soma += s._delta(m, dn).abs().mean(1)
        s.reflexo_soma += (s._ativ() > 0).any(1).float()
        s.mem_toque += oh_n[:, :, 0]
        s.n_pass = s.n_pass + 1.
        # --- estado anterior para o proximo passo ---
        s._rec = m.rec.clone(); s._dinh = m.dinh.clone()
        s._dorig = (m.e15_dorig.clamp(max=DMAX-1) if s.eco else s.ZL)

    # --------------------------------------------------------------- retrato
    def ativacao(s):
        """dict de tensores (B,) — SEM sync: quem chama e que converte no fim."""
        n = s.n_pass.clamp(min=1.)
        g = s.gate_soma/n                                                # (B,NG)
        mem = s.MEM[:, :s.D, :]
        out = {f'talamo_gate_{k}': g[:, i] for i, k in enumerate(NOMES_G)}
        out['talamo_gate_min'] = g.min(1).values
        out['talamo_gate_medio'] = g.mean(1)
        out['cortex_delta_abs'] = s.delta_soma/n
        out['cortex_delta_max'] = s.DLT.abs().amax((1, 2))
        for i, k in enumerate(NOMES_M):
            out[f'hipocampo_{k}_var'] = (mem[:, :, i].var(1) if s.D > 1
                                         else torch.zeros(mem.shape[0], device=DEV))
            out[f'hipocampo_{k}_abs'] = mem[:, :, i].abs().mean(1)
        out['hipocampo_ganho'] = s.g_hip[:, 0].abs()
        out['hipocampo_distritos_visitados'] = (s.mem_toque > 0).float().sum(1)
        out['reflexo_frac'] = s.reflexo_soma/n
        return out


def nomes_genes():
    """os 41 nomes dos genes NOVOS (depois dos 44 do Reativo + 7 do reflexo)."""
    tal = [f'tal_{k}_{p}' for k in NOMES_G for p in ('a', 'b', 'c')]
    cor = [f'cor_d{d}_{f}' for d in range(DMAX) for f in NOMES_C]
    return tal + cor + ['hip_tau', 'hip_ganho']


# ---- ablacoes (intervir, nao medir): cada camada sozinha ----
class SemTalamo(SerCamadas):
    """controle: os genes do talamo ficam mortos (gate == 1 sempre)."""
    nome = 'camadas-sem-talamo'
    def reset(s, m, W):
        super().reset(m, W); s.G3 = torch.zeros_like(s.G3)

class SemCortex(SerCamadas):
    nome = 'camadas-sem-cortex'
    def reset(s, m, W):
        super().reset(m, W); s.DLT = torch.zeros_like(s.DLT)

class SemHipocampo(SerCamadas):
    """controle da predicao 50: mesma arquitetura, memoria desligada na raiz."""
    nome = 'camadas-sem-hipocampo'
    def reset(s, m, W):
        super().reset(m, W); s.g_hip = torch.zeros_like(s.g_hip)

class SoHipocampo(SerCamadas):
    nome = 'camadas-so-hipocampo'
    def reset(s, m, W):
        super().reset(m, W)
        s.G3 = torch.zeros_like(s.G3); s.DLT = torch.zeros_like(s.DLT)
