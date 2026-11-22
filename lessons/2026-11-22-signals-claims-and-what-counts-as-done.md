# Signals, claims, and what counts as done

**2026-11-22. Claude Code 2.1.329 installed at the time of writing, with Codex
through T3 Code as the second provider. Drawn from Rally coordinator and worker
sessions between November 2 and November 22, Taskville milestones M7 to M10
(November 2 to 10), a small pipeline that posts short marketing videos, and a
read-only review of my other repositories on November 22.**

The November 2 lessons were about writing the setup down: tiers in role files,
handoffs before the limit, verdicts tied to one commit. This stretch tested
whether the written setup held when nobody was watching. Mostly it held on
paper. The failures were in the gaps between a rule and the signal that is
supposed to trigger it.

---

## 1. A public post is a production deploy

The video pipeline had dry runs and automated quality gates, and they passed.
The first post to a public social account went out with a silent audio track:
the video had been rendered before the voice-over and music existed. The
platform's API cannot delete a post, so it came down by hand and a corrected
version replaced it. The status file admitted afterwards that nobody had
listened to the mix on a phone.

Rule 10 (stage by default) was written for web deploys. It did not occur to
anyone that a post, an email, or a message to a list has the same shape: it is
production, it is public, and unlike a deploy it often cannot be rolled back.
The planned human approval page for the pipeline had been deferred as a nice
extra.

What changed: any action that cannot be undone in public gets a person
reviewing the exact file that will be sent, not a preview of a similar one.
Automated gates are necessary and not sufficient. They check what someone
thought to check.

## 2. A standing approval covers defaults, not reserved actions

Taskville's instructions say agents never close gates. During M8 the lead
listed what was waiting on me and I replied, in effect, "accept everything".
The lead then closed two milestone gates in my name, citing that message, and
the same standing order later settled a decision that accepted a missed
performance target. The retro records the gate as closed by the owner.

The message was mine and I meant it for the backlog of defaults the lead had
just listed. I did not mean it to rewrite a rule that reserves certain actions
for me. Rule 25 says authority comes from the current message and the written
rule. It did not say what happens when the two disagree.

What changed: a broad approval covers defaults and recommended options. An
action a written rule reserves for me needs a message that names it.

## 3. Ask "whether" before "which"

A batch of Taskville decisions included "hosted staging" as one default among
several. I accepted the batch. Nineteen hours later, when the deploy asked for a
credential, I asked why we were deploying a local-first tool at all, and held
it. The staging worker is merged and undeployed, and two issues still wait on
that hold.

The staging milestone itself came from my own staging-by-default rule, applied
mechanically to a product that does not deploy anywhere.

What changed: anything that adds hosting, cost, or credentials is its own yes
or no question, never one default in a batch. Staging applies to products that
deploy.

## 4. The provider switch needs a trigger the agent can see

On November 21 I wrote a rule: use Claude until its five-hour window runs out,
then move new work to GPT without waiting for me to notice. The next night I
was watching the usage meter drop and had to ask whether we were about to
switch. The coordinator answered that it could not see that meter. I told it to
switch by hand an hour later.

The same failure shows up earlier in Taskville. The lead hit the usage limit
three times and each time sat idle until I typed "continue"; the longest stall
lasted about nineteen hours. On Rally, workers failed on rate limits while an
automatic resume woke the coordinator about forty times overnight to reply with
a single character.

A rule that names a condition the agent cannot observe is a rule for the human.
What changed: the switch is tied to a signal the agent actually receives, the
first rate-limit error from a worker or the coordinator, and the brief says so.
Where no such signal exists, the rule names me as the trigger instead of
pretending otherwise.

## 5. A finished turn is not a finished worker

About fifteen delegated Rally workers in one week came back marked complete
with text like "the full check is still running, I'll finish when it
completes". One of those reports already showed a failing test. The worker's
turn had ended; its work had not.

What changed: every brief requires a fixed final line with the result commit,
what it was merged with, and the check verdict. A hand-back without that line is
treated as still running, and the coordinator does not integrate it.

## 6. The base a tool picks by default

