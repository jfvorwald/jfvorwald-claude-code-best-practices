# Standing instructions

Paste this block into the target's `CLAUDE.md` under one `## How I work` heading, with its headings demoted one level. Skip a rule only when the target gives the same instruction. The reasons and incidents are in the repository README.

## Working agreement

1. **Propose before you build.** For anything architectural, give me a short plan before code. A plan as long as the diff saves nothing.
2. **Record, do not act.** Suggestions and findings go in a durable backlog with stable IDs. Apply only the ones I pick.
3. **Say what is live, unasked.** After a change, state which files changed, whether the service restarted, and whether the check passed.
4. **Verify against the version you are running.** Check the installed binary, the actual script and the current tool list, not documentation or recall. Put any unverifiable gap in the artifact with a small smoke test.
5. **Finish the whole task and say what you skipped.** If part is blocked, do the rest in full and name what was left out and why. Scaling down is my call.
6. **Parallel work follows readiness.** Start a ticket when its prerequisites are accepted and integrated, its baseline includes them, its paths have one writer and its inputs exist. Use isolated worktrees for independent writers.
7. **Acceptance happens after integration.** A passing branch is a result, not an accepted increment. Rerun checks on the integrated commit and record it. Never close a hardware, provider or staging gate with a simulation.
8. **One writer owns every shared surface.** Boards, status, contracts, migrations, manifests, entry points and decision numbers each have one owner. Others propose in their own reports.
9. **Safety boundaries need executable tests.** A prompt states intent; a tool grant or hook controls capability. Test the allowed and the forbidden path. A hook that errors is a failed gate.
10. **Stage by default.** Deploy to protected staging. Promote the exact reviewed artifact to production only on my explicit say-so.
11. **Cap every agent session up front.** Scope freeze, two or three review rounds, one final check run, then hand back.
12. **When review repeats itself, change the design.** After two or three rounds of narrower findings in one class, ask for a class fix or a product decision. First check whether the feature traces to my words.
13. **One inbox, no mid-run questions.** Anything needing me is one item in one place: the question, lettered options with the recommended default first, and what it blocks. Chat stays short.
14. **The machine is shared.** Stop only processes you started, name scratch files by ticket, and guard disk and rate limits in long runs. Never `pkill` by pattern.

## Delegation hierarchy (dormant by default)

Applies only when I ask for an epic, a PRD or multi-ticket work, or when you are running as `cto` or one of its subagents. Otherwise ignore it and do the work directly. The roster is `cto`, `test-writer`, `implementer`, `debugger`, `code-reviewer`, `security-reviewer`, `docs-writer`. Red and green each have one owner. Refactor is its own ticket. Keep the ledger in a root file, not under `.claude/`, which agents cannot write. Do not spawn a `cto` for a task one session can finish.

## Style

No em dashes. Use hyphens.
