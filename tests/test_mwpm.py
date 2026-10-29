"""Tests for the hand-written toric-code MWPM decoder. They skip until mwpm.py is implemented."""

import numpy as np
import pymatching
import pytest
from _util import call_or_skip

from qec_stim import mwpm
from qec_stim.toric import (
    check_matrix,
    column_loop,
    h_edge,
    num_edges,
    plaquette,
    row_loop,
    sample_errors,
    syndrome,
    v_edge,
    vertex,
)

L = 6


# ---------- distances and paths ----------


@pytest.mark.parametrize(
    "a,b,d",
    [
        ((0, 0), (0, 0), 0),
        ((0, 0), (0, 2), 2),
        ((0, 0), (0, 5), 1),  # wraps around: 0 -> 5 is one step left
        ((0, 0), (3, 3), 6),
        ((1, 1), (5, 4), 5),  # 2 down (wrapping) + 3 right
    ],
)
def test_torus_distance(a, b, d):
    assert call_or_skip(mwpm.torus_distance, vertex(*a, L), vertex(*b, L), L) == d


@pytest.mark.parametrize("a,b", [((0, 0), (2, 3)), ((0, 0), (5, 5)), ((4, 1), (1, 4)), ((2, 2), (2, 2))])
def test_shortest_path(a, b):
    u, v = vertex(*a, L), vertex(*b, L)
    path = call_or_skip(mwpm.shortest_path, u, v, L)
    chain = np.zeros(num_edges(L), dtype=np.uint8)
    for e in path:
        chain[e] ^= 1
    assert len(path) == mwpm.torus_distance(u, v, L)
    expected = np.zeros(L * L, dtype=np.uint8)
    if u != v:
        expected[[u, v]] = 1
    assert np.array_equal(syndrome(chain, L), expected)


# ---------- decoding ----------


def test_single_error_corrected_exactly():
    err = np.zeros(num_edges(L), dtype=np.uint8)
    err[v_edge(2, 3, L)] = 1
    corr = call_or_skip(mwpm.decode, syndrome(err, L), L)
    assert np.array_equal(corr, err)


def test_correction_matches_syndrome():
    rng = np.random.default_rng(0)
    for _ in range(50):
        err = sample_errors(L, 0.08, rng)
        syn = syndrome(err, L)
        corr = call_or_skip(mwpm.decode, syn, L)
        assert np.array_equal(syndrome(corr, L), syn)


def test_correction_weight_matches_pymatching():
    """Both are exact MWPM on the same metric, so total weights must agree (paths may differ)."""
    rng = np.random.default_rng(1)
    reference = pymatching.Matching(check_matrix(L))
    for _ in range(100):
        syn = syndrome(sample_errors(L, 0.06, rng), L)
        ours = call_or_skip(mwpm.decode, syn, L)
        theirs = reference.decode(syn)
        assert ours.sum() == theirs.sum()


# ---------- logical check ----------


def test_trivial_cycles_are_not_logical():
    assert not call_or_skip(mwpm.logical_error, plaquette(1, 2, L), L)
    two = plaquette(0, 0, L) ^ plaquette(3, 4, L)
    assert not mwpm.logical_error(two, L)


def test_wrapping_cycles_are_logical():
    assert call_or_skip(mwpm.logical_error, row_loop(2, L), L)
    assert mwpm.logical_error(column_loop(4, L), L)
    # A wrapping loop deformed by a plaquette is still the same logical.
    assert mwpm.logical_error(row_loop(0, L) ^ plaquette(0, 0, L), L)
    # Two parallel wrapping loops cancel homologically.
    assert not mwpm.logical_error(row_loop(0, L) ^ row_loop(3, L), L)


def test_low_noise_rarely_fails():
    rng = np.random.default_rng(2)
    fails = 0
    for _ in range(300):
        err = sample_errors(L, 0.02, rng)
        corr = call_or_skip(mwpm.decode, syndrome(err, L), L)
        fails += call_or_skip(mwpm.logical_error, err ^ corr, L)
    assert fails / 300 < 0.02


def test_edge_helpers_consistent():
    # Sanity check of the harness itself (always runs).
    assert h_edge(0, 0, L) == 0 and v_edge(0, 0, L) == 1
    assert syndrome(plaquette(0, 0, L), L).sum() == 0
    assert syndrome(row_loop(1, L), L).sum() == 0
