import csv,json,hashlib,time
import numpy as np
import methods as m
from real_experiment import load,counts,OUT,ROOT

def main():
    start=time.time();rows=[]
    manifest=dict(protocol_sha256=hashlib.sha256((ROOT/'STABILITY_PROTOCOL.md').read_bytes()).hexdigest(),
        method_sha256=hashlib.sha256((ROOT/'methods.py').read_bytes()).hexdigest(),seeds=[791000,791099])
    (OUT/'stability_manifest.json').write_text(json.dumps(manifest,indent=2))
    for campaign in ('all','men','women'):
        d=load('random_'+campaign);a,y=d['action'],d['reward'];A=int(a.max()+1)
        unique,inv=np.unique(d['timestamp'],return_inverse=True)
        for rep in range(100):
            u=np.random.default_rng(791000+rep).random(len(unique));label=np.where(u<.2,0,np.where(u<.6,1,2))[inv]
            n0,k0=counts(a[label==0],y[label==0],A);n,k=counts(a[label==1],y[label==1],A)
            fit=m.evaluate(n0,k0,n,k)
            choices={name:int(np.argmax(b[:,0])) for name,b in fit['bounds'].items()}
            rn,rk=counts(a[label==2],y[label==2],A);gn,gk=m.aggregate(rn,rk,fit['inside']);reference=np.sum(fit['group_c']*gk/gn,axis=1)
            for name,b in fit['bounds'].items():
                i=choices[name];deploy=b[i,0]>1e-10
                rows.append(dict(campaign=campaign,rep=rep,method=name,certified=int(deploy),certified_candidates=int((b[:,0]>1e-10).sum()),
                    selected_k=int(fit['ks'][i]) if deploy else 0,selected_lower=float(b[i,0]) if deploy else 0,
                    selected_reference=float(reference[i]) if deploy else 0,
                    median_width=float(np.median(b[:,1]-b[:,0])),
                    median_width_reduction_vs_original=float(np.median(1-(b[:,1]-b[:,0])/np.diff(fit['bounds']['item_split'],axis=1).ravel()))))
        print(campaign,'100 repeated splits complete',flush=True)
    with (OUT/'stability.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print('seconds',time.time()-start,flush=True)
if __name__=='__main__':main()
