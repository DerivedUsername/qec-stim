"""Lattice-surgery Z_A Z_B measurement under circuit-level noise.

    python scripts/lattice_surgery.py             # PyMatching, d = 3, 5, 7 (a few minutes)
    python scripts/lattice_surgery.py --quick     # small run
    python scripts/lattice_surgery.py --mine      # also decode a sample with your dem_mwpm decoder

Needs zz_measurement (lattice_surgery.py, yours). Writes results/lattice_surgery.csv
and results/lattice_surgery.png.

Reported failure rates, per experiment (3 phases x d rounds):
  basis Z:  "ZZ"  = the lattice-surgery outcome Z_A Z_B is wrong
            "any" = any of Z_A Z_B, Z_A, Z_B is wrong
  basis X:  "XX"  = the preserved X_A X_B is wrong
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pymatching

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from qec_stim import dem_mwpm  # noqa: E402
from qec_stim.lattice_surgery import zz_measurement  # noqa: E402


def run_pymatching(circuit, max_shots, max_errors, seed):
    dem = circuit.detector_error_model(decompose_errors=True)
    m = pymatching.Matching.from_detector_error_model(dem)
    sampler = circuit.compile_detector_sampler(seed=seed)
    shots, wrong_first, wrong_any = 0, 0, 0
    while shots < max_shots and wrong_any < max_errors:
        det, obs = sampler.sample(min(20_000, max_shots - shots), separate_observables=True)
        bad = m.decode_batch(det) != obs
        shots += len(det)
        wrong_first += int(bad[:, 0].sum())
        wrong_any += int(bad.any(axis=1).sum())
    return shots, wrong_first, wrong_any


def run_mine(circuit, shots, seed):
    dem = circuit.detector_error_model(decompose_errors=True)
    g = dem_mwpm.dem_graph(dem)
    det, obs = circuit.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    pred = np.array([dem_mwpm.decode(g, d, dem.num_observables)[0] for d in det])
    bad = pred != obs
    return shots, int(bad[:, 0].sum()), int(bad.any(axis=1).sum())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--mine", action="store_true", help="also run your dem_mwpm decoder on a small sample")
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()

    ds = [3, 5] if args.quick else [3, 5, 7]
    ps = [0.002, 0.006] if args.quick else [0.001, 0.002, 0.003, 0.004, 0.006, 0.008]
    max_shots, max_errors = (20_000, 50) if args.quick else (1_000_000, 300)

    rows = []
    for basis in ("Z", "X"):
        for d in ds:
            for p in ps:
                c = zz_measurement(d, p, basis)
                n, w0, wa = run_pymatching(c, max_shots, max_errors, seed=1000 * d + int(p * 1e5))
                rows.append(dict(decoder="pymatching", basis=basis, d=d, p=p, shots=n, wrong_first=w0, wrong_any=wa))
                print(f"pymatching basis={basis} d={d} p={p:.3f}: first obs {w0 / n:.2e}, any {wa / n:.2e} ({n} shots)")
                if args.mine and d == 3:
                    n, w0, wa = run_mine(c, 2000, seed=1)
                    rows.append(dict(decoder="mine", basis=basis, d=d, p=p, shots=n, wrong_first=w0, wrong_any=wa))
                    print(f"mine       basis={basis} d={d} p={p:.3f}: first obs {w0 / n:.2e}, any {wa / n:.2e} ({n} shots)")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "lattice_surgery.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    for ax, basis, label in zip(axes, ("Z", "X"), ("Z_A Z_B outcome wrong", "X_A X_B not preserved")):
        for d in ds:
            pts = [(r["p"], r["wrong_first"] / r["shots"]) for r in rows
                   if r["decoder"] == "pymatching" and r["basis"] == basis and r["d"] == d and r["wrong_first"] > 0]
            if pts:
                ax.plot(*zip(*pts), "-o", label=f"d = {d}")
        mine = [(r["p"], r["wrong_first"] / r["shots"]) for r in rows
                if r["decoder"] == "mine" and r["basis"] == basis and r["wrong_first"] > 0]
        if mine:
            ax.plot(*zip(*mine), "kx", ms=9, label="my decoder, d = 3")
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("Physical error rate p (circuit-level)")
        ax.set_title(label)
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
    axes[0].set_ylabel("Failure probability per lattice-surgery experiment")
    fig.suptitle("Lattice surgery: merge and split of two rotated surface-code patches (3d rounds)")
    fig.tight_layout()
    fig.savefig(out / "lattice_surgery.png", dpi=160)
    print(f"wrote {out / 'lattice_surgery.csv'} and {out / 'lattice_surgery.png'}")


if __name__ == "__main__":
    main()
