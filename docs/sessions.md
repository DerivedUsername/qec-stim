# Roadmap

- [x] **Part 1: surface-code threshold** (AI-assisted). Circuit-level noise, PyMatching, d = 3–9, results committed.
- [ ] **Read `docs/walkthrough.md`** until you can explain each step. Before applying anywhere.
- [ ] **Part 2a: BB code construction** [you]. `bb_code.py`; done when `tests/test_bb_code.py` passes ([[72,12,6]] and [[144,12,12]] give k = 12).
- [ ] **Part 2b: BP-OSD decoding** [you]. Code-capacity noise first: sample X errors, compute syndromes with H_Z,
      decode with `ldpc.BpOsdDecoder`, count logical failures using the logical operators. Plot against the
      surface code at a similar number of physical qubits, and **label the noise model on the plot**.
- [ ] **Part 2c (stretch): BB code under circuit-level noise.** Use the syndrome-extraction circuit from Bravyi et al. 2024.
- [ ] **Part 3: resource estimate** [you]. `resource.py`: fit C and p_th from `results/threshold.csv`, then estimate the
      physical qubits needed to run the AJL trefoil circuit fault-tolerantly.
- [ ] **Part 4 (optional): one logical operation.** For example a lattice-surgery merge in Stim. Several postings ask
      about logical operations beyond memory.
