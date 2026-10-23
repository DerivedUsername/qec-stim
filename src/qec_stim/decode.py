"""Decoding a Stim circuit with minimum-weight perfect matching (PyMatching).

The pipeline for one experiment:
  1. circuit.detector_error_model()  -> every fault, the detectors it flips,
     and whether it flips the logical observable;
  2. pymatching.Matching.from_detector_error_model(dem) -> a matching graph;
  3. sample detector events + true observable flips;
  4. decode each shot's detector events -> predicted observable flip;
  5. a logical error is a shot where prediction != truth.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pymatching
import stim


@dataclass(frozen=True)
class Result:
    shots: int
    errors: int

    @property
    def rate(self) -> float:
        return self.errors / self.shots if self.shots else float("nan")

    def per_round(self, rounds: int) -> float:
        """Per-round logical error rate e, from P = (1 - (1 - 2e)^rounds) / 2."""
        p = self.rate
        return (1 - (1 - 2 * p) ** (1 / rounds)) / 2 if p < 0.5 else float("nan")


def logical_error_rate(circuit: stim.Circuit, shots: int, seed: int | None = None) -> Result:
    """Sample `shots` runs of `circuit` and count logical errors after MWPM decoding."""
    dem = circuit.detector_error_model(decompose_errors=True)
    matcher = pymatching.Matching.from_detector_error_model(dem)
    sampler = circuit.compile_detector_sampler(seed=seed)
    detections, observables = sampler.sample(shots, separate_observables=True)
    predictions = matcher.decode_batch(detections)
    errors = int(np.sum(np.any(predictions != observables, axis=1)))
    return Result(shots=shots, errors=errors)
