# 题面：从 raw runs 蒸馏出 RESULTS.md

> **给你的所有信息都在这。**

## 你的任务

我跑完了一组实验，raw 数据在 `fixtures/runs/` 下面：包含 5 次实验（3 个主跑 + 2 个消融），
每次实验有 `metrics.json` 和一段 `summary.txt`。

请基于这些 raw 数据起草一份 **`RESULTS.md`**，放到 `{{project_root}}/.omx/ai-research/{{slug}}/RESULTS.md`。

这份 RESULTS.md 必须满足：

1. **结构化表格**：所有 5 次跑分结果汇总到一张 markdown 表格里（run_id / 关键指标 / 状态）。
2. **结论与证据分离**：表后写"结论"，每条结论引用具体 run_id 和指标值。
3. **保留失败**：5 次跑分里有 1 次是失败的（看 raw data 你会发现），必须显式记录，不能偷偷删掉。
4. **对齐 CLAIMS**：如果有 `fixtures/CLAIMS.md`，结论必须明确支持 / 反驳 / 下调哪条 claim。
5. **指出下一步**：结尾给"下一步动作"清单。

## 输入材料

- `fixtures/runs/run_001/metrics.json`、`fixtures/runs/run_001/summary.txt`
- `fixtures/runs/run_002/metrics.json`、`fixtures/runs/run_002/summary.txt`
- `fixtures/runs/run_003/metrics.json`、`fixtures/runs/run_003/summary.txt`（含失败 run）
- `fixtures/runs/run_004/metrics.json`（消融）
- `fixtures/runs/run_005/metrics.json`（消融）
- `fixtures/CLAIMS.md`（如有）

## 输出要求

1. `{{project_root}}/.omx/ai-research/{{slug}}/RESULTS.md`

## 约束

- 不得修改 fixtures/ 下任何文件。
- 不得联网。
- 120 秒内完成。
- RESULTS.md 中的每个数值必须能在某个 `metrics.json` 里找到出处。

---

**剧本（仅给 runner 看）**

考生进程会收到环境变量：
- `HARNESS_EVAL_TASK_PATH`
- `HARNESS_EVAL_RUNS_DIR`：fixtures/runs/ 绝对路径
- `HARNESS_EVAL_CLAIMS_MD`：fixtures/CLAIMS.md 绝对路径（可能不存在）
- `HARNESS_EVAL_PROJECT_ROOT`
- `HARNESS_EVAL_SLUG`
- `HARNESS_EVAL_TIMEOUT`
