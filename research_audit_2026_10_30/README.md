# Research audit — 30 October 2026

The original `D:\IITB techfest\Problem_3_Off_Policy_Evaluation_Research.md` is preserved unchanged. This package audits a research dossier and proposed project, not an already implemented novel algorithm.

## Deliverables

| Requested output | File |
|---|---|
| A. Revised manuscript | [Revised research](Problem_3_Off_Policy_Evaluation_Revised.md) |
| B. Mathematical audit and equation inventory | [Audit](Mathematical_Audit.md) |
| C. Assumptions and guarantees | [Table](Assumptions_and_Guarantees.md) |
| D. Executable verification and report | [Report](Verification_Report.md), [script](verification/verify.py), [raw results](results/verification_results.json) |
| E. Novelty and literature | [Literature audit](Novelty_and_Literature.md), [citation ledger](results/citation_ledger.csv) |
| F. Prioritized next steps | [Remediation plan](Prioritized_Remediation_Plan.md) |

Supporting provenance: `original_snapshot.md`, `initial_manifest.json`, `changes.json`, `manuscript.diff`, `mathematical_appendix.md`, and `verification/revise.py`. The official challenge PDF was inspected, extracted and its relevant pages visually reviewed; extracted text and page images are under `results/`.

## Main conclusions

Core IPS/DR algebra and the restricted binary sensitivity bounds withstand the checks under the stated assumptions. The consequential weaknesses are insufficiently explicit inference assumptions, population bounds being mistaken for confidence limits, and unvalidated policy-revision/safety claims. Known propensities do not make missing action support disappear; cross-fitting does not guarantee good finite-sample Wald coverage.

All 29 automated tests passed. Four primary scenarios each used 1,000 independent datasets of 2,000 rows. Nominal 95% cross-fitted DR Wald coverage was 90.6% with rare rewards and 63.9% in the weak-overlap off-prior scenario. These are measured counterexamples to practical reliability, not failures of the DR identification identity. Additional fixed-nuisance experiments distinguish double robustness from simultaneous misspecification and hidden confounding.

## Reproduce

Tested runtime: Python 3.12.14, NumPy 2.3.5. No SciPy, SymPy, pytest or plotting dependency is required. From this package directory:

```powershell
python -X utf8 verification/verify.py
python -X utf8 verification/revise.py
python -X utf8 verification/validate_package.py
```

If `python` is not on PATH, the executable used in this workspace is:

```powershell
& 'C:\Users\Ayushman\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 verification/verify.py
```

The first command rewrites results using fixed seeds; elapsed time may differ. The second regenerates the revised manuscript and diff from the snapshot, asserting the original source hash remains unchanged. The last validates artifact structure, script provenance, source preservation and result completeness. Scripts resolve package paths from their own location. Revision/source preservation checks expect this package to remain beside the original manuscript.

No OBD experiment, general symbolic CAS verification, sensitivity-endpoint confidence guarantee, adaptive/cluster inference implementation, or policy-revision benchmark was executed. The literature search is claim-focused, not exhaustive. Passing tests does not establish every manuscript claim or external validity.
