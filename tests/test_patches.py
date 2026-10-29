"""The circuit builder and patch geometry (always run)."""

import pytest

from qec_stim.patches import memory, rectangle


def distance(circuit):
    return len(
        circuit.search_for_undetectable_logical_errors(
            dont_explore_detection_event_sets_with_size_above=4,
            dont_explore_edges_with_degree_above=4,
            dont_explore_edges_increasing_symptom_degree=False,
        )
    )


@pytest.mark.parametrize("d", [3, 5])
def test_patch_has_d2_minus_1_checks(d):
    assert len(rectangle(d, d)) == d * d - 1


@pytest.mark.parametrize("d", [3, 5])
@pytest.mark.parametrize("basis", ["Z", "X"])
def test_memory_is_deterministic_with_distance_d(d, basis):
    c = memory(d, 0.001, basis)
    c.detector_error_model(decompose_errors=True)  # raises if any detector is non-deterministic
    assert c.num_detectors == d * (d * d - 1)
    assert distance(c) == d


def test_noiseless_memory_fires_nothing():
    det, obs = memory(3, 0.0).compile_detector_sampler().sample(100, separate_observables=True)
    assert not det.any() and not obs.any()
