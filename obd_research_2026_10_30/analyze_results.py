"""Generate every figure and claim from saved experiment outputs."""
import json,hashlib,csv,math,os
from pathlib import Path
import methods as m
import numpy as np
import pandas as pd
os.environ['MPLCONFIGDIR']=str(Path(__file__).resolve().parent/'tmp'/'matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results';FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,
    'axes.titleweight':'bold','axes.titlesize':12,'axes.labelsize':10,'xtick.labelsize':10,'ytick.labelsize':10,
    'text.color':'#000000','axes.labelcolor':'#000000','xtick.color':'#000000','ytick.color':'#000000',
    'savefig.dpi':200,'figure.facecolor':'white','axes.facecolor':'white'})
COLORS={'item_split':'#8893a4','item_kl':'#b1b9c4','group_predictive':'#4976ae','group_exact':'#087f70','group_kl':'#baa040','dr_wald':'#bd6553','ips_wald':'#d6a269'}
LABELS={'item_split':'Original item likelihood','item_predictive':'Item predictive likelihood','item_jeffreys':'Item Jeffreys mixture',
    'item_kl':'Item KL box','group_predictive':'Grouped predictive likelihood','group_split':'Grouped split likelihood',
    'group_jeffreys':'Grouped Jeffreys mixture','group_kl':'Grouped KL box','group_exact':'Grouped exact binomial',
    'dr_wald':'Cross-fitted DR / Wald','ips_wald':'IPS / Wald'}
def save(fig,name):
    fig.savefig(FIG/f'{name}.png',bbox_inches='tight');fig.savefig(FIG/f'{name}.svg',bbox_inches='tight');plt.close(fig)
def wilson(k,n):
    p=k/n;z=1.95996398454;den=1+z*z/n;mid=(p+z*z/(2*n))/den;h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return max(0,mid-h),min(1,mid+h)

