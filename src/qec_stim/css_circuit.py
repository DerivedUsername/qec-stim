"""A small builder for multi-phase CSS syndrome-extraction circuits in Stim.

An experiment is a list of phases. Each phase measures a fixed set of checks
(stabilizers) for some number of rounds; data qubits can be reset at the start
of a phase and measured at its end. Lattice surgery is exactly this:
"two patches" -> "one merged patch" -> "two patches".

Detectors are built from stabilizer information only, never from the logical
state, so the decoder can't "see" a logical outcome it isn't supposed to know:

  (a) a check measured in round r > 0 is compared with itself in round r - 1;
  (b) a check's first round in a phase is compared with
        - the same check (same ancilla, same basis) in the previous phase, when the
          supports differ only by data qubits reset in that basis at the start of
          this phase or measured in that basis at the end of the previous one
          (e.g. merge and split of a boundary check), or
        - nothing, when every data qubit it touches was just reset in its basis
          (e.g. Z checks after resetting to |0>);
      otherwise the first outcome is random and gets no detector;
  (c) when data qubits are measured, each check of the phase whose whole support
      was measured in its basis is compared with its last round.

Noise (strength p, matching surface.py): DEPOLARIZE1 on active data at the start
of each round, DEPOLARIZE2 after every CNOT, flip errors after resets and before
measurements.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import stim

Coord = tuple[float, float]


@dataclass(frozen=True)
class Check:
    basis: str  # "X" or "Z"
    ancilla: Coord
    data: tuple[Coord | None, ...]  # CNOT order, one entry per time step; None = idle step

    @property
    def support(self) -> frozenset[Coord]:
        return frozenset(q for q in self.data if q is not None)


@dataclass
class Phase:
    checks: list[Check]
    rounds: int
    reset: dict[Coord, str] = field(default_factory=dict)  # data qubit -> "X" | "Z", at phase start
    measure: dict[Coord, str] = field(default_factory=dict)  # data qubit -> "X" | "Z", at phase end


@dataclass(frozen=True)
class Rec:
    """A measurement result: a check's outcome (phase, round, ancilla) or a data readout (phase, qubit)."""

    kind: str  # "check" | "data"
    phase: int
    coord: Coord
    round: int = 0  # checks only; -1 = last round of the phase


