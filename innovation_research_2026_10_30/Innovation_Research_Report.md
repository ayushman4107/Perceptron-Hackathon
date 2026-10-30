# Innovation investigation: what survives scrutiny?

Date: 30 October 2026. This report distinguishes an implementable project capability from a new research method. Among the candidates examined, none yet satisfies all five innovation gates. The strongest practical candidate is comparison-specific partial-identification inference, but its proposed mechanism reduces to established shared-model robust optimization. A verification prototype tests that reduction; it is not promoted as a novel algorithm.

## What existed before this investigation

The workspace contained the original OPE dossier, the official challenge PDF, and the completed mathematical audit. The audit implements toy IPS/SNIPS/DR, cross-fitted tabular simulations, sensitivity formula checks and counterexamples. It does not contain an application, production data pipeline, learned revision algorithm, active acquisition system or UI. Existing files remain unchanged. The current directory supplies isolated research code and deliverables A–G; it does not pretend there was an application to integrate into.

The central question remains: what can logged outcomes justify about a different policy's value or improvement? The most consequential unresolved problems are finite-sample inference under sparse support, comparison after policy selection, and distinguishing uncertainty that more of the same logs can resolve from structural non-identification. The audit's poor Wald coverage supplies a failure motivation, not a new solution.

## Research strategy and gates

Searches followed failure modes across partial identification, confidence-set learning, robust improvement, orthogonal OPE, estimator selection, transportability, subgroup inference and acquisition design. Closest full texts were examined for actual objectives and assumptions, rather than relying only on titles. `Literature_Comparison.md` records sources and reading depth. This is targeted research, not proof of exhaustive novelty coverage.

The decision rule for this investigation is conjunctive: a high score cannot rescue a known method or invalid identification claim. Correctness, feasibility and utility are separate from originality. Numerical success against a weaker comparator cannot establish novelty when a strong comparator is algebraically equivalent.

## Finalist research card C1: comparison-specific confidence certificates

1. **Name:** shared-region policy contrast certificate (descriptive, not a new branded estimator).
2. **Failure:** separately bounding two policy values can count the same uncertain action twice, producing indecision even when the policies' difference is identified.
3. **Baseline weakness:** interval subtraction allows the same unknown reward mean to take incompatible values in the target and reference. A properly paired/robust method already avoids this.
4. **Closest approaches:** shared-model robust policy improvement; partial-identification LPs; paired DR; simultaneous confidence-region projection. See sources L1–L4, L7.
5. **Proposed difference:** use signed policy differences before optimizing the uncertainty set; expose a comparison-specific structural ambiguity width. Relative to separate value intervals this is a real computational distinction. Relative to a shared-region robust objective it is no distinction.
6. **Formulation:** c_sa=p_s(pi_sa-pi0_sa), L=min_{q in C}c'q, U=max_{q in C}c'q; choose positive certified improvement or retain the reference.
7. **Assumptions:** finite fixed cells, bounded IID outcomes, exchangeability within cells, known target masses, stable reward means, correctly declared logger support. Finite-horizon union-bound confidence region.
8. **Identification:** shared unknown coefficients cancel; missing nonzero coefficients cannot be recovered without restrictions. Outcome samples cannot certify absence of confounding.
9. **Implementation:** sufficient-statistic aggregation, Hoeffding cell box, signed endpoint sums, independent scalar objective and tiny exhaustive-vertex oracle. Implemented only as research verification.
10. **Experiment:** frozen nine-scenario design, sample-size and candidate-count sweeps, repeated paired decisions and negative stresses. Full protocol in `Experimental_Protocol.md`.
11. **Baselines:** exact shared-model robust objective, separate value intervals, paired cross-fitted DR/Wald, midpoint ablation, always-reference.
12. **Benefit expected:** fewer unnecessary refusals relative to independent-value bounds where shared uncertainty is large.
13. **Failures:** confounding, wrong target population, sparse cells, high-dimensional partitions; no shared structural cancellation when reference=logger.
14. **Falsifier:** no gain over the exact robust reference, or loss of the touted benefit in the actual logger-reference setup. The first is already implied by algebra.
15. **Novelty verdict:** reject as a new algorithm. Retain as a useful implementation option and transparent benchmark case. A new name or evidence display does not change that verdict.

**Falsifiable hypothesis:** Under IID finite-cell exchangeability and known target masses, when two off-logger policies share a poorly observed component, separate-value uncertainty can prevent decisions. Projecting a common confidence region onto the policy contrast should increase beneficial decisions relative to separate intervals, at the cost of conservative cellwise inference. It is hypothesized to offer no decision advantage over the equivalent shared-model robust objective. Both statements are tested; only the first would support practical implementation value.

An especially important scope correction: the illustrative reference is a second alternative policy, not the historical logger. If the challenge is strictly target versus logger, structural missing-action cancellation cannot be advertised as the central innovation. Statistical covariance cancellation still matters, and paired OPE already addresses it.

## Finalist research card C2: collect data for the decision, not each value

