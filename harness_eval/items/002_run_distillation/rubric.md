# Rubric：002_run_distillation

## 一、硬性通过项

- [ ] **H1**：工件 `RESULTS.md` 存在且大小 ≥ 500 字节
- [ ] **H2**：包含一个 markdown 表格，列数 ≥ 4（含 run_id）
- [ ] **H3**：表格至少包含 5 行 run 数据
- [ ] **H4**：包含 "## 结论" 或 "## Conclusions" 小节
- [ ] **H5**：结论中至少 1 条引用了 run_id
- [ ] **H6**：包含 "## 下一步" 或 "## Next Steps" 小节
- [ ] **H7**：保留失败 run（不删除失败的 run_003 行）
- [ ] **H8**：如有 CLAIMS.md，结论中至少有 1 条对齐到 claim_id

## 二、质量项

- **Q1 数据准确性**：RESULTS.md 中每个数字都能在 metrics.json 找到出处（判官抽样核验）
- **Q2 失败归因**：对失败的 run_003 不仅标注 "failed"，还解释了为什么失败
- **Q3 claim 对齐**：结论与 CLAIMS.md 的对齐不是 "支持 / 反对" 标签党，而是具体说明哪条 claim 因哪些 run 数据发生了什么变化
- **Q4 不粉饰**：没把失败的 run 偷偷隐藏或合并
- **Q5 可重现**：下一步清单里至少有 1 条可执行命令或脚本路径

## 三、典型失分点

- 只挑好的 run 写进表格，失败 run 消失
- "结论"段只写"实验效果不错"这种没引用的空话
- 把 ablation run 和 main run 混在同一个表格里没区分
- 把 metric 名称缩写后与原始 metrics.json 对不上
- "下一步" 写 "继续优化" 这种零信息量

## 四、改进建议维度

[workflow] / [eval] / [capability] 三选一，强制。
