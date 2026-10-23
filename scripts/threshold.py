"""Surface-code threshold under circuit-level noise.

Sweeps distance d and physical error rate p, decodes with PyMatching via
sinter, writes results/threshold.csv and results/threshold.png.

    python scripts/threshold.py            # full run (minutes)
    python scripts/threshold.py --quick    # small run for CI / smoke tests
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import sinter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from qec_stim.surface import memory_circuit  # noqa: E402


def tasks(distances, ps):
    for d in distances:
        for p in ps:
            yield sinter.Task(
                circuit=memory_circuit(d, p),
                json_metadata={"d": d, "p": p, "r": d},
            )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--out", default=str(ROOT / "results"))
    args = ap.parse_args()

    if args.quick:
        distances, ps = [3, 5], [0.003, 0.008]
        max_shots, max_errors = 20_000, 50
    else:
        distances = [3, 5, 7, 9]
        ps = [0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.010, 0.012]
        max_shots, max_errors = 2_000_000, 300

    stats = sinter.collect(
        num_workers=os.cpu_count() or 1,
        tasks=list(tasks(distances, ps)),
        decoders=["pymatching"],
        max_shots=max_shots,
        max_errors=max_errors,
        print_progress=not args.quick,
    )

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "threshold.csv", "w") as f:
        print(sinter.CSV_HEADER, file=f)
        for s in stats:
            print(s.to_csv_line(), file=f)

    fig, ax = plt.subplots(figsize=(6.4, 4.6))
    sinter.plot_error_rate(
        ax=ax,
        stats=stats,
        x_func=lambda s: s.json_metadata["p"],
        group_func=lambda s: f"d = {s.json_metadata['d']}",
        failure_units_per_shot_func=lambda s: s.json_metadata["r"],
    )
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Physical error rate p (circuit-level depolarizing)")
    ax.set_ylabel("Logical error rate per round")
    ax.set_title("Rotated surface code, Z memory, MWPM decoding")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "threshold.png", dpi=160)
    print(f"wrote {out / 'threshold.csv'} and {out / 'threshold.png'}")


if __name__ == "__main__":
    main()
