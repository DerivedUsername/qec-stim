"""Part 3: resource estimates. These skip until resource.py is implemented."""

from _util import call_or_skip

from qec_stim import resource


def test_required_distance_monotone_in_target():
    kw = dict(p=0.001, logical_qubits=10, rounds=1000, C=0.1, p_th=0.008)
    loose = call_or_skip(resource.required_distance, target=1e-2, **kw)
    strict = call_or_skip(resource.required_distance, target=1e-6, **kw)
    assert loose % 2 == 1 and strict % 2 == 1
    assert strict > loose


def test_required_distance_meets_target():
    C, p_th, p, Q, T, target = 0.1, 0.008, 0.001, 10, 1000, 1e-3
    d = call_or_skip(resource.required_distance, p, Q, T, target, C, p_th)
    assert Q * T * C * (p / p_th) ** ((d + 1) / 2) <= target
    if d > 3:
        dm = d - 2
        assert Q * T * C * (p / p_th) ** ((dm + 1) / 2) > target
