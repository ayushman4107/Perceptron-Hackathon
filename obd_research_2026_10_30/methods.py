"""Policy-ratio compression with established likelihood confidence constructions."""
import sys,math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.deps'))
import numpy as np
from scipy.special import betaln,xlogy,xlog1py
from scipy.stats import beta,norm

def kl(p,q):
    p,q=np.broadcast_arrays(np.asarray(p,float),np.asarray(q,float))
    with np.errstate(divide='ignore',invalid='ignore'):
        return np.maximum(xlogy(p,p)-xlogy(p,q)+xlog1py(1-p,-p)-xlog1py(1-p,-q),0)

def validate(n,k):
    n,k=np.broadcast_arrays(np.asarray(n,float),np.asarray(k,float))
    if n.ndim<1 or not np.isfinite(n).all() or not np.isfinite(k).all() or (n<0).any() or (k<0).any() or (k>n).any() or (n%1).any() or (k%1).any():raise ValueError('Invalid binomial counts')
    return n,k

def radius(n,k,n0=None,k0=None,alpha=.05,kind='predictive'):
    n,k=validate(n,k)
    if not 0<alpha<1:raise ValueError('Invalid alpha')
    p=np.divide(k,n,out=np.full_like(k,.5),where=n>0)
    mle=np.sum(xlogy(k,p)+xlog1py(n-k,-p),axis=-1)
    jeff=np.sum(betaln(k+.5,n-k+.5)-betaln(.5,.5),axis=-1)
    if kind=='jeffreys':numerator=jeff
    else:
        n0,k0=validate(n0,k0)
        if n0.shape!=n.shape:raise ValueError('Pilot shape mismatch')
        if kind=='split':
            pred=(k0+.5)/(n0+1)
            numerator=np.sum(xlogy(k,pred)+xlog1py(n-k,-pred),axis=-1)
        elif kind=='predictive':
            posterior=np.sum(betaln(k+k0+.5,n-k+n0-k0+.5)-betaln(k0+.5,n0-k0+.5),axis=-1)
            numerator=np.logaddexp(posterior,jeff)-math.log(2)
        else:raise ValueError('Unknown likelihood construction')
    return math.log(1/alpha)+mle-numerator

def tilted(p,t):
    disc=np.sqrt((1-t)**2+4*t*p)
    with np.errstate(divide='ignore',invalid='ignore'):
        small=np.divide(2*p,1-t+disc,out=np.zeros_like(disc),where=1-t+disc>0)
        large=np.divide(t-1+disc,2*t,out=np.array(p,copy=True),where=t>0)
    return np.clip(np.where(t<=1,small,large),0,1)

def upper(c,n,k,r,details=False):
    n,k=validate(n,k);c,n,k=np.broadcast_arrays(np.atleast_2d(np.asarray(c,float)),np.atleast_2d(n),np.atleast_2d(k))
    r=np.broadcast_to(np.asarray(r,float),(len(c),))
    if not np.isfinite(c).all() or not np.isfinite(r).all() or (r<0).any():raise ValueError('Invalid objective or radius')
    observed=n>0;safe=np.maximum(n,1);p=k/safe
    cc=np.where(observed,c,0);pp=np.where(cc>=0,p,1-p)
    missing=np.sum(np.where(observed,0,np.maximum(c,0)),axis=1)
    def calc(lam):
        z=tilted(pp,abs(cc)/(lam[:,None]*safe));q=np.where(cc>=0,z,1-z)
        divergence=np.sum(safe*kl(p,q)*observed,axis=1)
        primal=np.sum(cc*q,axis=1)
        return divergence,primal,q
    left=np.zeros(len(c));right=np.ones(len(c))
    for _ in range(100):
        bad=calc(right)[0]>r
        if not bad.any():break
        right[bad]*=2
    else:raise RuntimeError('Could not bracket dual')
    for _ in range(65):
        mid=(left+right)/2;bad=calc(mid)[0]>r
        left=np.where(bad,mid,left);right=np.where(bad,right,mid)
    div,primal,q=calc(right)
    result=np.minimum(np.maximum(cc,0).sum(1),primal+right*(r-div)+1e-10)+missing
    q=np.where(observed,q,(c>0).astype(float));result[np.all(c==0,axis=1)]=0
    if details:return result,q,div,np.sum(c*q,axis=1)
    return result

def lr_bounds(c,n,k,r):return np.stack((-upper(-np.asarray(c),n,k,r),upper(c,n,k,r)),axis=-1)

