import pytest


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "provisional_pending_primary: test locked on secondary sources only (charter v0.7 §7 provenance "
        "discipline); re-check against the primary before treating as final",
    )
