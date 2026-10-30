## Appendix A. Audited mathematical specification

This appendix states sufficient conditions and supplies independent derivations. It does not assert that these conditions were established for a real deployment. Equation labels M01–M28 identify the original displayed expressions; equation tags A1–A7 identify additions. The separately titled identification and variance assumptions below are distinguished by their titles.

### A.1 Notation and scope

| Symbol | Domain and interpretation |
|---|---|
| n, K, F | Sample size n>=1, finite number of actions K>=1, cross-fitting folds 2<=F<=n |
| X, P_X | Pre-action context and its evaluation-population law |
| A, R(a), R | Action in {0,...,K-1}, potential reward, observed reward R=R(A) |
| mu, pi, pi_0 | Measurable logger, fixed target, fixed baseline; nonnegative action probabilities summing to one |
| p_i, b_i | Actual selected-action propensity; fitted/working selected-action propensity when distinguished |
| q, h | True potential-outcome mean q(x,a); generic fixed outcome nuisance h(x,a) |
| qhat_i, qhat_i^pi | Held-out prediction for observed action; target-probability-weighted prediction |
| w, Z, D_i | Nonnegative importance ratio; row score; paired improvement score (not the dataset D) |
| sigma^2(x,a) | Conditional observed-reward variance under identification |
| e, e*, Gamma | Nominal binary propensity, sufficient-latent full propensity, finite marginal-odds bound >=1 |
| m, ell, h_s | Treated success probability, lower/upper inverse-propensity bounds; h_s avoids confusion with outcome nuisance h |
| s_Z, bar w | Sample SD with denominator n−1; sample mean weight |
| H, gamma | Sequential horizon H>=1 and discount 0<=gamma<=1; unrelated to sensitivity Gamma |
| d | Predeclared minimum worthwhile improvement, d>=0 |

**A1 (basic identification regime).** Observations are IID; the potential-reward vector and action satisfy consistency, no interference, and R(a) independent of A given X. For P_X-almost every x, pi(a|x)>0 implies mu(a|x)>0. The target is fixed independently of evaluation outcomes. Assume target-weighted absolute rewards are integrable. Sums with pi=mu=0 are defined to contribute zero rather than evaluating 0/0. Structural support conditions apply to the population, not only sampled rows.

Known full propensities conditional on (X,U) give an alternative identification regime: replace the conditioning set by (X,U) in A1 and require conditional support there. This is not the same as using the marginal propensity e(X).

**A2 (variance).** To interpret M10 as a finite variance and apply a conventional CLT, require E[(wR)^2]<infinity. Finite K and rewards in [0,1] do not alone establish this. Uniform target-support overlap mu>=epsilon>0 with bounded rewards is a convenient sufficient condition. For independent non-identically distributed scores, variance is n^(-2) times the sum of row variances; the manuscript's IID sample-variance formula is not automatically applicable.

### A.2 Independent IPS and DR derivations

Under A1, E[R|X,A=a]=q(X,a). Conditional expectation gives M09. Absolute integrability justifies the finite action sum and outer expectation. Independence is not needed for this one-row identity; IID sampling is needed for the stated common-population sample-mean analysis. Applying total variance conditional on (X,A) gives

\[
\operatorname{Var}(wR)=E[w^2\sigma^2(X,A)]+\operatorname{Var}(wq(X,A)). \tag{A1}
\]

Dividing by n under IID yields M10. This is not a proof that either term is finite.

For fixed nuisances b(x,a)>0 on target support and h(x,a), with integrable scores, condition on X:

\[
E[Z_{DR}\mid X]=\sum_a\pi(a\mid X)\left[h(X,a)+\frac{\mu(a\mid X)}{b(X,a)}(q(X,a)-h(X,a))\right]. \tag{A2}
\]

Subtracting sum_a pi q gives M13 exactly. If b=mu or h=q, the conditional bias vanishes. Independent nuisance training lets us apply this conditional-on-training identity. Cross-fitting applies it fold by fold; fold scores are not mutually independent merely because each row is held out. Their pooled asymptotic variance requires a negligible fitted-nuisance remainder.

For clipped IPS and R>=0, the bias relative to valid IPS is

\[
E[(\min(w,c)-w)R]=-E[(w-c)_+R]\le0,\quad c\ge0. \tag{A3}
\]

This sign does not apply to negative rewards or to signed DR residuals. Switch and shrinkage change the correction and generally introduce model-dependent bias. At lambda=0 define shrunk weights as zero explicitly, including w=0; the unrepaired fraction has 0/0 at that point.

### A.3 When the reported DR standard error is justified

One sufficient regime is IID bounded rewards; fixed F and an independently fixed target; true and fitted propensities bounded below on target support; L2 consistency of both nuisances; and

\[
\|\hat q-q\|_2\|\hat\mu-\mu\|_2=o_p(n^{-1/2}), \tag{A4}
\]

