# jfvorwald-claude-code-best-practices

How I work with Claude Code, written down so other people can borrow the parts
that transfer.

This is a running document, not a finished guide. Things get added when they
earn their place: a rule that survived contact with real work, or a failure
worth not repeating. Nothing goes in because it sounded good in a blog post.

The configuration shape was cross-checked against the installed Claude Code
2.1.283 and its current documentation on September 26, 2026. The guard's
allowed and denied paths have executable tests. Project trust and live hook
invocation still need an interactive smoke test after cloning. Tool names and
configuration fields are versioned facts, so verify again after an upgrade.

---

## The working agreement

These are the standing instructions I give Claude. Each exists because its
absence cost me something specific.

### 1. Propose before you build

For anything architectural, I want the plan before the code. Not a summary after
the fact.

The reason is not caution, it is leverage. Reviewing a proposal costs me two
minutes and redirects the whole effort. Reviewing a finished implementation
costs me twenty and usually ends in "this is fine, but it is not what I wanted."
The correction is cheapest before the work exists.

Corollary: this only works if the proposal is short enough to actually read. A
plan that is as long as the diff has not saved anyone anything.

### 2. Record, do not act

When a session generates a list of suggestions, improvements, or findings, they
go into a durable backlog file. They do not get applied.

I pick items individually. A model that finds twelve things and fixes all twelve
has made one reviewable change into twelve unreviewable ones, and I now own
eleven decisions I never made. Backlog entries need stable IDs so I can say "do
B5" and mean exactly one thing.

The backlog is also the honest record of what was found and deliberately not
done, which matters more than the list of what was fixed.

### 3. Say what is live, without being asked

After any change, state what is now running: which files changed, whether the
service was restarted, whether the check passed. Unprompted.

Code changes and running code drift apart constantly. Editing a config is not
the same as loading it. If a restart is needed, the change is not done until the
restart happened.

### 4. Verify against the version you are running

Not against documentation, a guide, or model recall.

Tool names, config schemas, and flags move. Check the installed binary, the
actual script, the current tool list, and the session that will use them.
Release notes rank below live evidence because they say what changed, not what
this combination of version, model, settings, and platform is doing now.

When something cannot be verified, put the gap in the artifact with a small
smoke test. A doubt held only in working memory is a bug with a delay on it.

### 5. Finish the whole task, and say what you skipped

If part of the scope is blocked, do everything else in full and name what was
left out and why. Scaling the work down is my call, not the model's.

The thing I do not want is a quiet 80%, delivered with the confidence of 100%.

### 6. Parallel work follows readiness

Do not start a ticket because it exists or because a worker is idle. Start it
when its prerequisites are accepted and integrated, its baseline includes them,
its paths have one writer, and its external inputs exist.

Use isolated worktrees for independent writers. Remember that filesystem
isolation does not prevent two agents from making incompatible decisions about
the same contract.

### 7. Acceptance happens after integration

A worker's passing branch is a result, not an accepted product increment. Review
it, integrate it, rerun the relevant checks on the integrated commit, and record
that exact commit.

Keep `waiting_evidence`, `waiting_decision`, and `blocked` distinct. Never use a
simulation to close a browser, provider, staging, hardware, or physical gate.

### 8. One writer owns every shared surface

Boards, cross-session status, shared contracts, migrations, root manifests,
entry points, and decision numbering each have one active owner. Workers propose
changes in their task-owned reports; the owner integrates one coherent version.

### 9. Safety boundaries need executable tests

A prompt describes intent. A tool grant or hook controls capability. If the hook
is missing, not executable, skipped for lack of trust, or reports an error, the
boundary is not active.

Test both the allowed path and the forbidden path. A hook that exits 127 and a
hook that allows everything are both failed gates.

### 10. Stage by default, promote the reviewed artifact

Deploy ordinary changes to an isolated, protected staging environment. Promote
to production only after explicit authorization, and promote the exact artifact
that was reviewed. Do not rebuild a moving checkout and call it the same release.

### Style

No em dashes. This is a personal preference with no deeper justification, and
it is written down because style rules only work when the model can find them.

---

## The agent roster

The repository contains the seven project-level subagents under
[`.claude/agents`](.claude/agents). They are intentionally narrow:

| Agent | Owns | Writes |
| --- | --- | --- |
| [`cto`](.claude/agents/cto.md) | Epic decomposition, readiness, assignment, integration, acceptance | Ledger, shared coordination surfaces, integration |
| [`test-writer`](.claude/agents/test-writer.md) | Red phase | Tests and fixtures only |
| [`implementer`](.claude/agents/implementer.md) | Green phase | Source only |
| [`debugger`](.claude/agents/debugger.md) | Root cause after unclear or repeated failure | Existing files only |
| [`code-reviewer`](.claude/agents/code-reviewer.md) | Correctness, coverage, evidence | Nothing |
| [`security-reviewer`](.claude/agents/security-reviewer.md) | Security and enforcement review | Nothing |
| [`docs-writer`](.claude/agents/docs-writer.md) | Accepted behavior in README and docs | Documentation only |

Red and green each have one owner. Refactoring is deliberately not a phase hidden
inside implementation. If it matters, give it a ticket, a failing characterization
or behavior test, and its own review.

