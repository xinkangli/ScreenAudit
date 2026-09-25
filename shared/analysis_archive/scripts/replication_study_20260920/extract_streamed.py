"""I/O-only amendment: stream CSC by columns; scientific protocol unchanged."""
from pathlib import Path
import hashlib,json,datetime
path=Path(__file__).with_name('study.py');source=path.read_text()
old="""  for start in range(0,len(obs),2048):
   ix=np.arange(start,min(start+2048,len(obs)));valid=codes[ix]>=0
   if not valid.any():continue
   block=a.X[start:start+len(ix),:][valid].tocsr();assert np.isfinite(block.data).all() and (block.data>=0).all()
   ind=sparse.csr_matrix((np.ones(valid.sum()),(codes[ix][valid],np.arange(valid.sum()))),shape=(len(groups),valid.sum()))
   sums+=(ind@block).toarray()
"""
new="""  backed=a.X
  if getattr(backed,'format','csr')=='csc':
   agg=sparse.csr_matrix((np.ones(keep.sum()),(codes[keep],np.flatnonzero(keep))),shape=(len(groups),len(obs)))
   for start in range(0,a.n_vars,256):
    stop=min(start+256,a.n_vars);block=backed[:,start:stop].tocsc()
    assert np.isfinite(block.data).all() and (block.data>=0).all()
    sums[:,start:stop]=(agg@block).toarray()
   print('CSC_AGGREGATED',study,flush=True)
  else:
   for start in range(0,len(obs),2048):
    ix=np.arange(start,min(start+2048,len(obs)));valid=codes[ix]>=0
    if not valid.any():continue
    block=backed[start:start+len(ix),:][valid].tocsr();assert np.isfinite(block.data).all() and (block.data>=0).all()
    ind=sparse.csr_matrix((np.ones(valid.sum()),(codes[ix][valid],np.arange(valid.sum()))),shape=(len(groups),valid.sum()))
    sums+=(ind@block).toarray()
  # Cross-check directly summed rows against streamed aggregate, for fixed genes.
  small=backed[:,:20].toarray()
  for row in range(min(12,len(groups))):
   assert np.array_equal(sums[row,:20],small[codes==row].sum(0))
  print('AGGREGATION_EQUIVALENCE_PASS',study,flush=True)
"""
assert source.count(old)==1
out=Path('outputs/replication_study_20260920')
amendment={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'change':'CSC column streaming, CSR row streaming; arithmetic and all scientific choices unchanged','reason':'Frangieh X is CSC with 740736244 nonzeros; repeated row reads reread the complete sparse payload','locked_source_sha256':hashlib.sha256(source.encode()).hexdigest(),'adapter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'validation':'first20genes first12groups exact equality to independent direct group sums; assertions run per study','stage':'before any external outcome inspection or policy run'}
(out/'io_amendment.json').write_text(json.dumps(amendment,indent=2))
namespace={'__name__':'streamed_study','__file__':str(path)};exec(compile(source.replace(old,new),str(path),'exec'),namespace);namespace['extract']()
