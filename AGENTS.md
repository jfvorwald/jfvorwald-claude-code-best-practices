# Agent instructions for this repository

This repository is a written-down way of working with coding agents, plus the
agent definitions and guard hook that enforce part of it. `AGENTS.md` is the
entry point for Codex and other tools that read it. Claude Code reads the same
rules through [`README.md`](README.md) and the agent files in
[`.claude/agents`](.claude/agents).

## Read first

- [README.md](README.md): the working agreement (rules 1 to 27), the roster, and
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
`.codex/agents/*.toml` where present. A role's model and effort are the owner's
choice, not the session's.

| Role | Model / effort (Claude) | Owns |
| --- | --- | --- |
| `cto` | Opus / high | Decomposition, readiness, integration, acceptance. Main session only. |
| `test-writer` | Sonnet / medium | Red phase, tests only |
| `implementer` | Sonnet / medium | Green phase, source only |
| `debugger` | Opus / high | Root cause after two failed fixes |
| `code-reviewer` | Sonnet / high | Correctness and coverage, read-only |
| `security-reviewer` | Sonnet / high | Security review, read-only |
| `docs-writer` | Haiku / low | Docs after merge |

- The main session's model does not decide a worker's model. Do not inherit it.
- Launch workers through the tool that loads the role file (`Agent` with
  `subagent_type` in Claude Code). A dispatch path that skips role files gives
  the worker no role text, tools list, or hooks.
- Read back the model and effort that actually ran and record them. If a model
  is unavailable, report the error. Do not substitute or raise effort.
- Never spawn a `cto` as a worker. Red and green each have one owner. Refactor
  is its own ticket.

## Checks and tests

- Task tier: the test you changed, the touched package's tests, lint, and the
  project's fast check, once. Full suites run once per push that batches at
  least three tasks. Rerun a failure once, alone; a second failure is a finding.
- Report anything not run as NOT RUN.