Rally's main checkout had sat on a feature branch since late September, about
6,000 commits behind main. The worktree tool branches new worktrees from
whatever the main checkout holds, so 146 of 149 new worktrees in this period
started from that stale commit, and every session's first job was rebasing
itself. Three never rebased and were abandoned empty.

Taskville had a smaller version: local main was 368 commits behind, and the
completion gate ran its check against that stale tree.

Rule 15 says to name the tree you are auditing. It did not cover the tree a tool
chooses for you. What changed: keep the main checkout on a current main, or pass
an explicit base to every worktree tool, and check the base before the first
edit.

## 7. Two coordinators, one handoff

Two coordinator sessions started nineteen seconds apart from the same handoff
file. Both read it, both began work, and both created their own automatic
resume tasks. A duplicate notice caught it, but only after both had acted.

Rule 17 says to hand off through files. A file can be read twice. What changed:
a takeover first writes a claim into the handoff (session and time). A second
reader that finds a fresh claim stops and reports.

## 8. Run limits leak unless the tool counts the right thing

Rule 16 says to rerun a failure once, alone. There is a run tool that counts
heavy runs. Twice in this period a worker still started a third full run, once
of a fifty-minute browser audit. The tool counted per branch, not per suite,
and it had an over-budget flag that the worker could pass to itself.

What changed: the tool counts attempts per suite and refuses the third. Only
the coordinator can override it.

## 9. Releases from trees that Git never saw

The review on November 22 found two sites running in production from source
that was never committed, and one staging release built from commits that were
never pushed. That release's manifest recorded a content hash but no commit, so
nothing could tie it back to source.

Rule 20 says to deploy from a base that holds everything live. It assumed the
base was in Git. What changed: a release records its source commit and refuses
to build from a dirty tree.

## 10. Drift in both directions, again

The October 25 lessons said to diff installed copies against the repository in
both directions. This review found both:

- The installed role files had gained a GPT model mapping and a provider order
  that the repository never received.
- The repository's role files had a hardened guard hook and stricter role text
  that were never installed. Two installed roles had no hooks at all, so their
  restrictions were prompt-only on this machine.
- A Codex copy of the setup skill had been made by find-and-replace and now
  pointed at a repository name that does not exist.

What changed: both directions were reconciled in the repository first, and the
installed copies are updated from it. The repository is the source.

## Smaller notes

- **Secrets never go in chat output.** An agent printed three short-lived
  pairing links in full and judged the risk itself because they expired in
  minutes. Transcripts are read later by other agents, as this review did.
- **A new hostname is a new origin.** A second hostname was added to a
  protected staging app with no signed-out check recorded. Re-verify access for
  every route, not just every app.
- **Prove a red test can pass.** Several Taskville red tests could never pass:
  an unescaped regular expression, exact-match text assertions, a missing
  field. Each cost a green round before anyone noticed.
- **The coordinator is the main cost.** A benchmark comparison found the lead
  used most of the cache reads, well above any worker. Keep the lead's context
  thin and measure each role before blaming the workers.
- **The review cap held on paper.** Despite "one review plus one confirm", the
  automated reviewer ran a median of 7.5 jobs per ticket over three milestones,
  and tickets that changed provider partway ran far more. Count review jobs in
  the status file.
- **Background shells have a time limit.** The Claude Code background shell
  stops a command after 30 minutes by default and 2 hours at most. A wave run,
  a cache keepalive, and a live engine I asked to watch all died that way.
  Start anything meant to outlive the turn outside the agent's shell.
- **Agents scale output, not validation.** Real-user feedback that the product
  was unusable without the users' own plugins arrived after about a hundred
  releases, and led to a change of direction. The human pilot had been NOT RUN
  for a month.

---

## What I would do differently

- For every rule with a trigger, ask who can see the trigger. If only I can,
  say so in the rule.
- Treat a public post, a message, or anything that cannot be retracted as a
  production release with a human on the exact file.
- Keep the main checkout on main, and make "done" a line in a fixed format, not
  a feeling at the end of a turn.
- Make approvals narrow by default. "Accept everything" should accept the list
  I was shown, not the rules I wrote.