def build(phases: list[Phase], observables: list[list[Rec]], p: float) -> stim.Circuit:
    coords: set[Coord] = set()
    for ph in phases:
        coords |= set(ph.reset) | set(ph.measure)
        for c in ph.checks:
            coords.add(c.ancilla)
            coords |= c.support
    index = {q: i for i, q in enumerate(sorted(coords, key=lambda q: (q[1], q[0])))}

    circ = stim.Circuit()
    for q, i in index.items():
        circ.append("QUBIT_COORDS", [i], [q[0], q[1]])

    n_meas = 0
    check_rec: dict[tuple[int, int, Coord], int] = {}  # (phase, round, ancilla) -> absolute index
    data_rec: dict[tuple[int, Coord], int] = {}  # (phase, data qubit) -> absolute index
    active: dict[Coord, str] = {}  # data qubit -> basis it was last reset in
    t = 0  # detector time coordinate

    def lookback(abs_indices):
        return [stim.target_rec(a - n_meas) for a in abs_indices]

    def detector(abs_indices, x, y):
        circ.append("DETECTOR", lookback(abs_indices), [x, y, t])

    for k, ph in enumerate(phases):
        # ---- resets at phase start ----
        for basis in ("Z", "X"):
            qs = [index[q] for q, b in ph.reset.items() if b == basis]
            if qs:
                circ.append("R" if basis == "Z" else "RX", qs)
                circ.append("X_ERROR" if basis == "Z" else "Z_ERROR", qs, p)
        for q, b in ph.reset.items():
            if q in active:
                raise ValueError(f"phase {k}: {q} reset while still active")
            active[q] = b
        for c in ph.checks:
            missing = c.support - set(active)
            if missing:
                raise ValueError(f"phase {k}: check at {c.ancilla} uses inactive data {sorted(missing)}")

        prev = phases[k - 1] if k else None
        prev_by_anc = {(c.ancilla, c.basis): c for c in prev.checks} if prev else {}
        steps = max(len(c.data) for c in ph.checks)

        for r in range(ph.rounds):
            circ.append("TICK")
            circ.append("DEPOLARIZE1", [index[q] for q in active], p)
            xa = [index[c.ancilla] for c in ph.checks if c.basis == "X"]
            za = [index[c.ancilla] for c in ph.checks if c.basis == "Z"]
            if za:
                circ.append("R", za)
                circ.append("X_ERROR", za, p)
            if xa:
                circ.append("RX", xa)
                circ.append("Z_ERROR", xa, p)
            for s in range(steps):
                circ.append("TICK")
                pairs = []
                for c in ph.checks:
                    if s < len(c.data) and c.data[s] is not None:
                        a, d = index[c.ancilla], index[c.data[s]]
                        pairs += [a, d] if c.basis == "X" else [d, a]
                if pairs:
                    circ.append("CX", pairs)
                    circ.append("DEPOLARIZE2", pairs, p)
            circ.append("TICK")
            if za:
                circ.append("X_ERROR", za, p)
            if xa:
                circ.append("Z_ERROR", xa, p)
            order = [c for c in ph.checks if c.basis == "Z"] + [c for c in ph.checks if c.basis == "X"]
            if za:
                circ.append("M", za)
            if xa:
                circ.append("MX", xa)
            for c in order:
                check_rec[(k, r, c.ancilla)] = n_meas
                n_meas += 1

            # ---- detectors (rules a and b) ----
            for c in ph.checks:
                me = check_rec[(k, r, c.ancilla)]
                x, y = c.ancilla
                if r > 0:
                    detector([me, check_rec[(k, r - 1, c.ancilla)]], x, y)
                    continue
                reset_here = {q for q, b in ph.reset.items() if b == c.basis}
                old = prev_by_anc.get((c.ancilla, c.basis))
                if old is not None:
                    measured_before = {q for q, b in prev.measure.items() if b == c.basis}
                    diff = c.support ^ old.support
                    if diff <= (reset_here | measured_before):
                        extra = [data_rec[(k - 1, q)] for q in diff if q in measured_before]
                        detector([me, check_rec[(k - 1, prev.rounds - 1, c.ancilla)], *extra], x, y)
                        continue
                if c.support <= reset_here:
                    detector([me], x, y)
            t += 1

        # ---- data measurements at phase end ----
        circ.append("TICK")
        for basis in ("Z", "X"):
            qs = [q for q, b in ph.measure.items() if b == basis]
            if not qs:
                continue
            circ.append("X_ERROR" if basis == "Z" else "Z_ERROR", [index[q] for q in qs], p)
            circ.append("M" if basis == "Z" else "MX", [index[q] for q in qs])
            for q in qs:
                data_rec[(k, q)] = n_meas
                n_meas += 1
        for q in ph.measure:
            if q not in active:
                raise ValueError(f"phase {k}: measuring inactive data {q}")
            del active[q]
        # rule (c)
        for c in ph.checks:
            b = {ph.measure.get(q) for q in c.support}
            if b == {c.basis}:
                recs = [data_rec[(k, q)] for q in c.support] + [check_rec[(k, ph.rounds - 1, c.ancilla)]]
                detector(recs, *c.ancilla)
        t += 1

    if active:
        raise ValueError(f"data qubits never measured: {sorted(active)}")

    for i, obs in enumerate(observables):
        recs = []
        for rec in obs:
            if rec.kind == "check":
                rnd = rec.round if rec.round >= 0 else phases[rec.phase].rounds + rec.round
                recs.append(check_rec[(rec.phase, rnd, rec.coord)])
            else:
                recs.append(data_rec[(rec.phase, rec.coord)])
        circ.append("OBSERVABLE_INCLUDE", lookback(recs), i)
    return circ
