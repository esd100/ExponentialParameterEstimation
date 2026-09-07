# Exponential Parameter Estimation — project repository

Multi-exponential parameter estimation from MR decay signals: survey of all known approaches, then original
advances. This repository is the **home of the code and the mirror of the living documents** (charter §7, v0.10).

```
docs/project/        living documents — charter.md (authoritative plan), gaps-register.md, bibliography.md (G1),
                     changelog.md (newest first), phase0-findings.md, phase0-harness-status.md
mexp-harness/        the Phase 0 benchmark harness (Python package `mexp`, tests, scripts, results)
```

## Sync rule (charter §7)

The same six documents live in two places: here under `docs/project/`, and in the Claude project
"Exponential Parameter Estimation" (top-level `charter.md`, `gaps-register.md`, `bibliography.md`; `claude/changelog.md`,
`claude/phase0-findings.md`, `claude/phase0-harness-status.md`). Every working session ends by committing this
repository *and* writing the same files to the project. At session start the project copy is read first; if the two
disagree, the higher version number wins and the other is brought up to date before any work is done.

## Running the harness

```
cd mexp-harness
pip install -e ".[dev]"
pytest                                        # 60 tests
python scripts/phase0_conditioning.py         # SVD / Picard / truncation sweep
python scripts/phase0_threshold.py            # charter §1.2 threshold at the reference configuration
python scripts/phase0_threshold_tissues.py    # the same clauses over the tissue dictionary
```

Rules the code enforces: no estimators until the harness is finished (charter G2); noise is never generated
outside `mexp/sim` (charter §4 k-space-first standing rule, `tests/test_kspace_first_rule.py`); numbers the harness
locks on are traced to a primary source or flagged (charter §7 provenance discipline — see `mexp/datasets/lanczos.py`
and `mexp/tissues.py`).
