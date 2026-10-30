# Joint likelihood inference for policy comparisons

This is an application extension to the project, not a claim to have invented likelihood inference. It is being assessed against a strong cellwise KL baseline and an alternative joint mixture construction. Conclusions belong in `RESULTS.md`, which is generated only after experiments finish.

## Scope

There are S fixed, sufficient context strata and two actions. R is Bernoulli. Observations are IID under a fixed logging design, with consistency and exchangeability within strata. Let q_sa=E[R(a)|X=s], and let p_s be the known target context distribution. Fixed-stratum probabilities may alternatively describe an explicitly declared finite target population; that estimand is different from an unknown deployment-population value. The experiment uses known population weights.

The reference policy is the actual logger. For any candidate pi, define c_sa=p_s(pi(a|s)-mu(a|s)), and Delta=sum c_sa q_sa. q is an unknown vector of D=2S reward means. All policies use the same fixed cells; the uncertainty region covers the entire vector, so projection can accommodate outcome-adaptive policy selection on these cells. It does not accommodate a data-dependent partition without additional analysis.

## Split likelihood confidence region

Use an independent pilot half to fit any valid Bernoulli table qtilde. The implementation uses (successes+.5)/(count+1), which avoids zero predictive probabilities. On validation counts n_j and successes k_j, define

\[
E(q)=\prod_j\frac{\tilde q_j^{k_j}(1-\tilde q_j)^{n_j-k_j}}
{q_j^{k_j}(1-q_j)^{n_j-k_j}}.
\]

Conditional on the pilot and the validation assignments, E_q[E(q)]<=1: sum the numerator probability over the support of the denominator. With interior means it equals one. Markov's inequality therefore yields P_q(E(q)>1/alpha)<=alpha. This is the standard universal-inference argument, independently specialized here, not a new theorem. At boundary means, impossible observed outcomes have zero probability and the expectation inequality is sufficient.

Let phat_j=k_j/n_j for observed cells. The confidence set is equivalently

\[
C=\{q\in[0,1]^D:\sum_{j:n_j>0}n_j\,KL(Ber(\hat p_j)\Vert Ber(q_j))\le R\},
\quad R=\log(1/\alpha)+\sum_{j:n_j>0}n_j KL(\hat p_j\Vert\tilde q_j).
\]

An empty validation cell contributes zero to the likelihood constraint and remains completely uncertain, even if the pilot saw it. This is a real power cost of splitting. We do not secretly treat pilot-only predictions as identified outcomes.

For every q in C, obtain bounds L(c)=min c'q, U(c)=max c'q. On the single event qtrue in C, ALL such contrasts are covered. Selecting the largest lower bound and deploying only when it is positive consequently bounds the probability of a false improvement by alpha under the stated assumptions. This is a fixed-horizon result. The demo does not inherit anytime validity merely because related likelihood methods have it.

## Solver

For U(c), unconstrained empty cells contribute max(c_j,0). For observed cells the convex dual is

\[
U(c)=\inf_{\lambda\ge0}\left\{\lambda R+\sum_j\sup_{q_j\in[0,1]}
[c_jq_j-\lambda n_j KL(\hat p_j\Vert q_j)]\right\}+\sum_{n_j=0}\max(c_j,0).
\]

For a positive coefficient, put t=c_j/(lambda*n_j). The maximizing q solves t q(1-q)=q-phat. For t>0 its root in [phat,1] is

\[
q=\frac{t-1+\sqrt{(1-t)^2+4t\hat p}}{2t}.
\]

For t<=1 use the algebraically equivalent 2*phat/(1-t+sqrt(...)) to avoid cancellation; t=0 returns phat. Negative coefficients use the transformation p to 1-p and q to 1-q. Boundary empirical means are handled explicitly by these limits. A one-dimensional bisection finds the multiplier where the KL budget is exhausted, unless the unconstrained maximum already fits. Strict feasibility at phat when R>0 supports strong duality; boundary/unobserved cases have direct limiting solutions. Lower bounds follow by negating the upper projection for -c.

The implementation returns the dual bound with a 1e-10 numerical allowance, and checks primal/dual agreement and independent low-dimensional enumeration. This is ordinary floating-point verification, not a formal interval-arithmetic certificate. Numerical validity should be revalidated before expanding to much larger/scaled coefficients. Our policy coefficients lie in [-1,1].

Per projection batch, time is O(T*M*D), T=65 dual iterations, M candidate count; memory O(MD). Sufficient-statistic aggregation is O(n+D), and simulating sufficient statistics avoids storing raw rows. The simulator's multinomial counts/binomial successes have exactly the same law as aggregating the specified IID logs.

## Strong comparators

The full-data mixture region integrates each Bernoulli likelihood against an independent Jeffreys Beta(1/2,1/2) prior. Its numerator is a normalized mixture distribution, so the same expectation/Markov argument applies without splitting. Its KL radius is log(1/alpha)+log L(MLE)-log mixtureL. The prior is a construction of an e-value, not a Bayesian posterior-coverage claim. This is established mixture-likelihood methodology, not an invention here.

The KL-Chernoff box uses per-cell constraint n_j KL(phat_j||q_j)<=log(2D/alpha), with [0,1] for empty cells. A two-tail Chernoff bound and union bound establish simultaneous validity. It uses all observations and is much stronger for rare rewards than Hoeffding. Beating only Hoeffding would not support our extension.

The full-data saturated tabular Wald method uses known p and variance sum c_j^2 phat_j(1-phat_j)/n_j, with Bonferroni critical values over candidate policies. It is asymptotic; zero empirical variance can give false precision, and empty relevant cells are reported undefined. It is not presented as a full reproduction of general cross-fitted DR or empirical-likelihood OPE.

## Failure conditions

- Bernoulli model mismatch, insufficient strata or hidden confounding invalidate a causal reading of the region. Conditional observed-mean coverage is not causal identification.
- More cells increase the region's uncertainty budget and can reduce power. High-dimensional continuous covariates need an additional method, not naive binning.
- An unlucky or inaccurate pilot inflates R; splitting sacrifices observations and can lose to full-data methods.
- Unknown target-population weights require their own uncertainty analysis. Reward drift requires more than known new context masses.
- Zero support remains a partial-identification problem; the optimizer cannot create counterfactual observations.
- Aggregate improvement does not guarantee every subgroup benefits.

## Sources and novelty boundary

The split construction comes from [Wasserman, Ramdas and Balakrishnan, Universal Inference](https://arxiv.org/html/1912.11436v4), especially the confidence-set construction and profiling discussion. [Emmenegger, Mutny and Krause, NeurIPS 2023](https://papers.neurips.cc/paper_files/paper/2023/hash/5491280797f3192b895bce84eb83df8d-Abstract-Conference.html) studies likelihood confidence sets in sequential decision-making. [Karampatziakis, Langford and Mineiro, Empirical Likelihood for Contextual Bandits](https://arxiv.org/abs/1906.03323) already uses likelihood-based OPE and lower-bound optimization. These precedents rule out claiming that likelihood-based policy comparison itself is new. Our implemented specialization, missing-support handling and benchmark are a concrete application contribution whose empirical value is tested here.

Targeted data acquisition was not chosen as the immediate differentiator: [Wan, Kveton and Song, ICML 2022](https://proceedings.mlr.press/v162/wan22b.html) explicitly studies efficient and safe exploration for policy evaluation AND comparison, a close predecessor that strengthens the earlier novelty rejection. A competitive pitch must acknowledge it rather than claiming contrast-focused acquisition as an unexplored idea.
