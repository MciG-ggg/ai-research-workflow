# Rubric：003_scope_locking

> **这份文件只有判官能看到。**

## 一、硬性通过项

- [ ] **H1**：工件 `{{project_root}}/.omx/ai-research/{{slug}}/SCOPE.md` 存在
- [ ] **H2**：文件大小 ≥ 500 字节
- [ ] **H3**：包含 `in_scope` 小节
- [ ] **H4**：包含 `out_of_scope` 小节
- [ ] **H5**：包含 `deferred` 小节
- [ ] **H6**：`in_scope` 小节至少包含 2 条列表项
- [ ] **H7**：`out_of_scope` 小节至少包含 1 条列表项
- [ ] **H8**：`deferred` 小节至少包含 1 条列表项
- [ ] **H9**：正文显式引用 `RESEARCH.md`（不止一次）
- [ ] **H10**：`out_of_scope` 小节里的列表项，每条至少含 1 个拒绝理由关键词（`因为` / `优先级` / `范围外` / `资源` / `冲突` / `不在范围内`）
- [ ] **H11**：`deferred` 小节里的列表项，每条至少含 1 个触发条件关键词（`当` / `如果` / `触发` / `再次` / `恢复` / `达成` / `完成后`）

## 二、质量项（LLM judge 评 5 维）

- **Q1 faithfulness**：每条 in_scope 都能在 RESEARCH.md 找到对应 hypothesis / 目标 / 范围
- **Q2 completeness**：NEW_REQUEST.md 的 6 条新需求被**逐一判定**（不遗漏）
- **Q3 actionability**：deferred 的触发条件可观测（不是"以后再说"）
- **Q4 integration**：拒绝理由（out_of_scope）能追溯到 RESEARCH 的具体约束
- **Q5 evidence_quality**：不在场的新需求（如"加视觉"）被明确拒绝，没有偷偷纳入

## 三、典型失分点

- in_scope 写了 3 条但都引用了同一句 RESEARCH 的话（"自循环"）
- out_of_scope 写"以后再说"（这应该是 deferred）
- deferred 写"资源到位后做"（不可观测）—— 应该是"如果主实验 1 周内完成 + 显存峰值 < 18G，则启动 H3 ablation"
- 把"加视觉"放进 in_scope（违反 RESEARCH.md 明确说"明确不做的方向"）
- 没读 NEW_REQUEST.md 就开始写（transcript 里能看到）

## 四、改进建议归因维度

- `[workflow]`：scope 模板该补的强制项
- `[eval]`：本道题 task / rubric 哪里没说清楚
- `[capability]`：考生通用能力短板

## 五、评分锚点

```text
overall = 0.5 * compliance + 0.5 * execution_quality
pass = overall >= 3.5
```
