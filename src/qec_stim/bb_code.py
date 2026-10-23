"""Bivariate-bicycle (BB) codes.  Part 2 — HUMAN-AUTHORED (see CLAUDE.md).

Construction (Bravyi et al., "High-threshold and low-overhead fault-tolerant
quantum memory", Nature 2024): work in the group algebra
    F2[x, y] / (x^l - 1, y^m - 1),
realized as (l*m) x (l*m) binary matrices with
    x = S_l ⊗ I_m,   y = I_l ⊗ S_m,
where S_k is the k x k cyclic shift. A polynomial is a sum of monomials
x^a y^b, each a product of these permutation matrices (sums mod 2).

Given A, B in that algebra:
    H_X = [A | B],   H_Z = [B^T | A^T],
a CSS code on n = 2*l*m qubits. H_X H_Z^T = AB + BA = 0 mod 2 because the
algebra is commutative. k = n - rank_F2(H_X) - rank_F2(H_Z).

Polynomials are given as lists of (a, b) exponent pairs, e.g.
    A = x^3 + y + y^2  ->  [(3, 0), (0, 1), (0, 2)].

Known codes (tests check these):
    [[72, 12, 6]]:   l=6,  m=6,  A = x^3 + y + y^2,  B = y^3 + x + x^2
    [[144, 12, 12]]: l=12, m=6,  A = x^3 + y + y^2,  B = y^3 + x + x^2   (IBM's "gross" code)
"""

from __future__ import annotations

import numpy as np


def poly_matrix(terms: list[tuple[int, int]], l: int, m: int) -> np.ndarray:
    """The (l*m) x (l*m) binary matrix of sum_{(a,b) in terms} x^a y^b, entries in {0, 1}."""
    raise NotImplementedError("Part 2")


def bb_check_matrices(A: list[tuple[int, int]], B: list[tuple[int, int]], l: int, m: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (H_X, H_Z) as uint8 arrays of shape (l*m, 2*l*m)."""
    raise NotImplementedError("Part 2")


def rank_f2(H: np.ndarray) -> int:
    """Rank of a binary matrix over F2 (Gaussian elimination mod 2)."""
    raise NotImplementedError("Part 2")


def code_parameters(H_X: np.ndarray, H_Z: np.ndarray) -> tuple[int, int]:
    """(n, k) of the CSS code with these check matrices."""
    raise NotImplementedError("Part 2")
