"""Selection operators over a fixed map — the 'prune, don't generate' hypothesis
(docs/16-poda.md: pruning beat free mutation, p<1e-5, 18/20 seeds, 35 % of connections kept).

Neuron masks (B, n) float {0,1}: a neuron selected out emits nothing.
Pruning step (born dense): off with p_off, back on with p_on.
Controls that keep size/degree but destroy the map's information:
  shuffle_targets  — permute postsynaptic endpoints (out/in-degree and signs preserved)
  shuffle_signs    — same graph, signs redrawn with the same inhibitory fraction
"""
from __future__ import annotations

import numpy as np

from .connectome import Connectome


def dense_mask(B: int, n: int) -> np.ndarray:
    return np.ones((B, n), dtype=np.float32)


def prune_step(mask: np.ndarray, rng: np.random.Generator, p_off: float = 0.05, p_on: float = 0.015,
               protect: np.ndarray | None = None) -> np.ndarray:
    """One generation of the pruning operator from docs/16 (5 % off, 1.5 % on)."""
    m = mask.copy()
    off = rng.random(m.shape) < p_off
    on = rng.random(m.shape) < p_on
    m[off] = 0.0
    m[on] = 1.0
    if protect is not None:                      # bound I/O neurons are never pruned
        m[:, protect] = 1.0
    return m


def shuffle_targets(cm: Connectome, seed: int) -> Connectome:
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(cm.post))
    return Connectome(cm.n, cm.root_ids, cm.pre, cm.post[perm], cm.weight, cm.neurons)


def shuffle_signs(cm: Connectome, seed: int) -> Connectome:
    rng = np.random.default_rng(seed)
    frac_inh = float((cm.weight < 0).mean())
    sign = np.where(rng.random(len(cm.weight)) < frac_inh, -1, 1).astype(np.int32)
    return Connectome(cm.n, cm.root_ids, cm.pre, cm.post, np.abs(cm.weight) * sign, cm.neurons)


def shuffle_weights(cm: Connectome, seed: int) -> Connectome:
    """Same graph and signs, synapse counts permuted across edges."""
    rng = np.random.default_rng(seed)
    mag = np.abs(cm.weight)[rng.permutation(len(cm.weight))]
    return Connectome(cm.n, cm.root_ids, cm.pre, cm.post, mag * np.sign(cm.weight).astype(np.int32), cm.neurons)


def filter_edges(cm: Connectome, min_weight: int) -> Connectome:
    """Keep only edges with |synapse count| >= min_weight (3 keeps 33 % of edges, 76 % of synapses)."""
    if min_weight <= 1:
        return cm
    k = np.abs(cm.weight) >= min_weight
    return Connectome(cm.n, cm.root_ids, cm.pre[k], cm.post[k], cm.weight[k], cm.neurons)


MAP_VARIANTS = {'real': lambda cm, s: cm, 'shuffle_targets': shuffle_targets, 'shuffle_signs': shuffle_signs,
                'shuffle_weights': shuffle_weights}
