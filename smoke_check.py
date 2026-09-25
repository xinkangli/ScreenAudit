from pathlib import Path
import hashlib,json
import numpy as np
r=Path(__file__).resolve().parent/'shared/analysis_archive'
s=r/'scripts/replication_study_20260920/study.py'
assert hashlib.sha256(s.read_bytes()).hexdigest()=='1fabcf83485fc688dd84847fcf166c5fcea0a45fc70639c4095aefcb8cfb730e'
p=r/'outputs/replication_study_20260920'
tasks=json.loads((p/'tasks.json').read_text())
assert len(tasks)==15
for t in tasks:
 with np.load(p/(t['task']+'.npz')) as z:
  assert len(z['a'])==len(z['b'])==len(z['x'])==len(z['symbols'])
  assert np.isfinite(z['x']).all() and np.isfinite(z['a']).all() and np.isfinite(z['b']).all()
print('PASS: original source hash and 15 frozen candidate pools; this is not a full rerun.')
