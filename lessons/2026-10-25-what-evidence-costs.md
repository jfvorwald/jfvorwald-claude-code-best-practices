# What evidence costs

**2026-10-25. Claude Code 2.1.293 at the time of writing. Drawn from Rally's
coordinator and worker sessions between October 10 and October 25: v0.47.0 to
v0.78.0, up to three workers at once, and the same automated review panel as
the October 9 lessons.**

The October 9 lessons were about verdicts that were wrong: reviews over the
wrong range, runs over mixed code. This fortnight was about verdicts that were
right and still not worth what they cost. Twice I stopped the work to ask for
the process to be cut down. Both times the numbers said the same thing: most of
the spending was buying evidence that nobody needed.

---

## 1. Full runs are for bigger pushes

On October 19 I told the coordinator: "progress is too slow with no reward. I'd
like to see full test runs being done for bigger pushes, not individual tasks."

The audit behind that sentence:

- From October 16 to 19 there were 22 releases. Most carried one to four cards,
  and every one ran the full chain: the unit check, 112 browser suites one at a
  time (about 3 hours), and the audio harness in four runs (about 1 hour).
- The last eight full chains found one real product defect, a cross-card layout
  break at phone width.
- The rest of the failures were flakes (seven of one known WebKit timing shift,
  three load flakes) and tests made stale by another card's intended change: a
  locator, a menu order, a schema fixture.
- Each flake was A/B'd four to eight times against the base tree to prove it
  was a flake.
- On top of that, cards re-ran their own suites twice per round, ran CPU
  benchmarks and mutation checks on CSS, and took up to three review panels. One
  CSS polish card ran its narrow-layout suite about twelve times. The review
  tool ran about 130 jobs a day, and 52% of them failed.

The replacement is two tiers:

- **Task tier.** The unit check once, the task's own browser suites (at most
  three) once each, the audio harness only for engine changes and only the
  task's own groups. No A/B, no benchmarks, no full chains. Mutation checks only
  where a wrong rule is costly: engine, persistence, auth, security, legal. One
  review panel, plus one only to confirm a fix.
- **Push tier.** A full chain only for a release candidate that batches at
  least three cards, at most once a day. A failing suite is rerun once, alone.
  If it passes, it is a flake: one line in a flake ledger, and the release goes
  on. A suite that flakes in three releases gets one ticket to fix or move it.

The tiers are enforced by the run wrapper, not by the prompt. It refuses a full
chain off a candidate branch, keeps a ledger, and gives each card branch a
budget of ten heavy runs. Going over takes an explicit reason that lands in the
ledger.

After October 19 the release rate dropped from several a day to about one every
day or two, which is what the rule asked for. I adopted the same tiers in my
user-level instructions for every project, not only this one.

The release tier still earns its keep. The combined chain caught a regression
that card-level checks missed: a coordinator ruling allowed a gain step where
an effect's output was zero, and a delay effect stored the step and replayed it
a delay time later at full volume. Only the combined delay suite saw it. The
point is not to stop running the full suite. It is to run it once per batch.

## 2. Long conversations are the expensive part

On October 13 workers had grown to 400,000 to 550,000 tokens, waits were
costing repeated model turns, two heavy chains ran at once, and two cards each
got a fourth confirmation panel. I asked for five changes and then, when the
first draft made them advisory, said: "enforce the budgets mechanically, not
just advisory."

What changed:

- **Wait on notifications, not turns.** Long runs start as background jobs. The
  coordinator takes no turns while it waits. A subagent, which may not wake for
  its own notice, blocks once per ten minutes on a done marker instead of
  polling.
- **Implementation and validation are separate agents.** The implementer stops
  when its code and own suite pass and writes a handoff of at most 30 lines:
  branch, head, base, what changed, what to run, known risks, open findings. A
  fresh, cheaper validator runs the chains and the panel. A fresh fixer gets
  the handoff and the findings. Nobody resumes a 300,000-token conversation
  for a fix round.
- **One heavy run at a time.** A machine-wide lock with a first-come queue
  covers every full check and browser chain, across worktrees. Two overlapping
  unit runs had timed out a 30-second test.
- **A budget hook.** Every dispatch carries a line like
  `BUDGET: calls=60 context=200000`. A PreToolUse hook counts each subagent's
  calls and reads its context size from the transcript. At 85% it warns, past
  the limit it allows only wrap-up calls, and twenty calls later it denies
  everything.

The context limit then showed up as a planning constraint. At a 150,000-token
budget, every UI card's build worker stopped before reaching its browser
suites, screenshots and check. What worked was three fresh workers per UI card:
plan (about 55 calls), build to committed code and unit tests (about 75), and
finish with the suites, screenshots and one check (about 45). On a server card,
three build workers in a row hit the 85% warning after 38 to 53 calls, mostly
from reading one large module and the plan. Splitting it into narrow parts,
each reading only the previous worker's file-and-line handoff plus `git diff`,
fixed it. A contained side piece on its own branch finished in 21 calls.

Reading is the cost. Give each worker less to read, not more room to read it.

## 3. Decide what a guard defends before review starts

The budget hook went through the same review panel as product code, and the
panel kept finding ways around the wrap-up allowlist: a pipe, a quote inside a
comment, `git diff --output=`, a symlinked report path. Four panels in a row
found another way to steer a wrap-up call.

