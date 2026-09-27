# Data and feature provenance

Exact input paths, file sizes, source identifiers, retained genes and processing checks are recorded in the data_audit.json, task, protocol and environment files under analysis_archive/outputs/.

- Main inputs: FrangiehIzar2021_RNA, PapalexiSatija2021_eccite_RNA and TianKampmann2021_CRISPRi, distributed through scPerturb.
- Additional screened resources: ShifrutMarson2018 and DixitRegev2016. Exclusion records are retained.
- Gene sets: cached human MSigDB Hallmark 2020 memberships. Raw response extraction requires the original hallmark_2020.gmt cache.
- Geneformer features: static input-token embeddings and a previously fitted standardization/PCA projection. Feature-cache paths are referenced by the extraction code.
- scGPT features: checkpoint identity, revision, vocabulary, coverage and projection records are in scGPT_extension/ at the repository root.

Original data and gene-set sources:

- Shifrut et al. (2018): https://doi.org/10.1016/j.cell.2018.10.024
- Dixit et al. (2016): https://doi.org/10.1016/j.cell.2016.11.038
- Liberzon et al. (2015): https://doi.org/10.1016/j.cels.2015.12.004

Raw measurements and model weights are not bundled. Preserve source identifiers and provider terms when obtaining them.
