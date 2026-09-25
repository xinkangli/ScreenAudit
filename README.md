# ScreenAudit

Paired evaluation of sequential screening under policy selection.

Associated manuscript: A paired evaluation framework for policy selection in sequential perturbation screening.
Authors: Xinkang Li, Xueyan Zhou and Xiaoxing Yin.

## Scientific scope

The framework separates a fixed policy from an A-selected winner, follows the same selected genes onto archived readout B, and records acquisition budgets, comparison costs and the unit of uncertainty. The main archive has 15 tasks, eight numerical policies and 30 matched initial pools (3,600 runs). The scGPT extension contains 360 new trajectories plus 720 comparator replays. These are archived-data numerical experiments, not new independent-donor replications.

## Files

- shared/analysis_archive: original numerical code, frozen candidate arrays, protocols, trajectories and summary data.
- scGPT_extension: checkpoint provenance, frozen projection, run script and results for the supplementary representation example.
- authoring: retained figure/document construction scripts, including the revised Fig. 1 source. Some scripts depend on the original manuscript workspace and are not standalone build commands.
- smoke_check.py: checks the packaged source hash and frozen task arrays; does not rerun the experiments.

## Recorded environment

The Linux analysis used Python 3.9.18, NumPy 1.26.4, pandas 2.3.2, SciPy 1.13.1, scikit-learn 1.6.1, AnnData 0.10.9, h5py 3.14.0, safetensors 0.7.0 and Matplotlib 3.9.4. The extension also used PyTorch 2.6.0+cpu. See the original environment files. A new cross-platform install has not been certified. Full rerun time and minimum memory are not specified.

## Replay from frozen arrays

Work in a disposable extracted copy. Existing derived outputs in that copy will be replaced.

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

Do not invoke the one-time lock or follow-up append operations on the populated archive. The frozen-array replay does not require source h5ad files or model downloads. Raw extraction requires those external files and the original feature cache; see the detailed archived README and provenance.

## Supplementary representation example

The recorded script expects outputs/replication_study_20260920 relative to its working directory and best_model.pt beside run.py. To rerun it in an extracted copy, place the published checkpoint alongside scGPT_extension/run.py and launch that script with shared/analysis_archive as working directory. The script overwrites derived extension records, including protocol.json, so preserve the original copy. The model publisher is https://huggingface.co/wanglab/scGPT-human at revision a24c237737a40f3720f75abb555489e9fe753be6. The checkpoint SHA256 is 6cb5d451ab5c4b33eb673adbe4fddc61d2389df1b89b7651a9fe2e557572b922. Full contextual transformer inference was not used.

## Version and license

This local submission package has a SHA256 manifest. A GitHub release, commit identifier and archival DOI have not been assigned by this packaging operation. Authors should choose a code license consistent with ownership and third-party terms before public distribution; none is silently assigned here. Model and source-data terms remain those of their respective providers.
