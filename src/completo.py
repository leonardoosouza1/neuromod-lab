"""E54 CEREBRO COMPLETO NO MUNDO ABERTO (Leonardo, 2026-09-04 19:15: 'ele precisa de tudo o que tinha antes: talamo, cortex,
hipocampo e afins; o cerebro precisa estar em parte e completo').
Porta o SerCamadas do grafo (camadas.py, E42) pro campo continuo e junta com o que o campo ja tinha:
  LINEAR    24 sentidos por opcao + 10 servicos + bias (a espinha)
  REFLEXO   especie lenta c = EMA(1 - tanque) com tau; portao theta; empurra pro posto (w) e liga o abastecer (v)     4 genes
  TALAMO    atencao por GRUPO de sentidos (rota/servicos/corpo/economia/tempo): gate = 2*sigmoid(a + b*need + c*pax)  15 genes
  CORTEX    politica por DISTRITO: w_ef = w*(1 + delta_{d,f}) em d_alvo, d_posto, custo_frente, preco_frente, |delta| <= .5   48 genes
  HIPOCAMPO memoria por distrito (renda da ultima corrida com origem ali, tempo sem passageiro, dinheiro gasto), EMA com tau,
            entra BILINEAR (memoria x sentido) no movimento e nos servicos, com ganho mestre tanh(g)                104 genes
  RAPIDA    4 unidades relu sobre os 24 sentidos de cada opcao -> nota de movimento                                   104 genes
  LENTA     3 unidades relu sobre o corpo com estado z (tau em banco ~5/25/100) que modula pesos e servicos          150 genes
Tudo NASCE TRANSPARENTE (regra 17): genes de saida em zero => identico ao Linear bit a bit. Partes desligaveis (Sem*)."""
import torch
from campo import *

# grupos do talamo: indices em NOMES_F (NOMES_OP 0-9, NOMES_CORPO 10-23)
GRUPOS_NOMES = {'rota': ['d_alvo', 'custo_frente', 'casa_frente', 'e_tem_pax', 'livre'], 'servicos': ['d_posto', 'd_comida', 'd_agua', 'd_oficina', 'd_descanso'],
                'corpo': ['e_fuel', 'e_agua', 'e_fome', 'e_fadiga', 'e_calor', 'e_vida', 'e_consumo', 'e_autonomia'], 'economia': ['preco_frente', 'aliq_frente', 'e_dinheiro', 'e_reserva'],
                'tempo': ['h_sin', 'h_cos', 'e_noite', 'custo_aqui', 'bias']}   # [pre-F3] grupos do talamo por NOME: sentido novo (risco, demanda, espera, retina...) cai em 'corpo' sem deslocar indice nenhum
_TODOS = [n for ns in GRUPOS_NOMES.values() for n in ns]; _NOVOS = [n for n in NOMES_F[:NF] if n not in _TODOS]
GRUPOS = [(g, sorted(NOMES_F.index(n) for n in ns + (_NOVOS if g == 'corpo' else []) if n in NOMES_F)) for g, ns in GRUPOS_NOMES.items()]   # [E57] +consumo, autonomia; [E61] +risco no corpo; [E68] demanda/espera tambem no corpo (range(26, NF))
NOMES_G = [g for g, _ in GRUPOS]; NG = len(GRUPOS)
assert sorted(i for _, ids in GRUPOS for i in ids) == list(range(NF)), 'grupos nao cobrem os 24 sentidos'
_IG = [0]*NF
for _gi, (_gn, _ids) in enumerate(GRUPOS):
    for _i in _ids: _IG[_i] = _gi
IDX_CORTEX = [0, 1, 6, 7]; NOMES_C = ['d_alvo', 'd_posto', 'custo_frente', 'preco_frente']
DMAX = 12; NM = 3; NOMES_M = ['mem_renda', 'mem_espera', 'mem_gasto']
ESC_DELTA = .5; ESC_RENDA = 30.; ESC_GASTO = 30.

