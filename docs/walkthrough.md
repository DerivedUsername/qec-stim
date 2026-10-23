# How Part 1 works

Read this until you can explain each step without looking. These are the
questions an interviewer will ask about the threshold plot.

## 1. The circuit (`surface.py`)

`stim.Circuit.generated("surface_code:rotated_memory_z", ...)` builds a
distance-d rotated surface code patch: d² data qubits plus d² − 1 measurement
qubits (half measure X-stabilizers, half Z-stabilizers). The experiment:

1. reset all data qubits to |0⟩ (so the logical state is |0_L⟩),
2. run d rounds of syndrome extraction (CNOT ladders, then measure the ancillas),
3. measure every data qubit in the Z basis and read off the logical Z.

**Why Z memory?** It checks whether a logical X error happened. The X-memory
version is symmetric for this noise model.

## 2. The noise model

Each knob is set to the same p:

| Stim argument | What it adds |
|---|---|
| `after_clifford_depolarization` | 2-qubit depolarizing channel after every CNOT |
| `before_round_data_depolarization` | 1-qubit depolarizing on each data qubit, each round |
| `before_measure_flip_probability` | measurement result flipped with probability p |
| `after_reset_flip_probability` | reset produces the wrong state with probability p |

This is **circuit-level** noise: faults can occur at every location in the
syndrome-extraction circuit, including on the ancillas mid-circuit. That's why
the threshold (~1%) is far below the code-capacity threshold (~10%, data
errors only, perfect measurements). Be ready to explain the three noise-model
levels: code capacity < phenomenological < circuit-level.

## 3. Detectors and observables

A **detector** is a set of measurements whose parity is deterministic when
nothing goes wrong. Typically that's one stabilizer measured in two
consecutive rounds: if the parity flips, something happened in between. The
**observable** is the logical Z, read from the final data measurements.

Detector count: round 1 and the final readout each give (d²−1)/2 Z-checks.
Rounds 2…d each compare all d²−1 stabilizers with the round before. Total:
d·(d²−1). `tests/test_surface.py` checks this.

## 4. The detector error model (`decode.py`)

`circuit.detector_error_model(decompose_errors=True)` lists every independent
fault, its probability, which detectors it flips, and whether it flips the
observable. For the surface code each fault flips at most two detectors (after
decomposition), so faults are **edges** in a graph whose nodes are detectors.
Faults at the boundary flip one detector and connect to a virtual boundary node.

## 5. Matching

Given the detectors that fired in one shot, minimum-weight perfect matching
pairs them up (or pairs one with the boundary) using the most likely set of
edges, with weight −log(p_edge / (1 − p_edge)). The decoder then predicts
whether the matched edges flip the observable. A **logical error** is a shot
where the prediction is wrong. PyMatching v2 implements this with the
"sparse blossom" algorithm.

## 6. Threshold and Λ

- The logical error rate per round is computed from the whole-experiment rate
  P over r rounds by solving P = (1 − (1 − 2ε)^r) / 2 for ε.
- Below threshold, ε(d) ≈ C (p / p_th)^((d+1)/2), so increasing d by 2
  divides ε by Λ ≈ p_th / p. That's the "error suppression factor" Google
  reports for its hardware (Λ ≈ 2 on the Willow chip). In our data,
  Λ ≈ 5 at p = 0.2%.
- The **threshold** is where curves for different d cross. Here it's between
  0.9% and 1.0%. Finite-size effects shift the crossing slightly between
  pairs of distances.

## 7. Questions to prepare

- Why does circuit-level noise lower the threshold so much compared with code capacity?
- Why do the error bars widen at large d and small p? (Few logical errors observed.)
- What would change with a hardware-calibrated noise model such as SI1000?
- Why does decoding get slower near threshold? (More detection events, so a denser matching problem.)
- Why can't plain matching decode a bivariate-bicycle code? (Its faults flip more than two detectors, so the decoding problem is a hypergraph, not a graph. That's why Part 2 uses BP-OSD.)
