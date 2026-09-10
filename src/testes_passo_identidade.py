"""[reprojeto CS docs/70 #1 no passo()] as constantes do passo viraram tensores 0-dim (torch.full_like(x, c) -> s.T_c): IDENTIDADE bit a bit
contra o codigo ANTES do reprojeto (snapshot em /media/llm-data/universe-runs/neuromod-lab-taxi/snapshots/src_antes_reprojeto), rodando
o snapshot num subprocesso (PYTHONPATH) e o codigo atual neste, mesma W/mapas/cfg/semente, Linear e SerCompleto, T=300. Exit 1 se diferir."""
import sys, os, subprocess
AQUI = os.path.dirname(os.path.abspath(__file__)); SNAP = '/media/llm-data/universe-runs/neuromod-lab-taxi/snapshots/src_antes_reprojeto'
OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else '/media/llm-data/universe-runs/neuromod-lab-taxi/e72'
if os.environ.get('_NM_FILHO'):
    if os.environ['_NM_FILHO'] == 'antes': sys.path.insert(0, SNAP)
    else: sys.path.insert(0, AQUI)
    import torch; from campo import *; from completo import SerCompleto
    assert (os.environ['_NM_FILHO'] == 'antes') == os.path.abspath(sys.modules['campo'].__file__).startswith(SNAP), 'importou o campo errado'
    mapas = [gerar_mapa(1000, L=200., distinto=True), gerar_mapa(1001, L=200., distinto=True)]; g = torch.Generator(device=DEV); g.manual_seed(5); res = {}
    for Arq, nome in ((Linear, 'Linear'), (SerCompleto, 'SerCompleto')):
        W = torch.randn(512, Arq.NP, generator=g, device=DEV)*.3; W[:, :Linear.NP] = torch.randn(512, Linear.NP, generator=g, device=DEV)*.5
        c = CfgCampo(L=200., fitness='riqueza'); c.retina = dict(RETINA_PADRAO) if RETINA else None
        m = rodar(Arq, W, mapas, c, T=300, seed=3, R=1); res[nome] = {k: getattr(m, k).cpu() for k in ('pos', 'vida', 'fome', 'fuel', 'agua', 'dinh', 'calor', 'fad', 'res', 'tpar')}
    torch.save(res, os.path.join(OUT, f'passo_id_{os.environ["_NM_FILHO"]}.pt')); print('filho', os.environ['_NM_FILHO'], 'ok', flush=True); sys.exit(0)
os.makedirs(OUT, exist_ok=True)
for rot, caminho in (('antes', SNAP), ('agora', AQUI)):
    env = dict(os.environ, _NM_FILHO=rot, NM_COMPILE='0'); r = subprocess.run([sys.executable, os.path.abspath(__file__), '--out', OUT], env=env, cwd=caminho)
    if r.returncode != 0: print('PORTAO PASSO FALHOU: filho', rot, 'exit', r.returncode, flush=True); sys.exit(1)
import torch; a = torch.load(os.path.join(OUT, 'passo_id_antes.pt')); b = torch.load(os.path.join(OUT, 'passo_id_agora.pt')); falhas = []
for nome in a:
    ig = {k: torch.equal(a[nome][k], b[nome][k]) for k in a[nome]}; ok = all(ig.values()); falhas += [] if ok else [nome]
    print(f'  {nome:12} antes vs agora (passo com constantes 0-dim): {ig}', 'OK' if ok else 'FALHOU', flush=True)
print('PORTAO PASSO IDENTIDADE', 'ok' if not falhas else f'FALHOU em {falhas}', flush=True); sys.exit(0 if not falhas else 1)
