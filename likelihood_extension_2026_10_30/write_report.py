from pathlib import Path
import csv,hashlib,json,re
import numpy as np
ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'results/results.json').read_text())
manifest=json.loads((ROOT/'results/manifest.json').read_text())
for name,sha in manifest['source_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha,name
assert hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest()==manifest['protocol_sha256']
s='# Likelihood extension: measured results\n\n'
s+=f"Executed {r['logs']:,} independent simulated logs (sufficient statistics), 500 trials in each of 16 settings, with six comparison methods. All {r['tests']} tests passed. Runtime: {r['elapsed_seconds']:.1f} seconds on the local CPU environment. The first unit-test run exposed integer dtype handling in a scalar optimizer input; it was fixed before the benchmark. No experiment was tuned after observing its outputs.\n\n"
d=r['primary_paired_difference']
s+=f"**Primary gate failed.** Split likelihood and KL boxes each certified a beneficial change in 498/500 primary trials. The paired difference was {100*d['mean']:.2f} percentage points, 95% Monte Carlo interval [{100*d['normal95'][0]:.3f}, {100*d['normal95'][1]:.3f}]. The advertised >=10-point superiority target was not met. This is not a universal new algorithm; it is a tested specialization of established likelihood inference.\n\n"
s+='## Complete results\n\nBenefits/false improvements are percentages of trials; confidence brackets are Wilson 95% intervals for Monte Carlo rates. Coverage is simultaneous over all 32 candidate contrasts. Undefined candidate intervals make whole-family coverage unavailable; do not drop them silently.\n\n| Scenario | n | Method | Beneficial decision % [95% MC] | False improvement % | Family coverage % | Mean primary width |\n|---|---:|---|---:|---:|---:|---:|\n'
for t in r['summaries']:
    b=t['benefit'];cov=t['family_coverage']['mean'];w=t['primary_width']['mean']
    s+=f"| {t['scenario']} | {t['n']} | {t['method']} | {100*b['mean']:.1f} [{100*b['wilson95'][0]:.1f}, {100*b['wilson95'][1]:.1f}] | {100*t['false_improvement']['mean']:.1f} | {'undefined' if cov is None else f'{100*cov:.1f}'} | {'undefined' if w is None else f'{w:.5f}'} |\n"
s+='\n## Interpretation\n\nSome secondary scenarios favor split likelihood over the finite-sample KL box. These are exploratory results and do not replace the primary outcome. Wald often has higher decision power but can substantially undercover in sparse designs, even with a policy-count correction. Finite-sample methods can remain very conservative under weak overlap or many strata. All causal methods here fail when hidden confounding violates exchangeability. No method resolves unsupported causal outcomes without additional restrictions.\n\nThe hidden-confounding experiment is outside the causal theorem assumptions; its wrong decisions do not falsify the conditional observed-mean likelihood calculation. The simulator uses known context weights and binary rewards. No OBD experiment, general empirical-likelihood OPE implementation, adaptive logger, unknown-population inference or finished interface was evaluated.\n\n## Reproduction\n\nPython 3.12.14 and NumPy 2.3.5 were used. From this directory run `python -X utf8 experiment.py`, then `python -X utf8 write_report.py`. `test_likelihood.py` can run separately. `results/manifest.json` records the pre-run protocol and source hashes; `results/trials.csv` contains all 48,000 method/trial records. Original research files are untouched. This folder supports the abstract; the abstract promises the integrated report and adverse-model presentation as future work.\n'
(ROOT/'RESULTS.md').write_text(s,encoding='utf-8')
groups={}
with (ROOT/'results/trials.csv').open(newline='') as f:
    for row in csv.DictReader(f):groups.setdefault((row['scenario'],int(row['n']),row['method']),[]).append(row)
for t in r['summaries']:
    rows=groups[(t['scenario'],t['n'],t['method'])];assert len(rows)==500
    for key in ['benefit','false_improvement','harm','gain','regret','family_coverage','primary_width','undefined']:
        values=[float(x[key]) for x in rows if x[key]!=''];expected=t[key]['mean']
        assert (not values and expected is None) or abs(float(np.mean(values))-expected)<1e-10
abstract_dir=ROOT.parent/'abstract_submission_2026_10_31'
abstract=(abstract_dir/'Abstract.md').read_text(encoding='utf-8')
plain=re.sub(r'^#+\s*','',abstract,flags=re.M).replace('**','').replace('*','')
words=len(plain.split());assert 600<=words<=900,words
assert len(re.findall(r'^## ',abstract,flags=re.M))==8
(abstract_dir/'Abstract_plain.txt').write_text(plain,encoding='utf-8')
sha=hashlib.sha256((ROOT.parent/'Problem_3_Off_Policy_Evaluation_Research.md').read_bytes()).hexdigest()
assert sha==json.loads((ROOT.parent/'research_audit_2026_10_30/initial_manifest.json').read_text())['original_sha256']
report={'frozen_source_and_protocol_hashes_match':True,'raw_method_trial_rows':sum(map(len,groups.values())),
 'summaries_verified':len(groups),'tests_passed':r['tests'],'abstract_words_including_title_and_headings':words,'abstract_sections':8,'original_manuscript_unchanged':True}
(ROOT/'results/validation.json').write_text(json.dumps(report,indent=2))
(abstract_dir/'Validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
