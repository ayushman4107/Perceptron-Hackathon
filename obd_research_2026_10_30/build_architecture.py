from pathlib import Path
import sys, os
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.deps'))
os.environ['MPLCONFIGDIR']=str(ROOT/'tmp/matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
plt.rcParams.update({'font.family':'DejaVu Sans','text.color':'black','svg.fonttype':'none','pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(16,8.5));fig.patch.set_facecolor('white');ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
fig.subplots_adjust(left=.02,right=.98,top=.98,bottom=.02)
def text(x,y,s,size=13,weight='normal',ha='center',color='black'):
 ax.text(x,y,s,fontsize=size,fontweight=weight,ha=ha,va='center',color=color,linespacing=1.6)
def box(x,y,w,h,title,body,fill='#f5f7f9',edge='#b5bdc7'):
 ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=0.008,rounding_size=0.012',facecolor=fill,edgecolor=edge,linewidth=1.3))
 text(x,y+h*.20,title,15,'bold');text(x,y-h*.18,body,13.5)
def arrow(points,dashed=False):
 for a,b in zip(points[:-2],points[1:-1]):ax.plot([a[0],b[0]],[a[1],b[1]],color='#586472',lw=1.6,ls='--' if dashed else '-')
 ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',mutation_scale=15,lw=1.6,color='#586472',linestyle='--' if dashed else '-'))
text(.035,.94,'PoliSee | System architecture',25,'bold',ha='left')
text(.035,.883,'From logged decisions to evidence about a different policy',15,ha='left')
ax.plot([.035,.965],[.84,.84],color='#d3d9df',lw=1)
for x,t in [(.13,'1  INPUT'),(.365,'2  SPLIT'),(.63,'3  EVALUATE'),(.875,'4  REPORT')]:text(x,.795,t,12,'bold')
box(.13,.49,.18,.19,'Logged decisions','Actions, rewards\nand selection probabilities')
box(.365,.66,.19,.15,'Pilot','Select and freeze\ncandidate policies')
box(.365,.46,.19,.15,'Certification','Estimate candidate\npolicy gains')
box(.365,.24,.19,.15,'Reference','Independent check\nonly; no tuning')
arrow([(.228,.49),(.247,.49),(.247,.66),(.262,.66)])
arrow([(.247,.49),(.247,.46),(.262,.46)])
arrow([(.247,.46),(.247,.24),(.262,.24)])
box(.63,.64,.22,.17,'Policy-ratio compression','Check matching ratios;\ngroup equivalent actions',fill='#eef5fa',edge='#8ca9c4')
box(.63,.405,.22,.17,'Uncertainty estimation','Gain bounds + validity checks\nIPS / DR comparisons',fill='#eef5fa',edge='#8ca9c4')
arrow([(.468,.66),(.512,.66)])
arrow([(.468,.46),(.49,.46),(.49,.59),(.512,.59)])
arrow([(.63,.547),(.63,.498)])
box(.875,.49,.19,.36,'Decision report','Gain interval + assumptions\n\nEvidence of improvement*\nor insufficient evidence',fill='#edf6f2',edge='#92b4a4')
arrow([(.748,.405),(.772,.405)])
arrow([(.468,.24),(.875,.24),(.875,.302)],True)
text(.675,.205,'Held-out comparison',11)
text(.035,.10,'* Improvement requires a positive lower bound and satisfied validity conditions.',11,ha='left')
text(.035,.052,'Reference outcomes are empirical estimates, not exact counterfactual ground truth.',11,ha='left')
for ext in ['png','svg','pdf']:
 fig.savefig(ROOT/'figures'/f'06_polisee_architecture.{ext}',dpi=180,facecolor='white')
