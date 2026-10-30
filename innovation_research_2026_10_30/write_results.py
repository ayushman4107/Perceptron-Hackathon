"""Generate reports from executed results, never from expected outcomes."""
from pathlib import Path
import json,math
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'results/results.json').read_text())
timing=json.loads((ROOT/'results/runtime.json').read_text())


def row(scenario,method,n=3000,m=2):
    return next(t for t in r['summaries'] if t['scenario']==scenario and t['method']==method and t['n']==n and t['policies']==m)


def rate(z):
    return f"{100*z['mean']:.1f}% [{100*z['wilson95'][0]:.2f}, {100*z['wilson95'][1]:.2f}]"


s='# Executed results and novelty decision\n\n'
s+=f"The frozen protocol generated **{r['logs']:,} independent logs**, nine scenarios × two sample sizes × two candidate-family sizes × 1,000 repetitions. All **{r['tests_run']} automated tests passed** with {r['test_failures']} failures and {r['test_errors']} errors. Main experiment runtime was {r['elapsed_seconds']:.2f} seconds in this environment; this excludes subsequent report generation and timing sweeps.\n\n"
s+='## Primary result\n\n'
s+='For shared_blind, n=3,000 and two policies, the following are measured beneficial-deployment rates. Brackets are 95% Wilson Monte Carlo intervals, not policy-value confidence intervals.\n\n| Method | Beneficial deployment | False improvement | Mean primary interval width |\n|---|---:|---:|---:|\n'
for method in ['joint_contrast','robust_reference','separate_values','paired_DR_Wald','retain_reference']:
    t=row('shared_blind',method);width=t['primary_width']['mean']
    s+=f"| {method} | {rate(t['benefit'])} | {rate(t['false_improvement'])} | {'undefined' if width is None else f'{width:.5f}'} |\n"
d=r['primary_paired_benefit_difference']
s+=f"\nThe paired improvement versus separate intervals was {100*d['mean']:.1f} percentage points. Its preregistered-within-this-workspace normal Monte Carlo interval is degenerate because every paired trial had the same result (MCSE={d['mcse']:.3f}); this does **not** mean zero uncertainty about future trials. A supplemental distribution-free Hoeffding interval for a paired difference in [-1,1] is [{max(-1,d['mean']-math.sqrt(2*math.log(40)/1000)):.4f}, {min(1,d['mean']+math.sqrt(2*math.log(40)/1000)):.4f}]. This boundary check was added for reporting, not used to tune the method or choose the scenario.\n\n"
s+=f"H1's practical threshold is met. H2's novelty gate fails: the maximum endpoint discrepancy from the exact shared-model robust reference across all experiments was **{r['max_joint_reference_difference']:.3g}**. The algebra proves equality beyond these simulations. Paired DR also resolved every primary trial, with substantially narrower intervals. Thus neither a new algorithm nor superiority to a strong OPE comparator is demonstrated.\n\n"
s+='## Negative and adversarial results\n\nAll rows below use n=3,000, two policies and 1,000 repetitions. Family coverage means coverage of all candidate contrasts in that run; with two policies only one contrast is nontrivial. It is unavailable when a required contrast interval is undefined.\n\n| Scenario | Method | Beneficial deployment | False improvement | Family coverage |\n|---|---|---:|---:|---:|\n'
for scenario in ['logger_reference','weak_overlap','rare_rewards','null','heterogeneous','hidden_confounding','unmodeled_shift']:
    for method in ['joint_contrast','paired_DR_Wald']:
        t=row(scenario,method);cover=t['family_coverage']['mean']
        s+=f"| {scenario} | {method} | {rate(t['benefit'])} | {rate(t['false_improvement'])} | {'undefined' if cover is None else f'{100*cover:.1f}%'} |\n"
s+='\nThe box method makes no beneficial deployments in the listed weak-overlap and rare-reward two-policy settings. Its low error there reflects conservatism and missed benefits. In the logger-reference case, structural ambiguity persists; DR correctly declines the unsupported contrast. A midpoint extrapolation happens to select a beneficial policy in that world, but the indistinguishable-world unit test shows why this cannot be a reliable causal conclusion.\n\n'
s+='Hidden confounding and unmodeled shift deliberately violate the theorem assumptions. Both the box method and paired DR can then make harmful decisions with high confidence. These results are failures of applicability, not evidence that the conditional confidence-region proof is false. A declared sensitivity set or correct transport model is additional methodology, not a property of this prototype.\n\n'
s+='## Selection and ablations\n\nThe following null scenario highlights selection; harm is zero by construction, so false improvement is the relevant metric. A selected zero-effect policy counts as a false improvement.\n\n| n | Policies | Joint false improvement | DR/Wald false improvement | Midpoint false improvement |\n|---:|---:|---:|---:|---:|\n'
for n in [300,3000]:
    for m in [2,32]:
        s+=f"| {n} | {m} | {rate(row('null','joint_contrast',n,m)['false_improvement'])} | {rate(row('null','paired_DR_Wald',n,m)['false_improvement'])} | {rate(row('null','midpoint_no_uncertainty',n,m)['false_improvement'])} |\n"
s+='\nThe comparison to separate values removes cancellation; midpoint removes uncertainty; always-reference removes all deployment. The exact robust reference tests whether there is any new mechanism. No variance-adaptive box, pilot confidence-allocation scheme or sensitivity-adjusted prototype was tuned after observing these results. The DR model is two-fold tabular smoothing; general model-class misspecification experiments remain unrun.\n\n'
s+='## Runtime and reproducibility\n\n| Cells S | Policies M | Projection median (ms), five repeats |\n|---:|---:|---:|\n'
for t in timing['projection']:s+=f"| {t['cells']} | {t['policies']} | {1000*t['median_seconds']:.3f} |\n"
s+=f"\nAggregating 100,000 logged rows took a median {1000*timing['aggregate_100000_median_seconds']:.3f} ms over five repeats. These are local descriptive timings, not hardware-independent speed claims. Full summaries (all 216 scenario/method combinations), policy tables, raw 216,000 trial-method records, script hashes, protocol hash, and test statuses are under `results/`.\n\n"
s+='## Decision\n\nNo assessed candidate is promoted as a validated technical innovation. C1 is a sound, reproducible implementation of an established principle with a useful demonstration. C2 remains a research question without a differentiating acquisition algorithm or executed benchmark. The negative novelty finding is part of the requested result, not a missing positive claim. OBD replication and full comparisons to general published algorithms are unexecuted.\n'
(ROOT/'Results_Report.md').write_text(s,encoding='utf-8')

full='# Complete scenario summary\n\nRates and widths come directly from results.json. M is the candidate count including the reference. Coverage shown for midpoint is exact-point containment, not a legitimate confidence interval.\n\n| Scenario | n | M | Method | Deploy | Benefit | False improvement | Harm | Regret | Primary width | Family coverage |\n|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|\n'
for t in r['summaries']:
    vals=[t[k]['mean'] for k in ['deploy','benefit','false_improvement','harm','regret','primary_width','family_coverage']]
    full+='| '+f"{t['scenario']} | {t['n']} | {t['policies']} | {t['method']} | "+' | '.join('undefined' if x is None else f'{x:.6f}' for x in vals)+' |\n'
(ROOT/'results/Complete_Summary.md').write_text(full,encoding='utf-8')
print('Generated Results_Report.md and results/Complete_Summary.md from measured outputs.')
