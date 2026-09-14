"""docs/98 -- paired analysis of the prune-control battery (prune_control_battery
JSON output). Pure CPU: scipy.stats on <=20 numbers per arm, not a GPU
experiment -- allowed per project CLAUDE.md ("numpy/CPU so' pra I/O trivial e
plots"). Not queued through nmd; run directly.

    python src/analyze_prune_control.py <resultado.json>
"""
import sys, json, math
import numpy as np
from scipy import stats


def paired_report(a, b, name_a, name_b, label):
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    d = a - b
    n = len(d)
    t, p = stats.ttest_rel(a, b)
    mean_d = float(d.mean()); sd_d = float(d.std(ddof=1))
    se = sd_d / math.sqrt(n)
    tcrit = stats.t.ppf(0.975, df=n-1)
    lo, hi = mean_d - tcrit*se, mean_d + tcrit*se
    wins = int((d > 0).sum()); losses = int((d < 0).sum()); ties = n - wins - losses
    print(f'  {label}: {name_a} - {name_b}')
    print(f'    n={n}  media_{name_a}={a.mean():.3f}  media_{name_b}={b.mean():.3f}')
    print(f'    diferenca pareada = {mean_d:+.3f}  IC95%=[{lo:+.3f}, {hi:+.3f}]  '
          f't={t:.3f}  p={p:.4g}  vitorias {name_a}={wins}/{n}  {name_b}={losses}/{n}  empates={ties}')
    return dict(n=n, media_a=float(a.mean()), media_b=float(b.mean()), diferenca=mean_d,
                ic95=[lo, hi], t=float(t), p=float(p), vitorias_a=wins, vitorias_b=losses,
                empates=ties)


def main(path):
    d = json.load(open(path))
    cfg = d['config']
    seeds = cfg['evo_seeds']
    modos = d['modos']
    print(f"config: {cfg}")
    print(f"tempo_total_s: {d.get('tempo_total_s')}")
    out = dict(fonte=path, config=cfg, comparacoes={})

    def serie(modo, campo):
        ps = modos[modo]['por_semente']
        return [ps[str(sd)][campo] for sd in seeds]

    print('\n--- fitness de treino (ultima geracao) ---')
    ft = {m: serie(m, 'fit_treino') for m in modos}
    for (x, y) in [('prune', 'generate'), ('prune', 'generate_fine'), ('generate_fine', 'generate')]:
        if x in ft and y in ft:
            out['comparacoes'].setdefault('fit_treino', {})[f'{x}_vs_{y}'] = paired_report(
                ft[x], ft[y], x, y, 'fitness de treino')

    print('\n--- entregas held-out (media de eval_reps replicas) ---')
    et = {m: serie(m, 'entregas_teste') for m in modos}
    for (x, y) in [('prune', 'generate'), ('prune', 'generate_fine'), ('generate_fine', 'generate')]:
        if x in et and y in et:
            out['comparacoes'].setdefault('entregas_teste', {})[f'{x}_vs_{y}'] = paired_report(
                et[x], et[y], x, y, 'entregas held-out')

    print('\n--- avarias held-out (media de eval_reps replicas) ---')
    av = {m: serie(m, 'avarias_teste') for m in modos}
    for (x, y) in [('prune', 'generate'), ('prune', 'generate_fine'), ('generate_fine', 'generate')]:
        if x in av and y in av:
            out['comparacoes'].setdefault('avarias_teste', {})[f'{x}_vs_{y}'] = paired_report(
                av[x], av[y], x, y, 'avarias held-out')

    if 'prune' in modos:
        dens = serie('prune', 'densidade_mascara')
        print(f"\n--- densidade final da mascara (prune, {len(dens)} sementes) ---")
        print(f'  media={np.mean(dens):.3f}  dp={np.std(dens):.3f}  min={min(dens):.3f}  max={max(dens):.3f}')
        out['densidade_mascara_prune'] = dict(media=float(np.mean(dens)), dp=float(np.std(dens)),
                                              min=float(min(dens)), max=float(max(dens)), por_semente=dens)

    outp = path.replace('.json', '-analise.json')
    json.dump(out, open(outp, 'w'), indent=1, ensure_ascii=False)
    print('\nsalvo:', outp)
    return out


if __name__ == '__main__':
    main(sys.argv[1])
