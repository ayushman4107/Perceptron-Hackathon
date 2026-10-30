import math,unittest
from itertools import product
import numpy as np
from likelihood import *


class Checks(unittest.TestCase):
    def test_kl(self):
        np.testing.assert_allclose(kl([0,.3,1],[0,.3,1]),0)
        self.assertTrue(np.isinf(kl(.2,0)))
        self.assertAlmostEqual(float(kl(0,.3)),-math.log(.7))
    def test_domains(self):
        for n,k in [([1],[2]),([.5],[0]),([0],[float('nan')])]:
            with self.assertRaises(ValueError):stats(n,k)
        with self.assertRaises(ValueError):kl(-.1,.2)
        with self.assertRaises(ValueError):upper([1],[1],[0],-1)
    def test_empty_cell(self):
        np.testing.assert_allclose(bounds([[.3,-.2]],[0,0],[0,0],3),[[-.2,.3]])
    def test_identical_policy(self):
        np.testing.assert_array_equal(bounds([[0,0]],[50,30],[0,10],3),[[0,0]])
    def test_single_binomial_zero(self):
        result=bounds([[1]],[100],[0],3)[0]
        np.testing.assert_allclose(result,[0,1-math.exp(-3/100)],atol=1e-9)
    def test_grid_and_dual(self):
        n=np.array([20,30]);k=np.array([4,12]);c=np.array([[.6,-.4]])
        u,primal,q,div=upper(c,n,k,4,True)
        self.assertLess(abs(u[0]-primal[0]),1e-8)
        self.assertLessEqual(div[0],4+1e-10)
        grid=np.linspace(.001,.999,500)
        a,b=np.meshgrid(grid,grid,indexing='ij')
        feasible=20*kl(.2,a)+30*kl(.4,b)<=4
        ref=np.max((.6*a-.4*b)[feasible])
        self.assertGreaterEqual(u[0]+1e-10,ref)
        self.assertLess(u[0]-ref,.003)
    def test_tilted_optimality(self):
        for p,t in product([0,.1,.5,1],[0,.01,1,2,100]):
            q=float(tilted(np.array(p),np.array(t)))
            grid=np.linspace(0,1,10001)
            self.assertGreaterEqual(t*q-float(kl(p,q))+1e-10,float(np.max(t*grid-kl(p,grid))))
    def test_lr_expectation(self):
        truth=[.2,.7];pilot=[.4,.6];total=0
        for k in product(range(4),repeat=2):
            prob=math.prod(math.comb(3,ki)*q**ki*(1-q)**(3-ki) for ki,q in zip(k,truth))
            ratio=math.prod((p/q)**ki*((1-p)/(1-q))**(3-ki) for ki,q,p in zip(k,truth,pilot))
            total+=prob*ratio
        self.assertAlmostEqual(total,1)
    def test_mixture_empty(self):
        _,_,radius=mixture_region([0,0],[0,0])
        self.assertAlmostEqual(radius,math.log(20))
    def test_mixture_evalue_expectation(self):
        q=.3;n=5;expectation=0
        for k in range(n+1):
            logmix=math.lgamma(k+.5)+math.lgamma(n-k+.5)-math.lgamma(n+1)-2*math.lgamma(.5)
            expectation+=math.comb(n,k)*math.exp(logmix)
        self.assertAlmostEqual(expectation,1)
    def test_simultaneous_containment(self):
        rng=np.random.default_rng(8);n=np.array([40,100,0,60]);k=np.array([10,70,0,5]);p=np.divide(k,n,out=np.full(4,.5),where=n>0)
        truth=np.array([.3,.65,.8,.12]);radius=float(np.sum(n*kl(p,truth)))+1
        coefficients=rng.normal(size=(32,4))
        b=bounds(coefficients,n,k,radius);actual=coefficients@truth
        self.assertTrue(np.all(b[:,0]<=actual));self.assertTrue(np.all(actual<=b[:,1]))
    def test_box_inversion(self):
        lo,hi=kl_box([0,100,100],[0,20,0])
        self.assertEqual(lo[0],0);self.assertEqual(hi[0],1)
        self.assertAlmostEqual(100*float(kl(.2,lo[1])),math.log(120),places=8)
        self.assertGreater(hi[2],0)
    def test_radius_monotonicity(self):
        first=bounds([[.5,-.5]],[10,100],[2,40],3)
        second=bounds([[.5,-.5]],[10,100],[2,40],6)
        self.assertLessEqual(second[0,0],first[0,0]);self.assertGreaterEqual(second[0,1],first[0,1])


if __name__=='__main__':unittest.main(verbosity=2)
