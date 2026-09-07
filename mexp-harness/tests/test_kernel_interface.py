"""
Kernel interface conformance.

Part A exercises the registered T2 CPMG kernel.

Part B is the evidence for the charter's 'pluggable-kernel abstraction from
day one' claim (§2): each other modality's *distinguishing requirement* —
affine atom with a nuisance (IR), nuisance-corrected apparent constant
(Look-Locker), complex signal with a second per-component parameter (T2*),
a 2-D design with a physically parameterised second axis (T1rho dispersion),
and a matrix-variate kernel on the PSD cone (diffusion tensor) — is written
against the *unchanged* base class inside this test file.  These throw-away
kernels are deliberately NOT registered: nothing un-scored enters the
taxonomy (charter G2).  When a real plugin for one of them is written, it
should pass the same generic checks.
"""
import numpy as np
import pytest

from mexp.axes import Modality
from mexp.design import Design, product_design, scattered, stacked_design, uniform
from mexp.kernels import OffsetAugmented, available, get
from mexp.kernels.base import Kernel
from mexp.params import AmplitudeField, ParamSpec, SignalField, Theta


# ---------------------------------------------------------------------------
# generic conformance checks applied to every kernel
# ---------------------------------------------------------------------------

def _generic_checks(kernel: Kernel, theta: Theta, design: Design, fd_tol: float = 1e-5):
    kernel.validate_design(design)
    Phi = kernel.atoms(theta.nonlinear, theta.nuisance, design)
    assert Phi.shape == (design.N, theta.K)
    s = kernel.forward(theta, design)
    assert s.shape == (design.N,)
    expect = Phi @ theta.amplitudes
    if theta.fixed.size:
        expect = expect + kernel.fixed_atoms(design) @ theta.fixed
    assert np.allclose(s, expect)
    assert np.iscomplexobj(s) == (kernel.signal_field is SignalField.COMPLEX)
    # Jacobian: shape and, if the kernel overrides it, agreement with finite differences
    J = kernel.jacobian(theta, design)
    assert J.shape == (design.N, theta.pack().size)
    Jfd = Kernel.jacobian(kernel, theta, design)
    assert np.max(np.abs(J - Jfd)) < fd_tol * max(1.0, np.max(np.abs(J)))
    # discretize on a grid == atoms on that grid
    grid = kernel.default_grid(16)
    A = kernel.discretize(design, grid, theta.nuisance)
    assert A.shape == (design.N, grid.shape[0])
    assert np.allclose(A, kernel.atoms(grid, theta.nuisance, design))
    # pack / unpack round trip
    th2 = theta.unpack(theta.pack())
    assert np.allclose(th2.amplitudes, theta.amplitudes)
    assert np.allclose(th2.nonlinear, theta.nonlinear)
    assert np.allclose(th2.nuisance, theta.nuisance)
    # wrong coordinates are rejected
    with pytest.raises(ValueError):
        kernel.validate_design(design.with_coords(tuple("zz%d" % i for i in range(len(design.coords)))))


# ---------------------------------------------------------------------------
# Part A: T2 CPMG
# ---------------------------------------------------------------------------

def test_registry_has_only_t2_in_phase0():
    assert available() == ["t2_cpmg"]


def test_t2_cpmg_conformance():
    k = get("t2_cpmg")
    th = Theta([0.2, 0.8], [[20.0], [80.0]])
    _generic_checks(k, th, uniform(32, 10.0))


def test_t2_cpmg_rejects_negative_amplitude_and_bad_T2():
    k = get("t2_cpmg")
    with pytest.raises(ValueError):
        k.forward(Theta([-0.1, 0.8], [[20.0], [80.0]]), uniform(8, 10.0))
    with pytest.raises(ValueError):
        k.forward(Theta([0.1, 0.8], [[0.0], [80.0]]), uniform(8, 10.0))


def test_offset_augmented_t2():
    k = OffsetAugmented(get("t2_cpmg"))
    th = Theta([0.2, 0.8], [[20.0], [80.0]], fixed=[0.05])
    d = uniform(16, 10.0)
    _generic_checks(k, th, d)
    s = k.forward(th, d)
    assert np.allclose(s - 0.05, get("t2_cpmg").forward(Theta([0.2, 0.8], [[20.0], [80.0]]), d))


def test_reference_signal_is_unattenuated_sum():
    k = get("t2_cpmg")
    assert k.reference_signal(Theta([0.2, 0.8], [[20.0], [80.0]])) == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Part B: the other modalities' requirements, on the unchanged base class
