"""Lattice surgery: measuring Z_A Z_B between two surface-code patches.  HUMAN-AUTHORED (see CLAUDE.md).

Layout (d odd), using patches.py's global grid:
    patch A:  rectangle(d, d, x0=0)          data x = 0 .. d-1
    seam:     the column x = d               (d new data qubits)
    patch B:  rectangle(d, d, x0=d + 1)      data x = d+1 .. 2d
    merged:   rectangle(2d + 1, d, x0=0)     all of the above as one patch

The protocol is three phases for css_circuit.build, d rounds each by default:
    0. separate:  checks of A and B; reset all patch data in `basis`
    1. merge:     checks of the merged rectangle; reset the seam in X at the start,
                  measure the seam in X at the end (that end measurement is the split)
    2. split:     checks of A and B again; measure all patch data in `basis` at the end

What to work out (and be able to explain):
  * Which merged checks are NEW, i.e. have no check with the same ancilla and basis
    in phase 0? Why is each new Z check's first outcome random, and why is the
    product of all of them Z_A Z_B? (Each seam qubit sits in exactly two new Z checks;
    each qubit of columns d-1 and d+1 sits in exactly one.)
  * basis="Z" (start in |0>_A |0>_B), three observables, in this order:
        [Z_A Z_B outcome = product of the new Z checks' round-0 results in phase 1,
         Z_A = final Z readout of a column of A,
         Z_B = final Z readout of a column of B]
  * basis="X" (start in |+>_A |+>_B), one observable: X_A X_B. Merging measures
    checks that anticommute with X_A alone, so the preserved operator is
    X_A · X_seam · X_B along a row: final X readout of row 0 in A and in B,
    plus the X readout of seam qubit (d, 0) taken at the split.

Use Rec("check", phase, ancilla, round) and Rec("data", phase, qubit) for observables.
tests/test_lattice_surgery.py checks determinism, circuit distance d, and decoding.
"""

from __future__ import annotations

import stim


def zz_measurement(d: int, p: float, basis: str = "Z", rounds: int | None = None) -> stim.Circuit:
    """The three-phase Z_A Z_B lattice-surgery experiment above, `rounds` (default d) rounds per phase."""
    raise NotImplementedError("lattice surgery")
