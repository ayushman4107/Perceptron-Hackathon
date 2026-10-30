# Mathematical and scientific audit

Audit date: 30 October 2026. Main source: `original_snapshot.md`, byte-identical to the workspace manuscript when the audit started. Original locations below use section numbers and displayed-equation order M01–M28; revised equations carry those labels. The main source is a research dossier and planned workbench, not a manuscript containing a new theorem or completed product evaluation.

## Overall verdict

No critical algebraic defect was found in the central IPS, DR, toy-example, or binary sensitivity formulas under their proper domains and assumptions. This does not certify all real-world uses or every cited theorem. The most consequential issues are underspecified inference conditions, boundary handling, incomplete experimental specifications, and unsupported transfer of literature guarantees. The revision retains correct formulas and supplies independent derivations instead of inventing a new algorithm.

There are 11 major findings (M01–M04, M06–M09, M11–M13), four minor findings (M05, M10, N01–N02), and four editorial/scope findings (N03, E01, S01–S02). L01 is a minor literature-completeness finding. Severity counts describe the original dossier and its interpretation, not hypothetical errors already corrected in its Section 10. No claim that the old pasted pipeline's invalid Gamma method remains in the main dossier is made.

## Argument and dependency map

Historical log + fixed policy + specified population -> consistency/exchangeability/support -> identification -> IPS expectation -> DR bias-product identity -> nuisance estimation conditions -> interval approximation -> paired decision rule. Sensitivity is a separate branch: latent exchangeability + odds restriction + normalization -> feasible set -> population endpoints -> additional, currently unresolved endpoint inference. Temporal attribution requires an additional environment model. Policy revision requires policy selection followed by independent evaluation. Novelty requires comparisons to established methods, not merely valid mathematics.

Scope inventory: the workspace initially contained one Markdown dossier and one challenge PDF; no model code, LaTeX source, Word file, dataset, saved experiment, theorem appendix, or implemented revision algorithm was present. `initial_manifest.json` records names, sizes, and the original hash. The PDF's relevant pages were text-extracted and visually inspected. It supports the stated Problem 3 requirements. The dossier's extensive earlier-attachment audit is historical background, not a new experiment.

## Findings and changes

### M01 — Major: sampling and moment conditions were insufficiently explicit

- **Location/original:** Sections 3.2, 4.2, 7.2; “independent observations and a fixed environment”; M10 and M16.
- **Issue:** independence does not imply identical distribution or finite second moments. Pointwise positive action support can coexist with infinite IPS variance.
- **Independent counterexample:** X uniform (0,1), mu1=X, pi1=1, R1=1. E[IPS row]=1, E[row²]=integral 1/x=infinity. This satisfies the manuscript's basic causal identification and pointwise support assumptions; it does not satisfy finite-variance inference assumptions.
- **Correction/action:** Appendix A separates A1 identification from A2 variance and gives a convenient bounded-overlap sufficient condition. The body now explicitly says IID where that formula is used.
- **Status:** analytically established; exact finite-state variance decomposition also tested. General dependent-data inference remains outside the implementation.

### M02 — Major: calibration was characterized as necessary evidence

- **Location/original:** Section 4.1, “Predictive calibration under the logging distribution is necessary evidence”.
- **Issue:** a poorly calibrated reward model does not invalidate IPS, or DR with exact propensities and honest nuisance fitting. Calibration is a diagnostic, not a necessary mathematical condition for these estimators.
- **Derivation:** M13 is zero when b=mu for arbitrary integrable h. Thus even h=1 with zero rewards leaves DR unbiased, although variance can be bad.
- **Correction/action:** replace “necessary” with “useful diagnostic”; explicitly distinguish reward prediction from weighting validity.
- **Status:** established by bias identity and `test_dr_need_not_reduce_variance`.

### M03 — Major: finite-sample conditional identity versus nuisance limits

- **Location/original:** Section 4.4 describes M13 using nuisance “probability and reward limits”.
- **Issue:** the algebra is exact for fixed nuisances, or conditional on independent training. A probability-limit interpretation also needs convergence/integrability control. It cannot be inferred solely by substituting limits inside expectations.
- **Derivation:** A2 subtracts sum pi q before taking limits, producing M13. Cross-fitted scores share training data across folds; their exact joint independence is not implied.
- **Correction/action:** use fixed-function conditional bias as the primary statement; specify additional requirements for asymptotic claims.
- **Status:** independent algebra and exact rational-grid checks. General convergence results are conditional theory, not established for arbitrary user-selected models.

