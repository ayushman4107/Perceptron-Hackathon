"""Finite-tabular Bernoulli confidence-region projection; established LR ideas."""
import math
import numpy as np


def stats(n,k):
    n,k=np.asarray(n,float),np.asarray(k,float)
    if n.shape!=k.shape or n.ndim!=1 or not len(n) or not np.isfinite(n).all() or not np.isfinite(k).all() or (n<0).any() or (k<0).any() or (k>n).any() or (n!=np.floor(n)).any() or (k!=np.floor(k)).any():raise ValueError('Invalid binomial statistics')
    return n,k


def kl(p,q):
    p,q=np.broadcast_arrays(np.asarray(p,float),np.asarray(q,float))
    if not np.isfinite(p).all() or not np.isfinite(q).all() or (p<0).any() or (p>1).any() or (q<0).any() or (q>1).any():raise ValueError('Probabilities outside [0,1]')
    with np.errstate(divide='ignore',invalid='ignore'):
        first=np.where(p==0,0,p*(np.log(p)-np.log(q)))
        second=np.where(p==1,0,(1-p)*(np.log1p(-p)-np.log1p(-q)))
    return np.maximum(first+second,0)


def split_region(n0,k0,n1,k1,alpha=.05):
    n0,k0=stats(n0,k0);n1,k1=stats(n1,k1)
    if n0.shape!=n1.shape or not 0<alpha<1:raise ValueError('Invalid split/alpha')
    pilot=(k0+.5)/(n0+1)
    mle=np.divide(k1,n1,out=np.full_like(k1,.5),where=n1>0)
    radius=math.log(1/alpha)+float(np.sum(n1*kl(mle,pilot)))
    return n1,k1,radius


def mixture_region(n,k,alpha=.05):
    n,k=stats(n,k)
    if not 0<alpha<1:raise ValueError('Invalid alpha')
    p=np.divide(k,n,out=np.full_like(k,.5),where=n>0)
    log_mle=0.;log_mix=0.
    for ni,ki,pi in zip(n,k,p):
        if ki>0:log_mle+=ki*math.log(pi)
        if ni>ki:log_mle+=(ni-ki)*math.log1p(-pi)
        log_mix+=math.lgamma(ki+.5)+math.lgamma(ni-ki+.5)-math.lgamma(ni+1)-2*math.lgamma(.5)
    return n,k,math.log(1/alpha)+log_mle-log_mix


def tilted(p,t):
    """argmax_q t*q-KL(p||q) for t>=0, including boundary empirical means."""
    p,t=np.broadcast_arrays(np.asarray(p,float),np.asarray(t,float))
    disc=np.sqrt((1-t)**2+4*t*p)
    with np.errstate(divide='ignore',invalid='ignore'):
        small=np.divide(2*p,1-t+disc,out=np.zeros_like(disc),where=(1-t+disc)>0)
        large=np.divide(t-1+disc,2*t,out=np.array(p,copy=True),where=t>0)
    return np.clip(np.where(t<=1,small,large),0,1)


def upper(coeff,n,k,radius,details=False):
    n,k=stats(n,k);coeff=np.atleast_2d(np.asarray(coeff,float))
    if coeff.shape[1]!=len(n) or not np.isfinite(coeff).all() or not np.isfinite(radius) or radius<0:raise ValueError('Invalid contrast/radius')
    observed=n>0
    c=coeff[:,observed];nn=n[observed];p=k[observed]/nn
    missing=np.maximum(coeff[:,~observed],0).sum(1)
    if not len(nn):return missing
    pp=np.where(c>=0,p,1-p)
    def calc(lam):
        t=abs(c)/(lam[:,None]*nn)
        z=tilted(pp,t);q=np.where(c>=0,z,1-z)
        divergence=np.sum(nn*kl(p,q),axis=1)
        primal=np.sum(c*q,axis=1)
        return divergence,primal,q
    left=np.zeros(len(c));right=np.ones(len(c))
    for _ in range(100):
        bad=calc(right)[0]>radius
        if not bad.any():break
        right[bad]*=2
    else:raise RuntimeError('Dual bracket failed')
    for _ in range(65):
        mid=(left+right)/2
        too_far=calc(mid)[0]>radius
        left=np.where(too_far,mid,left);right=np.where(too_far,right,mid)
    divergence,primal,q=calc(right)
    dual=primal+right*(radius-divergence)
    # Dual is an upper bound; small conservative allowance for floating-point error.
    result=np.minimum(np.maximum(c,0).sum(1),dual+1e-10)+missing
    zero=np.all(coeff==0,axis=1);result[zero]=0
    if details:return result,primal+missing,q,divergence
    return result


def bounds(coeff,n,k,radius):
    return np.column_stack([-upper(-np.asarray(coeff),n,k,radius),upper(coeff,n,k,radius)])


def kl_box(n,k,alpha=.05):
    n,k=stats(n,k)
    if not 0<alpha<1:raise ValueError('Invalid alpha')
    p=np.divide(k,n,out=np.full_like(k,.5),where=n>0)
    threshold=math.log(2*len(n)/alpha)/np.maximum(n,1)
    left=np.zeros_like(p);right=p.copy()
    for _ in range(60):
        mid=(left+right)/2;large=kl(p,mid)>threshold
        left=np.where(large,mid,left);right=np.where(large,right,mid)
    lower=np.where(n>0,left,0)
    left=p.copy();right=np.ones_like(p)
    for _ in range(60):
        mid=(left+right)/2;large=kl(p,mid)>threshold
        right=np.where(large,mid,right);left=np.where(large,left,mid)
    return lower,np.where(n>0,right,1)


def project_box(coeff,lo,hi):
    return np.column_stack([np.sum(coeff*np.where(coeff>=0,lo,hi),axis=1),np.sum(coeff*np.where(coeff>=0,hi,lo),axis=1)])
