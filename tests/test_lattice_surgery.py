"""Lattice surgery Z_A Z_B measurement. These skip until lattice_surgery.py is implemented."""

import numpy as np
import pymatching
import pytest
from _util import call_or_skip

from qec_stim import lattice_surgery as ls


def distance(circuit):
    return len(
        circuit.search_for_undetectable_logical_errors(
            dont_explore_detection_event_sets_with_size_above=4,
            dont_explore_edges_with_degree_above=4,
            dont_explore_edges_increasing_symptom_degree=False,
        )
    )


@pytest.mark.parametrize("basis,n_obs", [("Z", 3), ("X", 1)])
def test_shape_and_determinism(basis, n_obs):
    c = call_or_skip(ls.zz_measurement, 3, 0.001, basis)
    # The merged 7 x 3 patch: 21 data + 20 ancillas. The separate patches reuse a subset of these sites.
    assert c.num_qubits == 2 * (2 * 3 + 1) * 3 - 1
    assert c.num_observables == n_obs
    c.detector_error_model(decompose_errors=True)  # raises on non-deterministic detectors/observables
    clean = call_or_skip(ls.zz_measurement, 3, 0.0, basis)
    det, obs = clean.compile_detector_sampler().sample(50, separate_observables=True)
    assert not det.any() and not obs.any()


@pytest.mark.parametrize("d", [3, 5])
@pytest.mark.parametrize("basis", ["Z", "X"])
def test_distance_is_d(d, basis):
    assert distance(call_or_skip(ls.zz_measurement, d, 0.001, basis)) == d


def test_one_round_is_not_enough():
    # With a single merged round, one measurement error on a new Z check flips
    # the Z_A Z_B outcome undetected: time-like distance 1.
    assert distance(call_or_skip(ls.zz_measurement, 3, 0.001, "Z", rounds=1)) < 3


def test_pymatching_decodes_it():
    c = call_or_skip(ls.zz_measurement, 3, 0.001, "Z")
    dem = c.detector_error_model(decompose_errors=True)
    m = pymatching.Matching.from_detector_error_model(dem)
    det, obs = c.compile_detector_sampler(seed=7).sample(20_000, separate_observables=True)
    wrong = np.any(m.decode_batch(det) != obs, axis=1).mean()
    assert wrong < 0.03
