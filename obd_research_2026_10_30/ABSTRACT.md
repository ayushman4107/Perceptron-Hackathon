# PoliSee: Counterfactual Policy Evaluation

[Code and reproducible results on GitHub](https://github.com/ayushman4107/Perceptron-Hackathon)

## Problem and theme

We address Problem 3, “Did the Policy Actually Work, or Did It Just Look Like It Did?”, under Theme 2: Cause and Effect in AI Decisions. Our starting point is a measured discrepancy. In Open Bandit Dataset’s men’s campaign, the deployed Thompson Sampling policy records a 0.7245% click-through rate. Evaluating uniform recommendation from those logs gives **0.5481% with doubly robust estimation**; the **independent Random-policy reference is 0.5380%**. Reusing the deployed policy’s average would answer the wrong question. We want to make that distinction visible before a team changes its decision system.

## Understanding the challenge

Logs contain the reward of the chosen action, not the alternatives. Unequal action probabilities distort comparisons; changing user populations can reverse their sign. Rare clicks create a second problem: **a reasonable point estimate can have unreliable uncertainty**. Searching several policies and reporting the most promising one compounds this problem. Our earlier item-level likelihood prototype was conservative and failed to establish superiority over a strong baseline. That led us to investigate whether evaluating every item separately was necessary for the policy change being considered.

## Proposed approach

Our extension uses **policy-ratio compression**. Actions enter the same group only when their target-to-logging probability ratios match. This preserves the policy-value difference **without assuming equal rewards within a group**. For uniform logging over A items and a target that recommends uniformly from a pilot-selected top-k set, the improvement is exactly (1−k/A) times the difference between two group click rates. **An 80-item comparison therefore needs two aggregate reward means.**

**An independent pilot chooses candidate sets; certification data evaluate them; a separate reference split checks the estimates.** We compare projected likelihood regions with grouped KL and exact Clopper–Pearson bounds, correcting across candidate policies. Experiments favor the **grouped exact procedure**, which we adopt. IPS, SNIPS and cross-fitted DR remain comparison estimators. The output includes a gain interval, its assumptions, and adverse group means attaining its lower bound. If no candidate clears zero, the system reports **insufficient evidence**. Python, NumPy and SciPy implement the statistical core; Streamlit will expose the report.

## Minimum viable demonstration

**Both required capabilities already have executable evidence.** Standard IPS and DR run on real logged bandit data. In a separate controlled simulator with 100,000 observations before and after a policy change, the raw average rises by **30.35 percentage points**; IPS using only the current-policy log estimates a **−6.14-point effect**, close to the known −6-point truth. The prototype demonstration will show this reversal beside the real-data policy certificates and their endpoint models.

## Stretch ambitions

**Uncertainty quantification is implemented and tested.** We will extend the report with sensitivity to specified propensity errors or unobserved confounding, keeping those assumptions separate from sampling uncertainty. We also report chronological-split and time-block-bootstrap diagnostics. These checks matter because a certificate for historical traffic does not automatically justify deployment on future traffic.

## Novelty and differentiation

Our contribution is a policy-specific evaluation procedure with a **checkable compression condition and explicit counterexamples to unsupported gains**. It avoids paying for distinctions between items that the requested comparison does not require. This extends our original likelihood approach into an auditable decision tool. It builds on established OPE, likelihood inference and evaluation-weight-preserving aggregation; we do not claim to have invented those components. The important empirical finding is that the representation change helps more than adding a complicated likelihood predictor.

## Evaluation and preliminary results

We processed **6.77 million rows** from four full Open Bandit campaign files. The primary first-position Random/all analysis separates 91,674 pilot, 183,450 certification and 182,881 reference observations. Across five candidate sizes, grouped exact intervals are **82.6% narrower** at the median than our original item-level likelihood intervals, and **79.0% narrower** than item-level KL bounds. The selected top-20 policy has a **family-corrected gain interval of [0.0528, 0.2515] CTR percentage points**; the independent reference gain is 0.2184 points, with a pointwise 95% interval of [0.1618, 0.2750]. **This reference is an estimate, not exact truth.**

Separately, **8,000 independent synthetic logs** compare **eleven methods** across rare rewards, heterogeneous effects, null gains and concentrated signals. We measure simultaneous coverage, false improvement, certification rate, regret and interval width. **Sixteen implementation tests pass**, including independent numerical optimization. Other campaigns, chronological splits, negative findings and reproducible results accompany the submission.

## Feasibility and risks

Our three members have Python/ML, statistics, backend and frontend experience, including substantial software projects. We will divide statistical verification, data integration and interface work accordingly. **The numerical core and benchmarks already run on CPU**; integration and presentation remain. Main risks are dependence between impressions, reward drift, cross-item effects within recommendation slates, and policy ratios that cannot be compressed. We therefore restrict the initial claim to position-wise, context-free policies under explicit identification and sampling assumptions, and **withhold a certificate when structural validity checks fail**.
