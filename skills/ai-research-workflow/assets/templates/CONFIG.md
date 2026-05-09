# AI Research Workflow Config

```yaml
feedback_memory: off
qa_capture: off
growth_review: off
```

Allowed values:

- `feedback_memory`: `off`, `lite`, `full`
- `qa_capture`: `off`, `research`, `all`
- `growth_review`: `off`, `milestone`, `always`

Invocation flags override this file for one invocation:

- `--feedback-memory`
- `--qa-capture`
- `--growth-review`
- `--no-feedback`
