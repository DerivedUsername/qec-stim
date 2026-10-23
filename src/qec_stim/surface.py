"""Rotated surface-code memory experiments under circuit-level noise.

Noise model: uniform circuit-level depolarizing noise of strength p
(Stim's built-in generator), applied as
  - two-qubit depolarizing after every Clifford gate,
  - single-qubit depolarizing on data qubits at the start of each round,
  - bit-flip with probability p before every measurement,
  - bit-flip with probability p after every reset.
This is the standard "uniform depolarizing" (SD6-style) model used in
threshold papers, simpler than hardware-calibrated models such as SI1000.
"""

from __future__ import annotations

import stim


def memory_circuit(distance: int, p: float, rounds: int | None = None, basis: str = "z") -> stim.Circuit:
    """A rotated surface-code memory experiment with `rounds` syndrome rounds (default: `distance`)."""
    if basis not in ("x", "z"):
        raise ValueError("basis must be 'x' or 'z'")
    return stim.Circuit.generated(
        f"surface_code:rotated_memory_{basis}",
        distance=distance,
        rounds=rounds if rounds is not None else distance,
        after_clifford_depolarization=p,
        before_round_data_depolarization=p,
        before_measure_flip_probability=p,
        after_reset_flip_probability=p,
    )


def physical_qubits(distance: int) -> int:
    """Data plus measurement qubits in a rotated surface-code patch: d^2 + (d^2 - 1)."""
    return 2 * distance * distance - 1
