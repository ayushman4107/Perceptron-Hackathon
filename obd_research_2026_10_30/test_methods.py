import itertools,math,unittest
import methods as m
import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln

class Checks(unittest.TestCase):
    def test_heterogeneous_exact_compression(self):
        rng=np.random.default_rng(16)
        for _ in range(100):
            mu=rng.dirichlet(np.ones(12));groups=np.repeat(np.arange(3),4)
            factor=rng.uniform(.2,3,3);pi=mu*factor[groups];pi/=pi.sum()
            mass,c=m.compress(mu,pi,groups);q=rng.random(12)
            grouped=np.array([np.dot(mu[groups==g],q[groups==g])/mass[g] for g in range(3)])
            self.assertAlmostEqual(np.dot(pi-mu,q),np.dot(c,grouped),places=13)
    def test_invalid_grouping_rejected(self):
        with self.assertRaises(ValueError):m.compress([.5,.5],[.8,.2],[0,0])
    def test_support_rejected(self):
        with self.assertRaises(ValueError):m.compress([1,0],[.5,.5],[0,1])
    def test_topk_identity_and_probability(self):
        rng=np.random.default_rng(91);n=np.arange(80)+10;k=rng.binomial(n,.05)
        ks,inside,pi,c=m.policies(n,k);np.testing.assert_allclose(pi.sum(1),1)
        q=rng.random(80)
        for i,kk in enumerate(ks):
            self.assertAlmostEqual(c[i]@q,(1-kk/80)*(q[inside[i]].mean()-q[~inside[i]].mean()))
    def test_predictive_distribution_normalized_and_evalue(self):
        n=np.array([3,4]);n0=np.array([5,7]);k0=np.array([1,3]);truth=np.array([.03,.7]);total=0
        for kk in itertools.product(range(4),range(5)):
            k=np.array(kk);logtruth=np.sum(m.xlogy(k,truth)+m.xlog1py(n-k,-truth))
            logmle=np.sum(m.xlogy(k,k/n)+m.xlog1py(n-k,-k/n))
            logr=m.radius(n,k,n0,k0,kind='predictive')-math.log(20)
            lognum=logmle-logr
            choose=np.exp(np.sum(gammaln(n+1)-gammaln(k+1)-gammaln(n-k+1)))
            total+=choose*np.exp(logtruth)*np.exp(lognum-logtruth)
        self.assertAlmostEqual(total,1,places=12)
    def test_pilot_selected_groups_still_normalized(self):
        # Select a top arm using pilot outcomes, then enumerate ALL validation outcomes.
        for pilot in itertools.product(range(3),repeat=3):
            chosen=int(np.argmax(pilot));n0=np.array([2,4]);k0=np.array([pilot[chosen],sum(pilot)-pilot[chosen]])
            n=np.array([2,3]);total=0
            for kk in itertools.product(range(3),range(4)):
                k=np.array(kk);p=k/n
                lognum=np.sum(m.xlogy(k,p)+m.xlog1py(n-k,-p))-(m.radius(n,k,n0,k0)-math.log(20))
                total+=math.comb(2,int(k[0]))*math.comb(3,int(k[1]))*math.exp(lognum)
            self.assertAlmostEqual(total,1,places=12)
    def test_empty_groups_full_uncertainty(self):
        b=m.lr_bounds([.6,-.6],[0,0],[0,0],3)
        np.testing.assert_allclose(b,[[-.6,.6]])
        lo,hi=m.box([0,0],[0,0],kind='exact');np.testing.assert_equal(lo,[0,0]);np.testing.assert_equal(hi,[1,1])
    def test_zero_contrast(self):np.testing.assert_equal(m.lr_bounds([0,0],[5,8],[0,8],3),[[0,0]])
    def test_zero_clicks_not_zero_uncertainty(self):
        b=m.lr_bounds([1,-1],[100,100],[0,0],3);self.assertGreater(b[0,1]-b[0,0],.01)
    def test_one_cell_exact_endpoint(self):
        b=m.lr_bounds([1],[100],[0],3);self.assertAlmostEqual(b[0,1],1-math.exp(-.03),places=8)
    def test_scipy_independent_solver(self):
        rng=np.random.default_rng(142)
        for _ in range(12):
            n=np.array([100,150,200]);k=rng.integers(10,60,3);p=k/n;c=rng.uniform(-1,1,3);r=2.3
            upper,q,div,primal=m.upper(c,n,k,r,True)
            fit=minimize(lambda x:-c@x,p,method='SLSQP',bounds=[(1e-9,1-1e-9)]*3,
                constraints=[dict(type='ineq',fun=lambda x:r-np.sum(n*m.kl(p,x)))],options=dict(ftol=1e-11,maxiter=1000))
            self.assertTrue(fit.success,fit.message);self.assertLess(abs(upper[0]+fit.fun),2e-7)
            self.assertLessEqual(div[0],r+1e-8);self.assertLess(upper[0]-primal[0],1e-7)
    def test_radius_monotonic(self):
        a=m.lr_bounds([.7,-.7],[100,100],[1,3],3);b=m.lr_bounds([.7,-.7],[100,100],[1,3],6)
        self.assertLessEqual(b[0,0],a[0,0]);self.assertGreaterEqual(b[0,1],a[0,1])
    def test_mixture_floor(self):
        n=np.array([100,100]);k=np.array([1,2]);n0=np.array([50,50]);k0=np.array([45,45])
        self.assertLessEqual(m.radius(n,k,n0,k0),m.radius(n,k,kind='jeffreys')+math.log(2)+1e-10)
    def test_scores_match_expanded_rows(self):
        n=np.array([10,15,20]);k=np.array([1,2,3]);c=np.array([[.2,-.3,.1]]);q=np.array([.1,.2,.3])
        a=np.repeat(np.arange(3),n);y=np.concatenate([np.r_[np.ones(ki),np.zeros(ni-ki)] for ni,ki in zip(n,k)])
        z=(c@q)[0]+3*c[0,a]*(y-q[a]);s,ss,N=m.score_stats(n,k,c,q=q)
        self.assertAlmostEqual(s[0],z.sum());self.assertAlmostEqual(ss[0],(z*z).sum());self.assertEqual(N,len(z))
    def test_invalid_counts(self):
        for n,k in [([1],[-1]),([1],[2]),([1.5],[1]),([1],[np.nan])]:
            with self.assertRaises(ValueError):m.radius(n,k,kind='jeffreys')
    def test_reproducible_evaluate_and_folds(self):
        n0=np.full(25,100);k0=np.arange(25)%4;n=np.full(25,200);k=np.arange(25)%7
        a=m.evaluate(n0,k0,n,k,folds=(n//2,k//2,n-n//2,k-k//2));b=m.evaluate(n0,k0,n,k)
        for name in b['bounds']:np.testing.assert_equal(a['bounds'][name],b['bounds'][name])

if __name__=='__main__':unittest.main(verbosity=2)
