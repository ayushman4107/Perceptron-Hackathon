# Innovation research and falsification package

**Outcome:** no assessed candidate supports a validated new-algorithm claim. The strongest practical idea—comparison through a shared uncertainty region—is mathematically sound and useful relative to separately comparing policy-value intervals, but matches the established robust objective exactly. This is an explicit negative novelty finding, not an unfinished positive claim.

The package contains all seven requested deliverable categories. Under the mission's “if no candidate survives” provision, the working code is a research verification prototype; no rejected candidate was integrated into an application or branded as new. There was no application in the workspace to modify. The original manuscript and prior audit remain intact.

| Deliverable | Artifact |
|---|---|
| A: research, finalist cards, scores, rejection decisions | [Innovation research report](Innovation_Research_Report.md) |
| B: estimand, assumptions, derivation, guarantees, limitations | [Technical specification](Technical_Specification.md) |
| C: closest primary sources and exact comparison scope | [Literature comparison](Literature_Comparison.md) |
| D: protocol fixed before the experiment | [Experimental protocol](Experimental_Protocol.md) |
| E: working verification prototype, tests and reproduction | [Core](src/core.py), [simulation](src/simulation.py), [tests](tests/test_core.py), [runner](run_experiments.py) |
| F: measured results and negative findings | [Results report](Results_Report.md), [all scenario summaries](results/Complete_Summary.md) |
| G: technical explanation and reproducible demo | [Judge explanation](Judge_Explanation.md), [demo](demo.py) |

## What was executed

- 17 automated tests, all passed, including independent exhaustive vertex checks, support counterexamples, exact invariants and invalid inputs.
- 36,000 independent synthetic logs: 9 scenarios × 2 sample sizes × 2 policy counts × 1,000 repetitions; 6 methods evaluated per log.
- A predetermined first-seed demonstration and local runtime/scalability checks.
- Targeted primary-source research; no claim of exhaustive literature coverage.

Primary result: beneficial decision in 1,000/1,000 trials for joint contrast, the exact robust reference, and paired DR; 0/1,000 for separate value bounds. The maximum discrepancy between joint contrast and the exact robust reference was zero. That equality, together with the derivation, rejects the new-method hypothesis. Hidden confounding and unmodeled shift produced harmful confident decisions; rare outcomes and weak overlap exposed severe conservatism in the box method.

## Reproduction

Tested environment: Python 3.12.14, NumPy 2.3.5, standard library. No GPU or network access is required. From this directory:

```powershell
python -X utf8 -m unittest discover -s tests -v
python -X utf8 run_experiments.py
python -X utf8 write_results.py
python -X utf8 demo.py
python -X utf8 validate.py
```

If `python` is absent from PATH, this workspace used:

```powershell
& 'C:\Users\Ayushman\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -X utf8 run_experiments.py
```

The runner uses deterministic seeds and rewrites only `results/`. It records the protocol and source hashes before sampling. Results include `trials.csv` (216,000 method-trial rows), `results.json`, `configurations.json`, `runtime.json`, `run_manifest.json`, and `tests.txt`. Run time and platform details may change across machines. `write_results.py` only formats measured outputs; `demo.py` uses the first primary seed without selection. `validate.py` checks artifact completeness, score arithmetic, manifests, raw-result consistency and original preservation.

## Research code structure

`src/core.py` handles validation, aggregation, confidence regions, comparison and baseline inference. `src/simulation.py` supplies policies, synthetic log generation and evaluator-only truth. `run_experiments.py` applies the frozen protocol and computes metrics. `write_results.py` produces tables; `demo.py` reproduces the example. There is no real-data loader or UI because neither is required to falsify this candidate's novelty. A separate input loader would be required for real logged data.

## What remains unexecuted or unresolved

No OBD replication, online data collection, full published algorithm reproduction, general continuous-context inference, estimated target-population uncertainty, adaptive logs, or sensitivity-adjusted confidence procedure was run. Ordinary paired DR/Wald is not treated as selection-safe. No claim of robustness to confounding/shift follows from the deliberate failures.

For a hackathon implementation, use this as an honest evidence module alongside established OPE methods. For a research-novelty claim, a genuinely different mechanism and an advantage over the appropriate strong baseline are still needed. The research report specifies two concrete follow-up questions and the comparisons they would require.
