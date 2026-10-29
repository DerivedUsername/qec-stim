"""Toric-code threshold under code-capacity noise: your MWPM decoder vs PyMatching.

    python scripts/toric_threshold.py                   # both decoders, a few minutes
    python scripts/toric_threshold.py --quick           # small run
    python scripts/toric_threshold.py --decoder mine    # only your decoder

Writes results/toric_threshold.csv and results/toric_threshold.png.
Needs mwpm.decode and mwpm.logical_error (yours); the PyMatching curve also
uses your logical_error, so both curves are scored the same way.
Expected: curves cross near p ≈ 10%, the known code-capacity MWPM threshold.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pymatching

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from qec_stim import mwpm  # noqa: E402
from qec_stim.toric import check_matrix, sample_errors, syndrome  # noqa: E402


def run(L: int, p: float, trials: int, decoder: str, rng: np.random.Generator) -> tuple[int, float]:
    if decoder == "pymatching":
        matcher = pymatching.Matching(check_matrix(L))
        decode = lambda syn: matcher.decode(syn).astype(np.uint8)  # noqa: E731
    else:
        decode = lambda syn: mwpm.decode(syn, L)  # noqa: E731
    fails, t0 = 0, time.perf_counter()
    for _ in range(trials):
        err = sample_errors(L, p, rng)
        corr = decode(syndrome(err, L))
        fails += bool(mwpm.logical_error(err ^ corr, L))
    return fails, (time.perf_counter() - t0) / trials


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--decoder", choices=["both", "mine", "pymatching"], default="both")
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()

    sizes = [4, 6] if args.quick else [4, 6, 8, 10, 12]
    ps = [0.06, 0.10, 0.14] if args.quick else [0.04, 0.06, 0.08, 0.09, 0.10, 0.11, 0.12, 0.14]
    trials = 200 if args.quick else 3000
    decoders = ["mine", "pymatching"] if args.decoder == "both" else [args.decoder]

    rng = np.random.default_rng(12345)
    rows = []
    for dec in decoders:
        for L in sizes:
            for p in ps:
                fails, sec = run(L, p, trials, dec, rng)
                rows.append({"decoder": dec, "L": L, "p": p, "trials": trials, "fails": fails, "sec_per_shot": sec})
                print(f"{dec:10s} L={L:2d} p={p:.2f} fail={fails / trials:.4f} ({sec * 1e3:.2f} ms/shot)")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "toric_threshold.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    for dec, style in zip(decoders, ["-o", "--x"]):
        for L in sizes:
            pts = [(r["p"], r["fails"] / r["trials"]) for r in rows if r["decoder"] == dec and r["L"] == L]
            ax.plot(*zip(*pts), style, label=f"{'mine' if dec == 'mine' else 'PyMatching'}, L = {L}")
    ax.set_xlabel("Physical error rate p (code capacity, X errors)")
    ax.set_ylabel("Logical failure probability")
    ax.set_title("Toric code, MWPM decoding")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=7, ncol=2)
    fig.tight_layout()
    fig.savefig(out / "toric_threshold.png", dpi=160)
    print(f"wrote {out / 'toric_threshold.csv'} and {out / 'toric_threshold.png'}")


if __name__ == "__main__":
    main()