The loop ended with a written decision, not a fix: the budget hook is a
spending limit for cooperating workers, not an isolation boundary. A worker
acting against its dispatch is caught by the coordinator's review of its
branch, not by the hook. The hook also fails open with a message, so a bug in
it can never freeze a worker.

That is the opposite of the agent guard in this repository, which fails closed
because it is a capability boundary. Both choices are right. What was wrong was
reviewing the budget hook without saying which kind it was, which made every
creative bypass look like a High.

## 4. Route review by path, never by text

To make low-risk changes cheaper, review routing skipped security review for
comment-only and docs-only changes, and decided "comment-only" by reading the
changed lines. Five panels bypassed that heuristic: a `//` line inside a
template literal, a server write through an API wrapper whose text named no
network call, a block comment closed by a `//` line.

The rule now reads only paths and git change status:

- docs only, deletions included: no review
- tests, test tools and CSS, added or modified: bug review only
- everything else, including any deletion, rename or retype outside docs: bug
  and security review

A classifier that reads attacker-shaped text has the attacker's parser
problems. Pick an input the author cannot shape.

The same lesson came back on a path-checking tool. It parsed allowed globs out
of issue prose and lexed imports by hand, and the panel kept finding cases each
one missed. Specify machine-readable input from the start, such as one fenced
block with one glob per line, and use a real, pinned parser.

## 5. Write the rules before the code for state, access, and legal

Two cards on October 14 burned all three of their panels on design decisions
that surfaced only in review: what fails safe, when a hold or a row may be
dropped, how two writes race. A rule list is cheaper to argue about than a diff.

Now, before dispatching any card that changes what is stored or deleted, who may
read or write, or what a person agrees to, the coordinator posts a numbered
`Rules` comment on its issue. Each rule is a statement a test or reviewer can
confirm. It covers retention and removal, failure, retry and late messages,
concurrent writers, the state with the feature switched off and after a
rollback, and what is out of scope. A product choice goes to my inbox first.

A finding that no rule covers changes the rules first, then a fixer codes to
them. When the same two cards resumed with rules posted, one landed in two
panels and the other in three. Each new finding was ruled on the issue before a fresh small fixer coded it, and
a ruled class did not come back in the next panel. Write the ruling where the
reviewer reads it: the module's state table plus a one-line note at each site.

## 6. Derive the handoff, do not write it

Context resets happened every night or two. The hand-written next-session
prompts ran from 16 to 120 lines, and they went stale between being written
and being read. On October 22 I asked to make the handoff "more
programmatic".

The coordinator handoff is now a script. It derives, at the moment it runs:
repository and branch state, what merged since the last tag, whether the full
run gate allows a run today, my open decision issues, untrusted tester reports
waiting for my review, machine state, removable worktrees, and the tail of the
run ledger. Only two hand-kept files remain: stable rules, changed only when a
rule changes, and a short carry-over list for open items no command can derive,
with lines deleted as they close. A skill runs the generator at the start of a
fresh session and follows its order.

Facts a command can produce should be produced by the command, every time.
Hand-written state is a snapshot pretending to be a status.

Two related mechanics:

- **A stopped agent cannot be resumed.** When I stopped two background workers
  and then asked for them to keep running, messaging them failed. The fix was
  fresh workers told to continue from each worktree's uncommitted state, with
  the files they must keep named.
- **Do not end a turn to report.** The coordinator had been ending turns with a
  summary after each milestone, which stalled work until I prompted again. On
  October 24 I said: "keep going, don't stop periodically just check the
  decisions and notify me if everything is blocked." The coordinator now starts
  the next item in the same turn, rereads my inbox between items, and sends one
  push notification only when nothing is ready and everything left waits on me.

## 7. Smaller mechanics worth keeping

- **Run the fast check first on a candidate.** The unit check failed twice on a
  release candidate after three green browser chains. Card workers had run the
  formatter and tests per file and never the whole check.
- **A schema bump stales "future version" fixtures.** A fixture hard-coded the
  next schema number as "a newer build". When a card bumped the schema, the
  fixture silently became the current version and the harness failed 3 of 599
  scenarios. Derive future versions as `SCHEMA_VERSION + 1`, and grep the test
  tools for the old literal on every bump.
- **A decision covers only the evidence it was given.** A worker proposed
  shipping 8 to 17.6 dB of onset clipping as a veto item under a decision I had
  answered on 0.7 to 2.1 dB numbers. Refusing that and directing a time-boxed
  spike fixed it within 90 minutes.
- **The coordinator's own rulings are hypotheses.** The delay regression in
  section 1 came from a coordinator ruling, not a worker's mistake. A ruling
  about the real system needs the same real-system check as code.

## What I would keep

- full runs once per batch of several tasks, rerun a failure once, log flakes,
  never A/B to prove one
- the tiers enforced by the run tool, with a budget and a ledger
- implementation and validation in separate fresh agents, joined by a short
  file handoff
- budgets enforced by a hook, and workers sized by how much they must read
- every guard labeled as a boundary or a spending limit before it is reviewed
- review routing by path and change status, never file text
- rules on the issue before code for storage, access, and legal work
- handoffs generated from live state, with hand-kept notes only for what no
  command can derive
- the next item started in the same turn, and one notification when everything
  is blocked

The thread running through all of it: a check is worth what it would change.
A full run that cannot change the release, a fourth panel that cannot change the
design, and a 500,000-token conversation that cannot remember its own start are
all spending without a decision attached.
