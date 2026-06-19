# Rubric：<一句话标题>

> **这份文件只有判官能看到，考生永远看不到。**

## 一、硬性通过项（全部达成才算 compliance >= 4）

每条都必须能在 transcript 或工件里找到客观证据。判官按 transcript
逐项核对，找不到证据 = 该项不通过。

- [ ] **H1**：<工件路径> 存在，且文件大小 > 0
- [ ] **H2**：<工件路径> 包含 <必填小节标题>
- [ ] **H3**：<工件路径> 第 N 行包含 <必填关键词>
- [ ] **H4**：transcript 中存在 tool call `<tool_name>` 且 input 非空
- [ ] **H5**：所有工件路径都在 `{{project_root}}` 范围内（不得越界）

## 二、质量项（execution_quality 评分依据）

不在于"做没做"，在于"怎么做的"。

- **Q1 主动性**：<是否在第一步就主动确认关键参数？还是被追问才补？>
- **Q2 严谨性**：<是否做了 dry-run / schema 校验？还是直接写盘？>
- **Q3 报告清晰度**：<最终汇报是否包含做了什么 / 为什么 / 下一步？>
- **Q4 错误处理**：<遇到工具失败 / 输入缺失时如何处理？>
- **Q5 一致性**：<跨多个工件之间，命名 / 单位 / 引用是否一致？>

## 三、典型失分点（用来给判官参考，但要避免"按模板套话"）

> 这些是历史跑分中真实出现的失败模式；判官应该针对**本次**的 transcript
> 来判定，而不是把这些当 checklist 打勾。

- 写了 EXPERIMENT.md 但完全没引用 RESEARCH.md 的 hypothesis（脱节）
- 用了"显然"、"一般"、"差不多"等模糊量化词
- baseline 列表不区分"已复现" vs "计划复现"
- metric 列表没有定义单位 / 方向 / 阈值
- 命令路径用了绝对路径而不是相对 {{project_root}}

## 四、改进建议归因维度（强制三选一）

每条改进建议必须打上以下三个标签之一：

- `[workflow]`：**工作流本身**该补什么 gate / rule / skill
  （例如：EXPERIMENT.md 必须显式引用 RESEARCH.md 的 hypothesis）
- `[eval]`：**本道题本身**有什么问题
  （例如：rubric 写得太模糊 / task.md 没说清楚单位）
- `[capability]`：**考生暴露的通用能力短板**
  （例如：长上下文下工具调用容易漏 / 不擅长校验 schema）

## 四.b、v1 LLM judge 自动评 5 维（rubric 不写，LLM judge 自动覆盖）

`judge_llm.py` 会按 5 个固定维度评分（每维 0-5），不需要在 rubric 写：

- **faithfulness**（忠实于源材料 — 不凭空捏造引用、数字、结论）
- **completeness**（覆盖完整度 — 是否回应 task.md 的每条要求）
- **actionability**（可执行性 — 描述/范围/触发条件可操作，不是空洞口号）
- **integration**（集成一致性 — 与上下游 artifact 的引用、单位、命名、claim_id 保持一致）
- **evidence_quality**（证据链质量 — 失败有归因、结论有 run_id / claim_id 锚点、不粉饰）

## 五、评分锚点

```text
overall = 0.5 * compliance + 0.5 * execution_quality
  5 = 所有硬性项达成 + 质量项全部主动/严谨
  4 = 所有硬性项达成 + 质量项大多主动
  3 = 硬性项达成 80% + 质量项混合
  2 = 硬性项达成 < 80% + 质量项偏被动
  1 = 硬性项多半失败 + 质量问题严重

pass = overall >= 3.5 （meta.yaml.scoring.pass_threshold 可覆盖）
```
