"""Unit tests for flybrain (CPU, synthetic graphs, seconds). Run: python src/fly_tests.py"""
import os, sys
import numpy as np
import pandas as pd
import torch

sys.path.insert(0, os.path.dirname(__file__))
from flybrain.connectome import Connectome, _csr
from flybrain.dynamics import LifBrain, LifParams, RateBrain


def toy(n=6):
    pre = np.array([0, 0, 1, 2, 3, 4], dtype=np.int32)
    post = np.array([1, 2, 3, 3, 4, 5], dtype=np.int32)
    w = np.array([200, -50, 200, 30, 200, -200], dtype=np.int32)
    neurons = pd.DataFrame({'super_class': ['sensory'] * 2 + ['central'] * 3 + ['motor'], 'cell_type': [''] * n})
    return Connectome(n, np.arange(n, dtype=np.int64) + 10, pre, post, w, neurons)


def test_csr_matches_edges():
    cm = toy()
    ip, cols, vals = cm.csr_by_pre()
    dense = np.zeros((cm.n, cm.n))
    for i in range(cm.n):
        for k in range(ip[i], ip[i + 1]):
            dense[i, cols[k]] += vals[k]
    ref = np.zeros((cm.n, cm.n)); np.add.at(ref, (cm.pre, cm.post), cm.weight)
    assert np.array_equal(dense, ref)
    ip2, cols2, vals2 = cm.csr_by_post()
    dense2 = np.zeros((cm.n, cm.n))
    for j in range(cm.n):
        for k in range(ip2[j], ip2[j + 1]):
            dense2[cols2[k], j] += vals2[k]
    assert np.array_equal(dense2, ref)
    assert list(cm.index_of([10, 15])) == [0, 5]
    assert list(cm.where(super_class='central')) == [2, 3, 4]


def test_lif_chain_and_delay():
    cm = toy(); p = LifParams()
    b = LifBrain(cm, batch=2, params=p, device='cpu')
    b.set_poisson([0], rate_hz=1e9)            # p >= 1: neuron 0 spikes every step
    D = b.D
    first_spike_1 = None
    for t in range(200):
        spk = b.step()
        if spk[0, 1] and first_spike_1 is None:
            first_spike_1 = t
    # neuron 0 spikes at t=0; its 200-synapse (55 mV) input reaches neuron 1 at t=D
    assert first_spike_1 is not None and first_spike_1 >= D, first_spike_1
    assert b.spike_count[0, 0] == 200                # no refractory for Poisson targets
    assert b.spike_count[0, 2] == 0                  # inhibited only: never fires
    assert b.spike_count[0, 5] == 0                  # inhibitory input from 4: never fires
    assert b.spike_count[0, 3] > 0 and b.spike_count[0, 4] > 0
    assert b.v[0, 2] < p.v_0 - 1.0                   # inhibition pushed neuron 2 below rest
    # refractory: neuron 1 cannot fire two steps in a row
    b2 = LifBrain(cm, batch=1, params=p, device='cpu'); b2.set_poisson([0], 1e9)
    spikes1 = [bool(b2.step()[0, 1]) for _ in range(300)]
    gaps = np.diff(np.flatnonzero(spikes1))
    assert gaps.min() >= b2.rfc_steps, gaps.min()


def test_neuron_mask_blocks_propagation():
    cm = toy()
    b = LifBrain(cm, batch=2, device='cpu'); b.set_poisson([0], 1e9)
    mask = np.ones((2, cm.n), dtype=np.float32); mask[1, 0] = 0.0   # being 1: neuron 0 selected out
    b.set_neuron_mask(mask)
    for _ in range(300): b.step()
    assert b.spike_count[0, 1] > 0 and b.spike_count[1, 1] == 0


def test_rate_brain_matches_dense():
    cm = toy()
    rb = RateBrain(cm, batch=3, device='cpu', tau_steps=2.0, scale=0.01)
    W = np.zeros((cm.n, cm.n), dtype=np.float32); np.add.at(W, (cm.post, cm.pre), cm.weight * 0.01)
    x = torch.randn(cm.n, 3); rb.x = x.clone()
    u = torch.randn(cm.n, 3)
    rb.step(u)
    r = torch.relu(x)
    ref = x + 0.5 * (-x + torch.as_tensor(W) @ r + u)
    assert torch.allclose(rb.x, ref, atol=1e-5)


