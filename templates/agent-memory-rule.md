# Agent Memory Rule / Skill 片段

> 复制到 Cursor Rules、Claude Code / Hermes skill、或系统提示中。
> 协议全文：[`topics/ai-ml/cross-app-agent-memory.md`](../topics/ai-ml/cross-app-agent-memory.md)
> 空模板：同目录 `CONTEXT.md` / `DECISIONS.md` / `session-summary.md`

---

## Cursor Rule（建议路径：`.cursor/rules/agent-memory.mdc`）

将下列内容保存为项目规则（always apply，或按 globs 作用于整个仓库）：

```markdown
---
description: Cross-app handoff via repo-local CONTEXT.md / DECISIONS.md / sessions/
alwaysApply: true
---

# Repo working memory

Before non-trivial work in this repository:

1. Read `CONTEXT.md` and `DECISIONS.md` at the repo root if they exist.
2. Treat them as the source of truth for goal, blockers, next steps, and past decisions.
3. Do not assume you remember prior chats in other apps.

When a session produces real progress (code changes, decisions, or a clear next step):

1. Update `CONTEXT.md` (goal / progress / blockers / next / key paths / Updated date).
2. Append new decisions to `DECISIONS.md` (never rewrite old entries).
3. If the work may continue in another app, add `sessions/YYYY-MM-DD-<topic>.md`
   using the fields in `templates/session-summary.md` (or this repo's copy).
   Write a summary only — never dump the full transcript.

Skip writes for trivial one-off questions with no lasting project state.
```

---

## Hermes / Claude Code Skill（建议名：`repo-memory`）

```markdown
# Skill: repo-memory

## When to use
- Starting work in a git repo that may have been touched by Cursor, Codex, Claude, Hermes, or a web LLM
- Ending a session that changed project state or decisions

## Instructions

### Session start
1. If `CONTEXT.md` or `DECISIONS.md` exists at the repo root, read both first.
2. Align the task with Goal / Next / Constraints; mention any Blockers before coding.
3. Optionally skim the newest file under `sessions/` if present.

### Session end (only if there was real progress)
1. Rewrite or patch `CONTEXT.md` so Progress / Blockers / Next / Updated are current.
2. Append to `DECISIONS.md` for each new decision (date, decision, why, rejected, source).
3. Create `sessions/YYYY-MM-DD-<short-topic>.md` with:
   Source, Repo, Goal, Outcome, Changes, Open questions, Takeaways (1–5).
4. Do not paste full chat transcripts.

### Source label
Use one of: cursor | codex | claude | hermes | chatgpt | gemini | grok | minimax | deepseek | other
```

---

## 一句话系统提示（轻量版）

若不能装 Rule/Skill，把下面整段放进自定义指令即可：

```text
Repo memory protocol: On start, read CONTEXT.md and DECISIONS.md if present.
On end of substantive work, update CONTEXT.md; append DECISIONS.md for new decisions;
add a short sessions/YYYY-MM-DD-<topic>.md summary (no full transcript).
```
