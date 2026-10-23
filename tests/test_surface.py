"""Part 1: surface-code circuits and MWPM decoding."""

import pytest

from qec_stim.decode import Result, logical_error_rate
from qec_stim.surface import memory_circuit, physical_qubits


@pytest.mark.parametrize("d", [3, 5, 7])
def test_circuit_shape(d):
    c = memory_circuit(d, 0.001)
    assert c.num_qubits >= physical_qubits(d)
    assert c.num_observables == 1
    # Round 1 and the final data readout each give (d^2-1)/2 Z-checks; rounds 2..d compare
    # all d^2-1 stabilizers with the previous round. Total: d * (d^2 - 1).
    assert c.num_detectors == d * (d * d - 1)


def test_noiseless_has_no_logical_errors():
    r = logical_error_rate(memory_circuit(3, 0.0), shots=500, seed=1)
    assert r.errors == 0


def test_distance_helps_below_threshold():
    # At p = 0.1%, well below threshold (~1% for this noise model), d=5 must beat d=3 per round.
    r3 = logical_error_rate(memory_circuit(3, 0.001), shots=200_000, seed=2)
    r5 = logical_error_rate(memory_circuit(5, 0.001), shots=200_000, seed=3)
    assert r5.per_round(5) < r3.per_round(3)


def test_per_round_inverts_total():
    e, rounds = 0.01, 7
    total = (1 - (1 - 2 * e) ** rounds) / 2
    shots = 10**9
    assert Result(shots=shots, errors=round(total * shots)).per_round(rounds) == pytest.approx(e, rel=1e-6)
