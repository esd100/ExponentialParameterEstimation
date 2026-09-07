"""
Kernel registry. Plugins register by name; the rest of the harness addresses
kernels by that name (it is the `kernel` field of :class:`mexp.axes.Cell`).

Only T2 CPMG is registered in Phase 0.  The interface is exercised against the
other modalities' requirements in tests/test_kernel_interface.py using
throw-away conformance kernels that are *not* registered, so that nothing
un-scored can leak into the taxonomy (charter G2).
"""
from __future__ import annotations

from typing import Type

from .base import Kernel, OffsetAugmented
from .t2_cpmg import T2CPMG

_REGISTRY: dict[str, Type[Kernel]] = {}


def register(cls: Type[Kernel]) -> Type[Kernel]:
    name = getattr(cls, "name", None)
    if not name:
        raise ValueError("kernel plugin must define a class attribute `name`")
    if name in _REGISTRY and _REGISTRY[name] is not cls:
        raise ValueError(f"kernel name {name!r} already registered")
    _REGISTRY[name] = cls
    return cls


def get(name: str) -> Kernel:
    try:
        return _REGISTRY[name]()
    except KeyError as e:
        raise KeyError(f"unknown kernel {name!r}; registered: {sorted(_REGISTRY)}") from e


def available() -> list[str]:
    return sorted(_REGISTRY)


register(T2CPMG)

__all__ = ["Kernel", "OffsetAugmented", "T2CPMG", "register", "get", "available"]
