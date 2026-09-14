"""Reader for Universe `.replay` files (src/replay.rs: 64-byte header, then entries of
tag 0xFE + being index + 128-byte #[repr(C)] ReplayFrame).

Only the fields we use are named; the dtype below mirrors the Rust layout including
the 3 implicit padding bytes after `fuel_norm` (u32 `tick` is 4-aligned)."""
from __future__ import annotations

import numpy as np

MAGIC = b'IARARPLY'
FRAME_DTYPE = np.dtype({
    'names': ['pos', 'fwd', 'speed', 'yaw_rate', 'arc_prog', 'laps', 'gear', 'hp_norm', 'fuel_norm', 'tick',
              'sensors', 'intent', 'final', 'diag', 'retina_fov', 'retina_peri'],
    'formats': ['<3f4', '<2f4', '<f4', '<f4', '<f4', '<u2', 'u1', 'u1', 'u1', '<u4',
                '<8f4', '<3f4', '<3f4', '4u1', '8i1', '8i1'],
    'offsets': [0, 12, 20, 24, 28, 32, 34, 35, 36, 40, 44, 76, 88, 100, 104, 112],
    'itemsize': 128})
SENSOR_NAMES = ['dist_wall_l', 'dist_wall_r', 'dist_wall_f', 'curv_40m', 'curv_70m', 'curv_120m', 'flow_align', 'line_offset']
SENSOR_SCALE = np.array([40.0, 40.0, 50.0, 1.0, 1.0, 1.0, 1.0, 5.0], dtype=np.float32)   # caps measured in the GPU replay (doc says 15/30)


def read_replay(path: str):
    """Returns (header dict, being_idx (N,) uint8, frames (N,) structured array)."""
    b = np.fromfile(path, dtype='u1')
    assert bytes(b[:8]) == MAGIC, 'not an IARA replay'
    version = int(b[8:10].view('<u2')[0]); assert version == 1, version
    header = dict(version=version, source=int(b[10]), n_beings=int(b[11]), tick_rate=float(b[12:16].view('<f4')[0]),
                  world_seed=int(b[16:24].view('<u8')[0]))
    body = b[64:]
    n = len(body) // 130
    ent = body[:n * 130].reshape(n, 130)
    assert (ent[:, 0] == 0xFE).all(), 'unexpected entry tag'
    being = ent[:, 1].copy()
    frames = np.ascontiguousarray(ent[:, 2:]).view(FRAME_DTYPE).reshape(n)
    return header, being, frames


def being_frames(path: str, being: int):
    header, idx, frames = read_replay(path)
    return header, frames[idx == being]


def observation_matrix(frames, fields=('dist_wall_l', 'dist_wall_r', 'dist_wall_f', 'speed', 'yaw_rate', 'hp_norm')) -> np.ndarray:
    """(T, n_in) float32, each field divided by its cap so values sit roughly in [-1, 1].

    The GPU evolution path (source=1) records only the three wall distances, speed,
    yaw rate, gear and hp; curvature/flow/line_offset, the retina and the raw intent
    are written as zeros there (measured 14/09 on u11b_r10_s031_ctrl/gen0014.replay).
    Use `final` (the applied command) as the behavioural target."""
    cols = []
    for f in fields:
        if f in SENSOR_NAMES:
            v = frames['sensors'][:, SENSOR_NAMES.index(f)].astype(np.float32) / SENSOR_SCALE[SENSOR_NAMES.index(f)]
        else:
            v = frames[f].astype(np.float32) / FIELD_SCALE[f]
        cols.append(v)
    return np.stack(cols, 1).astype(np.float32)


FIELD_SCALE = {'speed': 25.0, 'yaw_rate': 1.0, 'hp_norm': 127.0, 'fuel_norm': 127.0, 'gear': 6.0}
OBS_NAMES = SENSOR_NAMES + [f'retina_fov{i}' for i in range(8)] + [f'retina_peri{i}' for i in range(8)]
