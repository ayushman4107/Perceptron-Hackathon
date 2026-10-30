# Likelihood extension: measured results

Executed 8,000 independent simulated logs (sufficient statistics), 500 trials in each of 16 settings, with six comparison methods. All 13 tests passed. Runtime: 488.6 seconds on the local CPU environment. The first unit-test run exposed integer dtype handling in a scalar optimizer input; it was fixed before the benchmark. No experiment was tuned after observing its outputs.

**Primary gate failed.** Split likelihood and KL boxes each certified a beneficial change in 498/500 primary trials. The paired difference was 0.00 percentage points, 95% Monte Carlo interval [-0.555, 0.555]. The advertised >=10-point superiority target was not met. This is not a universal new algorithm; it is a tested specialization of established likelihood inference.

## Complete results

Benefits/false improvements are percentages of trials; confidence brackets are Wilson 95% intervals for Monte Carlo rates. Coverage is simultaneous over all 32 candidate contrasts. Undefined candidate intervals make whole-family coverage unavailable; do not drop them silently.

| Scenario | n | Method | Beneficial decision % [95% MC] | False improvement % | Family coverage % | Mean primary width |
|---|---:|---|---:|---:|---:|---:|
| rare | 6000 | split_LR | 10.6 [8.2, 13.6] | 0.0 | 100.0 | 0.09628 |
| rare | 6000 | mixture_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.12973 |
| rare | 6000 | KL_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.13321 |
| rare | 6000 | Hoeffding_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.27010 |
| rare | 6000 | Wald_Bonferroni | 47.0 [42.7, 51.4] | 0.0 | 84.6 | 0.03224 |
| rare | 6000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| rare | 60000 | split_LR | 99.6 [98.6, 99.9] | 0.0 | 100.0 | 0.02858 |
| rare | 60000 | mixture_LR | 100.0 [99.2, 100.0] | 0.0 | 100.0 | 0.03935 |
| rare | 60000 | KL_box | 99.6 [98.6, 99.9] | 0.0 | 100.0 | 0.03706 |
| rare | 60000 | Hoeffding_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.09864 |
| rare | 60000 | Wald_Bonferroni | 100.0 [99.2, 100.0] | 0.0 | 96.8 | 0.01032 |
| rare | 60000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| regular | 6000 | split_LR | 85.8 [82.5, 88.6] | 0.0 | 100.0 | 0.31359 |
| regular | 6000 | mixture_LR | 71.0 [66.9, 74.8] | 0.0 | 100.0 | 0.36071 |
| regular | 6000 | KL_box | 11.8 [9.3, 14.9] | 0.0 | 100.0 | 0.44976 |
| regular | 6000 | Hoeffding_box | 0.6 [0.2, 1.7] | 0.0 | 100.0 | 0.50053 |
| regular | 6000 | Wald_Bonferroni | 100.0 [99.2, 100.0] | 0.0 | 98.2 | 0.11774 |
| regular | 6000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| regular | 60000 | split_LR | 100.0 [99.2, 100.0] | 0.0 | 100.0 | 0.10223 |
| regular | 60000 | mixture_LR | 100.0 [99.2, 100.0] | 0.0 | 100.0 | 0.13731 |
| regular | 60000 | KL_box | 100.0 [99.2, 100.0] | 0.0 | 100.0 | 0.14676 |
| regular | 60000 | Hoeffding_box | 100.0 [99.2, 100.0] | 0.0 | 100.0 | 0.15758 |
| regular | 60000 | Wald_Bonferroni | 100.0 [99.2, 100.0] | 0.0 | 98.8 | 0.03721 |
| regular | 60000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| null_rare | 6000 | split_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.08789 |
| null_rare | 6000 | mixture_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.11805 |
| null_rare | 6000 | KL_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.12518 |
| null_rare | 6000 | Hoeffding_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.26824 |
| null_rare | 6000 | Wald_Bonferroni | 0.0 [0.0, 0.8] | 0.0 | 80.2 | 0.02386 |
| null_rare | 6000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| null_rare | 60000 | split_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.02260 |
| null_rare | 60000 | mixture_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.03126 |
| null_rare | 60000 | KL_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.03209 |
| null_rare | 60000 | Hoeffding_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.09683 |
| null_rare | 60000 | Wald_Bonferroni | 0.0 [0.0, 0.8] | 0.2 | 97.8 | 0.00769 |
| null_rare | 60000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| heterogeneous | 6000 | split_LR | 2.0 [1.1, 3.6] | 0.0 | 100.0 | 0.20707 |
| heterogeneous | 6000 | mixture_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.24445 |
| heterogeneous | 6000 | KL_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.28983 |
| heterogeneous | 6000 | Hoeffding_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.41230 |
| heterogeneous | 6000 | Wald_Bonferroni | 91.8 [89.1, 93.9] | 0.0 | 98.0 | 0.07791 |
| heterogeneous | 6000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| heterogeneous | 60000 | split_LR | 99.8 [98.9, 100.0] | 0.0 | 100.0 | 0.06781 |
| heterogeneous | 60000 | mixture_LR | 100.0 [99.2, 100.0] | 0.0 | 100.0 | 0.09117 |
| heterogeneous | 60000 | KL_box | 100.0 [99.2, 100.0] | 0.0 | 100.0 | 0.09120 |
| heterogeneous | 60000 | Hoeffding_box | 93.6 [91.1, 95.4] | 0.0 | 100.0 | 0.13693 |
| heterogeneous | 60000 | Wald_Bonferroni | 100.0 [99.2, 100.0] | 0.0 | 99.0 | 0.02468 |
| heterogeneous | 60000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| weak_overlap | 6000 | split_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 1.02529 |
| weak_overlap | 6000 | mixture_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 1.04361 |
| weak_overlap | 6000 | KL_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 1.07001 |
| weak_overlap | 6000 | Hoeffding_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 1.13001 |
| weak_overlap | 6000 | Wald_Bonferroni | 0.6 [0.2, 1.7] | 0.0 | 25.0 | 0.23402 |
| weak_overlap | 6000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| weak_overlap | 60000 | split_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.70396 |
| weak_overlap | 60000 | mixture_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.79886 |
| weak_overlap | 60000 | KL_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.80305 |
| weak_overlap | 60000 | Hoeffding_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.88313 |
| weak_overlap | 60000 | Wald_Bonferroni | 18.2 [15.1, 21.8] | 0.0 | 78.4 | 0.30783 |
| weak_overlap | 60000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| many_strata | 6000 | split_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.19591 |
| many_strata | 6000 | mixture_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.29550 |
| many_strata | 6000 | KL_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.40265 |
| many_strata | 6000 | Hoeffding_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.57809 |
| many_strata | 6000 | Wald_Bonferroni | 47.8 [43.5, 52.2] | 0.0 | 80.2 | 0.03190 |
| many_strata | 6000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| many_strata | 60000 | split_LR | 48.2 [43.9, 52.6] | 0.0 | 100.0 | 0.05614 |
| many_strata | 60000 | mixture_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.07574 |
| many_strata | 60000 | KL_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.08632 |
| many_strata | 60000 | Hoeffding_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 0.19358 |
| many_strata | 60000 | Wald_Bonferroni | 100.0 [99.2, 100.0] | 0.0 | 96.2 | 0.01028 |
| many_strata | 60000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| no_overlap | 6000 | split_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 1.00762 |
| no_overlap | 6000 | mixture_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 1.01045 |
| no_overlap | 6000 | KL_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 1.01386 |
| no_overlap | 6000 | Hoeffding_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 1.06761 |
| no_overlap | 6000 | Wald_Bonferroni | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| no_overlap | 6000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| no_overlap | 60000 | split_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 1.00241 |
| no_overlap | 60000 | mixture_LR | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 1.00335 |
| no_overlap | 60000 | KL_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 1.00377 |
| no_overlap | 60000 | Hoeffding_box | 0.0 [0.0, 0.8] | 0.0 | 100.0 | 1.02276 |
| no_overlap | 60000 | Wald_Bonferroni | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| no_overlap | 60000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| hidden_confounding | 6000 | split_LR | 0.0 [0.0, 0.8] | 100.0 | 0.0 | 0.09880 |
| hidden_confounding | 6000 | mixture_LR | 0.0 [0.0, 0.8] | 100.0 | 0.0 | 0.11801 |
| hidden_confounding | 6000 | KL_box | 0.0 [0.0, 0.8] | 100.0 | 0.0 | 0.16091 |
| hidden_confounding | 6000 | Hoeffding_box | 0.0 [0.0, 0.8] | 100.0 | 0.0 | 0.18581 |
| hidden_confounding | 6000 | Wald_Bonferroni | 0.0 [0.0, 0.8] | 100.0 | 0.0 | 0.03583 |
| hidden_confounding | 6000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |
| hidden_confounding | 60000 | split_LR | 0.0 [0.0, 0.8] | 100.0 | 0.0 | 0.03096 |
| hidden_confounding | 60000 | mixture_LR | 0.0 [0.0, 0.8] | 100.0 | 0.0 | 0.04327 |
| hidden_confounding | 60000 | KL_box | 0.0 [0.0, 0.8] | 100.0 | 0.0 | 0.05128 |
| hidden_confounding | 60000 | Hoeffding_box | 0.0 [0.0, 0.8] | 100.0 | 0.0 | 0.05871 |
| hidden_confounding | 60000 | Wald_Bonferroni | 0.0 [0.0, 0.8] | 100.0 | 0.0 | 0.01134 |
| hidden_confounding | 60000 | retain_logger | 0.0 [0.0, 0.8] | 0.0 | undefined | undefined |

## Interpretation

Some secondary scenarios favor split likelihood over the finite-sample KL box. These are exploratory results and do not replace the primary outcome. Wald often has higher decision power but can substantially undercover in sparse designs, even with a policy-count correction. Finite-sample methods can remain very conservative under weak overlap or many strata. All causal methods here fail when hidden confounding violates exchangeability. No method resolves unsupported causal outcomes without additional restrictions.

The hidden-confounding experiment is outside the causal theorem assumptions; its wrong decisions do not falsify the conditional observed-mean likelihood calculation. The simulator uses known context weights and binary rewards. No OBD experiment, general empirical-likelihood OPE implementation, adaptive logger, unknown-population inference or finished interface was evaluated.

## Reproduction

Python 3.12.14 and NumPy 2.3.5 were used. From this directory run `python -X utf8 experiment.py`, then `python -X utf8 write_report.py`. `test_likelihood.py` can run separately. `results/manifest.json` records the pre-run protocol and source hashes; `results/trials.csv` contains all 48,000 method/trial records. Original research files are untouched. This folder supports the abstract; the abstract promises the integrated report and adverse-model presentation as future work.
