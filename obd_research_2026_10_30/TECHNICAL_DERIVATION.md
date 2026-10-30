# From item-level uncertainty to policy-specific evidence

## What changes relative to the previous prototype

The previous solver built a confidence region for every item reward mean, then projected it onto a policy difference. Its primary synthetic comparison tied a strong KL-box baseline. Increasing solver complexity alone did not establish a benefit.

This extension changes the statistical representation before applying the solver. When a proposed policy multiplies the logger's probabilities by only a few distinct factors, only a few aggregate reward means are needed for that comparison. The implementation verifies this property algebraically. It does not cluster items because their estimated rewards look similar.

## Exact grouping identity

Let A be an action drawn from a known, positive, context-free logger mu, Y in {0,1}, and q_a=E[Y|A=a]. Under randomization/identification, q_a also identifies the population reward mean for action a. For a fixed target policy pi, define c_a=pi_a-mu_a and d_a=c_a/mu_a. The gain is Delta=sum_a c_a q_a.

Choose a partition G such that d_a=d_g for every action in group g. Write mu_g=sum_{a in g}mu_a and Q_g=sum_{a in g}mu_a q_a/mu_g. Then

    Delta = sum_g (mu_g*d_g)*Q_g.

Within-group q_a may differ arbitrarily. Given IID logs, a retained group observation has binary reward with marginal success probability Q_g. Conditional on group counts, group successes are independent binomials. We condition on group membership/counts, not on the finer realized action counts. Treating each action's realized count as fixed and then claiming a homogeneous binomial for the pooled rewards would be the wrong argument.

This identity is a simple conditional-expectation reduction. Related work on marginalized OPE and evaluation-weight-preserving coarsening must be credited; this document does not claim a new identification theorem.

### Uniform logging and a top-k target

With A available items, mu_a=1/A and pi uniform over a pilot-selected set T of k items, the two ratios are A/k-1 inside T and -1 outside. Thus

    Delta = (1-k/A)*(Q_T-Q_notT).

An 80-item comparison becomes a two-mean inference problem. Item heterogeneity is allowed. Different candidate top-k sets require different groupings; one confidence region does not automatically cover all such groupings. We use alpha/M per candidate for M pilot-selected candidates.

### Why arbitrary grouping is not valid

If d_a varies within a group, replacing it with dbar_g changes the estimand. The residual is sum_a mu_a(d_a-dbar_g)q_a. For q in [0,1], its exact unrestricted range is [sum min(residual_coefficient,0), sum max(residual_coefficient,0)]. Our present implementation rejects nonconstant-ratio groups rather than omitting this error. A rounded-policy extension would need to include this penalty and account for partition selection; it is not part of the measured results.

## Independent learning and certification

The pilot may select item sets, estimate reward means and choose any proper predictive distribution. All of these are frozen before seeing certification rewards. Let validation counts be n_g,k_g and pilot grouped counts n0_g,k0_g. The numerator is a fixed equal-weight mixture of two normalized distributions on validation reward sequences:

    P_pilot = product_g B(k_g+k0_g+1/2, n_g-k_g+n0_g-k0_g+1/2)
                         / B(k0_g+1/2,n0_g-k0_g+1/2)
    P_flat  = product_g B(k_g+1/2,n_g-k_g+1/2)/B(1/2,1/2)
    P_mix   = (P_pilot + P_flat)/2.

The binomial coefficients are omitted because this is sequence likelihood; they cancel in the likelihood ratio and appear when summing over possible count vectors. Conditional on the pilot and validation group counts, each component sums to one over reward sequences, even if pilot predictions are inaccurate or pilot groups were selected optimistically. There is no assumption that a Bayesian prior generates the real reward means.

For any candidate mean vector Q, let E(Q)=P_mix/L_validation(Q). At the true vector, E[E(Q_true)|pilot, counts]<=1. Therefore Markov's inequality gives a (1-alpha/M) confidence region E(Q)<=M/alpha. In KL form:

    sum_g n_g KL(Ber(k_g/n_g) || Ber(Q_g)) <= R
    R = log(M/alpha) + log L_validation(MLE) - log P_mix.

Unobserved groups have [0,1] uncertainty: a pilot posterior is a predictor, not an extra observation in the validation likelihood. The flat component prevents a bad pilot from making the region more than log(2) worse in KL radius than the flat predictive region using the same data. This follows from P_mix>=P_flat/2; it does not assert that the predictive method always has narrower intervals.

Projection minimizes/maximizes the signed group contrast over the convex KL set. The one-dimensional dual solver is inherited from the earlier extension, generalized to batched group counts, and checked independently. It returns a conservative floating-point dual bound plus a feasible endpoint model. A union bound covers all M policy intervals; choosing the largest positive lower bound controls false improvement under the declared model. Numerical tolerances are checked, not certified by interval arithmetic.