with stable finite second moments and a nonzero limiting score variance. Norms may be taken over P_X and the finite action counting measure with uniform boundedness assumptions. Cauchy–Schwarz bounds the bias product from M13; cross-fitting and L2 convergence control empirical-process remainder terms. Then the leading influence function is q^pi(X)+pi(A|X)/mu(A|X)(R−q(X,A))−V, and its sample variance supports asymptotic Wald inference. These are sufficient, not necessary, assumptions. Exact known propensities allow broader outcome-model regimes but still require stable held-out predictions and appropriate moments for the variance approximation.

**Consistency does not imply this regime.** Take one context, target always action 1, true mu(1)=1/4, working b(1)=1/2, true q1=1/2, and h_n(1)=1/2+n^(-1/4), for n>=16. The reward nuisance converges to the truth, yet the DR bias is (1−mu/b)(h_n−q)=n^(-1/4)/2. This dominates n^(-1/2) sampling error. Cross-fitting a deterministic h_n changes nothing. Ordinary centered root-n inference fails despite consistency.

For SNIPS, apply the delta method to f(u,v)=u/v at (E[wR],E[w])=(V,1). Its gradient is (1,−V), giving influence w(R−V), and the plug-in M17. This needs a nonzero denominator and a valid joint CLT; it does not make an all-zero-weight sample evaluable. For paired differences, Var(Z−B)=Var(Z)+Var(B)−2Cov(Z,B), which yields M18 under the same justified sampling regime.

### A.4 Binary sensitivity: necessity, feasibility, and boundaries

Assume binary A and R, a fixed positive-probability context stratum, 0<e<1, and finite Gamma>=1. There exists sufficient latent U so that assignment is independent of both potential outcomes conditional on (X,U). Under the stated odds bound, full propensities are bounded away from both zero and one within this stratum.

Rearranging the lower and upper odds inequalities yields M21. Inverting endpoints gives M22. For m in (0,1), consistency and full-propensity weighting yield M23 and q1=em z1. Let t=q1 and s=1−q1. Then

\[
em\ell\le t\le emh_s,\quad e(1-m)\ell\le s\le e(1-m)h_s,\quad t+s=1. \tag{A5}
\]

Intersecting these intervals yields M24–M25. This is a two-variable linear program, independently checked by vertex enumeration in the verification code.

**Feasibility for a single potential mean.** For any t in the interval with 0<t<1, choose P(R(1)=1|X)=t, e*(R(1)=1)=em/t, and e*(R(1)=0)=e(1−m)/(1−t). A5 ensures both assignment probabilities satisfy the odds bound; their population average is e, and the observed treated success rate is m. To accommodate an arbitrary observed control success probability m0, choose R(0) independently of R(1) with mean m0, and let assignment depend only on R(1). Thus the construction matches the binary observed outcome marginals. This establishes attainability for this restricted single-arm mean with otherwise unrestricted latent dependence; it does not establish joint extrema for arbitrary contrasts or additional structural restrictions.

If m=0 or m=1, do not define a conditional average for the absent treated-outcome category. Instead A5 directly yields t=0 or t=1. Finite Gamma with full latent positivity makes these boundaries meaningful at the population level. In a finite sample, observing zero successes does not imply population m=0. Plug-in endpoint collapse can substantially understate uncertainty.

As Gamma increases, the underlying feasible set expands, so lower endpoints cannot increase and upper endpoints cannot decrease. At Gamma=1, ell=h_s=1/e and L=U=m. Independent context strata permit averaging single-arm endpoints using fixed population shares. Changing the target population requires replacing those shares under an explicit transport assumption.

**Statistical status:** the derivation is a population identification argument. It does not provide finite-sample coverage for plug-in endpoints. The referenced quantile-balancing inference theorem for continuous outcomes is not a binary-outcome CI theorem. No such CI guarantee is established in this audit.

### A.5 Counterexamples that delimit claims

1. **Overlap does not imply finite variance.** X uniform on (0,1), mu(1|X)=X, target always 1, R(1)=1. IPS has mean 1 but second moment integral_0^1 (1/x) dx=infinity. This satisfies pointwise support; it violates A2, not A1.
2. **DR can have larger variance than IPS.** No context; mu(1)=0.1; target always 1; rewards always zero; h1=1. IPS is identically zero; DR=1−10 I(A=1) has mean zero and variance 9. True propensities, bounded rewards, and overlap all hold.
3. **SNIPS can have larger variance than IPS.** No context; mu=(1/2,1/2); pi=(1/4,3/4); deterministic rewards (1,1/3). For n=1, IPS is always 1/2. SNIPS equals the observed reward, with variance 1/9. Both actions are supported and all weights are positive.
4. **Same-row reward fitting breaks the conditional DR argument.** With unique contexts, uniform logger and target, and Bernoulli(1/2) rewards, a memorizer predicting the observed reward for the observed action and zero for the other action has zero residual and target prediction R/2. Expected DR is 1/4 rather than the true 1/2. Independent nuisance fitting was violated.
5. **Exact full propensities versus confounding.** U uniform on {0,1}; mu(1|U)=(0.1,0.9), q1(U)=(0.1,0.9). The true value is 0.5. Marginal propensity 0.5 gives IPS mean 0.82, while exact full-propensity weighting gives 0.5. The marginal odds departure bound needed is Gamma=9.
6. **Missing support.** A logger always selects A0 with mean reward 0.2. Worlds with q1=0 and q1=1 yield identical observed logs but different always-A1 values. No estimator can distinguish them without extra assumptions.
7. **Fallback is not a safety theorem.** Baseline selects an action worth 1, proposed policy an action worth 0. A 20% mixture toward the proposal is a valid distribution with value 0.8, still worse than baseline.

