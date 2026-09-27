# 数值实验代码与冻结数据

scripts/replication_study_20260920保存数据读取适配、数值策略、轨迹检查和统计分析代码。outputs/replication_study_20260920保存15个冻结候选池、3600条轨迹、CSV结果、协议与校验记录。outputs/replication_extension_20260920保存Tian/Dixit适配及排除记录。initial_external_results保留扩展前的结果。

在副本中运行，保持scripts与outputs相对位置。安装根目录记录的依赖后，依次执行：

```bash
python scripts/replication_study_20260920/study.py run
python scripts/replication_study_20260920/study.py analyze
python scripts/replication_study_20260920/supplement.py
python scripts/replication_study_20260920/report_assets.py
python scripts/replication_study_20260920/selection_audit.py
python scripts/replication_study_20260920/robustness.py
```

命令会更新派生结果，并生成本地诊断图。后续脚本依赖前序输出；图像不纳入仓库跟踪。run最多使用6个进程。不要在已有完整数据的归档中重复执行lock或extend_study.py的一次性追加流程。

每个任务NPZ包含特征x、候选genes/symbols、响应a/b/c和阈值校准数据dev_a/dev_b/dev_c。tasks.json记录任务与阈值，runs.csv是终点表，traces.jsonl记录初始选择、批次及反馈。

原始study.py源码摘要保持不变。检查包括初始池匹配、无重复选择、预算、A/B终点重算、解析留一法和未查询标签不改变预测。种子重复反映固定数据上的算法随机性，不代表新的生物学重复。

从原始测量重建需要data/scperturb_rna中的h5ad、outputs/replogle_residual_vcell/geneformer_cache中的模型及匹配表，以及outputs/agent_compute_full_20260916中的投影数组和Hallmark GMT。这些外部文件未包含在本归档中。首阶段使用extract_streamed.py，扩展适配使用extend_study.py。输入与处理记录见data_audit.json及协议文件。

environment_versions.json记录原环境。MANIFEST_SHA256.json记录当前归档文件哈希，不包含清单自身。
