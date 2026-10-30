# Did the Policy Actually Work, or Did It Just Look Like It Did?

**Research dossier for Perceptron, IIT Bombay Techfest — Problem 3**  
**Research cutoff: 28 October 2026**  
Prepared from both supplied research files, primary papers, proceedings, and official dataset/software documentation.

This is a broad, problem-focuse56d literature synthesis, not a claim to enumerate every OPE publication. Established results are distinguished from recent research, proposed experiments, and calculations derived for this report. Exact toy-example numbers below are population calculations, not fabricated experimental results. No Open Bandit experiment was run for this dossier.

## Reading map

1. The problem in plain language
2. What the question actually asks
3. Formal setup and identification
4. Core estimators and their tradeoffs
5. Historical development and research landscape
6. Data, benchmarks, and software
7. Uncertainty and decision rules
8. Hidden confounding and defensible sensitivity analysis
9. Drift, feedback, and practical failure modes
10. Detailed audit of your existing research
11. Recommended hackathon experiments and implementation blueprint
12. Research opportunities, presentation strategy, and reading priorities

## 1. The problem in plain language

A recommendation system decides which product each visitor sees. Its logs tell you whether people clicked **the products it showed**. They do not tell you whether those same people would have clicked different products.

Now somebody proposes a new recommendation rule. You want to estimate how well it would work without deploying it. Averaging the old clicks does not answer this: those clicks came from the old rule. Comparing last month with this month is also misleading if the audience, sale season, or product availability changed.

**Off-policy evaluation (OPE) estimates the average outcome of a new decision rule using outcomes collected under another rule.** It can work when the old system explored the relevant actions and recorded how likely each choice was. It cannot recover arbitrary missing counterfactuals without assumptions.

A simple technique gives more weight to decisions that the new rule would make more often. A more advanced technique, doubly robust estimation, combines that reweighting with outcome predictions. The stretch goals ask how uncertain the answer is and how fragile it becomes if an important cause of both decisions and outcomes was never recorded.

For your hackathon, the central deliverable should be: **“The dashboard says the policy improved performance. A comparison on the same population shows that the policy actually made performance worse.”** Then show the assumptions, evidence, uncertainty, and conditions under which that conclusion changes.

### An exact example you can explain to judges

Suppose half the visitors have low purchase intent and half have high intent. There are two actions: A0 and A1. The current policy gives A1 mostly to high-intent visitors.

| Visitor group | Population share | Current probability of A1 | Success probability with A0 | Success probability with A1 |
|---|---:|---:|---:|---:|
| Low intent | 50% | 10% | 20% | 10% |
| High intent | 50% | 90% | 80% | 70% |

The proposed policy gives A1 to everybody. A1 is actually worse in both groups.

The current policy succeeds with probability:

\[
V(\mu)=0.5(0.9\cdot0.2+0.1\cdot0.1)+0.5(0.1\cdot0.8+0.9\cdot0.7)=0.45.
\]

The proposed policy's value on the **same population in the same period** is:

\[
V(\pi)=0.5(0.1)+0.5(0.7)=0.40.
\]

But the success rate among visitors historically given A1 is:

\[
E[R\mid A=1]=\frac{0.05(0.1)+0.45(0.7)}{0.50}=0.64.
\]

That misleading 64% happens because the old policy mostly gave A1 to people likely to succeed anyway. IPS corrects the imbalance:

\[
E\left[\frac{\mathbf1(A=1)R}{\mu(1\mid X)}\right]
=0.05\frac{0.1}{0.1}+0.45\frac{0.7}{0.9}=0.40.
\]

Now suppose a sale increases every action's success probability by 20 percentage points in the following period. The new policy achieves 60%. A before/after dashboard reports **60% − 45% = +15 percentage points**. Yet keeping the current policy during the sale would achieve 65%. The policy change itself is **−5 percentage points**.

| Quantity | Value | What it means |
|---|---:|---|
| Current policy, original period | 45% | Factual incumbent performance |
| Historical A1-only average | 64% | Selection-biased estimate of assigning A1 to everyone |
| New policy, original conditions | 40% | Counterfactual target of historical-period OPE |
| New policy during sale | 60% | Observed later performance |
| Current policy during sale | 65% | Simulator-only counterfactual benchmark |
| Naive before/after change | +15 pp | Policy change mixed with a better environment |
| Policy effect, holding period fixed | −5 pp | Actual harm caused by changing policies |

These are deliberately simple illustrative probabilities, not realistic e-commerce CTRs. Their purpose is to isolate the causal mechanism. The arithmetic was checked during preparation of this report.

## 2. What the question actually asks

### 2.1 Separate four different questions

| Question | Statistical target | Can ordinary one-step OPE answer it? |
|---|---|---|
| How did the deployed system perform? | Mean observed reward under the logger | Yes; the log average is often appropriate |
| What would another rule have achieved on this historical population? | Counterfactual policy value | Yes, under identification assumptions |
| What is the gain relative to a baseline rule? | Difference in policy values on the same population | Yes, often using paired estimates |
| What happens after deployment changes users and future states? | Long-run intervention value | Generally requires sequential or structural modeling |

The log average is not inherently a bad metric. It is wrong when presented as the value of a different policy. Likewise, an observed increase is real as a descriptive fact; its attribution to the policy may be wrong.

Three “naive” estimators in your attachments should be named separately:

- **Logger average:** mean reward across every logged row.
- **Action-matched average:** mean reward among rows whose action agrees with a deterministic target policy.
- **Before/after difference:** later mean minus earlier mean.

The first answers the incumbent-performance question; the second can select a different context distribution; the third mixes policy and time effects. Replacing a stochastic target policy by its argmax changes the policy being evaluated.

### 2.2 Why ordinary supervised evaluation is insufficient

A random train/test split of the incumbent's data retains the incumbent's action-selection mechanism. Excellent prediction on that test set need not imply accurate predictions for actions the target policy favors. Missing outcomes are not negative outcomes: an unshown item is not a “no click.”

