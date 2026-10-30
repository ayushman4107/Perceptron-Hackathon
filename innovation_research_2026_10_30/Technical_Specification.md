# Technical specification: comparison through a shared uncertainty set

Status: mathematically valid restricted research prototype; novelty must pass a separate gate. The following elementary derivations are independent checks, not claims of newly discovered theorems.

## Problem and assumptions

X has a fixed, finite, prespecified domain of S cells; A has K actions. Data are n IID triples (X,A,R), R in [0,1]. Consistency and conditional exchangeability identify observed cell means with potential-reward means q_sa. Context masses p_s are known for the target population. Conditional reward means transport unchanged if p differs from the logging masses. The logger is fixed; structural support is supplied by its design, not inferred from sample counts. Adaptive logging, hidden confounding and unknown transport masses require other methods.

Policies pi_j are S by K probability arrays. Reference pi_0 is not necessarily the logger mu. Define c_j,sa=p_s(pi_j,sa-pi_0,sa), Delta_j=sum c_j,sa q_sa. The scientific question is whether Delta_j>0. n_sa and rbar_sa denote observed cell counts and sample reward means. A fixed partition must capture all confounders needed for exchangeability; aggregating continuous covariates into arbitrary bins can violate this assumption.

## Simultaneous confidence region

For n_sa>0, let h_sa=sqrt(log(2SK/alpha)/(2n_sa)), l_sa=max(0,rbar_sa-h_sa), u_sa=min(1,rbar_sa+h_sa). For n_sa=0 use [0,1]. Let C=product_sa[l_sa,u_sa]. Conditional on the vector of assignments, each observed cell contains independent bounded rewards with the same mean under the assumptions. Hoeffding bounds each cell's two-sided failure by alpha/(SK); a union bound and integration over assignments imply P(q in C)>=1-alpha. Empty cells cover trivially. This is fixed-horizon simultaneous coverage, not an anytime guarantee. Rewards need not be Bernoulli for this argument.

The global count SK deliberately includes irrelevant cells. Dropping cells after inspecting outcome estimates without adjusting the guarantee is prohibited. The endpoints are conservative confidence limits; they are not exact equal-tail binomial intervals.

## Contrast projection and derivation

For each j,

\[
L_j=\min_{q\in C}c_j^Tq=\sum_{c_j\ge0}c_jl+\sum_{c_j<0}c_ju,
\qquad U_j=\sum_{c_j\ge0}c_ju+\sum_{c_j<0}c_jl.
\]

Each coordinate is independently constrained, so minimization chooses l for a positive coefficient and u for a negative one. These endpoints are attained by feasible vertices; the derivation is exact for a rectangular region. Coupled smoothness/causal constraints require a different optimization, and this rectangle may then be loose.

For separate policy intervals, Lsep_j=sum p*pi_j*l - sum p*pi_0*u. Subtracting yields the exact identity

\[
L_j-Lsep_j=\sum_{s,a}p_s\min(\pi_j(a|s),\pi_0(a|s))(u_{sa}-l_{sa})\ge0.
\]

This quantifies duplicated uncertainty in separate projections. It does not show superiority to paired DR or robust contrast optimization, both of which already preserve shared terms. In particular, the direct robust objective min_{q in C}(V_q(pi_j)-V_q(pi_0)) IS L_j; there is no difference from that established objective to discover experimentally.

## Identification and width

At the population limit, observed-support cells have known q; missing cells B have [0,1]. The sharp unrestricted contrast width is

\[
W_{ID,j}=\sum_{(s,a)\in B}p_s|\pi_j(a|s)-\pi_0(a|s)|.
\]

Sufficiency for point identification: every missing-cell coefficient is zero. Necessity in the unrestricted bounded-mean model: change a single missing mean from 0 to 1; the observed law is unchanged but the contrast changes by its nonzero coefficient. Zero target population mass contributes nothing. This is a linear identifiability observation, not a remedy for missing data.

Finite-sample width is sum |c|*(u-l). It includes sampling uncertainty on observed cells and complete ambiguity on empty cells. An empirical zero count is not evidence of population zero support: with small positive logging probabilities, additional logs may help. Knowing structural support allows that distinction; the reward samples alone do not.

