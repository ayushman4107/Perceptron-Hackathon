# Judge-facing technical explanation

**What we can defend:** a comparison can be more identifiable than either policy's absolute value. We implement comparison-specific uncertainty and show exactly when this helps and when it cannot help. We do not claim to have invented robust policy comparison.

Suppose two recommendation policies both assign 40% probability to an action absent from the historical log. One puts its remaining 60% on action A, the other on B. Their absolute values depend on an unknown outcome, but their difference is 0.6 times the difference between B and A. Separate value intervals can count the common unknown reward twice and refuse to compare policies whose difference is estimable.

Our research prototype represents plausible reward means in one simultaneous confidence region and optimizes the signed policy difference over that same region. For a rectangular region this is just a signed endpoint sum. We derive its finite-sample conditional guarantee under bounded IID outcomes, correct within-cell exchangeability and known target population weights. It covers policy selection on the fixed cells. It does not establish safety under unknown confounding, changed reward mechanisms or data-dependent discretization.

The strongest applicable comparator solves the same robust objective independently. Across 36,000 synthetic logs its answers were identical to ours. In the primary 1,000-run setting, both made the beneficial decision in every trial, whereas subtracting separate value intervals never did. Paired DR also resolved every trial. These results justify implementing the principle; they **do not establish a novel estimator or superiority to existing robust methods**.

There is a critical restriction: the reference in that example is another candidate policy. If the reference is the historical logger, it has zero probability on every structurally unlogged action, so the advertised missing-action cancellation cannot occur. We include that case and refuse an unsupported comparison. We also show high-confidence harmful decisions under deliberately unmodeled confounding and shift, and lost power under rare rewards.

The defensible contribution today is a reproducible failure analysis and application prototype with explicit identification limits. To claim research novelty, we would need a distinct mechanism that beats an appropriately adapted robust/paired inference baseline under a specified decision objective. That evidence is not yet available.

## Demonstration script

1. Run `python -X utf8 demo.py`. It uses the first seed from the frozen primary protocol, without searching seeds.
2. Show the separate, exact population before/after example: the average rises from .32 to .58, while changing policies in the same new population loses .10. Label these as known synthetic expectations, not measured deployment results.
3. Move to the logged-data comparison experiment. Display the historical logger, two alternative policies, cell counts and missing third action. Explicitly distinguish the reference from the logger.
4. Display separate value-difference bounds and explain the duplicated unknown mean.
5. Display the joint contrast certificate, the independently implemented robust reference, and paired DR side by side. Do not hide the matching strong baseline.
6. Reveal the simulator's true policy gain, .24, only after the estimates are calculated.
7. Show the 1,000-trial primary comparison and Wilson intervals in `Results_Report.md`, rather than relying on the displayed seed.
8. Show the logger-reference failure case: more data from the same missing-support logger cannot uniquely determine the contrast.
9. Show rare-reward conservatism and hidden-confounding/shift failures. Explain which assumptions break and which merely reduce power.
10. Conclude with the honest novelty verdict: useful mechanism, established principle, no validated new-method claim. The hackathon entry can still be technically strong through correct implementation and reproducible evidence.

Closest research and exact reading scope are in `Literature_Comparison.md`; the proof and implementation are in `Technical_Specification.md` and `src/core.py`.
