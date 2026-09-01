# jfvorwald-claude-code-best-practices

How I work with Claude Code, written down so other people can borrow the parts
that transfer.

This is a running document, not a finished guide. Things get added when they
earn their place: a rule that survived contact with real work, or a failure
worth not repeating. Nothing goes in because it sounded good in a blog post.

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

The failure this prevents is subtle. Code changes and running code drift apart
constantly, and the gap is invisible until something behaves like the old
version and you spend an hour debugging the new one. Editing a config is not the
same as loading it. If a restart is needed, the change is not done until the
restart happened.

### 4. Verify against the version you are running

Not against the documentation, not against a guide, and definitely not against
model recall.

Tool names, config schemas, and flags move. A config written correctly a year
ago can be silently wrong today, and the failure mode is usually not an error,
it is a feature that quietly does nothing. Check the actual binary, run the
actual script, read the actual release notes for the version installed.

This is the single highest-yield habit on this list. See
[lessons/2026-09-01-auditing-a-multi-agent-setup.md](lessons/2026-09-01-auditing-a-multi-agent-setup.md)
for the case that made me write it down.

### 5. Finish the whole task, and say what you skipped

If part of the scope turns out to be blocked, do everything else in full and
name what was left out and why. Scaling the work down is my call, not the
model's.

The thing I do not want is a quiet 80%, delivered with the confidence of a 100%.

### 6. Style: no em dashes

Hyphens. This is a personal preference with no deeper justification, and it is
here because style rules only work if they are written down somewhere the model
will actually read.

---

## Lessons

Longer write-ups from specific sessions. These are case studies, not rules.

| Date | Lesson |
|------|--------|
| 2026-09-01 | [Auditing a multi-agent setup](lessons/2026-09-01-auditing-a-multi-agent-setup.md) |

---

## How to add an entry

A rule belongs in the working agreement if it is short, general, and I can name
the incident that produced it. If I cannot name the incident, it is a preference
and it goes in the style section or nowhere.

A lesson belongs in `lessons/` if the interesting part is the reasoning rather
than the conclusion. Date-prefix the filename. Do not rewrite old lessons when
the tooling changes; add a note at the top saying what is now stale. The point
of a dated lesson is that it was true then.
