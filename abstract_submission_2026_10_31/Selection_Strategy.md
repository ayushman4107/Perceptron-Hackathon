# Submission strategy — supporting notes, not part of the abstract word count

## The proposal in one sentence

**Evaluate a policy-change claim by searching for a statistically plausible reward model that would overturn it, and return an improvement certificate or an explicit counterexample under declared assumptions.**

The evaluator-facing hook is a concrete decision: “Is the claimed gain supported, contradicted, or unresolved?” The technical center is optimization of a policy contrast over a shared likelihood confidence region. The visible output is both the interval and a candidate adverse reward table. This moves the submission beyond merely listing estimators while remaining feasible for a three-person team.

## Why this is the recommended abstract for tomorrow

The supplied challenge document assesses depth and rigor of a technical plan at this stage. It asks for differentiation; it does not require proving a world-first algorithm before submission. A precise application extension, explicit assumptions, a strong evaluation protocol and a credible fallback satisfy that brief better than an unsupported promise of universal superiority.

The current abstract covers all eight requested sections and stays within 600–900 words. The optional diagram shows the separation between logged data, estimator outputs, confidence-region optimization and evaluator-only simulator truth. Team skills are based on the team's own description; the division of responsibilities is proposed, not a claim about named members' past work.

## Claim boundaries

| Claim | Status / wording |
|---|---|
| Standard OPE and synthetic reversal | Existing research prototypes and checked examples support feasibility; final demonstration is planned |
| Joint likelihood inference and convex projection | Implemented numerical prototype; 13 tests passed; based on established methods |
| Explicit adverse reward-table presentation | Proposed extension of solver outputs into an auditable report; no finished interface claimed |
| Better decisions in every setting | Unsupported; do not claim |
| Unique algorithm or first-ever policy certificate | Unsupported; do not claim |
| Protection against arbitrary hidden confounding | False; assumptions and optional sensitivity analysis are necessary |
| New data can always fix uncertainty | False; structural missing support needs new action coverage or defensible restrictions |
| Superiority over other teams | Unknown; their submissions are unavailable |

## What the new pilot actually showed

An additional 8,000-log comparison tested split likelihood inference against KL boxes, Hoeffding boxes, a full-data mixture region and Bonferroni-corrected tabular Wald intervals. The prespecified primary comparison did **not** establish superiority: split likelihood and KL boxes each certified a beneficial change in 498/500 trials. Some secondary settings showed useful gains; these are exploratory findings, not a reason to conceal the primary tie. The abstract therefore proposes to characterize the operating range and test the extension, rather than advertising a proven universally superior algorithm.

The previous 36,000-log experiment also showed that a shared-box contrast method exactly matched its established robust comparator. We retained the useful principle but rejected a new-method claim. This history informs the current modest scope; it should not be presented as a string of novel algorithms.

## Questions to prepare for

**What is your technical difference from an IPS/DR dashboard?**
We optimize the same target-minus-logger estimand over an explicit joint uncertainty set and expose a model that challenges the gain. Our claim is a concrete, auditable application extension with planned comparative tests, not a new IPS formula.

**Is the adverse reward table the actual counterfactual world?**
No. It is one model in the specified confidence/ambiguity set. It demonstrates that the current evidence does not rule out that outcome. Under missing support, different reward models can produce the same observed law. With sampling uncertainty, membership means confidence-set plausibility, not exact observational equivalence.

**How does selecting from many policies avoid optimism?**
Within fixed finite cells, one region covers the whole reward-mean table, so its projected bounds cover all candidate contrasts together. We do not apply that guarantee to data-dependent feature partitions or arbitrary continuous-context learners.

**Why use a likelihood method if a strong baseline tied it?**
The purpose is to test a specific decision procedure and its operating range. Secondary gains justify investigation, while the primary tie prevents an exaggerated superiority claim. The simpler KL-box method remains an explicit fallback if the more complex region offers no practical benefit.

**Can your confidence certificate survive confounding?**
Only if its identification assumptions hold. Our hidden-confounding stress test intentionally breaks them and makes the failure visible. The stretch analysis quantifies sensitivity to a specified departure, not detection of all unmeasured confounders.

**What can three people actually finish?**
A synthetic generator, standard estimators, finite-cell numerical solver, tested decision logic and Streamlit demo need ordinary CPU resources. An arbitrary real-data causal modeling platform, online exploration system or new general-purpose theorem is outside the promised scope.

## Primary references for technical discussion

- [Universal Inference — Wasserman, Ramdas and Balakrishnan](https://arxiv.org/abs/1912.11436): split likelihood confidence construction; relevant full-text sections were checked.
- [Empirical Likelihood for Contextual Bandits — Karampatziakis, Langford and Mineiro](https://arxiv.org/abs/1906.03323): prior likelihood-based OPE and lower-bound optimization; abstract and proceedings metadata checked.
- [Likelihood Ratio Confidence Sets for Sequential Decision Making — Emmenegger, Mutny and Krause](https://papers.neurips.cc/paper_files/paper/2023/hash/5491280797f3192b895bce84eb83df8d-Abstract-Conference.html): related confidence-set methodology; relevant theorem and scope checked.
- [Safe Exploration for Efficient Policy Evaluation and Comparison — Wan, Kveton and Song](https://proceedings.mlr.press/v162/wan22b.html): direct predecessor to generic contrast-focused acquisition claims; this is why acquisition is not pitched as our immediate novelty.

The proposal should be submitted as a plan with precisely scoped differentiation. No literature search can certify uniqueness against every paper, and no available evidence can guarantee selection against unknown teams.