class SerCompleto(Cerebro):
    nome = 'completo-campo'
    O_REF = Cerebro.NP; N_REF = 4                       # tau, w, v, theta
    O_TAL = O_REF + N_REF; N_TAL = NG*3
    O_COR = O_TAL + N_TAL; N_COR = DMAX*len(IDX_CORTEX)
    O_HIP = O_COR + N_COR; N_HIP = 2 + NM*NF + NM*S      # tau_h, ganho, M_h (3xNF), P_h (3xS)
    NP = O_HIP + N_HIP
    liga = dict(talamo=True, cortex=True, hipocampo=True, reflexo=True, livre=True)
    @staticmethod
    def nomes_genes(): return nomes_genes_completos()   # [spec I1a] usado por dof_por_bloco
    def reset(s, m, W):
        Cerebro.reset(s, m, W); B = m.B; L = s.liga
        if not L.get('rapida', True): s.V = torch.zeros_like(s.V)
        if not L.get('lenta', True): s.M = torch.zeros_like(s.M); s.P = torch.zeros_like(s.P)
        if not L['livre']: s.V = torch.zeros_like(s.V); s.M = torch.zeros_like(s.M); s.P = torch.zeros_like(s.P)
        o = s.O_REF; s.tau_r = 1. + 200.*torch.sigmoid(W[:, o] - 4.); s.w = W[:, o+1]; s.v = W[:, o+2]; s.theta = torch.sigmoid(W[:, o+3])
        if not L['reflexo']: s.w = torch.zeros_like(s.w); s.v = torch.zeros_like(s.v)
        s.c = torch.zeros(B, device=DEV)
        s.G3 = W[:, s.O_TAL:s.O_TAL+s.N_TAL].reshape(B, NG, 3)
        if not L['talamo']: s.G3 = torch.zeros_like(s.G3)
        s.IDXG = torch.tensor(_IG, device=DEV)[None, :].expand(B, -1)
        s.DLT = float(getattr(m.cfg, 'cortex_amp', ESC_DELTA))*torch.tanh(W[:, s.O_COR:s.O_COR+s.N_COR].reshape(B, DMAX, len(IDX_CORTEX))); s.TNORM = bool(getattr(m.cfg, 'talamo_norm', False))
        if not L['cortex']: s.DLT = torch.zeros_like(s.DLT)
        s.IDXC = torch.tensor(IDX_CORTEX, device=DEV); s.IDX1 = torch.tensor([1], device=DEV)   # [g10] buffer criado UMA vez: torch.tensor no extra() era a unica sincronizacao do completo (H2D por passo)
        o = s.O_HIP; s.tau_h = 1. + 200.*torch.sigmoid(W[:, o:o+1] - 4.); s.g_hip = torch.tanh(W[:, o+1:o+2])
        if not L['hipocampo']: s.g_hip = torch.zeros_like(s.g_hip)
        o += 2; s.M_h = W[:, o:o+NM*NF].view(B, NM, NF); o += NM*NF; s.P_h = W[:, o:o+NM*S].view(B, NM, S)
        s.MEM = torch.zeros(B, DMAX, NM, device=DEV); s.ARD = torch.arange(DMAX, device=DEV)[None, :]
        s._rec = m.rec.clone(); s._dinh = m.dinh.clone(); s.dn = torch.zeros(B, dtype=torch.long, device=DEV)
        s.gate_soma = torch.zeros(B, NG, device=DEV); s.n_pass = torch.zeros((), device=DEV); s.ref_soma = torch.zeros(B, device=DEV)
    def _need(s, m):
        return torch.stack([1. - m.fuel/100., 1. - m.agua/100., m.fome/100., m.fad/100., m.calor/120.], 1).max(1).values
    def _gate(s, m):
        need = s._need(m); pax = (m.pd_ >= 0).float()
        gt = 2.*torch.sigmoid(s.G3[:, :, 0] + s.G3[:, :, 1]*need[:, None] + s.G3[:, :, 2]*pax[:, None])     # genes 0 -> 1.0 exato
        if s.TNORM: gt = gt*(NG/gt.sum(1, keepdim=True)).clamp(max=1.)
        return gt
    def _ativ(s): return (s.c - s.theta).clamp(min=0.)
    def _mem(s, m):
        s.dn = m.distrito(m.pos).clamp(max=DMAX-1)
        return s.MEM.gather(1, s.dn[:, None, None].expand(-1, 1, NM)).squeeze(1)*s.g_hip           # (B,3) memoria do distrito atual x ganho
    def extra(s, m, W, F):
        # [perfil 09-08: 12 bmm minusculos/passo] soma os vetores de peso por ser ANTES de multiplicar por F: 1 bmm em vez de ~10.
        s.corpo = F[:, G - 1, len(NOMES_OP):]
        h = torch.relu(torch.einsum('bgf,bhf->bgh', F, s.U) + s.bU[:, None, :]); s.h = h                     # rapida (unico bmm por opcao)
        Wtot = torch.einsum('bk,bkf->bf', s.z, s.M)*s.ESC                                                   # lenta: pesos modulados pelo estado
        gf = s._gate(m).gather(1, s.IDXG); Wtot = Wtot + W[:, :NF]*(gf - 1.)                                # talamo
        mem = s._mem(m)                                                                                     # (define s.dn)
        delta = s.DLT.gather(1, s.dn[:, None, None].expand(-1, 1, len(IDX_CORTEX))).squeeze(1)
        Wtot = Wtot.index_add(1, s.IDXC, W[:, s.IDXC]*delta)                                                # cortex por distrito (4 colunas)
        Wtot = Wtot + torch.einsum('bk,bkf->bf', mem, s.M_h)*Cerebro.ESC                                    # hipocampo bilinear
        a = s._ativ(); Wtot = Wtot.index_add(1, s.IDX1, -(s.w*a)[:, None])            # reflexo: empurra pro posto (coluna d_posto) [g10: sem torch.tensor no passo]
        if s.ATIV:   # [spec F2] saidas POR BLOCO na nota de movimento (so no modo ativacao; 5 einsums a mais a cada passo)
            zc = torch.zeros_like(W[:, :NF])
            s._blk = {'rap': torch.einsum('bgh,bh->bg', h, s.V)*s.ESC, 'len': torch.einsum('bgf,bf->bg', F, torch.einsum('bk,bkf->bf', s.z, s.M)*s.ESC),
                      'tal': torch.einsum('bgf,bf->bg', F, W[:, :NF]*(gf - 1.)), 'cor': torch.einsum('bgf,bf->bg', F, zc.index_add(1, s.IDXC, W[:, s.IDXC]*delta)),
                      'hip': torch.einsum('bgf,bf->bg', F, torch.einsum('bk,bkf->bf', mem, s.M_h)*Cerebro.ESC), 'ref': torch.einsum('bgf,bf->bg', F, zc.index_add(1, s.IDX1, -(s.w*a)[:, None]))}   # ref = contribuicao REAL na nota (revisao 09-09)
        out = torch.einsum('bgh,bh->bg', h, s.V)*s.ESC + torch.einsum('bgf,bf->bg', F, Wtot)
        if s.ORC is not None: out = out*s._fator_orc()
        return out
    def extra_serv(s, m):
        ss = Cerebro.extra_serv(s, m)
        mem = s.MEM.gather(1, s.dn[:, None, None].expand(-1, 1, NM)).squeeze(1)*s.g_hip
        ss = ss + torch.einsum('bk,bks->bs', mem, s.P_h)*Cerebro.ESC_S
        z = torch.zeros(m.B, S, device=DEV); z[:, :5] = (s.v*s._ativ())[:, None]
        return ss + z
    def atualizar(s, m):
        Cerebro.atualizar(s, m)
        s.c = s.c + ((1. - m.fuel/100.) - s.c)/s.tau_r
        renda = (m.rec - s._rec)/ESC_RENDA; ev_ent = (renda > 0).float()
        espera = (m.pd_ < 0).float()
        gasto = (s._dinh - m.dinh).clamp(min=0.)/ESC_GASTO; ev_gasto = (gasto > 0).float()
        x = torch.stack([renda, espera, gasto], 1); gate = torch.stack([ev_ent, torch.ones_like(espera), ev_gasto], 1)
        dorig = m.orig_d.clamp(max=DMAX-1); dn = m.distrito(m.pos).clamp(max=DMAX-1)
        oh_o = (s.ARD == dorig[:, None]).float()[:, :, None]; oh_n = (s.ARD == dn[:, None]).float()[:, :, None]
        oh = torch.cat([oh_o, oh_n.expand(-1, -1, 2)], 2)
        s.MEM.add_(oh*gate[:, None, :]*(1./s.tau_h)[:, :, None]*(x[:, None, :] - s.MEM))
        s._rec = m.rec.clone(); s._dinh = m.dinh.clone()
        s.gate_soma += s._gate(m); s.ref_soma += (s._ativ() > 0).float(); s.n_pass = s.n_pass + 1.
    def ativacao(s, m):
        n = s.n_pass.clamp(min=1.); g = s.gate_soma/n
        out = {f'talamo_{k}': g[:, i] for i, k in enumerate(NOMES_G)}
        out['cortex_delta_max'] = s.DLT.abs().amax((1, 2)); out['hipocampo_ganho'] = s.g_hip[:, 0].abs()
        for i, k in enumerate(NOMES_M): out[f'{k}_abs'] = s.MEM[:, :, i].abs().mean(1)
        out['reflexo_frac'] = s.ref_soma/n
        for k in range(s.K): out[f'lenta_z{k}'] = s.z[:, k]
        return out