def test_flymap_file_roundtrip():
    import tempfile
    from flybrain.flymap_file import NONE, read_flymap, write_flymap
    cm = toy()
    order = np.argsort(cm.post, kind='stable')
    indptr = np.zeros(cm.n + 1, np.int64); np.add.at(indptr, cm.post + 1, 1); indptr = np.cumsum(indptr)
    type_of = np.array([0, 0, 1, 1, 1, 2], np.uint32)
    in_group_of = np.array([0, 0, NONE, NONE, NONE, NONE], np.uint32)
    out_indptr, out_members = np.array([0, 1], np.uint32), np.array([5], np.uint32)
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'toy.bin')
        write_flymap(p, indptr, cm.pre[order], cm.weight[order].astype(np.float32), type_of, in_group_of, out_indptr, out_members,
                     sidecar=dict(k_in=1, n_types=3))
        z = read_flymap(p)
    assert z['n'] == 6 and z['m'] == 6 and z['k_in'] == 1 and z['n_types'] == 3 and z['k_out'] == 1
    assert np.array_equal(z['indptr'], indptr) and np.array_equal(z['indices'], cm.pre[order])
    # row 3 (post=3) has inputs from pre 1 (200) and pre 2 (30)
    r = slice(z['indptr'][3], z['indptr'][4])
    assert sorted(zip(z['indices'][r].tolist(), z['weights'][r].tolist())) == [(1, 200.0), (2, 30.0)]
    assert z['in_group_of'][2] == NONE and z['out_members'].tolist() == [5]


# ── flymap v2 (docs/96-flymap-v2.md) ─────────────────────────────────────────────────────────
def _toy_flymap_arrays():
    """The toy map as flymap tables: v1 CSR (by post), presynaptic CSR, and the small tables."""
    cm = toy()
    order = np.argsort(cm.post, kind='stable')
    indptr = np.zeros(cm.n + 1, np.int64); np.add.at(indptr, cm.post + 1, 1); indptr = np.cumsum(indptr)
    pre_order = np.argsort(cm.pre, kind='stable')
    pre_indptr = np.zeros(cm.n + 1, np.int64); np.add.at(pre_indptr, cm.pre + 1, 1); pre_indptr = np.cumsum(pre_indptr)
    return dict(cm=cm, indptr=indptr.astype(np.uint32), indices=cm.pre[order].astype(np.uint32),
                weights=cm.weight[order].astype(np.float32), type_of=np.array([0, 0, 1, 1, 1, 2], np.uint32),
                in_group_of=np.array([0, 0, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF], np.uint32),
                out_indptr=np.array([0, 1], np.uint32), out_members=np.array([5], np.uint32),
                pre_indptr=pre_indptr.astype(np.uint32), pre_indices=cm.post[pre_order].astype(np.uint32),
                pre_weights=cm.weight[pre_order].astype(np.float32))


def _v1_reference_bytes(t, k_in=1, n_types=3):
    """The v1 layout spelled out here, so the byte-identity test does not trust the module it checks."""
    n, m = len(t['indptr']) - 1, len(t['indices'])
    buf = bytearray(b'FLYMAP01')
    buf += np.array([n, m, n_types, k_in, len(t['out_indptr']) - 1, len(t['out_members']), 0, 0], '<u4').tobytes()
    for key, dt in (('indptr', '<u4'), ('indices', '<u4'), ('weights', '<f4'), ('type_of', '<u4'),
                    ('in_group_of', '<u4'), ('out_indptr', '<u4'), ('out_members', '<u4')):
        buf += np.ascontiguousarray(t[key], dt).tobytes()
    return bytes(buf)


def _write(path, t, **kw):
    from flybrain.flymap_file import write_flymap
    write_flymap(path, t['indptr'], t['indices'], t['weights'], t['type_of'], t['in_group_of'],
                 t['out_indptr'], t['out_members'], sidecar=dict(k_in=1, n_types=3), **kw)


def test_flymap_v1_bytes_unchanged_by_v2():
    """Writing without any optional block must still produce the exact v1 file."""
    import tempfile
    t = _toy_flymap_arrays()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'v1.bin'); _write(p, t)
        got = open(p, 'rb').read()
    assert got == _v1_reference_bytes(t), 'v1 output changed'
    assert got[:8] == b'FLYMAP01' and got[36:40] == b'\x00\x00\x00\x00'


