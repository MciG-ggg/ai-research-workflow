# Question Capture

Use this reference when the user asks a research, design, architecture, experiment, interpretation, or workflow question instead of issuing a command.

## Activation

Question capture is opt-in. It is disabled by default.

Enable it with:

- `--qa-capture`: enable question capture for this invocation.
- `.omx/ai-research/CONFIG.md` with `qa_capture: research` or `qa_capture: all`.

Disable it with:

- `--no-feedback`: disables feedback memory, growth review, and question capture for this invocation.
- `.omx/ai-research/CONFIG.md` with `qa_capture: off`.

Config values:

```yaml
qa_capture: off | research | all
```

`research` captures research/workflow/design questions inside this skill's scope. `all` captures any durable question-like prompt in this skill's scope unless it is transient, private, or unsafe to persist.

## What Counts As A Question

Capture when the user asks for explanation, judgment, comparison, interpretation, strategy, architecture, tradeoffs, research taste, experiment design, result meaning, reproducibility, or workflow behavior.

Do not capture:

- explicit commands to implement, run, commit, push, install, or inspect
- status checks such as "done?", "continue", or "ok"
- secrets, credentials, private data, or sensitive personal material
- purely transient UI/chat coordination
- questions whose answer was not actually given

## Where To Write

Use `assets/templates/QUESTIONS.md` when creating a new ledger.

Write global or cross-workstream Q&A to:

```text
.omx/ai-research/QUESTIONS.md
```

Write workstream-specific Q&A to:

```text
.omx/ai-research/<slug>/QUESTIONS.md
```

Then route durable content to other feedback artifacts when useful:

- Concepts, methods, paper knowledge, or domain knowledge -> `LEARNINGS.md`
- Problems, blockers, failed assumptions, or recovery steps -> `ISSUES.md`
- Method, architecture, experiment, or workflow decisions -> `DECISIONS.md`
- Workstream design rationale -> `<slug>/DESIGN.md`
- Reusable process notes or commands -> `<slug>/NOTES.md`
- Capability reflection -> `SKILL_GROWTH.md` or `<slug>/REVIEW.md` when growth review is enabled

## Entry Format

Append one concise row or bullet entry containing:

- Date
- Scope: `portfolio`, `<slug>`, or `cross-workstream`
- User question, summarized if long
- Answer summary
- Evidence links: artifacts, code paths, citations, commands, or "chat-only reasoning"
- Routed updates: files also updated, or `none`
- Follow-up: next question, decision, experiment, or `none`

## Answer-first Rule

Answer the user first. Persist the Q&A immediately after answering when enabled. If capture fails, say which file could not be written and why; do not silently claim it was recorded.

## Hook Boundary

A future `UserPromptSubmit` hook may classify prompts as question-like and mark question capture as pending, but it must not write a final Q&A entry because the answer does not exist yet. The durable contract remains this file: after the assistant answers, it appends the Q&A to `QUESTIONS.md` and routes distilled knowledge to the appropriate feedback artifacts.
