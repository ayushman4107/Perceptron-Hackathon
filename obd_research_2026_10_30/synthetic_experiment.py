"""Run the prespecified 8,000-log study, with held-out policy selection in every trial."""
import csv,hashlib,json,time,os
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import methods as m
import numpy as np
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results';OUT.mkdir(exist_ok=True)

def case_run(args):
    ci,A,N,design=args;start=time.time();rows=[];q=np.full(A,.004)
    if design=='heterogeneous':q=np.random.default_rng(9).permutation(np.linspace(.001,.009,A))
    if design=='rare':q=np.random.default_rng(9).permutation(np.linspace(.0001,.002,A))
    if design=='signal':q=np.r_[np.full(A//10,.015),np.full(A-A//10,.002)]
    for rep in range(500):
        rng=np.random.default_rng(831000+100000*ci+rep)
        n0=rng.multinomial(N//5,np.full(A,1/A));k0=rng.binomial(n0,q)
        n=rng.multinomial(N-N//5,np.full(A,1/A));k=rng.binomial(n,q)
        ka=rng.binomial(k,.5);fa=rng.binomial(n-k,.5);na=ka+fa
        fit=m.evaluate(n0,k0,n,k,folds=(na,ka,n-na,k-ka));truth=fit['c']@q
        for name,b in fit['bounds'].items():
            chosen=int(np.argmax(b[:,0]));deploy=bool(b[chosen,0]>1e-10)
            rows.append(dict(case=ci,actions=A,n_total=N,design=design,rep=rep,method=name,
                covered=int(np.all((b[:,0]<=truth+1e-9)&(b[:,1]>=truth-1e-9))),
                false_improvement=int(np.any((b[:,0]>1e-10)&(truth<=1e-12))),
                beneficial=int(deploy and truth[chosen]>1e-12),deployed=int(deploy),
                selected_gain=float(truth[chosen]) if deploy else 0.,
                regret=float(max(0,truth.max())-(truth[chosen] if deploy else 0)),
                median_width=float(np.median(b[:,1]-b[:,0])),chosen_k=int(fit['ks'][chosen]) if deploy else 0))
    path=OUT/f'synthetic_case_{ci:02d}.csv'
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return dict(case=ci,actions=A,n_total=N,design=design,seconds=time.time()-start,rows=len(rows))

def main():
    cases=[(i,*values) for i,values in enumerate((A,N,d) for A in (20,80) for N in (10000,50000) for d in ('null','heterogeneous','rare','signal'))]
    manifest=dict(protocol_sha256=hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest(),
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'methods.py',ROOT/'synthetic_experiment.py',ROOT/'test_methods.py')},cases=cases,replications=500)
    (OUT/'synthetic_manifest.json').write_text(json.dumps(manifest,indent=2))
    start=time.time();runtime=[]
    with ProcessPoolExecutor(max_workers=4) as pool:
        jobs=[pool.submit(case_run,x) for x in cases]
        for future in as_completed(jobs):
            result=future.result();runtime.append(result);print(json.dumps(result),flush=True)
    (OUT/'synthetic_runtime.json').write_text(json.dumps(dict(total_seconds=time.time()-start,cases=runtime),indent=2))
if __name__=='__main__':main()
