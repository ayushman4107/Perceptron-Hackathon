"""Synthetic environments and oracle metrics; isolated from core estimators."""
import numpy as np

NAMES=['shared_blind','logger_reference','full_overlap','weak_overlap','rare_rewards','null','heterogeneous','hidden_confounding','unmodeled_shift']


def setting(name,m):
    if name not in NAMES: raise ValueError(name)
    q=np.array([[.2,.6,.9],[.3,.7,.1]])
    mu=np.tile([.5,.5,0.],(2,1)); p=np.array([.5,.5]); actual=p.copy()
    base=np.tile([.6,0.,.4],(2,1)); target=np.tile([0.,.6,.4],(2,1))
    if name=='logger_reference': base=mu.copy()
    if name in ['full_overlap','rare_rewards','heterogeneous','null','unmodeled_shift']:
        mu=np.tile([.45,.45,.1],(2,1))
    if name=='weak_overlap': mu=np.tile([.4995,.0005,.5],(2,1))
    if name=='rare_rewards': q=q*.01
    if name=='null': q=np.array([[.3,.3,.8],[.5,.5,.2]])
    if name in ['heterogeneous','unmodeled_shift']:
        q=np.array([[.2,.7,.5],[.8,.4,.5]])
    if name=='unmodeled_shift': p=np.array([.9,.1]); actual=np.array([.1,.9])
    if name=='hidden_confounding':
        q=np.tile([.6,.5,.5],(2,1)); base=np.tile([1.,0.,0.],(2,1)); target=np.tile([0.,1.,0.],(2,1))
    rng=np.random.default_rng(8128)
    candidates=[base,target]
    for _ in range(m-2):
        # Prespecified heterogeneous mixtures, not fitted to reward outcomes.
        lam=rng.random((2,1)); candidates.append(base*(1-lam)+target*lam)
    return dict(name=name,q=q,mu=mu,p_log=p,p_input=p.copy(),p_actual=actual,base=base,candidates=np.asarray(candidates))


def draw(cfg,n,seed):
    rng=np.random.default_rng(seed); x=(rng.random(n)>=cfg['p_log'][0]).astype(int)
    if cfg['name']=='hidden_confounding':
        u=rng.integers(0,2,n); e=np.where(u==0,.1,.9)
        a=(rng.random(n)<e).astype(int)
        probability=np.where(a==1,e,.6)
    else:
        a=(rng.random(n)[:,None]>=np.cumsum(cfg['mu'][x],axis=1)).sum(1)
        probability=cfg['q'][x,a]
    r=(rng.random(n)<probability).astype(float)
    return x,a,r


def oracle_differences(cfg):
    return np.sum(cfg['p_actual'][None,:,None]*(cfg['candidates']-cfg['base'])*cfg['q'],axis=(1,2))
