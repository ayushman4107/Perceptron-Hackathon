"""Generate a transparent source ledger and validate final audit artifacts."""
from pathlib import Path
import csv, hashlib, json, re

root = Path(__file__).resolve().parents[1]
original = root.parent / 'Problem_3_Off_Policy_Evaluation_Research.md'
snapshot = root / 'original_snapshot.md'
assert original.read_bytes() == snapshot.read_bytes()
assert hashlib.sha256(original.read_bytes()).hexdigest() == json.loads((root/'initial_manifest.json').read_text())['original_sha256']

urls = sorted(set(re.findall(r'https?://[^\s)\]>]+', snapshot.read_text(encoding='utf-8'))))
checked = {
 '1103.4601','1608.00060','2008.07146','2102.04543','2607.22012','2610.10974',
 '2606.22639','2609.19135','2505.00961','2210.10768','2211.13904','1805.08593',
 '2605.15108','wang17a','su20a','laroche19a','ryu25a','dann23a','ishikawa23a','zhu22a','st-tech/zr-obp'
}
with (root/'results/citation_ledger.csv').open('w',encoding='utf-8',newline='') as f:
    writer=csv.writer(f)
    writer.writerow(['original_url','audit_status','verification_scope'])
    for url in urls:
        if '2102.04543' in url or '2008.07146' in url:
            status='rechecked: relevant full-text sections'
            scope='Same underlying paper checked through arXiv HTML; not an independent proof of every theorem'
        elif any(key in url for key in checked):
            status='rechecked: primary landing page/abstract or repository'
            scope='Bibliographic existence and claim relevance; no full external implementation replication'
        else:
            status='not independently rechecked in this audit'
            scope='Retained from original research; not counted as newly verified'
        writer.writerow([url,status,scope])

required=['README.md','Problem_3_Off_Policy_Evaluation_Revised.md','Mathematical_Audit.md',
 'Assumptions_and_Guarantees.md','Verification_Report.md','Novelty_and_Literature.md',
 'Prioritized_Remediation_Plan.md','changes.json','manuscript.diff']
for name in required:
    p=root/name
    assert p.is_file() and p.stat().st_size > 100, name
for p in root.glob('*.md'):
    s=p.read_text(encoding='utf-8')
    assert not any(ord(c)<32 and c not in '\n\r\t' for c in s), f'control character: {p}'
    assert s.count('```')%2==0, f'code fence: {p}'
    assert s.count(r'\[')==s.count(r'\]'), f'math delimiters: {p}'
revised=(root/required[1]).read_text(encoding='utf-8')
assert re.findall(r'\*Equation M(\d\d)\.\*',revised)==[f'{i:02d}' for i in range(1,29)]
r=json.loads((root/'results/verification_results.json').read_text())
assert r['tests_run']==29 and r['failures']==r['errors']==0
assert r['source_script_sha256']==hashlib.sha256((root/'verification/verify.py').read_bytes()).hexdigest()
assert len(r['monte_carlo'])==20
assert len(set(x['scenario'] for x in r['monte_carlo']))==4
assert len(urls)==61, len(urls)
report={'original_unchanged':True,'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
 'required_artifacts_present':True,'markdown_structure_checks':'passed','original_display_equations':28,
 'original_source_urls_in_ledger':len(urls),'verification_script_hash_matches':True,
 'tests_passed':r['tests_run'],'scenario_method_rows':len(r['monte_carlo'])}
(root/'results/package_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
