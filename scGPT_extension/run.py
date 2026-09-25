import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,hashlib,datetime
import numpy as np,pandas as pd,torch
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
P=Path(__file__).parent;R=Path('outputs/replication_study_20260920')
v=json.loads((P/'vocab.json').read_text());tasks=json.loads((R/'tasks.json').read_text())
coverage=[];eligible=[];all_symbols=set()
for t in tasks:
 d=np.load(R/(t['task']+'.npz'));missing=[str(s) for s in d['symbols'] if s not in v];all_symbols.update(d['symbols'])
 coverage.append({'task':t['task'],'total':len(d['symbols']),'matched':len(d['symbols'])-len(missing),'missing':missing})
 if not missing:eligible.append(t)
protocol={'date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'model':'wanglab/scGPT-human','revision':json.loads((P/'model_api.json').read_text())['sha'],'feature':'static encoder.embedding.weight followed by encoder.enc_norm; no contextual transformer inference','policy':'updating ridge alpha10','projection':'standard scale then PCA24 whiten; randomized random_state20260923 iterated_power2; fit vocabulary tokens excluding all archived candidates and special tokens, sha256(symbol) first8 mod5==0','eligibility':'all original candidate symbols present; no alias substitution; preserve original pools and thresholds','seeds':list(range(30)),'analysis':'exploratory fixed-policy representation example; two eligible sources; no winner selection or tuning','coverage':coverage}
(P/'protocol.json').write_text(json.dumps(protocol,indent=2))
state=torch.load(P/'best_model.pt',map_location='cpu',weights_only=True)
e=state['encoder.embedding.weight'];e=torch.nn.functional.layer_norm(e,(e.shape[1],),state['encoder.enc_norm.weight'],state['encoder.enc_norm.bias'],1e-5).numpy()
dev=sorted(s for s in v if s not in all_symbols and not s.startswith('<') and int(hashlib.sha256(s.encode()).hexdigest()[:8],16)%5==0)
sc=StandardScaler().fit(e[[v[s] for s in dev]]);pc=PCA(n_components=24,svd_solver='randomized',iterated_power=2,random_state=20260923,whiten=True).fit(sc.transform(e[[v[s] for s in dev]]))
np.savez_compressed(P/'projection.npz',scaler_mean=sc.mean_,scaler_scale=sc.scale_,pca_mean=pc.mean_,pca_components=pc.components_,pca_variance=pc.explained_variance_,development_symbols=np.array(dev))
print('FEATURES',len(dev),e.shape,flush=True)
def pred(x,ids,y):
 z=x[ids];mu=z.mean(0);z=z-mu;yc=y-y.mean();return (x-mu)@np.linalg.inv(z.T@z+10*np.eye(x.shape[1]))@z.T@yc+y.mean()
rows=[];traces=[]
for t in eligible:
 d=np.load(R/(t['task']+'.npz'));gx=d['x'].astype(float);sx=pc.transform(sc.transform(e[[v[str(s)] for s in d['symbols']]])).astype(float);n=len(gx);budget=min(80,max(6,int(.3*n)));initial=min(16,max(3,budget//4));batch=max(2,initial)
 for seed in range(30):
  init=np.random.default_rng(seed).choice(n,initial,replace=False).tolist()
  for name,x in [('random',gx),('geneformer_updating',gx),('scgpt_updating',sx)]:
   ids=init.copy();rng=np.random.default_rng(seed+1234)
   while len(ids)<budget:
    pool=np.setdiff1d(np.arange(n),ids);k=min(batch,budget-len(ids))
    choose=rng.choice(pool,k,replace=False) if name=='random' else pool[np.argsort(-pred(x,ids,d['a'][ids])[pool],kind='stable')[:k]]
    ids.extend(map(int,choose))
   assert len(set(ids))==budget
   rows.append({'task':t['task'],'study':t['study'],'seed':seed,'policy':name,'a':float((d['a'][ids]>t['threshold_a']).mean()),'b':float((d['b'][ids]>t['threshold_b']).mean()),'budget':budget})
   traces.append({'task':t['task'],'seed':seed,'policy':name,'initial':init,'selected':ids})
 print('DONE',t['task'],flush=True)
f=pd.DataFrame(rows);f.to_csv(P/'runs.csv',index=False)
with (P/'traces.jsonl').open('w') as out:
 for t in traces:out.write(json.dumps(t)+'\n')
old=pd.read_csv(R/'runs.csv');checks=[]
for new,oldname in [('random','random'),('geneformer_updating','greedy_ridge')]:
 a=f[f.policy==new].merge(old[old.policy==oldname],on=['task','study','seed']);err=max(abs(a['a']-a['precision_a']).max(),abs(a['b']-a['precision_b']).max());checks.append({'policy':new,'maximum_endpoint_error':float(err)});assert err<1e-12

rnd=f[f.policy=='random'].set_index(['task','study','seed']);summ=[]
def summarize(study,policy,metric,y):
 y=np.asarray(y);bs=np.random.default_rng(20260923).choice(y,(10000,len(y)),replace=True).mean(1)
 summ.append({'study':study,'policy':policy,'metric':metric,'mean_pp':float(y.mean()),'low_pp':float(np.quantile(bs,.025)),'high_pp':float(np.quantile(bs,.975))})
for study in sorted(f.study.unique()):
 for policy in ['geneformer_updating','scgpt_updating']:
  z=f[(f.study==study)&(f.policy==policy)].set_index(['task','study','seed'])
  g=(z[['a','b']]-rnd.loc[z.index,['a','b']]).reset_index().groupby('seed')[['a','b']].mean()*100
  for metric in ['a','b']:summarize(study,policy,metric,g[metric])
 ss=f[(f.study==study)&(f.policy=='scgpt_updating')].set_index(['task','seed'])
 gg=f[(f.study==study)&(f.policy=='geneformer_updating')].set_index(['task','seed'])
 y=(ss.b-gg.b).reset_index().groupby('seed').b.mean()*100
 summarize(study,'scgpt_minus_geneformer','b',y)
pd.DataFrame(summ).to_csv(P/'summary.csv',index=False)
(P/'verification.json').write_text(json.dumps({'checks':checks,'tasks':len(eligible),'runs':len(f),'new_scgpt_runs':int((f.policy=='scgpt_updating').sum()),'development_tokens':len(dev),'no_response_based_tuning':True},indent=2))
print(pd.DataFrame(summ).to_string(index=False),flush=True)
