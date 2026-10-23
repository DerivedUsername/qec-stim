# qec-stim — rules for agents

Portfolio project for quantum error correction roles. Qiyu must be able to
explain every part of it in an interview, so the split below matters.

## Human-authored — agents REVIEW ONLY

Agents may explain concepts, review Qiyu's code with line references, point out
bugs, and suggest idioms in snippets of at most 3 lines. They must not fill in
`NotImplementedError` bodies unless Qiyu explicitly says he is giving up that piece.

- `src/qec_stim/bb_code.py` — bivariate-bicycle code construction over F2 (Part 2)
- `src/qec_stim/resource.py` — scaling fit and resource estimate (Part 3)
- the BP-OSD comparison script for Part 2, once started

## Written with AI assistance — Qiyu reviewed

- `src/qec_stim/surface.py`, `src/qec_stim/decode.py`, `scripts/threshold.py` (Part 1)
- everything in `tests/`, `.github/`, `setup.ps1`, `pyproject.toml`, `docs/`

## Conventions

- Python 3.11+, stim, pymatching, sinter, ldpc (BP-OSD), numpy, matplotlib.
- Noise: uniform circuit-level depolarizing of strength p (see `surface.py`).
  Part 2 may start with code-capacity noise for BB codes; label every plot with its noise model.
- Logical error rates are reported **per round** (sinter `failure_units_per_shot = rounds`).
- Every number in the README must come from a committed CSV in `results/`.

## Hazards

- A full threshold sweep takes minutes; CI runs `--quick` only.
- Don't compare surface and BB codes under different noise models without saying so.
- Don't claim hardware results; everything here is simulation.
