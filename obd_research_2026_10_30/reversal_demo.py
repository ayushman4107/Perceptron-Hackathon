"""A coherent logged-data before/after reversal with known randomized propensities."""
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent
rng=np.random.default_rng(43107);N=100000
q=np.array([[.2,.1],[.8,.7]])
old_pop=np.array([.8,.2]);new_pop=np.array([.2,.8]);old_pi=np.array([.8,.2]);new_pi=np.array([.2,.8])
x0=rng.choice(2,N,p=old_pop);a0=rng.choice(2,N,p=old_pi);y0=rng.binomial(1,q[x0,a0])
x1=rng.choice(2,N,p=new_pop);a1=rng.choice(2,N,p=new_pi);y1=rng.binomial(1,q[x1,a1])
# Only the CURRENT logger's chosen-action rewards enter OPE.
scores=(new_pi[a1]-old_pi[a1])/new_pi[a1]*y1
estimate=float(scores.mean());se=float(scores.std(ddof=1)/np.sqrt(N))
truth=float(np.sum(new_pop[:,None]*(new_pi-old_pi)*q))
result=dict(seed=43107,n_before=N,n_after=N,q=q.tolist(),old_population=old_pop.tolist(),new_population=new_pop.tolist(),
    old_policy=old_pi.tolist(),new_policy=new_pi.tolist(),observed_before=float(y0.mean()),observed_after=float(y1.mean()),
    naive_change=float(y1.mean()-y0.mean()),ips_policy_effect=estimate,ips_wald95=[estimate-1.96*se,estimate+1.96*se],
    true_effect_same_new_population=truth,expected_before=float(np.sum(old_pop[:,None]*old_pi*q)),
    expected_after=float(np.sum(new_pop[:,None]*new_pi*q)),minimum_logged_propensity=.2)
assert result['naive_change']>0 and estimate<0 and abs(truth+.06)<1e-12
(ROOT/'results/reversal_demo.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