The causal framing of learning systems was developed explicitly in computational advertising by Bottou and colleagues. Recommendation research also treats exposure and rating selection as mechanisms that require correction. [Bottou et al., 2013](https://jmlr.org/papers/v14/bottou13a.html); [Schnabel et al., 2016](https://proceedings.mlr.press/v48/schnabel16.html).

### 2.3 Match the hackathon requirements precisely

The minimum asks for a standard estimator and a concrete difference from a naive before/after number. A filtered-action average alone demonstrates a related problem, but does not literally implement a temporal before/after comparison. Use the two-period synthetic example for that requirement and a real-data OPE benchmark for external credibility.

The estimator should only see current-policy logs. Simulator ground truth and target-policy validation logs belong to a separate evaluator. Showing hidden truth afterward is legitimate benchmarking; using it to train or tune the estimator is leakage.

## 3. Formal setup and identification

### 3.1 Contextual bandits and potential outcomes

For observation \(i\):

- \(X_i\): context measured before choosing the action;
- \(A_i\in\{0,\ldots,K-1\}\): selected action;
- \(R_i(a)\): potential reward under action \(a\);
- \(R_i=R_i(A_i)\): observed reward;
- \(\mu(a\mid x)\): behavior/logging policy;
- \(\pi(a\mid x)\): fixed target policy;
- \(p_i=\mu(A_i\mid X_i)\): propensity of the action actually selected.

The data are \(D=\{X_i,A_i,R_i,p_i\}_{i=1}^n\). For a specified context population \(P_X\), define:

\[
q(x,a)=E[R(a)\mid X=x],\qquad
V_{P_X}(\pi)=E_{X\sim P_X}\left[\sum_a\pi(a\mid X)q(X,a)\right].
\]

This is a population-average counterfactual. It does not recover what would have happened to each particular individual. Define improvement as \(\Delta=V(\pi)-V(\pi_0)\), with the same reward, population, and horizon in both terms.

For binary actions, the ATE is \(E[R(1)-R(0)]\). A policy-value contrast is more general:

\[
\Delta=E_X\sum_a[\pi(a\mid X)-\pi_0(a\mid X)]q(X,a).
\]

Potential-outcome reasoning predates modern bandits; Rubin's work is a foundational reference. [Rubin, 1974](https://dash.harvard.edu/entities/publication/73120378-82c0-6bd4-e053-0100007fdf3b).

### 3.2 The assumptions that make the question answerable

**Consistency and well-defined interventions.** The logged reward equals the potential reward under the chosen action. “Show product A” must mean the same intervention across training and deployment. Position, price, eligibility, and surrounding recommendations may be part of the treatment.

**Conditional exchangeability.** For each action, \(R(a)\perp A\mid X\). This concerns potential outcomes, not the assertion that observed reward is independent of action. If human operators used unrecorded information to choose actions, exchangeability given the stored context may fail.

**Overlap.** Wherever the target assigns positive probability, the logger must also assign positive probability. Practical overlap needs sufficiently frequent observations, not merely a mathematically positive probability. If the old system always showed electronics, arbitrary book recommendations are not nonparametrically identifiable from those logs alone.

**Appropriate sampling and stability.** Simple formulas below assume independent observations and a fixed environment. Repeated users, adaptive policies, delayed outcomes, and drift require changes to the analysis. No-interference is a separate causal requirement: one user's action should not change another user's reward in an unmodeled way.

**Valid propensity information.** A model score is not necessarily a probability. A softmax probability before business-rule filtering may not be the probability of the final served action. Record the actual sampling probability after all eligibility and selection logic.

### 3.3 A useful nuance: missing features need not invalidate exact logged probabilities

If the logger uses an unrecorded variable \(U\), but logs the **actual randomized assignment probability** \(\mu(A\mid X,U)\), IPS can still cancel assignment conditional on \((X,U)\), assuming that conditioning set is sufficient, overlap holds, and the target depends only on available context. Merely omitting \(U\) from the analysis does not automatically make these exact weights wrong.

The problematic case is using the observed-context marginal \(P(A\mid X)\), an incorrect propensity, or a deterministic decision when outcomes and actions share hidden causes. Your hidden-confounding simulation must distinguish those cases. This follows directly by conditioning the importance-weighting identity on \((X,U)\).

### 3.4 Adaptive loggers and action availability

A learning logger has probabilities \(p_t=\mu_t(A_t\mid X_t,H_{t-1})\), where \(H_{t-1}\) is its history. Save the probability used **at the time of the action**. A final policy snapshot or overall action frequency generally cannot replace it.

If action sets vary, record the eligible set \(\mathcal A_i\), and require the target to assign zero probability to unavailable actions. Evaluating a target that would change candidate generation requires additional coverage analysis. Adaptive OPE inference has dedicated theory; treating such data as IID is not automatically valid. [Waudby-Smith et al., anytime-valid inference](https://arxiv.org/abs/2210.10768).

## 4. Core estimators and their tradeoffs

Write \(w_i=\pi(A_i\mid X_i)/p_i\), and \(\hat q_i^\pi=\sum_a\pi(a\mid X_i)\hat q(X_i,a)\).

### 4.1 Direct method: predict all relevant action outcomes

\[
\hat V_{DM}=\frac1n\sum_i\hat q_i^\pi.
\]

Train an outcome model on observed context-action-reward triples. Suitable starting points are logistic regression for binary outcomes and a tree-based model for nonlinear relationships. Include action-context interactions or use separate action models where sample sizes permit.

DM avoids large importance weights, but it can confidently extrapolate into regions with little data. Predictive calibration under the logging distribution is necessary evidence, not proof of counterfactual calibration. Lack of overlap remains an identification problem even when a model produces a number.

### 4.2 IPS/IPW: correct the action distribution

\[
\hat V_{IPS}=\frac1n\sum_iw_iR_i.
\]

The weighting principle has roots in unequal-probability sampling. [Horvitz and Thompson, 1952](https://www.stat.cmu.edu/~brian/905-2008/papers/Horvitz-Thompson-1952-jasa.pdf).

Under valid identification and known probabilities, the cancellation is:

\[
E[wR\mid X=x]=\sum_a\mu(a\mid x)\frac{\pi(a\mid x)}{\mu(a\mid x)}q(x,a)
=\sum_a\pi(a\mid x)q(x,a).
\]

Thus IPS is finite-sample unbiased for a fixed target under the stated sampling setup, not merely “asymptotically unbiased.” Estimated propensities generally remove that exact finite-sample guarantee.

Why variance can explode: with conditional outcome variance \(\sigma^2(x,a)\), the IID variance decomposes as

\[
\operatorname{Var}(\hat V_{IPS})=\frac1n\left\{E[w^2\sigma^2(X,A)]+\operatorname{Var}[wq(X,A)]\right\}.
\]

A few rare target-compatible actions can dominate both terms. A formally unbiased estimator can be practically unreliable. The minimax analysis of Wang et al. explains why this difficulty is fundamental rather than just an implementation defect. [Wang et al., 2017](https://proceedings.mlr.press/v70/wang17a.html).

### 4.3 SNIPS: normalize the weights

\[
\hat V_{SNIPS}=\frac{\sum_iw_iR_i}{\sum_iw_i}.
\]

With nonnegative weights and a positive denominator, the result lies within the observed reward range. It is a ratio estimator: usually biased in finite samples and consistent under suitable conditions. It often improves stability, but lower variance is not a universal theorem. A zero denominator means no matched support in that sample, not a value of zero.

Self-normalization also matters in policy learning, where optimizing a raw IPS objective can exploit estimation artifacts. [Swaminathan and Joachims, 2015, self-normalized learning](https://papers.nips.cc/paper/2015/hash/39027dfad5138c9ca0c474d71db915c3-Abstract.html).

### 4.4 Doubly robust estimation: prediction plus weighted correction

\[
\hat V_{DR}=\frac1n\sum_i\left[\hat q_i^\pi+w_i\{R_i-\hat q(X_i,A_i)\}\right].
\]

The prediction supplies a baseline; the weighted residual corrects its errors. Dudík, Langford, and Li established this approach for contextual-bandit evaluation and learning. A later expanded treatment analyzes policy evaluation and optimization. [Dudík et al., 2011](https://arxiv.org/abs/1103.4601); [expanded treatment](https://arxiv.org/abs/1503.02834).

Here is the useful algebra, conditional on nuisance models fitted independently of evaluation observations. If \(\tilde\mu\) and \(\tilde q\) are their probability and reward limits, the bias term is

\[
E_X\sum_a\pi(a\mid X)
\left(1-\frac{\mu(a\mid X)}{\tilde\mu(a\mid X)}\right)
[\tilde q(X,a)-q(X,a)].
\]

If either nuisance is correct, this product is zero. This is the reason for “double robustness.” It is not robustness to hidden confounding, missing support, incorrect target-policy probabilities, or a changed environment.

When both nuisance models converge sufficiently well, DR can attain favorable asymptotic efficiency. Consistency under one correct nuisance is weaker than valid root-n confidence intervals: the latter needs additional convergence-rate and moment conditions. Neither DR nor SNIPS is uniformly best in finite samples. DR can produce estimates outside the reward range; silently clipping the final answer changes the estimator.

### 4.5 Cross-fitting: protect the correction from overfitting

For IID data, split rows into K folds, fit nuisance models on K−1 folds, and compute scores only on the held-out fold. Pool the held-out scores. Use group splits for repeated users and a justified temporal design for dependent or adaptive logs.

Cross-fitting reduces dependence between fitted predictions and their own residuals. It does not remove confounding or create action coverage. For flexible nuisance estimates, orthogonal scores plus sample splitting underpin modern debiased inference. A common sufficient condition is that the product of appropriate nuisance estimation errors is \(o_p(n^{-1/2})\), together with overlap and regularity. [Chernozhukov et al., double/debiased machine learning](https://arxiv.org/abs/1608.00060).

Keep target-policy learning separate: use training data to learn the candidate, validation data to choose settings, and untouched evaluation data to report final value. Cross-fitting an outcome model alone does not eliminate policy-selection optimism.

### 4.6 Clipping, switching, and shrinkage

**Clipped IPS:** replace \(w\) by \(\min(w,c)\). This limits variance but introduces bias. With rewards in \([0,1]\) and exact weights, its population bias relative to IPS is nonpositive. That special direction does not automatically carry over to clipped DR residuals.

**Switch-DR:**

\[
\hat V_{Switch}=\frac1n\sum_i[\hat q_i^\pi+\mathbf1(w_i\le\tau)w_i(R_i-\hat q_i)].
\]

Large weights trigger reliance on the model. Small thresholds approach DM; an infinite threshold gives DR. [Wang et al., 2017](https://proceedings.mlr.press/v70/wang17a.html).

**Optimistic DR shrinkage:** a studied form uses \(\tilde w=\lambda w/(w^2+\lambda)\) in the correction, interpolating toward DM as \(\lambda\to0\) and DR as \(\lambda\to\infty\). The framework optimizes a bound on MSE; it does not guarantee that any shrinkage choice improves every dataset. [Su et al., 2020](https://proceedings.mlr.press/v119/su20a.html).

**MRDR:** fit the nuisance model for the variance of the DR objective rather than ordinary prediction loss. This targets the downstream statistical task but adds optimization and tuning complexity. [Farajtabar et al., 2018](https://proceedings.mlr.press/v80/farajtabar18a).

For the hackathon, implement DM, IPS, SNIPS, and cross-fitted DR first. Add one stabilization method only after diagnostics show a reason. Tune thresholds without consulting final benchmark truth.

| Method | Main advantage | Main failure mode | Essential reporting |
|---|---|---|---|
| DM | Simple predictions, often stable | Misspecification and unsupported extrapolation | Held-out calibration and support |
| IPS | Transparent, exact weighting identity | Rare actions create high variance | Propensities and weight distribution |
| SNIPS | Bounded weighted average | Ratio bias, no-match denominator | Weight sum and ESS |
| DR | Corrects a model using observed residuals | Bad nuisances, overlap, leakage | Cross-fitting and score variability |
| Clipped/Switch/DR shrinkage | Controls influential weights | Bias from stabilization | Tuning rule and sensitivity sweep |

## 5. Historical development and research landscape

### 5.1 Foundations and the contextual-bandit era

The field combines several research traditions rather than starting with one ML paper:

| Period | Representative contribution | Relevance to your problem |
|---|---|---|
| 1952 | Horvitz–Thompson unequal-probability estimation | Reweight selective observations |
| 1974 | Rubin's potential-outcome framing | State the missing counterfactual explicitly |
| 1994 | Robins–Rotnitzky–Zhao missing-data semiparametric methods | Roots of augmented weighting and robust estimation |
| 2011 | Li et al. replay evaluation | Evaluate bandit policies using randomized logged actions |
| 2011–2014 | Dudík et al. contextual-bandit DR | Combine reward and assignment models |
| 2013 | Bottou et al. causal reasoning in advertising | Define interventions in deployed learning systems |
| 2015 | CRM/POEM and self-normalization | Control variance when learning from logged feedback |
| 2016–2020 | Recommendation debiasing, SWITCH, MRDR, shrinkage | Address selection bias and finite-sample instability |
| 2021 onward | Public OPE benchmarks, inference, estimator selection | Test whether estimates and decisions are trustworthy |

Historical references: [Robins et al., 1994](https://www.tandfonline.com/doi/abs/10.1080/01621459.1994.10476818); [Li et al., replay](https://arxiv.org/abs/1003.5956); [CRM/POEM](https://proceedings.mlr.press/v37/swaminathan15.html). The other foundational sources are linked in Sections 2–4. Avoid describing the 1994 paper as if it introduced today's contextual-bandit DR algorithm.

Replay accepts events where the evaluation algorithm agrees with randomized logged actions. Under the appropriate logging design, accepted events can represent target-policy operation. Arbitrary filtering under a context-dependent logger is not equivalent to unbiased replay.

### 5.2 Recommendation, exposure bias, and feedback loops

Schnabel et al. treat recommendation exposure as treatment assignment, correcting biased learning and evaluation. Chaney et al. simulate repeated recommendation and retraining, showing how algorithmically generated data can change apparent preferences and population behavior. Their findings motivate the problem statement, but a one-step estimator does not automatically solve the resulting long-term dynamics. [Recommendations as Treatments](https://proceedings.mlr.press/v48/schnabel16.html); [Chaney et al., 2018](https://arxiv.org/abs/1710.11214).

Practical implication: distinguish **selection of observations today** from **a policy changing future preferences or states**. Only the former fits a static contextual-bandit model without further assumptions.

### 5.3 Large action spaces and embeddings

If there are thousands of possible products, very few logged events support a particular target recommendation. Marginalized IPS instead weights action embeddings, borrowing information across related actions. Validity depends on assumptions about whether embeddings capture reward-relevant action differences; learned similarity alone is not sufficient. [Saito and Joachims, 2022](https://proceedings.mlr.press/v162/saito22a.html).

OffCEM decomposes effects into action-cluster effects and residual effects, weighting at cluster level and modeling residual differences. Its local-correctness condition differs from ordinary DR assumptions. Learned embeddings and marginalized DR are related follow-ups. [OffCEM, 2023](https://arxiv.org/abs/2305.08062); [learned action embeddings](https://arxiv.org/abs/2305.03954).

These methods exchange variance for structural assumptions. They do not contradict the impossibility of identifying unsupported actions without extra information.

### 5.4 Slates, rankings, and candidate generation

Showing three items together is a joint action. Clicking the middle item may depend on its neighbors and on whether earlier items were examined. Joint slate probabilities can be extremely small. Position-wise, cascade, additive-reward, and abstraction-based estimators use different assumptions to reduce complexity.

Slate abstraction learns or chooses a lower-dimensional representation of the joint action for evaluation. It is relevant to multi-slot interfaces, but requires a stronger modeling discussion than a single-action bandit. [Kiyohara et al., WWW 2024](https://arxiv.org/abs/2402.02171).

Changing a candidate generator creates another support boundary: an item excluded before ranking has no serving probability under the old system. Recent work addresses OPE of candidate generators explicitly. [RecSys 2025 primary paper](https://assets.amazon.science/c4/f9/66932e364785bdf271d0fb867408/scipub-approval152129-37504163-offpolicy-evaluation-of-candidate-generators-in-twostage-recommender-systems.pdf).

### 5.5 Sequential decisions and long-horizon evaluation

In an MDP, today's action changes tomorrow's state. The target is often \(E_\pi[\sum_{t=0}^{H-1}\gamma^tR_t]\). Trajectory importance weights multiply \(\pi(A_t\mid S_t)/\mu(A_t\mid S_t)\) across time and can become unstable with horizon.

Important branches include:

- Sequential DR and weighted estimators: extend correction methods to trajectories. [Jiang and Li, 2016](https://proceedings.mlr.press/v48/jiang16.html).
- Fitted Q evaluation: learn target-policy value functions through Bellman regression; validity depends on coverage and function approximation.
- Marginal state/state-action density ratios: replace full trajectory products when Markov structure permits.
- Double reinforcement learning: combine marginalized ratios and value models with efficiency theory. [Kallus and Uehara, 2020](https://jmlr.org/beta/papers/v21/19-827.html).
- DICE methods: learn stationary distribution corrections through optimization. DualDICE is a central example. [Nachum et al., 2019](https://arxiv.org/abs/1906.04733).

A broad statistical overview is [Uehara, Shi, and Kallus, 2022](https://arxiv.org/abs/2212.06355). These methods are useful context; adding full RL to a one-step hackathon solution would substantially increase validation work.

### 5.6 Continuous actions

For prices, dosages, or bid amounts, a deterministic target may choose a value that has probability zero under a continuous logger. Density-ratio weighting works for appropriately supported stochastic target distributions; deterministic targets commonly require smoothing and smoothness assumptions. Kernel approaches exploit nearby treatments at the cost of bandwidth-dependent bias. [Kallus and Zhou, 2018](https://proceedings.mlr.press/v84/kallus18a.html).

### 5.7 Distributional OPE and risk-aware policy selection

The mean can hide a disastrous lower tail. Distributional OPE estimates a reward or return CDF and functions such as quantiles and CVaR. This introduces its own assumptions and uncertainty. [Huang et al., 2021](https://arxiv.org/abs/2104.08977).

OPE can also be evaluated by the quality of policies it selects, not only estimation error. The ICLR 2024 risk-return benchmark introduces SharpeRatio@k for assessing selected policy sets. It is distinct from a confidence interval for a single mean. [Kiyohara et al., 2024](https://arxiv.org/abs/2311.18207).

### 5.8 Estimator selection is itself a learning problem

You cannot choose whichever estimator gives the highest value and call it the most accurate. PAS-IF constructs pseudo-policy evaluation tasks by subsampling available logs to guide estimator selection. It addresses the lack of ground-truth estimator error on the actual task. [Udagawa et al., AAAI 2023](https://arxiv.org/abs/2211.13904).

For your project, predeclare a primary estimator and display alternatives as diagnostics. Disagreement is information about instability, not permission to select the most flattering answer.

### 5.9 Developments located in the 2025–October 2026 search

This is a focused frontier update. Recent abstracts establish research directions, not a basis for claiming a new method is universally superior.

| Work and verified status | Main direction | Practical implication |
|---|---|---|
| Ryu et al., COLT 2025 | Betting-based confidence bounds and freezing objectives for selection/learning | Confidence-aware selection remains an active topic. [Paper](https://proceedings.mlr.press/v291/ryu25a.html) |
| DOLCE, 2025 preprint revised February 2026 | Lagged contexts and residual invariance to address support limitations | Extra temporal structure is an assumption, not free coverage. [Paper](https://arxiv.org/abs/2505.00961) |
| Guo and Xu, June 2026 preprint | Inference when adaptive contextual-bandit working models are misspecified | Adaptive logging can invalidate naive normal approximations. [Paper](https://arxiv.org/abs/2606.22639) |
| Cross-Domain OPE/L, July 2026 arXiv posting; page reports ICLR 2025 acceptance | Combine source-domain and target-domain logs | Requires extra datasets and transport assumptions; outside a strict single-log MVP. [Paper](https://arxiv.org/abs/2607.22012) |
| Jajoo, September 2026 preprint | Exponential difficulty in a history-dependent POMDP construction | Marginal action coverage alone need not make long-horizon evaluation easy. [Paper](https://arxiv.org/abs/2609.19135) |
| Xiang et al., October 2026 preprint; page reports NeurIPS 2026 acceptance | Allocate costly/noisy counterfactual annotations from multiple sources | An extension using additional evidence, not pure logged-data OPE. [Paper](https://arxiv.org/abs/2610.10974) |

Publication status in the last two “page reports” entries is author-reported arXiv metadata, not independently verified proceedings acceptance. This report does not rely on the numerical performance claims in those abstracts. An LLM-generated counterfactual label is a model-dependent annotation, never automatically ground truth.

## 6. Data, benchmarks, and software

### 6.1 Recommended data strategy

Use **a controlled synthetic benchmark as the primary proof of correctness**, followed by **Open Bandit Dataset as a real-world validation**. They answer different questions: simulation gives exact counterfactual truth and controlled violations; real logs expose realistic reward sparsity, action imbalance, and preprocessing issues.

| Data source | Strength | Limitation | Recommended role |
|---|---|---|---|
| Custom synthetic bandit | Known potential-outcome means, propensities, and causal structure | Conclusions depend on the simulated mechanisms | Primary MVP and both stretch goals |
| Open Bandit Dataset | Real recommendation logs, probabilities, two deployed policies | Reference outcomes only for deployed policies; multiple positions | Real-world validation |
| Yahoo! randomized news logs/replay setting | Classic randomized bandit evaluation design | Access, schema, candidate sets, and historical availability require checking | Background or alternative |
| Supervised-to-bandit conversion | Full labels permit counterfactual reward construction | Often unrealistic action effects and noise | Fast estimator stress testing |
| Sequential simulation/RL benchmarks | Evaluate multi-step policies and rankings | Much larger modeling scope | Future extension |

For supervised conversion, a common construction sets reward to one when an action equals the known class label. Retain all labels only in the evaluator and expose only the sampled action's reward to the estimator. This is a test of estimation, not evidence about real human behavior.

### 6.2 What Open Bandit Dataset actually provides

ZOZO's official release describes approximately 26 million records collected during an A/B test of Random and Bernoulli Thompson Sampling policies. Fields include timestamps, items, recommendation positions, clicks, propensities, anonymized user features, and affinity features. The dataset supports three campaigns. [Official data release](https://research.zozo.com/data.html).

The published benchmark reports 80 supported items for ALL, 34 for Men's, and 46 for Women's, with three display positions. Rounded ALL-campaign CTRs are 0.35% for Random and 0.50% for Bernoulli TS. These are **empirical on-policy references with sampling error**, not exact population constants or individual counterfactual labels. The paper also finds substantial dependence of estimator performance on experimental setting and reward-model choice. [Saito et al., NeurIPS 2021](https://arxiv.org/html/2008.07146v5).

The official dataset card currently exposes a full-size download and points to a smaller example in the OBP repository. It labels the data CC BY 4.0. Preserve attribution and check the actual downloaded release's terms; do not paraphrase the license as simply “noncommercial only.” This report does not perform a legal interpretation. [Official dataset card](https://huggingface.co/datasets/zozonext/open-bandit/blob/main/README.md).

### 6.3 Real-data experimental protocol

1. Pick one campaign and define whether the unit is a slot impression, a slate, or a user/session. Use the same definition throughout.
2. Begin with a fixed position if implementing a one-action estimator. Explicitly assume the outcome model does not require unmodeled interactions with other displayed items, or describe the result as a position-wise approximation.
3. Use one policy's log as estimation data and the other's observed reward as a held-out reference for that deployed policy.
4. Reproduce target probabilities using the benchmark's documented policy-replication procedure; for Thompson Sampling, do not substitute empirical click rates or an unrelated freshly trained policy.
5. Align campaign, time window, reward definition, position, and eligible action set.
6. Fit reward models only on estimation/training data, with appropriate splitting. Keep target reference rewards outside estimator fitting and hyperparameter selection.
7. Report uncertainty in both OPE and the on-policy reference; compare a difference with its uncertainty rather than treating the reference as error-free.
8. Repeat for multiple sample sizes and both policy directions where feasible.

**Important implementation details:** derive action counts from loader metadata and unique supported IDs rather than the largest raw ID; map IDs consistently; inspect whether positions are one- or zero-indexed; use probabilities for the same event as the target numerator; inspect the distribution of clicks before training per-action models.

With an 80-action uniform logger and a deterministic target, only about one in 80 rows matches the target. Ignoring other structure, ESS is then roughly \(n/80\), even though all matching weights equal 80. Full support does not imply high precision. Estimating a diffuse target from a concentrated logger can be especially difficult, but the actual difficulty must be measured from weights and rewards.

Do not infer exact truth for an arbitrary learned policy from the Random or TS CTR. Those references only validate the corresponding deployed policies under the matched benchmark setup.

### 6.4 Software choices

**Open Bandit Pipeline (OBP)** supplies data loaders, synthetic generators, policy learners, regression utilities, and OPE estimators. Its repository is a useful reference implementation. Dependency versions should be checked in the actual package metadata and pinned; this research task did not install or test OBP locally. [Official repository](https://github.com/st-tech/zr-obp).

**SCOPE-RL** covers offline RL, OPE, policy selection, confidence intervals, distributional evaluation, and simulation environments. Use it if you deliberately extend into sequential decisions. [Official repository](https://github.com/hakuhodo-technologies/scope-rl).

For a transparent MVP, a small NumPy/scikit-learn implementation of the four basic estimators is enough. Libraries save integration time, but neither a library result nor a bootstrap function certifies that the causal assumptions hold.

## 7. Uncertainty and decision rules

### 7.1 Separate uncertainty from systematic error

A confidence interval usually describes repeated-sample uncertainty under a specified model and sampling design. It does not automatically include hidden confounding, unsupported actions, future drift, reward misspecification, or leakage. Increasing n can make a biased answer look increasingly certain.

### 7.2 Influence-score intervals for a fixed policy

For IID observations with justified nuisance estimation, use per-row scores:

\[
Z_i^{IPS}=w_iR_i,\qquad
Z_i^{DR}=\hat q_i^\pi+w_i(R_i-\hat q_i).
\]

The basic asymptotic standard error is

\[
\widehat{SE}(\hat V)=\frac{s_Z}{\sqrt n},\qquad
CI_{95\%}=\hat V\pm1.96\widehat{SE}(\hat V).
\]

This is an approximation with finite-moment, nuisance-rate, and sampling assumptions. Rare events and extreme weights can make it poor. Cross-fitting helps justify the score construction but does not guarantee a good normal approximation.

For SNIPS, use a ratio-estimator influence contribution approximately

\[
\hat\phi_i=\frac{w_i(R_i-\hat V_{SNIPS})}{\bar w}.
\]

Use its empirical variance for the standard error. Applying the IPS standard-error formula unchanged to SNIPS is incorrect.

### 7.3 Estimate improvement directly

For two fixed policies evaluated on the same rows, construct \(D_i=Z_i^\pi-Z_i^{\pi_0}\). Then

\[
\hat\Delta=\bar D,\qquad \widehat{SE}(\hat\Delta)=s_D/\sqrt n.
\]

This retains covariance between estimates. Overlap or non-overlap of two separate CIs is not the right general test of policy improvement.

When the baseline is the factual mean reward of the actual current logger, use \(D_i=Z_i^\pi-R_i\), provided both refer to the same population and period. If the baseline itself is another hypothetical policy, evaluate it as such. Under hidden confounding, an X-only stochastic policy matching marginal action frequencies need not equal the original logger that used U.

### 7.4 Bootstrap

For independent rows, resample rows and recompute the estimator. For dependent data, resample the appropriate unit: users, sessions, independent episodes, or justified time blocks. Resampling individual slots from a shared slate can break dependencies.

Two workflows answer different inferential questions:

- **Full-pipeline bootstrap:** refit nuisance models and repeat the splitting procedure; more expensive and still dependent on estimator regularity.
- **Score bootstrap:** resample already computed held-out scores; fast, and appropriate as an asymptotic approximation only when nuisance contributions are negligible under the relevant theory.

If the policy is selected or retrained in each repetition, explicitly decide whether the target is a fixed policy's value or the performance of a learning procedure. A bootstrap that accidentally mixes these targets is difficult to interpret.

Use enough bootstrap repetitions for stable quantiles, and test sensitivity to the count. More repetitions reduce Monte Carlo error in the bootstrap calculation; they do not fix invalid resampling or lack of coverage. A model-based OPE bootstrap is a distinct literature, not a universal guarantee for arbitrary resampling. [Hanna et al., 2017](https://arxiv.org/abs/1606.06126).

### 7.5 High-confidence and anytime-valid alternatives

High-confidence OPE develops bounds appropriate to conservative policy decisions. [Thomas et al., 2015](https://ojs.aaai.org/index.php/AAAI/article/view/9541). Self-normalized finite-sample bounds and empirical likelihood provide alternatives to simple Wald intervals. [Kuzborskij et al., 2021](https://proceedings.mlr.press/v130/kuzborskij21a/kuzborskij21a.pdf); [Karampatziakis et al., 2020](https://proceedings.neurips.cc/paper/2020/hash/6d34d468ac8876333c4d7173b85efed9-Abstract.html).

A concentration bound requiring a deterministic maximum weight cannot simply use the largest observed weight as a guaranteed bound on all possible weights. Clipping may make a bound applicable to a clipped estimand, but bias relative to the original policy value still needs treatment.

For repeated monitoring and data-dependent stopping, confidence sequences provide time-uniform inference. Repeatedly checking a conventional 95% interval until it becomes favorable does not retain the nominal guarantee. [Off-Policy Confidence Sequences, 2021](https://proceedings.mlr.press/v139/karampatziakis21a/karampatziakis21a.pdf); [Waudby-Smith et al.](https://arxiv.org/abs/2210.10768).

### 7.6 Diagnostics that should accompany every estimate

\[
ESS=\frac{(\sum_iw_i)^2}{\sum_iw_i^2}.
\]

Report n, ESS, ESS/n, number of clicks, target-action match count, minimum positive logged propensity, weight quantiles, maximum weight, mean weight, and the fraction of total weight carried by the largest observations. Under the standard identity, mean weight should approach one; a discrepancy can reflect sampling noise, support problems, or incorrect probabilities.

ESS is a weight-concentration diagnostic, not a theorem that an interval is valid. High ESS does not rule out confounding. Low ESS does not imply every conservative interval is too narrow. No universal ESS cutoff certifies a safe decision.

Also inspect reward-model calibration, influential score contributions, group-specific support, and sensitivity to clipping. Plot both weights and weighted residuals: DR uncertainty is driven by the latter as well as by predicted target values.

### 7.7 Validate coverage honestly

On synthetic data, generate many **independent datasets** from the same data-generating process. For each, fit the full pipeline and record whether its interval contains the exact population target. Report coverage, width, bias, RMSE, and Monte Carlo uncertainty of coverage itself.

If M independent repetitions produce estimated coverage \(\hat c\), a rough Monte Carlo SE is \(\sqrt{\hat c(1-\hat c)/M}\). With 200 repetitions near 95% coverage, this is about 1.5 percentage points. Small departures from 95% may be simulation noise.

Repeated bootstrap samples from a single real log are not equivalent to independent sampling from the real deployment process. Real-data calibration against an independent on-policy reference is valuable, but should not be presented as exact coverage against known population truth.

## 8. Hidden confounding and defensible sensitivity analysis

### 8.1 What hidden confounding changes

Suppose an unrecorded user-intent variable U influences both action assignment and reward. Then \(E[R\mid X,A=a]\) may differ from \(E[R(a)\mid X]\). A very accurate predictive outcome model may still be causally wrong.

Without additional assumptions, more logged data does not resolve this ambiguity. Sensitivity analysis asks how conclusions change over a specified set of plausible hidden-bias mechanisms. It does not estimate or eliminate the hidden confounder.

Kallus and Zhou study policy improvement robust to a set of confounded assignment weights, relative to a baseline. Their infinite-horizon extension addresses a different sequential setting. [2018 policy improvement](https://arxiv.org/abs/1805.08593); [2020 sequential evaluation](https://papers.nips.cc/paper/2020/hash/fd4f21f2556dad0ea8b7a5c04eabebda-Abstract.html).

### 8.2 Define Gamma correctly

For binary actions, let \(e(x)=P(A=1\mid X=x)\) be the nominal marginal propensity and \(e^*(x,u)=P(A=1\mid X=x,U=u)\) the full propensity. A marginal sensitivity model assumes:

\[
\frac1\Gamma\le
\frac{e^*(x,u)/(1-e^*(x,u))}{e(x)/(1-e(x))}
\le\Gamma,\qquad\Gamma\ge1.
\]

Gamma bounds an **odds ratio**, not an additive percentage-point change or a multiplier on policy value. Gamma=1 recovers the no-hidden-assignment-bias case within this model, assuming U is sufficient for exchangeability. Rosenbaum's pairwise matched-unit model is related but is not identical to this nominal-versus-full propensity model.

Solving the inequalities gives:

\[
\frac{e}{e+\Gamma(1-e)}\le e^*\le
\frac{\Gamma e}{1-e+\Gamma e}.
\]

For treated observations, the inverse propensity lies between

\[
\ell=1+\frac{1/e-1}{\Gamma},\qquad
h=1+\Gamma(1/e-1).
\]

Consequently, multiplying a DR estimate by Gamma and dividing it by Gamma is **not a derivation of sensitivity bounds**. Likewise, the box \([w/\Gamma,\Gamma w]\) is not the exact odds-model weight interval. The marginal model and compatibility constraints are developed in [Dorn and Guo](https://arxiv.org/html/2102.04543v3).

### 8.3 A simple, mathematically explicit stretch-goal implementation

Use binary rewards, binary actions, and a small number of discrete context strata. Evaluate the target “give action 1 to everyone.” This restriction makes a valid illustrative sensitivity calculation manageable.

Within stratum x, let \(m=P(R=1\mid A=1,X=x)\). Let \(z_1\) and \(z_0\) be average inverse full-propensity weights among treated successes and failures. The bounds imply \(\ell\le z_1,z_0\le h\), while normalization requires:

\[
e[mz_1+(1-m)z_0]=1.
\]

The counterfactual success probability is \(q_1=e m z_1\). Eliminating \(z_0\) yields the following population interval for that treated potential-outcome mean:

\[
L_x=\max\{em\ell,\;1-e(1-m)h\},
\]

\[
U_x=\min\{emh,\;1-e(1-m)\ell\}.
\]

Average endpoints using the target population's stratum probabilities: \(L=\sum_xP(x)L_x\), \(U=\sum_xP(x)U_x\). This is an elementary derivation for the restricted binary, single-potential-outcome setting from the odds and normalization constraints. It is not a general multi-action DR sensitivity estimator, nor a claim of joint sharpness for arbitrary policy contrasts.

For finite data, plug-in values of e, m, and stratum frequencies are **estimated bound endpoints**, not automatically confidence limits. Sparse cells and max/min boundary points need inferential care. If reliable interval inference is beyond scope, present these as a sensitivity analysis and keep the point-estimation CI separately labeled.

Applied to Section 1's exact observed population probabilities:

| Gamma | Lower target value | Upper target value |
|---:|---:|---:|
| 1.00 | 40.00% | 40.00% |
| 1.25 | 38.725% | 41.425% |
| 1.50 | 37.75% | 42.75% |
| 2.00 | 36.25% | 45.25% |
| 3.00 | 34.667% | 50.00% |

These endpoints were calculated from the displayed formulas. The original toy generator is unconfounded; this table asks which other counterfactual values could be compatible with the same observations under allowed hidden assignment bias. At Gamma=1.5, the entire interval remains below the factual incumbent's 45%. At Gamma=2, that harm conclusion is no longer established by this sensitivity set alone. Sampling uncertainty is absent from this population illustration.

### 8.4 General sensitivity methods and sharpness

For continuous covariates and outcomes, naive independent weight boxes ignore compatibility constraints. Conditional moment or quantile-balancing restrictions can tighten the region. A bound is **sharp** if it describes the smallest range compatible with the stated observed distribution and assumptions; a conservative outer bound can still be useful if labeled correctly.

Dorn and Guo develop quantile balancing; Dorn, Guo, and Kallus develop doubly valid/doubly sharp sensitivity estimators; Ishikawa and He use kernel conditional moment constraints for confounding-robust policy evaluation. [Doubly valid/doubly sharp analysis](https://arxiv.org/abs/2112.11449); [Ishikawa and He, AISTATS 2023](https://proceedings.mlr.press/v206/ishikawa23a.html).

For binary targets other than always-1, formulate the corresponding control-arm and policy-value problem. For general K-action policies, use an explicitly multi-action sensitivity model with coherent probabilities; independently perturbing each action's probability can violate the requirement that probabilities sum to one.

### 8.5 Interpret the sensitivity plot correctly

If claiming improvement, report the smallest Gamma at which the **lower bound on improvement** crosses zero. If claiming harm, inspect when the **upper bound on improvement** reaches zero. If testing many policies or Gamma thresholds for a formal decision, account for that selection.

Compare candidates and baseline under a shared uncertainty set when both are counterfactual policies. Separately optimized endpoint differences can be conservative and may not be sharp. Include sampling uncertainty before making a confidence-qualified robustness statement.

Gamma is chosen by the analyst or domain knowledge, not identified from the observational data alone. Benchmarking against omission of important observed covariates is helpful context but not proof that unobserved variables are equally weak. Avoid importing an E-value interpretation without matching its outcome and effect-scale assumptions.

### 8.6 How to generate a genuine hidden-confounding experiment

Generate a measured X and latent U. Let:

\[
A\sim\operatorname{Bernoulli}(\operatorname{sigmoid}(b_0+b_X X+b_U U)),
\]

\[
R(a)\sim\operatorname{Bernoulli}(\operatorname{sigmoid}(c_0+c_X X+c_A a+c_{XA}Xa+c_U U)).
\]

Use \(b_U\ne0\) and \(c_U\ne0\), hide U from the analyst, and make the analyst use the marginal propensity e(X), not the oracle e(X,U). Compute truth by integrating over the full simulator. Show how nominal IPS/DR can fail and whether a correctly specified sensitivity set covers the true value. In the evaluator, check that the simulated odds departures actually obey the chosen Gamma.

Do not simply remove a feature while continuing to supply oracle full-assignment probabilities, then assume you have created IPS confounding bias. Do not thin real randomized logs based on realized rewards and treat that as a clean treatment-confounding experiment: it can additionally change the population and induce outcome-dependent selection.

## 9. Drift, feedback, and practical failure modes

### 9.1 Time drift is not fixed by action weighting alone

Write \(V_t(\pi)=E_{X\sim P_t}\sum_a\pi(a\mid X)q_t(X,a)\). Then the observed before/after difference decomposes as:

\[
V_1(\pi)-V_0(\mu)
=\underbrace{V_0(\pi)-V_0(\mu)}_{\text{policy difference in the historical environment}}
+\underbrace{V_1(\pi)-V_0(\pi)}_{\text{environment/population change for the target}}.
\]

Historical OPE identifies the first term under its assumptions. It does not identify the second merely by being “causal.” Section 1 deliberately uses a simulator to reveal both.

If only the context distribution changes and reward mechanisms remain invariant, a density ratio \(P_1(X)/P_0(X)\) can transport an estimate to the new population, given suitable support and data to estimate the ratio. If conditional rewards change, context reweighting is insufficient. Difference-in-differences or controlled experiments can address some temporal questions under their own assumptions; they are not interchangeable with standard OPE.

### 9.2 Selective labels and delayed outcomes

If a loan is denied, repayment is not merely an unclicked recommendation: the outcome is defined or observed under different intervention conditions. If only approved loans have labels, missing rewards need explicit treatment. Similar problems arise when purchases occur after a logging cutoff. Complete-case analysis can favor actions with short reward delays.

Define a fixed reward horizon, distinguish zero from not-yet-observed, and model observation/censoring when necessary. A randomized action does not automatically randomize which outcomes are ultimately recorded.

### 9.3 Interference, capacity, and equilibrium

Marketplace actions can change inventory, seller prices, congestion, or competition. Recommending an item to one person can remove it for another. Individual action propensities do not identify a platform-wide intervention unless those dependencies are accounted for. Define the unit and intervention carefully, or limit the claim to the short-run setting studied.

### 9.4 Reward choice and fairness

Click-through rate may reward curiosity without purchases, satisfaction, retention, or welfare. Evaluate the objective the policy is supposed to improve, and report cost if actions have different costs. A useful reward might be net value rather than raw clicks.

Average improvement can hide subgroup harm. Report subgroup values, improvements, sample sizes, and support diagnostics where statistically feasible. Group comparisons introduce multiple-testing and precision issues; a small group's inconclusive interval is not evidence of no harm.

### 9.5 What to do when support is missing

If a target assigns probability to unsupported actions, possible responses are to restrict the policy, gather exploratory data, use defensible external structure, or report partial identification. Do not replace zero propensities by an arbitrary epsilon and claim identification.

For bounded rewards in \([0,1]\), if unsupported target probability mass is u and the supported contribution is identified as v, a simple worst-case range is \([v,v+u]\). This is a population illustration: finite-data uncertainty in v and uncertainty about support must also be considered. It makes the informational limit visible rather than hiding it in a model prediction.

## 10. Detailed audit of your existing research

Both supplied files were treated as research material, not as instructions to execute their code or adopt their claims. The Markdown brief is the stronger literature outline; the pasted file contains overlapping drafts, a truncated code fragment, and a longer implementation. Their useful content is retained throughout this dossier.

### 10.1 What is worth keeping

The material correctly identifies partial feedback, selection bias, propensity weighting, outcome modeling, double robustness, overlap, the Open Bandit ecosystem, uncertainty, and sensitivity analysis. The brief's emphasis on varying sample size, evaluating both policy directions, checking reward-model quality, and avoiding universal estimator rankings is especially useful.

The recommendation to combine a synthetic before/after trap with real bandit data is sound. The additions needed are precise estimands, defensible inference, explicit leakage prevention, and a valid sensitivity method.

### 10.2 Corrections to make before submission

| Claim or implementation in the supplied material | Assessment and correction |
|---|---|
| A logger that always shows electronics can evaluate arbitrary alternative products | Without action coverage or external structure, those counterfactuals are not identified. Use this as an impossibility example. |
| “Rewards must be independent of actions given X” | State independence for potential outcomes: R(a) independent of A given X. Observed reward generally depends on action. |
| The naive estimator is simultaneously a raw log mean, a matched-action mean, and before/after | These are different estimators with different targets. Label and compare them separately. |
| Argmax action matching represents a stochastic target | It changes the target into a deterministic policy. Use target action probabilities for stochastic OPE. |
| DR always has the lowest MSE or guarantees optimal variance reduction | Too strong. DR can perform worse with poor models or weak overlap. Efficiency is an asymptotic statement under conditions. |
| The DR residual always has zero conditional mean | Only with the correct conditional reward model. With a wrong model, valid weights can cancel the model's bias in the combined score. |
| SNIPS always has substantially lower variance | Often, not universally. It also has ratio bias and can be undefined with no matched observations. |
| DM has little support dependency | A numerical prediction does not identify unsupported outcomes. DM relies on extrapolation assumptions there. |
| Shrinkage “solves” low support | It changes the bias–variance tradeoff; it does not recover unidentified counterfactuals. |
| IPS is unbiased only asymptotically | With known valid probabilities and a fixed target in the standard setup, it is finite-sample unbiased. |
| `from sklearn.ensemble import GradientBoostingRegressor, LogisticRegression` | `LogisticRegression` belongs to `sklearn.linear_model`; the import in the supplied code is invalid. |
| The pasted pipeline is complete and runnable | An earlier fragment ends at `age = np.random.uniform(18, 7...` and runs into another draft. Cleanly separate prose and code. |
| For q0=2X and q1=1+1.5X, the better action changes at X=0.5 | False: q1−q0=1−0.5X is positive across [0,1]; equality would occur at X=2. |
| X<0.3 has less than 20% probability of action 1 under sigmoid(4X−2) | False over that entire range: at X=0.3 the probability is about 31.0%. It falls below 20% only for X below about 0.1534. |
| The sample simulator contains unobserved confounding | Its assignment and reward depend on recorded X; it demonstrates observed selection bias. Add a latent common cause to test hidden confounding. |
| The sample simulator demonstrates before/after failure | It has no separate periods or changing environment. Add a time variable and an explicitly changed outcome or context process. |
| The printed table establishes exact simulated results | Results are not accompanied by a verified run; the code's invalid import already prevents execution as written. Label illustrative values or regenerate them. |
| The target truth is exactly 1.7500 in every sample | 1.75 is the population mean for uniform X. The code uses the finite sample mean of 1+1.5X, which fluctuates. |
| A single-run estimate minus truth is estimator “bias” | It is realized estimation error. Bias is an expectation over repeated datasets, estimated using repetitions. |
| Fit and evaluate flexible reward models on the same rows | Use honest splitting/cross-fitting for the reported DR procedure. |
| `[V_DR/Gamma, V_DR*Gamma]` gives Rosenbaum bounds | Invalid. Derive bounds from assignment odds and compatibility constraints; see Section 8. |
| `[w/Gamma, w*Gamma]` is the exact marginal sensitivity model | It is not the exact odds-model transformation. Arbitrary weight boxes also omit compatibility constraints. |
| Thinning randomized OBD logs on reward is a clean confounding validation | It may introduce outcome selection and population change. Prefer a known latent-variable simulator. |
| Low ESS means every interval is optimistic | Low ESS signals weak information; a valid conservative interval may be wide. ESS alone cannot certify or invalidate inference. |
| OBD CTR is exact “ground truth” | It is a finite-sample on-policy reference. Include its uncertainty. |
| OBD is the only public real-world OPE dataset | Its benchmark design was distinctive historically. Avoid a timeless exclusivity claim. |
| Full OBD campaign statistics apply to the small repository sample | Recompute statistics for the data actually used; sample figures can differ substantially. |
| A lower sensitivity endpoint above baseline is conclusive proof | It is an assumption-qualified statement, with sampling uncertainty and baseline uncertainty still to address. |
| DICE “solves” long-horizon OPE generally | It addresses occupancy-ratio estimation under structural/coverage assumptions, not arbitrary confounded or partially observed systems. |

For the original uniform-X simulator, numerical integration gives the **large-sample matched-action mean about 1.9609**, while the population target mean is 1.75. This confirms selection bias, but does not verify the pasted table's 1.9982 as an actual seeded sample result. The report did not execute that invalid pipeline.

Some bibliographic wording also needs correction: Bottou et al.'s paper is *Counterfactual Reasoning and Learning Systems: The Example of Computational Advertising*. “Yin et al., 2023” is too ambiguous to use as a general confounding-OPE reference without identifying the exact paper; Gao and Yin's Human-AI collaboration work is one relevant, more specific contribution. DR shrinkage and CAB should not be treated as interchangeable names without checking their definitions. Exact benchmark percentage improvements in the supplied brief have not been adopted here as universal results.

## 11. Recommended hackathon experiments and implementation blueprint

### 11.1 A focused project proposition

Build a **policy evaluation workbench** that reports:

> “For this population, reward, and horizon, the estimated improvement is X, with an uncertainty interval Y. The conclusion depends on these assumptions and becomes inconclusive under this degree of hidden bias.”

Its distinctive feature should be evidence about when to trust the answer. IPS and DR are established methods; implementing them is not itself a new research contribution. A reproducible demonstration that exposes misleading metrics, checks calibration, and refuses unsupported conclusions is a strong application contribution.

### 11.2 Experiment A: the literal before/after trap

Use Section 1's two-group binary-reward generator.

1. Generate historical contexts with equal group probability.
2. Sample actions from the current logger, with A1 probabilities 0.1 and 0.9.
3. Sample binary rewards from the displayed table and record selected-action probabilities.
4. Fix the target as always-A1 before evaluation.
5. Estimate target value from historical data using DM, IPS, SNIPS, and cross-fitted DR.
6. Estimate target-minus-current improvement using paired row contributions.
7. Separately generate after-period target data with a 0.2 seasonal increment. These rows are for the naive dashboard and simulator validation only.
8. Display the positive before/after change alongside the negative same-period policy effect.

The main chart should distinguish “observed before/after,” “estimated same-period effect,” and “simulator truth.” Avoid placing raw values and value differences on a shared axis without labeling units. Include confidence intervals only for quantities actually estimated from samples.

Run many independent seeds. Do not engineer a single lucky seed where one estimator happens to match the truth exactly. The expected answer is a 40% historical target value and a −5 pp effect; finite samples will vary.

### 11.3 Experiment B: the double-robustness stress test

Use a separate generator with nonlinear context-action effects and a stochastic logger. Make a four-cell experiment:

| Outcome model | Propensity model | Expected asymptotic lesson |
|---|---|---|
| Correct | Correct | DM, IPS, SNIPS, and DR can be consistent; finite-sample precision differs |
| Misspecified | Correct | IPS remains valid; DR can correct outcome-model bias |
| Correct | Misspecified | DM remains valid; DR can remain consistent under conditions |
| Misspecified | Misspecified | DR has no general consistency guarantee |

Use a controlled parametric model to make “correct” meaningful, and hold the causal assumptions and support constant. Add a separate run with hidden U to show that “double robustness” is not a cure for confounding.

### 11.4 Experiment C: overlap and rare rewards

Reduce the logger's probability for target-preferred actions over a grid, for example 0.3, 0.1, 0.03, and 0.01, and vary n. These values are proposed experimental settings, not universal thresholds.

Plot RMSE, interval width, coverage, ESS, and the largest weight contribution. Repeat with sparse binary rewards resembling real click data. Add IPS clipping and Switch-DR to show the bias–variance tradeoff. Include a zero-support example where the system explicitly returns an identification limitation rather than a spurious estimate.

### 11.5 Experiment D: hidden-confounding sensitivity

Use Section 8.6's generator with a hidden common cause. For the simple sensitivity implementation, discretize X by design into a few strata instead of discretizing a complex real dataset after seeing results. Estimate the nominal propensity and treated success rate in each stratum.

Compute the Section 8.3 sensitivity curve, and use full simulator knowledge only to check the true odds bound and true value. Vary hidden-confounding strength. Show both a case where nominal OPE is biased and a case where the sensitivity interval becomes too wide to decide. Treat sampling uncertainty around endpoint estimates as a separate extension requiring validation.

### 11.6 Experiment E: real-world benchmark

Use one OBD campaign and a documented policy pair. Display the historical logger average, OPE estimates, and the held-out target-policy reference. This demonstrates the distinction between factual logger performance and target value; it is not a temporal before/after experiment.

If downloads or dependency integration become the bottleneck, keep the complete synthetic experiment as the core deliverable. A small real-data example with few clicks should be labeled exploratory rather than presented as decisive evidence.

### 11.7 Minimal data contract

| Field | Meaning | Validation |
|---|---|---|
| event_id / unit_id | Decision and dependence unit | No unintended duplicates; support grouped analysis |
| timestamp | Decision time | Features precede action and reward |
| context | Pre-decision information | No post-action leakage |
| action | Actual served choice | Valid, consistent ID mapping |
| propensity | Probability of that served action | Strictly positive for observed action; at most one |
| eligible_actions | Available choices at decision time | Target respects availability |
| reward | Outcome with fixed horizon | Distinguish missing, censored, and zero |
| policy_version | Logging rule identifier | Preserve probability provenance |
| position / slate_id | If relevant | Align reward unit and sampling probability |

For multiple logging policies, retain which policy generated each row. Naively pooling logs can be statistically inefficient, and using a single incorrect propensity can be biased. Dedicated multi-logger estimators account for the sampling design. [Agarwal et al., 2017](https://arxiv.org/abs/1703.06180); [Kallus et al., 2021](https://proceedings.mlr.press/v139/kallus21a/kallus21a.pdf).

### 11.8 Estimator pseudocode

The following is a specification, not a tested library integration:

```text
freeze target policy and evaluation population
validate contexts, actions, reward horizon, availability, propensities
create independent training/validation/evaluation partitions as appropriate

for each cross-fitting fold in the evaluation analysis:
    fit outcome model on the other folds
    predict q_hat(x, a) for every eligible action on held-out rows
    if true propensities were not logged:
        fit and predict a propensity model honestly
    calculate target probability of the action actually observed
    calculate w = target_probability / logging_probability
    calculate DM, IPS, and DR row contributions

pool held-out contributions
compute SNIPS from pooled weighted reward and pooled weights
compute paired target-versus-baseline improvement scores
calculate justified uncertainty intervals
report support, ESS, reward sparsity, and influence diagnostics
run the specified sensitivity analysis separately

only now reveal simulator truth or held-out on-policy reference
```

Nuisance fitting and policy learning are different operations. If an evaluation policy is learned, training that policy on the same rows used for final evaluation changes the problem and needs its own correction or holdout.

### 11.9 Metrics and figures

| Assessment | Metric or figure | Why it matters |
|---|---|---|
| Point accuracy | Bias, variance, RMSE over independent runs | Separates systematic error from noise |
| Calibration | CI coverage and mean width | Checks whether uncertainty is believable |
| Support | ESS, weight histogram, top-weight contribution | Exposes dependence on rare events |
| Decisions | Incorrect sign, false improvement rate, regret | Measures deployment-relevant errors |
| Hidden bias | Bound endpoints versus Gamma | Shows assumption sensitivity |
| Temporal attribution | Before/after versus same-period policy effect | Directly answers the problem statement |
| Subgroups | Group effects with support and uncertainty | Checks whether average gains hide harm |

For CTR, report percentage points and relative changes distinctly. A change from 0.35% to 0.50% is +0.15 percentage points and approximately +43% relative, not +43 percentage points. Relative estimation error becomes unstable when the reference value is near zero, so retain absolute error and RMSE.

### 11.10 A decision rule the system can explain

Let the minimum worthwhile gain be a predeclared threshold d, possibly zero.

- **Evidence of improvement under stated assumptions:** lower confidence bound for improvement exceeds d and diagnostics support the inference.
- **Evidence of harm:** upper confidence bound for improvement is below zero.
- **Inconclusive:** the interval spans the decision threshold or the sample is too weak.
- **Not identified under the chosen model:** required support or identification conditions are absent.

Add a separate hidden-confounding status, such as “improvement remains positive up to the prespecified Gamma range,” only if the sensitivity calculation supports it. Do not merge a sensitivity range and a sampling CI without defining what the combined coverage statement means.

This is an evidence report for a decision, not an automatic deployment guarantee.

### 11.11 Reproducibility deliverables

Keep one command or notebook entry point that regenerates the synthetic experiment and figures. Save the seed list, generator equations, environment versions, target probabilities, split definitions, clipping settings, model hyperparameters, and complete result tables. Preserve full-precision calculations even when charts show rounded values.

Meaningful implementation checks include: IPS equals the log mean when target equals logger; Gamma=1 recovers the nominal estimand; the exact two-group population calculations match Section 1; unsupported actions are rejected; and simulated interval coverage is assessed across independent datasets. Agreement between two implementations is useful but cannot replace a known-truth experiment.

## 12. Research opportunities, presentation strategy, and reading priorities

### 12.1 Other important branches to know about

**Targeted learning.** TMLE-style methods update outcome models toward the policy-value estimand, rather than only optimizing prediction loss. Regularized targeted learning is an established OPE branch. [Bibaut et al., ICML 2019](https://proceedings.mlr.press/v97/bibaut19a.html).

**Distributional robustness.** Robust OPE can optimize or evaluate worst-case value under a specified distribution-shift neighborhood. This is different from robustness to nuisance estimation and different again from hidden-confounding sensitivity. [Kallus et al., ICML 2022](https://proceedings.mlr.press/v162/kallus22a); [robust MDP evaluation, 2024](https://arxiv.org/abs/2404.00099).

**Proxy-based identification.** Negative controls, instrumental variables, and proximal methods seek identification under assumptions different from observed-context ignorability. Proximal RL uses proxies and bridge-function conditions in partially observed settings. Having any correlated proxy is not enough. [Bennett and Kallus](https://arxiv.org/abs/2110.15332).

**Prediction versus mean-value inference.** A prediction interval for an individual future reward is different from a confidence interval for expected policy value. Recent conformal/PAC off-policy prediction work studies the former; it should not be presented as automatically solving the hackathon's mean-value uncertainty requirement. [Wan et al., 2025 preprint](https://arxiv.org/abs/2507.16236).

**Marginalized DR.** Follow-up work combines embedding-based evaluation with a doubly robust construction for large action spaces. It belongs in the extended reading list, but should not be mixed with ordinary action-level DR without specifying the new assumptions. [Shimizu and Forastiere](https://arxiv.org/abs/2308.03443).

**Evaluation of many candidates.** Multiple-policy inference and selection-adjusted guarantees matter when a dashboard searches over many rules. A 95% interval for a prespecified policy does not automatically cover the winner chosen after inspecting dozens of estimates. [Dann et al., AISTATS 2023](https://proceedings.mlr.press/v206/dann23a.html).

### 12.2 What remains genuinely difficult

1. **Selecting estimators without ground truth.** Agreement is reassuring but can reflect shared bias; disagreement is hard to adjudicate.
2. **Weak or absent action support.** Large datasets can still contain little information about the target policy.
3. **Hidden confounding.** Point identification requires additional information or assumptions; sensitivity parameters cannot be learned from the observed distribution alone.
4. **Valid inference for adaptive, dependent data.** Real serving logs rarely resemble independent textbook rows perfectly.
5. **Transport to the future.** Historical validity does not establish tomorrow's value under changing behavior or rewards.
6. **Long-term feedback and interference.** A static value can miss retention, preference changes, competition, and resource constraints.
7. **Decision calibration.** Low average RMSE need not imply a low rate of harmful policy selections.
8. **Reliable logging.** Incorrect propensities and missing decision context can defeat otherwise correct estimators.

### 12.3 The most useful scope for this hackathon

My recommendation is to prioritize **clear estimands, controlled failure cases, and honest uncertainty** over a long list of advanced estimators. Complete these in order:

1. Synthetic before/after reversal with IPS and cross-fitted DR.
2. Paired confidence interval for policy improvement and coverage validation.
3. Weight diagnostics and a visible “inconclusive/not identified” outcome.
4. Correct binary sensitivity analysis with a known latent-variable simulator.
5. One carefully scoped OBD replication.
6. One optional variance-reduction comparison if time permits.

The result can be distinctive without claiming algorithmic novelty. Frame it as an auditable way to test whether an apparent policy win survives population adjustment, uncertainty, and plausible hidden bias.

### 12.4 Suggested presentation sequence

**Opening:** show 45% before and 60% after. Ask the audience whether the new policy worked.

**Reveal:** the new policy is worth 40% under old conditions; the incumbent would reach 65% during the sale. The apparent +15 pp win conceals a −5 pp policy effect.

**Explain:** the old policy selected different actions for different people. Logged assignment probabilities let the estimator correct that selection under explicit assumptions.

**Evidence:** show estimator estimates, ground truth, paired uncertainty, and repeated-run calibration.

**Stress test:** make exploration rare, then introduce hidden confounding. Show when the estimate becomes uncertain or assumption-dependent.

**Real data:** show the OBD replication with an empirical reference and its limits.

**Contribution:** a reproducible evaluation workflow that reports what the logs support and what they cannot establish.

### 12.5 Prioritized reading list

Read the core papers for their setup and assumptions, not just their headline estimator formulas.

| Priority | Source | What to extract |
|---|---|---|
| 1 | [Dudík et al., DR, 2011](https://arxiv.org/abs/1103.4601) | Why regression and weighting complement each other |
| 2 | [Open Bandit Dataset and Pipeline, 2021](https://arxiv.org/abs/2008.07146) | Data protocol and how to benchmark an evaluator |
| 3 | [Bottou et al., 2013](https://jmlr.org/papers/v14/bottou13a.html) | Define the intervention and its operating environment |
| 4 | [Wang et al., SWITCH, 2017](https://proceedings.mlr.press/v70/wang17a.html) | Fundamental variance limits and the role of outcome models |
| 5 | [Chernozhukov et al., DML](https://arxiv.org/abs/1608.00060) | Orthogonality, cross-fitting, and inference assumptions |
| 6 | [Kallus and Zhou, 2018](https://arxiv.org/abs/1805.08593) | Baseline-relative robust policy improvement |
| 7 | [Dorn and Guo, quantile balancing](https://arxiv.org/abs/2102.04543) | Correct sensitivity models and compatibility constraints |
| 8 | [Kuzborskij et al., 2021](https://proceedings.mlr.press/v130/kuzborskij21a/kuzborskij21a.pdf) | Confidence-qualified evaluation and selection |
| 9 | [Waudby-Smith et al.](https://arxiv.org/abs/2210.10768) | Adaptive data and continuously monitored estimates |
| 10 | [Uehara, Shi, and Kallus, review](https://arxiv.org/abs/2212.06355) | How the one-step problem connects to sequential OPE |

For extensions, follow the directly linked sources in Sections 5 and 12.1 rather than treating every advanced method as an MVP requirement.

### 12.6 Research provenance and limitations of this dossier

The supplied Markdown brief and pasted research were read and compared, including their formulas, code, numerical claims, and proposed experiments. Searches covered foundational weighting and causal inference, contextual-bandit DR, variance reduction, benchmarks, confidence intervals, adaptive inference, confounding sensitivity, large actions, slates, sequential OPE, and recent 2025–2026 developments.

Primary sources were preferred: original papers, PMLR/NeurIPS/AAAI proceedings, author-hosted manuscripts, arXiv records, and official ZOZO/OBP/SCOPE-RL documentation. Sources are linked at the relevant claims. Full text was inspected where needed for the Open Bandit statistics and sensitivity-model details; several frontier entries were checked at the primary abstract/metadata level only. A blocked OpenReview page was not used as evidence for detailed claims.

This is not a systematic review with a registered search protocol, database-completeness guarantee, or independently reproduced results from every cited paper. The local checks verified the illustrative arithmetic, original-generator integration, and displayed binary sensitivity endpoints. They did not run the supplied pipeline, download OBD, fit models, or establish empirical performance for a completed hackathon implementation.