# ---------------------------------------------------------------------------

class _IR(Kernel):
    """T1 inversion recovery: affine atom with a global nuisance (inversion efficiency eta)."""
    name = "_test_t1_ir"
    modality = Modality.T1
    coords = ("TI",)
    component_params = (ParamSpec("T1", "ms", "log", lower=1e-9),)
    nuisance_params = (ParamSpec("eta", "", "linear", lower=0.0, upper=1.0),)
    amplitude_field = AmplitudeField.REAL   # polarity may be unresolved in magnitude data

    def physical_range(self):
        return ((50.0,), (5000.0,))

    def nuisance_defaults(self):
        return np.array([1.0])

    def atoms(self, xi, nu, design):
        ti = design.coord("TI")[:, None]
        T1 = np.asarray(xi).reshape(-1, 1)[:, 0][None, :]
        return 1.0 - 2.0 * nu[0] * np.exp(-ti / T1)


class _LookLocker(Kernel):
    """Look-Locker: dense uniform TI sampling; apparent T1* = (1/T1 - ln cos(alpha)/TR)^-1
    computed *inside the atom* from nuisance (alpha, TR), so the component parameter
    stays the true T1 and the Prony family sees a uniform grid (charter §2.3 route 1)."""
    name = "_test_t1_ll"
    modality = Modality.T1
    coords = ("TI",)
    component_params = (ParamSpec("T1", "ms", "log", lower=1e-9),)
    nuisance_params = (ParamSpec("alpha", "rad", "linear", 0.0, np.pi / 2), ParamSpec("TR", "ms", "linear", 1e-9))

    def physical_range(self):
        return ((50.0,), (5000.0,))

    def nuisance_defaults(self):
        return np.array([np.deg2rad(8.0), 10.0])

    def atoms(self, xi, nu, design):
        ti = design.coord("TI")[:, None]
        T1 = np.asarray(xi).reshape(-1, 1)[:, 0][None, :]
        alpha, TR = nu
        R1star = 1.0 / T1 - np.log(np.cos(alpha)) / TR
        Mss_over_M0 = (1.0 / T1) / R1star  # steady-state fraction
        return Mss_over_M0 - (1.0 + Mss_over_M0) * np.exp(-ti * R1star)


class _T2Star(Kernel):
    """T2* mGRE with retained phase: COMPLEX signal, two per-component parameters
    (T2*, frequency offset df), a global phase nuisance, complex amplitudes."""
    name = "_test_t2star"
    modality = Modality.T2STAR
    coords = ("TE",)
    component_params = (ParamSpec("T2star", "ms", "log", lower=1e-9), ParamSpec("df", "kHz", "linear", -np.inf, np.inf))
    nuisance_params = (ParamSpec("phi0", "rad", "linear", -np.pi, np.pi),)
    signal_field = SignalField.COMPLEX
    amplitude_field = AmplitudeField.COMPLEX

    def physical_range(self):
        return ((1.0, -0.5), (200.0, 0.5))

    def atoms(self, xi, nu, design):
        te = design.coord("TE")[:, None]
        xi = np.asarray(xi).reshape(-1, 2)
        T2s, df = xi[:, 0][None, :], xi[:, 1][None, :]
        return np.exp(-te / T2s + 2j * np.pi * df * te + 1j * nu[0])


class _T1rhoDispersion(Kernel):
    """T1rho dispersion: 2-D design (TSL, omega1); R1rho(omega1) = R0 + Rex kex^2/(kex^2 + omega1^2)
    (Chopra / Trott-Palmer form). Three per-component parameters, all physical."""
    name = "_test_t1rho_disp"
    modality = Modality.T1RHO
    coords = ("TSL", "w1")
    component_params = (ParamSpec("R0", "1/ms", "log", 1e-9), ParamSpec("Rex", "1/ms", "log", 1e-12),
                        ParamSpec("kex", "rad/ms", "log", 1e-9))

    def physical_range(self):
        return ((1e-3, 1e-4, 0.1), (0.1, 0.1, 100.0))

    def atoms(self, xi, nu, design):
        tsl = design.coord("TSL")[:, None]
        w1 = design.coord("w1")[:, None]
        xi = np.asarray(xi).reshape(-1, 3)
        R0, Rex, kex = (xi[:, j][None, :] for j in range(3))
        R = R0 + Rex * kex**2 / (kex**2 + w1**2)
        return np.exp(-tsl * R)