The enforcement script is [`.claude/hooks/agent-guard.py`](.claude/hooks/agent-guard.py).
It fails closed and covers the capability distinctions that prompts alone cannot
guarantee. Do not add `memory:` to a read-only agent: current Claude Code enables
Read, Write, and Edit for subagent memory management.

### Verify the setup

```sh
./scripts/verify.sh
```

This runs the guard's allowed and denied cases, checks the agent frontmatter,
and prints the installed Claude Code version when available. Project agent
hooks also require the workspace to be trusted. After cloning, accept the trust
dialog and deliberately exercise one allowed and one denied action before
relying on a restricted agent.

Claude Code recursively discovers project agents under `.claude/agents/`. If
you copy these agents elsewhere, copy `.claude/hooks/agent-guard.py` with them
and rerun the verification from that project's root. The `${CLAUDE_PROJECT_DIR}`
paths are deliberate: they avoid a user name, home directory, or operating
system baked into the agent files.

---

## How to work with this setup

Most tasks should stay in one session. Use the roster when work has independent
phases or several ready tickets, not as ceremony around a one-file change.

### For a small change

Ask directly:

```text
Fix the rejected upload state. Read the existing tests, reproduce it, make the
smallest change, run the focused test and project check, and tell me what is live
and what you did not verify.
```

### For one test-driven ticket

```text
Use test-writer for T17, then implementer after the red-state handoff. Have
code-reviewer review the completed diff. Do not widen the ticket or apply review
nits without recording them.
```

Add `security-reviewer` when the ticket touches authentication, authorization,
user input, secrets, storage, dependencies, or external calls.

### For an epic or PRD

```text
Run this epic through cto. First show me the bounded ticket plan, prerequisites,
shared-surface owners, evidence needs, and safe parallel wave. Use one worktree
per active implementation ticket. Only the coordinator may accept integrated
work or update the shared board.
```

The coordinator should normally run no more than two to four workers, and fewer
when the board has less ready work. Workers finish with exact evidence and a
result commit. The coordinator integrates, rechecks, reviews follow-ups, and
records the accepted commit.

### For a research spike

State the claim the harness is supposed to test and the evidence it cannot
produce. Ask the reviewer to challenge whether the experiment actually tests
that claim. Keep deterministic sizes, simulated timing, browser results,
provider behavior, and physical measurements labeled separately.

### For a release

```text
Deploy the candidate to protected staging, record the release identity and
checks, and stop. Do not promote to production until I explicitly authorize
that reviewed release. Promote that artifact, not a rebuild of the checkout.
```

### Useful standing instructions

- Read immediately before writing a shared or frequently changed file.
- Record suggestions with stable IDs; do not apply them automatically.
- After two failed fixes, stop and root-cause instead of guessing again.
- Report failures and flaky runs, not only the final pass.
- Name the environment and evidence behind every operational claim.
- If an enforcement hook errors, stop the restricted agent.
- When sources disagree, state the contradiction and apply the authority rule
  for that field instead of smoothing the accounts together.
- Put arithmetic, data reduction, and safety decisions in deterministic code.
  Let the model interpret results, not invent them.
- Record source age and refresh state. A correct answer from stale input is
  still operationally wrong.
- Keep sensitive raw inputs out of Git when a minimized derived artifact is
  enough. Git history is part of the privacy boundary.
- After a deploy, verify the user's real client and cached path, not only the
  server artifact.

---

## Lessons

Longer write-ups from specific sessions. These are case studies, not rules.

| Date | Lesson |
| --- | --- |
| 2026-09-01 | [Auditing a multi-agent setup](lessons/2026-09-01-auditing-a-multi-agent-setup.md) - finding the problems |
| 2026-09-01 | [Fixing what the audit found](lessons/2026-09-01-fixing-what-the-audit-found.md) - closing them, which taught different things |
| 2026-09-26 | [Running parallel agents on a real product](lessons/2026-09-26-running-parallel-agents-on-rally.md) - what Rally taught about readiness, integration, evidence, and enforcement |
| 2026-09-26 | [What transferred across the other repositories](lessons/2026-09-26-cross-repo-lessons.md) - authority, staleness, privacy, deterministic checks, and live state |

---

## Source and version notes

The local examples are grounded in Rally's task board, task reports, worktrees,
review follow-ups, staging runbook, and agent transcripts, plus deployment,
privacy, source-authority, and instruction-routing failures from other local
repositories. Project-specific and private details stay in their source repos;
this repository keeps only the transferable workflow.

Current Claude Code behavior was cross-checked against the installed 2.1.283
binary and the official documentation for
[custom subagents](https://code.claude.com/docs/en/sub-agents) and
[hooks](https://code.claude.com/docs/en/hooks). Those pages are supporting
evidence, not a substitute for `./scripts/verify.sh` on the version being used.

## How to add an entry

A rule belongs in the working agreement if it is short, general, and I can name
the incident that produced it. If I cannot name the incident, it is a preference
and belongs in the style section or nowhere.

A lesson belongs in `lessons/` if the interesting part is the reasoning rather
than the conclusion. Date-prefix the filename. Do not rewrite old lessons when
tooling changes; add a note at the top saying what is now stale. The point of a
dated lesson is that it was true then.
