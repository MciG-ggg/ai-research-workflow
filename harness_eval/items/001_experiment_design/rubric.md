# Rubric：001_experiment_design

> **这份文件只有判官能看到。**

## 一、硬性通过项

- [ ] **H1**：工件 `{{project_root}}/.omx/ai-research/{{slug}}/EXPERIMENT.md` 存在
- [ ] **H2**：文件大小 ≥ 500 字节（说明不是空壳）
- [ ] **H3**：包含 "## Hypothesis" 或 "## 假设" 小节
- [ ] **H4**：包含 "## Baselines" 或 "## 基线" 小节
- [ ] **H5**：包含 "## Metrics" 或 "## 指标" 小节
- [ ] **H6**：包含 "## Dataset" 或 "## 数据集" 小节
- [ ] **H7**：Baselines 小节中至少列出 2 个 baseline 名称
- [ ] **H8**：Metrics 小节中至少 1 个指标带方向标注（↑ / ↓ / 越大越好 / 越小越好）
- [ ] **H9**：文件正文显式引用 `RESEARCH.md`（不是泛泛的"如前所述"）
- [ ] **H10**：transcript 中存在至少 1 次对 RESEARCH.md 的读取调用

## 二、质量项

- **Q1 假设可证伪性**：Hypothesis 是 binary 可判定的（不是"研究 X 的影响"这种开放式问题）
- **Q2 Baseline 分层**：区分了"强基线 vs 弱基线"或"已复现 vs 计划复现"
- **Q3 指标严谨性**：每个指标都有方向 + 单位 + 合理范围
- **Q4 失败策略**：明确写了"什么算失败"和"什么算无效"
- **Q5 引用一致**：引用 RESEARCH.md 时用了文件名 + 段落锚点，不是空泛引用
- **Q6 报告闭环**：最终汇报说明"做了什么 / 为什么这么设计 / 下一步"

## 三、典型失分点

- "我想看看 X 怎么样" 这种不可证伪假设
- baselines 只列名字不区分已复现/计划复现
- 指标没有方向 / 单位 / 阈值
- 把 "失败策略" 写成 "如果效果不好就调参"（空洞）
- 引用 RESEARCH.md 但找不到对应原文段落（凭空捏造引用）

## 四、改进建议维度

判官输出时**每条**改进建议必须打上 [workflow] / [eval] / [capability] 之一。

## 五、评分锚点

```text
overall = 0.5 * compliance + 0.5 * execution_quality
pass = overall >= 3.5
```
