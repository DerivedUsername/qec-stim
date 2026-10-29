# Surface codes and qLDPC codes under circuit-level noise

Simulations of quantum error correction with [Stim](https://github.com/quantumlib/Stim):
the rotated surface code under circuit-level noise, decoded with minimum-weight
perfect matching, and (in progress) IBM-style bivariate-bicycle qLDPC codes
built from their group-algebra description and decoded with BP-OSD.

| Part | Status |
|---|---|
| 1. Surface-code threshold, circuit-level noise, MWPM (PyMatching) | ✅ |
| 2. Bivariate-bicycle codes from F2[x,y]/(xˡ−1, yᵐ−1), BP-OSD, comparison with the surface code | ⬜ in progress |
| 3. Resource estimate from the measured scaling | ⬜ |
| 4. Hand-written MWPM decoder for the toric code, checked against PyMatching | ⬜ in progress |
| 5. Lattice surgery: logical Z⊗Z measurement between two patches (merge and split) | ⬜ in progress |
| 6. The Part 4 decoder generalized to Stim detector error models, decoding Part 5 | ⬜ in progress |

## Part 1 result

![Logical error rate per round against physical error rate, for d = 3, 5, 7, 9](results/threshold.png)

Rotated surface code, Z-basis memory, d rounds of syndrome extraction, uniform
circuit-level depolarizing noise of strength p (two-qubit depolarizing after
every CNOT, data depolarizing each round, measurement and reset flips).
Decoded with PyMatching through `sinter`; error bars are sinter's likelihood
intervals. Raw counts: [`results/threshold.csv`](results/threshold.csv).

- **Threshold.** The curves for d = 7 and d = 9 cross between p = 0.9% and
  p = 1.0%; below that, larger codes win.
- **Error suppression.** At p = 0.2%, each step d → d + 2 lowers the logical
  error rate per round by a factor of about 5 (Λ ≈ 5.3, 5.2, 4.6 for
  3→5, 5→7, 7→9), reaching 8.5 × 10⁻⁶ per round at d = 9.
- **Cost.** Sampling plus decoding takes about 11 µs per shot at d = 9,
  p = 0.2% on a 2-core machine, rising to about 85 µs per shot near threshold,
  where the matching problem gets denser.

## Run it

Windows PowerShell:

```powershell
.\setup.ps1                       # venv, dependencies, quick run, tests
python scripts\threshold.py       # full sweep (a few minutes), rewrites results/
```

macOS/Linux:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && pip install -e .
python scripts/threshold.py --quick --out results/quick && pytest
```

## Layout

```
src/qec_stim/
  surface.py     rotated surface-code memory circuits with circuit-level noise
  decode.py      detector error model → PyMatching → logical error rate
  bb_code.py     bivariate-bicycle check matrices over F2          (Part 2)
  resource.py    scaling fit and qubit-count estimate               (Part 3)
  toric.py       toric-code lattice: edges, checks, syndromes        (Part 4)
  mwpm.py        minimum-weight perfect matching decoder             (Part 4)
  css_circuit.py multi-phase CSS syndrome-extraction circuit builder (Part 5)
  patches.py     rotated surface-code patches on a shared grid       (Part 5)
  lattice_surgery.py  the Z⊗Z merge/split protocol                   (Part 5)
  dem_mwpm.py    MWPM on a Stim detector error model                 (Part 6)
scripts/threshold.py         the Part 1 sweep, CSV and plot
scripts/toric_threshold.py   Part 4: my decoder vs PyMatching, code-capacity noise
scripts/lattice_surgery.py   Parts 5–6: lattice-surgery failure rates, PyMatching and mine
tests/                       pytest; unfinished parts skip
docs/walkthrough.md          how the Part 1 pipeline works, step by step
docs/decoder.md              the decoder, step by step
docs/lattice_surgery.md      lattice surgery, step by step
```

## How this was built

The Part 1 pipeline, the circuit builder and patch geometry (`css_circuit.py`,
`patches.py`), and the test harness were written with AI assistance and reviewed
by me. The code construction, resource estimate, matching decoders and the
lattice-surgery protocol (`bb_code.py`, `resource.py`, `mwpm.py`, `dem_mwpm.py`,
`lattice_surgery.py`) are my own work. The split is recorded in [CLAUDE.md](CLAUDE.md).

## References

**Simulation and decoding tools**
- C. Gidney, "Stim: a fast stabilizer circuit simulator", Quantum 5, 497 (2021).
- O. Higgott, C. Gidney, "Sparse Blossom: correcting a million errors per core second with minimum-weight matching" (PyMatching v2), Quantum 9, 1600 (2025).
- J. Roffe, D. R. White, S. Burton, E. Campbell, "Decoding across the quantum low-density parity-check code landscape" (BP-OSD, `ldpc`), Phys. Rev. Research 2, 043423 (2020).
- A. Hagberg, D. Schult, P. Swart, "Exploring network structure, dynamics, and function using NetworkX", Proc. SciPy (2008). Used for the matching in Parts 4 and 6.

**Surface code and its decoding (Parts 1, 4, 6)**
- A. Kitaev, "Fault-tolerant quantum computation by anyons", Ann. Phys. 303, 2 (2003).
- E. Dennis, A. Kitaev, A. Landahl, J. Preskill, "Topological quantum memory", J. Math. Phys. 43, 4452 (2002). Decoding by minimum-weight matching of defects.
- C. Wang, J. Harrington, J. Preskill, "Confinement-Higgs transition in a disordered gauge theory and the accuracy threshold for quantum memory", Ann. Phys. 303, 31 (2003). The ~10.3% code-capacity threshold.
- J. Edmonds, "Paths, trees, and flowers", Can. J. Math. 17, 449 (1965). The blossom algorithm for maximum matching.
- A. G. Fowler, M. Mariantoni, J. M. Martinis, A. N. Cleland, "Surface codes: Towards practical large-scale quantum computation", Phys. Rev. A 86, 032324 (2012). Rotated layout and the CNOT order that avoids hook errors.

**qLDPC codes (Part 2)**
- S. Bravyi, A. W. Cross, J. M. Gambetta, D. Maslov, P. Rall, T. J. Yoder, "High-threshold and low-overhead fault-tolerant quantum memory", Nature 627, 778 (2024).

**Lattice surgery (Part 5)**
- C. Horsman, A. G. Fowler, S. Devitt, R. Van Meter, "Surface code quantum computing by lattice surgery", New J. Phys. 14, 123011 (2012).
- L. Z. Cohen, I. H. Kim, S. D. Bartlett, B. J. Brown, "Low-overhead fault-tolerant quantum computing using long-range connectivity", Sci. Adv. 8 (2022), arXiv:2110.10794.
- A. Cowtan, S. Burton, "CSS code surgery as a universal construction", Quantum 8, 1344 (2024).
- D. J. Williamson, T. J. Yoder, "Low-overhead fault-tolerant quantum computation by gauging logical operators", arXiv:2410.02213 (2024).
