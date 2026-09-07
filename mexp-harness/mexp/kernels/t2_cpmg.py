"""
T2 CPMG kernel: the pure real Laplace kernel (charter §1, §2.2 column 1).

    phi(TE; T2) = exp(-TE / T2)

No nuisance parameters: refocusing-pulse imperfection (B1) and stimulated
echoes are *not* a nuisance on this kernel; they change the atom shape and
belong to a separate EPG-atom kernel (`t2_cpmg_epg`, xi=(T2,), nu=(B1, T1))
which is the charter's 'physically realistic path' and is scored as model
misspecification against this one.  Keeping them apart is what lets the
harness measure the misspecification cost instead of hiding it.

Units: TE and T2 in the same unit (ms by default). The kernel is
dimensionless in the ratio, so the Lanczos test uses x and 1/rate directly.
"""
from __future__ import annotations

import numpy as np

from ..axes import Modality
from ..design import Design
from ..params import AmplitudeField, ParamSpec, SignalField, Theta
from .base import Kernel


class T2CPMG(Kernel):
    name = "t2_cpmg"
    modality = Modality.T2
    coords = ("TE",)
    component_params = (ParamSpec("T2", "ms", "log", lower=1e-12, description="transverse relaxation time"),)
    nuisance_params = ()
    signal_field = SignalField.REAL
    amplitude_field = AmplitudeField.POSITIVE
    citation = "Whittall & MacKay 1989 J Magn Reson 84:134 (discretised form); Lanczos 1956 ch. IV (degeneracy)"

    # physiological default for the T-range axis: 5 ms (myelin water, short) .. 2000 ms (CSF)
    _range = ((5.0,), (2000.0,))

    def physical_range(self):
        return self._range

    def atoms(self, xi: np.ndarray, nu: np.ndarray, design: Design) -> np.ndarray:
        te = design.coord("TE")[:, None]          # (N, 1)
        T2 = np.asarray(xi, dtype=float).reshape(-1, 1)[:, 0][None, :]  # (1, M)
        return np.exp(-te / T2)

    def jacobian(self, theta: Theta, design: Design, rel_step: float = 1e-6) -> np.ndarray:
        """Analytic: dS/da_k = e^{-t/T_k};  dS/dT_k = a_k t / T_k^2 e^{-t/T_k}."""
        self.validate_design(design)
        self.validate_theta(theta)
        te = design.coord("TE")[:, None]
        T2 = theta.nonlinear[:, 0][None, :]
        E = np.exp(-te / T2)
        dA = E
        dT = theta.amplitudes[None, :] * te / T2**2 * E
        cols = [dA, dT]
        if theta.fixed.size:
            cols.append(self.fixed_atoms(design))
        return np.hstack(cols)
