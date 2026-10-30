"""Frozen comparative experiment. Oracle means stay in generator/metrics."""
from pathlib import Path
from statistics import NormalDist
import csv,hashlib,io,json,platform,time,unittest
import numpy as np
from likelihood import *

ROOT=Path(__file__).resolve().parent
NAMES=['rare','regular','null_rare','heterogeneous','weak_overlap','many_strata','no_overlap','hidden_confounding']
METHODS=['split_LR','mixture_LR','KL_box','Hoeffding_box','Wald_Bonferroni','retain_logger']


def scenario(name):
    s=32 if name=='many_strata' else 8;e=.1
    q=np.tile([.002,.02],(s,1))
    if name=='regular':q[:]=[.2,.4]
    if name=='null_rare':q[:]=[.01,.01]
    if name=='heterogeneous':q[:,0]=.1;q[:,1]=np.where(np.arange(s)%2,.02,.25)
    if name=='weak_overlap':e=.001;q[:]=[.1,.2]
    if name=='no_overlap':e=0
    if name=='hidden_confounding':e=.5;q[:]=[.6,.5]
    observed=q.copy()
    if name=='hidden_confounding':observed[:,1]=.82
    mu=np.tile([1-e,e],(s,1));base=mu.copy();target=np.tile([0.,1.],(s,1))
    rng=np.random.default_rng(915);policies=[base,target]
    for _ in range(30):
        lam=rng.random((s,1));policies.append((1-lam)*base+lam*target)
    c=(np.asarray(policies)-base)/s
    return c.reshape(32,-1),q.ravel(),observed.ravel(),(mu/s).ravel()


def draw(n,prob,observed,seed):
    rng=np.random.default_rng(seed);n0=rng.multinomial(n//2,prob);n1=rng.multinomial(n-n//2,prob)
    return n0,rng.binomial(n0,observed),n1,rng.binomial(n1,observed)


def estimates(c,n0,k0,n1,k1):
    n=n0+n1;k=k0+k1
    out=[bounds(c,*split_region(n0,k0,n1,k1)),bounds(c,*mixture_region(n,k))]
    out.append(project_box(c,*kl_box(n,k)))
    phat=np.divide(k,n,out=np.full(len(n),.5),where=n>0)
    h=np.sqrt(np.log(2*len(n)/.05)/(2*np.maximum(n,1)))
    lo=np.where(n>0,np.maximum(0,phat-h),0);hi=np.where(n>0,np.minimum(1,phat+h),1)
    out.append(project_box(c,lo,hi))
    point=c@phat;variance=(c*c)@(phat*(1-phat)/np.maximum(n,1))
    z=NormalDist().inv_cdf(1-.05/(2*31));rad=z*np.sqrt(variance)
    wb=np.column_stack([point-rad,point+rad]);wb[np.any((n==0)&(abs(c)>1e-12),axis=1)]=np.nan
    wb[0]=0;out.append(wb)
    keep=np.full_like(wb,np.nan);keep[0]=0;out.append(keep)
    return out


def rate(v):
    v=np.asarray(v);m=float(v.mean());n=len(v);z=1.96
    center=(m+z*z/(2*n))/(1+z*z/n);rad=z*np.sqrt(m*(1-m)/n+z*z/(4*n*n))/(1+z*z/n)
    return {'mean':m,'mcse':float(np.sqrt(m*(1-m)/n)),'wilson95':[float(center-rad),float(center+rad)]}


def run():
    out=ROOT/'results';out.mkdir(exist_ok=True)
    stream=io.StringIO();test=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.discover(str(ROOT),pattern='test_likelihood.py'))
    (out/'tests.txt').write_text(stream.getvalue());print(stream.getvalue(),flush=True)
    if not test.wasSuccessful():raise SystemExit(1)
    manifest={'python':platform.python_version(),'numpy':np.__version__,'protocol_sha256':hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest(),
        'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob('*.py')},'tests_passed':test.testsRun}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2))
    start=time.perf_counter();summaries=[];paired=[];primary_decisions=[]
    fields=['scenario','n','rep','seed','method','selected','benefit','false_improvement','harm','gain','regret','family_coverage','primary_width','undefined']
    with (out/'trials.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for si,name in enumerate(NAMES):
            c,truth,observed,prob=scenario(name);delta=c@truth
            for ni,n in enumerate([6000,60000]):
                records={method:[] for method in METHODS}
                for rep in range(500):
                    seed=2200000+si*100000+ni*10000+rep
                    n0,k0,n1,k1=draw(n,prob,observed,seed)
                    output=estimates(c,n0,k0,n1,k1);benefits={}
                    for method,b in zip(METHODS,output):
                        lower=np.where(np.isnan(b[:,0]),-np.inf,b[:,0]);j=int(np.argmax(lower))
                        if lower[j]<=1e-10:j=0
                        gain=float(delta[j]);undefined=int(np.isnan(b[:,0]).sum())
                        row=dict(scenario=name,n=n,rep=rep,seed=seed,method=method,selected=j,
                            benefit=int(j!=0 and gain>1e-12),false_improvement=int(j!=0 and gain<=1e-12),harm=int(gain < -1e-12),
                            gain=gain,regret=float(max(delta)-gain),family_coverage=None if undefined else int(np.all((b[:,0]<=delta+1e-9)&(delta<=b[:,1]+1e-9))),
                            primary_width=None if np.isnan(b[1]).any() else float(b[1,1]-b[1,0]),undefined=undefined)
                        writer.writerow(row);records[method].append(row);benefits[method]=row['benefit']
                    if name=='rare' and n==60000:
                        paired.append(benefits['split_LR']-benefits['KL_box']);primary_decisions.append(benefits)
                for method,rows in records.items():
                    summary={'scenario':name,'n':n,'method':method,'repetitions':500}
                    for metric in ['benefit','false_improvement','harm']:
                        summary[metric]=rate([v[metric] for v in rows])
                    for metric in ['gain','regret','family_coverage','primary_width','undefined']:
                        values=[v[metric] for v in rows if v[metric] is not None]
                        summary[metric]={'mean':float(np.mean(values)) if values else None,'defined':len(values)}
                        if metric=='family_coverage' and values:summary[metric].update(rate(values))
                    summaries.append(summary)
                print(f'Completed {name}, n={n}, time={time.perf_counter()-start:.1f}s',flush=True)
    mean=float(np.mean(paired));se=float(np.std(paired,ddof=1)/np.sqrt(500))
    result={'logs':8000,'tests':test.testsRun,'elapsed_seconds':time.perf_counter()-start,'primary_paired_difference':{'mean':mean,'mcse':se,'normal95':[mean-1.96*se,mean+1.96*se]},
        'empirical_primary_power_gate_passed':mean>=.1 and mean-1.96*se>0,'summaries':summaries,'primary_decisions':primary_decisions,
        'novelty_status':'Application of established likelihood inference; unique/new algorithm NOT established'}
    (out/'results.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k not in ['summaries','primary_decisions']},indent=2),flush=True)


if __name__=='__main__':run()