### M04 — Major: DR consistency is weaker than the displayed inference claim

- **Location/original:** Sections 4.5 and 7.2 mention nuisance rates but do not specify a usable sufficient regime; M16.
- **Issue:** correct limit of one nuisance does not establish root-n asymptotic linearity or make nuisance uncertainty negligible.
- **Counterexample:** true mu1=1/4, working b1=1/2, q1=1/2, h_n=q1+n^(-1/4). Bias is n^(-1/4)/2 despite consistency. It dominates the proposed root-n scale.
- **Correction/action:** Appendix A.3 states fixed-fold cross-fitting, bounded probabilities/rewards, L2 conditions, a product rate, and nondegenerate variance; explicitly defines sample SD and n>=2.
- **Status:** analytic counterexample and measured interval stress tests. This audit does not claim a universal valid alternative interval for all sparse cases.

### M05 — Minor: unqualified clipping/stabilization wording

- **Location/original:** Section 4.6, “This limits variance but introduces bias.”
- **Issue:** the sign and precision claims require reward/cap conditions; adaptive tuning adds selection issues. Clipping the weight does not bound the score when rewards are unbounded.
- **Derivation:** clipped bias equals −E[(w−c)+ R], nonpositive only for nonnegative R. DR residuals can have either sign.
- **Correction/action:** specify fixed nonnegative cap and distinguish bias–variance tradeoff from universal improvement.
- **Status:** analytic and exact numerical direction check; no arbitrary-reward stabilization guarantee asserted.

### M06 — Major: simulation called proof

- **Location/original:** Section 6.1, “primary proof of correctness”.
- **Issue:** a finite simulator benchmark cannot prove an estimator theorem or validity for real deployment.
- **Correction/action:** “primary empirical verification”; separate written derivations, deterministic checks, and simulations throughout the supplement.
- **Status:** corrected scientific interpretation; no mathematical counterexample needed.

### M07 — Major: sensitivity domains and attainable-world construction missing

- **Location/original:** Section 8.3, M23–M25; conditional averages z1 and z0.
- **Issue:** e=0 or e=1 invalidates inverse-odds derivation; m at 0 or 1 makes one conditional average undefined. Necessary weight constraints alone do not demonstrate that their endpoints correspond to possible full-data laws.
- **Derivation:** introduce population success/failure masses t,s with t+s=1. Intersect their bounded intervals (A5); then construct e*(Y1=1)=em/t and e*(Y1=0)=e(1−m)/(1−t). Let Y0 be independent with the observed control mean to match the remaining observed marginal. Boundaries handled directly with masses.
- **Correction/action:** explicit 0<e<1, finite Gamma, sufficient latent exchangeability, and feasibility construction in Appendix A.4. Clarify that sensitivity relaxes the assignment mechanism rather than retaining exact randomization as an extra constraint.
- **Status:** derived and checked against an independent 2-variable LP vertex enumeration on 400 random cases, endpoint-world checks, and boundary tests. Original numerical table retained because it is correct. General multi-action/joint-policy sharpness not established.

### M08 — Major: binary endpoint inference needs its own method

- **Location/original:** Sections 8.3–8.4 acknowledge endpoint uncertainty but do not resolve zero treated cells or the scope of cited quantile-regression theorems.
- **Issue:** no treated observations leaves m unestimated; a sample success rate of zero does not prove a population rate of zero. The linked Dorn–Guo inferential theorem assumes continuous conditional outcome densities, despite discrete identification results.
- **Correction/action:** explicitly prohibit epsilon repair of empty cells and transfer of the continuous-outcome CI theorem. Label endpoint confidence inference unresolved. Keep sensitivity ranges separate from sampling intervals.
- **Status:** source checked at full-text conditions and analytic boundary analysis. No endpoint-coverage theorem or calibrated endpoint bootstrap was run.

### M09 — Major: confounded generator not fully specified

