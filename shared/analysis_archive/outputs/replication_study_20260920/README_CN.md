# 扰动 Agent 独立验证与评估研究

完成日期：2026-09-20。使用公开归档数据，无新湿实验。

## 结论先行

完成 3 个独立来源研究、15 个相关任务、8 种数值决策策略、30 个配对初始池，共 3600 次闭环。原先锁定的方法优越性与固定策略普遍高估假设均未通过。后续分析发现：在每次运行完成后，以发现侧成绩从 7 个策略中挑选赢家，相对随机只选 1 个策略，发现侧收益增幅大于复核侧。主阈值下三个研究的差值为 5.98、1.58、4.81 个百分点。

此结果是后续探索性评估证据，不能覆盖原主假设失败；不能证明所有 Agent 失效。Papalexi 在连续指标上方向相反，且任务级或初始池留出选择不能在所有研究中重现正向高估。完整反例保留在结果中。误差区间来自固定数据上初始池随机性，不是生物学重复的置信区间。已知模型选择偏差不是本研究首创。

## 目录

- `scripts/replication_study_20260920/`：锁定算法、稀疏矩阵读取适配、复核、后续分析。
- `outputs/replication_study_20260920/`：15 个冻结 NPZ 候选池、3600 次轨迹、CSV、图、协议与校验。
- `outputs/replication_extension_20260920/`：Tian/Dixit 后续协议、排除记录与数据审计。
- `outputs/replication_study_20260920/initial_external_results/`：扩展前首阶段结果。
- `environment_versions.json`：实际运行版本。
- `MANIFEST_SHA256.json`：包内逐文件摘要，不含自身。

## 最小复现

在新目录解压，保持脚本与 outputs 相对布局。使用 Python 3 和环境清单中的依赖。服务器已有相应环境。本包包含冻结数值池，重新运行决策与统计不需要再次读取原始 h5ad 或下载模型。

```bash
python scripts/replication_study_20260920/study.py run
python scripts/replication_study_20260920/study.py analyze
python scripts/replication_study_20260920/supplement.py
python scripts/replication_study_20260920/report_assets.py
python scripts/replication_study_20260920/selection_audit.py
python scripts/replication_study_20260920/robustness.py
```

这些命令覆盖解压目录中的派生 CSV 和图，运行前可复制一份作为对照。不要重新运行 `lock` 或 `extend_study.py`：协议文件具有防覆盖保护，现有 NPZ 已包括扩展任务。默认最多 6 个进程。全部轨迹检查、独立端点重算及源码摘要校验需通过。

## 从原始数据重建

需原项目缓存：`data/scperturb_rna/` 原始 h5ad、`outputs/replogle_residual_vcell/geneformer_cache/` 的模型/词表/匹配表，以及 `outputs/agent_compute_full_20260916/` 中的 PCA/scaler 数组和 Hallmark GMT。这些大文件不在本包内；其路径、输入形状、分组及直接求和检查见数据审计。

首阶段读取使用 `extract_streamed.py`，后续使用 `extend_study.py`。后者是原研究一次性追加脚本，不能直接在已追加数据上反复执行。科学算法 study.py 在协议锁定后保持字节一致；CSC 列分块读取修正另有 io_amendment.json 记录。协议为内部时间戳锁定，不是公开预注册。

## 科学解释限制

1. Frangieh 与 Tian 是同一研究内 guide 划分；Papalexi 是样本标签划分。独立来源研究不等于每个任务都有独立供者。
2. 使用静态 Geneformer 输入词向量的冻结 PCA 表示，未运行完整细胞 Transformer；未复现具名完整 LLM Agent。
3. 分数为原始计数伪 bulk 的相对程序抑制，不是经协变量校正的差异表达、细胞活性或疾病机制。Tian 中免疫程序只作评价压力测试。
4. 初始池留出共享候选基因与归档实验，不能称为新生物数据验证。策略仅获得查询过的 A 反馈，B/C 不作为选择输入；这是可信程序结构隔离，不是安全沙箱。
5. 每次运行后挑选赢家是有意构造的乐观汇报诊断，不是满足单策略预算的可部署方法。尝试多种策略的反馈开销不应隐藏。
6. Papalexi 的门控策略因预算 6、批次 3 和向下取整 25% 利用比例而退化为全随机；此实现保持锁定，未用测试结果调参修正。
7. 阈值、移除策略、连续指标和第三面板检查均如实报告；后续分析的局部 Holm 校正不修复整个探索过程的选择偏差。

详细数字、可写入论文的论点与不支持的论点见中文 Word 报告。
