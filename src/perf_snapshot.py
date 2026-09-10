"""[10/09 15:40] VELOCIDADE snapshot (src_antes_reprojeto, codigo de 10/09 ~10:00) vs codigo atual: o mesmo rodar(Linear) em dois
subprocessos (PYTHONPATH), mesma W/mapa/cfg/semente, B = 5120 (P256 x R4 x 5 sementes, o lote da celula e78), T = 600 tiques, horizonte
fixo. Motivo: e78/P256sig01 (09/09 23:48) levou 813 s e z2/z1 (10/09, mesmo protocolo) 1923/2097 s — 2.4x mais lento. Este portao
separa 'codigo ficou lento' de 'cauda do horizonte aberto / GPU quente'. Exit 1 se agora > 1.15x o snapshot."""
import sys, os, json, subprocess, time
AQUI = os.path.dirname(os.path.abspath(__file__)); SNAP = os.environ.get('_NM_SNAP') or '/media/llm-data/universe-runs/neuromod-lab-taxi/snapshots/src_antes_reprojeto'
if not os.environ.get('_NM_FILHO') and '--antes' in sys.argv: SNAP = sys.argv[sys.argv.index('--antes') + 1]; os.environ['_NM_SNAP'] = SNAP   # [16:30] bisect: qualquer snapshot de src/ (ex. src_2309_2305 = 09/09 23:05, antes do jardim comum)
if os.environ.get('_NM_FILHO'):
    if os.environ['_NM_FILHO'] == 'antes': sys.path.insert(0, SNAP)
    else: sys.path.insert(0, AQUI)
    os.environ['NM_COMPILE'] = '0'; import torch; import campo; from campo import *
    assert (os.environ['_NM_FILHO'] == 'antes') == os.path.abspath(campo.__file__).startswith(SNAP), 'importou o campo errado'
    B = int(os.environ.get('_NM_B', '5120')); T = int(os.environ.get('_NM_T', '600')); cfg = CfgCampo(L=200., fitness='vida'); mapa = gerar_mapa(1000, L=200., distinto=True)
    g = torch.Generator(device=DEV); g.manual_seed(0); W = torch.randn(B, Linear.NP, generator=g, device=DEV)*.5
    rodar(Linear, W[:256], [mapa], cfg, 50, seed=7777, R=1); torch.cuda.synchronize()   # aquecimento
    t0 = time.time(); m = rodar(Linear, W, [mapa], cfg, T, seed=7777, R=1); torch.cuda.synchronize(); dt = time.time() - t0
    print(json.dumps(dict(quem=os.environ['_NM_FILHO'], B=m.B, T=T, ms_tique=1000*dt/T, seg=dt, vida=float(m.vida.mean()), rec=float(m.rec.mean()), arquivo=os.path.abspath(campo.__file__))), flush=True); sys.exit(0)
res = {}
for rot, caminho in (('antes', SNAP), ('agora', AQUI)):
    env = dict(os.environ, _NM_FILHO=rot, NM_COMPILE='0'); r = subprocess.run([sys.executable, os.path.abspath(__file__)], env=env, cwd=caminho, capture_output=True, text=True)
    linha = [l for l in r.stdout.strip().split('\n') if l.startswith('{')]; assert r.returncode == 0 and linha, f'{rot}: exit {r.returncode}\n{r.stderr[-1500:]}'
    res[rot] = json.loads(linha[-1]); print(f"  {rot:5s}: B {res[rot]['B']} T {res[rot]['T']} | {res[rot]['ms_tique']:.2f} ms/tique ({res[rot]['seg']:.1f} s) | vida {res[rot]['vida']:.2f} rec {res[rot]['rec']:.2f} | {res[rot]['arquivo']}", flush=True)
razao = res['agora']['ms_tique']/res['antes']['ms_tique']; print(f"  agora/antes = {razao:.2f}x | identidade vida/rec: {res['agora']['vida'] == res['antes']['vida'] and res['agora']['rec'] == res['antes']['rec']}", flush=True)
assert razao <= 1.15, f'PERF: codigo atual {razao:.2f}x mais lento que o snapshot'
print('PORTAO PERF ok', flush=True)