- **Location/original:** Section 8.6, M26–M27.
- **Issue:** conditional marginals alone omit the joint law of X,U, coefficients, and independence of assignment/reward randomization. This prevents exact reproducibility and does not ensure latent exchangeability.
- **Correction/action:** preserve logistic equations as a proposed family; specify independent conditional randomization. Add a fully specified finite latent-U experiment in Appendix A.6 and executable code.
- **Status:** measured nominal IPS about 0.82 and oracle full-propensity IPS about 0.50, consistent with derived population values. Logistic-family sweeps remain proposed, not performed.

### M10 — Minor: ESS and score denominators lack executable boundary rules

- **Location/original:** Sections 7.2, 7.6, 11.8; M16–M19.
- **Issue:** all-zero weights give 0/0 ESS/SNIPS; n=0 or n=1 prevents the displayed variance estimate. Selected-action propensity validation cannot certify unobserved population support.
- **Correction/action:** raise errors or report insufficient evidence; specify finite nonnegative weights and positive sum. Tests distinguish absent known support from a rare action not sampled.
- **Status:** invalid-domain, support, singleton, overflow-resistant ESS scaling tests passed.

### M11 — Major: multiple-policy citation does not validate post-selection intervals

- **Location/original:** Section 12.1 attaches Dann et al. to selection-adjusted dashboard guarantees.
- **Issue:** the paper studies efficient evaluation of multiple RL policies with reused on-policy Monte Carlo samples; it is not a proof that the manuscript's post-selection logged-data intervals work.
- **Correction/action:** retain it as related work, explicitly distinguish its setting, and require independent final evaluation or a valid simultaneous procedure.
- **Status:** proceedings abstract inspected; no claim of independently re-proving that paper.

### M12 — Major: actual sparse-case coverage is materially below nominal

- **Location/original:** Sections 7 and 11 propose intervals and coverage experiments, but provide no executed results.
- **Issue:** this is an empirical gap, not a false theorem in the original. The implemented stress test demonstrates why the condition warnings matter.
- **Evidence:** 1,000 rare-reward datasets, n=2,000: DR cross-fit coverage 90.6%, Monte Carlo SE about 0.92 pp. In weak overlap with q1=0.5, IPS coverage 40.9%; SNIPS undefined in 360/1,000 runs. Raw outputs retained. These failures are limitations of naive finite-sample normal approximations, not failures of IPS unbiasedness.
- **Correction/action:** add complete measured tables, denominators, prior dependence, and negative results. Do not promote the displayed Wald interval to a blanket production decision rule.
- **Status:** executed/reproducible. Choice and validation of a more conservative sparse-regime procedure remains a priority.

### M13 — Major: policy revision is not yet a specified tested method

- **Location/original:** later chat's novelty proposal; not a method claimed in the original file.
- **Issue:** no alpha-selection algorithm, independent evaluation, relevant baseline comparison, or safety theorem exists in the workspace. A valid mixture need not improve value.
- **Counterexample:** baseline worth 1, proposed policy worth 0, alpha=.2 -> revised value .8. It is a valid distribution and still harmful.
- **Correction/action:** Appendix A.7 labels the proposal optional and heuristic; derives normalization and the context-dependent value difference; requires independent evaluation. Novelty report identifies SPIBB as prior art.
- **Status:** probability and counterexample tests passed. A complete revision method and efficacy comparison remain unimplemented; no safety guarantee claimed.

### N01 — Minor: symbol collision and missing definition

- **Original/location:** K denotes action count in Section 3 and cross-fitting folds in Section 4.5; qhat_i appears without explicit definition in M14–M15.
- **Correction:** use F folds; define qhat_i=qhat(X_i,A_i), sample SD, and full notation table.
- **Status:** revised and structurally checked.

### N02 — Minor: shrinkage has an undefined endpoint

- **Original/location:** Section 4.6, lambda*w/(w²+lambda).
- **Issue/correction:** at lambda=w=0 this is 0/0; define zero by continuous extension. Require finite nonnegative weights and lambda>=0.
- **Status:** dedicated regression test passed.

### N03 — Editorial: context density notation

