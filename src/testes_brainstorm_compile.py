"""[revisor 09-09, v2] flags novas sob torch.compile == eager, UMA POR VEZ e todas juntas. v1 comparava rodar() compilado com um laco eager
escrito a mao — que nao tinha a contabilidade de custo (metab/ativ) que vive em rodar(): falhava por culpa do laco, nao das flags.
v2: o MESMO rodar() em dois subprocessos (NM_COMPILE=0 e =1), cada um grava pos/metab/vida por flag; o pai compara.
Tolerancia = a de testes_campo (empates de argmax: <= 3 seres em 128); metab comparado so nos seres de trajetoria igual (em modo
ativacao/disparo o metab depende da trajetoria). Exit 1 e diz QUAL flag falhou."""
import sys, os, subprocess, json
AQUI = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else '/media/llm-data/universe-runs/neuromod-lab-taxi/e72'
FLAGS = {'nenhuma': {}, 'temp_decisao': dict(temp_decisao=.3), 'talamo_fixo': dict(talamo_norm='fixo'), 'canais': dict(custo_canais=('fome', 'agua', 'calor'), custo_gene=.3, custo_basal=.15),
         'disparo': dict(custo_gene=.3, custo_modo='disparo'), 'cortex_amp': dict(cortex_amp=2.), 'hip_esc': dict(hip_esc=1.),
         'todas': dict(temp_decisao=.3, talamo_norm='fixo', custo_canais=('fome', 'agua', 'calor'), custo_gene=.3, custo_modo='disparo', custo_basal=.15, cortex_amp=2., hip_esc=1.)}
if os.environ.get('_NM_FILHO'):
    import torch; sys.path.insert(0, AQUI); from campo import *; from completo import SerCompleto
    mapas = [gerar_mapa(1000, L=200., distinto=True)]; g = torch.Generator(device=DEV); g.manual_seed(5)
    W = torch.randn(64, SerCompleto.NP, generator=g, device=DEV)*.3; W[:, :Linear.NP] = torch.randn(64, Linear.NP, generator=g, device=DEV)*.5; res = {}
    for nome, kw in FLAGS.items():
        c = CfgCampo(L=200., fitness='riqueza')
        for k, v in kw.items(): setattr(c, k, v)
        m = rodar(SerCompleto, W, mapas, c, T=200, seed=3, R=2); res[nome] = dict(pos=m.pos.cpu(), metab=m.metab.cpu(), vida=m.vida.cpu())
    torch.save(res, os.path.join(OUT, f'bc_compile{os.environ["NM_COMPILE"]}.pt')); print('filho NM_COMPILE', os.environ['NM_COMPILE'], 'ok', flush=True); sys.exit(0)
os.makedirs(OUT, exist_ok=True)
for modo in ('0', '1'):
    env = dict(os.environ, _NM_FILHO='1', NM_COMPILE=modo); r = subprocess.run([sys.executable, os.path.abspath(__file__), '--out', OUT], env=env)
    if r.returncode != 0: print('PORTAO BRAINSTORM COMPILE FALHOU: filho NM_COMPILE', modo, 'exit', r.returncode, flush=True); sys.exit(1)
import torch; a = torch.load(os.path.join(OUT, 'bc_compile0.pt')); b = torch.load(os.path.join(OUT, 'bc_compile1.pt')); falhas = []
for nome in FLAGS:
    igual = (a[nome]['pos'] - b[nome]['pos']).abs().max(1).values <= 1e-6; dif = int((~igual).sum()); dm = float((a[nome]['metab'] - b[nome]['metab']).abs()[igual].max()) if bool(igual.any()) else float('inf'); dv = float((a[nome]['vida'] - b[nome]['vida']).abs().max())
    ok = dif <= 3 and dm < 1e-5; falhas += [] if ok else [nome]
    print(f'  {nome:14} eager vs compilado (mesmo rodar): seres com pos diferente {dif:3d}/128 (tolerancia 3) | max dif metab {dm:.1e} vida {dv:.2e}', 'OK' if ok else 'FALHOU', flush=True)
print('PORTAO BRAINSTORM COMPILE', 'ok' if not falhas else f'FALHOU em {falhas}', flush=True); sys.exit(0 if not falhas else 1)