def _parte(nome, **off):
    class P(SerCompleto): pass
    P.nome = nome; P.liga = {**SerCompleto.liga, **off}; P.__name__ = nome; return P
SemTalamo = _parte('sem-talamo', talamo=False); SemCortex = _parte('sem-cortex', cortex=False); SemHipocampo = _parte('sem-hipocampo', hipocampo=False)
SemReflexo = _parte('sem-reflexo', reflexo=False); SemLivre = _parte('sem-livre', livre=False)
SemRapida = _parte('sem-rapida', rapida=False); SemLenta = _parte('sem-lenta', lenta=False)
SoCamadas = _parte('so-camadas', livre=False)     # talamo+cortex+hipocampo+reflexo (o SerCamadas do grafo, no campo)

def nomes_genes_cerebro():
    """[spec I1a] os 304 genes do Cerebro (livre) na ORDEM dos offsets: rapida (U, bU, V) e lenta (U2, b2, tau, M, P)"""
    H, K, NC_ = Cerebro.H, Cerebro.K, Cerebro.NC_
    rap = [f'rap_U_h{h}_{f}' for h in range(H) for f in NOMES_F[:NF]] + [f'rap_bU_h{h}' for h in range(H)] + [f'rap_V_h{h}' for h in range(H)]
    len_ = [f'len_U2_k{k}_{c}' for k in range(K) for c in NOMES_CORPO] + [f'len_b2_k{k}' for k in range(K)] + [f'len_tau_k{k}' for k in range(K)] + [f'len_M_k{k}_{f}' for k in range(K) for f in NOMES_F[:NF]] + [f'len_P_k{k}_{a}' for k in range(K) for a in NOMES_F[NF:NF+S]]
    return rap + len_

def nomes_genes_completos():
    """[spec I1a] TODOS os genes alem da espinha linear, na ordem dos offsets: cerebro (rap, len) + ref + tal + cor + hip. len == SerCompleto.NP - Linear.NP"""
    return nomes_genes_cerebro() + nomes_genes()

def nomes_genes():
    ref = ['ref_tau', 'ref_w', 'ref_v', 'ref_theta']; tal = [f'tal_{k}_{p}' for k in NOMES_G for p in ('a', 'b', 'c')]
    cor = [f'cor_d{d}_{f}' for d in range(DMAX) for f in NOMES_C]
    hip = ['hip_tau', 'hip_ganho'] + [f'hipM_{k}_{f}' for k in NOMES_M for f in NOMES_F[:NF]] + [f'hipP_{k}_{a}' for k in NOMES_M for a in NOMES_F[NF:NF+S]]
    return ref + tal + cor + hip

Cerebro.nomes_genes = staticmethod(nomes_genes_cerebro)   # [spec I1a/F2] o Cerebro livre (rap+len) tambem decompoe dof e aceita custo por ativacao
