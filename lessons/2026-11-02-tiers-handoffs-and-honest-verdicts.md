# Tiers, handoffs, and honest verdicts

**2026-11-02. Claude Code 2.1.316 installed at the time of writing, plus a second provider
(Codex through T3 Code) for part of the period. Drawn from Taskville sessions
between October 30 and November 2: milestones M3 to M6, two to four workers at
once, the same automated branch review panel as before, and one main-session
handoff from Claude to GPT and back.**

Earlier lessons were about review that did not converge and evidence that cost
too much. This stretch added a different pressure: the quota ran out, so the
work had to survive a change of lead, and the question became whether the
setup I had written down was the setup that actually ran.

---

## 1. Model and effort tiers are a decision, so write them where the launcher reads them

Claude kept hitting its usage limit, and I asked whether subagents were running
on lower models than I had chosen, and to fix the agent files if not.

What the check found:

- The role files already named a tier: Sonnet at medium effort for tests and
  implementation, Sonnet at high for reviews, Opus at high for debugging, Haiku
  at low for docs, Opus at high for the coordinator.
- The launch records did not match the files. In the benchmark record, most
  Claude implementer and test-writer launches show effort `high`, not the
  `medium` the file says, and some rows have a blank model or an odd label
  (`high-definition`) in the effort field. I have not established why: some of
  it may be how the benchmark labeled its baseline. That is the point. The
  record, not the definition, is what shows what ran, and mine was not clean
  enough to answer "what did each worker use" with confidence. The role files
  themselves already pointed workers at Sonnet and Haiku, not at the
  coordinator's model, so the lower-model suspicion was not the cause I could
  confirm.
- Work dispatched through T3's `delegate_task` loaded none of the role files
  at all. Those children had no role text, no tools list, and no hooks. The
  first M4 workers ran that way until I noticed and asked.
- A role file's prose does not configure a runtime. Only launch arguments do.

What changed:

- Every role file carries `model:` and `effort:` in its frontmatter, and the
  coordinator's file carries the same table as a policy section.
- Selecting a model for the main session does not select it for the children.
  Only an explicit instruction to override every worker does that.
- The coordinator reads the returned model and effort after each launch and
  records them. A mismatch or an unavailable model is reported with the exact
  error. It is never quietly replaced and effort is never raised.
- Native Claude workers go through the `Agent` tool with the role's
  `subagent_type`, with `isolation: "worktree"` for separate checkouts. Then
  the role's hooks are active, and I check one (the test-protection hook) by
  trying an action it must refuse.
- Changing a tier is the owner's decision. The coordinator asks first.

The generalizable part: inheritance is the default failure. A lead on the
biggest model with a worker told "do the thing" will spend the biggest model on
every ticket, and the bill arrives as a limit that ends the session mid-wave.

## 2. A limit cutoff is a handoff, so build the handoff before the limit

The first M2 lead hit its usage limit with one ticket committed but unreported,
one assigned but not started, one correction unpushed, and the status file
seventeen merges behind. Only live GitHub, refs, and worktrees could reconcile
it.

Later, when I moved the main session between providers on purpose, the same
discipline made it painless:

- The outgoing lead wrote one handoff file: authorization, what is open,
  exact head SHAs, which checkout holds what, what is blocked and why, and what
  not to touch (a demo I had running, untracked files that were mine).
- It said which facts were verified at handoff and which were not: CI on one
  commit was green, CI on the next had not been checked, and the note said so.
- Historical records stayed historical. GPT launches were never relabeled as
  Claude ones in the benchmark file, and a failed review job stayed FAIL even
  after a decision made its finding moot.
- Each worker pushed a checkpoint before stopping, so an interruption left
  branches, not local state.

Set a stop time in every brief, read the live usage before assigning, and have
workers push before they hand back.

## 3. Review rounds do not end on their own, so end them with pins

A branch panel found new valid issues on seven consecutive rounds for one
ticket, and the next two tickets behaved the same. Every finding was real. The
process still did not converge, because the reviewer finds the next layer once
the previous one is fixed.

Rules that came out of it:

- One review and one confirming round. Past that, defer non-critical findings to
  follow-up tickets that start with a failing test, so the finding is a
  contract and not a note.
- After two failed fix rounds on the same bug, hand it to the debugger. A timing
  bug that survived two implementer rounds was solved in one debugger round by
  replacing two code paths with one deadline.
