# Writing the toric-code MWPM decoder

This is the "explain how you'd decode the surface code" interview answer, built
in code. Write `src/qec_stim/mwpm.py` in this order, running
`pytest tests/test_mwpm.py -v` as you go. Lattice indexing is in `toric.py`:
read its docstring first.

## The 30-second answer

> X errors on edges flip the Z-checks at both ends of each error chain, so the
> syndrome shows only the chains' endpoints, the anyons. Under independent noise
> with p < ½ the most likely error is the lightest one consistent with the
> syndrome, so I pair up the anyons with minimum total distance (minimum-weight
> perfect matching) and connect each pair by a shortest path. Error plus
> correction is then a closed loop. If the loop is contractible it's a product
> of stabilizers and decoding succeeded; if it wraps the torus it's a logical
> operator and decoding failed. Under code-capacity noise the threshold is about
> 10.3%. With measurement errors, the matching moves to a 3D space-time graph.

## 1. `torus_distance(u, v, L)`

Manhattan distance with wrap-around: in each direction take min(|Δ|, L − |Δ|).
Use `toric.coords` to get (i, j).

## 2. `shortest_path(u, v, L)`

Walk horizontally the short way, then vertically the short way, collecting
edge indices. The off-by-one trap: stepping **left** from column j uses
`h_edge(i, j − 1)`, not `h_edge(i, j)`, because horizontal edge h(i, j) joins
column j to column j + 1. Same for stepping **up**. The test checks that the
path's syndrome is exactly {u, v}.

## 3. `match_defects(defects, L)`

Complete graph on the defects, weight = −distance, then
`networkx.max_weight_matching(G, maxcardinality=True)`. `maxcardinality=True`
forces a *perfect* matching, which is the "minimum-weight perfect" part.
On a torus there is no boundary, so every defect gets a partner. Their number
is always even, since every error edge has two ends.

## 4. `decode(syn, L)`

Defects = `np.flatnonzero(syn)`. XOR the shortest paths of all matched pairs
into one correction array. The test `test_correction_weight_matches_pymatching`
checks that your total weight equals PyMatching's on 100 random syndromes. Both
are exact MWPM, so the weights must agree even when the chosen paths differ.

## 5. `logical_error(residual, L)`

`residual = error ^ correction` has zero syndrome, so it's a union of closed
loops. It's a logical error iff it crosses the vertical cut {h(i, 0)} or the
horizontal cut {v(0, j)} an odd number of times. Those two parities are the
logical-Z measurements. A contractible loop crosses any cut an even number of
times; that's the homology argument in one line.

## 6. Run the threshold

```bash
python scripts/toric_threshold.py
```

This scores your decoder and PyMatching the same way and writes
`results/toric_threshold.png`. The curves for different L should cross near
p ≈ 10%, and yours should sit on top of PyMatching's. Yours will be several times
slower, and the gap grows with L: networkx runs a general blossom algorithm on a
complete graph of defects, while PyMatching runs sparse blossom on the lattice
itself. That's a good thing to point out, not hide.

## Next: the same decoder on real circuits

Once this passes, `src/qec_stim/dem_mwpm.py` asks you to run the same algorithm
on the graph Stim builds from a circuit-level noise model. It has a boundary
node, weighted edges, and observables on edges instead of a homology check.
That's what decodes the lattice-surgery experiment (`docs/lattice_surgery.md`).

## Follow-up questions

- **Why is matching enough for the surface code but not for qLDPC codes?** Each surface-code error flips at most two checks, so the decoding problem is a graph. In qLDPC codes one error flips several checks, which makes a hypergraph, so you use belief propagation with ordered-statistics decoding (BP-OSD) instead.
- **Planar surface code vs toric?** The planar code has boundaries. A defect may match to the boundary instead of another defect, which you handle by adding a virtual boundary node. The logical is then a chain from boundary to boundary.
- **Measurement errors?** Repeat syndrome extraction d times and match in 3D. A defect becomes a change in a check's value between rounds, and time-like edges represent measurement errors. That's what Part 1's Stim pipeline does.
- **Why is the code-capacity threshold (~10%) so much higher than circuit-level (~1%)?** Code capacity assumes perfect syndrome measurement and no faults inside the extraction circuit.
- **Union-find vs MWPM?** Union-find grows clusters around defects. It's almost linear time and gives a slightly lower threshold (about 9.9% vs 10.3% at code capacity).