1. **Name:** contrast-focused augmentation design.
2. **Failure:** collecting data on actions where policies agree may reduce individual-value error without resolving their comparison.
3. **Baseline weakness:** uniform or target-only acquisition can waste budget on irrelevant components.
4. **Closest approaches:** MVAL, safe optimal design, best-arm identification with offline data, and linear contrast experimental design; see L5, L6, L10, L11.
5. **Proposed difference:** optimize contrast uncertainty instead of one policy's value. This is a standard change of estimand in design, not by itself a new design principle. Cost and safety constraints alone also do not establish novelty.
6. **Formulation:** for fixed context and oracle residual variance sigma_a^2, minimize sum_a d_a^2 sigma_a^2/nu_a subject to nu being a probability vector, plus any legitimate floors/cost constraints. Cauchy–Schwarz gives unconstrained nu_a proportional to |d_a|sigma_a when the numerator is nonzero. With all numerators zero every feasible design ties. Finite budgets and historical data change the effective denominators.
7. **Assumptions:** new randomized data can be collected; residual variances or justified estimates are available; stationarity and valid combined-log inference; any operational safety constraints must be explicitly supplied.
8. **Identification:** an outcome observed under a new randomized action can resolve that cell; collecting more of an unchanged zero-support log cannot. The unknown variance and mean cannot be treated as oracle inputs to a deployable recommender.
9. **Implementation plan:** fit variances on independent pilot data, solve a constrained convex allocation, collect simulated augmentation data, evaluate the combined estimator. Not built as a new contribution after the novelty gate.
10. **Experiment design:** compare equal total old/new budgets, costs and contexts; evaluate decision resolution and error rather than just individual-value MSE. Include high-variance estimation errors and reversed rankings.
11. **Baselines:** MVAL adapted to the same signed contrast, classical contrast allocation, uniform, target sampling, and acquisition-free reference.
12. **Expected benefit:** avoid irrelevant data acquisition compared with naive allocation.
13. **Failures:** incorrect pilot variances, unavailable action access, reward drift, hidden bias, safety feasibility, or the need to evaluate many different future contrasts.
14. **Falsifier:** equality with appropriately adapted design baselines, or no decision advantage after matching error and acquisition costs.
15. **Novelty uncertainty:** a constrained, multi-comparison design might still contain a research problem, but no distinct rule or advantage is established here. Broad next-data recommendation claims are rejected.

**Research hypothesis, unexecuted:** Under stationary randomized augmentation and independent variance estimates, a contrast-specific design improves comparison resolution over value-specific/uniform collection when policies share many actions, sacrificing information about other policy values. It must beat an adapted contrast-optimal baseline to justify methodological novelty. That hurdle is currently unmet; no acquisition performance is claimed.

## Candidate rubric

Scores are judgments, not measurements. Columns are 1–5. Weighted score = .25*N + .20*M + .20*E + .20*F + .10*R + .05*D.

| Candidate | Novelty N | Math M | Falsifiability E | Feasibility F | Relevance R | Demo D | Weighted /5 | Hard-gate result |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| C1 shared-region contrasts | 1 | 5 | 5 | 5 | 4 | 5 | 3.90 | Reject new-method claim: equivalent robust objective |
| C2 contrast-focused acquisition | 2 | 4 | 4 | 3 | 4 | 4 | 3.30 | Reject broad novelty; no distinct extension established |
| C3 selected subgroup harm certificates | 1 | 4 | 4 | 4 | 5 | 4 | 3.35 | Existing simultaneous inference/sample-splitting principles |
| C4 infer cause from IPS–DR disagreement | 1 | 2 | 3 | 4 | 5 | 3 | 2.70 | Cause not identified by disagreement alone |
| C5 drift/confounding robust policy frontier | 1 | 4 | 4 | 3 | 4 | 3 | 3.00 | Existing robust OPE/improvement; no precise new uncertainty model |

C3 would maximize a prespecified or independently learned subgroup contrast subject to simultaneous lower/upper bounds. Searching subgroups is not new; without honest discovery/inference separation it recreates selection bias. C4 is more problematic: the same observed law can be generated with or without an unmeasured confounder, so no statistic of the logs can always label the cause. Disagreement can flag instability but cannot distinguish all causes. C5 needs an uncertainty-set justification and a measurable difference from robust OPE, not extra sliders. These directions were rejected before implementation, not silently forgotten.

## What additional evidence could change the outcome?

A serious extension must start from a concrete restriction unmet by a strong comparator. One promising follow-up question is simultaneous comparison under data-dependent continuous partitions with sparse support, without paying the full cell-count penalty. That requires an actual inference construction, complexity control and a comparison to existing uniform/orthogonal inference; it is not solved by the box prototype. Another is cost-constrained decision resolution with unknown variances and multiple relevant contrasts, where an adapted MVAL or best-identification method is the baseline. Neither is asserted to be novel merely because it is not implemented here.

For the hackathon, the defensible immediate choice is an evidence-focused OPE application that explicitly credits paired and robust inference, demonstrates where confidence fails, and reports unresolved identification. For a research-novelty pitch, the current evidence is insufficient. This negative outcome prevents a stronger but false claim; it does not prove that the field contains no available innovation.
