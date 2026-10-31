# PoliSee — Counterfactual Policy Evaluation

Team research for IIT Bombay Techfest, **Problem 3: Did the Policy Actually Work, or Did It Just Look Like It Did?** Updated 30 October 2026.

Our project evaluates which policy changes logged data can support. The latest extension groups actions only when their policy-to-logger probability ratios match, preserving the comparison while reducing its dimension. Full Open Bandit campaign experiments and synthetic tests now support a concrete proposal; grouped exact-binomial bounds outperformed the more elaborate predictive likelihood variant in the principal comparisons.

## Start here

1. [Current abstract](obd_research_2026_10_30/ABSTRACT.md) — 797 words covering all eight requested sections, with measured results.
2. [Illustrated submission PDF](obd_research_2026_10_30/output/pdf/Abstract_with_Evidence.pdf) — two abstract pages including a result plot, plus an evidence supplement and a full portrait system-architecture page.
3. [Latest research package](obd_research_2026_10_30/README.md), [results](obd_research_2026_10_30/RESULTS_REPORT.md), and [technical derivation](obd_research_2026_10_30/TECHNICAL_DERIVATION.md) — data access, assumptions, code, figures, and full comparisons.
4. [Revised research document](research_audit_2026_10_30/Problem_3_Off_Policy_Evaluation_Revised.md) — detailed foundations, methods, literature, assumptions, and limitations.
5. [Earlier likelihood extension](likelihood_extension_2026_10_30/TECHNICAL_NOTE.md) and [its results](likelihood_extension_2026_10_30/RESULTS.md) — the preceding experiment, retained unchanged for provenance.

The [current plain-text abstract](obd_research_2026_10_30/ABSTRACT_plain.txt) is available for submission forms. The older `abstract_submission_2026_10_31` draft is superseded; it is retained as historical material.

## Research status and evidence

This repository contains research documents, numerical prototypes, real-data evaluation, endpoint models, tests, figures, and saved benchmarks. It is **not yet an integrated application**. The Streamlit interface and a specified hidden-confounding sensitivity module remain planned work.

| Package | Purpose | Recorded evidence |
|---|---|---|
| [Research audit](research_audit_2026_10_30/README.md) | Corrected foundations and mathematical checks | 29 passing tests; finite-sample failures of ordinary Wald inference documented |
| [Earlier innovation investigation](innovation_research_2026_10_30/README.md) | Shared-region comparison and novelty falsification | 17 passing tests; 36,000 synthetic logs; candidate matched an established robust comparator |
| [Earlier likelihood extension](likelihood_extension_2026_10_30/TECHNICAL_NOTE.md) | Joint likelihood region and policy-contrast optimization | 13 passing tests; 8,000 synthetic logs; primary comparison tied the strong KL-box baseline |
| [Current OBD extension](obd_research_2026_10_30/README.md) | Exact policy-ratio compression and comparative inference | 16 passing tests; 6.77 million real rows processed; 8,000 additional synthetic logs; 11 methods |
| [Current submission materials](obd_research_2026_10_30/ABSTRACT.md) | Evidence-based proposal and illustrated supplement | Eight sections; 797-word abstract; six standalone figures |

**Do not claim a world-first algorithm or universal superiority.** On the fixed primary OBD split, grouped exact bounds reduced median interval width by 82.6% versus the original item-level likelihood and 79.0% versus item-level KL bounds. The predictive likelihood extension did not beat the stronger grouped exact baseline overall. Real-data references have sampling uncertainty, and repeated splits overlap. Confidence statements require the declared identification and statistical assumptions.

The current abstract is the source for the proposed project scope. Earlier research explains how that scope evolved; rejected novelty claims are retained as evidence, not current promises. The [original research manuscript](Problem_3_Off_Policy_Evaluation_Research.md) is preserved for provenance; use the revised manuscript for the audited account.

## Working with the code

Recorded environment: Python 3.12.14. The latest package additionally uses pandas, SciPy, Matplotlib and PDF libraries; versions are pinned. No GPU is needed. From the repository root:

```sh
python -m pip install -r requirements.txt
python -X utf8 -m unittest discover -s innovation_research_2026_10_30/tests -v
```

Run the latest extension's tests from its directory:

```sh
cd obd_research_2026_10_30
python -X utf8 -m unittest test_methods -v
```

Each package includes its experimental protocol, code, result summaries, raw CSVs, and provenance manifests. Consult package documentation before rerunning experiments: runners regenerate saved outputs and can take several minutes. The original audit and earlier innovation package have their own reproduction instructions. Historical logs may mention the original author's local paths; these are provenance, not required installation paths.

## Suggested team ownership

- Statistical methods, assumptions, and evaluation metrics.
- Synthetic data, estimator integration, and backend.
- Demo interface, architecture, and presentation.

These are proposed roles, not fixed assignments. Keep measured results separate from planned functionality when editing the abstract or presenting the project.
