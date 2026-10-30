# Executed verification report

Audit date: 30 October 2026. The executable source is `verification/verify.py`; full test names/statuses appear in `results/test_log.txt`. Runtime versions, script SHA-256, seed ranges, timings, summary metrics and unexecuted work are recorded in `results/verification_results.json`. Per-trial estimates/intervals are in `results/monte_carlo_raw.csv`.

## What actually ran

29 unittest tests passed, with zero failures and zero errors. Checks cover exact rational toy arithmetic; the fixed-nuisance DR bias identity over 243 rational configurations; independent scalar versus vectorized estimators; target-equals-logger and zero-outcome-model limits; variance counterexamples; sample-size/shape/probability validation; structural versus empirical support; ESS boundaries and scaling; binary sensitivity endpoints against independent LP vertex enumeration on 400 random cases; sensitivity domains/monotonicity/attainability; latent confounding; cross-fit exclusion; paired covariance; SNIPS delta-method gradient by finite differences; clipping and shrinkage boundaries; unsafe mixtures; unsupported indistinguishable worlds; and numerical integration of the original illustrative generator.

Exact rational enumeration is not a general symbolic proof. Independent written derivations in Appendix A provide the general small identities; SymPy/CAS was unavailable and not run. Numerical integration and finite-difference checks have numerical tolerance and are not formal proofs.

The final rerun used 1,000 independent datasets per primary scenario, n=2,000 each, with five-fold tabular cross-fitting. Seeds, nuisance smoothing and potential-outcome generation are specified in code and Appendix A. An additional 1,000 independent batches evaluate four fixed-nuisance regimes and a hidden-U experiment. The estimator only sees observed context/action/reward/propensities; oracle DR and hidden full-propensity comparisons are explicitly evaluator-only.

| Scenario | Cross-fitted DR nominal 95% coverage | MC standard error | Interpretation |
|---|---:|---:|---|
| Regular | 93.8% | 0.76 percentage points | Finite-sample evidence, not exact nominal coverage |
| Weak overlap, q1=0.5 | 98.1% | 0.43 percentage points | Truth matches the model's empty-cell prior; highly special |
| Weak overlap, q1=0.7 | 63.9% | 1.52 percentage points | Strong undercoverage when truth differs from prior |
| Rare rewards | 90.6% | 0.92 percentage points | Wald approximation is unreliable in this regime |

In weak-overlap runs SNIPS was undefined in 360/1,000 and 349/1,000 trials respectively because no target actions were observed. The JSON reports both coverage conditional on an interval being defined and successful coverage across all attempts. Undefined trials are not silently dropped. Normal intervals are untruncated and use critical value 1.96. DR can legitimately return values outside the reward range; clipping such estimates would change the procedure.

The fixed-nuisance population limits are 0.4 when either nuisance is correct and 0.6 when both specified nuisances are wrong, versus true value 0.4. Hidden-U nominal IPS tends to 0.82 versus true value 0.5; using the full latent design propensity targets 0.5. Measured means and Monte Carlo standard errors are in the revised manuscript and JSON.

## Integrity and limits

An initial three-scenario run is preserved as `results/first_run_results.json`. The audit then added the off-prior weak-overlap case and fixed-nuisance experiments rather than replacing the favorable weak-overlap scenario. The final rerun also separates positive-decision rate from false-improvement rate: the latter is only defined for scenarios with nonpositive true contrast. Identical random seeds preserve the original three scenarios.

The sampling unit is an independent synthetic row; these experiments do not establish clustered-user or adaptive-logging inference. They do not benchmark a finished hackathon product, measure real-world deployment value, compare learned policy revision, or validate a confidence procedure for sensitivity endpoints. The simulated uncertainty failures are substantive findings, not failed software assertions. No coverage thresholds were changed to make tests pass.

The Markdown build uses stable identifiers for all 28 original displayed equations and appends independently derived assumptions, counterexamples and measured results. Structural validation checks paired math delimiters/fences, no control-character corruption, complete artifact presence, original SHA-256 preservation, and the result script hash. This is source validation, not a rendered LaTeX/Word publication build.
