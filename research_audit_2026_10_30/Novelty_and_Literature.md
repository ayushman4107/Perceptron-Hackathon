# Novelty and literature audit

This is a targeted comparison, not an exhaustive novelty search. The existing file is a literature dossier plus project plan. It does not establish a new estimator, a formal safety result, or comparative effectiveness of a finished workbench. Later chat proposals are reviewed here without retroactively treating them as implemented manuscript contributions.

## Contribution-by-contribution assessment

| Proposed/claimed contribution | Closest established approach | Technical difference currently specified | Evidence for difference | Uncertainty | Recommended wording |
|---|---|---|---|---|---|
| IPS and DR evaluation | Dudík et al.; established weighting literature | None at estimator level | Formulas match standard methods | No original estimator demonstrated | Implement established estimators transparently |
| Confidence-aware evaluation | High-confidence OPE; anytime-valid inference | A planned diagnostic interface around conventional intervals | Executed tabular interval stress tests | Robust sparse/adaptive inference not implemented | Evaluate uncertainty calibration; abstain when evidence is inadequate |
| Gamma sensitivity | Kallus–Zhou; Dorn–Guo; conditional-moment bounds | Restricted binary-stratum calculation with explanatory interface | Algebra and endpoint tests | General policy-contrast and endpoint inference unresolved | Provide assumption-qualified binary sensitivity analysis |
| Claim audit | Causal estimand specification and OPE diagnostics | Combines before/after, same-period OPE, and assumptions in a report | Exact worked example and revised specification | User benefit and deployment impact untested | An auditable evaluation workflow |
| Evidence map | Subgroup effect/coverage diagnostics | Proposed visual presentation of predefined groups | No implemented UI or comparative test | Data-driven group search raises multiplicity | Report prespecified segment evidence and limitations |
| Policy revision/fallback | SPIBB; confounding-robust improvement | Contextual-bandit mixture alpha(x), selection rule not yet fixed | Distribution validity and counterexample only | No efficacy or safety theorem | Optional conservative heuristic, independently evaluated |
| Next-data recommendation | Safe optimal logging design; logging policy design for OPE | Planned ranking of information gaps | No implemented acquisition objective | Data efficiency compared with baselines untested | Proposed exploration-planning extension |
| Estimator selection | Adaptive estimator selection (2020); PAS-IF (2023) | Primary estimator predeclaration, not a new selector | Protocol only | No evidence of superior selection | Compare methods without selecting the most favorable value |
| Synthetic before/after reversal | Established confounding/drift counterexamples | A reproducible, pedagogical two-period example tied to this challenge | Exact arithmetic and audit simulations | External generalization not implied | Demonstrate a misleading before/after claim under controlled conditions |
| Integration of all components | Existing OPE and causal-analysis workflows | A specified combination of diagnostics, reporting, and failure handling | Dossier and audit code | New combination is not automatically research novelty | Engineering/application contribution pending full implementation |

## Closest primary sources rechecked

