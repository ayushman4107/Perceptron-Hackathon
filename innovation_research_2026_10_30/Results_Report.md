# Executed results and novelty decision

The frozen protocol generated **36,000 independent logs**, nine scenarios × two sample sizes × two candidate-family sizes × 1,000 repetitions. All **17 automated tests passed** with 0 failures and 0 errors. Main experiment runtime was 83.12 seconds in this environment; this excludes subsequent report generation and timing sweeps.

## Primary result

For shared_blind, n=3,000 and two policies, the following are measured beneficial-deployment rates. Brackets are 95% Wilson Monte Carlo intervals, not policy-value confidence intervals.

| Method | Beneficial deployment | False improvement | Mean primary interval width |
|---|---:|---:|---:|
| joint_contrast | 100.0% [99.62, 100.00] | 0.0% [0.00, 0.38] | 0.14512 |
| robust_reference | 100.0% [99.62, 100.00] | 0.0% [0.00, 0.38] | 0.14512 |
| separate_values | 0.0% [0.00, 0.38] | 0.0% [0.00, 0.38] | 0.94512 |
| paired_DR_Wald | 100.0% [99.62, 100.00] | 0.0% [0.00, 0.38] | 0.03891 |
| retain_reference | 0.0% [0.00, 0.38] | 0.0% [0.00, 0.38] | undefined |

The paired improvement versus separate intervals was 100.0 percentage points. Its preregistered-within-this-workspace normal Monte Carlo interval is degenerate because every paired trial had the same result (MCSE=0.000); this does **not** mean zero uncertainty about future trials. A supplemental distribution-free Hoeffding interval for a paired difference in [-1,1] is [0.9141, 1.0000]. This boundary check was added for reporting, not used to tune the method or choose the scenario.

H1's practical threshold is met. H2's novelty gate fails: the maximum endpoint discrepancy from the exact shared-model robust reference across all experiments was **0**. The algebra proves equality beyond these simulations. Paired DR also resolved every primary trial, with substantially narrower intervals. Thus neither a new algorithm nor superiority to a strong OPE comparator is demonstrated.

## Negative and adversarial results

All rows below use n=3,000, two policies and 1,000 repetitions. Family coverage means coverage of all candidate contrasts in that run; with two policies only one contrast is nontrivial. It is unavailable when a required contrast interval is undefined.

| Scenario | Method | Beneficial deployment | False improvement | Family coverage |
|---|---|---:|---:|---:|
| logger_reference | joint_contrast | 0.0% [0.00, 0.38] | 0.0% [0.00, 0.38] | 100.0% |
| logger_reference | paired_DR_Wald | 0.0% [0.00, 0.38] | 0.0% [0.00, 0.38] | undefined |
| weak_overlap | joint_contrast | 0.0% [0.00, 0.38] | 0.0% [0.00, 0.38] | 100.0% |
| weak_overlap | paired_DR_Wald | 45.5% [42.44, 48.60] | 0.0% [0.00, 0.38] | 72.8% |
| rare_rewards | joint_contrast | 0.0% [0.00, 0.38] | 0.0% [0.00, 0.38] | 100.0% |
| rare_rewards | paired_DR_Wald | 32.6% [29.77, 35.57] | 0.0% [0.00, 0.38] | 93.9% |
| null | joint_contrast | 0.0% [0.00, 0.38] | 0.0% [0.00, 0.38] | 100.0% |
| null | paired_DR_Wald | 0.0% [0.00, 0.38] | 2.8% [1.94, 4.02] | 95.5% |
| heterogeneous | joint_contrast | 0.0% [0.00, 0.38] | 0.0% [0.00, 0.38] | 100.0% |
| heterogeneous | paired_DR_Wald | 74.4% [71.61, 77.01] | 0.0% [0.00, 0.38] | 94.6% |
| hidden_confounding | joint_contrast | 0.0% [0.00, 0.38] | 100.0% [99.62, 100.00] | 0.0% |
| hidden_confounding | paired_DR_Wald | 0.0% [0.00, 0.38] | 100.0% [99.62, 100.00] | 0.0% |
| unmodeled_shift | joint_contrast | 0.0% [0.00, 0.38] | 100.0% [99.62, 100.00] | 0.0% |
| unmodeled_shift | paired_DR_Wald | 0.0% [0.00, 0.38] | 100.0% [99.62, 100.00] | 0.0% |

The box method makes no beneficial deployments in the listed weak-overlap and rare-reward two-policy settings. Its low error there reflects conservatism and missed benefits. In the logger-reference case, structural ambiguity persists; DR correctly declines the unsupported contrast. A midpoint extrapolation happens to select a beneficial policy in that world, but the indistinguishable-world unit test shows why this cannot be a reliable causal conclusion.

Hidden confounding and unmodeled shift deliberately violate the theorem assumptions. Both the box method and paired DR can then make harmful decisions with high confidence. These results are failures of applicability, not evidence that the conditional confidence-region proof is false. A declared sensitivity set or correct transport model is additional methodology, not a property of this prototype.

## Selection and ablations

The following null scenario highlights selection; harm is zero by construction, so false improvement is the relevant metric. A selected zero-effect policy counts as a false improvement.

| n | Policies | Joint false improvement | DR/Wald false improvement | Midpoint false improvement |
|---:|---:|---:|---:|---:|
| 300 | 2 | 0.0% [0.00, 0.38] | 2.8% [1.94, 4.02] | 50.2% [47.11, 53.29] |
| 300 | 32 | 0.0% [0.00, 0.38] | 7.4% [5.94, 9.19] | 76.1% [73.36, 78.64] |
| 3000 | 2 | 0.0% [0.00, 0.38] | 2.8% [1.94, 4.02] | 48.1% [45.02, 51.20] |
| 3000 | 32 | 0.0% [0.00, 0.38] | 6.7% [5.31, 8.42] | 73.0% [70.16, 75.66] |

The comparison to separate values removes cancellation; midpoint removes uncertainty; always-reference removes all deployment. The exact robust reference tests whether there is any new mechanism. No variance-adaptive box, pilot confidence-allocation scheme or sensitivity-adjusted prototype was tuned after observing these results. The DR model is two-fold tabular smoothing; general model-class misspecification experiments remain unrun.

## Runtime and reproducibility

| Cells S | Policies M | Projection median (ms), five repeats |
|---:|---:|---:|
| 2 | 2 | 0.112 |
| 2 | 32 | 1.722 |
| 2 | 128 | 6.956 |
| 100 | 2 | 0.117 |
| 100 | 32 | 1.828 |
| 100 | 128 | 7.309 |
| 1000 | 2 | 0.165 |
| 1000 | 32 | 2.647 |
| 1000 | 128 | 10.638 |

Aggregating 100,000 logged rows took a median 0.422 ms over five repeats. These are local descriptive timings, not hardware-independent speed claims. Full summaries (all 216 scenario/method combinations), policy tables, raw 216,000 trial-method records, script hashes, protocol hash, and test statuses are under `results/`.

## Decision

No assessed candidate is promoted as a validated technical innovation. C1 is a sound, reproducible implementation of an established principle with a useful demonstration. C2 remains a research question without a differentiating acquisition algorithm or executed benchmark. The negative novelty finding is part of the requested result, not a missing positive claim. OBD replication and full comparisons to general published algorithms are unexecuted.
