"""One panel and one API over the laboratory database, on the standard library only.

This replaces the habit of growing a viewer per battery. It reads `lab_db` and serves
history; the live panel inside `gpu_evolve` (`--painel`, port 3200) answers a different
question -- what is happening in this process right now -- and stays as it is. The six
`replay_*` binaries also stay: the panel links to what they produce rather than
reimplementing a track view.

    python src/lab_api.py --port 8130
    # then http://localhost:8130

Routes, all read-only:

    GET /                              the panel
    GET /api/batteries                 one row per battery
    GET /api/runs?battery=b1           runs, with their status and configuration
    GET /api/run/<name>                one run: generations, driving curve, artifacts
    GET /api/compare?battery=b1&left=fixed&right=nocost&metric=brake_pct_alive
    GET /api/sql?q=select+...          any SELECT, for an agent that wants its own shape

An agent that can run Python should import `lab_db` directly instead of calling this --
no server, no port, no dependency. The API exists for the browser and for whatever
cannot import Python.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lab_db  # noqa: E402

PANEL = """<!doctype html><meta charset="utf-8"><title>Laboratory</title>
<style>
 :root{color-scheme:light dark}
 body{font:14px/1.45 system-ui,sans-serif;margin:0;background:#fbfbfa;color:#1a1a19}
 header{padding:1rem 1.5rem;border-bottom:1px solid #e3e3e0;background:#fff}
 h1{font-size:1rem;margin:0;font-weight:600}
 header span{color:#6b6b66}
 main{display:grid;grid-template-columns:15rem 1fr;min-height:calc(100vh - 3.6rem)}
 nav{border-right:1px solid #e3e3e0;padding:1rem;background:#fff}
 nav button{display:block;width:100%;text-align:left;border:0;background:none;padding:.45rem .6rem;
   border-radius:5px;font:inherit;cursor:pointer;color:inherit}
 nav button:hover{background:#f0f0ed} nav button[aria-current=true]{background:#e8eef7;font-weight:600}
 nav small{color:#6b6b66;font-weight:400}
 section{padding:1.25rem 1.5rem;overflow-x:auto}
 table{border-collapse:collapse;font-variant-numeric:tabular-nums;margin-bottom:1.5rem}
 th,td{padding:.3rem .65rem;border-bottom:1px solid #e8e8e5;text-align:right;white-space:nowrap}
 th:first-child,td:first-child{text-align:left}
 th{font-weight:600;color:#44443f;border-bottom:1px solid #ccccc6}
 tr.running td{color:#a06a00}
 h2{font-size:.95rem;margin:1.2rem 0 .5rem}
 .agree{color:#6b6b66;font-weight:400}
 .pos{color:#0a7d33} .neg{color:#b3261e}
 canvas{background:#fff;border:1px solid #e3e3e0;border-radius:6px;margin-bottom:1rem}
 @media(prefers-color-scheme:dark){
  body{background:#16161a;color:#e6e6e3} header,nav,canvas{background:#1d1d22;border-color:#33333a}
  nav button:hover{background:#26262c} nav button[aria-current=true]{background:#24313f}
  th,td{border-color:#2b2b31} th{color:#b8b8b2;border-bottom-color:#3a3a42}
 }
 @media(max-width:700px){main{grid-template-columns:1fr}nav{border-right:0;border-bottom:1px solid #e3e3e0}}
</style>
<header><h1>Laboratory <span id="sub">— loading</span></h1></header>
<main><nav id="nav"></nav><section id="body"></section></main>
<script>
const q = (u) => fetch(u).then(r => r.json());
const fmt = (v, d = 2) => v === null || v === undefined ? '–'
  : (typeof v === 'number' ? (Number.isInteger(v) ? v : v.toFixed(d)) : v);

function table(rows, cols, cls = () => '') {
  if (!rows.length) return '<p>(nothing yet)</p>';
  const head = cols.map(c => `<th>${c.label ?? c.key}</th>`).join('');
  const body = rows.map(r => '<tr class="' + cls(r) + '">' +
    cols.map(c => `<td>${c.render ? c.render(r) : fmt(r[c.key], c.d)}</td>`).join('') + '</tr>').join('');
  return `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

function curves(runs, series) {
  const w = 620, h = 200, pad = 34;
  const all = runs.flatMap(r => series[r.name] || []);
  if (!all.length) return '';
  const maxX = Math.max(...all.map(p => p[0])), maxY = Math.max(...all.map(p => p[1]), 1);
  const colour = ['#2d6cdf', '#d2691e', '#0a7d33', '#b3261e', '#7a4fbf', '#0f8f95'];
  const paths = runs.map((r, i) => {
    const pts = series[r.name] || [];
    if (!pts.length) return '';
    const d = pts.map((p, j) => (j ? 'L' : 'M') +
      (pad + p[0] / maxX * (w - pad - 8)) + ' ' + (h - pad - p[1] / maxY * (h - pad - 12))).join(' ');
    return `<path d="${d}" fill="none" stroke="${colour[i % 6]}" stroke-width="1.6"/>`;
  }).join('');
  const legend = runs.map((r, i) =>
    `<tspan fill="${colour[i % 6]}" x="${pad}" dy="${i ? 12 : 0}">■ ${r.name}</tspan>`).join('');
  return `<svg width="${w}" height="${h + runs.length * 12 + 16}" style="max-width:100%">
    <line x1="${pad}" y1="${h - pad}" x2="${w - 8}" y2="${h - pad}" stroke="#bbb"/>
    <line x1="${pad}" y1="8" x2="${pad}" y2="${h - pad}" stroke="#bbb"/>
    <text x="4" y="14" font-size="10" fill="#777">${fmt(maxY, 0)}</text>
    <text x="${w - 40}" y="${h - pad + 14}" font-size="10" fill="#777">gen ${maxX}</text>
    ${paths}<text font-size="10" y="${h + 6}">${legend}</text></svg>`;
}

async function showBattery(id) {
  document.querySelectorAll('nav button').forEach(b =>
    b.setAttribute('aria-current', b.dataset.id === id));
  const runs = await q('/api/runs?battery=' + encodeURIComponent(id));
  const series = {};
  await Promise.all(runs.map(async r => {
    const d = await q('/api/run/' + encodeURIComponent(r.name));
    series[r.name] = d.generations.map(g => [g.gen, g.median_progress_m]);
  }));
  const arms = [...new Set(runs.map(r => r.arm))];
  let compare = '';
  for (let i = 0; i < arms.length; i++) for (let j = i + 1; j < arms.length; j++) {
    const rows = await Promise.all(
      ['brake_pct_alive', 'brake_alone_pct_alive', 'near_wall_pct_alive',
       'mean_speed_mps', 'impacts_per_km', 'distance_m'].map(m =>
        q(`/api/compare?battery=${id}&left=${arms[i]}&right=${arms[j]}&metric=${m}`)));
    const usable = rows.filter(r => r.n > 0);
    if (!usable.length) continue;
    compare += `<h2>${arms[i]} − ${arms[j]} <span class="agree">(pareado, só corridas terminadas)</span></h2>` +
      table(usable, [
        {key: 'metric', label: 'métrica'},
        {key: 'mean', label: 'diferença', render: r =>
          `<span class="${r.mean > 0 ? 'pos' : 'neg'}">${r.mean > 0 ? '+' : ''}${fmt(r.mean, 3)}</span>`},
        {key: 'n', label: 'n'},
        {key: 'agree', label: 'mesma direção', render: r => `${r.agree}/${r.n}`}]);
  }
  document.getElementById('body').innerHTML =
    `<h2>avanço mediano por geração</h2>${curves(runs, series)}` +
    `<h2>corridas</h2>` + table(runs, [
      {key: 'name', label: 'corrida'}, {key: 'arm', label: 'braço'}, {key: 'seed'},
      {key: 'status', label: 'estado'},
      {key: 'gens_complete', label: 'gerações', render: r => `${r.gens_complete}/${r.gens_requested}`},
      {key: 'beings', label: 'seres'}, {key: 'ticks', label: 'tiques'},
      {key: 'wall_cost', label: 'custo parede'}, {key: 'impact_cost', label: 'custo impacto'},
      {key: 'replays', label: 'replays'}], r => r.status === 'running' ? 'running' : '') +
    compare;
}

q('/api/batteries').then(bs => {
  document.getElementById('sub').textContent =
    `— ${bs.length} baterias, ${bs.reduce((a, b) => a + b.runs, 0)} corridas`;
  document.getElementById('nav').innerHTML = bs.map(b =>
    `<button data-id="${b.battery}">${b.battery}<br><small>${b.finished}/${b.runs} terminadas · ${b.arms} braços</small></button>`).join('');
  document.querySelectorAll('nav button').forEach(b =>
    b.onclick = () => showBattery(b.dataset.id));
  if (bs.length) showBattery(bs[0].battery);
});
</script>
"""


class Handler(BaseHTTPRequestHandler):
    db_path = lab_db.DEFAULT_PATH

    def log_message(self, fmt, *args):  # quieter than the default one-line-per-request
        pass

    def _send(self, payload: object, code: int = 200) -> None:
        body = json.dumps(payload, default=str).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - the base class names it
        parsed = urllib.parse.urlparse(self.path)
        query = {k: v[0] for k, v in urllib.parse.parse_qs(parsed.query).items()}
        route = parsed.path
        try:
            db = lab_db.connect(self.db_path)
        except sqlite3.Error as error:
            return self._send({'error': str(error)}, 500)
        try:
            if route == '/':
                body = PANEL.encode()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif route == '/api/batteries':
                self._send([dict(r) for r in lab_db.batteries(db)])
            elif route == '/api/runs':
                rows = [dict(r) for r in lab_db.runs(db, battery=query.get('battery'),
                                                    arm=query.get('arm'))]
                for row in rows:
                    row['replays'] = db.execute(
                        "SELECT COUNT(*) FROM artifact WHERE run_name = ? AND kind = 'replay'",
                        (row['name'],)).fetchone()[0]
                self._send(rows)
            elif route.startswith('/api/run/'):
                name = urllib.parse.unquote(route[len('/api/run/'):])
                run = db.execute('SELECT * FROM run WHERE name = ?', (name,)).fetchone()
                if run is None:
                    return self._send({'error': f'no such run: {name}'}, 404)
                self._send({
                    'run': dict(run),
                    'generations': [dict(r) for r in db.execute(
                        'SELECT * FROM generation WHERE run_name = ? ORDER BY gen', (name,))],
                    'driving': [dict(r) for r in db.execute(
                        'SELECT * FROM driving WHERE run_name = ? ORDER BY gen', (name,))],
                    'artifacts': [dict(r) for r in db.execute(
                        'SELECT kind, gen, path, bytes FROM artifact WHERE run_name = ?'
                        ' ORDER BY kind, gen', (name,))],
                })
            elif route == '/api/compare':
                self._send(lab_db.paired(
                    db, query.get('battery', ''), query.get('left', ''),
                    query.get('right', ''), query.get('metric', 'brake_pct_alive'),
                    query.get('include_running') == '1'))
            elif route == '/api/sql':
                statement = query.get('q', '')
                lowered = statement.strip().lower()
                if not (lowered.startswith('select') or lowered.startswith('with')):
                    return self._send({'error': 'only SELECT/WITH are served here'}, 400)
                self._send([dict(r) for r in db.execute(statement).fetchall()])
            else:
                self._send({'error': f'no such route: {route}'}, 404)
        except (sqlite3.Error, ValueError) as error:
            self._send({'error': str(error)}, 400)
        finally:
            db.close()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--port', type=int, default=8130)
    ap.add_argument('--db', default=lab_db.DEFAULT_PATH)
    ap.add_argument('--bind', default='127.0.0.1',
                    help='loopback by default: this serves absolute paths on the machine')
    a = ap.parse_args()
    Handler.db_path = a.db
    server = ThreadingHTTPServer((a.bind, a.port), Handler)
    print(f'laboratory panel on http://{a.bind}:{a.port}  (database {a.db})')
    server.serve_forever()


if __name__ == '__main__':
    main()
