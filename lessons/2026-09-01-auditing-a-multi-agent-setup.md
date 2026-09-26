# Auditing a multi-agent setup

**2026-09-01. Claude Code 2.1.252.**

> **Update, 2026-09-26:** Claude Code 2.1.283 still uses `Agent` for custom
> subagent delegation, and it now documents recursive discovery under both
> `.claude/agents/` and `~/.claude/agents/`. The exact tool roster remains
> version-specific. The repository now includes the audited agent files and
> their enforcement hook, plus an executable verification script.

I built a CEO/CTO/subagent hierarchy on top of Agent Teams plus standard
subagents, gated by a Stop hook that was supposed to block completion until the
project's check command passed. Six subagents, a hook script, a settings file.
It looked right. I had Claude review it before trusting it with real work.

It was not safe to run. Not because of one bug, but because every load-bearing
piece failed in the same way: quietly, while appearing to work.

Writing down the general lessons, because the specific bugs are already obsolete.

---

## 1. Check tool names against the binary you are running

The orchestrator agent declared `tools: Read, Grep, Glob, Bash, Edit, Write, Task`.

`Task` was the tool that spawned subagents when the config was written. It is
not any more. The current name is `Agent`, and `Task*` now refers to an
unrelated task-list API that was itself removed on newer models.

`tools:` is an allowlist. A name that matches nothing grants nothing, and
nothing warns you. So the orchestrator, whose entire job was delegating, had
silently lost the ability to delegate. It still had `Edit` and `Write`, so it
just did all the work itself, in one context, and produced output that looked
exactly like success.

**The general shape:** a renamed capability in an allowlist degrades into a
missing capability, and a competent agent will route around a missing capability
by doing the work itself. You get plausible output and a broken architecture.
Nothing in the transcript says "I could not delegate."

The fix is not "read the docs." The docs were also stale, in the same guide that
had the correct name three files away. The fix is to check the running version:
the release notes for your installed build, and the tool list the model actually
has.

## 2. A gate that fails open is worse than no gate

The hook was written to run `${CLAUDE_CHECK_CMD:-echo 'not set, edit this file'}`
and block on failure. If the variable is unset, the fallback `echo` succeeds, so
the check passes, so the hook exits 0 and approves everything.

I ran it. Exit code 0.

A gate named `loop-gate.sh` that approves everything is worse than no gate,
because no gate is a known gap and this is a false negative wearing a
reassuring filename. It had also never been registered in settings at all, so it
was not even running, but that was almost beside the point.

**The general shape:** any default that makes a safety check pass is a bug.
Unconfigured should mean *blocked*, or at minimum *loud*. Default-deny is the
whole point of a gate; a gate that defaults to allow has inverted its own
purpose while keeping its name.

And check the quiet path specifically. On success the hook printed its "not set"
warning to stdout, which on exit 0 is not surfaced anywhere. The system was
telling me it was misconfigured, into a channel nobody reads.

## 3. Run the script

I did not reason about whether the hook failed open. I ran it and read the exit
code. Thirty seconds.

The reasoning was available and I would probably have gotten there, but "I
traced the logic" and "I observed the exit code" are different classes of claim,
and only one of them is worth putting in a review. For anything with an exit
code, an HTTP status, or a return value, go get the actual value.

## 4. The prompt is not a permission boundary

Two agents were documented as read-only. Their prompts said so: "You never edit
files, only report." Both had unrestricted `Bash`.

`Bash` is a shell. `echo x > file` is an edit. So the read-only property was a
polite request made to the exact two agents whose entire value proposition is
being trustworthy about someone else's code.

**The general shape:** if a constraint matters, it belongs in the tool grant, not
in the system prompt. Prompts express intent and usually work. Tool grants
express capability and always hold. The gap between them is where an audit
finds things.

They genuinely needed `git diff`, which is what motivated the broad grant. The
answer was to scope the grant, not widen it and write a note asking for
restraint.

## 5. Enumerate the lifecycle and check every phase has an owner

The roster had six agents: an orchestrator, a test writer, a debugger, a code
reviewer, a security reviewer, a docs writer.

Nobody wrote the implementation.

The test writer was explicitly forbidden from implementing. The debugger only
engaged on an already-failing test. Both reviewers were read-only by intent. The
docs writer ran post-merge. The orchestrator's own prompt said it did not write
implementation code, one line above an instruction to delegate implementation to
a roster that could not accept it.

Six well-written agents, and the green phase of red-green-refactor had no owner.

This is easy to miss because every individual agent reads as sensible. You only
see it by listing the phases of the actual workflow and asking, for each one,
which named agent owns it. Same exercise for the top of the hierarchy: the CEO
tier was referenced by the orchestrator's prompt and defined nowhere.

## 6. Prose is not a limit

The orchestrator's prompt said "prefer 2-4 subagents running in parallel."

The enforced limits were a concurrent cap of 20 and a spawn depth of 3, neither
configured. And nothing excluded the orchestrator from its own spawnable set,
while its description advertised "coordinating multiple subagents" - exactly what
an orchestrator would match on when it decided a sub-epic needed decomposing.

A budget in a prompt is a suggestion to a system that is optimizing for
something else. If a limit matters, set the limit.

## 7. Partial fixes to a safety mechanism are the dangerous state

The most useful thing to come out of the review was the ordering.

Right now the setup is broken but inert. The broken tool name means the
orchestrator cannot spawn, which incidentally means the unbounded fan-out cannot
happen either. Two bugs cancelling, badly.

The dangerous state is the partial fix: register the hook and correct the tool
name, without also fixing the fail-open default, the missing subagent-scoped
registration, and the recursion bound. That converts an inert setup into an
expensive one that actively certifies unverified work as checked. Strictly worse
than today.

**The general shape:** when a safety mechanism has several independent defects,
they are one work item, not several. Fix them together or leave them alone.
Ordering a backlog by severity is the wrong instinct here; order it by which
intermediate states are safe to stop in.

---

## What I would keep

The parts of the setup that reviewed well were the parts that encoded judgment
rather than mechanism: the severity scheme, red-green-refactor ordering, and a
rule that an agent failing the same fix twice must stop and escalate instead of
guessing a third time. Those were good and none of them depend on the tooling
being correct.

Everything that broke was infrastructure claiming to be enforcement.
