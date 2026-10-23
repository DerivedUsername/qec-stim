"""Part 2: bivariate-bicycle codes. These skip until bb_code.py is implemented."""

import numpy as np
import pytest
from _util import call_or_skip

from qec_stim import bb_code

A = [(3, 0), (0, 1), (0, 2)]  # x^3 + y + y^2
B = [(0, 3), (1, 0), (2, 0)]  # y^3 + x + x^2


def test_monomials_are_permutations():
    for a, b in [(0, 0), (1, 0), (0, 1), (2, 3)]:
        M = call_or_skip(bb_code.poly_matrix, [(a, b)], 6, 6)
        assert M.shape == (36, 36)
        assert np.all(M.sum(axis=0) == 1) and np.all(M.sum(axis=1) == 1)


def test_x_and_y_commute():
    x = call_or_skip(bb_code.poly_matrix, [(1, 0)], 6, 6)
    y = call_or_skip(bb_code.poly_matrix, [(0, 1)], 6, 6)
    assert np.array_equal((x @ y) % 2, (y @ x) % 2)


def test_rank_f2_simple():
    H = np.array([[1, 1, 0], [0, 1, 1], [1, 0, 1]], dtype=np.uint8)  # rows sum to 0 mod 2
    assert call_or_skip(bb_code.rank_f2, H) == 2


@pytest.mark.parametrize("l,m", [(6, 6), (12, 6)])
def test_css_condition(l, m):
    HX, HZ = call_or_skip(bb_code.bb_check_matrices, A, B, l, m)
    assert HX.shape == (l * m, 2 * l * m) and HZ.shape == (l * m, 2 * l * m)
    assert not np.any((HX.astype(int) @ HZ.T.astype(int)) % 2)


@pytest.mark.parametrize("l,m,n,k", [(6, 6, 72, 12), (12, 6, 144, 12)])
def test_known_parameters(l, m, n, k):
    HX, HZ = call_or_skip(bb_code.bb_check_matrices, A, B, l, m)
    assert call_or_skip(bb_code.code_parameters, HX, HZ) == (n, k)