def box(n,k,alpha=.05,kind='kl'):
    n,k=validate(n,k);D=n.shape[-1]
    if kind=='exact':
        lo=np.where(k==0,0,beta.ppf(alpha/(2*D),k,n-k+1))
        hi=np.where(k==n,1,beta.ppf(1-alpha/(2*D),k+1,n-k))
        return lo,hi
    p=np.divide(k,n,out=np.full_like(k,.5),where=n>0);threshold=math.log(2*D/alpha)/np.maximum(n,1)
    left=np.zeros_like(p);right=p.copy()
    for _ in range(60):
        mid=(left+right)/2;bad=kl(p,mid)>threshold
        left=np.where(bad,mid,left);right=np.where(bad,right,mid)
    lo=np.where(n>0,left,0)
    left=p.copy();right=np.ones_like(p)
    for _ in range(60):
        mid=(left+right)/2;bad=kl(p,mid)>threshold
        right=np.where(bad,mid,right);left=np.where(bad,left,mid)
    return lo,np.where(n>0,right,1)

def box_bounds(c,lo,hi):
    return np.stack((np.sum(c*np.where(c>=0,lo,hi),axis=-1),np.sum(c*np.where(c>=0,hi,lo),axis=-1)),axis=-1)

def compress(mu,pi,labels):
    """Verify exact signed-ratio grouping; return group masses and coefficients."""
    mu,pi=np.asarray(mu,float),np.asarray(pi,float);labels=np.asarray(labels)
    if mu.ndim!=1 or mu.shape!=pi.shape or labels.shape!=mu.shape or (mu<=0).any() or (pi<0).any() or not np.isclose(mu.sum(),1) or not np.isclose(pi.sum(),1):raise ValueError('Invalid supported policy')
    ratio=(pi-mu)/mu;mass=[];coeff=[]
    for g in np.unique(labels):
        idx=labels==g
        if np.ptp(ratio[idx])>1e-12:raise ValueError('Grouping does not preserve the contrast')
        mass.append(mu[idx].sum());coeff.append((pi[idx]-mu[idx]).sum())
    return np.array(mass),np.array(coeff)

def policies(n0,k0):
    A=len(n0);ks=np.array([k for k in (1,3,5,10,20) if k<A]);rank=np.lexsort((np.arange(A),-(k0+.5)/(n0+1)))
    inside=np.zeros((len(ks),A),bool)
    for i,k in enumerate(ks):inside[i,rank[:k]]=True
    pi=inside/ks[:,None];c=pi-1/A
    return ks,inside,pi,c

def aggregate(n,k,inside):
    n1=inside@np.asarray(n);k1=inside@np.asarray(k)
    return np.stack((n1,np.sum(n)-n1),axis=-1),np.stack((k1,np.sum(k)-k1),axis=-1)

def score_stats(n,k,c,mu=None,q=None):
    n,k=np.asarray(n),np.asarray(k);N=n.sum();A=len(n)
    if mu is None:mu=np.full(A,1/A)
    if q is None:q=np.zeros(A)
    weight=c/mu;constant=c@q
    z1=constant[:,None]+weight*(1-q);z0=constant[:,None]-weight*q
    sums=z1@k+z0@(n-k);squares=(z1*z1)@k+(z0*z0)@(n-k)
    return sums,squares,N

def evaluate(n0,k0,n,k,alpha=.05,folds=None):
    ks,inside,pi,c=policies(n0,k0);M=len(ks);A=len(n)
    gn,gk=aggregate(n,k,inside);gn0,gk0=aggregate(n0,k0,inside)
    gc=np.stack((1-ks/A,-(1-ks/A)),axis=1);result={}
    for kind in ('split','predictive','jeffreys'):
        result['item_'+kind]=lr_bounds(c,n,k,radius(n,k,n0,k0,alpha,kind))
        result['group_'+kind]=lr_bounds(gc,gn,gk,radius(gn,gk,gn0,gk0,alpha/M,kind))
    result['item_kl']=box_bounds(c,*box(n,k,alpha))
    for kind in ('kl','exact'):
        result['group_'+kind]=box_bounds(gc,*box(gn,gk,alpha/M,kind))
    z=norm.ppf(1-alpha/(2*M));s,ss,N=score_stats(n,k,c)
    est=s/N;se=np.sqrt(np.maximum((ss-s*s/N)/(N-1)/N,0))
    result['ips_wald']=np.stack((est-z*se,est+z*se),axis=1)
    points={'ips':est,'snips':(pi@k)/(pi@n)-k.sum()/N,
        'group':np.sum(gc*np.divide(gk,gn,out=np.full_like(gk,.5,dtype=float),where=gn>0),axis=1)}
    if folds is not None:
        na,ka,nb,kb=folds
        assert np.array_equal(na+nb,n) and np.array_equal(ka+kb,k)
        s1,ss1,_=score_stats(na,ka,c,q=(kb+.5)/(nb+1));s2,ss2,_=score_stats(nb,kb,c,q=(ka+.5)/(na+1))
        s=s1+s2;ss=ss1+ss2;est=s/N;se=np.sqrt(np.maximum((ss-s*s/N)/(N-1)/N,0))
        result['dr_wald']=np.stack((est-z*se,est+z*se),axis=1);points['dr']=est
    return dict(ks=ks,inside=inside,pi=pi,c=c,group_n=gn,group_k=gk,group_n0=gn0,group_k0=gk0,group_c=gc,bounds=result,points=points)
