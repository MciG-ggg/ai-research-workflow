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

For deterministic capture, call:

```bash
python3 scripts/capture_question.py <project-root> --question "..." --answer-summary "..." --workstream <slug>
```

`capture_question.py` creates the appropriate `QUESTIONS.md` from `assets/templates/QUESTIONS.md` when needed, appends the Q&A ledger entry, and refuses likely secret/credential text unless explicitly overridden. It is a post-answer capture helper, not an experiment runner or docs publisher.

## Answer-first Rule

Answer the user first. Persist the Q&A immediately after answering when enabled. If capture fails, say which file could not be written and why; do not silently claim it was recorded.

## Hook Boundary

A `UserPromptSubmit` hook may classify prompts as question-like and mark question capture as pending, but it must not write a final Q&A entry because the answer does not exist yet. The durable contract remains this file: after the assistant answers, it appends the Q&A to `QUESTIONS.md` and routes distilled knowledge to the appropriate feedback artifacts. Hooks may call `capture_question.py` only after an answer summary exists and only when `qa_capture` resolves to `research` or `all`.

## Hook Integration Helper

Use `scripts/question_capture_hook.py` when a hook system needs deterministic two-stage capture:

```bash
python3 scripts/question_capture_hook.py --stage submit --project-root <project-root> --prompt "为什么这个结果有价值？"
python3 scripts/question_capture_hook.py --stage answer --project-root <project-root> --answer-summary "The result constrains the claim boundary." --workstream <slug>
```

Submit stage behavior:

- reads the prompt from `--prompt`, `--prompt-file`, supported hook environment variables, or stdin
- parses `.omx/ai-research/CONFIG.md`
- checks whether `qa_capture: research | all` enables capture for the inferred scope
- refuses likely secret/credential text
- writes only pending state to `.omx/state/ai-research-question-capture-pending.json` unless `--no-pending-write` is used
- never writes the final Q&A ledger because the answer does not exist yet

Answer stage behavior:

- requires `--answer-summary` or `--answer-file`
- uses the pending prompt unless `--prompt` is supplied again
- appends to `.omx/ai-research/QUESTIONS.md` or `.omx/ai-research/<slug>/QUESTIONS.md`
- removes the pending marker after successful capture unless `--keep-pending` is used

`assets/hooks/question-capture.example.json` shows example hook wiring. Adapt paths to the local Codex/OMX hook runner; the skill does not install global hooks automatically.
