# Lattice surgery: measuring Z⊗Z between two patches

This part answers a specific kind of job requirement: "lattice surgery / code
surgery" and "using chain complexes to construct measurement protocols for CSS
codes". You write `src/qec_stim/lattice_surgery.py` (about 40 lines). The Stim
plumbing is in `css_circuit.py` and `patches.py`, so your code is only the
protocol: which checks, when, and what the outcome is.

## The idea in one paragraph

Two rotated surface-code patches A and B sit side by side, with a column of
fresh qubits (the seam) between them. Measuring the stabilizers of the single
big patch covering A + seam + B for d rounds, then going back to measuring A and
B separately, performs a logical Z_A Z_B measurement. The new Z checks along the
seam each give a random outcome, but their product is fixed: it is Z_A Z_B. No
logical information is lost, because the merged patch still encodes the
operator Z_A (equivalently Z_B) and X_A X_B. Splitting by measuring the seam in
X restores the two patches.

## Why the product of the new Z checks is Z_A Z_B

With the grid conventions in `patches.py`, each seam qubit (d, y) lies in
exactly two new Z checks, so its Z factors cancel in the product. Each qubit of
column d − 1 (A's right edge) and column d + 1 (B's left edge) lies in exactly
one new Z check. The product is therefore Z on column d − 1 times Z on column
d + 1, which is logical Z_A times logical Z_B. Check this against the picture
you draw, not just the text.

**Chain-complex view (the one to use in a cover letter).** A CSS code is a
chain complex C₂ → C₁ → C₀ over F₂: Z checks, qubits, X checks, with ∂₂ sending
a Z check to its support and ∂₁ sending a qubit to the X checks containing it
(∂₁∂₂ = 0 because the checks commute). Logical Z operators are the homology
classes H₁ = ker ∂₁ / im ∂₂. Merging glues two complexes along the seam. The
new Z checks are new cells whose total boundary is the sum of two
representatives of logical Z. That makes the logical class a boundary in the
merged complex: measuring the new cells measures it. Code surgery for general
qLDPC codes (Cohen et al.; Cowtan–Burton) does exactly this gluing for
arbitrary CSS codes, and the hard part is keeping the distance up when the
logical operators aren't simple lines.

## Writing `zz_measurement`

1. Build A = `rectangle(d, d, 0, 0)`, B = `rectangle(d, d, d + 1, 0)`,
   M = `rectangle(2 * d + 1, d, 0, 0)`, and the seam `[(d, y) for y in range(d)]`
   (as floats, since coordinates are floats).
2. Three `Phase`s, as in the module docstring. The seam is reset in X at the
   start of phase 1 and measured in X at its end.
3. The new Z checks: those in M whose `(ancilla, basis)` is not in A + B.
   The Z⊗Z observable is `[Rec("check", 1, a, 0) for a in new_z]`.
4. basis "Z": add Z_A and Z_B as final data readouts of one column each
   (`logical_z` helps). basis "X": one observable, row 0 of A and of B read out
   at the end, plus the seam qubit (d, 0) read out at the split.
5. `build(phases, observables, p)`.

Stim then checks you: `circuit.detector_error_model()` raises if any detector or
observable is non-deterministic. That's the fastest feedback you'll get on
whether your protocol is right. `pytest tests/test_lattice_surgery.py -v` also
checks the circuit distance is d.

## Why d rounds

`test_one_round_is_not_enough` shows the distance drops to 1 with one merged
round. A single measurement error on one new Z check flips the Z⊗Z outcome, and
nothing later catches it, because those checks stop existing after the split.
Repeating the merged checks d times makes such a fault show up as a
detection-event pair in time. This is the "time-like distance" of lattice
surgery.

## Decoding it

PyMatching decodes the whole experiment from its detector error model, the same
way it decodes the memory experiment. Your `dem_mwpm.py` (see `docs/decoder.md`,
then its docstring) generalizes your toric-code decoder to these circuits.
`scripts/lattice_surgery.py --mine` puts your decoder's points on the same plot
as PyMatching's.

## Questions to be ready for

- Why are the new Z checks' first outcomes random? (The seam starts in |+⟩, an X eigenstate, which anticommutes with Z checks touching it.)
- What happens to the old weight-2 X checks on A's right edge? (They grow into weight-4 checks including seam qubits. Their value is still known: old value × X_seam = old value, since the seam is in |+⟩.)
- Why is X_A alone not preserved, but X_A X_seam X_B is? (X_A anticommutes with the new Z checks it crosses.)
- How would you measure X_A X_B instead? (Merge along the other boundaries, the Z-type top/bottom edges, with the seam in |0⟩.)
- What's the cost? (One extra column of d data qubits plus its ancillas, and d rounds of time.)
- Lattice surgery vs transversal gates? (Lattice surgery only needs nearest-neighbour connectivity in 2D, which is why it's the standard for superconducting hardware.)

## References

- C. Horsman, A. Fowler, S. Devitt, R. Van Meter, "Surface code quantum computing by lattice surgery", New J. Phys. 14, 123011 (2012).
- L. Z. Cohen, I. H. Kim, S. D. Bartlett, B. J. Brown, "Low-overhead fault-tolerant quantum computing using long-range connectivity", Sci. Adv. 8 (2022).
- A. Cowtan, S. Burton, "CSS code surgery as a universal construction", Quantum (2024).
- D. Williamson, T. Yoder, "Low-overhead fault-tolerant quantum computation by gauging logical operators" (2024).
