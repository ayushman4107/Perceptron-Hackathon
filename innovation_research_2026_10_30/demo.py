"""Deterministic first-seed demonstration; no hand-picked favorable seed."""
from pathlib import Path
import json
import numpy as np
from src.core import aggregate,confidence_box,contrast_bounds,robust_reference,separate_bounds,dr_intervals
from src.simulation import setting,draw,oracle_differences


def demo():
    c=setting('shared_blind',2);seed=1010000
    x,a,r=draw(c,3000,seed);count,total=aggregate(x,a,r,2,3);lo,hi=confidence_box(count,total)
    args=(c['candidates'][1],c['base'],c['p_input'],lo,hi)
    report={'seed':seed,'selection_rule':'first seed in frozen primary experiment; no seed search',
        'warning':'Reference is another candidate, NOT the historical logger; cancellation does not solve target-versus-logger missing support.',
        'counts':count.tolist(),'separate_value_contrast':separate_bounds(*args),
        'joint_contrast':contrast_bounds(*args),'established_robust_reference':robust_reference(*args),
        'paired_DR_Wald':dr_intervals(x,a,r,c['mu'],c['candidates'],c['base'])[1].tolist(),
        'oracle_true_contrast_revealed_after_estimation':float(oracle_differences(c)[1])}
    # Separate population-level before/after example, not a measured trial result.
    q=np.array([[.2,.1],[.8,.7]]);old=np.array([.8,.2]);new=np.array([.2,.8])
    report['separate_before_after_population_example']={'old_action0_mean':float(old@q[:,0]),
        'new_action1_mean':float(new@q[:,1]),'naive_time_difference':float(new@q[:,1]-old@q[:,0]),
        'same_new_population_policy_difference':float(new@(q[:,1]-q[:,0]))}
    return report


if __name__=='__main__':
    result=demo();print(json.dumps(result,indent=2))
    out=Path(__file__).resolve().parent/'results';out.mkdir(exist_ok=True)
    (out/'demo.json').write_text(json.dumps(result,indent=2))
