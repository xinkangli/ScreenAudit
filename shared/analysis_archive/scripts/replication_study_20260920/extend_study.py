"""Follow-up protocol on new independent studies, preserving initial null results."""
from pathlib import Path
import json,hashlib,datetime,ast
base=Path(__file__).parent;out=Path('outputs/replication_study_20260920');newout=Path('outputs/replication_extension_20260920');newout.mkdir(exist_ok=True)
protocol={'locked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'motivation':'Initial universal inflation criterion failed; Frangieh task-wide and seed-holdout winner inflation positive, Papalexi counterexample. Preserve both.','new_studies':['TianKampmann2021_CRISPRi','DixitRegev2016'],'selection_reason':'new independent studies with explicit guide IDs; no outcome scores inspected before this lock','primary_followup':'Test task-wide winner chosen on discovery A versus independent guide B, then selection using seeds0..14 and evaluation seeds15..29. Seek confirmation in at least one of two new studies while retaining initial Frangieh/Papalexi.','unchanged':'all8 policies, feature projection, program library, QC20cells/4dev/12candidates, threshold, 30seeds, budgets, score; no method tuning','new_data_adapter':'single perturbation nperts<=1; controls perturbation==control; within study all cells, lexically sorted guides per target alternate A/B; targets taken from perturbation for Tian and target for Dixit; separate NT guide sets for control','scope':'follow-up selected after first-stage results, explicitly not original confirmatory primary hypothesis','source_sha256':hashlib.sha256((base/'study.py').read_bytes()).hexdigest()}
p=newout/'extension_protocol.json'
if p.exists():raise FileExistsError('Extension already locked')
p.write_text(json.dumps(protocol,indent=2))
source=(base/'study.py').read_text();tree=ast.parse((base/'extract_streamed.py').read_text());assignments={}
for n in tree.body:
 if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ['old','new']:assignments[n.targets[0].id]=ast.literal_eval(n.value)
source=source.replace(assignments['old'],assignments['new'])
source=source.replace("  guide=obs.guide_id.astype(str).values;single=", "  guide=obs.guide_id.astype(str).values;single=")
source=source.replace("  target=np.full(len(obs),'',dtype=object);side=np.full(len(obs),'',dtype=object)","  single=single&(obs.nperts.to_numpy()<=1)\n  target=np.full(len(obs),'',dtype=object);side=np.full(len(obs),'',dtype=object)")
source=source.replace("  if study=='Frangieh':", "  if study in ['Tian','Dixit']:")
source=source.replace("condition=obs.perturbation_2.astype(str).values", "condition=np.full(len(obs),'all')",1)
source=source.replace("   target=np.where(control,'control',obs.perturbation.astype(str).values)","   target=np.where(control,'control',(obs.target if study=='Dixit' else obs.perturbation).astype(str).values)")
namespace={'__name__':'extension','__file__':str(base/'study.py')};exec(compile(source,str(base/'study.py'),'exec'),namespace)
# Extraction assertion refers to the original locked protocol; retain it unchanged.
(newout/'locked_protocol.json').write_bytes((out/'locked_protocol.json').read_bytes())
namespace['ROOT']=newout;namespace['FILES']={'Tian':'TianKampmann2021_CRISPRi','Dixit':'DixitRegev2016'}
# feature symbol mapping must retain the original annotation-only map.
originalfiles={'Frangieh':'FrangiehIzar2021_RNA','Papalexi':'PapalexiSatija2021_eccite_RNA'}
feat=namespace['features']
def fixed_features():
 saved=namespace['FILES'];namespace['FILES']=originalfiles
 try:return feat()
 finally:namespace['FILES']=saved
namespace['features']=fixed_features;namespace['extract']()
# Append new frozen tasks to the main ledger after preserving original outputs.
import shutil
initial=out/'initial_external_results';initial.mkdir(exist_ok=True)
for name in ['tasks.json','runs.csv','paired_gains.csv','study_summary.csv','comparisons.csv','report_snapshot.json','winner_summary.csv','ranking_audit.csv']:
 shutil.copy2(out/name,initial/name)
original_tasks=json.loads((out/'tasks.json').read_text());extra_tasks=json.loads((newout/'tasks.json').read_text())
for task in extra_tasks:shutil.copy2(newout/(task['task']+'.npz'),out/(task['task']+'.npz'))
(out/'tasks.json').write_text(json.dumps(original_tasks+extra_tasks,indent=2))
print('APPENDED_FROZEN_TASKS',len(extra_tasks),flush=True)
