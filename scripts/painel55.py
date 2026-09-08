"""Monta docs/painel-55-pico.html a partir dos resultados (reprodutível). Uso: python scripts/painel55.py [--snr JSON]"""
import json, re, os, sys, argparse
R = '/media/llm-data/universe-runs/neuromod-lab-taxi'; REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument('--snr', default=R + '/e66/diag_snr_q8.json'); a = ap.parse_args()
def traj(p):
    d = {}
    for l in open(p, errors='ignore'):
        m = re.match(r'\s*ger\s+(\d+)\s*\|\s*(.*?)\s*\(melhor', l)
        if m and int(m.group(1)) not in d: d[int(m.group(1))] = [float(x) for x in m.group(2).split()]
    return d
out = {'traj': {'GA': traj(R + '/_nmd/log/q8_busca8x.log'), 'ES s.1': traj(R + '/_nmd/log/q9b2_es_s01.log'), 'ES s.3': traj(R + '/_nmd/log/q9c2_es_s03.log')}, 'bracos': {}}
ks = ['mortos', 'panes', 'ent', 'fit', 'dinh', 'res', 'n_posto']
arms = [('GA', 'e64/e43_busca8x_L200.json', 'linear'), ('ES s.1', 'e65/e43_es_s01_L200.json', 'linear'), ('ES s.3', 'e65/e43_es_s03_L200.json', 'linear'), ('GA bilinear-risco', 'e64/e43_busca8x_L200.json', 'bilinear risco (esc 3)'), ('ES s.1 R16', 'e67/e43_es_s01_R16_L200.json', 'linear')]
for nome, f, arm in arms:
    p = os.path.join(R, f)
    if not os.path.exists(p): print('sem', f); continue
    b = json.load(open(p))['bracos'].get(arm)
    if b: out['bracos'][nome] = {k: b[k + '_por_semente'] for k in ks}
if 'ES s.1 R16' in out['bracos']: out['traj']['ES s.1 R16'] = traj(R + '/_nmd/log/q11_es_s01_R16.log')
out['snr'] = json.load(open(a.snr))['sigmas']
t = open(os.path.join(REPO, 'docs', 'painel-55-pico.tpl.html')).read()
open(os.path.join(REPO, 'docs', 'painel-55-pico.html'), 'w').write(t.replace('/*DATA*/', json.dumps(out, separators=(',', ':'))))
print('painel ok; bracos', list(out['bracos']), '| F na snr:', 'F' in out['snr']['0.3'], '|', os.path.getsize(os.path.join(REPO, 'docs', 'painel-55-pico.html'))//1024, 'KB')
