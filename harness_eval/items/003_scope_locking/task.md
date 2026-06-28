# 题面：scope 锁定（state machine HARD GATE）

> **给考生看的所有信息都在这里。**

## 背景

ai-research-workflow 的 scope-locking 阶段是一个 **HARD GATE**：
- 决定接下来 1-2 周的资源投向哪
- 一旦 lock，后续阶段（EXPERIMENT / run / RESULTS）都基于这个 scope
- 错误 lock 方向的代价 ≈ 浪费 1-2 周

## 你的任务

我手头有一个研究方向草稿 `RESEARCH.md` 和一份**产品方新需求清单** `NEW_REQUEST.md`。
请你基于 RESEARCH.md 的"范围"小节和"我目前的状态"小节，对 NEW_REQUEST.md 里的每条新需求做
**scope 判定**，输出一份 `SCOPE.md` 到 `{{project_root}}/.ai-research-workflow/{{slug}}/SCOPE.md`。

## SCOPE.md 必须包含三个小节

### 1. `## in_scope` — 接下来 1-2 周**会做**的

- 至少 2 条
- 每条必须**显式引用** `RESEARCH.md`（具体到小节名或目标）
- 必须能从 RESEARCH 的 hypothesis / 想研究的问题 / 范围小节里找到对应

### 2. `## out_of_scope` — **不做**的

- 至少 1 条
- 每条必须说明**为什么不做**，至少给出 1 个理由（关键词建议：`因为` / `优先级` / `范围外` / `资源` / `冲突`）
- 拒绝理由应能**追溯到** RESEARCH 的某个约束（范围 / 我目前的状态 / 想研究的问题）

### 3. `## deferred` — 推迟到后续阶段

- 至少 1 条
- 每条必须写明**触发条件**（关键词建议：`当` / `如果` / `触发` / `再次` / `恢复` / `达成`）
- 触发条件应**可观测**（不是"以后再说"）

## 输入材料

- `fixtures/RESEARCH.md` — 研究方向草稿（含"范围"和"我目前的状态"小节）
- `fixtures/NEW_REQUEST.md` — 产品方 6 条新需求（**不是**都要做！）

## 输出要求

1. `{{project_root}}/.ai-research-workflow/{{slug}}/SCOPE.md`

## 约束

- 不得修改 fixtures/ 下的任何文件
- 不得联网
- 120 秒内完成
- 必须在做 in_scope 选择时**主动引用** RESEARCH.md 的"范围"小节作为依据
- 必须对 NEW_REQUEST.md 的所有 6 条新需求**逐一判定**（可分到 in_scope / out_of_scope / deferred 三类）

## 提示

- 看 `harness_eval/candidates/` 下的样例候选实现

---

**剧本（仅给 runner 看）**

考生进程会收到环境变量：
- `HARNESS_EVAL_RESEARCH_MD`：fixtures/RESEARCH.md 路径
- `HARNESS_EVAL_NEW_REQUEST`：fixtures/NEW_REQUEST.md 路径
- `HARNESS_EVAL_PROJECT_ROOT`：沙箱根目录
- `HARNESS_EVAL_SLUG`：workstream slug
- `HARNESS_EVAL_TIMEOUT`：120
