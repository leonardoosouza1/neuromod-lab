"""vida_hip.py — [10/09] a vida inteira de cada ser num kernel HIP (src/hip/vida.cu): uma thread por ser, T tiques no device, sem
lancamento por tique. Inicializacao (berco, passageiros, fase) continua sendo a do Campo (torch, mesma semente); o kernel roda o laco e
devolve o estado final no proprio Campo (m.t_vida, m.rec, m.ent, ...), de modo que _fit()/medidas leem igual. So cerebro Linear (NP 40,
NF 29 = RISCO + PONTO ligados, sem retina/regime). Compila uma vez (hipcc) em TORCH_EXTENSIONS_DIR em /media/llm-data."""
import os, sys, torch
os.environ.setdefault('TORCH_EXTENSIONS_DIR', '/media/llm-data/scratch/torch_ext')
from campo import Campo, Linear, TIPOS, NF, DEV
_MOD = None
def modulo():
    global _MOD
    if _MOD is None:
        from torch.utils.cpp_extension import load
        os.environ['PATH'] = os.path.dirname(sys.executable) + os.pathsep + os.environ.get('PATH', '')   # [10/09] ninja do venv: a fila chama o python por caminho absoluto, sem ativar o venv
        _MOD = load(name='vida_hip', sources=[os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hip', 'vida.cu')], extra_cuda_cflags=['-O3'], verbose=False)
    return _MOD
def _cfg_f(c):
    ks = ('L', 'fuel_passo', 'agua_passo', 'agua_calor', 'fome_passo', 'fad_passo', 'calor_sobe', 'calor_desce', 'CALOR_MAX', 'D_QUENTE', 'D_PANE', 'D_RODAR', 'fome_mata', 'FOME_CRIT', 'agua_mata', 'AGUA_CRIT', 'KCAL_PANE', 'GUINCHO', 'FUEL_POS_PANE', 'raio', 'raio_px', 'vel', 'vel_noite', 'amp_preco', 'periodo_preco', 'preco_L', 'preco_agua', 'preco_comida', 'HOTEL', 'preco_oficina', 'REPARO', 'tarifa_base', 'tarifa_km', 'aluguel', 'LIMITE_DIVIDA', 'PERDA_ARMAZ', 'RES_MAX', 'perda_res', 'REFEICAO', 'margem_risco', 'respawn')
    return {k: float(getattr(c, k)) for k in ks}
def rodar_hip(W, mapas, cfg, T, seed, R=1, alvo=None, grava=False):
    """mesma assinatura util de rodar(Linear, ...): devolve o Campo com o estado final; se grava, tambem (acoes (T,B), traj (T,B,7))"""
    assert NF == 29 and W.shape[1] == Linear.NP == 40, f'kernel v0 = NF 29 / NP 40 (RISCO+PONTO, sem retina); aqui NF {NF} NP {W.shape[1]}'
    assert cfg.custo_gene == 0. and not cfg.regime and not cfg.reproducao and cfg.ponto == 0. and cfg.retina is None, 'kernel v0: sem custo de gene, regime, reproducao, ponto ou retina'
    m = Campo(mapas, W.shape[0], cfg, seed=seed, R=R); B = m.B; Wb = W[m.gidx].contiguous().float()
    assert int(cfg.NPX) == 12 and m.px.shape[1] == 12, f'kernel vida.cu compilado com NPX 12 fixo (cfg.NPX {cfg.NPX}, slots {m.px.shape[1]}): outro valor le fora do buffer'
    NC = m.NC; K = m.pmul0.shape[1]; NPTS = max(m.serv[t].shape[1] for t in TIPOS)
    serv = torch.zeros(NC, len(TIPOS), NPTS, 2, device=DEV); nserv = torch.zeros(NC, len(TIPOS), dtype=torch.int32, device=DEV)
    for j, t in enumerate(TIPOS): n = m.serv[t].shape[1]; serv[:, j, :n] = m.serv[t]; nserv[:, j] = m.serv_msk[t].sum(1).int()
    st = dict(custo=m.custo_tex.float().contiguous(), cdist=m.campo_dist.int().contiguous(), pmul0=m.pmul0.float().contiguous(), aliq=m.aliq.float().contiguous(), alug=m.alug.float().contiguous(), demanda=m.demanda.float().contiguous(), fase_preco=m.fase_preco.float().contiguous(),
              serv=serv.contiguous(), nserv=nserv, W=Wb, cidx=m.cidx.int().contiguous(), fase=m.fase.float().contiguous(), casa=m.casa.int().contiguous(),
              px=m.pos[:, 0].contiguous(), py=m.pos[:, 1].contiguous(), fuel=m.fuel.contiguous(), fome=m.fome.contiguous(), agua=m.agua.contiguous(), dinh=m.dinh.contiguous(), vida=m.vida.contiguous(), calor=m.calor.contiguous(), fad=m.fad.contiguous(), res=m.res.contiguous(), tpar=m.tpar.contiguous(), cons=m.cons.contiguous(),
              pxs=m.px.contiguous().view(-1).clone(), pxd=m.pxd.contiguous().view(-1).clone(), px_ok=m.px_ok.int().contiguous(), pd_=m.pd_.contiguous(), destx=m.dest[:, 0].contiguous(), desty=m.dest[:, 1].contiguous(), embx=m.emb[:, 0].contiguous(), emby=m.emb[:, 1].contiguous(), orig_d=m.orig_d.int().contiguous(), t_ult=m.t_ult.contiguous(),
              ent=m.ent.contiguous(), rec=m.rec.contiguous(), avar=m.avar.contiguous(), av_fuel=m.av_fuel.contiguous(), n_posto=m.n_posto.contiguous(), litros=m.litros.contiguous(), n_oficina=m.n_oficina.contiguous(), n_come=m.n_come.contiguous(), n_agua=getattr(m, 'n_agua', torch.zeros(B, device=DEV)).contiguous(), dano_soma=m.dano_soma.contiguous(), t_vida=m.t_vida.contiguous())
    if alvo is not None: st['alvo_inj'] = alvo.float().contiguous()
    INT = {'cdist', 'nserv', 'cidx', 'casa', 'px_ok', 'orig_d', 'acoes'}   # [18:25] o kernel le float* em tudo que nao esta aqui: no caminho do e43 (cenario + 4 mapas de treino) algum buffer chegou Long -> cast explicito e nome na falha
    for k in list(st):
        if k in INT: st[k] = st[k].to(torch.int32).contiguous()
        elif st[k].dtype != torch.float32: st[k] = st[k].float().contiguous()
    if grava: st['acoes'] = torch.zeros(T, B, dtype=torch.int32, device=DEV); st['traj'] = torch.zeros(T, B, 7, device=DEV)
    cfg_i = dict(dia=int(cfg.dia), K=int(K), NPTS=int(NPTS), loja=int(bool(cfg.loja_no_posto)), T=int(T), injeta_alvo=int(alvo is not None), grava=int(grava))
    modulo().vida(st, _cfg_f(cfg), cfg_i, int(seed)*7919 + 13); torch.cuda.synchronize()
    m.pos = torch.stack([st['px'], st['py']], 1)
    for k in ('fuel', 'fome', 'agua', 'dinh', 'vida', 'calor', 'fad', 'res', 'tpar', 'cons', 'pd_', 't_ult', 'ent', 'rec', 'avar', 'av_fuel', 'n_posto', 'litros', 'n_oficina', 'n_come', 'n_agua', 'dano_soma', 't_vida'): setattr(m, k, st[k])
    m.dest = torch.stack([st['destx'], st['desty']], 1); m.emb = torch.stack([st['embx'], st['emby']], 1); m.orig_d = st['orig_d'].long(); m.px = st['pxs'].view(B, -1, 2); m.pxd = st['pxd'].view(B, -1, 2); m.px_ok = st['px_ok'].bool(); m.t = torch.tensor(T, device=DEV)
    return (m, st['acoes'].long(), st['traj']) if grava else m
def avaliar_hip(Arq, W, mapas, cfg, T, seed=0, R=1):
    """[motor hip] mesma assinatura de campo.avaliar: uma geracao inteira no kernel; so Linear (NP 40)"""
    from campo import _fit
    m = rodar_hip(W, mapas, cfg, T, seed, R=R); return _fit(m, cfg, T).view(W.shape[0], m.NC*m.R).mean(1)