- An implementer cannot write tests under the test-protection hook, so every
  review fix it makes lands untested. Budget a test-writer pin round after any
  green phase that fixed findings, and list untested fix commits in the report.
  Several of those pins found real bugs.
- An implementer who disagrees with the architecture document does not answer
  the reviewer with a rebuttal. A rebuttal that contradicts the document's
  literal text came back as a high finding. Disputes with the document go to
  the coordinator.
- Run the branch panel on each step of a merge chain. Ticket-level review passed
  work that the chain-level panel then found 15 medium findings in, because the
  bugs lived in how tickets met.

## 4. A verdict belongs to one commit and one scope

- An approval, a green CI run, and a review job each name a commit. A later
  commit gets a fresh claim or no claim. One handoff said so in plain words:
  CI is verified on the tested head, the newer head only changes the report,
  and "do not claim CI on the newer one until verified."
- A decision from the owner changes scope, not source. When I accepted that a
  feature would only work for producers that supply a task ID, the ticket went
  back to review, but the earlier failed panel stayed failed until a
  confirming run, and the report said "scope approval only."
- Record the producer-to-domain relationship before claiming acceptance. A UI
  that works on a synthetic fixture can be unavailable for the real source, and
  an unknown relationship stays unknown rather than being guessed from time or
  order.
- A fake adapter can hide what the shipped default does. A test that injects a
  fake `execFile` never exercised "wait for exit" versus "return at launch."
  Pin the real adapter against a harmless real program.
- A decision deferred "until milestone N" needs a line at the top of milestone
  N's security review. One latent path became live when a later ticket gave
  browser sessions a command scope, and no ticket-level review flagged it.

## 5. An old claim about my permissions is not my permission

Two sessions made opposite calls about merging. One assistant wrote down that I
had a standing order to merge with the admin bypass. A later session, working
under my current instruction to record enforced restrictions and continue,
treated the same ruleset as a blocker, held ten ready PRs, and logged a lesson
saying the older claim does not override me.

Both were real moments, and they cannot both be the rule. What I now require:

- Merge authority is checked against my latest message and the project's
  written rule, not against a memory note or a previous session's lesson.
- When the permission classifier blocks `gh pr merge --admin`, that is a prompt
  to check whether I authorized it, not a hurdle to route around. Earlier
  merges stalled for about three hours before I gave an explicit order.
- If the project refuses a normal merge, the coordinator records the refusal
  on the issue, leaves the PR ready and unwatched, and keeps working on
  independent tickets. It never alters protections.

## 6. The machine and the tools are not neutral

- Browser suites that pass alone fail in bulk when several workers run at once.
  One wave had ten failures in eight files, every one green alone. A load
  average of 61 produced the same pattern earlier. Run the wave suite when
  workers are idle, rerun a timeout once alone, and give a third timeout of the
  same test a fix-or-quarantine ticket.
- The orchestrator itself can perturb tests. T3 Code probed every new local
  listening port with a GET about every three seconds, and a stand-in server
  counted those as client requests. Count only the client under test.
- A live end-to-end test through the real `claude` binary in a new folder writes
  a trust entry to `~/.claude.json`. That is a user-config change. Build a
  replay test first, and treat the live one as a decision.
- `brew upgrade` of Claude Code deletes the binary path that already-spawned
  teammates relaunch from. Four workers died with status 127 while the spawn
  call reported success. Restart the lead with `claude --continue` after an
  upgrade and check the panes after every spawn.
- Worker handoffs over about 16,000 characters were truncated in delivery.
  Cap handoff length in the brief, and ask for a short resend when one arrives
  cut off.
- A reviewer under a read-only guard cannot run the tests. The lead runs the
  checks and puts the results in the review brief.
- Pin dependencies older than the package manager's release-age window instead
  of adding an exclusion to get CI green.
- Formatters rewrite escape sequences. Biome turned `\u` escapes for invisible
  characters into the characters themselves, which then broke the next edit.
  Format, restore the escapes, check, then commit.
- Text meant to be pasted into a shell is an execution surface. A copied working
  directory containing `;` ran a second command. Single-quote every value.

---

## What I would do differently

- Write the tier table on day one, verify the first launch's returned model and
  effort, and keep verifying: the first dispatch path I used silently skipped
  the files I had written.
- Treat the review budget as part of the ticket: one review, one confirm, one
  pin round, then follow-ups.
- Make every handoff say what was verified, on which commit, and what was not.