The associated automated tests include exact rational calculations, independent scalar implementations, vertex checks, and invalid-input rejection. Cases 1 and 4 are analytic arguments; their generality is not established by numerical testing.

### A.6 Fully specified verification experiments

Primary experiments: X is Bernoulli(1/2), A given X is Bernoulli(e_X), and independent reward uniforms produce Bernoulli(q_XA) outcomes. The target always selects A1. Historical contextual q tables are given in `verification/verify.py`. The regular case reproduces Section 1. Weak overlap sets both e_X=0.0005 and q1=0.5; a second weak-overlap case changes q1 to 0.7 to test sensitivity to the fitted model's prior. The rare-reward case scales the original reward probabilities by 0.01. Every run has n=2,000; each scenario uses 1,000 independently seeded datasets.

Cross-fitting uses five folds defined by a random permutation modulo five. For each held-out fold and each context-action cell, fit (success count+0.5)/(cell count+1) using only the other folds. This yields a defined fallback for empty training cells without inventing overlap. It is an explicit modeling choice, not a confidence guarantee. The fitted model never sees simulator reward means. Oracle DR is reported separately as a diagnostic using evaluator-only truth.

Fixed-nuisance experiments use the regular generator. Wrong action propensities equal 0.5; wrong reward predictions are 0.3 in context 0 and 0.4 in context 1 for both actions. The DR limit is 0.4 if either nuisance is exact and 0.6 if both specified nuisances are wrong. These checks isolate algebra; they do not test the convergence rate of arbitrary fitted ML nuisances.

In the hidden-U experiment the measured context is constant, U is Bernoulli(1/2), e*(U)=(0.1,0.9), and both action-specific reward probabilities are (0.1,0.9) across U. Action/reward uniforms are independent conditional on U. The analyst uses e=0.5. Each batch also computes an explicitly oracle comparator using full propensities.

### A.7 Algorithms, complexity, and the proposed policy-revision extension

Let T_fit(m,K,d) be the chosen nuisance model's training cost on m observations of d features and T_pred(n,K,d) the cost of all-action predictions. F-fold evaluation costs approximately F T_fit(n(1−1/F),K,d)+T_pred(n,K,d)+O(nK); add a separate propensity-training cost if probabilities are fitted. Storing all-action predictions uses O(nK) memory; streaming target-weighted predictions can reduce score-storage memory to O(n), besides model and input memory. IPS with only selected-action probabilities is O(n). SNIPS and ESS are O(n); quantile plots may require O(n log n) sorting. Binary sensitivity with S strata and G Gamma values costs O(n+SG). A score bootstrap with B repetitions costs O(Bn); a full-refit bootstrap also multiplies model-training cost by B. These are operation counts, not measured production latency.

The later chat proposed a context-dependent policy mixture; it is **not an implemented contribution in the original manuscript**. A mathematically valid optional extension is

\[
\pi_\alpha(a|x)=\alpha(x)\pi(a|x)+(1-\alpha(x))\pi_0(a|x),\quad 0\le\alpha(x)\le1. \tag{A6}
\]

Policies must share action eligibility. Summing A6 over actions proves normalization. Its value difference is

\[
V(\pi_\alpha)-V(\pi_0)=E_X\left[\alpha(X)\sum_a(\pi(a|X)-\pi_0(a|X))q(X,a)\right]. \tag{A7}
\]

The sign is not guaranteed. For context-dependent alpha it is generally wrong to replace this expression by E[alpha] times the unmodified policy improvement. Select alpha on development data, freeze it, then evaluate on independent final data or use a justified simultaneous procedure. A fixed finite candidate grid is a possible experimental specification, not a new theorem or a proven safety mechanism. Baseline bootstrapping is prior art: [Laroche et al., ICML 2019](https://proceedings.mlr.press/v97/laroche19a.html).

For drift, M28 is an exact add-and-subtract identity for population values, not an automatic causal attribution of measured sample differences. If P1 is absolutely continuous with respect to P0 and q1=q0, transport adds the context density ratio to the action weight. Both action support and context support are required.

For unsupported mass u, v+u bounds require known reward range [0,1], known support, and identification of the supported contribution v. With a general reward range [L,U], the corresponding interval is [v+Lu,v+Uu]. This is partial identification, not an ordinary confidence interval.
