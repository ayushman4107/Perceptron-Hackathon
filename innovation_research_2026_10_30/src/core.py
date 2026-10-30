"""Research verification of established confidence-set policy comparison.

No novelty claim. NumPy only. No simulator truth enters these functions.
"""
import numpy as np


def policy(p):
    p=np.asarray(p,float)
    if p.ndim!=2 or not p.size or not np.isfinite(p).all() or (p<0).any() or not np.allclose(p.sum(1),1,atol=1e-12,rtol=0):
        raise ValueError('Expected finite S by K probability table')
    return p


def masses(p,s):
    p=np.asarray(p,float)
    if p.shape!=(s,) or not np.isfinite(p).all() or (p<0).any() or not np.isclose(p.sum(),1,atol=1e-12,rtol=0):
        raise ValueError('Expected known target population probabilities')
    return p


def aggregate(x,a,r,s,k):
    x,a,r=map(np.asarray,(x,a,r))
    if s<1 or k<1 or x.ndim!=1 or a.shape!=x.shape or r.shape!=x.shape:
        raise ValueError('Invalid dimensions')
    if not np.issubdtype(x.dtype,np.integer) or not np.issubdtype(a.dtype,np.integer):
        raise ValueError('Integer context/action labels required')
    if (x<0).any() or (x>=s).any() or (a<0).any() or (a>=k).any() or not np.isfinite(r).all() or (r<0).any() or (r>1).any():
        raise ValueError('Invalid labels/rewards')
    idx=x*k+a
    return np.bincount(idx,minlength=s*k).reshape(s,k),np.bincount(idx,weights=r,minlength=s*k).reshape(s,k)


def confidence_box(count,total,alpha=.05):
    count,total=np.asarray(count,float),np.asarray(total,float)
    if count.ndim!=2 or not count.size or total.shape!=count.shape or not np.isfinite(count).all() or not np.isfinite(total).all() or (count<0).any() or (count!=np.floor(count)).any() or (total<0).any() or (total>count).any() or not 0<alpha<1:
        raise ValueError('Invalid sufficient statistics/alpha')
    mean=np.divide(total,count,out=np.full_like(total,.5),where=count>0)
    h=np.sqrt(np.log(2*count.size/alpha)/(2*np.maximum(count,1)))
    return np.where(count>0,np.maximum(0,mean-h),0),np.where(count>0,np.minimum(1,mean+h),1)


def validate_box(lo,hi,shape):
    lo,hi=np.asarray(lo,float),np.asarray(hi,float)
    if lo.shape!=shape or hi.shape!=shape or not np.isfinite(lo).all() or not np.isfinite(hi).all() or (lo<0).any() or (hi>1).any() or (hi<lo).any():
        raise ValueError('Invalid confidence box')
    return lo,hi


def contrast_bounds(pi,base,p,lo,hi):
    pi,base=policy(pi),policy(base)
    if pi.shape!=base.shape: raise ValueError('Policy shape mismatch')
    p=masses(p,len(pi)); lo,hi=validate_box(lo,hi,pi.shape)
    c=p[:,None]*(pi-base)
    return float(np.sum(c*np.where(c>=0,lo,hi))),float(np.sum(c*np.where(c>=0,hi,lo)))


def robust_reference(pi,base,p,lo,hi):
    # Independently structured scalar minimization of the same robust objective.
    lower=upper=0.
    for s in range(len(p)):
        for a in range(len(pi[s])):
            coefficient=float(p[s])*(float(pi[s][a])-float(base[s][a]))
            left=coefficient*float(lo[s][a]); right=coefficient*float(hi[s][a])
            lower+=min(left,right); upper+=max(left,right)
    return lower,upper


def separate_bounds(pi,base,p,lo,hi):
    p=np.asarray(p)[:,None]
    return float(np.sum(p*(pi*lo-base*hi))),float(np.sum(p*(pi*hi-base*lo)))


def select(lower):
    lower=np.asarray(lower,float)
    if lower.ndim!=1 or not len(lower) or np.isinf(lower).any(): raise ValueError('Invalid lower bounds')
    valid=np.where(np.isnan(lower),-np.inf,lower)
    j=int(np.argmax(valid))
    return j if valid[j]>1e-12 else 0


def dr_intervals(x,a,r,mu,candidates,base,misspecified=False):
    """Paired two-fold DR, logging population; no simultaneous Wald claim."""
    n=len(x); s,k=mu.shape
    if n<2: raise ValueError('At least two observations required')
    qhat=np.empty((n,k))
    folds=np.arange(n)%2
    for fold in (0,1):
        train=folds!=fold; test=~train
        count,total=aggregate(x[train],a[train],r[train],s,k)
        fit=(total+.5)/(count+1)
        if misspecified: fit[:]=.5
        qhat[test]=fit[x[test]]
    out=[]
    for pi in candidates:
        d=pi-base
        if np.any((mu==0)&(np.abs(d)>1e-12)):
            out.append((np.nan,np.nan)); continue
        z=np.sum(d[x]*qhat,axis=1)+d[x,a]/mu[x,a]*(r-qhat[np.arange(n),a])
        mean=z.mean(); rad=1.96*z.std(ddof=1)/np.sqrt(n)
        out.append((mean-rad,mean+rad))
    return np.asarray(out)
