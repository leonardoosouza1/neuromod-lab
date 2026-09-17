"""A request id present in both pedidos/ (live) and feitos/ (stale copy) mirrors as live."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import lab_db  # noqa: E402


def test_live_request_wins_over_stale_done_copy(tmp_path):
    spool = tmp_path / '_nmd'
    for folder in ('pedidos', 'feitos', 'estado'):
        (spool / folder).mkdir(parents=True)
    req = {'id': 'b9_x', 'script': 'gpu_evolve', 'args': {}}
    (spool / 'pedidos' / 'b9_x.json').write_text(json.dumps(req))
    (spool / 'feitos' / 'b9_x.json').write_text(json.dumps(req))
    (spool / 'estado' / 'b9_x.json').write_text(json.dumps({'id': 'b9_x', 'fase': 'rodando'}))
    db = lab_db.connect(str(tmp_path / 'lab.db'))
    lab_db.mirror_queue(db, spool=str(spool))
    rows = db.execute('select id, state from queue_mirror').fetchall()
    assert [tuple(r) for r in rows] == [('b9_x', 'running')]
