# Agent instructions for this repository

This repository is a written-down way of working with coding agents, plus the
agent definitions and guard hook that enforce part of it. `AGENTS.md` is the
entry point for Codex and other tools that read it. Claude Code reads the same
rules through [`README.md`](README.md) and the agent files in
[`.claude/agents`](.claude/agents).

## Read first

- [README.md](README.md): the working agreement (rules 1 to 34), the roster, and
  the lesson index. Each rule names the incident behind it.
- [lessons/](lessons/): dated case studies. They were true on their date; do not
  rewrite them when tooling changes, add a note at the top instead.

## Working rules for edits here

- A rule goes in the working agreement only if it is short, general, and tied to
  a named incident. Otherwise it is a preference or it does not go in.
- Keep the README rules, the short form in
  [`standing-instructions.md`](.claude/skills/bootstrapping-my-workflow/standing-instructions.md),
  and this file in step. A rule added to one is added to all three.
- Do not name private projects, people, tokens, pairing codes, or paths outside
  the repository. Keep only the transferable workflow.
- Do not claim a configuration fact you did not check against the installed
  tool. Put unverified gaps in the text.
- No em dashes. Use hyphens.
- Run `./scripts/verify.sh` before committing. Report what it printed.

## Agent roster and model tiers

Roles are defined once in `.claude/agents/*.md` and mirrored for Codex in
`.codex/agents/*.toml`. A role's model and effort are the owner's choice, not
the session's. The GPT column is the owner's mapping for Codex and T3 launches,
not a claim that the models are equivalent.

| Role | Claude model / effort | GPT model / effort | Owns |
| --- | --- | --- | --- |
| `cto` | Opus / high | Owner's chosen main model / high | Decomposition, readiness, integration, acceptance. Top-level session only. |
| `test-writer` | Sonnet / medium | Sol / medium | Red phase, tests only |
| `implementer` | Sonnet / medium | Sol / medium | Green phase, source only |
| `debugger` | Opus / high | Astra / high | Root cause after two failed fixes |
| `code-reviewer` | Sonnet / high | Sol / high | Correctness and coverage, read-only |
| `security-reviewer` | Sonnet / high | Sol / high | Security review, read-only |
| `docs-writer` | Haiku / low | Luna / low | Docs after merge |

- The main session's model does not decide a worker's model. Do not inherit it.
- Launch workers through the tool that loads the role file (`Agent` with
  `subagent_type` in Claude Code). A dispatch path that skips role files gives
  the worker no role text, tools list, or hooks.
- In Codex or T3, set the mapped model and effort in the launch arguments. Role
  text alone configures nothing.
- Read back the model and effort that actually ran and record them. If a model
  is unavailable, report the error. Do not substitute or raise effort.
- Provider order: new work starts on Claude. On the first rate-limit error from
  a worker or the coordinator, push that worker's state and relaunch the same
  brief on GPT. Workers already on GPT finish there. New work returns to Claude
  when the window resets. Keep the handoff current so either provider can
  resume cold.
- `cto` is the top-level session, never a spawned worker. Red and green each
  have one owner. Refactor is its own ticket.

## Coordination

- A hand-back ends with one line: result commit, what it merged with, and the
  check verdict. Without that line the worker is still running (rule 30).
- Check the base before the first edit. Worktree tools branch from the main
  checkout's HEAD, so keep it on a current main or pass an explicit base
  (rule 31).
- A takeover writes its session and time into the handoff before acting. A
  second reader that finds a fresh claim stops (rule 32).
- A broad approval covers defaults, not actions a written rule reserves for the
  owner (rule 29). Hosting, cost, or credentials get their own yes or no
  question (rule 33).
- A post, email, or anything else that cannot be retracted gets a person on the
  exact file first (rule 28). Releases record their source commit and refuse a
  dirty tree (rule 20).
- Never print a secret in chat, however short-lived (rule 34).

## Checks and tests

- Task tier: the test you changed, the touched package's tests, lint, and the
  project's fast check, once. Full suites run once per push that batches at
  least three tasks. Rerun a failure once, alone; a second failure is a finding.
  The run tool counts attempts per suite; only the coordinator overrides it.
- Count review jobs per ticket in the status file.
- Report anything not run as NOT RUN.
