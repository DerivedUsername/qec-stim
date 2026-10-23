"""Resource estimates from measured logical error rates.  Part 3 — HUMAN-AUTHORED (see CLAUDE.md).

Goal: "How many physical qubits does a fault-tolerant run of a given circuit
need, at physical error rate p, to finish with total failure probability
below a target?"

Standard model (fit it to YOUR threshold data, don't just assume it):
    p_L(d) ≈ C * (p / p_th) ** ((d + 1) / 2)     per logical qubit per round
A circuit with Q logical qubits running for T rounds fails with probability
about Q * T * p_L(d). Choose the smallest odd d meeting the target, then count
physical qubits with surface.physical_qubits(d) per logical qubit (ignoring
routing and magic-state factories — say so in the README).
"""

from __future__ import annotations


def fit_scaling(rows: list[dict]) -> tuple[float, float]:
    """Fit (C, p_th) from threshold rows {distance, p, per_round_rate} below threshold."""
    raise NotImplementedError("Part 3")


def required_distance(p: float, logical_qubits: int, rounds: int, target: float, C: float, p_th: float) -> int:
    """Smallest odd distance d with logical_qubits * rounds * p_L(d) <= target."""
    raise NotImplementedError("Part 3")
