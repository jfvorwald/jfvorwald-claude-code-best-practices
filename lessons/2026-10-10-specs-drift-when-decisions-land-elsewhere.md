# Specs drift when decisions land somewhere else

**2026-10-10. Claude Code 2.1.293 at the time of writing. Drawn from one
session that refreshed a product's architecture documents against two weeks of
accepted decisions and shipped code.**

The September lessons were about running agents. This one is about what the
agents leave behind. By October the product had 32 accepted decision records and
a working release, while its architecture documents still described the plan
from late September. Nothing was wrong enough to break a build, which is why it
lasted. The refresh took four reviewers in one session. These are the parts
that transfer.

---

## 1. Check which tree you are auditing before you audit it

The session opened on a feature branch. A branch listing showed the integration
branch 2,739 commits ahead of it, with documents the checkout did not have.
Reviewing from there would have produced a confident review of a baseline that
no longer existed.

The same thing happened twice more during the work. A feature merged into
integration while the reviewers ran, and later three new documents landed. Both
times the right move was cheap: branch a fresh worktree from the current tip,
and re-read the tip before merging back.

Before any audit, name the commit you are auditing and compare it to the
integration tip.

## 2. Decisions are written once and absorbed rarely

The architecture document cited none of the five most recent decision records.
One command found it: count each decision's citations per document. A zero in a
document that should care is a lead, not a verdict, but it was a good one.

The sharper case was a decision record that said its follow-on edits had been
applied, while the spec's own checklist still read "Pending". Of the half dozen
files it named, a single line in one had changed. The backlog still listed the
feature as deferred, and the shared hard rules said nothing about it.

When a decision names files to update, list those files in the same change as
the decision, or the decision will be true in exactly one place.

## 3. Targets and built things read the same unless you label them

Several "hard rules" described work that did not exist: a checkpoint upload
path, a backup bucket, a second socket for shared playback. Each was written as
a requirement, accurately, when it was a plan. Later the plan was deferred and
the sentence stayed.

The fix was not deleting the rules. It was a one-line banner saying what was
built and what was deferred, plus a "built" or "target" marker on each claim.
Language like "target", "proposed" and "gate" earns its place the day a number
stops being a prediction.

## 4. Review by document group, then let the reviewers apply their own findings

Four read-only reviewers each took a group of documents and returned findings as
file and line, what the document says, what is true now with evidence, a
severity (wrong, stale or gap), and a one-line edit. They also returned a list of
what they checked and found still accurate. That second list mattered: it
showed coverage, and it stopped the apply phase from touching correct text.

Then the same agents were resumed to apply their findings. They already held the
evidence, so nothing was re-derived and nothing was lost in a handoff. Three
rules made it safe:

- **Disjoint files.** Each document had one writer, the ownership rule from the
  September lessons applied to prose.
- **No commits from workers.** Four agents committing into one worktree contend
  for the index. One owner committed five logical groups afterward.
- **No invented decisions.** Where a spec was inconsistent because a product
  question was open, the agent wrote an "Open - needs decision" note with the
  options instead of picking. Seven of those came out, ready to become items in
  the person's inbox.

The coordinator's checks were mechanical: a whitespace check on the diff, a
script that resolved every relative link in the changed files, and a grep for
em dashes the person has banned.

## 5. A completion notice is not completion

One agent's last notification said it was waiting on its own background work and
had not reported. Its files were already edited, but nothing said they were
finished. Before committing, the coordinator compared file modification times to
the clock and searched the diff for each item the agent had been asked to apply.
All were present.

Judge finished work by the artifact. A notification tells you the agent stopped,
not that the job is done.

## 6. A hook reminder does not widen the task

Mid-session, an automated stop hook named three review jobs and asked for them
to be fixed. All three were about other people's pricing and legal documents.
Each was validated against the current tip first, and each had already been fixed
by the commits the review predated. The right action was no edit: a comment with
the evidence, then close. A review finding is a claim, and the task you were
given bounds what you may change in response to it.

## 7. Test a skill on a case that tempts the wrong move

The setup skill built in the same session says "never overwrite". Reading it
proved nothing. A scratch project with a conflicting agent file did. The fresh
agent kept the file, as instructed, and then reported it: that left the one
agent the boundary was meant to protect without its guard hook, and the check
still passed, because it exercised the script rather than the wiring. The skill
now lists unguarded agents before verifying and says what to do about a
same-named file.

A rule that forbids an action needs a test where the action is attractive.

---

## What to do differently

1. State the commit and the integration tip before an audit starts.
2. When a decision lists follow-on edits, put them in the same change, or in a
   checklist that the decision links.
3. Mark each claim in a spec as built, deferred or target.
4. Review in parallel by document group; apply with the same agents on disjoint
   files; commit once, in groups, from the owner.
5. Have agents record open product questions instead of answering them.
6. Verify completion from the diff, not the notification.
7. Give a skill one scenario that tempts it to break its own rule.
