# Beyond Apparent Lift: Counterfactual Policy Evaluation with Decision Certificates

## Problem and theme chosen

We address **Problem 3: “Did the Policy Actually Work, or Did It Just Look Like It Did?”**, under **Theme 2: Cause and Effect in AI Decisions**. Recommendation and allocation systems influence which outcomes become observable, making apparent improvement an unreliable guide to deployment. Our team is interested in turning this statistical difficulty into a practical tool that can challenge a policy-change claim before it is acted upon.

## Understanding of the challenge

A higher average reward after a policy change can reflect a different user population rather than a better policy. In our motivating synthetic example, average reward rises from 0.32 to 0.58, although switching policies reduces expected reward by 0.10 on the same population. Historical logs reveal only the outcome of the selected action. Importance weighting can correct observed assignment bias under appropriate assumptions, but rare actions create unstable estimates, absent actions create non-identification, and choosing the most promising policy after inspecting many estimates introduces selection bias. These are distinct problems that an attractive point estimate cannot resolve.

## Proposed approach

We propose a **counterexample-driven evaluation system** whose central question is: *Could a reward model still compatible with the stated evidence overturn this claimed improvement?*

The pipeline will ingest contexts, actions, rewards and logging propensities; validate probability and action-support assumptions; and evaluate target policies against the logger on a common target population. We will implement IPS, self-normalized IPS and cross-fitted doubly robust estimation using Python, NumPy and scikit-learn. A controlled contextual-bandit simulator will expose ground-truth policy values only to the benchmark evaluator.

Our focused extension is a decision-certificate engine for **prespecified finite contexts and binary rewards**, evaluated on a declared target context distribution. It will construct a joint confidence region over conditional reward means using established split likelihood-ratio inference, then minimize and maximize the target-minus-logger value over that region. A specialized convex solver will produce both bounds and the reward tables attaining, or numerically approaching, them. The output will distinguish supported improvement, supported deterioration and insufficient evidence. For an unresolved claim, the interface will display a concrete adverse reward table and identify which unobserved or weakly observed cells permit it. Such a table is a statistical counterexample under stated assumptions, not a discovered hidden confounder.

## Minimum viable scope

The prototype will satisfy both minimum requirements: apply standard IPS and doubly robust OPE, and reproduce a concrete reversal between naive before/after improvement and the same-population counterfactual effect. A reproducible demonstration will show the log, competing estimates, uncertainty, and simulator truth. The baseline pipeline will remain usable independently of the certificate extension, ensuring that the minimum submission does not depend on an ambitious research component succeeding.

## Stretch ambitions

We will quantify uncertainty and test its empirical coverage, especially with rare rewards and weak overlap. We will also implement a basic marginal-odds sensitivity analysis for unobserved confounding, reporting how policy conclusions change as the sensitivity parameter increases. Sensitivity ranges will be distinguished from sampling confidence intervals. If time permits, we will add an Open Bandit Dataset replication using its documented evaluation protocol and empirical reference values, without treating unobserved action outcomes as available ground truth.

## Novelty and differentiation

Our differentiation is **auditable evidence for a policy decision**: a comparative uncertainty bound accompanied by an explicit adverse model when improvement cannot be established. The joint region preserves dependencies across comparisons and supports policy selection within the fixed tabular model, rather than attaching an uncorrected interval to a winner selected from many estimates. We will build on robust optimization and likelihood inference, with the technical contribution evaluated as a concrete application extension. We will not claim that IPS, DR or confidence-region projection are newly invented algorithms, or that more data can repair structural missing support without additional assumptions.

## Evaluation plan

We will benchmark against naive comparisons, IPS, SNIPS, cross-fitted DR with conventional intervals, cellwise Hoeffding and KL bounds, and a full-data mixture-likelihood alternative. Controlled experiments will vary sample size, action overlap, reward rarity, context heterogeneity and candidate-policy count; separate stress tests will violate exchangeability or introduce population shift. Policies and evaluation seeds will be fixed before final comparisons. Metrics will include value-estimation error, simultaneous coverage, false-improvement decisions, beneficial decisions, regret, interval width and runtime, with Monte Carlo uncertainty. The extension must improve decision usefulness against a strong finite-sample baseline; improvement over Hoeffding alone will not establish superiority. Negative findings and undefined estimates will remain visible.

## Feasibility and risks

Our three-member team has Python/ML, statistics, backend and frontend experience, including substantial software projects. We will divide responsibility across statistical evaluation, data/backend engineering and an interactive Streamlit demonstration, with shared testing. Initial numerical prototypes and synthetic benchmarks are available; the integrated interface and sensitivity workflow remain planned. The core is CPU-based and requires no large-model training. Principal risks are overly conservative bounds, insufficient context adjustment, unsupported actions and invalid transport assumptions. We will control scope through fixed synthetic strata, independent benchmark truth, explicit assumptions, numerical solver checks and a staged baseline-first build. The intended outcome is a reproducible answer to when a policy claim is supported—and a concrete explanation when it is not.
