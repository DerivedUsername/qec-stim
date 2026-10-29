"""Your MWPM decoder, generalized from the toric code to any Stim circuit.  HUMAN-AUTHORED (see CLAUDE.md).

mwpm.py decodes the toric code under code-capacity noise, where the graph is the
lattice and every edge has the same weight. Under circuit-level noise the graph
comes from the circuit's detector error model (DEM) instead:

  * nodes  = detectors, plus one boundary node "B";
  * edges  = errors. With decompose_errors=True every DEM error splits into
             components that flip one detector (an edge to "B") or two detectors.
  * weight = log((1 - p) / p), so the lightest correction is the most likely one;
  * each edge records which logical observables it flips.

Then decoding is the same algorithm as on the torus:
  1. defects = detectors that fired;
  2. shortest-path distances between defects, and from each defect to "B"
     (networkx.single_source_dijkstra);
  3. MWPM where a defect may pair with another defect OR with the boundary.
     Standard trick: give each defect i its own boundary copy b_i, with edge
     (i, b_i) of weight dist(i, B) and weight 0 between all pairs of copies.
  4. the prediction is the XOR of the observables flipped along the chosen paths.

Parallel edges (several errors with the same detectors) must be merged into one
edge with probability p1(1 - p2) + p2(1 - p1); otherwise your weights won't match
PyMatching's and test_weight_matches_pymatching will fail.
"""

from __future__ import annotations

import networkx as nx
import numpy as np
import stim


def dem_graph(dem: stim.DetectorErrorModel) -> nx.Graph:
    """Weighted matching graph of a decomposed DEM.

    Nodes: 0 .. dem.num_detectors - 1, and "B". Each edge carries
    weight=log((1-p)/p), p=its merged probability, and obs=frozenset of observable indices.
    """
    raise NotImplementedError("DEM decoder")


def decode(graph: nx.Graph, detection_events: np.ndarray, num_observables: int) -> tuple[np.ndarray, float]:
    """(predicted observable flips as a 0/1 array, total weight of the chosen correction)."""
    raise NotImplementedError("DEM decoder")
