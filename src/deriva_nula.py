"""[CS DERIVA-DELEGACAO §2] MODELO NULO DA DERIVA: populacao nasce transparente (zeros) ou semeada (sigma0/sigma_espinha) e anda sem
selecao com a MESMA mutacao da evolucao (lab.evoluir_sementes: N(0, .3), corte +-5). Sai dof(g) (fracao |w| > gene_min) e fracao do
cortex encostado na trava (|.5 tanh(w)| > .4) nas geracoes de referencia. Serve de regua: dof de campeao so e evidencia de selecao
se ficar FORA do nulo na mesma geracao efetiva. GPU, segundos."""
import sys, os, json, argparse; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ['NM_COMPILE'] = '0'
import torch; from campo import DEV, Linear; from completo import SerCompleto
ap = argparse.ArgumentParser(); ap.add_argument('--out', default='/media/llm-data/universe-runs/neuromod-lab-taxi/e72'); ap.add_argument('--P', type=int, default=4000); ap.add_argument('--G', type=int, default=200)
ap.add_argument('--sigma-mut', type=float, default=.3); ap.add_argument('--gene-min', type=float, default=.5); ap.add_argument('--sigma0', type=float, default=0.); ap.add_argument('--sigma-espinha', type=float, default=0.); a = ap.parse_args()
g = torch.Generator(device=DEV); g.manual_seed(11); NP = SerCompleto.NP; o = SerCompleto.O_COR; nc = SerCompleto.N_COR
W = torch.randn(a.P, NP, generator=g, device=DEV)*a.sigma0; W[:, :Linear.NP] = torch.randn(a.P, Linear.NP, generator=g, device=DEV)*a.sigma_espinha
marcos = [0, 5, 10, 20, 30, 45, 60, 90, 120, 200]; out = {}
def mede(it):
    dof = float((W[:, Linear.NP:].abs() > a.gene_min).float().mean()); trava = float(((.5*torch.tanh(W[:, o:o+nc])).abs() > .4).float().mean()); dof_esp = float((W[:, :Linear.NP].abs() > a.gene_min).float().mean())
    out[str(it)] = dict(dof_novos=dof, dof_espinha=dof_esp, cortex_trava=trava); print(f'  ger {it:>3} | dof genes novos {dof:.3f} | dof espinha {dof_esp:.3f} | cortex na trava {trava:.3f}', flush=True)
print(f'DERIVA NULA: P {a.P} NP {NP} sigma_mut {a.sigma_mut} corte +-5 gene_min {a.gene_min} semeadura sigma0 {a.sigma0} espinha {a.sigma_espinha}', flush=True); mede(0)
for it in range(1, a.G + 1):
    W = (W + torch.randn(a.P, NP, generator=g, device=DEV)*a.sigma_mut).clamp(-5, 5)
    if it in marcos: mede(it)
os.makedirs(a.out, exist_ok=True); p = os.path.join(a.out, f'deriva_nula_s{a.sigma0}_e{a.sigma_espinha}.json'); json.dump(dict(args=vars(a), NP=NP, N_novos=NP - Linear.NP, marcos=out), open(p, 'w'), indent=1); print('gravado', p, flush=True)
