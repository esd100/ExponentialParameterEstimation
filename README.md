# Exponential Parameter Estimation — project repository

Multi-exponential parameter estimation from MR decay signals: survey of all known approaches, then original
advances. This repository is the **home of the code and the mirror of the living documents** (charter §7, v0.10).

```
docs/project/        living documents — charter.md (authoritative plan), gaps-register.md, bibliography.md (G1),
                     literature-requests.md (what to fetch, with DOIs), changelog.md (newest first),
                     phase0-findings.md, phase0-harness-status.md
mexp-harness/        the Phase 0 benchmark harness (Python package `mexp`, tests, scripts, results, data/ releases)
literature/          PDFs the project reads — local only, git-ignored (see literature/README.md)
appliedanalysisLanczos/  page images of Lanczos 1956 pp. 272–279 — local only, git-ignored
```

Charter versions are tagged (`git tag`: charter-v0.10, charter-v0.11, …) so any result can be traced to the plan it was
produced under. **License: not yet chosen** — needed before the harness or the dictionary is released (charter E1/E3).

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
pytest                                        # 64 tests
python scripts/phase0_conditioning.py         # SVD / Picard / truncation sweep
python scripts/phase0_threshold.py            # charter §1.2 threshold at the reference configuration
python scripts/phase0_threshold_tissues.py    # the same clauses over the tissue dictionary
python scripts/export_tissue_dictionary.py    # regenerate data/tissue_dictionary.json
python scripts/render_tissue_dictionary_doc.py # regenerate docs/tissue-dictionary.md
```

Rules the code enforces: no estimators until the harness is finished (charter G2); noise is never generated
outside `mexp/sim` (charter §4 k-space-first standing rule, `tests/test_kspace_first_rule.py`); numbers the harness
locks on are traced to a primary source or flagged (charter §7 provenance discipline — see `mexp/datasets/lanczos.py`
and `mexp/tissues.py`).
