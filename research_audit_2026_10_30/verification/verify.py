"""Reproducible manuscript audit; Python stdlib + NumPy only.

Run: python -X utf8 verification/verify.py (from audit directory or anywhere).
No data downloads, model packages, or network calls. Tests are not proofs.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import csv
import hashlib
import io
import json
import math
import platform
import time
import unittest
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results'


def policy_array(p):
    p = np.asarray(p, dtype=float)
    if p.ndim != 2 or not p.size or not np.isfinite(p).all():
        raise ValueError('Policy must be a nonempty finite matrix')
    if (p < 0).any() or (p > 1).any() or not np.allclose(p.sum(1), 1, atol=1e-12, rtol=0):
        raise ValueError('Invalid action probabilities')
    return p


def support_check(mu, pi):
    mu, pi = policy_array(mu), policy_array(pi)
    if mu.shape != pi.shape:
        raise ValueError('Policy shape mismatch')
    if np.any((pi > 0) & (mu == 0)):
        raise ValueError('Target support absent in known logging design')


def scores(a, r, p, pi, q):
    pi = policy_array(pi)
    a, r, p, q = map(np.asarray, (a, r, p, q))
    n, k = pi.shape
    if a.shape != (n,) or r.shape != (n,) or p.shape != (n,) or q.shape != pi.shape:
        raise ValueError('Shape mismatch')
    if not np.issubdtype(a.dtype, np.integer) or (a < 0).any() or (a >= k).any():
        raise ValueError('Invalid action')
    if not all(np.isfinite(t).all() for t in (r, p, q)) or (p <= 0).any() or (p > 1).any():
        raise ValueError('Nonfinite data or invalid selected propensity')
    # Selected propensities alone cannot certify population-wide overlap.
    w = pi[np.arange(n), a] / p
    dm = (pi * q).sum(1)
    return w, dm, w * r, dm + w * (r - q[np.arange(n), a])


def scalar_reference(a, r, p, pi, q):
    # Independently structured scalar row loop, not a call to scores().
    result = []
    for j in range(len(a)):
        ratio = float(pi[j][a[j]]) / float(p[j])
        prediction = sum(float(pi[j][b])*float(q[j][b]) for b in range(len(pi[j])))
        result.append((ratio, prediction, ratio*r[j], prediction+ratio*(r[j]-q[j][a[j]])))
    return np.asarray(result).T


def snips(w, r):
    w, r = np.asarray(w, float), np.asarray(r, float)
    if w.shape != r.shape or not w.size or not np.isfinite(w).all() or not np.isfinite(r).all() or (w < 0).any() or w.sum() <= 0:
        raise ValueError('SNIPS needs finite nonnegative nonzero weights')
    return float(w @ r / w.sum())


def ess(w):
    w = np.asarray(w, float)
    if not w.size or not np.isfinite(w).all() or (w < 0).any() or w.max() == 0:
        raise ValueError('ESS undefined')
    z = w / w.max()  # Avoid overflow for large finite weights.
    return float(z.sum()**2 / (z @ z))


def wald(z):
    z = np.asarray(z, float)
    if z.ndim != 1 or len(z) < 2 or not np.isfinite(z).all():
        raise ValueError('Variance requires at least two finite observations')
    mean, se = float(z.mean()), float(z.std(ddof=1)/np.sqrt(len(z)))
    return mean, se, mean-1.96*se, mean+1.96*se


def sensitivity(e, m, gamma):
    if not all(math.isfinite(x) for x in (e,m,gamma)) or not (0 < e < 1 and 0 <= m <= 1 and gamma >= 1):
        raise ValueError('Require 0<e<1, 0<=m<=1, finite Gamma>=1')
    # Algebraically scaled form avoids multiplying huge inverse weights by e.
    el = e + (1-e)/gamma
    eh = e + gamma*(1-e)
    return max(m*el, 1-(1-m)*eh), min(m*eh, 1-(1-m)*el)


def sensitivity_vertices(e, m, gamma):
    # Independent LP reference in success/failure population masses t, s:
    # t+s=1; em*l<=t<=em*h; e(1-m)*l<=s<=e(1-m)*h.
    lower = np.array([e*m, e*(1-m)]) * (1+(1/e-1)/gamma)
    upper = np.array([e*m, e*(1-m)]) * (1+gamma*(1/e-1))
    feasible = []
    for j in (0,1):
        for boundary in (lower[j], upper[j]):
            mat = np.array([[1.,1.], [float(j==0),float(j==1)]])
            v = np.linalg.solve(mat, [1.,boundary])
            if np.all(v >= lower-1e-10) and np.all(v <= upper+1e-10):
                feasible.append(v[0])
    if not feasible:
        raise AssertionError('LP has no feasible vertex')
    return min(feasible), max(feasible)


def crossfit_tabular(x, a, r, folds):
    """Two strata/two actions; smoothed cell means on complementary folds.
    Prior mean .5 with prior count 1 is specified even for empty cells.
    """
    out = np.empty((len(x),2))
    for fold in np.unique(folds):
        train, test = folds != fold, folds == fold
        cell = 2*x[train] + a[train]
        count = np.bincount(cell, minlength=4)
        total = np.bincount(cell, weights=r[train], minlength=4)
        fitted = ((total+.5)/(count+1)).reshape(2,2)
        out[test] = fitted[x[test]]
    return out


class MathematicalChecks(unittest.TestCase):
    def test_exact_toy(self):
        half=F(1,2)
        baseline=half*(F(9,10)*F(2,10)+F(1,10)*F(1,10))+half*(F(1,10)*F(8,10)+F(9,10)*F(7,10))
        target=half*(F(1,10)+F(7,10))
        self.assertEqual(baseline,F(45,100)); self.assertEqual(target,F(4,10))
        self.assertEqual((F(5,100)*F(1,10)+F(45,100)*F(7,10))/half,F(64,100))
        self.assertEqual(target+F(2,10)-baseline,F(15,100))
        self.assertEqual(target-baseline,F(-5,100))

    def test_exact_dr_bias_identity(self):
        for mu,b,q,h,pi in product([F(1,5),F(1,2),F(4,5)], repeat=5):
            expected=pi*h+mu*pi/b*(q-h)-pi*q
            self.assertEqual(expected,pi*(1-mu/b)*(h-q))

    def test_vector_matches_independent_reference(self):
        rng=np.random.default_rng(314)
        pi=rng.dirichlet(np.ones(4),size=100)
        mu=rng.dirichlet(np.ones(4),size=100)
        a=np.array([rng.choice(4,p=row) for row in mu]); r=rng.normal(size=100); q=rng.normal(size=(100,4))
        p=mu[np.arange(100),a]
        np.testing.assert_allclose(scores(a,r,p,pi,q),scalar_reference(a,r,p,pi,q),rtol=1e-12,atol=1e-12)

    def test_target_equals_logger(self):
        pi=np.array([[.3,.7],[.6,.4]])
        w,dm,ip,dr=scores(np.array([0,1]),np.array([0.,1.]),np.array([.3,.4]),pi,np.zeros_like(pi))
        np.testing.assert_equal(w,1); np.testing.assert_equal(ip,[0.,1.])

    def test_dr_zero_model_equals_ips(self):
        w,dm,ip,dr=scores(np.array([1,0]),np.array([1.,0.]),np.array([.1,.9]),np.array([[0.,1.],[0.,1.]]),np.zeros((2,2)))
        np.testing.assert_equal(ip,dr)

    def test_ips_variance_decomposition(self):
        mu=np.array([.7,.3]); pi=np.array([.2,.8]); q=np.array([.1,.9]); w=pi/mu
        probs=np.ravel(np.column_stack((mu*(1-q),mu*q)))
        values=np.ravel(np.column_stack((np.zeros(2),w)))
        mean=probs@values; var=probs@(values-mean)**2
        rhs=np.sum(mu*w*w*q*(1-q))+np.sum(mu*(w*q-mean)**2)
        self.assertAlmostEqual(var,rhs)

    def test_snips_range(self):
        self.assertTrue(.2 <= snips([1,100,0],[.2,.8,9]) <= .8)

    def test_snips_need_not_reduce_variance(self):
        # n=1, mu=(.5,.5), pi=(.25,.75), rewards=(1,1/3).
        ips=np.array([.5,1.5])*np.array([1.,1/3])
        self.assertAlmostEqual(ips.var(),0); self.assertGreater(np.array([1.,1/3]).var(),0)

    def test_dr_need_not_reduce_variance(self):
        # R=0, qhat=1, deterministic target, logger probability .1.
        mean=.1*(-9)+.9*1
        self.assertAlmostEqual(mean,0); self.assertAlmostEqual(.1*81+.9,9)

    def test_no_match_errors(self):
        with self.assertRaises(ValueError): snips([0,0],[1,0])
        with self.assertRaises(ValueError): ess([0,0])

    def test_ess_bounds_scaling(self):
        for w in ([1,1,1],[0,0,9],[1,2,100]):
            self.assertTrue(1 <= ess(w) <= len(w)+1e-12)
            self.assertAlmostEqual(ess(w),ess(np.asarray(w)*1e200))

    def test_empty_singleton_variance(self):
        for z in ([],[1]):
            with self.assertRaises(ValueError): wald(z)

    def test_invalid_policy(self):
        for p in ([],[[.1,.1]],[[-.1,1.1]],[[float('nan'),1]]):
            with self.assertRaises(ValueError): policy_array(p)

    def test_invalid_propensity_and_shapes(self):
        for p in ([0],[float('nan')],[1.1]):
            with self.assertRaises(ValueError): scores(np.array([1]),[1],p,[[0,1]],[[0,0]])
        with self.assertRaises(ValueError): scores(np.array([2]),[1],[.5],[[0,1]],[[0,0]])

    def test_support_not_sample_match(self):
        with self.assertRaises(ValueError): support_check([[1,0]],[[0,1]])
        support_check([[.999,.001]],[[0,1]])

    def test_sensitivity_vertex_reference(self):
        rng=np.random.default_rng(808)
        for _ in range(400):
            e=rng.uniform(.001,.999); m=rng.random(); g=rng.uniform(1,10)
            np.testing.assert_allclose(sensitivity(e,m,g),sensitivity_vertices(e,m,g),atol=1e-9,rtol=1e-9)

    def test_sensitivity_null_boundaries_monotonicity(self):
        for e in (.000001,.1,.5,.9,.999999):
            for m in (0,.1,.5,.9,1):
                np.testing.assert_allclose(sensitivity(e,m,1),[m,m],atol=1e-12)
                prev=(m,m)
                for g in (1,1.1,2,10,1e6):
                    lo,hi=sensitivity(e,m,g)
                    self.assertTrue(-1e-12<=lo<=hi+1e-12<=1+2e-12)
                    self.assertLessEqual(lo,prev[0]+1e-12); self.assertGreaterEqual(hi,prev[1]-1e-12)
                    prev=(lo,hi)

    def test_sensitivity_invalid_domain(self):
        for args in ((0,.5,1),(1,.5,1),(.5,-.1,2),(.5,.5,.9),(.5,.5,float('inf'))):
            with self.assertRaises(ValueError): sensitivity(*args)

    def test_sensitivity_exact_table(self):
        expected=[(.4,.4),(.38725,.41425),(.3775,.4275),(.3625,.4525),(1.04/3,.5)]
        for g,wanted in zip([1,1.25,1.5,2,3],expected):
            got=np.mean([sensitivity(.1,.1,g),sensitivity(.9,.7,g)],axis=0)
            np.testing.assert_allclose(got,wanted,atol=1e-12)

    def test_sensitivity_endpoint_construction(self):
        # Construct full-data Y1 masses and assignment probabilities attaining bounds.
        for e,m,g in product((.1,.5,.9),(.1,.5,.9),(1,1.5,3)):
            for t in sensitivity(e,m,g):
                e1=e*m/t; e0=e*(1-m)/(1-t)
                for p in (e1,e0):
                    odds=(p/(1-p))/(e/(1-e))
                    self.assertTrue(1/g-1e-9<=odds<=g+1e-9)
                self.assertAlmostEqual(t*e1+(1-t)*e0,e)

    def test_hidden_confounding_and_full_propensity(self):
        p=np.array([.1,.9]); q=np.array([.1,.9])
        nominal=np.mean(p*q/.5); oracle=np.mean(p*q/p)
        self.assertAlmostEqual(nominal,.82); self.assertAlmostEqual(oracle,.5)
        lo,hi=sensitivity(.5,.82,9); self.assertTrue(lo<=.5<=hi)

    def test_crossfit_excludes_own_fold(self):
        x=np.array([0,0,1,1]*5); a=np.array([0,1,0,1]*5); r=np.arange(20)%2; f=np.arange(20)%5
        q=crossfit_tabular(x,a,r,f); r2=r.copy(); r2[f==0]=1-r2[f==0]
        q2=crossfit_tabular(x,a,r2,f)
        np.testing.assert_equal(q[f==0],q2[f==0])

    def test_paired_variance_identity(self):
        z=np.array([1,2,3,5.]); b=np.array([1,3,2,6.])
        expected=z.var(ddof=1)+b.var(ddof=1)-2*np.cov(z,b,ddof=1)[0,1]
        self.assertAlmostEqual((z-b).var(ddof=1),expected)

    def test_snips_delta_gradient(self):
        a,b=.4,1.2; h=1e-6
        grad=np.array([((a+h)/b-(a-h)/b)/(2*h),(a/(b+h)-a/(b-h))/(2*h)])
        np.testing.assert_allclose(grad,[1/b,-a/b**2],rtol=1e-8)

    def test_clipping_direction(self):
        mu=np.array([.9,.1]); pi=np.array([0.,1.]); q=np.array([.2,.8]); w=pi/mu
        self.assertLess(np.sum(mu*np.minimum(w,2)*q),np.sum(pi*q))

    def test_shrinkage_zero_defined(self):
        def shrink(w,lam): return np.zeros_like(w) if lam==0 else lam*w/(w*w+lam)
        w=np.array([0.,1.,10.]); np.testing.assert_equal(shrink(w,0),0)
        np.testing.assert_allclose(shrink(w,1e14),w,atol=1e-10)

    def test_mixture_valid_but_not_safe(self):
        base=np.array([[1.,0.]]); target=np.array([[0.,1.]]); q=np.array([[1.,0.]])
        mix=.2*target+.8*base; policy_array(mix)
        self.assertLess(float((mix*q).sum()),float((base*q).sum()))

    def test_missing_support_indistinguishable_worlds(self):
        # Logger always A0 with reward .2. A1 can have mean 0 or 1 without altering logs.
        mu=np.array([1.,0.]); worlds=[np.array([.2,0]),np.array([.2,1])]
        self.assertEqual(mu@worlds[0],mu@worlds[1]); self.assertNotEqual(worlds[0][1],worlds[1][1])

    def test_original_generator_quadrature(self):
        x=(np.arange(200000)+.5)/200000; e=1/(1+np.exp(-(4*x-2)))
        val=float(np.sum(e*(1+1.5*x))/e.sum())
        self.assertAlmostEqual(val,1.9609005525,places=9)
        self.assertTrue(np.all(1-.5*x>0))


def simulations(repetitions=1000,n=2000):
    rows=[]; raw=[]
    for scenario,e,q in [
        ('regular',np.array([.1,.9]),np.array([[.2,.1],[.8,.7]])),
        ('weak_overlap',np.array([.0005,.0005]),np.array([[.2,.5],[.8,.5]])),
        ('weak_overlap_off_prior',np.array([.0005,.0005]),np.array([[.2,.7],[.8,.7]])),
        ('rare_reward',np.array([.1,.9]),np.array([[.002,.001],[.008,.007]]))]:
        truth=float(q[:,1].mean()); baseline=float(np.mean((1-e)*q[:,0]+e*q[:,1]))
        base_seed={'regular':123000,'weak_overlap':223000,'rare_reward':323000,'weak_overlap_off_prior':423000}[scenario]
        collected={name:[] for name in ['IPS','SNIPS','DR_crossfit','DR_oracle','paired_DR_difference']}
        undefined=0
        for rep in range(repetitions):
            rng=np.random.default_rng(base_seed+rep); x=rng.integers(0,2,n); a=(rng.random(n)<e[x]).astype(int)
            r=(rng.random(n)<q[x,a]).astype(float); p=np.where(a==1,e[x],1-e[x]); pi=np.tile([0.,1.],(n,1))
            folds=rng.permutation(n)%5; qhat=crossfit_tabular(x,a,r,folds)
            w,dm,ip,dr=scores(a,r,p,pi,qhat); oracle=scores(a,r,p,pi,q[x])[3]
            for name,z in [('IPS',ip),('DR_crossfit',dr),('DR_oracle',oracle),('paired_DR_difference',dr-r)]:
                est,se,lo,hi=wald(z); target=truth-baseline if name=='paired_DR_difference' else truth
                collected[name].append((est,target,se,lo<=target<=hi,hi-lo,lo>0 if name=='paired_DR_difference' else False))
                raw.append([scenario,rep,name,est,target,se,lo,hi])
            if w.sum()>0:
                v=snips(w,r); influence=w*(r-v)/w.mean(); se=float(influence.std(ddof=1)/np.sqrt(n))
                collected['SNIPS'].append((v,truth,se,v-1.96*se<=truth<=v+1.96*se,3.92*se,False))
                raw.append([scenario,rep,'SNIPS',v,truth,se,v-1.96*se,v+1.96*se])
            else: undefined+=1
        for name,records in collected.items():
            v=np.asarray(records,float); errors=v[:,0]-v[:,1]; coverage=float(v[:,3].mean())
            rows.append(dict(scenario=scenario,method=name,n=n,repetitions=repetitions,defined=len(records),undefined=undefined if name=='SNIPS' else 0,
                bias=float(errors.mean()),bias_mcse=float(errors.std(ddof=1)/np.sqrt(len(errors))),rmse=float(np.sqrt(np.mean(errors**2))),
                coverage_among_defined=coverage,coverage_all_attempts=float(v[:,3].sum()/repetitions),coverage_mcse=float(np.sqrt(coverage*(1-coverage)/len(v))),
                mean_width=float(v[:,4].mean()),positive_decision_rate=float(v[:,5].mean()) if name=='paired_DR_difference' else None,
                false_improvement_rate=float(v[:,5].mean()) if name=='paired_DR_difference' and truth-baseline<=0 else None))
    with (OUT/'monte_carlo_raw.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f); writer.writerow(['scenario','rep','method','estimate','truth','se','lower','upper']); writer.writerows(raw)
    return rows


def nuisance_experiments(repetitions=1000,n=2000):
    # Fixed true/wrong nuisance functions isolate DR algebra. Not fitted-model inference.
    e=np.array([.1,.9]); q=np.array([[.2,.1],[.8,.7]]); bad_q=np.array([[.3,.3],[.4,.4]])
    result={name:[] for name in ['both_correct','only_propensity_correct','only_outcome_correct','both_wrong']}
    hidden=[]
    for rep in range(repetitions):
        rng=np.random.default_rng(523000+rep); x=rng.integers(0,2,n); a=(rng.random(n)<e[x]).astype(int)
        r=(rng.random(n)<q[x,a]).astype(float); pi=np.tile([0.,1.],(n,1))
        p=np.where(a==1,e[x],1-e[x])
        for name,pp,qq in [('both_correct',p,q[x]),('only_propensity_correct',p,bad_q[x]),('only_outcome_correct',np.full(n,.5),q[x]),('both_wrong',np.full(n,.5),bad_q[x])]:
            result[name].append(float(scores(a,r,pp,pi,qq)[3].mean()))
        # All measured X constant; U binary and hidden. mu(1|U)=q1(U)=(.1,.9).
        u=rng.integers(0,2,n); a=(rng.random(n)<e[u]).astype(int); r=(rng.random(n)<e[u]).astype(float)
        truep=np.where(a==1,e[u],1-e[u])
        hidden.append([float(np.mean(a*r/.5)),float(np.mean(a*r/truep))])
    summary={name:{'mean':float(np.mean(v)),'mcse':float(np.std(v,ddof=1)/np.sqrt(repetitions)),
        'population_limit':.6 if name=='both_wrong' else .4,'true_value':.4} for name,v in result.items()}
    summary['hidden_confounding']={'nominal_ips_mean':float(np.mean(np.asarray(hidden)[:,0])),
        'full_propensity_ips_mean':float(np.mean(np.asarray(hidden)[:,1])),
        'nominal_limit':.82,'truth':.5,'gamma_required':9}
    return summary


def run():
    OUT.mkdir(exist_ok=True)
    stream=io.StringIO(); start=time.perf_counter()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MathematicalChecks))
    (OUT/'test_log.txt').write_text(stream.getvalue(),encoding='utf-8')
    print(stream.getvalue())
    if not result.wasSuccessful(): raise SystemExit(1)
    mc=simulations(); nuisance=nuisance_experiments()
    record={'python':platform.python_version(),'numpy':np.__version__,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
        'simulation_repetitions_per_scenario':1000,'simulation_n':2000,'crossfit_folds':5,
        'seed_ranges':[[123000,123999],[223000,223999],[323000,323999],[423000,423999],[523000,523999]],
        'elapsed_seconds':time.perf_counter()-start,'monte_carlo':mc,'nuisance_experiments':nuisance,
        'source_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'not_executed':['SymPy CAS (unavailable)','OBD experiment (not downloaded)','policy-revision learning comparison (no specified method)','adaptive/cluster inference','formal coverage for sensitivity endpoints']}
    (OUT/'verification_results.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
    print(json.dumps(record,indent=2))


if __name__=='__main__': run()