- **Original/location:** Section 9.1, P1(X)/P0(X).
- **Correction:** use dP1/dP0 and require absolute continuity; the probability-mass notation is not general for continuous contexts.
- **Status:** corrected; no transport experiment claimed.

### E01 — Editorial: source typo

- **Original/location:** introduction contains `problem-focuse56d` in the on-disk source.
- **Correction/status:** restored `problem-focused`; original preserved byte-for-byte.

### S01/S02 — Editorial/scope: provenance and current verification status

- **Original:** describes preparation on 28 October and says no models were fitted.
- **Correction:** preserve original research cutoff, add audit date and actual executed scope. Distinguish this audit's tabular checks from the unbuilt product and unrun OBD replication.
- **Status:** manifest, script hashes, log, generated tables, and full diff supplied.

### L01 — Minor: missing estimator-selection predecessor

- **Location:** Section 5.8 covers PAS-IF but omits Su et al. (ICML 2020).
- **Action:** add the earlier adaptive-estimator-selection paper. This does not accuse the dossier of a false “first ever” claim; it improves the closest-work coverage.
- **Status:** primary proceedings page checked; novelty comparison updated.

## Complete displayed-equation audit

| IDs | Result | Evidence / required conditions |
|---|---|---|
| M01–M04 | Correct | Exact rational toy arithmetic and selected-action weighting |
| M05–M06 | Correct definitions | Fixed population, potential rewards, normalized policies, integrability |
| M07 | Correct estimator | q model quality controls identification/consistency; no universal low variance claim |
| M08–M09 | Correct | A1 identification; zero-support terms excluded/defined appropriately |
| M10 | Correct under IID finite moments | Independent enumeration and total-variance derivation |
| M11 | Correct if positive denominator | Ratio bias and no-match cases explicit |
| M12–M13 | Correct fixed-nuisance identity | Conditional algebra; limit/inference qualification strengthened |
| M14 | Correct Switch-DR form | qhat_i now defined, finite tau>=0; no standard DR guarantee after switching |
| M15 | Correct score definitions | Honest nuisance construction |
| M16 | Conditional asymptotic approximation | A.3 sufficient regime, n>=2; observed finite-sample undercoverage |
| M17 | Correct plug-in ratio influence | Delta-method gradient and finite nonzero denominator |
| M18 | Correct under justified paired inference | Covariance identity; factual versus hypothetical baseline distinction |
| M19 | Correct diagnostic on stated domain | Scale invariance, 1<=ESS<=n, zero weights rejected |
| M20–M22 | Correct odds algebra | 0<e<1, finite Gamma>=1, sufficient latent U |
| M23–M25 | Correct restricted population interval | A5 mass constraints, construction, independent LP vertices; not a CI |
| M26–M27 | Valid marginal specifications, incomplete generator | Joint distribution/coefficients/noise independence now explicit as requirements |
| M28 | Correct add-and-subtract identity | Fixed policies; population decomposition not observed-data causal attribution |

Inline expressions were also inspected: policy/weight normalization; binary ATE; propensity history; product-rate condition; clipping and shrinkage limits; long-horizon discounted sum; n/80 ESS illustration; Monte Carlo coverage SE; Gamma aggregation; latent-generator logits; unsupported-mass bound; percentage-point arithmetic; and the original attachment's q1−q0 and sigmoid thresholds. Their qualifications or corrections are recorded above and in Appendix A. No gradients, Hessians, matrix optimization algorithm, or central original theorem was present to audit. General sequential, proxy, and embedding methods are cited literature, not proved methods of this project.

## Verification integrity

Test passes verify implemented properties and known answers; they do not prove external validity. Stochastic estimates are reported with Monte Carlo uncertainty, not turned into brittle pass/fail coverage thresholds. A first-run JSON is retained. After that run, an off-prior weak-overlap scenario was added because the initial q1=0.5 happened to equal the reward model's empty-cell prior; this was a diagnostic expansion, not result replacement. The second run retains the original scenario and adds fixed-nuisance/hidden-U checks.

An initial PDF extraction hit Windows console encoding, then succeeded with Python UTF-8 mode. During document generation, a non-raw Python string produced a warning and could interpret a LaTeX escape as a control character; it was corrected before final document validation. Neither incident changed the source manuscript or mathematical simulation results.
