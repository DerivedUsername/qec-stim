"""Rotated surface-code patches on a global grid, for css_circuit.build.

Data qubits sit at integer points (x, y). A plaquette with lower-left data qubit
(x, y) has its ancilla at (x + 0.5, y + 0.5) and is X-type if x + y is even,
Z-type if odd. A width x height rectangle keeps:
  - every interior plaquette (weight 4),
  - weight-2 X plaquettes on its left and right edges,
  - weight-2 Z plaquettes on its top and bottom edges.
So logical Z runs along a column (between the X edges) and logical X along a row.

Because types come from the global grid, a d x d patch at x0 = 0 and another at
x0 = d + 1 (d odd) line up with the (2d + 1) x d rectangle spanning both plus the
column x = d between them. That is what makes lattice surgery a change of check set.

CNOT order (hook errors): X checks touch their corners in the order
(x-, y-), (x-, y+), (x+, y-), (x+, y+), so an ancilla fault leaves a vertical
X pair, perpendicular to logical X. Z checks use (x-, y-), (x+, y-), (x-, y+),
(x+, y+), leaving a horizontal Z pair, perpendicular to logical Z. tests/test_patches.py
checks that memory circuits built this way have circuit distance exactly d.
"""

from __future__ import annotations

from qec_stim.css_circuit import Check, Coord, Phase, Rec, build

X_ORDER = [(-0.5, -0.5), (-0.5, 0.5), (0.5, -0.5), (0.5, 0.5)]
Z_ORDER = [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)]


def data_qubits(width: int, height: int, x0: int = 0, y0: int = 0) -> list[Coord]:
    return [(float(x), float(y)) for y in range(y0, y0 + height) for x in range(x0, x0 + width)]


def rectangle(width: int, height: int, x0: int = 0, y0: int = 0) -> list[Check]:
    """Checks of a rotated surface code on the width x height block with lower-left data (x0, y0)."""
    data = set(data_qubits(width, height, x0, y0))
    checks = []
    for y in range(y0 - 1, y0 + height):
        for x in range(x0 - 1, x0 + width):
            basis = "X" if (x + y) % 2 == 0 else "Z"
            cx, cy = x + 0.5, y + 0.5
            order = X_ORDER if basis == "X" else Z_ORDER
            slots = tuple((cx + dx, cy + dy) if (cx + dx, cy + dy) in data else None for dx, dy in order)
            n = sum(s is not None for s in slots)
            if n == 4:
                checks.append(Check(basis, (cx, cy), slots))
            elif n == 2:
                on_lr = x < x0 or x >= x0 + width - 1  # plaquette sticks out left or right
                if (on_lr and basis == "X") or (not on_lr and basis == "Z"):
                    checks.append(Check(basis, (cx, cy), slots))
    return checks


def logical_z(x: int, height: int, y0: int = 0) -> list[Coord]:
    """Support of a logical Z: the column at x."""
    return [(float(x), float(y)) for y in range(y0, y0 + height)]


def logical_x(y: int, width: int, x0: int = 0) -> list[Coord]:
    """Support of a logical X: the row at y."""
    return [(float(x), float(y)) for x in range(x0, x0 + width)]


def memory(d: int, p: float, basis: str = "Z", rounds: int | None = None):
    """Single-patch memory experiment through the builder (used to validate it against surface.py)."""
    data = data_qubits(d, d)
    rounds = d if rounds is None else rounds
    ph = Phase(rectangle(d, d), rounds, reset={q: basis for q in data}, measure={q: basis for q in data})
    support = logical_z(0, d) if basis == "Z" else logical_x(0, d)
    return build([ph], [[Rec("data", 0, q) for q in support]], p)
