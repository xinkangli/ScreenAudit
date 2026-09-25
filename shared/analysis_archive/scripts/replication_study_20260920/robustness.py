"""Secondary robustness of selection multiplicity; no new fitting or tuning."""
import json,zipfile
from pathlib import Path
import numpy as np,pandas as pd
ROOT=Path('outputs/replication_study_20260920')
base=pd.read_csv(ROOT/'runs.csv');sens=pd.read_csv(ROOT/'threshold_sensitivity.csv')
rows=[]
def audit(frame,label,drop=None,ac='precision_a',bc='precision_b'):
 frame=frame[(frame.policy!='random')&(frame.policy!=drop)]
 for (task,study,seed),g in frame.groupby(['task','study','seed']):
  g=g.sort_values('policy');a=g[ac].to_numpy();b=g[bc].to_numpy();rng=np.random.default_rng(seed+20260920);deltas=[]
  for _ in range(50):
   order=rng.permutation(len(g));j=order[np.argmax(a[order])];k=order[0]
   assert a[j]>=a[k]-1e-12
   deltas.append((a[j]-a[k])-(b[j]-b[k]))
  rows.append({'analysis':label,'task':task,'study':study,'seed':seed,'delta':float(np.mean(deltas))})
audit(base,'q75')
for q,g in sens.groupby('quantile'):audit(g,'q'+str(int(q*100)))
audit(base,'continuous_scaled',ac='scaled_a',bc='scaled_b')
audit(base[base.precision_c.notna()],'third_panel_C',bc='precision_c')
for p in sorted(set(base.policy)-{'random'}):audit(base,'without_'+p,drop=p)
raw=pd.DataFrame(rows);raw.to_csv(ROOT/'selection_robustness.csv',index=False)
summary=[];rng=np.random.default_rng(20260920)
for (label,study),g in raw.groupby(['analysis','study']):
 z=g.groupby('seed').delta.mean().to_numpy();boot=rng.choice(z,(10000,len(z)),replace=True).mean(1)
 summary.append({'analysis':label,'study':study,'effect':float(z.mean()),'ci_low':float(np.quantile(boot,.025)),'ci_high':float(np.quantile(boot,.975))})
pd.DataFrame(summary).to_csv(ROOT/'selection_robustness_summary.csv',index=False)
prior=pd.read_csv(ROOT/'selection_multiplicity_contrasts.csv').set_index('study')
for r in summary:
 if r['analysis']=='q75':assert abs(r['effect']-prior.loc[r['study'],'selection_optimism'])<1e-12
snap=json.loads((ROOT/'report_snapshot.json').read_text());snap['selection_robustness']=summary
snap['selection_verification']={'q75_independent_recomputation':True,'discovery_gain_nonnegative_each_order':True,'orders_averaged_within_seed':50,'scope':'All robustness is secondary and descriptive; pointwise intervals, no new confirmatory success claims.'}
(ROOT/'report_snapshot.json').write_text(json.dumps(snap,indent=2));print(pd.DataFrame(summary).to_string(index=False))
with zipfile.ZipFile(ROOT/'report_inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
 for n in ['report_snapshot.json','external_gains.png','winner_bias.png','selection_multiplicity.png']:z.write(ROOT/n,n)
