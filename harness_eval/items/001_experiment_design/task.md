# 题面：从 RESEARCH 草稿起草 EXPERIMENT

> **这是给你的所有信息。rubric 和 env 不会告诉你。**

## 你的任务

我手头有一个研究方向的早期草稿 `RESEARCH.md`（在 fixtures 里），写了点想法但很粗。
请你基于它起草一份 **`EXPERIMENT.md`**，放到 `{{project_root}}/.ai-research-workflow/{{slug}}/EXPERIMENT.md`。

这份 EXPERIMENT 必须满足：

1. **明确假设**：从 RESEARCH.md 提炼出**可证伪**的假设（不能是"我们想看看 X 怎么样"这种开放式问题）。
2. **基线列表**：至少列 2 个 baseline（1 个简单基线 + 1 个 SOTA 即可），区分"已复现"和"计划复现"。
3. **指标定义**：每个指标写清楚**方向**（越大越好还是越小越好）和**单位**。
4. **数据集**：指定具体数据集和版本/分割。
5. **失败策略**：明确"什么算失败"和"什么算无效"。

## 输入材料

- `fixtures/RESEARCH.md` — 研究方向早期草稿
- `fixtures/literature_notes.md` — 已知相关工作（你可以选择性引用）

## 输出要求

必须产出：

1. `{{project_root}}/.ai-research-workflow/{{slug}}/EXPERIMENT.md`

## 约束

- 不得修改 fixtures/ 下的任何文件。
- 不得联网下载额外数据。
- 必须在 120 秒内完成。
- 不得删除或覆盖 RESEARCH.md。
- EXPERIMENT.md 必须**显式引用** RESEARCH.md 中至少 1 个具体观点（用文件名 + 段落/行号）。

## 提示

- 路径里的 `{{project_root}}` 和 `{{slug}}` 会由 runner 在沙箱里替换成实际路径。
- 不知道该用哪个工具？看 `harness_eval/candidates/` 下的样例候选实现。

---

**剧本（仅给 runner 看）**

考生进程会收到环境变量：
- `HARNESS_EVAL_TASK_PATH`：本文件路径
- `HARNESS_EVAL_RESEARCH_MD`：fixtures/RESEARCH.md 路径
- `HARNESS_EVAL_PROJECT_ROOT`：沙箱根目录
- `HARNESS_EVAL_SLUG`：workstream slug（默认 `eval_demo_001`）
- `HARNESS_EVAL_TIMEOUT`：120

runner 会在沙箱 `runs/<timestamp>_001_experiment_design/sandbox/` 里跑考生。
考生的所有 stdout/stderr 写入 transcript.jsonl。
