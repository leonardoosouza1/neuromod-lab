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
