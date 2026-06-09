# AI Research Workflow Config

```yaml
schema_version: 1
workflow_preset: guided
idea_scouting: auto
completion_handoff: auto
worktree_closeout: report-before-merge
feedback_memory: off
qa_capture: off
growth_review: off
```

Allowed values:

- `schema_version`: `1`
- `workflow_preset`: `conservative`, `guided`, `autonomous`
- `idea_scouting`: `auto`, `off`, `on`
- `completion_handoff`: `auto`, `off`
- `worktree_closeout`: `off`, `report-before-merge`
- `feedback_memory`: `off`, `lite`, `full`
- `qa_capture`: `off`, `research`, `all`
- `growth_review`: `off`, `milestone`, `always`

Invocation flags override this file for one invocation:

- `--idea-scouting`
- `--no-idea-scouting`
- `--feedback-memory`
- `--qa-capture`
- `--growth-review`
- `--no-feedback`

Preset meaning:

- `conservative`: do only explicitly requested workflow phases.
- `guided`: infer common workflow phases from user language, but ask before final-topic, workstream creation, merge, push, or deletion.
- `autonomous`: proactively maintain relevant artifacts and next-step plans, while still respecting destructive-action confirmation boundaries.