## What an endpoint witness means

The adverse Q vector is a model in a group-level confidence set that nearly attains the lower bound. It shows what the retained comparison evidence cannot exclude. It is not an estimate of a hidden confounder, not the true counterfactual world, and not automatically a model in the original full item-likelihood region. The compression intentionally discards item distinctions irrelevant to this contrast; a witness must be labeled at that information level.

## Repair and sensitivity boundaries

Selecting a better-supported top-k candidate is a restricted alternative-policy search. It is not a general policy optimizer. Merely mixing an unresolved candidate with the logger cannot change the sign of its lower bound: L(rho*pi+(1-rho)*mu)=rho*L(pi). The useful alternative must change which actions receive mass, not only shrink the same direction.

For a positive lower bound L and tau=1-k/A, if each of the two population group reward means changes by at most epsilon, the gain is at least L-2*tau*epsilon. Thus L/(2*tau) is an interpretable absolute-mean drift tolerance. It is not a Rosenbaum/marginal-odds confounding parameter and does not provide protection against arbitrary hidden confounding.

## Data assumptions and limitations

- The OBD primary analysis uses Random logs, a single position, and context-free target policies. Randomization lets us average over user contexts without fitting a potentially insufficient context partition.
- Position-specific click responses may depend on the surrounding slate. As in standard position-wise OBD OPE, a causal interpretation of changing the marginal position policy needs an appropriate no-cross-item-interference/position-response assumption. We do not evaluate an arbitrary whole-slate policy.
- The binomial argument assumes stationary IID impressions. Exact timestamp groups stay in the same split; single-position filtering avoids duplicating a slate. User-level dependence remains unidentified because no stable user IDs are used. Time-block bootstrap and chronological tests are diagnostics, not repairs to the theorem.
- OBD references are noisy empirical estimates. Only synthetic experiments have known truth and support genuine coverage/regret measurement.
- Exact ratio grouping helps structured candidate policies; arbitrary personalized softmax policies may have nearly as many ratio levels as actions. No general dimensionality reduction is promised.
- Grouped exact Clopper-Pearson and grouped KL methods are strong, simple competitors. If they win, the project should use them rather than insist on a more elaborate likelihood mechanism.

## Primary literature and novelty boundary

1. Wasserman, Ramdas and Balakrishnan, [Universal Inference](https://arxiv.org/html/1912.11436v4): the split/predictive likelihood-ratio confidence principle and profiling are established.
2. Karampatziakis, Langford and Mineiro, [Empirical Likelihood for Contextual Bandits](https://arxiv.org/abs/1906.03323), NeurIPS 2020: likelihood-based policy evaluation and lower-bound optimization precede this project; their full method is not reproduced here.
3. Saito and Joachims, [Off-Policy Evaluation for Large Action Spaces via Embeddings](https://proceedings.mlr.press/v162/saito22a.html), ICML 2022: action aggregation and marginalized weighting are established. Their causal-mediation route differs from our exact policy-ratio identity; neither makes arbitrary aggregation harmless.
4. Lee, Zou and Kosorok, [What a Data Release Must Preserve for Off-Policy Evaluation](https://arxiv.org/abs/2610.15283), October 2026 preprint: especially close work on evaluation-weight-preserving coarsening and policy comparisons. This rules out a broad claim that our ratio-preserving reduction is unexplored. Their released-history identification problem differs from the finite-sample grouped Bernoulli procedure implemented here.
5. Laroche, Trichelair and Tachet des Combes, [Safe Policy Improvement with Baseline Bootstrapping](https://www.microsoft.com/en-us/research/wp-content/uploads/2019/04/ICML2019___SPIBB-15.pdf), ICML 2019: restricting changes where evidence is weak is established safe-improvement methodology.
6. Ouyang, Gong and Bondell, [Bayesian Inference of Contextual Bandit Policies via Empirical Likelihood](https://www.jmlr.org/papers/v27/23-0958.html), JMLR 2026: joint policy comparison with likelihood uncertainty is also active prior work. Our frequentist conditional e-value construction should not be described as the first joint likelihood analysis.
7. Saito et al., [Open Bandit Dataset and Pipeline](https://arxiv.org/abs/2008.07146), NeurIPS 2021 Datasets and Benchmarks: data source and multi-policy empirical evaluation protocol. See [ZOZO's release page](https://research.zozo.com/data.html).

The defensible contribution is an implemented, tested combination with a concrete operating range and auditable outputs. A targeted literature search cannot establish worldwide novelty or predict other teams' submissions.