- **Dudík, Langford, Li (2011), Doubly Robust Policy Evaluation and Learning:** supports attribution of contextual-bandit DR. Its reported empirical improvement is not a universal variance-dominance theorem. [Paper](https://arxiv.org/abs/1103.4601).
- **Wang, Agarwal, Dudík (2017):** minimax OPE analysis and SWITCH; relevant stabilization baseline. [Proceedings](https://proceedings.mlr.press/v70/wang17a.html).
- **Su, Dimakopoulou, Krishnamurthy, Dudík (2020):** DR shrinkage and finite-sample MSE tradeoffs. [Proceedings](https://proceedings.mlr.press/v119/su20a.html).
- **Su, Srinath, Krishnamurthy (2020):** an earlier estimator-selection contribution missing from the dossier's short account. [Proceedings](https://proceedings.mlr.press/v119/su20d.html).
- **Udagawa et al. (2023), PAS-IF:** target-adaptive pseudo-policy tasks for estimator selection. [Paper](https://arxiv.org/abs/2211.13904).
- **Laroche, Trichelair, Tachet Des Combes (2019), SPIBB:** baseline bootstrapping in batch RL with assumptions and algorithm-specific guarantees. A context-dependent mixture does not inherit that theorem. [Proceedings](https://proceedings.mlr.press/v97/laroche19a.html).
- **Kallus and Zhou (2018):** worst-case regret against a baseline under confounding sensitivity. The dossier's single-arm bound is not this complete learning algorithm. [Paper](https://arxiv.org/abs/1805.08593).
- **Dorn and Guo:** sharp sensitivity identification and quantile balancing. Full-text conditions distinguish discrete identification from continuous-outcome inferential theory. [Full text](https://arxiv.org/html/2102.04543v3).
- **Ishikawa and He (2023):** conditional moment constraints tighten confounding-robust policy bounds under their conditions. [Proceedings](https://proceedings.mlr.press/v206/ishikawa23a.html).
- **Chernozhukov et al.:** orthogonal scores and cross-fitting for causal-parameter inference; conditions cannot be reduced to “one nuisance correct.” [Paper](https://arxiv.org/abs/1608.00060).
- **Waudby-Smith et al.:** adaptive, anytime-valid OPE inference is a dedicated procedure, not the dossier's ordinary Wald interval. [Paper](https://arxiv.org/abs/2210.10768).
- **Dann et al. (2023):** multiple-policy RL evaluation using shared on-policy samples. The original citation was overly broad as support for post-selection logged-data inference. [Proceedings](https://proceedings.mlr.press/v206/dann23a.html).
- **Zhu and Kveton (2022):** safe optimal logging design. Relevant comparison for any proposed next-data recommendation. [Proceedings](https://proceedings.mlr.press/v151/zhu22a.html).
- **Douglas, Persson, Provost (2026 preprint):** logging-policy design for OPE across information regimes. Abstract and metadata checked; theorem proofs not independently reproduced. [Paper](https://arxiv.org/abs/2605.15108).
- **Saito et al. (2021), OBD/OBP:** published campaign/action counts and ALL CTRs match the dossier. They remain empirical references, not exact population truths. [Full text](https://arxiv.org/html/2008.07146v5); [repository](https://github.com/st-tech/zr-obp).

The six frontier entries in Section 5.9 were re-opened at their primary metadata/abstract pages. Their broad topic summaries match those pages. Author-reported acceptance remains labeled author-reported; this audit does not certify proceedings status or independently verify recent theorem proofs. In particular, a July 2026 arXiv submission reporting ICLR 2025 acceptance is a metadata chronology requiring confirmation before relying on its publication status. The Guo–Xu page contains an arXiv notice of text overlap with another preprint; this is recorded as metadata, not a judgment on validity. No numerical frontier-paper performance claims were used to justify our method.

All 61 unique original source links are inventoried in `results/citation_ledger.csv`. Each is marked as rechecked during this audit or not independently rechecked during this audit. Prior conversation research is not silently counted as a new full-text examination. Bibliographic existence does not verify every theorem, experiment, or implementation.

## What would substantiate an actual research contribution?

Freeze one concrete decision/revision rule before comparison. Use a finite candidate policy set, an independent development split for alpha/threshold selection, and a final test split. Compare naive selection, IPS/DR point estimates, a properly specified lower-bound selection rule, and the proposed rule. If claiming a relation to SPIBB, either implement an applicable variant or clearly explain the contextual-bandit baseline adaptation rather than claiming identical theoretical guarantees.

Measure true value/regret, false-improvement rate only when the true contrast is nonpositive, missed benefits, abstention, selected-policy uncertainty, subgroup harms, and data requirements. Report both unconditional performance and performance conditional on making a decision. Always-abstain must be an explicit reference, so reduced harm is not achieved merely by refusing everything.

Use ablations: without uncertainty, without support diagnostics, without hidden-bias sensitivity, and without revision. Match data access, policy classes, tuning budget, and evaluation seeds. Include strong/weak support, rare rewards, misspecification, hidden U, and environment drift. A new diagnostic or selection objective should improve a prespecified metric over a relevant baseline while documenting tradeoffs. The present audit establishes none of those comparative novelty claims.

**Defensible current statement:** “We specify an auditable contextual-bandit policy evaluation workflow, independently verify its core identities, and demonstrate finite-sample failure modes of conventional uncertainty estimates. Policy revision and data-acquisition recommendations remain proposed extensions.”