class _DiffusionTensor(Kernel):
    """Matrix-variate Laplace kernel: exp(-B:D) with B, D symmetric 3x3 given by
    (xx, yy, zz, xy, xz, yz). Six per-component parameters; grid = any table of PSD tensors."""
    name = "_test_dti_dist"
    modality = Modality.DIFFUSION
    coords = ("bxx", "byy", "bzz", "bxy", "bxz", "byz")
    component_params = tuple(ParamSpec(f"D{c}", "um^2/ms", "linear", -np.inf, np.inf)
                             for c in ("xx", "yy", "zz", "xy", "xz", "yz"))

    def physical_range(self):
        return ((0.1, 0.1, 0.1, -0.5, -0.5, -0.5), (3.0, 3.0, 3.0, 0.5, 0.5, 0.5))

    def atoms(self, xi, nu, design):
        B = design.points                     # (N, 6)
        D = np.asarray(xi).reshape(-1, 6)     # (M, 6)
        w = np.array([1, 1, 1, 2, 2, 2.0])    # off-diagonals count twice in B:D
        return np.exp(-(B * w) @ D.T)


def test_ir_with_nuisance():
    k = _IR()
    th = Theta([0.3, 0.7], [[300.0], [1200.0]], nuisance=[0.95])
    d = scattered([50, 100, 200, 400, 800, 1600, 3200], coord="TI")   # classic irregular TIs
    _generic_checks(k, th, d)
    assert k.jacobian(th, d).shape[1] == 2 + 2 + 1                     # a, T1, eta


def test_look_locker_uniform_dense_grid():
    k = _LookLocker()
    th = Theta([0.3, 0.7], [[300.0], [1200.0]], nuisance=[np.deg2rad(8.0), 10.0])
    d = uniform(64, 25.0, start=25.0, coord="TI")
    _generic_checks(k, th, d)
    assert d.lattice_indices() is not None                             # Prony-family ready


def test_t2star_complex_two_parameter_components():
    k = _T2Star()
    th = Theta(np.array([0.3 * np.exp(0.2j), 0.7]), [[10.0, 0.03], [50.0, 0.0]], nuisance=[0.4])
    d = uniform(24, 2.0, start=2.0)
    _generic_checks(k, th, d, fd_tol=1e-5)
    J = k.jacobian(th, d)
    assert np.iscomplexobj(J) and J.shape[1] == 2 + 2 + 4 + 1          # Re a, Im a, (T2*, df) x2, phi0
    assert Kernel.as_real_rows(J).shape == (2 * d.N, J.shape[1])
    grid = k.default_grid(64)
    assert grid.shape[1] == 2                                          # 2-D product grid for p = 2


def test_t1rho_dispersion_two_dimensional_design():
    k = _T1rhoDispersion()
    tsl = uniform(6, 10.0, start=2.0, coord="TSL")
    w1 = scattered([0.5, 1.0, 2.0, 4.0], coord="w1")                  # rad/ms spin-lock amplitudes
    d = product_design(tsl, w1)
    assert d.N == 24 and d.coords == ("TSL", "w1")
    th = Theta([1.0], [[0.02, 0.01, 2.0]])
    _generic_checks(k, th, d)


def test_diffusion_tensor_matrix_variate_kernel():
    k = _DiffusionTensor()
    rng_free_dirs = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, 1, 0], [1, 0, 1], [0, 1, 1]], float)
    rng_free_dirs /= np.linalg.norm(rng_free_dirs, axis=1, keepdims=True)
    rows = []
    for b in (0.0, 1.0, 2.0):
        for g in rng_free_dirs:
            Bm = b * np.outer(g, g)
            rows.append([Bm[0, 0], Bm[1, 1], Bm[2, 2], Bm[0, 1], Bm[0, 2], Bm[1, 2]])
    d = stacked_design(np.array(rows), k.coords)
    D1 = [1.7, 0.3, 0.3, 0.0, 0.0, 0.0]   # prolate tensor
    D2 = [0.8, 0.8, 0.8, 0.0, 0.0, 0.0]   # isotropic
    th = Theta([0.6, 0.4], [D1, D2])
    _generic_checks(k, th, d)
    # discretize on an explicit table of PSD tensors (an (M, 6) grid), the way a
    # diffusion-tensor-distribution method would
    grid = np.array([D1, D2, [1.0, 1.0, 1.0, 0.1, 0.0, 0.0]])
    assert k.discretize(d, grid).shape == (d.N, 3)
