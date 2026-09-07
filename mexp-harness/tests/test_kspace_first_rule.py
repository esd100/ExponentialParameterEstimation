"""
Structural enforcement of the charter §4 standing rule: the only place in the
package that may draw random numbers or mention an image-domain noise model
is mexp/sim/ (and there, only add_kspace_noise once it exists).  A module
outside mexp/sim that imports a random generator fails this test.
"""
import pathlib
import re

import pytest

import mexp
from mexp.sim import ImageDomainNoiseForbidden, add_image_noise

PKG = pathlib.Path(mexp.__file__).parent
# What is forbidden is *generating* noise or injecting it into image-domain data.
# Naming a likelihood (Rician, non-central chi) is fine: the CRLB module and,
# later, the magnitude-arm estimators must evaluate those likelihoods.
FORBIDDEN = [
    r"np\.random", r"numpy\.random", r"default_rng", r"\brandn?\(", r"\.rvs\(",
    r"\brice\.rvs", r"add_noise\(", r"add_image_noise\(", r"noisy_image", r"noise_floor",
]


def test_no_random_or_noise_model_outside_sim():
    offenders = []
    for path in PKG.rglob("*.py"):
        rel = path.relative_to(PKG).as_posix()
        if rel.startswith("sim/"):
            continue
        text = path.read_text()
        # strip docstrings / comments crudely: only flag code lines
        for i, line in enumerate(text.splitlines(), 1):
            code = line.split("#", 1)[0]
            if code.strip().startswith(('"""', "'''", '"', "'")):
                continue
            for pat in FORBIDDEN:
                if re.search(pat, code):
                    offenders.append(f"{rel}:{i}: {line.strip()}")
    assert not offenders, "image-domain noise / RNG use outside mexp/sim:\n" + "\n".join(offenders)


def test_image_domain_noise_entry_point_is_unusable():
    with pytest.raises(ImageDomainNoiseForbidden):
        add_image_noise(None, sigma=1.0)