If pi_0=mu, then pi_0=0 on every structurally missing action. W_ID,j reduces to target unsupported mass: there is no shared-blind-action cancellation. This materially narrows the candidate's relevance to the original target-versus-current-logger question. It can compare two alternatives that both differ from the historical logger.

## Decision guarantee, and what it does not guarantee

Choose jhat maximizing L_j, including j=0 whose contrast is exactly zero. Deploy only if L_jhat>0, otherwise keep reference. The implementation uses the slightly more conservative threshold 1e-12 to avoid floating-point decisions at zero. On q in C, Delta_j>=L_j for ALL probability tables on these cells, so even data-selected jhat satisfies Delta_jhat>=L_jhat. Thus under the assumptions P(deploy with Delta_jhat<=0)<=alpha. The selection step adds no policy-count factor because the same region covers the whole finite reward table. It does not cover data-dependent partitions, unmodeled context mass uncertainty or arbitrary continuous policies. A finite-sample false-improvement bound is not a promise of high power or global optimality.

This guarantee is an immediate confidence-set implication. We claim neither a new safe-policy theorem nor equivalence to every setting of published safe-learning algorithms. The closest reference implementation in code shares exactly this region and objective, providing a fair equality comparator.

## DR comparison

For independent held-out nuisance predictions h, the paired DR row score is z_i=sum_a d_a(X_i)h(X_i,a) + d_(A_i)(X_i)/mu(A_i|X_i)*(R_i-h(X_i,A_i)), where d=pi-pi_0. With known full propensities and contrast support, its expectation targets the logging-context contrast even if h is incorrect. The implementation uses two-fold smoothed tabular means. Ordinary Wald intervals are diagnostics, not a uniform selection guarantee. They are declined if d is nonzero on a structural missing cell. Known target context weights in the box method do not automatically transport this DR implementation; shift runs expose that distinction.

## Counterexamples and limits

1. **Useful versus separate projection:** q0=.2, q1=.6, missing q2; reference (.6,0,.4), target (0,.6,.4). True contrast .24; independent limiting value difference interval [-.16,.64], joint contrast [.24,.24]. The shared-model robust baseline gives exactly the same answer.
2. **No novelty:** replacing c by p*(pi-pi0) in a box linear program gives exactly this method, for every sample. No benchmark can make two identical objectives different algorithms.
3. **No guaranteed resolution:** logger (.5,.5,0), reference=logger, target (0,.6,.4), q0=.2,q1=.6. Contrast equals -.04+.4q2, so both harmful and beneficial observationally indistinguishable worlds exist.
4. **Confounding failure:** latent U equiprobable, P(A=1|U) in {.1,.9}, q1(U) in {.1,.9}, q0=.6. Nominal treatment propensity .5. Observed treated mean .82 exceeds .6, while causal q1=.5 is worse. A shrinking box around observed means eventually certifies the wrong causal decision.
5. **Shift failure:** q rows (.2,.7),(.8,.4); training masses (.9,.1) versus deployment (.1,.9). A uniform action-0 to action-1 change has old-population gain .41 and deployment loss -.31. Weighting by the wrong population cannot be fixed by a narrower outcome interval.
6. **Conservative power:** Hoeffding ignores low reward variance; rare rewards and many cells can make intervals far wider than a valid variance-adaptive alternative. High-dimensional discretization is not a free extension.

## Complexity and interface

Counting and reward sums: O(n+SK) time, O(SK) aggregation memory; input storage O(n). Confidence box: O(SK). M policies: O(MSK) time and policy memory; a streaming policy loop needs O(SK) working memory. Scalar reference has the same asymptotic complexity. Independent exhaustive vertex checks use 2^(SK) vertices only for tiny test examples; they are not the production calculation. DR adds two fits, score generation O(MnK), and model memory O(SK). Scalability reports must distinguish projection from loading/fitting.

The prototype accepts only logged x/a/r, policy tables, known masses and logger design. Oracle q belongs in simulation/metrics only. There is no hidden access to counterfactual outcomes, no learned trust score and no epsilon replacement for absent support.
