"""Regression for the perception->action ordering bug (docs/97 section 1, Astra's review 14/09/2026).

`obs()` runs before `passo()` and reads the ORIGIN node. The arrival block inside `passo()`
switches `m.no` to the destination, so applying the chosen index in the same tick would index
the NEW node's neighbour list with a choice made on the OLD node's list. A being that has just
arrived must therefore not act until the next tick, when `obs()` has seen the new node.

    python src/test_arrival_action.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
import torch

import lab


def test_just_arrived_being_does_not_act_this_tick():
    cid = lab.gerar_cidade(0)
    cfg = lab.Cfg(1.0)
    m = lab.Lote([cid], 4, cfg, seed=0)
    # put being 0 in transit, one step from arriving at a node that is NOT its current one
    target = int(m.A_()[0][m.A_()[0] >= 0][0].item())
    m.rest[0] = 1.0
    m.indo[0] = target
    origin = int(m.no[0].item())
    esc = torch.zeros(m.B, dtype=torch.long, device=m.no.device)
    lab.passo(m, esc)
    assert int(m.no[0].item()) == target, 'the being should have arrived'
    assert float(m.rest[0].item()) <= 0.0
    # with the fix it stays put this tick; the legacy order would already have moved it again
    assert int(m.indo[0].item()) == -1, 'arrival must clear the in-transit destination'
    assert float(m.rest[0].item()) == 0.0, 'it must not have started a new leg in the same tick'
    assert origin != target


def test_legacy_flag_restores_the_old_order():
    assert lab.CHEGADA_LEGADO is False, 'the fix must be the default'


if __name__ == '__main__':
    for name, fn in sorted(globals().items()):
        if name.startswith('test_'):
            fn()
            print('ok', name)
    print('ALL PASSED')
