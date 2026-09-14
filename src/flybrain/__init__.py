"""flybrain — use the FlyWire (Drosophila, v783) connectome as a fixed brain map.

Design rule (Leonardo, 14/09/2026): we do NOT generate a brain; we SELECT on the
fly's own map. The map (138 639 neurons, 15.1 M signed connections) is loaded once
and shared; what evolves is a selection over it (masks, I/O bindings).

Modules
  connectome  load + cache the map (CSR both ways) and the neuron table
  dynamics    batched torch dynamics on the map: LIF (Shiu et al. 2024) and rate
  selection   masks over neurons/edges; pruning operators; shuffled controls
  io_map      bind task observations to afferent groups, read commands from efferents
"""
from .connectome import Connectome, load_connectome  # noqa: F401
