# Running parallel agents on a real product

**2026-09-26. Claude Code 2.1.283. Drawn from Rally's planning, spike, product,
review, integration, and staging work.**

The first two lessons were about making a multi-agent setup structurally safe.
Rally supplied the next test: use the setup across a product with a large
specification, research spikes, shared contracts, browser behavior, private
staging, and several independent worktrees.

The important discoveries were less about prompting and more about controlling
state. Parallel work only became reliable when every meaningful state had one
owner and one durable artifact.

---

## 1. Parallelism begins at readiness, not at decomposition

A plan can expose ten tickets and still have only two that are safe to start.
On Rally, a ticket was ready only when:

- every prerequisite was accepted and integrated
- the worker's baseline commit contained those prerequisites
- the worker owned disjoint paths
- required contracts and fixtures existed
- any necessary hardware, provider access, credential, or product decision was
  actually available

"The prerequisite agent is working on it" is not a dependency state. Starting
a consumer from an older baseline merely moves the dependency failure into the
merge, where it is more expensive and harder to see.

This also changes how to think about agent utilization. An idle worker is
cheaper than invented work. When only two tickets are ready, run two workers.

## 2. One writer per shared surface

Worktrees stop two agents from overwriting the same bytes. They do not stop two
agents from assigning different meanings to the same interface.

Rally reserved these surfaces to the coordinator or a named contract owner:

- the task board and cross-session status
- shared protocol and schema files
- migration numbering
- root manifests and lockfiles
- application entry-point wiring
- architecture decision numbering

Workers owned feature directories and one task report. When a worker needed a
shared change, it proposed the interface and named affected consumers in the
report. The coordinator integrated one version and told consumers which commit
to rebase onto.

The general rule is not "never edit shared files." It is "a shared surface has
one active writer and a visible queue."

## 3. Worker completion and acceptance are different events

A worker can have passing tests and still not be done. Its result has not yet
met the other work, the integration branch, or the acceptance environment.

The reliable sequence was:

1. worker records its result commit and evidence
2. reviewer checks the complete bounded diff
3. coordinator integrates it
4. relevant checks run again on the integrated commit
5. review follow-ups land and are rechecked
6. the board records the exact accepted integration commit

Rally's product feedback wave made this concrete. Worker branches passed their
own checks, then coordinator review found interaction and integration details:
cursor behavior after a collapsed drag, stable pointer colors between screens,
stale presence data, viewer behavior, and lifecycle edges. The follow-up work
was normal integration, not evidence that the workers had failed.

"Green in the worktree" and "accepted in the product" answer different
questions. Keep both states.

## 4. Evidence needs types, not just a pass/fail label

Rally included unit tests, deterministic fixture matrices, browser walks,
screenshots, local Workers, private staging, provider configuration, and tests
that required physical audio output. They are not interchangeable.

A simulation can validate a state machine. It cannot qualify physical output
skew. A signed test token can validate claim parsing. It cannot prove the
identity provider is sending that claim in staging. A browser test can confirm
that a metronome schedules clicks. It cannot say anyone heard them through
speakers.

The task reports therefore recorded:

- exact commands and results
- environment, browser, device, fixture, and workload
- failed and flaky runs, not only the final pass
- what was simulated
- what was implemented but not deployed
- what still needed a person, provider, or physical device

That led to separate waiting states: `waiting_evidence` and
`waiting_decision`. Neither should be collapsed into "blocked," and neither can
be closed by writing a more confident sentence.

## 5. A reviewer should attack the claim as well as the code

One Rally research report said a collaboration model could not enforce an edit
precondition. Coordinator review found that the harness had dropped the
precondition before the wire. The result still made the model unattractive for
other verified reasons, but that particular conclusion was overstated.

This is the review question that caught it: "Does the experiment test the
claimed property, or only this implementation of the experiment?"

Research harnesses need the same adversarial review as product code. A passing
matrix can be internally correct and still answer a narrower question than its
report claims.

## 6. A hook error is a failed boundary

The most direct operational failure was not theoretical. The personal reviewer
and implementer agents loaded on macOS, but their PreToolUse hooks pointed to an
absolute path from another machine:

```text
/home/<old-user>/.claude/hooks/agent-guard.sh
```

That file did not exist on the machine. Claude Code logged exit 127 as a
non-blocking hook error, then the subagents continued. The prompts still said
the restrictions were enforced.

The nested `~/.claude/agents/agents/` directory was not the bug. Claude Code
2.1.283 discovers agent definitions recursively. The absolute, machine-specific
hook path was the bug, and the larger bug was trusting the declared boundary
without testing the failure path.

The version in this repository changes three things:

1. Hook paths use `${CLAUDE_PROJECT_DIR}` and live with the agent definitions.
2. The guard exits 2 on malformed input, an unknown mode, or an unrecognized
   command, so uncertainty blocks rather than warns.
3. `scripts/verify.sh` runs executable tests for allowed and denied cases.

There is one more runtime rule. Project-level agent hooks are skipped until the
workspace is trusted. If a restricted agent says its hook was skipped or
errored, stop using that agent until the boundary is live.

## 7. Exact artifacts connect review to release

The same state discipline extends past code. Staging is the default release
target. Production receives the exact artifact that was reviewed in staging,
with a recorded release identity. Rebuilding the current checkout after review
creates a different artifact and breaks the chain.

This is the release equivalent of starting a worker from the wrong baseline.
Both failures come from replacing an identity with a description like "the
latest code."

## What I would keep

- one coordinator and up to three workers when the board has ready, disjoint
  work
- isolated worktrees from named accepted commits
- stable ticket IDs and task-owned reports
- one writer for every shared surface
- worker result, integrated result, and accepted result as separate states
- exact evidence and explicit missing evidence
- review of claims, not only implementations
- executable tests for every permission boundary
- staging by default and explicit production promotion of the reviewed artifact

The reusable unit is not an impressive agent prompt. It is a workflow where
ownership, evidence, and artifact identity remain legible after every agent has
stopped.
