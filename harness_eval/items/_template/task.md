# 题面：<一句话标题>

> **给考生看的所有信息都在这里。**
> 阅卷标准（rubric.md）和环境检查（env.yaml）考生看不到。

## 你的任务

<用户角度的自然语言描述，可能带点模糊——这是真实场景>

## 输入材料

- `<fixture 路径 1>`：<说明>
- `<fixture 路径 2>`：<说明>

## 输出要求

你必须产出以下文件（路径相对于工作目录）：

1. `<输出文件 1>`：<说明这个文件应该包含什么>
2. `<输出文件 2>`：<说明>

## 约束

- 不得修改 `{{project_root}}` 之外的任何文件。
- 不得联网下载额外数据。
- 必须在 {{timeout_seconds}} 秒内完成。

## 你应该调用什么工具（v0 提示）

v0 阶段，"考生"是一个可执行命令。如果你不知道该用哪个，参考
本仓库 `harness_eval/candidates/` 下提供的样例候选实现。

---

**剧本（仅给 runner 看，不展示给考生）**

<!-- runner:executor -->
候选命令（`meta.yaml` 里 `default_candidate.argv`）会被 runner 在
沙箱里执行。runner 负责：

1. 把 `task.md` 完整内容通过环境变量 `HARNESS_EVAL_TASK` 传给考生
2. 把 `env.yaml` 里的环境变量注入到考生进程
3. 抓取考生所有 stdout/stderr/file-write 到 transcript.jsonl
4. 考生退出后，用 `env.yaml.outputs` 校验工件是否存在
<!-- /runner:executor -->