def test_flymap_v2_roundtrip_and_prefix():
    import tempfile
    from flybrain.flymap_file import FLAG_NO_REFRACTORY, FLAG_PIXEL_BINDING, FLAG_PRE_CSR, pack_bitmap, read_flymap
    t = _toy_flymap_arrays()
    n = len(t['type_of'])
    pixel = np.full(n, 0xFFFFFFFF, np.uint32); pixel[0] = 7; pixel[1] = 1763
    no_rfc = pixel != 0xFFFFFFFF
    with tempfile.TemporaryDirectory() as d:
        p1 = os.path.join(d, 'v1.bin'); _write(p1, t)
        p2 = os.path.join(d, 'v2.bin')
        _write(p2, t, pre_indptr=t['pre_indptr'], pre_indices=t['pre_indices'], pre_weights=t['pre_weights'],
               pixel_of_neuron=pixel, no_refractory=no_rfc)
        b1, b2 = open(p1, 'rb').read(), open(p2, 'rb').read()
        z = read_flymap(p2)
        z1 = read_flymap(p1)
    flags_expected = FLAG_PRE_CSR | FLAG_PIXEL_BINDING | FLAG_NO_REFRACTORY
    assert z['version'] == 2 and z['flags'] == flags_expected
    assert z1['version'] == 1 and z1['flags'] == 0 and 'pre_indptr' not in z1
    assert b2[:8] == b'FLYMAP02' and b2[40:len(b1)] == b1[40:], 'v2 must extend v1, not reshuffle it'
    # header word 6 (byte 32..36) is the flag word, word 7 (byte 36..40) stays reserved = 0
    hdr = np.frombuffer(b2[8:40], dtype='<u4')
    assert hdr[6] == flags_expected and hdr[7] == 0, 'flags must sit at header word 6, reserved at word 7'
    for k in ('indptr', 'indices', 'weights', 'pre_indptr', 'pre_indices', 'pre_weights'):
        assert np.array_equal(z[k], t[k] if k in t else z[k]), k
    assert np.array_equal(z['pixel_of_neuron'], pixel)
    assert np.array_equal(z['no_refractory'], pack_bitmap(no_rfc))


def test_flymap_v2_pre_csr_is_the_same_edge_multiset():
    """Both CSRs must carry exactly the same (pre, post, weight) triples."""
    import tempfile
    from flybrain.flymap_file import read_flymap
    t = _toy_flymap_arrays()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'v2.bin')
        _write(p, t, pre_indptr=t['pre_indptr'], pre_indices=t['pre_indices'], pre_weights=t['pre_weights'])
        z = read_flymap(p)
    post_side = sorted((int(z['indices'][e]), j, float(z['weights'][e]))
                       for j in range(z['n']) for e in range(z['indptr'][j], z['indptr'][j + 1]))
    pre_side = sorted((i, int(z['pre_indices'][e]), float(z['pre_weights'][e]))
                      for i in range(z['n']) for e in range(z['pre_indptr'][i], z['pre_indptr'][i + 1]))
    assert post_side == pre_side, 'presynaptic CSR is a different edge multiset'
    cm = t['cm']
    assert pre_side == sorted(zip(cm.pre.tolist(), cm.post.tolist(), cm.weight.astype(np.float32).tolist()))


def test_retina_pixel_angles_match_the_shader():
    from flybrain.eye import RETINA_MAX_PITCH_RAD, RETINA_MIN_PITCH_RAD, retina_pixel_angles
    el, az = retina_pixel_angles()
    assert el.shape == (14,) and az.shape == (14, 126)
    assert np.isclose(el[0], np.degrees(RETINA_MIN_PITCH_RAD)) and np.isclose(el[-1], np.degrees(RETINA_MAX_PITCH_RAD))
    assert np.isclose(az[1, 0], -60.0) and np.isclose(az[1, -1], 60.0)          # uniform rows span the FOV
    assert np.isclose(az[0, 0], -60.0) and np.isclose(az[0, -1], 60.0)          # warped row 0 has the same extent
    assert abs(az[0, 63] - az[0, 62]) < abs(az[1, 63] - az[1, 62])              # ... but is denser at the centre
    assert np.all(np.diff(az[0]) > 0) and np.all(np.diff(el) < 0)               # monotone: col -> right, row -> down


