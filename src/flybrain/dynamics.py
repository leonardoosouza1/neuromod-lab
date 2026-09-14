"""Batched dynamics on the fly map (torch, GPU).

LifBrain  — the leaky integrate-and-fire model of Shiu et al. 2024 (Nature), same
            constants, batched over B independent trials/beings. Spike propagation
            uses only the rows of the ACTIVE presynaptic neurons (the brain is
            ~0.3 % active), so a step costs O(active edges), not O(15 M).
RateBrain — leaky rate units on the same signed map, one SpMM per step; the
            closed-loop model for control tasks (one step per world tick).

Both accept an optional per-being selection (see selection.py): a neuron mask
(B, n) in {0,1} multiplies the outgoing activity, and an edge mask is applied
through `edge_scale`.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import torch

from .connectome import Connectome


@dataclass
class LifParams:
    """Shiu et al. 2024, model.py `default_params` (units: mV, ms)."""
    dt: float = 0.1
    v_0: float = -52.0
    v_rst: float = -52.0
    v_th: float = -45.0
    t_mbr: float = 20.0      # membrane time constant
    tau: float = 5.0         # synaptic conductance decay
    t_rfc: float = 2.2       # refractory period
    t_dly: float = 1.8       # synaptic delay
    w_syn: float = 0.275     # mV per synapse
    f_poi: float = 250.0     # Poisson input weight factor (w_syn*f_poi = 68.75 mV → spike)


class LifBrain:
    def __init__(self, cm: Connectome, batch: int, params: LifParams = LifParams(),
                 device: str = 'cuda', edge_scale: torch.Tensor | None = None):
        self.cm, self.B, self.p, self.dev = cm, batch, params, device
        n = cm.n
        indptr, cols, vals = cm.csr_by_pre()
        self.indptr = torch.as_tensor(indptr, device=device)
        self.cols = torch.as_tensor(cols, device=device, dtype=torch.int64)
        self.vals = torch.as_tensor(vals, device=device) * params.w_syn
        if edge_scale is not None:
            self.vals = self.vals * edge_scale.to(device)
        self.D = int(round(params.t_dly / params.dt))
        self.rfc_steps = int(round(params.t_rfc / params.dt))
        self.dec_g = float(np.exp(-params.dt / params.tau))
        self.dec_v = float(np.exp(-params.dt / params.t_mbr))
        self.v = torch.full((batch, n), params.v_0, device=device)
        self.g = torch.zeros((batch, n), device=device)
        self.rfc = torch.zeros((batch, n), device=device, dtype=torch.int16)
        self.ring = torch.zeros((self.D, batch, n), device=device, dtype=torch.bool)
        self.t = 0
        self.poisson_idx = None
        self.poisson_p = 0.0
        self.no_rfc = torch.zeros(n, device=device, dtype=torch.bool)
        self.neuron_mask = None      # (B, n) float, multiplies outgoing spikes
        self.spike_count = torch.zeros((batch, n), device=device, dtype=torch.int32)

    def set_poisson(self, idx, rate_hz: float):
        """Neurons in idx receive Poisson kicks (N=1, weight w_syn*f_poi) at rate_hz;
        their refractory period is 0, as in the reference model."""
        self.poisson_idx = torch.as_tensor(np.asarray(idx), device=self.dev, dtype=torch.int64)
        self.poisson_p = rate_hz * self.p.dt * 1e-3
        self.no_rfc[:] = False
        self.no_rfc[self.poisson_idx] = True

    def set_neuron_mask(self, mask):
        self.neuron_mask = None if mask is None else torch.as_tensor(mask, device=self.dev, dtype=torch.float32)

    @torch.no_grad()
    def step(self):
        p = self.p
        slot = self.t % self.D
        s_in = self.ring[slot]                             # spikes emitted D steps ago, (B, n) bool
        # ---- propagate only the active presynaptic rows -------------------------------
        active = torch.nonzero(s_in.any(0)).squeeze(1)
        if active.numel():
            starts, ends = self.indptr[active], self.indptr[active + 1]
            lens = ends - starts
            e_pre = torch.repeat_interleave(active, lens)
            offs = torch.arange(int(lens.sum()), device=self.dev) - torch.repeat_interleave(torch.cumsum(lens, 0) - lens, lens)
            e = torch.repeat_interleave(starts, lens) + offs
            e_post, e_w = self.cols[e], self.vals[e]
            src = s_in[:, e_pre].float()                   # (B, E)
            if self.neuron_mask is not None:
                src = src * self.neuron_mask[:, e_pre]
            self.g.index_add_(1, e_post, src * e_w)
        # ---- integrate (exact for g, exact for v with g held over the step) ----------
        free = self.rfc <= 0
        v_new = p.v_0 + (self.v - p.v_0) * self.dec_v + self.g * (1.0 - self.dec_v)
        g_new = self.g * self.dec_g
        self.v = torch.where(free, v_new, self.v)
        self.g = torch.where(free, g_new, self.g)
        self.rfc = torch.where(free, self.rfc, self.rfc - 1)
        # ---- Poisson kicks -------------------------------------------------------------
        if self.poisson_idx is not None and self.poisson_p > 0:
            kick = torch.rand((self.B, self.poisson_idx.numel()), device=self.dev) < self.poisson_p
            self.v[:, self.poisson_idx] += kick.float() * (p.w_syn * p.f_poi)
        # ---- threshold + reset ----------------------------------------------------------
        spk = self.v > p.v_th
        self.v = torch.where(spk, torch.full_like(self.v, p.v_rst), self.v)
        self.g = torch.where(spk, torch.zeros_like(self.g), self.g)
        self.rfc = torch.where(spk & ~self.no_rfc[None, :], torch.full_like(self.rfc, self.rfc_steps), self.rfc)
        self.ring[slot] = spk                               # delivered at t + D
        self.spike_count += spk.int()
        self.t += 1
        return spk

    def run(self, steps: int):
        for _ in range(steps):
            self.step()
        return self.spike_count

    def rates_hz(self):
        """Mean firing rate (Hz) per neuron over the run, averaged over the batch."""
        t_s = self.t * self.p.dt * 1e-3
        return self.spike_count.float().mean(0) / t_s


class RateBrain:
    """x <- x + (dt/tau) * (-x + W r + u), r = relu(x); W = signed synapse count * scale.
    One dense-column SpMM per step over the full map. Rows = postsynaptic."""

    def __init__(self, cm: Connectome, batch: int, device: str = 'cuda', tau_steps: float = 4.0,
                 scale: float = 1e-2, edge_scale: torch.Tensor | None = None, act: str = 'relu'):
        self.cm, self.B, self.dev = cm, batch, device
        indptr, cols, vals = cm.csr_by_post()
        v = torch.as_tensor(vals) * scale
        if edge_scale is not None:
            v = v * edge_scale.cpu()
        self.W = torch.sparse_csr_tensor(torch.as_tensor(indptr), torch.as_tensor(cols, dtype=torch.int64), v,
                                         size=(cm.n, cm.n)).to(device)
        self.x = torch.zeros((cm.n, batch), device=device)     # column-major: (n, B) for SpMM
        self.alpha = 1.0 / tau_steps
        self.act = act
        self.neuron_mask = None

    def set_neuron_mask(self, mask):
        self.neuron_mask = None if mask is None else torch.as_tensor(mask, device=self.dev, dtype=torch.float32).T.contiguous()

    def rates(self):
        r = torch.relu(self.x) if self.act == 'relu' else torch.tanh(self.x)
        return r if self.neuron_mask is None else r * self.neuron_mask

    @torch.no_grad()
    def step(self, u: torch.Tensor | None = None):
        """u: (n, B) external drive (already scattered onto neurons) or None."""
        r = self.rates()
        inp = torch.sparse.mm(self.W, r)
        if u is not None:
            inp = inp + u
        self.x = self.x + self.alpha * (-self.x + inp)
        return self.x
