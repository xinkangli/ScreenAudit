# ScreenAudit

Code and frozen data for replaying numerical policies in sequential perturbation screening.

## Contents

- `shared/analysis_archive/scripts/replication_study_20260920/`: data adapters, acquisition policies, verification and statistical analysis.
- `shared/analysis_archive/outputs/`: frozen candidate arrays, task definitions, protocols, trajectories and numerical results.
- `scGPT_extension/`: representation experiment code, vocabulary, projection arrays, checkpoint metadata and results.
- `smoke_check.py`: source-hash and frozen-array checks; this is not a full experiment rerun.
- `requirements-recorded.txt`: recorded dependencies.
- `PACKAGE_SHA256.json`: current tracked-file hashes, excluding the manifest itself.

The main archive contains 15 tasks, eight policies and 30 initial-pool seeds (3,600 runs). The representation experiment contains 360 scGPT trajectories and 720 comparator replays. These are computational replays of archived measurements, not new biological replicates.

## Environment

The recorded Linux environment used Python 3.9.18, NumPy 1.26.4, pandas 2.3.2, SciPy 1.13.1, scikit-learn 1.6.1, AnnData 0.10.9, h5py 3.14.0, safetensors 0.7.0 and Matplotlib 3.9.4. The scGPT code also used PyTorch 2.6.0+cpu. See the environment JSON files. The requirements file records the original environment; it does not certify every platform.

## Replay from frozen arrays

Use a disposable working copy because analysis commands overwrite derived results. Execute these commands in order:

```bash
python smoke_check.py
cd shared/analysis_archive
python scripts/replication_study_20260920/study.py run
python scripts/replication_study_20260920/study.py analyze
python scripts/replication_study_20260920/supplement.py
python scripts/replication_study_20260920/report_assets.py
python scripts/replication_study_20260920/selection_audit.py
python scripts/replication_study_20260920/robustness.py
```

Later stages consume earlier outputs. Some analysis scripts also create diagnostic plots locally; generated images are not tracked. The run stage uses up to six processes. Do not repeat the one-time lock or follow-up append operations in the populated archive.

Frozen-array replay does not require raw h5ad files or model downloads. Rebuilding the arrays requires the original h5ad resources, feature cache and projection inputs described in the data audits and `shared/Original_Provenance.md`.

## scGPT representation experiment

Place `best_model.pt` beside `scGPT_extension/run.py`, then launch it with `shared/analysis_archive` as the working directory:

```bash
cd shared/analysis_archive
python ../../scGPT_extension/run.py
```

This overwrites derived extension records, including protocol.json; preserve an original copy. The checkpoint source is `wanglab/scGPT-human`, revision `a24c237737a40f3720f75abb555489e9fe753be6`. Expected SHA256: `6cb5d451ab5c4b33eb673adbe4fddc61d2389df1b89b7651a9fe2e557572b922`.

The experiment uses static gene-token embeddings with normalization and PCA, not full contextual transformer inference. Checkpoint weights and raw h5ad files are not included. Model and source-data terms remain those of their providers.
