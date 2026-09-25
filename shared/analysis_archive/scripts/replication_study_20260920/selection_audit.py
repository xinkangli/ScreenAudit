"""Secondary selection-multiplicity audit; no policy changes or re-fitting.
This explanatory analysis was specified after the initial external results.
50 tie/subset orders are averaged within each seed, never counted as replicates.
"""
import json
from pathlib import Path
import numpy as np,pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path('outputs/replication_study_20260920')
df=pd.read_csv(ROOT/'runs.csv');rows=[]
for (task,study,seed),g in df[df.policy!='random'].groupby(['task','study','seed']):
 g=g.sort_values('policy');a=g.precision_a.to_numpy();b=g.precision_b.to_numpy();rng=np.random.default_rng(seed+20260920)
 for repetition in range(50):
  order=rng.permutation(len(g))
  for m in [1,2,4,7]:
   choices=order[:m];j=choices[np.argmax(a[choices])]
   rows.append({'task':task,'study':study,'seed':seed,'order':repetition,'choices':m,'precision_a':a[j],'precision_b':b[j],'gap':a[j]-b[j]})
raw=pd.DataFrame(rows);avg=raw.groupby(['task','study','seed','choices'])[['precision_a','precision_b','gap']].mean().reset_index();avg.to_csv(ROOT/'selection_multiplicity.csv',index=False)
summary=avg.groupby(['study','choices'])[['precision_a','precision_b','gap']].mean().reset_index();summary.to_csv(ROOT/'selection_multiplicity_summary.csv',index=False)
rng=np.random.default_rng(20260920);comparisons=[]
for study,g in avg.groupby('study'):
 z=g.groupby(['seed','choices'])[['precision_a','precision_b','gap']].mean().reset_index();p=z.pivot(index='seed',columns='choices',values='gap');delta=p[7]-p[1];boots=rng.choice(delta.values,(10000,len(delta)),replace=True).mean(1)
 pa=z.pivot(index='seed',columns='choices',values='precision_a');pb=z.pivot(index='seed',columns='choices',values='precision_b')
 comparisons.append({'study':study,'discovery_improvement':float((pa[7]-pa[1]).mean()),'replication_improvement':float((pb[7]-pb[1]).mean()),'selection_optimism':float(delta.mean()),'ci_low':float(np.quantile(boots,.025)),'ci_high':float(np.quantile(boots,.975)),'p':float(stats.ttest_1samp(delta,0).pvalue)})
order=sorted(range(len(comparisons)),key=lambda i:comparisons[i]['p']);last=0
for rank,i in enumerate(order):last=max(last,min(1.,comparisons[i]['p']*(len(order)-rank)));comparisons[i]['holm_p']=last
pd.DataFrame(comparisons).to_csv(ROOT/'selection_multiplicity_contrasts.csv',index=False)
fig,axes=plt.subplots(1,len(comparisons),figsize=(11,3.5),sharey=True)
for ax,study in zip(np.atleast_1d(axes),sorted(summary.study.unique())):
 g=summary[summary.study==study];base=g[g.choices==1].iloc[0]
 ax.plot(g.choices,100*(g.precision_a-base.precision_a),'-o',label='Discovery A',color='#467db0');ax.plot(g.choices,100*(g.precision_b-base.precision_b),'-o',label='Replication B',color='#278b73');ax.set(title=study,xlabel='Policies available for post-hoc selection');ax.set_xticks([1,2,4,7]);ax.axhline(0,color='grey',lw=.6);ax.spines[['top','right']].set_visible(False)
axes[0].set_ylabel('Improvement vs choosing 1 policy (pp)');axes[-1].legend(frameon=False,fontsize=8);fig.tight_layout()
for ext in ['png','pdf','svg']:fig.savefig(ROOT/('selection_multiplicity.'+ext),dpi=200,bbox_inches='tight')
snap=json.loads((ROOT/'report_snapshot.json').read_text());snap['selection_contrasts']=comparisons;snap['selection_scope']='Secondary explanatory analysis after initial external results; does not turn initial failed primary hypotheses into successful ones.'
snap['extension_protocol']=json.loads(Path('outputs/replication_extension_20260920/extension_protocol.json').read_text());snap['extension_exclusions']=json.loads(Path('outputs/replication_extension_20260920/exclusions.json').read_text())
(ROOT/'report_snapshot.json').write_text(json.dumps(snap,indent=2));print(pd.DataFrame(comparisons).to_string(index=False))
import zipfile
with zipfile.ZipFile(ROOT/'report_inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in ['report_snapshot.json','external_gains.png','winner_bias.png','selection_multiplicity.png']:z.write(ROOT/n,n)
