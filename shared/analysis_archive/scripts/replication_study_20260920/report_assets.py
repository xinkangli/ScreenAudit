import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,zipfile,hashlib
import numpy as np,pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from study import ROOT,POLICIES

def main():
 summ=pd.read_csv(ROOT/'study_summary.csv');comp=pd.read_csv(ROOT/'comparisons.csv');runs=pd.read_csv(ROOT/'runs.csv');ranks=pd.read_csv(ROOT/'ranking_audit.csv')
 winner_types={'per_seed_optimistic':'posthoc_winner_audit.csv','task_wide':'taskwise_winner_audit.csv','seed_holdout':'seed_holdout_winner_audit.csv'};winner_summary=[];rng=np.random.default_rng(20092026)
 for kind,file in winner_types.items():
  w=pd.read_csv(ROOT/file)
  for study,g in w.groupby('study'):
   z=g.groupby('seed')[['apparent_gain','replicated_gain','inflation']].mean();boots=rng.choice(z.inflation.values,(10000,len(z)),replace=True).mean(1)
   winner_summary.append({'kind':kind,'study':study,'apparent_gain':float(z.apparent_gain.mean()),'replicated_gain':float(z.replicated_gain.mean()),'inflation':float(z.inflation.mean()),'ci_low':float(np.quantile(boots,.025)),'ci_high':float(np.quantile(boots,.975)),'p':float(stats.ttest_1samp(z.inflation,0).pvalue) if z.inflation.std()>0 else 1.})
 for kind in winner_types:
  ix=sorted([i for i,v in enumerate(winner_summary) if v['kind']==kind],key=lambda i:winner_summary[i]['p']);last=0
  for rank,i in enumerate(ix):last=max(last,min(1.,winner_summary[i]['p']*(len(ix)-rank)));winner_summary[i]['holm_p']=last
 pd.DataFrame(winner_summary).to_csv(ROOT/'winner_summary.csv',index=False)
 sensitivity=pd.read_csv(ROOT/'threshold_sensitivity.csv');sensitivity_summary=[]
 for q,df in sensitivity.groupby('quantile'):
  r=df[df.policy=='random'].set_index(['task','seed'])
  for (study,p),g in df.groupby(['study','policy']):
   g=g.set_index(['task','seed']);rr=r.reindex(g.index);sensitivity_summary.append({'quantile':q,'study':study,'policy':p,'inflation':float(((g.precision_a-rr.precision_a)-(g.precision_b-rr.precision_b)).mean())})
 pd.DataFrame(sensitivity_summary).to_csv(ROOT/'sensitivity_summary.csv',index=False)
 studies=sorted(summ.study.unique());names={'fixed_ridge':'Fixed ridge','greedy_ridge':'Greedy ridge','linear_ucb':'Linear UCB','diversity':'Diversity','extra_trees':'Extra Trees','gated_random':'Gated random','old_controller':'Old controller'}
 plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
 fig,axes=plt.subplots(1,len(studies),figsize=(13,4),sharey=True,squeeze=False)
 for ax,study in zip(axes[0],studies):
  g=summ[(summ.study==study)&(summ.policy!='random')].set_index('policy').loc[list(names)];y=np.arange(len(g));ax.barh(y-.17,g.gain_precision_a*100,.32,label='Discovery A',color='#467db0');ax.barh(y+.17,g.gain_precision_b*100,.32,label='Replication B',color='#278b73');ax.set_yticks(y);ax.set_yticklabels([names[p] for p in g.index]);ax.set_title(study);ax.axvline(0,color='black',lw=.7);ax.set_xlabel('Precision gain vs random (pp)')
 axes[0,0].invert_yaxis();axes[0,-1].legend(frameon=False,fontsize=9);fig.tight_layout()
 for ext in ['png','svg','pdf']:fig.savefig(ROOT/('external_gains.'+ext),dpi=200,bbox_inches='tight')
 plt.close(fig)
 fig,axes=plt.subplots(1,3,figsize=(11,3.5),sharey=True)
 for ax,(kind,label) in zip(axes,zip(winner_types,['Per-seed winner (optimistic)','Task-wide winner','Winner with seed holdout'])):
  g=pd.DataFrame(winner_summary).query('kind==@kind').set_index('study').reindex(studies);xx=np.arange(len(studies));ax.bar(xx-.18,g.apparent_gain*100,.35,label='Discovery A',color='#467db0');ax.bar(xx+.18,g.replicated_gain*100,.35,label='Replication B',color='#278b73');ax.set_xticks(xx);ax.set_xticklabels(studies,rotation=20);ax.set_title(label,fontsize=10);ax.axhline(0,color='black',lw=.7)
 axes[0].set_ylabel('Selected policy gain vs random (pp)');axes[-1].legend(frameon=False,fontsize=8);fig.tight_layout()
 for ext in ['png','svg','pdf']:fig.savefig(ROOT/('winner_bias.'+ext),dpi=200,bbox_inches='tight')
 plt.close(fig)
 checks={'method_success':False,'evaluation_success':False}
 method=comp[comp.kind=='method'];checks['method_success']=all(((method.study==s)&(method.baseline==b)&(method.effect>0)&(method.holm_p<.05)).any() for s in studies for b in ['random','greedy_ridge'])
 infl=comp[(comp.kind=='inflation')&(comp.effect>0)&(comp.holm_p<.05)];checks['positive_inflation_studies']=sorted(infl.study.unique());checks['positive_inflation_policies']=sorted(infl.policy.unique());checks['evaluation_success']=len(infl.study.unique())>=2 and len(infl.policy.unique())>=3
 snap={'summary':summ.to_dict('records'),'comparisons':comp.to_dict('records'),'tasks':json.loads((ROOT/'tasks.json').read_text()),'exclusions':json.loads((ROOT/'exclusions.json').read_text()),'diagnosis':json.loads((ROOT/'development_diagnosis.json').read_text()),'protocol':json.loads((ROOT/'locked_protocol.json').read_text()),'verification':json.loads((ROOT/'verification.json').read_text()),'integrity':json.loads((ROOT/'protocol_integrity.json').read_text()),'winner_summary':winner_summary,'ranks':ranks.to_dict('records'),'sensitivity':sensitivity_summary,'success_checks':checks,'runs':len(runs),'third_replicate_records':int(runs.get('precision_c',pd.Series(dtype=float)).notna().sum())}
 (ROOT/'report_snapshot.json').write_text(json.dumps(snap,indent=2,ensure_ascii=False));print(json.dumps(checks,indent=2));print(pd.DataFrame(winner_summary).to_string(index=False))
 with zipfile.ZipFile(ROOT/'report_inputs.zip','w',zipfile.ZIP_DEFLATED) as z:
  for n in ['report_snapshot.json','external_gains.png','winner_bias.png']:z.write(ROOT/n,n)

if __name__=='__main__':main()
