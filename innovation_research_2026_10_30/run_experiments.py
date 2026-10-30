"""Execute the frozen falsification protocol; no parameter search."""
from pathlib import Path
import csv,hashlib,io,json,platform,time,unittest
import numpy as np
from src.core import aggregate,confidence_box,contrast_bounds,robust_reference,separate_bounds,select,dr_intervals
from src.simulation import NAMES,setting,draw,oracle_differences

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'
METHODS=['joint_contrast','robust_reference','separate_values','paired_DR_Wald','midpoint_no_uncertainty','retain_reference']


def wilson(values):
    v=np.asarray(values,float);n=len(v);p=float(v.mean());z=1.96
    mid=(p+z*z/(2*n))/(1+z*z/n)
    rad=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    return {'mean':p,'mcse':float(np.sqrt(p*(1-p)/n)),'wilson95':[float(mid-rad),float(mid+rad)]}


def run(repetitions=1000):
    OUT.mkdir(exist_ok=True)
    start=time.perf_counter()
    manifest={'protocol_sha256':hashlib.sha256((ROOT/'Experimental_Protocol.md').read_bytes()).hexdigest(),
        'python':platform.python_version(),'numpy':np.__version__,'repetitions':repetitions,
        'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(ROOT.rglob('*.py'))}}
    (OUT/'run_manifest.json').write_text(json.dumps(manifest,indent=2))
    stream=io.StringIO()
    tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT/'tests')))
    (OUT/'tests.txt').write_text(stream.getvalue());print(stream.getvalue(),flush=True)
    if not tests.wasSuccessful():raise SystemExit(1)
    summaries=[]; configs=[]; max_discrepancy=0.; primary=[]
    with (OUT/'trials.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['scenario','n','policies','rep','seed','method','selected','deploy','benefit','harm','false_improvement','improvement','regret','family_coverage','primary_width','undefined_candidates']
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for si,name in enumerate(NAMES):
            for ni,n in enumerate([300,3000]):
                for mi,m in enumerate([2,32]):
                    cfg=setting(name,m); truth=oracle_differences(cfg)
                    configs.append({key:value.tolist() if isinstance(value,np.ndarray) else value for key,value in cfg.items()}|{'n':n,'policies':m})
                    records={method:[] for method in METHODS}
                    for rep in range(repetitions):
                        seed=1000000+si*100000+ni*10000+mi*2000+rep
                        x,a,r=draw(cfg,n,seed);count,total=aggregate(x,a,r,2,3);lo,hi=confidence_box(count,total)
                        joint=np.asarray([contrast_bounds(pi,cfg['base'],cfg['p_input'],lo,hi) for pi in cfg['candidates']])
                        reference=np.asarray([robust_reference(pi,cfg['base'],cfg['p_input'],lo,hi) for pi in cfg['candidates']])
                        separated=np.asarray([separate_bounds(pi,cfg['base'],cfg['p_input'],lo,hi) for pi in cfg['candidates']]);separated[0]=0
                        dr=dr_intervals(x,a,r,cfg['mu'],cfg['candidates'],cfg['base'])
                        midpoint=joint.mean(1);plug=np.column_stack([midpoint,midpoint])
                        retain=np.full_like(joint,np.nan);retain[0]=0
                        max_discrepancy=max(max_discrepancy,float(np.max(abs(joint-reference))))
                        trial_benefits={}
                        for method,bounds in zip(METHODS,[joint,reference,separated,dr,plug,retain]):
                            j=select(bounds[:,0]);delta=float(truth[j]);undefined=int(np.isnan(bounds[:,0]).sum())
                            row=dict(scenario=name,n=n,policies=m,rep=rep,seed=seed,method=method,selected=j,
                                deploy=int(j!=0),benefit=int(j!=0 and delta>1e-12),harm=int(j!=0 and delta < -1e-12),
                                false_improvement=int(j!=0 and delta<=1e-12),improvement=delta,regret=float(max(truth)-delta),
                                family_coverage=None if undefined else int(np.all((truth>=bounds[:,0]-1e-12)&(truth<=bounds[:,1]+1e-12))),
                                primary_width=None if np.isnan(bounds[1]).any() else float(bounds[1,1]-bounds[1,0]),undefined_candidates=undefined)
                            writer.writerow(row);records[method].append(row);trial_benefits[method]=row['benefit']
                        if name=='shared_blind' and n==3000 and m==2:
                            primary.append(trial_benefits['joint_contrast']-trial_benefits['separate_values'])
                    for method,rows in records.items():
                        item={'scenario':name,'n':n,'policies':m,'method':method,'repetitions':repetitions}
                        for metric in ['deploy','benefit','harm','false_improvement']:
                            item[metric]=wilson([row[metric] for row in rows])
                        for metric in ['improvement','regret','primary_width','undefined_candidates','family_coverage']:
                            values=[row[metric] for row in rows if row[metric] is not None]
                            item[metric]={'mean':float(np.mean(values)) if values else None,'defined':len(values)}
                            if metric in ['improvement','regret']:
                                item[metric]['mcse']=float(np.std(values,ddof=1)/np.sqrt(len(values)))
                            if metric=='family_coverage' and values:item[metric].update(wilson(values))
                        summaries.append(item)
                    print(f'Completed {name}, n={n}, M={m}',flush=True)
    difference=float(np.mean(primary));se=float(np.std(primary,ddof=1)/np.sqrt(len(primary)))
    results={'tests_run':tests.testsRun,'test_failures':len(tests.failures),'test_errors':len(tests.errors),
        'logs':len(NAMES)*4*repetitions,'primary_paired_benefit_difference':{'mean':difference,'mcse':se,'normal95':[difference-1.96*se,difference+1.96*se]},
        'max_joint_reference_difference':max_discrepancy,'summaries':summaries,'elapsed_seconds':time.perf_counter()-start,
        'novel_method_gate':'REJECTED: algebraically identical shared-region robust objective',
        'not_executed':['OBD','general smoothness-constrained LP','MVAL or active acquisition','PoLeCe implementation','adaptive logs','unknown target mass inference']}
    (OUT/'results.json').write_text(json.dumps(results,indent=2));(OUT/'configurations.json').write_text(json.dumps(configs,indent=2))
    timings=[]
    rng=np.random.default_rng(44)
    for s in [2,100,1000]:
        for m in [2,32,128]:
            pi=rng.dirichlet([1,1,1],(m,s));base=pi[0];p=np.full(s,1/s);lo=np.full((s,3),.2);hi=np.full((s,3),.8)
            elapsed=[]
            for _ in range(5):
                tick=time.perf_counter()
                for candidate in pi:contrast_bounds(candidate,base,p,lo,hi)
                elapsed.append(time.perf_counter()-tick)
            timings.append(dict(cells=s,actions=3,policies=m,median_seconds=float(np.median(elapsed))))
    cfg=setting('full_overlap',2);x,a,r=draw(cfg,100000,77);elapsed=[]
    for _ in range(5):
        tick=time.perf_counter();aggregate(x,a,r,2,3);elapsed.append(time.perf_counter()-tick)
    (OUT/'runtime.json').write_text(json.dumps({'projection':timings,'aggregate_100000_median_seconds':float(np.median(elapsed))},indent=2))
    print(json.dumps({k:v for k,v in results.items() if k!='summaries'},indent=2),flush=True)


if __name__=='__main__':run()
