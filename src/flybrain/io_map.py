"""Bind task observations to afferent groups and read commands from efferent groups.

Everything here is a CHOICE over the fly's own map — no weights are generated.
  input k  -> one afferent group (all its neurons receive obs[k] * gain)
  output j -> (plus group, minus group) of efferent neurons; cmd_j = mean rate(plus) - mean rate(minus)
Groups are cell types (Schlegel et al. 2024 annotations), so a binding is biologically
addressable ("channel 3 drives the Johnston's organ JO-C neurons").
"""
from __future__ import annotations

import numpy as np
import torch

from .connectome import Connectome


class Groups:
    """Neuron groups (index arrays) with a sparse membership matrix for scatter/gather."""

    def __init__(self, cm: Connectome, flow: str, min_size: int = 1, device: str = 'cuda'):
        nrn = cm.neurons
        sel = nrn[nrn.flow == flow]
        key = sel['cell_type'].where(sel['cell_type'] != '', sel['cell_class'] + '?')  # unnamed types fall back to class
        grouped = sel.groupby(key.to_numpy()).indices
        self.names = [k for k, v in grouped.items() if len(v) >= min_size]
        self.members = [sel.index.to_numpy()[grouped[k]] for k in self.names]
        self.K = len(self.names)
        rows = np.concatenate([np.full(len(m), i) for i, m in enumerate(self.members)])
        cols = np.concatenate(self.members)
        vals = np.concatenate([np.full(len(m), 1.0 / len(m), dtype=np.float32) for m in self.members])
        self.n = cm.n
        # M: (K, n) mean-membership (rows sum to 1); M1: (n, K) plain membership (scatter)
        self.M = torch.sparse_coo_tensor(np.stack([rows, cols]), vals, (self.K, cm.n)).coalesce().to(device)
        self.M1 = torch.sparse_coo_tensor(np.stack([cols, rows]), np.ones(len(rows), np.float32), (cm.n, self.K)).coalesce().to(device)
        self.sizes = np.array([len(m) for m in self.members])
        self.device = device

    def mean_rates(self, r: torch.Tensor) -> torch.Tensor:
        """r (n, B) -> (K, B) mean rate per group."""
        return torch.sparse.mm(self.M, r)

    def scatter(self, drive: torch.Tensor) -> torch.Tensor:
        """drive (K, B) -> (n, B): every member of group k gets drive[k]."""
        return torch.sparse.mm(self.M1, drive)


class Bindings:
    """Per-being selection: in_group (B, n_in) group ids; out_pair (B, n_out, 2) group ids."""

    def __init__(self, in_groups: Groups, out_groups: Groups, in_group: np.ndarray, out_pair: np.ndarray,
                 gain: float = 1.0):
        self.gi, self.go = in_groups, out_groups
        self.B, self.n_in = in_group.shape
        self.n_out = out_pair.shape[1]
        dev = in_groups.device
        self.in_group = torch.as_tensor(in_group, device=dev, dtype=torch.int64)
        self.out_pair = torch.as_tensor(out_pair, device=dev, dtype=torch.int64)
        self.gain = gain

    @staticmethod
    def random(in_groups: Groups, out_groups: Groups, B: int, n_in: int, n_out: int, rng: np.random.Generator, gain=1.0):
        ig = rng.integers(0, in_groups.K, size=(B, n_in))
        op = rng.integers(0, out_groups.K, size=(B, n_out, 2))
        return Bindings(in_groups, out_groups, ig, op, gain)

    def drive(self, obs: torch.Tensor) -> torch.Tensor:
        """obs (B, n_in) -> u (n, B) external drive on the map."""
        K, B = self.gi.K, self.B
        d = torch.zeros((B, K), device=obs.device)
        d.scatter_add_(1, self.in_group, obs * self.gain)
        return self.gi.scatter(d.T.contiguous())

    def read(self, r: torch.Tensor) -> torch.Tensor:
        """r (n, B) -> cmd (B, n_out) = mean(plus) - mean(minus)."""
        g = self.go.mean_rates(r).T                       # (B, K)
        plus = torch.gather(g, 1, self.out_pair[:, :, 0])
        minus = torch.gather(g, 1, self.out_pair[:, :, 1])
        return plus - minus

    def mutate(self, rng: np.random.Generator, p: float = 0.1):
        ig = self.in_group.cpu().numpy().copy(); op = self.out_pair.cpu().numpy().copy()
        m = rng.random(ig.shape) < p; ig[m] = rng.integers(0, self.gi.K, size=m.sum())
        m = rng.random(op.shape) < p; op[m] = rng.integers(0, self.go.K, size=m.sum())
        return Bindings(self.gi, self.go, ig, op, self.gain)

    def select(self, idx) -> 'Bindings':
        return Bindings(self.gi, self.go, self.in_group.cpu().numpy()[idx], self.out_pair.cpu().numpy()[idx], self.gain)
