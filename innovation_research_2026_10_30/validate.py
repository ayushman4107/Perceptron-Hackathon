"""Validate research artifacts and provenance without rerunning experiments."""
from pathlib import Path
import csv,hashlib,json,re
import numpy as np
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'results/run_manifest.json').read_text())
for path,expected in manifest['source_sha256'].items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
assert hashlib.sha256((ROOT/'Experimental_Protocol.md').read_bytes()).hexdigest()==manifest['protocol_sha256']
original=ROOT.parent/'Problem_3_Off_Policy_Evaluation_Research.md'
original_hash=hashlib.sha256(original.read_bytes()).hexdigest()
assert original_hash==json.loads((ROOT.parent/'research_audit_2026_10_30/initial_manifest.json').read_text())['original_sha256']
required=['README.md','Innovation_Research_Report.md','Technical_Specification.md','Literature_Comparison.md','Experimental_Protocol.md','Results_Report.md','Judge_Explanation.md','src/core.py','tests/test_core.py']
for path in required:assert (ROOT/path).is_file(),path
for p in ROOT.glob('*.md'):
    s=p.read_text(encoding='utf-8')
    assert not any(ord(c)<32 and c not in '\t\r\n' for c in s),p
    assert s.count('```')%2==0,p
    assert s.count(r'\[')==s.count(r'\]'),p
    for target in re.findall(r'\]\(([^)]+)\)',s):
        if not target.startswith('http'):assert (p.parent/target).exists(),(p,target)
scores=[]
for line in (ROOT/'Innovation_Research_Report.md').read_text(encoding='utf-8').splitlines():
    if re.match(r'\| C[1-5] ',line):
        parts=[x.strip() for x in line.split('|')][1:-1]
        computed=sum(float(x)*w for x,w in zip(parts[1:7],[.25,.20,.20,.20,.10,.05]))
        assert abs(computed-float(parts[7]))<1e-12,parts
        scores.append(computed)
assert len(scores)==5
r=json.loads((ROOT/'results/results.json').read_text())
assert r['tests_run']==17 and r['test_failures']==r['test_errors']==0
assert len(r['summaries'])==216 and r['logs']==36000
groups={}
with (ROOT/'results/trials.csv').open(encoding='utf-8',newline='') as f:
    for row in csv.DictReader(f):
        key=(row['scenario'],int(row['n']),int(row['policies']),row['method'])
        groups.setdefault(key,[]).append(row)
for summary in r['summaries']:
    key=(summary['scenario'],summary['n'],summary['policies'],summary['method'])
    records=groups[key];assert len(records)==1000
    for metric in ['deploy','benefit','harm','false_improvement','improvement','regret','undefined_candidates','primary_width','family_coverage']:
        vals=[float(t[metric]) for t in records if t[metric]!='']
        expected=summary[metric]['mean']
        assert (expected is None and not vals) or abs(float(np.mean(vals))-expected)<1e-12,(key,metric)
report={'original_unchanged':True,'original_sha256':original_hash,'recorded_source_hashes_match':True,
        'frozen_protocol_hash_matches':True,'candidate_score_arithmetic':'passed','markdown_links_and_structure':'passed',
        'raw_method_trial_rows':sum(map(len,groups.values())),'summary_rows_verified':len(groups),'tests_passed':r['tests_run']}
(ROOT/'results/package_validation.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
