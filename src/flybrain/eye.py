"""The fly's eye as an input organ: photoreceptors placed on angular coordinates.

FlyWire gives every R1-6 photoreceptor a position in the EM volume (`pos_x/y/z`, one
eye per hemisphere). The retina/lamina is a curved 2-D sheet, so the first two principal
axes of the positions of one eye give a (u, v) chart of that sheet; we map it linearly
to azimuth (0° = straight ahead, 180° = behind, per side) and elevation (−60°..+60°).
The chart orientation is fixed by anatomy up to a flip; `assume_front_medial` picks the
convention that the medial edge of the eye (towards the head midline) looks forward.
This is a first-order retinotopy — no ommatidium clustering, no eye curvature model —
enough to bind a rendered retina to the right region of the eye.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .connectome import Connectome

AZIMUTH_SPAN_DEG = (5.0, 175.0)       # each eye sees roughly one hemifield
ELEVATION_SPAN_DEG = (-60.0, 60.0)


def photoreceptor_chart(cm: Connectome, annotations_tsv: str, cell_type: str = 'R1-6') -> pd.DataFrame:
    """One row per photoreceptor: index, side, azimuth_deg (signed: left < 0), elevation_deg."""
    ann = pd.read_csv(annotations_tsv, sep='\t', low_memory=False, usecols=['root_id', 'pos_x', 'pos_y', 'pos_z'])
    ann = ann.drop_duplicates('root_id').set_index('root_id')
    nrn = cm.neurons
    sel = nrn[nrn['cell_type'] == cell_type].join(ann, on='root_id')
    out = []
    midline_x = float(nrn.join(ann, on='root_id')['pos_x'].median())
    for side, q in sel.groupby('side'):
        if side not in ('left', 'right') or len(q) < 10:
            continue
        p = q[['pos_x', 'pos_y', 'pos_z']].to_numpy(dtype=np.float64)
        c = p - p.mean(0)
        _, _, vt = np.linalg.svd(c, full_matrices=False)
        uv = c @ vt[:2].T                                  # (k, 2) chart coordinates
        # orient axis 0 so that it increases AWAY from the midline (medial → lateral = front → back)
        lateral = (p[:, 0] - midline_x) * (1.0 if side == 'right' else -1.0)
        if np.corrcoef(uv[:, 0], lateral)[0, 1] < 0:
            uv[:, 0] *= -1
        # orient axis 1 so that it increases with z (dorsal); sign is arbitrary in the volume, keep it monotone
        if np.corrcoef(uv[:, 1], p[:, 2])[0, 1] < 0:
            uv[:, 1] *= -1
        u = (uv[:, 0] - uv[:, 0].min()) / np.ptp(uv[:, 0])
        v = (uv[:, 1] - uv[:, 1].min()) / np.ptp(uv[:, 1])
        az = AZIMUTH_SPAN_DEG[0] + u * (AZIMUTH_SPAN_DEG[1] - AZIMUTH_SPAN_DEG[0])
        el = ELEVATION_SPAN_DEG[0] + v * (ELEVATION_SPAN_DEG[1] - ELEVATION_SPAN_DEG[0])
        out.append(pd.DataFrame({'index': q.index.to_numpy(), 'side': side,
                                 'azimuth_deg': np.where(side == 'left', -az, az), 'elevation_deg': el}))
    return pd.concat(out, ignore_index=True)


def photoreceptors_in(chart: pd.DataFrame, az_center: float, el_center: float, radius_deg: float) -> np.ndarray:
    """Indices of photoreceptors whose direction lies within `radius_deg` of (az, el) (small-angle metric)."""
    d = np.hypot(chart['azimuth_deg'].to_numpy() - az_center, chart['elevation_deg'].to_numpy() - el_center)
    return chart['index'].to_numpy()[d <= radius_deg]


def retina_binding(chart: pd.DataFrame, cols: int, rows: int, fov_deg: float, max_pitch_deg: float,
                   radius_deg: float = 4.0) -> list[np.ndarray]:
    """For each rendered-retina pixel (row-major, `rows × cols`), the photoreceptors it drives.

    Columns span [−fov/2, +fov/2] of azimuth (uniform; the renderer's tan-warp is ignored here),
    rows span [0, −max_pitch] of elevation (row 0 = horizon, last row = looking down at the road)."""
    binding = []
    for r in range(rows):
        el = -max_pitch_deg * r / max(rows - 1, 1)
        for c in range(cols):
            az = -fov_deg / 2 + fov_deg * (c + 0.5) / cols
            binding.append(photoreceptors_in(chart, az, el, radius_deg))
    return binding


# ── The rendered retina of Universe (src/config.rs `retina` block, src/gpu/retina.wgsl) ──────
# Verified 14/09/2026 against Universe src/config.rs:261-267 and src/gpu/retina.wgsl:51-95.
RETINA_ROWS = 14
RETINA_COLS = 126
RETINA_FOV_DEG = 120.0            # config FOV_DEG; columns span [-60, +60] degrees of azimuth
RETINA_MIN_PITCH_RAD = -0.012     # row 0: the far/horizon row  (-0.6875 degrees)
RETINA_MAX_PITCH_RAD = -0.06      # row rows-1: the near/ground row (-3.4377 degrees)
TAN_WARP_K = 1.25                 # retina.wgsl TAN_K — warps row 0 ONLY (the fovea row)


def retina_pixel_angles(rows: int = RETINA_ROWS, cols: int = RETINA_COLS, fov_deg: float = RETINA_FOV_DEG,
                        min_pitch_rad: float = RETINA_MIN_PITCH_RAD, max_pitch_rad: float = RETINA_MAX_PITCH_RAD,
                        warp_row0: bool = True):
    """Direction every rendered-retina pixel actually samples: (elevation_deg[rows], azimuth_deg[rows, cols]).

    Copies `retina.wgsl` exactly, with gaze_yaw = 0 (the shader adds the per-being gaze to row 0 only;
    a static binding table cannot follow it). Row 0 is the fovea row and is tan-warped
    (`tan(u*K)/tan(K)`, dense at the centre); rows 1.. are uniform in azimuth.
    """
    r = np.arange(rows, dtype=np.float64)
    pitch = min_pitch_rad + (max_pitch_rad - min_pitch_rad) * (r / max(rows - 1, 1))
    elevation_deg = np.degrees(pitch)
    u = (np.arange(cols, dtype=np.float64) / max(cols - 1, 1)) * 2.0 - 1.0   # [-1, 1] at the column CENTRES
    linear = u * (fov_deg / 2.0)
    warped = (np.tan(u * TAN_WARP_K) / np.tan(TAN_WARP_K)) * (fov_deg / 2.0)
    azimuth_deg = np.tile(linear, (rows, 1))
    if warp_row0 and rows > 0:
        azimuth_deg[0] = warped
    return elevation_deg, azimuth_deg


def _cell_edges(centers: np.ndarray) -> np.ndarray:
    """Boundaries of the angular cell owned by each sample of an ASCENDING centre array
    (midpoints; the two outer edges extend by half the outer gap)."""
    c = np.asarray(centers, dtype=np.float64)
    if len(c) == 1:
        return np.array([c[0] - 0.5, c[0] + 0.5])
    mid = 0.5 * (c[:-1] + c[1:])
    return np.concatenate([[2 * c[0] - mid[0]], mid, [2 * c[-1] - mid[-1]]])


def _bin_into_cells(values: np.ndarray, centers: np.ndarray):
    """Index of the cell of `centers` that owns each value, and whether it is inside the covered span.
    `centers` may be ascending or descending; the returned index refers to `centers` as given."""
    c = np.asarray(centers, dtype=np.float64)
    descending = len(c) > 1 and c[0] > c[-1]
    asc = c[::-1] if descending else c
    edges = _cell_edges(asc)
    k = np.clip(np.searchsorted(edges, values, side='right') - 1, 0, len(asc) - 1)
    inside = (values >= edges[0]) & (values <= edges[-1])
    return (len(c) - 1 - k if descending else k), inside


def pixel_of_photoreceptor(chart: pd.DataFrame, n: int, rows: int = RETINA_ROWS, cols: int = RETINA_COLS,
                           fov_deg: float = RETINA_FOV_DEG, min_pitch_rad: float = RETINA_MIN_PITCH_RAD,
                           max_pitch_rad: float = RETINA_MAX_PITCH_RAD, fit: str = 'strip',
                           warp_row0: bool = True) -> np.ndarray:
    """u32[n]: the rendered-retina pixel (row-major, `row * cols + col`) that drives each neuron,
    0xFFFFFFFF for every neuron that is not a bound photoreceptor.

    fit='strip' (default, anatomically honest): a photoreceptor is bound to the pixel whose sampled
      direction owns its (azimuth, elevation); receptors looking outside the rendered window stay
      unbound. The tan-warp of row 0 is INVERTED — binding uses the angle the pixel really samples,
      not a linear column index.
    fit='stretch' (experiment): the chart's full azimuth AND elevation span is mapped linearly onto
      the columns and rows, so every photoreceptor is bound. Not angle-faithful by construction;
      it exists because the rendered retina is a thin strip (see docs/96-flymap-v2.md).
    """
    assert fit in ('strip', 'stretch'), fit
    out = np.full(int(n), 0xFFFFFFFF, dtype=np.uint32)
    idx = chart['index'].to_numpy().astype(np.int64)
    az = chart['azimuth_deg'].to_numpy(dtype=np.float64)
    el = chart['elevation_deg'].to_numpy(dtype=np.float64)
    if fit == 'stretch':
        row = np.clip(((el.max() - el) / max(np.ptp(el), 1e-9) * rows).astype(np.int64), 0, rows - 1)
        col = np.clip(((az - az.min()) / max(np.ptp(az), 1e-9) * cols).astype(np.int64), 0, cols - 1)
        out[idx] = (row * cols + col).astype(np.uint32)
        return out
    elevation_deg, azimuth_deg = retina_pixel_angles(rows, cols, fov_deg, min_pitch_rad, max_pitch_rad, warp_row0)
    row, in_el = _bin_into_cells(el, elevation_deg)
    col = np.zeros(len(idx), dtype=np.int64)
    in_az = np.zeros(len(idx), dtype=bool)
    for r in range(rows):                       # each row may have its own azimuth profile (row 0 is warped)
        sel = np.flatnonzero(in_el & (row == r))
        if len(sel) == 0:
            continue
        col[sel], in_az[sel] = _bin_into_cells(az[sel], azimuth_deg[r])
    bound = in_el & in_az
    out[idx[bound]] = (row[bound] * cols + col[bound]).astype(np.uint32)
    return out
