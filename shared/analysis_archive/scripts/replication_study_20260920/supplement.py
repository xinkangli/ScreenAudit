"""Prespecified endpoint robustness and transparent post-hoc selection diagnostics."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
from scipy import stats
from study import ROOT,POLICIES,ridge

def main():
 tasks=json.loads((ROOT/'tasks.json').read_text());runs=pd.read_csv(ROOT/'runs.csv');gains=pd.read_csv(ROOT/'paired_gains.csv');index=runs.set_index(['task','seed','policy']);pools={};extra=[];replay=[]
 for t in tasks:
  with np.load(ROOT/(t['task']+'.npz')) as f:pools[t['task']]={k:f[k] for k in f.files}
 for line in (ROOT/'traces.jsonl').open():
  z=json.loads(line);d=pools[z['task']];ids=z['selected'];base={'task':z['task'],'seed':z['seed'],'policy':z['policy'],'study':index.loc[z['task'],z['seed'],z['policy']]['study']}
  for q in [.6,.8]:
   extra.append({**base,'quantile':q,'precision_a':float((d['a'][ids]>max(0.,np.quantile(d['dev_a'],q))).mean()),'precision_b':float((d['b'][ids]>max(0.,np.quantile(d['dev_b'],q))).mean())})
 pd.DataFrame(extra).to_csv(ROOT/'threshold_sensitivity.csv',index=False)
 # realistic task-wide winner (one policy across all seeds), versus intentionally
 # optimistic per-seed winner already recorded by primary analysis.
 winners=[];ranks=[]
 for task,g in gains.groupby('task'):
  avg=g.groupby('policy')[['precision_a','precision_b','gain_precision_a','gain_precision_b']].mean();avg=avg.drop('random');p=avg.precision_a.idxmax();sub=g[g.policy==p].copy()
  for r in sub.to_dict('records'):winners.append({'task':task,'study':r['study'],'seed':r['seed'],'chosen_policy':p,'apparent_gain':r['gain_precision_a'],'replicated_gain':r['gain_precision_b'],'inflation':r['inflation']})
  ranks.append({'task':task,'study':g.study.iloc[0],'spearman_policy_ranking':float(stats.spearmanr(avg.precision_a,avg.precision_b).statistic),'winner_A':p,'winner_B':avg.precision_b.idxmax(),'winner_transfer':p==avg.precision_b.idxmax()})
 pd.DataFrame(winners).to_csv(ROOT/'taskwise_winner_audit.csv',index=False);pd.DataFrame(ranks).to_csv(ROOT/'ranking_audit.csv',index=False)
 # Independent initial-pool halves: select policy using A in seeds0..14, assess
 # A and B only in seeds15..29. This separates seed winner's curse from replication.
 honest=[]
 for task,g in gains.groupby('task'):
  dev=g[(g.seed<15)&(g.policy!='random')].groupby('policy').precision_a.mean();p=dev.idxmax()
  for r in g[(g.seed>=15)&(g.policy==p)].to_dict('records'):honest.append({'task':task,'study':r['study'],'seed':r['seed'],'chosen_policy':p,'apparent_gain':r['gain_precision_a'],'replicated_gain':r['gain_precision_b'],'inflation':r['inflation']})
 pd.DataFrame(honest).to_csv(ROOT/'seed_holdout_winner_audit.csv',index=False)
 # Test exact LOO residuals and invariance to unavailable outcomes.
 rng=np.random.default_rng(45);x=rng.normal(size=(40,24));y=rng.normal(size=40);ids=np.arange(12);pred,nov,skill=ridge(x,ids,y[ids]);hidden=y.copy();hidden[12:]+=100
 assert np.array_equal(pred,ridge(x,ids,hidden[ids])[0]);err=[]
 for i in ids:
  sub=ids[ids!=i];err.append(y[i]-ridge(x,sub,y[sub])[0][i])
 exact=1-np.sum(np.square(err))/np.sum((y[ids]-y[ids].mean())**2);assert abs(exact-skill)<1e-10
 sourcehash=hashlib.sha256(Path(__file__).with_name('study.py').read_bytes()).hexdigest();locked=json.loads((ROOT/'locked_protocol.json').read_text());assert sourcehash==locked['source_sha256']
 (ROOT/'protocol_integrity.json').write_text(json.dumps({'source_unchanged_since_lock':True,'exact_loo_check':True,'hidden_label_invariance':True,'supplement_scope':'evaluation only; no policy or parameter refitting; task-wise and seed-holdout winner analyses refine original locked winner diagnostic'},indent=2))
 print('Supplement complete; source unchanged since protocol lock')

if __name__=='__main__':main()