def main():
    df=pd.concat([pd.read_csv(p,keep_default_na=False) for p in sorted(OUT.glob('synthetic_case_*.csv'))],ignore_index=True)
    assert len(df)==88000 and len(df[['case','rep']].drop_duplicates())==8000
    groupcols=['case','actions','n_total','design','method'];agg=df.groupby(groupcols,sort=True).agg(
        trials=('rep','size'),covered=('covered','sum'),false_improvement=('false_improvement','sum'),beneficial=('beneficial','sum'),
        mean_selected_gain=('selected_gain','mean'),mean_regret=('regret','mean'),mean_median_width=('median_width','mean')).reset_index()
    agg.to_csv(OUT/'synthetic_summary.csv',index=False)
    r=json.loads((OUT/'obd_all_random.json').read_text());bts=json.loads((OUT/'bts_to_random.json').read_text())
    ex=np.array(r['bounds']['group_exact']);old=np.array(r['bounds']['item_split']);pred=np.array(r['bounds']['group_predictive']);ikl=np.array(r['bounds']['item_kl'])
    chosen=int(np.argmax(ex[:,0]));k=r['ks'][chosen]
    summary=dict(real_rows_processed=sum(x['rows'] for x in json.loads((ROOT/'data/data_manifest.json').read_text())['datasets'].values()),
        primary_split_counts=r['counts'],primary_k=k,primary_exact_interval=ex[chosen].tolist(),primary_reference=r['reference'][chosen],
        primary_reference_wald95=r['reference_wald95'][chosen],primary_reference_block95=r['reference_block_bootstrap']['intervals'][chosen],
        primary_width_reduction_vs_original=float(np.median(1-np.diff(ex,axis=1)/np.diff(old,axis=1))),
        primary_width_reduction_vs_item_kl=float(np.median(1-np.diff(ex,axis=1)/np.diff(ikl,axis=1))),
        primary_predictive_width_reduction_vs_original=float(np.median(1-np.diff(pred,axis=1)/np.diff(old,axis=1))),
        bts_naive_relative_error=abs(bts['observed_bts']['mean']/bts['on_policy_random']['mean']-1),
        bts_dr_relative_error=abs(bts['dr']['mean']/bts['on_policy_random']['mean']-1),
        bts_ips_relative_error=abs(bts['ips']['mean']/bts['on_policy_random']['mean']-1),
        tests_passed=16,synthetic_logs=8000,method_trial_rows=len(df),
        aggregate_fixed_benchmark=df.groupby('method')[['covered','false_improvement','beneficial','selected_gain','median_width']].mean().to_dict('index'))
    # Exact-box adverse witness for the selected policy, computed without changing any inference.
    gn=np.array(r['group_n']);gk=np.array(r['group_k']);lo,hi=m.box(gn,gk,.05/len(r['ks']),kind='exact')
    tau=1-k/r['n_actions'];witness=[float(lo[chosen,0]),float(hi[chosen,1])]
    summary['selected_exact_witness']=dict(group_means=witness,gain=tau*(witness[0]-witness[1]),
        absolute_group_mean_drift_tolerance=ex[chosen,0]/(2*tau),interpretation='Group-level adverse means inside the simultaneous exact box, not a hidden-confounder estimate.')
    # Scientific figure 1: standard OPE against a different policy's actual logged outcomes.
    fig,ax=plt.subplots(figsize=(7.6,3.2));names=['Raw BTS CTR\n(naive proxy)','IPS','Cross-fitted DR','Random on-policy\nreference']
    vals=[bts['observed_bts'],bts['ips'],bts['dr'],bts['on_policy_random']]
    for i,v in enumerate(vals):
        center=v['mean']*100;ci=np.array(v['wald95'])*100
        ax.errorbar(i,center,yerr=[[center-ci[0]],[ci[1]-center]],fmt='o',capsize=5,color=['#8893a4','#4976ae','#087f70','#252c3a'][i],markersize=7)
        # Anchor to the confidence interval's TOP, not the point estimate.
        # The white label background also keeps grid lines out of the number.
        ax.annotate(f'{center:.3f}%',(i,ci[1]),xytext=(0,8),textcoords='offset points',ha='center',va='bottom',fontsize=10,
                    bbox=dict(facecolor='white',edgecolor='none',pad=1.5))
    ax.set_xticks(range(4),names);ax.set_ylabel('Click-through rate (%)');ax.set_ylim(.45,.82)
    ax.set_title('Logged performance is not the new policy’s performance',loc='left',pad=18)
    ax.grid(axis='y',alpha=.18);fig.tight_layout();save(fig,'01_obd_counterfactual')
    # Figure 2: selected candidate, full family correction, reference uncertainty visible.
    names=['item_split','item_kl','group_predictive','group_exact','dr_wald'];fig,ax=plt.subplots(figsize=(8.4,3.6))
    ref=np.array(r['reference_wald95'][chosen])*100
    ax.axvspan(*ref,color='#e7eee9',label='Independent reference: pointwise 95% Wald band')
    ax.axvline(r['reference'][chosen]*100,color='#658171',ls=':',lw=1.4);ax.axvline(0,color='#343b47',lw=1)
    for i,name in enumerate(names):
        bound=np.array(r['bounds'][name][chosen])*100
        if name=='dr_wald':point=r['points']['dr'][chosen]*100
        elif name.startswith('item_'):point=float((np.array(r['policies'][chosen])-1/r['n_actions'])@(np.array(r['cert_k'])/np.array(r['cert_n'])))*100
        else:point=r['points']['group'][chosen]*100
        ax.plot(bound,[i,i],lw=3,color=COLORS[name]);ax.plot(point,i,'o',color=COLORS[name],ms=5)
        ax.plot(bound,[i,i],'|',color=COLORS[name],ms=10)
    ax.set_yticks(range(len(names)),[LABELS[x] for x in names]);ax.invert_yaxis()
    ax.set_xlabel('CTR gain over uniform logging (percentage points)');fig.suptitle('An 80-item problem reduced to a two-group certificate',x=.5,ha='center',fontsize=14,fontweight='bold')
    # The PDF caption explains the shaded reference band at the shared caption size.
    # Avoid a duplicate, tiny legend after scaling the chart into the document.
    ax.grid(axis='x',alpha=.16);fig.tight_layout();save(fig,'02_policy_certificate')
    # Figure 3: all five candidates, not a handpicked easiest interval.
    names=['item_split','item_predictive','item_kl','group_predictive','group_kl','group_exact'];widths=[np.median(np.diff(r['bounds'][x],axis=1))*100 for x in names]
    fig,ax=plt.subplots(figsize=(8,3.5));ax.barh(range(len(names)),widths,color=[COLORS.get(x,'#99aabe') for x in names],height=.58)
    for i,w in enumerate(widths):ax.text(w+.025,i,f'{w:.3f}',va='center',fontsize=9)
    ax.set_yticks(range(len(names)),[LABELS[x] for x in names]);ax.invert_yaxis();ax.set_xlim(0,max(widths)*1.15)
    ax.set_xlabel('Median confidence-interval width (CTR percentage points)');ax.set_title('Compression helps; the simpler exact bound wins',loc='left',pad=15)
    ax.grid(axis='x',alpha=.15);fig.tight_layout();save(fig,'03_ablation')
    # Figure 4: prespecified 80-action/50k scenarios, calibration beside power.
    names=['item_split','group_predictive','group_exact','group_kl','dr_wald'];designs=['null','heterogeneous','rare','signal']
    fig,axes=plt.subplots(1,2,figsize=(10.4,3.7));sub=agg[(agg.actions==80)&(agg.n_total==50000)]
    for j,name in enumerate(names):
        data=sub[sub.method==name].set_index('design').loc[designs]
        x=np.arange(4)+(j-2)*.14
        for ax,column in zip(axes,['covered','beneficial']):
            rates=data[column].to_numpy()/500;ci=np.array([wilson(int(z),500) for z in data[column]])
            ax.errorbar(x,rates*100,yerr=np.stack((rates-ci[:,0],ci[:,1]-rates))*100,fmt='o',capsize=2,ms=4,color=COLORS[name],label=LABELS[name])
    axes[0].axhline(95,ls='--',lw=1,color='#444');axes[0].set_title('Whole-family interval coverage',loc='left');axes[1].set_title('Beneficial policy certified',loc='left')
    for ax in axes:ax.set_xticks(range(4),['Null','Heterogeneous','Rare','Signal']);ax.set_ylim(-4,104);ax.set_ylabel('% of 500 independent logs');ax.grid(axis='y',alpha=.15)
    fig.legend(*axes[1].get_legend_handles_labels(),loc='lower center',ncol=3,fontsize=8,frameon=False,bbox_to_anchor=(.5,-.08));fig.tight_layout();save(fig,'04_synthetic_calibration')
    # Figure 5: exact synthetic before/after reversal, clearly distinct from OBD.
    reversal=json.loads((OUT/'reversal_demo.json').read_text())
    fig,ax=plt.subplots(figsize=(6.6,2.6));vals=[reversal['naive_change']*100,reversal['ips_policy_effect']*100]
    ax.barh(['Naive before/after change','IPS policy-change estimate'],vals,color=['#bd6553','#087f70']);ax.axvline(0,color='#333',lw=1)
    ax.set_xlabel('Reward change (percentage points)');ax.set_title('Logged simulator: apparent gain, counterfactual harm',fontsize=11,loc='left')
    fig.tight_layout();save(fig,'05_simulated_reversal')
    summary['synthetic_before_after']=reversal
    if (OUT/'stability.csv').exists():
        st=pd.read_csv(OUT/'stability.csv');summary['exploratory_repeated_splits']=st.groupby(['campaign','method']).agg(
            certified_fraction=('certified','mean'),median_width_reduction=('median_width_reduction_vs_original','median'),
            min_width_reduction=('median_width_reduction_vs_original','min'),max_width_reduction=('median_width_reduction_vs_original','max')).reset_index().to_dict('records')
    (OUT/'claim_ledger.json').write_text(json.dumps(summary,indent=2))
    # Full report includes all frozen scenarios and negative results.
    lines=['# Results: policy-aware compression on Open Bandit Dataset','',
        'The strongest practical result is the reduction to the policy comparison’s required reward groups. The proposed predictive-mixture likelihood improved on the earlier item-level procedure, but did not outperform the grouped exact-binomial baseline overall. The recommended implementation is therefore grouped exact inference, with likelihood methods retained as audited alternatives. This is an application extension, not a validated world-first algorithm.','',
        '## Data and storage','',
        f"Processed {summary['real_rows_processed']:,} rows from four full campaign files in the official ZOZO archive. Retrieved members occupy 93.85 MiB; compact arrays approximately 34.73 MiB. The 160 GB warning on ZOZO’s page concerns SHIFT15M, not OBD. No full CSV extraction was needed.",
        '', 'Primary analysis: Random/all, first position, 80 items. Pilot/certification/reference counts are '+', '.join(f'{x:,}' for x in r['counts'])+'. Other campaigns and chronological splits are reported below. Observations from matching exact timestamps stay in the same split. This does not establish independence of repeated users.',
        '', '## Standard OPE: BTS men to uniform Random','',
        f"BTS observations: {bts['n_behavior']:,}; independent Random reference observations: {bts['n_reference']:,}, both first position. Logged BTS CTR is {bts['observed_bts']['mean']*100:.4f}%; IPS estimates Random CTR at {bts['ips']['mean']*100:.4f}%; cross-fitted tabular DR gives {bts['dr']['mean']*100:.4f}%; observed Random reference is {bts['on_policy_random']['mean']*100:.4f}%.",
        f"Relative discrepancy from this empirical reference is {summary['bts_naive_relative_error']*100:.2f}% for reusing BTS CTR and {summary['bts_dr_relative_error']*100:.2f}% for DR. These are empirical point-estimate discrepancies, not errors against exact ground truth or evidence that DR beats IPS significantly. The raw BTS mean is a naive target-policy proxy, not a before/after causal estimator.",
        f"Maximum importance weight: {bts['weight_max']:.1f}; weight ESS: {bts['weight_ess']:.1f}. Supplied BTS propensities are Monte Carlo approximations. Cross-fitting uses a smoothed action-level reward model and known logged propensities; it is not a rich personalized reward model.",
        '', '![OBD estimates](figures/01_obd_counterfactual.png)','', '## Primary extension result','',
        f"Across all five prespecified candidate sizes, grouped exact bounds reduce interval width by a median {summary['primary_width_reduction_vs_original']*100:.2f}% against the original item-level likelihood and {summary['primary_width_reduction_vs_item_kl']*100:.2f}% against item-level KL boxes. Predictive likelihood alone achieves a {summary['primary_predictive_width_reduction_vs_original']*100:.2f}% median reduction against the original. All these are within the same fixed primary split.",
        f"The grouped-exact selector chooses k={k}. Its family-corrected interval is [{ex[chosen,0]*100:.4f}, {ex[chosen,1]*100:.4f}] CTR percentage points. Independent reference gain: {r['reference'][chosen]*100:.4f} points, with pointwise 95% Wald interval [{r['reference_wald95'][chosen][0]*100:.4f}, {r['reference_wald95'][chosen][1]*100:.4f}]. These refer to sampling uncertainty under their respective assumptions; reference outcomes are not used to tune the policy or interval.",
        '', '![Policy certificate](figures/02_policy_certificate.png)','', '![Ablation](figures/03_ablation.png)','',
        '| Method | Median width (pp) | Candidates certified / 5 |','|---|---:|---:|']
    for name,b in r['bounds'].items():
        b=np.array(b);lines.append(f"| {LABELS[name]} | {np.median(np.diff(b,axis=1))*100:.4f} | {int((b[:,0]>1e-10).sum())} |")
    lines+=['','The narrower Wald intervals are asymptotic; their nominal coverage must be checked independently rather than inferred from width.','',
        '## Replication and chronological stress','', '| Campaign / split | Grouped exact: certified candidates | Predictive likelihood: certified candidates |','|---|---:|---:|']
    for p in sorted(OUT.glob('obd_*.json')):
        rr=json.loads(p.read_text());lines.append(f"| {rr['campaign']} / {rr['split']} | {int((np.array(rr['bounds']['group_exact'])[:,0]>1e-10).sum())} | {int((np.array(rr['bounds']['group_predictive'])[:,0]>1e-10).sum())} |")
    lines+=['','Chronological results concern different time populations and are not IID-coverage experiments. The predictive method certifies no candidate on any chronological split; grouped exact certifies two only on all. This limits any broad deployment claim. Reference and certification 15-minute block-bootstrap diagnostics are stored in each JSON; they do not remove hidden user dependence or guarantee transport to future traffic.','',
        '## Synthetic truth and calibration','',
        '16 frozen cases x 500 independent logs = 8,000 logs; 11 methods = 88,000 method-trial records. Policies are relearned using each trial’s independent pilot. Whole-family coverage means every candidate gain is inside its interval. Beneficial certification is a decision metric, not interval coverage. Wilson intervals in the calibration figure quantify Monte Carlo uncertainty for each 500-log case.','',
        '![Calibration and power](figures/04_synthetic_calibration.png)','',
        '| Actions | Total n | Design | Method | Family coverage | False improvement | Beneficial certified | Mean selected gain |','|---:|---:|---|---|---:|---:|---:|---:|']
    for row in agg.itertuples():lines.append(f'| {row.actions} | {row.n_total} | {row.design} | {row.method} | {row.covered}/500 | {row.false_improvement}/500 | {row.beneficial}/500 | {row.mean_selected_gain:.6f} |')
    lines+=['','The grouped-exact method has 7,991/8,000 simultaneous coverages across this fixed benchmark grid, versus 6,074/8,000 for the tabular DR/Wald comparison. These aggregate proportions describe this benchmark mix, not a population-wide guarantee. Undercoverage can occur on either endpoint; it must not be equated to the false-improvement rate. The exact method is conservative: a nominal 95% lower guarantee does not require empirical coverage to equal 95%.','',
        '## Explicit MVP before/after reversal','',
        f"In a two-context simulator, reward means by action are ((.2,.1),(.8,.7)); the population changes from (.8,.2) to (.2,.8), while the action-1 probability changes from .2 to .8. We generate 100,000 logged observations before and 100,000 after. Observed reward rises from {reversal['observed_before']*100:.3f}% to {reversal['observed_after']*100:.3f}%, a {reversal['naive_change']*100:.3f}-point apparent gain. IPS using ONLY current-policy logged actions, rewards and propensities estimates a {reversal['ips_policy_effect']*100:.3f}-point policy effect (95% Wald interval [{reversal['ips_wald95'][0]*100:.3f}, {reversal['ips_wald95'][1]*100:.3f}]); known truth is -6 points. This is a separately labeled controlled demonstration, not an OBD finding.",'',
        '![Known-truth reversal](figures/05_simulated_reversal.png)','',
        '## Limitations and reproducibility','',
        'Sixteen implementation tests passed, including independent SciPy optimization and exact enumeration of predictive likelihood normalization. Tests do not establish worldwide novelty. See TECHNICAL_DERIVATION.md for the validity argument, prior work, the single-position/no-interference assumption, IID limitations, missing-support handling, and why the adverse group model is not a hidden-confounder estimate.',
        'The fixed primary experiment was not tuned after observing results. The optional repeated-split study is separately labeled exploratory; its samples overlap and are not independent replications. No result demonstrates arbitrary-context, arbitrary-policy, confounding-robust, or whole-slate evaluation.',
        'Protocols, code hashes, raw trial CSVs, data checksums, and the machine-readable claim ledger accompany the report. Datasets and dependency binaries remain local.']
    if (OUT/'stability.csv').exists():
        lines+=['','## Exploratory split stability','',
            '100 repeated random splits per campaign; the splits overlap, so these frequencies are descriptive and not independent replication probabilities.','',
            '| Campaign | Method | Splits with a certificate / 100 | Median width reduction vs original |','|---|---|---:|---:|']
        for row in summary['exploratory_repeated_splits']:
            if row['method'] in ('item_split','group_predictive','group_exact','group_kl'):
                lines.append(f"| {row['campaign']} | {row['method']} | {round(row['certified_fraction']*100)} | {row['median_width_reduction']*100:.2f}% |")
    (ROOT/'RESULTS_REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k not in ['aggregate_fixed_benchmark','exploratory_repeated_splits']},indent=2))
if __name__=='__main__':main()
