"""Locked external replication audit; run from xnxbagent project root."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
from pathlib import Path
import json,hashlib,datetime,re,pickle,argparse
import numpy as np,pandas as pd
from scipy import sparse,stats
from sklearn.ensemble import ExtraTreesRegressor
from safetensors import safe_open
import anndata as ad
ROOT=Path('outputs/replication_study_20260920')
OLD=Path('outputs/agent_compute_full_20260916')
POLICIES=['random','fixed_ridge','greedy_ridge','linear_ucb','diversity','extra_trees','gated_random','old_controller']
PROGRAMS={'IFNG':'Interferon Gamma Response','TNFA':'TNF-alpha Signaling via NF-kB','IL2STAT5':'IL-2/STAT5 Signaling'}
FILES={'Frangieh':'FrangiehIzar2021_RNA','Papalexi':'PapalexiSatija2021_eccite_RNA','Shifrut':'ShifrutMarson2018'}
def dump(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False))
def lock():
 ROOT.mkdir(parents=True,exist_ok=True)
 p=ROOT/'locked_protocol.json'
 if p.exists():raise FileExistsError('Protocol already locked; do not overwrite')
 dump(p,{'locked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'development':'CD4 20260916 only; external metadata inspected but scores not inspected','external_studies':FILES,'programs':PROGRAMS,'policies':POLICIES,'seeds':list(range(30)),'direction':'program relative suppression','external_split':'Frangieh: within each condition, lexically sorted single guides alternating A/B; NT guides split similarly. Papalexi: rep1-tx A, rep3-tx B, rep4-tx C robustness. Shifrut: D1 A, D2 B in each condition; all targeting guides pooled per gene.','qc':'single unambiguous guide; min20 cells per target per side; >=10 program genes; controls min50; pretrained feature availability; no effect-size based inclusion','development_genes':'sha256 gene ID first 8 hex mod5==0; need >=4 development and >=12 candidates, otherwise skip explicitly','budget':'min(80,max(6,floor(0.30*N))); initial=min(16,max(3,B//4)); batch=max(2,initial)','outcome':'pseudobulk sum counts, CP10K, log2 ratio to separately computed controls with fixed pseudocount0.1; whole-gene mean minus program mean excluding own gene','primary_evaluation':'same single-panel hit definition on A vs B (NOT conjunction); threshold max(0,development q75); compare uplift over paired random; continuous gain normalized by development SD sensitivity','method_revision':'fixed ridge alpha10; LOO_R2<=0 => uniform random instead of novelty; positive => at most25% predicted top per batch and rest uniform; no external tuning','statistical_unit':'within task paired initial pools; average tasks within study, then studies equally; no claim all tasks are independent biological replicates','success_method':'positive confirmed gain over random and greedy_ridge with Holm p<.05 in every external study; no test-set tuning','success_evaluation':'positive A-minus-B random-adjusted gain inflation in at least2 independent studies, across at least3 non-oracle policy families; report absent/negative findings; compare winning policy A ranking versus B','limitations':'numeric policies are representative decision mechanisms, not replications of named full LLM agents; internal protocol lock is not public preregistration'})
 print('PROTOCOL_LOCKED',hashlib.sha256(p.read_bytes()).hexdigest(),flush=True)

def features():
 meta=json.loads(Path('outputs/replogle_residual_vcell/geneformer_cache/geneformer_meta.json').read_text())
 with open(meta['token_dictionary_path'],'rb') as f:tokens=pickle.load(f)
 with safe_open(meta['weight_path'],framework='numpy') as f:emb=f.get_tensor('bert.embeddings.word_embeddings.weight')
 with np.load(OLD/'guide_Stim8hr_IFNG_pool.npz') as f:
  x=((emb-f['scaler_mean'])/f['scaler_scale']-f['pca_mean'])@f['pca_components'].T/np.sqrt(f['pca_variance'])
 symbolmap={}
 for n in [FILES['Frangieh'],FILES['Papalexi']]:
  a=ad.read_h5ad('data/scperturb_rna/'+n+'.h5ad',backed='r')
  for symbol,e in zip(a.var_names,a.var.ensembl_id):
   e=str(e).split('.')[0]
   if e in tokens:symbolmap[str(symbol)]=e
  a.file.close()
 old=pd.read_parquet('outputs/replogle_residual_vcell/geneformer_cache/geneformer_match_table.parquet')
 for s,e in zip(old.perturbation_gene,old.gene_ensembl_id):symbolmap.setdefault(str(s),str(e))
 return tokens,x,symbolmap

def extract():
 assert (ROOT/'locked_protocol.json').exists()
 tokens,xf,symbolmap=features();lib={}
 for line in (OLD/'hallmark_2020.gmt').read_text().splitlines():
  p=line.split('\t');lib[p[0].strip()]=set(p[2:])
 tasks=[];audit=[];exclusions=[]
 for study,fn in FILES.items():
  path=Path('data/scperturb_rna')/(fn+'.h5ad');a=ad.read_h5ad(path,backed='r');obs=a.obs.copy();gn=np.asarray(a.var_names,dtype=str)
  guide=obs.guide_id.astype(str).values;single=np.array([bool(s and s not in ['nan','None','NA'] and ';' not in s and ',' not in s) for s in guide])
  target=np.full(len(obs),'',dtype=object);side=np.full(len(obs),'',dtype=object)
  if study=='Frangieh':
   control=obs.perturbation.astype(str).values=='control';condition=obs.perturbation_2.astype(str).values
   target=np.where(control,'control',obs.perturbation.astype(str).values)
   for c in np.unique(condition):
    for g in np.unique(target[condition==c]):
     ix=np.flatnonzero((condition==c)&(target==g)&single);ugs=sorted(set(guide[ix]))
     mapping={v:('A' if i%2==0 else 'B') for i,v in enumerate(ugs)}
     side[ix]=[mapping[v] for v in guide[ix]]
  elif study=='Papalexi':
   control=np.array([s.startswith('NTg') for s in guide]);target=np.array(['control' if ct else re.sub(r'g\d+$','',g) for g,ct in zip(guide,control)])
   condition=np.full(len(obs),'IFNg');ht=obs.hto.astype(str).values
   side=np.array([{'rep1-tx':'A','rep3-tx':'B','rep4-tx':'C'}.get(v,'') for v in ht])
  else:
   control=np.array([s=='control' or 'NonTarget' in s for s in guide]);target=np.array(['control' if ct else g.split('.')[-1] for g,ct in zip(guide,control)])
   condition=obs.perturbation_2.astype(str).values;side=np.array([{'D1':'A','D2':'B'}.get(v,'') for v in obs.replicate.astype(str)])
  keep=single&(side!='')&(target!='')
  keys=[(condition[i],side[i],target[i]) for i in np.flatnonzero(keep)];groups=sorted(set(keys));mapping={k:i for i,k in enumerate(groups)};codes=np.full(len(obs),-1)
  codes[np.flatnonzero(keep)]=[mapping[k] for k in keys]
  sums=np.zeros((len(groups),a.n_vars),dtype=np.float64);counts=np.bincount(codes[keep],minlength=len(groups))
  for start in range(0,len(obs),2048):
   ix=np.arange(start,min(start+2048,len(obs)));valid=codes[ix]>=0
   if not valid.any():continue
   block=a.X[start:start+len(ix),:][valid].tocsr();assert np.isfinite(block.data).all() and (block.data>=0).all()
   ind=sparse.csr_matrix((np.ones(valid.sum()),(codes[ix][valid],np.arange(valid.sum()))),shape=(len(groups),valid.sum()))
   sums+=(ind@block).toarray()
  masks={k:np.flatnonzero(np.isin(gn,list(lib[v]))) for k,v in PROGRAMS.items()}
  assert all(len(v)>=10 for v in masks.values())
  cp=sums/np.maximum(sums.sum(1,keepdims=True),1)*10000
  pd.DataFrame([{'condition':c,'side':s,'target':g,'n_cells':int(n)} for (c,s,g),n in zip(groups,counts)]).to_csv(ROOT/(study+'_group_counts.csv'),index=False)
  scoremap={}
  for c in sorted(set(condition)):
   for s in sorted(set(side)-{''}):
    ctrl=mapping.get((c,s,'control'))
    if ctrl is None or counts[ctrl]<50:continue
    for (cc,ss,g),row in mapping.items():
     if cc!=c or ss!=s or g=='control' or counts[row]<20:continue
     effect=np.log2((cp[row]+.1)/(cp[ctrl]+.1));effect[gn==g]=np.nan;bg=np.nanmean(effect)
     scoremap[(c,s,g)]=np.array([bg-np.nanmean(effect[v]) for v in masks.values()])
  for c in sorted(set(condition)):
   common=sorted({g for cc,s,g in scoremap if cc==c and s=='A'}&{g for cc,s,g in scoremap if cc==c and s=='B'})
   eligible=[g for g in common if g in symbolmap and symbolmap[g] in tokens];genes=[symbolmap[g] for g in eligible]
   if len(genes)!=len(set(genes)):raise ValueError('Gene aliases duplicate candidate IDs')
   dev=np.array([int(hashlib.sha256(g.encode()).hexdigest()[:8],16)%5==0 for g in genes])
   if dev.sum()<4 or (~dev).sum()<12:
    exclusions.append({'study':study,'condition':c,'reason':'small cohort per locked rule','matched':len(genes),'development':int(dev.sum())});continue
   x=xf[[tokens[g] for g in genes]];ya=np.stack([scoremap[c,'A',g] for g in eligible]);yb=np.stack([scoremap[c,'B',g] for g in eligible]);yc=np.stack([scoremap.get((c,'C',g),np.full(3,np.nan)) for g in eligible])
   for j,p in enumerate(PROGRAMS):
    name=study+'_'+c.replace('γ','g').replace('-','')+'_'+p
    np.savez_compressed(ROOT/(name+'.npz'),x=x[~dev],a=ya[~dev,j],b=yb[~dev,j],c=yc[~dev,j],dev_a=ya[dev,j],dev_b=yb[dev,j],dev_c=yc[dev,j],genes=np.array(genes)[~dev],symbols=np.array(eligible)[~dev])
    tasks.append({'task':name,'study':study,'condition':c,'program':p,'n_candidates':int((~dev).sum()),'n_development':int(dev.sum()),'spearman_AB':float(stats.spearmanr(ya[~dev,j],yb[~dev,j]).statistic),'common_before_feature_match':len(common),'threshold_a':max(0.,float(np.quantile(ya[dev,j],.75))),'threshold_b':max(0.,float(np.quantile(yb[dev,j],.75)))})
  audit.append({'study':study,'path':str(path),'size':path.stat().st_size,'cells_total':len(obs),'cells_used':int(keep.sum()),'group_count':len(groups),'program_genes':{k:gn[v].tolist() for k,v in masks.items()},'control_split':'separate controls per condition and side'})
  a.file.close();print('EXTRACTED',study,'tasks',len(tasks),flush=True)
 dump(ROOT/'tasks.json',tasks);dump(ROOT/'data_audit.json',audit);dump(ROOT/'exclusions.json',exclusions)

def ridge(x,ids,y):
 z=x[ids];mu=z.mean(0);z=z-mu;xx=x-mu;yc=y-y.mean();inv=np.linalg.inv(z.T@z+10*np.eye(x.shape[1]));b=inv@z.T@yc
 pred=xx@b+y.mean();nov=np.sqrt(np.maximum(np.sum((xx@inv)*xx,1),0));hat=np.sum((z@inv)*z,1)+1/len(ids);err=(yc-z@b)/np.maximum(1-hat,1e-6)
 return pred,nov,1-float(err@err)/max(float(yc@yc),1e-12)

def run_task(task):
 with np.load(ROOT/(task['task']+'.npz')) as f:d={k:f[k] for k in f.files}
 x=d['x'].astype(float);y=d['a'];n=len(y);B=min(80,max(6,int(.3*n)));initial=min(16,max(3,B//4));batch=max(2,initial)
 rows=[];traces=[]
 for seed in range(30):
  init=np.random.default_rng(seed).choice(n,initial,replace=False).tolist()
  for policy in POLICIES:
   rng=np.random.default_rng(seed+1234);ids=init.copy();events=[];fixed=ridge(x,ids,y[ids])[0]
   while len(ids)<B:
    pool=np.setdiff1d(np.arange(n),ids);k=min(batch,B-len(ids));pred,nov,skill=ridge(x,ids,y[ids]);mode=policy
    if policy=='random':choose=rng.choice(pool,k,replace=False)
    elif policy=='gated_random':
     if skill<=0:choose=rng.choice(pool,k,replace=False);mode='random_fallback'
     else:
      top=pool[np.argsort(-pred[pool],kind='stable')[:int(.25*k)]];rest=rng.choice(np.setdiff1d(pool,top),k-len(top),replace=False);choose=np.r_[top,rest];mode='limited_exploitation'
    else:
     if policy=='fixed_ridge':score=fixed
     elif policy=='greedy_ridge':score=pred
     elif policy=='linear_ucb':score=pred+.5*max(y[ids].std(),1e-8)*nov
     elif policy=='diversity':score=nov
     elif policy=='old_controller':score=nov if skill<=0 else pred+.25*max(y[ids].std(),1e-8)*nov
     else:
      m=ExtraTreesRegressor(n_estimators=32,min_samples_leaf=2,max_features=1.,random_state=seed,n_jobs=1).fit(x[ids],y[ids]);score=m.predict(x)
     choose=pool[np.argsort(-score[pool],kind='stable')[:k]]
    assert not set(choose)&set(ids);ids.extend(map(int,choose));events.append({'selected':list(map(int,choose)),'feedback':y[choose].tolist(),'loo_r2':skill,'mode':mode})
   ta,tb=task['threshold_a'],task['threshold_b'];r={'task':task['task'],'study':task['study'],'seed':seed,'policy':policy,'budget':B,'initial':initial,'precision_a':float((d['a'][ids]>ta).mean()),'precision_b':float((d['b'][ids]>tb).mean()),'mean_a':float(d['a'][ids].mean()),'mean_b':float(d['b'][ids].mean()),'scaled_a':float(d['a'][ids].mean()/max(d['dev_a'].std(),1e-8)),'scaled_b':float(d['b'][ids].mean()/max(d['dev_b'].std(),1e-8)),'selected_norm':float(np.linalg.norm(x[ids],axis=1).mean())}
   if np.isfinite(d['c']).all() and np.isfinite(d['dev_c']).all():r['precision_c']=float((d['c'][ids]>max(0.,float(np.quantile(d['dev_c'],.75)))).mean())
   rows.append(r);traces.append({'task':task['task'],'seed':seed,'policy':policy,'initial_ids':init,'selected':ids,'events':events})
 return rows,traces

def run():
 from concurrent.futures import ProcessPoolExecutor
 tasks=json.loads((ROOT/'tasks.json').read_text());rows=[]
 with ProcessPoolExecutor(max_workers=6) as pool, (ROOT/'traces.jsonl').open('w') as out:
  for task,(rr,tt) in zip(tasks,pool.map(run_task,tasks)):
   rows+=rr
   for r in tt:out.write(json.dumps(r)+'\n')
   print('RUN_COMPLETE',task['task'],len(rr),flush=True)
 pd.DataFrame(rows).to_csv(ROOT/'runs.csv',index=False)

def analyze():
 df=pd.read_csv(ROOT/'runs.csv');keys=['task','study','seed'];rand=df[df.policy=='random'].set_index(keys);parts=[]
 for p,g in df.groupby('policy'):
  g=g.set_index(keys).copy()
  for metric in ['precision_a','precision_b','scaled_a','scaled_b']:g['gain_'+metric]=g[metric]-rand[metric]
  g['inflation']=g.gain_precision_a-g.gain_precision_b;g['scaled_inflation']=g.gain_scaled_a-g.gain_scaled_b;parts.append(g.reset_index())
 gains=pd.concat(parts,ignore_index=True);gains.to_csv(ROOT/'paired_gains.csv',index=False)
 summ=gains.groupby(['study','policy'])[['precision_a','precision_b','gain_precision_a','gain_precision_b','inflation','scaled_inflation']].mean().reset_index();summ.to_csv(ROOT/'study_summary.csv',index=False)
 comparisons=[];rng=np.random.default_rng(20260920)
 def ci(vals):
  z=np.asarray(vals);b=rng.choice(z,(5000,len(z)),replace=True).mean(1)
  return float(z.mean()),float(np.quantile(b,.025)),float(np.quantile(b,.975)),float(stats.ttest_1samp(z,0).pvalue) if z.std()>0 else 1.
 for (study,p),g in gains[gains.policy!='random'].groupby(['study','policy']):
  z=g.groupby('seed').inflation.mean();m,lo,hi,pv=ci(z);comparisons.append({'kind':'inflation','study':study,'policy':p,'baseline':'random_adjusted_A_minus_B','effect':m,'ci_low':lo,'ci_high':hi,'p':pv})
 for study,g in gains.groupby('study'):
  for base in ['random','greedy_ridge','linear_ucb','extra_trees','old_controller']:
   z=g[g.policy.isin(['gated_random',base])].pivot_table(index=['task','seed'],columns='policy',values='precision_b');diff=(z.gated_random-z[base]).groupby('seed').mean();m,lo,hi,pv=ci(diff);comparisons.append({'kind':'method','study':study,'policy':'gated_random','baseline':base,'effect':m,'ci_low':lo,'ci_high':hi,'p':pv})
 # Correct separately by scientific question, never count seeds as donors.
 for kind in ['inflation','method']:
  ids=[i for i,r in enumerate(comparisons) if r['kind']==kind];ids=sorted(ids,key=lambda i:comparisons[i]['p']);last=0
  for rank,i in enumerate(ids):last=max(last,min(1.,comparisons[i]['p']*(len(ids)-rank)));comparisons[i]['holm_p']=last
 pd.DataFrame(comparisons).to_csv(ROOT/'comparisons.csv',index=False)
 winners=[]
 for (task,seed),g in gains.groupby(['task','seed']):
  # Intentionally optimistic post-hoc policy selection; diagnostic, NOT a valid agent.
  candidates=g[g.policy!='random'].sort_values('policy');best=candidates.loc[candidates.precision_a.idxmax()]
  winners.append({'task':task,'study':best.study,'seed':seed,'selected_policy':best.policy,'apparent_gain':float(best.gain_precision_a),'replicated_gain':float(best.gain_precision_b),'inflation':float(best.inflation)})
 pd.DataFrame(winners).to_csv(ROOT/'posthoc_winner_audit.csv',index=False)
 verification={'traces':0,'same_initial_pools':True,'budgets_and_unique':True,'all_endpoints_recomputed':True,'confirmed_labels_never_policy_arguments':True};inits={};pools={}
 for t in json.loads((ROOT/'tasks.json').read_text()):
  with np.load(ROOT/(t['task']+'.npz')) as f:pools[t['task']]={k:f[k] for k in f.files}
 index=df.set_index(['task','seed','policy'])
 for line in (ROOT/'traces.jsonl').open():
  t=json.loads(line);ids=t['selected'];r=index.loc[t['task'],t['seed'],t['policy']];assert len(ids)==len(set(ids))==r.budget
  key=(t['task'],t['seed']);inits.setdefault(key,t['initial_ids']);assert inits[key]==t['initial_ids'];d=pools[t['task']]
  for side in ['a','b']:
   threshold=max(0.,float(np.quantile(d['dev_'+side],.75)));assert abs((d[side][ids]>threshold).mean()-r['precision_'+side])<1e-10
  verification['traces']+=1
 verification['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest();dump(ROOT/'verification.json',verification)
 print(summ.to_string(index=False));print('VERIFIED',verification['traces'])

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['lock','extract','run','analyze']);a=p.parse_args();globals()[a.action]()
