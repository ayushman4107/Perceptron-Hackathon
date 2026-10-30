"""Frozen-policy OBD evaluation; reference outcomes accessed only after inference."""
import csv,hashlib,json,time
from pathlib import Path
import methods as m
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)

def counts(a,y,A):return np.bincount(a,minlength=A),np.bincount(a,weights=y,minlength=A).astype(int)
def load(key):
    with np.load(ROOT/'data'/f'{key}.npz') as f:d={k:f[k] for k in f.files}
    keep=d['position']==d['position'].min();return {k:v[keep] for k,v in d.items()}
def split(ts,kind):
    unique,inverse=np.unique(ts,return_inverse=True)
    if kind=='random':u=np.random.default_rng(731029).random(len(unique));label=np.where(u<.2,0,np.where(u<.6,1,2))
    else:label=np.where(np.arange(len(unique))<len(unique)*.2,0,np.where(np.arange(len(unique))<len(unique)*.6,1,2))
    return label[inverse]
def plain(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return x.item()
    raise TypeError(str(type(x)))

def block_bootstrap(a,y,ts,inside,ks,A,reps=1000):
    # Cluster diagnostic over fixed 15-minute bins; not the formal binomial certificate.
    block=(ts//(15*60*10**9));unique,inv=np.unique(block,return_inverse=True);B=len(unique)
    ng=np.empty((len(ks),B,2));kg=np.empty_like(ng)
    totaln=np.bincount(inv,minlength=B);totalk=np.bincount(inv,weights=y,minlength=B)
    for i,g in enumerate(inside):
        pick=g[a];ni=np.bincount(inv[pick],minlength=B);ki=np.bincount(inv[pick],weights=y[pick],minlength=B)
        ng[i]=np.stack((ni,totaln-ni),axis=-1);kg[i]=np.stack((ki,totalk-ki),axis=-1)
    rng=np.random.default_rng(731030);weights=rng.multinomial(B,np.full(B,1/B),reps)
    nn=np.einsum('rb,mbd->rmd',weights,ng);kk=np.einsum('rb,mbd->rmd',weights,kg)
    values=(1-ks/A)*(kk[:,:,0]/nn[:,:,0]-kk[:,:,1]/nn[:,:,1])
    return dict(intervals=np.quantile(values,[.025,.975],axis=0).T,blocks=B,repetitions=reps,block_minutes=15)

def random_campaign(campaign,kind):
    d=load('random_'+campaign);a,y,ts=d['action'],d['reward'],d['timestamp'];A=int(a.max()+1)
    assert np.allclose(d['pscore'],1/A,rtol=0,atol=1e-14)
    labels=split(ts,kind);n0,k0=counts(a[labels==0],y[labels==0],A);n,k=counts(a[labels==1],y[labels==1],A)
    certidx=np.flatnonzero(labels==1);fold=np.random.default_rng(731031).random(len(certidx))<.5
    na,ka=counts(a[certidx[fold]],y[certidx[fold]],A);nb,kb=n-na,k-ka
    start=time.time();fit=m.evaluate(n0,k0,n,k,folds=(na,ka,nb,kb));elapsed=time.time()-start
    infer=dict(ks=fit['ks'],inside=fit['inside'],bounds=fit['bounds'],points=fit['points'])
    frozen=json.dumps(infer,default=plain,sort_keys=True).encode();inference_hash=hashlib.sha256(frozen).hexdigest()
    # Only now inspect reference rewards. They do not enter any fitting or interval construction above.
    ref=labels==2;rn,rk=counts(a[ref],y[ref],A);gn,gk=m.aggregate(rn,rk,fit['inside']);gc=fit['group_c']
    means=gk/gn;reference=np.sum(gc*means,axis=1)
    se=np.sqrt(np.sum(gc*gc*means*(1-means)/gn,axis=1))
    reference_wald=np.stack((reference-1.96*se,reference+1.96*se),axis=1)
    reference_exact=m.box_bounds(gc,*m.box(gn,gk,alpha=.05/len(fit['ks']),kind='exact'))
    witness={}
    for i,kk in enumerate(fit['ks']):
        r=m.radius(fit['group_n'][i],fit['group_k'][i],fit['group_n0'][i],fit['group_k0'][i],alpha=.05/len(fit['ks']))
        u,q,div,primal=m.upper(-gc[i],fit['group_n'][i],fit['group_k'][i],r,True)
        witness[str(kk)]=dict(group_means=q[0],kl_used=div[0],kl_budget=r,primal_gain=-primal[0],lower_bound=-u[0],
            # A bound on uniform absolute group-mean drift, NOT a hidden-confounding sensitivity result.
            mean_drift_tolerance=max(0,-u[0])/(2*(1-kk/A)))
    result=dict(campaign=campaign,split=kind,position=int(d['position'].min()),n_actions=A,
        first_position_rows=len(a),unique_timestamps=len(np.unique(ts)),counts=[int((labels==i).sum()) for i in range(3)],
        clicks=[int(y[labels==i].sum()) for i in range(3)],inference_seconds=elapsed,inference_sha256_before_reference=inference_hash,
        ks=fit['ks'],policies=fit['pi'],top_items=[np.flatnonzero(x) for x in fit['inside']],bounds=fit['bounds'],points=fit['points'],
        reference=reference,reference_wald95=reference_wald,reference_exact_family95=reference_exact,
        reference_block_bootstrap=block_bootstrap(a[ref],y[ref],ts[ref],fit['inside'],fit['ks'],A),
        cert_block_bootstrap=block_bootstrap(a[labels==1],y[labels==1],ts[labels==1],fit['inside'],fit['ks'],A),
        group_n=fit['group_n'],group_k=fit['group_k'],pilot_n=n0,pilot_k=k0,cert_n=n,cert_k=k,
        reference_n=rn,reference_k=rk,witness=witness)
    (OUT/f'obd_{campaign}_{kind}.json').write_text(json.dumps(result,default=plain,indent=2))
    print(campaign,kind,'counts',result['counts'],'reference',reference,'group lower',fit['bounds']['group_predictive'][:,0],flush=True)
    return result

def bts_to_random():
    d=load('bts_men');r=load('random_men');a,y,p=d['action'],d['reward'],d['pscore'];A=34;w=1/A/p
    ips=w*y;snips=ips.sum()/w.sum();fold=np.random.default_rng(731040).random(len(y))<.5
    dr=np.zeros(len(y))
    for f in (False,True):
        train=fold!=f;test=~train;n,k=counts(a[train],y[train],A);q=(k+.5)/(n+1)
        dr[test]=q.mean()+w[test]*(y[test]-q[a[test]])
    def mean_ci(z):
        mean=float(z.mean());se=float(z.std(ddof=1)/np.sqrt(len(z)));return dict(mean=mean,wald95=[mean-1.96*se,mean+1.96*se])
    result=dict(behavior='bts',evaluation='uniform random',campaign='men',position=1,
        n_behavior=len(y),n_reference=len(r['reward']),observed_bts=mean_ci(y),on_policy_random=mean_ci(r['reward']),
        ips=mean_ci(ips),snips=snips,dr=mean_ci(dr),weight_max=float(w.max()),weight_ess=float(w.sum()**2/(w*w).sum()),
        nonzero_reward_weight_ess=float(ips.sum()**2/(ips*ips).sum()),min_propensity=float(p.min()),
        actions_observed=np.unique(a).tolist(),clipped_ips={str(cap):float((np.minimum(w,cap)*y).mean()) for cap in (10,50,100,1000)},
        note='On-policy reference is an independent empirical estimate; not exact truth. Supplied BTS propensities are Monte Carlo approximations. Wald intervals are asymptotic.')
    (OUT/'bts_to_random.json').write_text(json.dumps(result,indent=2));print('BTS benchmark',json.dumps(result),flush=True)
    return result

def main():
    manifest=dict(protocol_sha256=hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest(),
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'methods.py',ROOT/'real_experiment.py']})
    (OUT/'real_manifest.json').write_text(json.dumps(manifest,indent=2))
    results=[]
    for campaign in ('all','men','women'):
        for kind in ('random','chronological'):results.append(random_campaign(campaign,kind))
    bts_to_random()
    rows=[]
    for r in results:
        for method,b in r['bounds'].items():
            for i,k in enumerate(r['ks']):rows.append(dict(campaign=r['campaign'],split=r['split'],k=int(k),method=method,
                lower=float(b[i,0]),upper=float(b[i,1]),width=float(b[i,1]-b[i,0]),reference=float(r['reference'][i])))
    with (OUT/'real_intervals.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
if __name__=='__main__':main()
