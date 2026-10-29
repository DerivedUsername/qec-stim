"""Your DEM-level MWPM decoder vs PyMatching. These skip until dem_mwpm.py is implemented."""

import numpy as np
import pymatching
import pytest
from _util import call_or_skip

from qec_stim import dem_mwpm
from qec_stim import lattice_surgery as ls
from qec_stim.patches import memory


def compare(circuit, shots, seed):
    dem = circuit.detector_error_model(decompose_errors=True)
    g = call_or_skip(dem_mwpm.dem_graph, dem)
    ref = pymatching.Matching.from_detector_error_model(dem)
    det, _ = circuit.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    for s in range(shots):
        _, w_ours = call_or_skip(dem_mwpm.decode, g, det[s], dem.num_observables)
        _, w_ref = ref.decode(det[s], return_weight=True)
        assert w_ours == pytest.approx(w_ref, abs=1e-6), f"shot {s}"


def test_graph_shape():
    dem = memory(3, 0.005).detector_error_model(decompose_errors=True)
    g = call_or_skip(dem_mwpm.dem_graph, dem)
    assert g.number_of_nodes() == dem.num_detectors + 1
    assert "B" in g
    for _, _, e in g.edges(data=True):
        assert e["weight"] > 0 and 0 < e["p"] < 0.5


def test_no_defects_no_correction():
    dem = memory(3, 0.005).detector_error_model(decompose_errors=True)
    g = call_or_skip(dem_mwpm.dem_graph, dem)
    pred, w = call_or_skip(dem_mwpm.decode, g, np.zeros(dem.num_detectors, dtype=bool), 1)
    assert not pred.any() and w == 0


def test_weight_matches_pymatching_on_memory():
    compare(memory(3, 0.005), shots=200, seed=3)


def test_weight_matches_pymatching_on_lattice_surgery():
    compare(call_or_skip(ls.zz_measurement, 3, 0.003, "Z"), shots=100, seed=4)


def test_logical_error_rate_close_to_pymatching():
    c = memory(3, 0.004)
    dem = c.detector_error_model(decompose_errors=True)
    g = call_or_skip(dem_mwpm.dem_graph, dem)
    det, obs = c.compile_detector_sampler(seed=5).sample(3000, separate_observables=True)
    ours = np.array([call_or_skip(dem_mwpm.decode, g, d, 1)[0] for d in det])
    ref = pymatching.Matching.from_detector_error_model(dem).decode_batch(det)
    assert abs(np.any(ours != obs, axis=1).mean() - np.any(ref != obs, axis=1).mean()) < 0.01
