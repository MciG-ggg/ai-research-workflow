# Harness Eval — 模板题

> 复制本目录为 `items/<NNN>_<slug>/`，按下面规则填 4 个文件即可新增一道题。
> 新题不需要理解任何代码，5 分钟完成。

## 4 文件职责

| 文件 | 角色 | 必填 |
|---|---|---|
| `meta.yaml` | 题目身份（id、版本、波次、难度、考察目的） | 是 |
| `task.md` | 题面（给考生看的）+ 剧本（给执行器看的） | 是 |
| `rubric.md` | 阅卷标准（硬性通过项 / 质量项 / 典型失分点） | 是 |
| `env.yaml` | 环境前提（前置 check 命令 / 关键工件） | 是 |
| `fixtures/` | 题目输入数据（可选） | 否 |

## 关键约束

1. **`task.md` 必须包含完整任务描述**，但**绝对不能引用 `rubric.md` 的内容**。
   考生在执行时只能看到 `task.md`——避免"对着答案抄"。

2. **`rubric.md` 的每条硬性项都必须能从 transcript 或工件中找到客观证据**。
   不允许"我觉得考生应该做了"这种主观判定。

3. **`env.yaml` 的 `setup` 字段是确定性可执行命令**。
   评测引擎会自动跑这些命令确认环境就绪；任意一条失败则该题不计分。

4. **路径占位符**：题目里的所有路径用 `{{workstream_dir}}`、`{{project_root}}`
   等占位符，由 runner 在沙箱里替换。

## 模板文件

- [`meta.yaml`](meta.yaml)
- [`task.md`](task.md)
- [`rubric.md`](rubric.md)
- [`env.yaml`](env.yaml)

## 题目生命周期

```text
编写 (4 文件填好)
  -> 本地自检：runner check <item> 验证 env 跑通、rubric schema 合规
  -> 入库：items/<NNN>_<slug>/ 加入题库
  -> 跑分：runner run <item> --candidate <impl>
  -> 归因：人工 review review.md，把 [workflow] 类改进喂回 skill 迭代
```
