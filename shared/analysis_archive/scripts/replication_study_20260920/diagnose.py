import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
import json
from pathlib import Path
import pandas as pd,numpy as np
from scipy.stats import spearmanr
OLD=Path('outputs/agent_compute_full_20260916');OUT=Path('outputs/replication_study_20260920');tasks=json.loads((OLD/'tasks.json').read_text());pools={};taskrows=[]
for t in tasks:
 with np.load(OLD/(t['task']+'_pool.npz')) as f:p={k:f[k] for k in f.files}
 pools[t['task']]=p;nrm=np.linalg.norm(p['features'],axis=1);ya=p['discovery'];yb=p['confirmation'];pa=np.maximum(p['development_y'].std(),1e-8);pb=np.maximum(p['development_v'].std(),1e-8)
 taskrows.append({'task':t['task'],'pair':t['pair'],'norm_spearman_A':spearmanr(nrm,ya).statistic,'norm_spearman_B':spearmanr(nrm,yb).statistic,'norm_spearman_replica_disagreement':spearmanr(nrm,np.abs(ya/pa-yb/pb)).statistic,'replica_spearman':spearmanr(ya,yb).statistic})
rows=[];modes=[]
for line in (OLD/'traces.jsonl').open():
 t=json.loads(line);p=pools[t['task']];ids=t['selected'];nrm=np.linalg.norm(p['features'],axis=1)
 rows.append({'task':t['task'],'seed':t['seed'],'policy':t['policy'],'mean_norm':float(nrm[ids].mean()),'norm_ratio_to_pool':float(nrm[ids].mean()/nrm.mean()),'new_selection_norm':float(nrm[ids[16:]].mean()),'mean_discovery':float(p['discovery'][ids].mean()),'mean_confirmation':float(p['confirmation'][ids].mean())})
 if t['policy']=='controller':
  for ev in t['events']:modes.append({'task':t['task'],'seed':t['seed'],**{k:ev[k] for k in ['mode','loo_r2']}})
pd.DataFrame(taskrows).to_csv(OUT/'development_task_diagnosis.csv',index=False);pd.DataFrame(rows).to_csv(OUT/'development_selection_diagnosis.csv',index=False);pd.DataFrame(modes).to_csv(OUT/'development_modes.csv',index=False)
r=pd.DataFrame(rows);m=pd.DataFrame(modes)
summary={'controller_exploration_fraction':float((m['mode']=='explore_unreliable_model').mean()),'median_observed_loo_r2':float(m.loo_r2.median()),'norm_ratio_by_policy':r.groupby('policy').norm_ratio_to_pool.mean().to_dict(),'median_replica_spearman':float(pd.DataFrame(taskrows).replica_spearman.median()),'interpretation':'Associational diagnosis on previously seen CD4 development data; does not establish causal mediation or generalize automatically.'}
(OUT/'development_diagnosis.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
