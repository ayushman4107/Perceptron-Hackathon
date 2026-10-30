# Protocol: policy-ratio compression and predictive likelihood certificates

Written before inspecting policy-comparison outcomes. Date: 30 October 2026. This follows the earlier negative novelty results; it is a new experiment, not a replacement of their frozen primary endpoints.

## Hypothesis and extension

The original item-level joint region pays for many reward parameters that a particular policy comparison does not need. For a known, context-free logger mu, group actions with exactly equal signed ratios (pi(a)-mu(a))/mu(a). The policy gain equals a weighted sum of group reward means even when action reward means differ arbitrarily within a group. Under IID Bernoulli logged observations, group successes conditional on group counts are binomial. This permits applying the existing likelihood solver in a lower dimension without an equal-reward assumption.

The candidate method combines this exact policy-ratio compression with a validation likelihood numerator that is a fixed 50:50 mixture of (i) the pilot-posterior predictive Beta-binomial distribution and (ii) the Jeffreys predictive distribution. Its confidence region is an ordinary likelihood-ratio region with a proper, pilot-conditional predictive numerator. Finite-sample validity is inherited from established universal-inference arguments. There is no claim that grouping, likelihood inference, safe policy improvement, or posterior prediction was invented here.

For a pilot-selected top-k policy under uniform logging over A items, use exactly two groups: top-k and the remaining items. The gain is (1-k/A)*(q_top-q_rest). Uniform random is the reference logger. Candidate k values are {1,3,5,10,20}, omitting k>=A. Rank pilot items by (clicks+0.5)/(count+1); tie-break by item ID. Candidate policies and groups are frozen before certification or reference outcomes. Correct each group's region at alpha/M for M candidates, so selecting the greatest certified gain does not evade multiple-comparison control.

## Real-data design

Use full Open Bandit Dataset campaign members retrieved from the official ZOZO ZIP, not the 10,000-row examples. Storage-based scope chosen before policy outcomes: Random logs for all, men, women, plus BTS men. Primary campaign: all. Primary position: minimum numeric position (the first display slot), analyzed separately to avoid treating three items in one slate as independent. Other campaigns are replications, not a search for the largest gain. Record checksums, row counts, click rates, action support, propensity diagnostics, dates and units.

Randomly assign first-position rows with seed 731029 into 20% pilot, 40% certification, 40% reference, independently of rewards. Use timestamp-block assignment if timestamps identify shared display events, and document the exact implementation before inference. The primary IID inference remains conditional on the usual stationary independent-impression model; repeated users cannot be ruled out without identifiers. Add chronological train/certification/reference stress analysis and time-block bootstrap as diagnostics, not as a proof that the binomial guarantee holds under arbitrary dependence.

Hold the reference split aside from policy construction, certification, hyperparameters and method selection. Report its own uncertainty. Replay/group means on independent Random data supply an empirical reference for the selected policy gain, NOT exact real-world causal ground truth. True coverage, false certification and regret are measured in simulations. Do not report real-data coverage against a noisy reference as mathematical coverage.

## Baselines and ablations

At equal pilot/certification budgets compare: item-level joint split likelihood (original extension), item-level predictive-mixture likelihood, item-level Jeffreys-mixture likelihood, item-level KL-Chernoff box; grouped predictive mixture (candidate); grouped split likelihood; grouped Jeffreys mixture; grouped KL-Chernoff box; grouped exact Clopper-Pearson box; IPS and tabular cross-fitted DR with simultaneous asymptotic Wald intervals. The grouped exact and KL baselines receive the SAME grouping and policy-family correction as the candidate. An apparent improvement over only an item-level or Hoeffding baseline is not evidence of superiority over strong alternatives. Clipping and SNIPS are point-estimator diagnostics, not finite-sample confidence procedures.

Primary quantitative question: does compression reduce median interval width across the five policies versus the original item-level split region on the all campaign? A separate, stricter comparison asks whether predictive likelihood improves on grouped exact/KL baselines. Report every method and every policy, even if the simpler baseline wins. No predetermined numeric superiority claim is placed in the abstract.

For BTS men -> uniform Random, apply IPS, SNIPS, tabular cross-fitted DR on the first-position BTS log and compare to independent on-policy Random CTR. Known release propensities are used as supplied; their Monte Carlo approximation and near-zero support are reported. This benchmark is distinct from our Random-log learned-policy experiment and is not a proof that the new exact-ratio compression applies to arbitrary BTS probabilities.

## Synthetic testing

Independently test algebra against arbitrary heterogeneous reward tables and nonuniform loggers; invalid grouping must be rejected or carry an explicit bounded approximation error. Check likelihood e-value expectation by exact small-sample enumeration, including pilot-based selection. Verify empty groups, zero clicks, deterministic rewards, all-zero contrasts, monotonicity, primal/dual feasibility, and numerical solutions against an independent SciPy constrained optimizer.

Frozen simulation cases: A in {20,80}, n_total in {10000,50000}, 20% pilot/80% certification; reward designs null (all .004), heterogeneous (linearly spaced .001 to .009 with permuted item order), rare (linearly spaced .0001 to .002), and concentrated signal (first 10% at .015, rest .002). 500 independent replications per design = 8,000 logs; seed 831000 + 100000*case_index + repetition. Policy learning is repeated within each log. Every method receives the same counts and chosen policies. Report simultaneous coverage across the five selected candidates, family-wise false improvement, beneficial certification, selected true gain, median width, and paired method differences with Monte Carlo intervals. Diagnostic mismatched-logger and postselection tests deliberately violate assumptions and must be labeled as such.

## Figures and submission

Create figures from saved machine-readable outputs: real-data policy-gain intervals with independent reference; interval-width ablation; synthetic calibration/power; and, if informative, the BTS -> Random discrepancy. Keep units explicit (CTR percentage points or clicks per 10,000). Produce a 600-900-word abstract and a separate one-page approach/evidence sheet in the permitted architecture supplement. Results may change the preferred method and contribution claim. Raw datasets and dependency folders must not be pushed to GitHub.