def test_photoreceptor_binding_known_angles():
    from flybrain.eye import NONE_PIXEL, pixel_of_neuron
    chart = pd.DataFrame({'index': [0, 1, 2, 3],
                          'azimuth_deg': [60.0, -60.0, 0.0, 120.0],          # last one looks outside the window
                          'elevation_deg': [-3.4377468, -2.0, -0.6875493, -1.0]})
    n = 6
    p = pixel_of_neuron(chart, n, fit='strip')
    assert p[0] == 13 * 126 + 125, p[0]          # bottom-right corner pixel
    assert p[1] == 6 * 126 + 0, p[1]             # elevation -2.0 falls in row 6 (-1.957), leftmost column
    assert p[2] // 126 == 0 and abs(int(p[2] % 126) - 62.5) <= 0.5             # straight ahead, fovea row, centre
    assert p[3] == NONE_PIXEL and p[4] == NONE_PIXEL and p[5] == NONE_PIXEL   # outside the FOV / not in the chart
    bound = p != NONE_PIXEL
    assert p[bound].max() < 14 * 126 and bound.sum() == 3                     # ~strip: only 3/4 charted neurons bound
    # stretch binds every charted neuron, including the one looking 120 degrees to the right
    q = pixel_of_neuron(chart, n, fit='stretch')
    assert (q[:4] != NONE_PIXEL).all() and (q[4:] == NONE_PIXEL).all() and q[:4].max() < 14 * 126


def test_motion_chart_shares_photoreceptor_chart_machinery():
    """motion_chart (T4/T5) must produce the same PCA-sheet chart shape as photoreceptor_chart (R1-6),
    with no cross-talk between the two cell-type selections, on a synthetic connectome + annotations file."""
    import tempfile
    from flybrain.connectome import Connectome
    from flybrain.eye import motion_chart, photoreceptor_chart
    rng = np.random.default_rng(0)
    n_r, n_t4, n_t5, n_other = 20, 15, 12, 5
    n = n_r + n_t4 + n_t5 + n_other
    cell_type = ['R1-6'] * n_r + ['T4a'] * n_t4 + ['T5b'] * n_t5 + ['Mi1'] * n_other
    side = (['left'] * (n_r // 2) + ['right'] * (n_r - n_r // 2) + ['left'] * (n_t4 // 2) + ['right'] * (n_t4 - n_t4 // 2)
           + ['left'] * (n_t5 // 2) + ['right'] * (n_t5 - n_t5 // 2) + ['left'] * n_other)
    root_ids = np.arange(n, dtype=np.int64) + 1000
    neurons = pd.DataFrame({'cell_type': cell_type, 'side': side, 'root_id': root_ids})
    cm = Connectome(n, root_ids, np.zeros(0, np.int32), np.zeros(0, np.int32), np.zeros(0, np.int32), neurons)
    # a flat sheet plus noise is enough for PCA to recover two in-plane axes per side
    pos = rng.normal(size=(n, 3)) * np.array([[10.0, 10.0, 0.1]])
    ann = pd.DataFrame({'root_id': root_ids, 'pos_x': pos[:, 0], 'pos_y': pos[:, 1], 'pos_z': pos[:, 2]})
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, 'annotations.tsv'); ann.to_csv(p, sep='\t', index=False)
        rc = photoreceptor_chart(cm, p)
        mc = motion_chart(cm, p)
    assert set(rc['index']) == set(range(n_r)), 'photoreceptor_chart must select only R1-6'
    assert set(mc['index']) == set(range(n_r, n_r + n_t4 + n_t5)), 'motion_chart must select only T4+T5'
    for chart in (rc, mc):
        assert {'index', 'side', 'azimuth_deg', 'elevation_deg'} <= set(chart.columns)
        assert chart['azimuth_deg'].between(-180.0, 180.0).all() and chart['elevation_deg'].between(-60.0, 60.0).all()


def test_no_refractory_bitmap_matches_the_binding():
    from flybrain.flymap_file import NONE, pack_bitmap, unpack_bitmap
    n = 100
    pixel = np.full(n, NONE, np.uint32)
    pixel[[3, 31, 32, 64, 99]] = [0, 1, 2, 3, 1763]
    words = pack_bitmap(pixel != NONE)
    assert len(words) == (n + 31) // 32 == 4
    back = unpack_bitmap(words, n)
    assert np.array_equal(back, pixel != NONE) and back.sum() == 5
    assert bool(words[0] & (1 << 3)) and bool(words[1] & 1) and not bool(words[0] & 1)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith('test_'):
            fn(); print('ok', name)
    print('ALL PASSED')
