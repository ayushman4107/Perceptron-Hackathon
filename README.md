# Perceptron Hackathon — Off-Policy Evaluation

Team research for IIT Bombay Techfest, **Problem 3: Did the Policy Actually Work, or Did It Just Look Like It Did?** Updated 30 October 2026.

Our proposed project evaluates whether a policy-change claim survives statistically plausible alternative reward models. It combines standard off-policy estimators with a finite-context confidence-region procedure that can report improvement, deterioration, or insufficient evidence. The planned report also exposes an adverse reward model that challenges the claimed gain.

## Start here

1. [Current abstract](abstract_submission_2026_10_31/Abstract.md) — the current submission proposal, covering all eight requested sections; 848 words including title and headings.
2. [Architecture](abstract_submission_2026_10_31/Architecture.md) — proposed data flow and separation of evaluation-only simulator truth.
3. [Submission strategy and judge questions](abstract_submission_2026_10_31/Selection_Strategy.md) — positioning, claim boundaries, and what has actually been tested.
4. [Revised research document](research_audit_2026_10_30/Problem_3_Off_Policy_Evaluation_Revised.md) — detailed foundations, methods, literature, assumptions, and limitations.
5. [Latest extension: technical note](likelihood_extension_2026_10_30/TECHNICAL_NOTE.md) and [measured results](likelihood_extension_2026_10_30/RESULTS.md) — the mathematical and experimental basis for the current proposal.

The [plain-text abstract](abstract_submission_2026_10_31/Abstract_plain.txt) is available for submission forms. The [supplied challenge PDF](Perceptron_Hackathon_by_optive_PS.pdf) is included for reference.

## Research status and evidence

This repository contains research documents, numerical prototypes, tests, and saved synthetic benchmarks. It is **not yet an integrated application**. The interface, adverse-model presentation, real-data integration, and sensitivity module described in the abstract are proposed work.

| Package | Purpose | Recorded evidence |
|---|---|---|
| [Research audit](research_audit_2026_10_30/README.md) | Corrected foundations and mathematical checks | 29 passing tests; finite-sample failures of ordinary Wald inference documented |
| [Earlier innovation investigation](innovation_research_2026_10_30/README.md) | Shared-region comparison and novelty falsification | 17 passing tests; 36,000 synthetic logs; candidate matched an established robust comparator |
| [Latest likelihood extension](likelihood_extension_2026_10_30/TECHNICAL_NOTE.md) | Joint likelihood region and policy-contrast optimization | 13 passing tests; 8,000 synthetic logs; primary comparison tied the strong KL-box baseline |
| [Submission materials](abstract_submission_2026_10_31/Abstract.md) | Current proposal and optional architecture | Eight sections; 848-word abstract |

**Do not claim a world-first algorithm or universal superiority.** In the latest prespecified primary comparison, split likelihood and KL boxes each certified beneficial changes in 498/500 trials. Secondary advantages are exploratory. Confidence statements require the declared identification and statistical assumptions; hidden-confounding stress tests deliberately demonstrate their failure outside those assumptions.

The current abstract is the source for the proposed project scope. Earlier research explains how that scope evolved; rejected novelty claims are retained as evidence, not current promises. The [original research manuscript](Problem_3_Off_Policy_Evaluation_Research.md) is preserved for provenance; use the revised manuscript for the audited account.

## Working with the code

Recorded environment: Python 3.12.14 and NumPy 2.3.5. The numerical prototypes need no GPU. From the repository root:

```sh
python -m pip install -r requirements.txt
python -X utf8 -m unittest discover -s innovation_research_2026_10_30/tests -v
```

Run the latest extension's tests from its directory:

```sh
cd likelihood_extension_2026_10_30
python -X utf8 -m unittest test_likelihood -v
```

Each package includes its experimental protocol, code, result summaries, raw CSVs, and provenance manifests. Consult package documentation before rerunning experiments: runners regenerate saved outputs and can take several minutes. The original audit and earlier innovation package have their own reproduction instructions. Historical logs may mention the original author's local paths; these are provenance, not required installation paths.

## Suggested team ownership

- Statistical methods, assumptions, and evaluation metrics.
- Synthetic data, estimator integration, and backend.
- Demo interface, architecture, and presentation.

These are proposed roles, not fixed assignments. Keep measured results separate from planned functionality when editing the abstract or presenting the project.
