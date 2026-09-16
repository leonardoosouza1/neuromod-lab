"""Drive a pre-registered battery through its stages with no LLM in the loop.

A battery spec (`batteries/<name>.json`) lists stages that run in order:

    requests        arms x seeds training runs queued on the nmd spool
    champion_eval   freeze the final champion of each run and evaluate it on tracks
    command         local commands (ingest, analysis) run in the repo root

The runner only waits and hands work to the nmd daemon; it never touches the GPU itself.
Everything it decides is written to one line of `_battery/events.log`. A session that must
react to the battery runs `battery_runner.py wait`, which blocks at zero token cost and
exits when a DONE/FAIL/IDLE event appears, so the model is woken only when a decision is
needed.

It is idempotent: a request that is already queued, running or finished is never queued
again, so after a reboot the same `run` command resumes where the battery stopped.

    python scripts/battery_runner.py run batteries/b6.json     # detach with setsid nohup
    python scripts/battery_runner.py status
    python scripts/battery_runner.py wait                       # blocks until an event
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import enqueue_champion_eval as champ  # noqa: E402

BASE = champ.BASE
SPOOL = champ.SPOOL
STATE_ROOT = os.path.join(BASE, '_battery')
EVENTS = os.path.join(STATE_ROOT, 'events.log')
CURSOR = os.path.join(STATE_ROOT, 'wait.cursor')  # byte offset of the last event a waiter saw
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON = '/home/leonardo/projects/LLM/.venv-rocm/bin/python'
WAKE_LEVELS = ('DONE', 'FAIL', 'IDLE')


def now() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M')


def event(level: str, battery: str, text: str) -> None:
    os.makedirs(STATE_ROOT, exist_ok=True)
    with open(EVENTS, 'a') as f:
        f.write(f'{now()} {level} {battery} {text}\n')


def pid_alive(pid) -> bool:
    try:
        os.kill(int(pid), 0)
        return True
    except (OSError, TypeError, ValueError):
        return False


def request_status(rid: str) -> str:
    """queued | running | stale | ok | failed | refused | absent, read from the nmd spool.

    nmd keeps a request file in `pedidos/` while it runs and moves it to `feitos/` only when
    it ends, so a live `estado` must be checked before the queue.
    """
    state = None
    path = os.path.join(SPOOL, 'estado', f'{rid}.json')
    if os.path.exists(path):
        try:
            with open(path) as f:
                state = json.load(f)
        except (OSError, json.JSONDecodeError):
            return 'running'  # being rewritten by the daemon heartbeat
    if state and state.get('fase') == 'rodando' and pid_alive(state.get('pid')):
        return 'running'
    if glob.glob(os.path.join(SPOOL, 'pedidos', f'*_{rid}.json')):
        return 'queued'
    if state:
        if state.get('fase') == 'terminou':
            return 'ok' if state.get('exit_code') == 0 else 'failed'
        return 'stale'
    if glob.glob(os.path.join(SPOOL, 'recusados', f'*_{rid}.json')):
        return 'refused'
    return 'absent'


def queue_pressure() -> tuple[int, int]:
    """(waiting requests, live running requests) across the whole daemon."""
    live = set()
    for path in glob.glob(os.path.join(SPOOL, 'estado', '*.json')):
        try:
            with open(path) as f:
                state = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if state.get('fase') == 'rodando' and pid_alive(state.get('pid')):
            live.add(state.get('id'))
    waiting = [p for p in glob.glob(os.path.join(SPOOL, 'pedidos', '*.json'))
               if os.path.basename(p)[:-5].split('_', 1)[-1] not in live]
    return len(waiting), len(live)


def daemon_alive() -> bool:
    out = subprocess.run(['pgrep', '-f', 'scripts/nmd.py'], capture_output=True, text=True).stdout
    return any(pid.strip() and int(pid) != os.getpid() for pid in out.split())


def train_requests(spec: dict, stage: dict) -> list[dict]:
    out = []
    for seed in stage['seeds']:
        for arm, extra in stage['arms'].items():
            rid = f"{spec['battery']}_{arm}_s{seed}"
            args = dict(stage['base_args'])
            args.update(extra)
            args['seed'] = seed
            out.append({'id': rid, 'script': 'universe_run', 'out': rid, 'env': {},
                        'args': args, 'battery': spec['battery']})
    return out


class Runner:
    def __init__(self, spec_path: str):
        with open(spec_path) as f:
            self.spec = json.load(f)
        self.name = self.spec['battery']
        self.state_path = os.path.join(STATE_ROOT, self.name, 'state.json')
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        self.state = {'battery': self.name, 'spec': os.path.abspath(spec_path), 'stages': {},
                      'retried': []}
        if os.path.exists(self.state_path):
            with open(self.state_path) as f:
                self.state.update(json.load(f))
        self.warned_daemon = False

    def save(self) -> None:
        self.state['updated'] = now()
        tmp = self.state_path + '.tmp'
        with open(tmp, 'w') as f:
            json.dump(self.state, f, indent=1)
        os.replace(tmp, self.state_path)

    def stage_ids(self, name: str) -> list[str]:
        return self.state['stages'].get(name, {}).get('ids', [])

    def settle(self, stage: dict, ids: list[str], submit) -> bool:
        """Submit what is absent, retry a stale request once, report when all are final."""
        counts: dict[str, int] = {}
        failed = []
        for rid in ids:
            status = request_status(rid)
            if status == 'absent':
                submit(rid)
                status = 'queued'
            elif status == 'stale' and rid not in self.state['retried']:
                self.state['retried'].append(rid)
                event('INFO', self.name, f'{rid} stale (pid dead, e.g. reboot): resubmitted once')
                submit(rid)
                status = 'queued'
            counts[status] = counts.get(status, 0) + 1
            if status in ('failed', 'refused', 'stale'):
                failed.append(rid)
        record = self.state['stages'].setdefault(stage['name'], {})
        record.update(ids=ids, counts=counts)
        final = sum(counts.get(k, 0) for k in ('ok', 'failed', 'refused', 'stale'))
        if final < len(ids):
            record['status'] = 'waiting'
            return False
        record.update(status='done', failed=failed)
        level = 'FAIL' if failed else 'INFO'
        event(level, self.name, f"stage {stage['name']} finished: {counts.get('ok', 0)}/{len(ids)} ok"
              + (f"; failed: {' '.join(failed)}" if failed else ''))
        return True

    def run_requests(self, stage: dict) -> bool:
        requests = {r['id']: r for r in train_requests(self.spec, stage)}
        prefix = stage.get('prefix', '3')
        return self.settle(stage, list(requests), lambda rid: champ.write_request(requests[rid], prefix))

    def run_champion_eval(self, stage: dict) -> bool:
        record = self.state['stages'].setdefault(stage['name'], {})
        ids, sources = [], {}
        for group in stage['groups']:
            runs = list(group.get('runs', []))
            for source in group.get('runs_from', []):
                runs += self.stage_ids(source)
            for run in runs:
                if request_status(run) != 'ok':
                    if run not in record.get('skipped', []):
                        record.setdefault('skipped', []).append(run)
                        event('FAIL', self.name, f'{run} did not finish ok; its champion is not evaluated')
                    continue
                for track in group['tracks']:
                    rid = f'{run}_eval_t{track}'
                    ids.append(rid)
                    sources[rid] = (run, track)
        frozen: dict[str, tuple[str, dict]] = {}

        def submit(rid: str) -> None:
            run, track = sources[rid]
            if run not in frozen:
                frozen[run] = champ.freeze_champion(run)
            path, args = frozen[run]
            request = champ.eval_request(run, track, path, args, stage.get('ticks', 20000),
                                         stage.get('beings', 8))
            champ.write_request(request, stage.get('prefix', '2'))

        return self.settle(stage, ids, submit)

    def run_command(self, stage: dict) -> bool:
        record = self.state['stages'].setdefault(stage['name'], {})
        log_path = os.path.join(STATE_ROOT, self.name, f"{stage['name']}.out")
        with open(log_path, 'w') as log:
            for argv in stage['commands']:
                argv = [PYTHON if a == '{python}' else a for a in argv]
                log.write(f"$ {' '.join(argv)}\n")
                log.flush()
                rc = subprocess.run(argv, cwd=REPO, stdout=log, stderr=subprocess.STDOUT).returncode
                if rc != 0:
                    record.update(status='done', failed=[' '.join(argv)], exit_code=rc)
                    event('FAIL', self.name, f"stage {stage['name']} exit {rc}: see {log_path}")
                    return True
        record.update(status='done', failed=[], output=log_path)
        event('INFO', self.name, f"stage {stage['name']} ok: {log_path}")
        return True

    def step(self) -> bool:
        """Advance as far as possible; True when every stage is done."""
        if not daemon_alive():
            if not self.warned_daemon:
                event('FAIL', self.name, 'nmd daemon is not running; nothing can advance')
                self.warned_daemon = True
            return False
        self.warned_daemon = False
        handlers = {'requests': self.run_requests, 'champion_eval': self.run_champion_eval,
                    'command': self.run_command}
        for stage in self.spec['stages']:
            if self.state['stages'].get(stage['name'], {}).get('status') == 'done':
                continue
            done = handlers[stage['kind']](stage)
            self.save()
            if not done:
                return False
        return True

    def ingest_progress(self) -> None:
        """Re-ingest this battery's own runs so the panel shows a battery in flight; the final
        `ingest` stage still ingests the whole tree. Failures are logged, never fatal."""
        log_path = os.path.join(STATE_ROOT, self.name, 'progress_ingest.out')
        with open(log_path, 'w') as log:
            subprocess.run([PYTHON, 'src/lab_db.py', 'ingest', BASE, '--match', f'{self.name}_*'],
                           cwd=REPO, stdout=log, stderr=subprocess.STDOUT)

    def loop(self, interval: int, ingest_every: int) -> None:
        event('INFO', self.name, f"runner started (pid {os.getpid()}): {self.state['spec']}")
        last_ingest = 0.0
        while not self.step():
            if ingest_every and time.time() - last_ingest >= ingest_every:
                self.ingest_progress()
                last_ingest = time.time()
            time.sleep(interval)
        self.state['finished'] = now()
        self.save()
        event('DONE', self.name, f'all stages done; state {self.state_path}')


def status() -> None:
    for path in sorted(glob.glob(os.path.join(STATE_ROOT, '*', 'state.json'))):
        with open(path) as f:
            state = json.load(f)
        parts = []
        for name, record in state['stages'].items():
            counts = ','.join(f'{k}={v}' for k, v in sorted(record.get('counts', {}).items()))
            parts.append(f"{name}:{record.get('status')}" + (f'[{counts}]' if counts else ''))
        print(f"{state['battery']:6s} updated {state.get('updated')} {' '.join(parts)}")
    queued, running = queue_pressure()
    print(f'nmd queued={queued} running={running} daemon={"up" if daemon_alive() else "DOWN"}')


def wait(idle_minutes: int, max_hours: float) -> None:
    """Block until a wake-level event is appended, the GPU queue sits idle, or time runs out."""
    size = os.path.getsize(EVENTS) if os.path.exists(EVENTS) else 0
    try:
        with open(CURSOR) as f:
            start = min(int(f.read().strip()), size)
    except (OSError, ValueError):
        start = size
    deadline = time.time() + max_hours * 3600
    idle_since = None
    while time.time() < deadline:
        if os.path.exists(EVENTS) and os.path.getsize(EVENTS) > start:
            with open(EVENTS) as f:
                f.seek(start)
                fresh = f.read().splitlines()
            wake = [line for line in fresh if line.split(' ')[2:3] and line.split(' ')[2] in WAKE_LEVELS]
            if wake:
                print('\n'.join(fresh[-15:]))
                with open(CURSOR, 'w') as f:
                    f.write(str(os.path.getsize(EVENTS)))
                return
        queued, running = queue_pressure()
        if queued == 0 and running == 0:
            idle_since = idle_since or time.time()
            if time.time() - idle_since >= idle_minutes * 60:
                print(f'{now()} IDLE gpu queue empty for {idle_minutes} min')
                return
        else:
            idle_since = None
        time.sleep(30)
    print(f'{now()} TIMEOUT no wake event in {max_hours} h')


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='command', required=True)
    p = sub.add_parser('run')
    p.add_argument('spec')
    p.add_argument('--interval', type=int, default=60)
    p.add_argument('--once', action='store_true', help='advance one step and exit')
    p.add_argument('--ingest-every', type=int, default=180,
                   help='seconds between progress ingests of this battery (0 disables)')
    sub.add_parser('status')
    p = sub.add_parser('wait')
    p.add_argument('--idle-minutes', type=int, default=5)
    p.add_argument('--max-hours', type=float, default=6)
    a = ap.parse_args()
    if a.command == 'run':
        runner = Runner(a.spec)
        if a.once:
            runner.step()
            runner.save()
        else:
            runner.loop(a.interval, a.ingest_every)
    elif a.command == 'status':
        status()
    else:
        wait(a.idle_minutes, a.max_hours)


if __name__ == '__main__':
    main()
