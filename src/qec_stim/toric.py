"""Toric-code lattice bookkeeping for the hand-written MWPM decoder.

L x L torus. Vertices (i, j) with i, j mod L, index i*L + j.
Edges (qubits), 2*L*L of them:
    horizontal h(i, j): from (i, j) to (i, j+1), index 2*(i*L + j)
    vertical   v(i, j): from (i, j) to (i+1, j), index 2*(i*L + j) + 1

Noise model: code capacity. Each edge independently gets an X error with
probability p; syndrome measurement is perfect.

Checks: the vertex (star) operator at v is Z on its 4 incident edges. An X error
on an edge flips the checks at both of its endpoints, so a chain of X errors
lights up exactly the vertices at its ends: those are the "defects" (anyons).
"""

from __future__ import annotations

import numpy as np


def vertex(i: int, j: int, L: int) -> int:
    return (i % L) * L + (j % L)


def coords(v: int, L: int) -> tuple[int, int]:
    return divmod(v, L)


def h_edge(i: int, j: int, L: int) -> int:
    return 2 * vertex(i, j, L)


def v_edge(i: int, j: int, L: int) -> int:
    return 2 * vertex(i, j, L) + 1


def num_edges(L: int) -> int:
    return 2 * L * L


def edge_endpoints(e: int, L: int) -> tuple[int, int]:
    v, kind = divmod(e, 2)
    i, j = coords(v, L)
    return (v, vertex(i, j + 1, L)) if kind == 0 else (v, vertex(i + 1, j, L))


def check_matrix(L: int) -> np.ndarray:
    """Vertex-by-edge incidence matrix over F2, shape (L*L, 2*L*L)."""
    H = np.zeros((L * L, num_edges(L)), dtype=np.uint8)
    for e in range(num_edges(L)):
        a, b = edge_endpoints(e, L)
        H[a, e] = 1
        H[b, e] = 1
    return H


def syndrome(chain: np.ndarray, L: int) -> np.ndarray:
    """Vertex parities of an edge chain (0/1 array of length 2*L*L)."""
    return (check_matrix(L) @ chain.astype(np.int64)) % 2


def sample_errors(L: int, p: float, rng: np.random.Generator) -> np.ndarray:
    return (rng.random(num_edges(L)) < p).astype(np.uint8)


def plaquette(i: int, j: int, L: int) -> np.ndarray:
    """The 4 edges around the face with lower-left corner (i, j): a trivial (contractible) cycle."""
    c = np.zeros(num_edges(L), dtype=np.uint8)
    for e in (h_edge(i, j, L), v_edge(i, j + 1, L), h_edge(i + 1, j, L), v_edge(i, j, L)):
        c[e] ^= 1
    return c


def row_loop(i: int, L: int) -> np.ndarray:
    """All horizontal edges in row i: a cycle wrapping the torus horizontally (logical X)."""
    c = np.zeros(num_edges(L), dtype=np.uint8)
    for j in range(L):
        c[h_edge(i, j, L)] = 1
    return c


def column_loop(j: int, L: int) -> np.ndarray:
    """All vertical edges in column j: a cycle wrapping the torus vertically (the other logical X)."""
    c = np.zeros(num_edges(L), dtype=np.uint8)
    for i in range(L):
        c[v_edge(i, j, L)] = 1
    return c
