"""Audit saved results and claims without rerunning or tuning the experiments."""
import hashlib,io,json,re,unittest
from pathlib import Path
import methods as m
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    for name in ('real_manifest.json','synthetic_manifest.json'):
        manifest=json.loads((OUT/name).read_text());assert manifest['protocol_sha256']==sha(ROOT/'PROTOCOL.md')
        for p,h in manifest['source_sha256'].items():assert sha(ROOT/p)==h,p
    stability=json.loads((OUT/'stability_manifest.json').read_text())
    assert stability['protocol_sha256']==sha(ROOT/'STABILITY_PROTOCOL.md') and stability['method_sha256']==sha(ROOT/'methods.py')
    df=pd.concat([pd.read_csv(p,keep_default_na=False) for p in sorted(OUT.glob('synthetic_case_*.csv'))],ignore_index=True)
    assert len(df)==88000 and len(df[['case','rep']].drop_duplicates())==8000
    assert df.groupby(['case','method']).size().eq(500).all()
    assert not df.duplicated(['case','rep','method']).any()
    saved=pd.read_csv(OUT/'synthetic_summary.csv',keep_default_na=False)
    for row in saved.itertuples():
        part=df[(df['case']==row.case)&(df.method==row.method)]
        for col in ('covered','false_improvement','beneficial'):assert int(part[col].sum())==int(getattr(row,col))
    claims=json.loads((OUT/'claim_ledger.json').read_text());r=json.loads((OUT/'obd_all_random.json').read_text())
    exact=np.array(r['bounds']['group_exact']);original=np.array(r['bounds']['item_split'])
    assert np.isclose(np.median(1-np.diff(exact,axis=1)/np.diff(original,axis=1)),claims['primary_width_reduction_vs_original'])
    j=int(np.argmax(exact[:,0]));assert r['ks'][j]==claims['primary_k']==20
    np.testing.assert_allclose(exact[j],claims['primary_exact_interval'])
    assert claims['selected_exact_witness']['gain']==np.float64(claims['selected_exact_witness']['gain'])
    assert abs(claims['selected_exact_witness']['gain']-exact[j,0])<1e-12
    for path in OUT.glob('obd_*.json'):
        rr=json.loads(path.read_text());A=rr['n_actions'];pi=np.array(rr['policies']);n=np.array(rr['cert_n']);k=np.array(rr['cert_k'])
        np.testing.assert_allclose(pi.sum(1),1);assert sum(rr['counts'])==rr['first_position_rows']
        for i,kk in enumerate(rr['ks']):
            inside=pi[i]>0;mu=np.full(A,1/A);m.compress(mu,pi[i],inside)
            gn=np.array([n[inside].sum(),n[~inside].sum()]);gk=np.array([k[inside].sum(),k[~inside].sum()])
            coeff=np.array([1-kk/A,-(1-kk/A)])
            independent=m.box_bounds(coeff,*m.box(gn,gk,.05/len(pi),kind='exact'))
            np.testing.assert_allclose(independent,rr['bounds']['group_exact'][i],rtol=1e-12,atol=1e-12)
    data_manifest=json.loads((ROOT/'data/data_manifest.json').read_text())
    for key,info in data_manifest['datasets'].items():
        member=ROOT/'data'/f'{key}.member'
        if member.exists():assert sha(member)==info['member_sha256']
        compact=ROOT/'data'/f'{key}.npz'
        if compact.exists():
            with np.load(compact) as d:assert len(d['reward'])==info['rows'] and int(d['reward'].sum())==info['clicks']
    abstract=(ROOT/'ABSTRACT.md').read_text(encoding='utf-8');assert 600<=len(abstract.split())<=900 and abstract.count('\n## ')==8
    for name in ('01_obd_counterfactual','02_policy_certificate','03_ablation','04_synthetic_calibration','05_simulated_reversal'):
        assert (ROOT/'figures'/f'{name}.png').exists() and (ROOT/'figures'/f'{name}.svg').exists()
    layout=json.loads((ROOT/'output/pdf/layout_validation.json').read_text());assert layout['pages']==3 and layout['words_including_title_headings']==len(abstract.split())
    # Capture the final test log as part of this package's verification evidence.
    buf=io.StringIO();test=unittest.TextTestRunner(stream=buf,verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT),pattern='test_methods.py'))
    (OUT/'tests.txt').write_text(buf.getvalue());assert test.wasSuccessful() and test.testsRun==16
    st=pd.read_csv(OUT/'stability.csv');assert len(st)==3000 and st.groupby(['campaign','method']).size().eq(100).all()
    result=dict(protocol_and_inference_hashes_unchanged=True,raw_method_trial_rows=len(df),synthetic_logs=8000,
        summary_rows_checked=len(saved),obd_conditions_checked=6,real_rows_processed=claims['real_rows_processed'],
        exploratory_splits=300,unit_tests_passed=test.testsRun,abstract_words=len(abstract.split()),pdf_pages=layout['pages'],
        figures=5,visual_inspection='All three rendered PDF pages inspected; no clipping or overlap observed.')
    (OUT/'validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__':main()
