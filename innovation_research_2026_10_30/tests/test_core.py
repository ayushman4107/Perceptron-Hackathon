import sys,unittest
from pathlib import Path
from itertools import product
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.core import *
from src.simulation import setting,draw,oracle_differences


class Checks(unittest.TestCase):
    def setUp(self):
        self.c=setting('shared_blind',2)
        self.base=self.c['base']; self.pi=self.c['candidates'][1]; self.p=self.c['p_input']
    def test_known_answer(self):
        lo=self.c['q'].copy(); hi=lo.copy(); lo[:,2]=0;hi[:,2]=1
        np.testing.assert_allclose(contrast_bounds(self.pi,self.base,self.p,lo,hi),[.24,.24])
        np.testing.assert_allclose(separate_bounds(self.pi,self.base,self.p,lo,hi),[-.16,.64])
    def test_vertex_reference(self):
        rng=np.random.default_rng(7)
        for _ in range(40):
            pi=rng.dirichlet([1,1,1],2); base=rng.dirichlet([1,1,1],2)
            lo=rng.random((2,3)); hi=lo+(1-lo)*rng.random((2,3))
            c=self.p[:,None]*(pi-base)
            vertices=[np.sum(c*np.where(np.asarray(bits).reshape(2,3),hi,lo)) for bits in product([0,1],repeat=6)]
            got=contrast_bounds(pi,base,self.p,lo,hi)
            np.testing.assert_allclose(got,[min(vertices),max(vertices)],atol=1e-12)
            np.testing.assert_allclose(got,robust_reference(pi,base,self.p,lo,hi),atol=1e-12)
    def test_cancellation_identity(self):
        rng=np.random.default_rng(8)
        for _ in range(50):
            pi=rng.dirichlet([1,1,1],2); base=rng.dirichlet([1,1,1],2)
            lo=rng.random((2,3));hi=lo+(1-lo)*rng.random((2,3))
            gain=contrast_bounds(pi,base,self.p,lo,hi)[0]-separate_bounds(pi,base,self.p,lo,hi)[0]
            self.assertAlmostEqual(gain,np.sum(self.p[:,None]*np.minimum(pi,base)*(hi-lo)))
    def test_unchanged(self):
        self.assertEqual(contrast_bounds(self.base,self.base,self.p,np.zeros((2,3)),np.ones((2,3))),(0.,0.))
    def test_empty(self):
        count,total=aggregate(np.array([],int),np.array([],int),np.array([]),2,3)
        lo,hi=confidence_box(count,total)
        np.testing.assert_array_equal(lo,0);np.testing.assert_array_equal(hi,1)
    def test_zero_reward_not_zero_uncertainty(self):
        lo,hi=confidence_box(np.ones((2,3))*10,np.zeros((2,3)))
        self.assertTrue((hi>0).all())
    def test_invalid(self):
        for p in [[[.3,.3]],[[float('nan'),1]],[[-.1,1.1]]]:
            with self.assertRaises(ValueError): policy(p)
        with self.assertRaises(ValueError): confidence_box([[0]],[[-1]])
        with self.assertRaises(ValueError): confidence_box([[1]],[[2]])
        with self.assertRaises(ValueError): confidence_box([[1]],[[0]],0)
        with self.assertRaises(ValueError): masses([.2,.2],2)
        with self.assertRaises(ValueError): aggregate(np.array([0]),np.array([3]),np.array([1.]),2,3)
        with self.assertRaises(ValueError): contrast_bounds(self.pi,self.base,self.p,np.ones((2,3)),np.zeros((2,3)))
    def test_width(self):
        lo=np.zeros((2,3));hi=np.ones((2,3))
        l,u=contrast_bounds(self.pi,self.base,self.p,lo,hi)
        self.assertAlmostEqual(u-l,np.sum(self.p[:,None]*abs(self.pi-self.base)))
    def test_truth_containment_and_selection(self):
        rng=np.random.default_rng(11)
        for _ in range(50):
            q=rng.random((2,3));lo=q*rng.random((2,3));hi=q+(1-q)*rng.random((2,3))
            cfg=setting('full_overlap',32)
            bounds=np.array([contrast_bounds(pi,cfg['base'],self.p,lo,hi) for pi in cfg['candidates']])
            truth=np.sum(self.p[None,:,None]*(cfg['candidates']-cfg['base'])*q,axis=(1,2))
            self.assertTrue(np.all(truth>=bounds[:,0]-1e-12));self.assertTrue(np.all(truth<=bounds[:,1]+1e-12))
            self.assertGreaterEqual(truth[select(bounds[:,0])],-1e-12)
    def test_support_distinction(self):
        c=setting('logger_reference',2);x,a,r=draw(c,300,1)
        got=dr_intervals(x,a,r,c['mu'],c['candidates'],c['base'])
        self.assertTrue(np.isnan(got[1]).all())
        x,a,r=draw(self.c,300,1)
        self.assertTrue(np.isfinite(dr_intervals(x,a,r,self.c['mu'],self.c['candidates'],self.base)).all())
    def test_logger_missing_mass(self):
        c=setting('logger_reference',2);d=c['candidates'][1]-c['base']
        self.assertAlmostEqual(np.sum(self.p[:,None]*abs(d)*(c['mu']==0)),.4)
    def test_reproducibility(self):
        for first,second in zip(draw(self.c,100,4),draw(self.c,100,4)):np.testing.assert_array_equal(first,second)
    def test_hidden_world(self):
        self.assertAlmostEqual((.5*.1*.1+.5*.9*.9)/.5,.82)
        self.assertAlmostEqual(oracle_differences(setting('hidden_confounding',2))[1],-.1)
    def test_shift_reversal(self):
        c=setting('unmodeled_shift',2)
        self.assertLess(oracle_differences(c)[1],0)
        self.assertGreater(np.sum(c['p_input'][:,None]*(c['candidates'][1]-c['base'])*c['q']),0)
    def test_no_false_precision_from_one_row(self):
        lo,hi=confidence_box(np.ones((2,3)),np.ones((2,3)))
        self.assertTrue((hi-lo>.9).all())
    def test_identical_value_worlds_different_policy_gap(self):
        c=setting('logger_reference',2);qlo=c['q'].copy();qhi=qlo.copy();qlo[:,2]=0;qhi[:,2]=1
        np.testing.assert_array_equal(qlo[c['mu']>0],qhi[c['mu']>0])
        d=c['p_input'][:,None]*(c['candidates'][1]-c['base'])
        self.assertLess(np.sum(d*qlo),0);self.assertGreater(np.sum(d*qhi),0)
    def test_missing_predicted_not_known(self):
        self.assertEqual(select([0,np.nan,-.1]),0)
        self.assertEqual(select([0,np.nan,.1]),2)


if __name__=='__main__':unittest.main(verbosity=2)
