# Experimental protocol, frozen before the experiment run

Date: 30 October 2026. This is a falsification study, not an external preregistration. The runner records this file's hash before sampling. No final-seed tuning is permitted. The original project and audit are read-only inputs.

## Candidate and hypotheses

Candidate C1: compare two policies by projecting one simultaneous reward-mean confidence box onto their difference, rather than subtracting separately projected value intervals. Unknown means shared by both policies cancel. This candidate has passed elementary algebra and feasibility checks, but its novelty is already doubtful: it is a rectangular robust-optimization specialization. Code is a stage-7/8 research verification prototype, not integration of an accepted innovation.

H1 (practical effect): in finite tabular, bounded, unconfounded data, shared-region contrast bounds certify more true improvements than separately subtracting value bounds when policies have common uncertain components. Primary comparison: shared_blind, n=3000, two policies, 1000 independent repetitions. Success: paired improvement in beneficial-deployment rate >10 percentage points and paired normal 95% Monte Carlo interval excludes zero. Report harmful deployments and intervals, even if H1 fails.

H2 (differentiation): C1 supplies an improvement beyond the same rectangular shared-model robust objective implemented independently. Reject algorithmic novelty if they are algebraically identical and agree numerically to tolerance 1e-10. Winning only against separate intervals does not establish new research. This is the strongest applicable baseline for the exact restricted model, not a claimed full reproduction of a published general algorithm.

H3 (operating limits): hidden confounding and unmodeled transport shift can produce confidently wrong decisions. Their runs are outside the theorem assumptions and must not be pooled with valid-design coverage results. A current-logger reference has no shared structural blind-action cancellation.

## Data and controls

Finite X in {0,1}; three actions; Bernoulli potential outcomes independent of action given X except the explicit confounding stress. Only chosen outcomes are supplied to estimators. Known population masses are inputs, a restrictive assumption; no plug-in mass uncertainty is hidden. Policy candidates are generated once per scenario/class size using fixed seed 8128 and then frozen. The same log is supplied to all methods within a repetition. The true reward table is used only by the simulator, metrics and oracle checks.

Scenario parameters are explicit in `src/simulation.py`. Nine designs: common unsupported action; current-logger reference; full overlap; weak overlap; rare rewards; null effects; heterogeneous effects; hidden confounding; unmodeled context shift. Shared-blind q=[[.2,.6,.9],[.3,.7,.1]], mu=(.5,.5,0), reference=(.6,0,.4), principal target=(0,.6,.4), population=(.5,.5). Its contrast is .24, even though each value has unidentified contribution from action 2. The logger-reference case uses reference=mu and the same principal target. Weak overlap changes mu to (.4995,.0005,.5). Rare rewards multiply the full-overlap reward table by .01. Other exact tables are in code.

Run n in {300,3000}, policy count in {2,32}, and 1000 repetitions per cell: 36,000 logs total. Two policies means reference plus principal target; 32 adds fixed stochastic competitors. Seed formula: 1000000 + scenario_index*100000 + n_index*10000 + class_index*2000 + repetition. Each setting therefore has distinct seeds. Policy tables and all scenario parameters are exported. No learning on final evaluation logs except the explicitly evaluated policy selection and cross-fitted DR nuisance estimates. Confidence boxes simultaneously cover every policy on the fixed cells, so selecting a policy within them does not need an additional per-policy Bonferroni factor.

## Baselines and ablations

1. Joint contrast box (candidate under scrutiny): cellwise Hoeffding with alpha=.05 over all six cells; empty cells [0,1]. Maximize lower contrast; deploy only when >0, otherwise reference.
2. Shared-model robust reference: independently loop over scalar coordinates and choose the adverse endpoint for each signed coefficient. Same confidence set/objective. Exact comparator and novelty gate.
3. Separate value bounds: target lower minus reference upper, using the same simultaneous box. This isolates lost cancellation without changing the confidence model.
4. Cross-fitted DR contrast plus ordinary 1.96 Wald interval, selecting maximum lower bound. Two folds; smoothed cell-mean predictions; known selected propensities. If a policy difference has structural zero support, report it unevaluable; never divide by epsilon or supply oracle predictions. Post-selection coverage is not claimed for this diagnostic.
5. Midpoint plug-in contrast: box midpoint without uncertainty, an ablation that can extrapolate and overselect.
6. Always retain reference: zero harm at zero deployment, to prevent rewarding abstention alone.

A separate exact before/after demonstration distinguishes time/context composition from same-population policy contrast. An unchanged-policy control and independent vertex enumeration are unit tests. No claim of new methodology is based on beating the weak plug-in or separate-bounds comparators. No full SPIBB/PoLeCe/MVAL implementations: their extra settings/assumptions differ, and C1's restricted robust objective already has an exact strong comparator.

## Metrics and uncertainty

Report deployment rate, beneficial deployment (true selected improvement >1e-12), harmful deployment (<-1e-12), false improvement (deployment with true improvement <=1e-12), mean true selected improvement, oracle regret over the frozen candidate family including reference, all-candidate interval coverage, primary-target width, and undefined candidate counts. False improvement includes selecting a null policy; harm does not. Always-retain is not called abstaining from baseline safety.

For proportions: Monte Carlo SE and Wilson 95% interval, including zero-event cases. For paired benefit differences: mean paired difference and 1.96*sampleSD/sqrt(1000); primary setting fixed in advance. Worst-case MCSE for a proportion is 1.58 percentage points with 1000 repetitions; this can resolve the 10-point primary effect but cannot establish tiny risk differences. Scenario comparisons beyond the primary contrast are exploratory; no multiplicity-adjusted significance claims. Runtime is descriptive, hardware-dependent, and timed separately for cell aggregation and projection.

## Falsification, resources and omissions

Reject correctness if vertex/reference checks disagree, if unchanged-policy bounds are nonzero, or if simultaneous containment fails on a constructed box containing truth. Reject the novel-method claim on H2 equivalence regardless of H1's result. Reject broad superiority if advantages vanish against paired DR in well-supported settings; report conservative power loss, not just harm reduction.

Scalability: time projection at S in {2,100,1000}, M in {2,32,128}, K=3 using synthetic confidence boxes, repeat five times and report median; this measures the calculation, not end-to-end ingestion. Public-dataset evaluation is not executed in this protocol because exact unknown-action truth and a known finite target context distribution are required for these tests; OBD replication remains a separate follow-up with empirical reference uncertainty. General reward-model learners, adaptive logs, uncertain context masses, estimated propensity misspecification, sensitivity-bound inference, sequential RL and actual data acquisition are not covered. The hidden-U and shift stress tests do not confer robustness to either.
