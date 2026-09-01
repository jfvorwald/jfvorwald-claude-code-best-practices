# Fixing what the audit found

**2026-09-01. Claude Code 2.1.252. Companion to
[auditing a multi-agent setup](2026-09-01-auditing-a-multi-agent-setup.md).**

The audit found nineteen problems in my agent hierarchy. This is what I learned
closing them, which turned out to be a different set of lessons than finding
them.

---

## 1. A gate that fails closed globally is a gate nobody can deploy

The audit's headline finding was that my completion gate failed open: unset
check command, fallback succeeds, everything passes. Obvious fix, make it fail
closed.

Except the hook is registered in my *global* config, so it fires in every
project on the machine. A gate that blocks whenever no check is configured would
have blocked every turn in every directory I have never set up. That is not a
safe default, it is an unusable one, and I would have deleted the hook within a
day. Which is how safety mechanisms actually die: not disabled on purpose, but
made annoying enough that disabling them is the reasonable move.

What worked was making the gate **opt-in by file presence**. A project either
provides a check script or it does not:

- no check script: no gate, exit 0, silent
- present but not executable: block loudly, because that is a half-configuration
- present and passing: exit 0
- present and failing: block, and feed the failure back

The distinction that matters: the original bug was a *configured* gate that
silently passed. Absence-means-unconfigured is a different thing from
configured-but-broken, as long as the two states cannot be confused for each
other. Half-configured has to be loud, because that is the state where someone
thinks they are protected.

**General shape:** "fail closed" is correct advice for a check with a known
scope. For anything that runs everywhere by default, the real question is what
happens in the majority of contexts that never asked for it, and the answer has
to be "nothing", or the mechanism gets removed.

## 2. Order the backlog by which intermediate states are safe

The audit said this and I believed it. Executing it is what made it concrete.

Two of the defects were cancelling each other. A broken tool name meant the
orchestrator could not spawn anything, which incidentally meant an unbounded
fan-out could not happen either. Fixing the tool name alone would have converted
a dead feature into an expensive one.

So the fix order was not by severity. It was: structure first, then delegation
*together with* the fan-out bound, then the gate as one indivisible unit of four
defects. Any partial landing of that last group produces a system that certifies
unverified work as checked, which is strictly worse than the inert broken thing
I started with.

When several defects share a mechanism, they are one work item. Sequencing by
severity will happily walk you through an intermediate state that is worse than
where you started.

## 3. When you cannot verify something, put the gap in the artifact

Two changes needed a parameterized tool-grant syntax. One form I verified
against a first-party plugin installed on the machine. The other form I could
not: it is documented, the same field accepts other parameterized tools, no
installed example uses it.

The tempting move is to ship it and say nothing, because it will probably work.
The failure mode if it does not is the interesting part: either the agent
visibly loses access (fine, you find out immediately) or the parameter is
ignored and the agent silently keeps full access, meaning the fix I just claimed
to have made did not happen.

So it went into the backlog as a named caveat with a two-command smoke test.
Not into my head, and not into a sentence in a chat log that scrolls away.

**General shape:** a known-unknown recorded in the artifact is engineering. The
same known-unknown held only in working memory is a bug with a delay on it. This
is the same discipline as `# TODO: unverified` in code, applied to config.

## 4. Release notes tell you what changed, not what is true right now

Mid-remediation I wrote a factual claim into a config file: a particular tool
family was unavailable on current models. I had a real release note saying
exactly that, from the correct version, which I had read carefully.

Then those tools showed up in my session an hour later.

The release note was accurate about a change. It was not a statement about what
my session actually had, which depends on model, version, settings, and things I
was not tracking. I corrected the file, and the underlying decision survived
because it turned out to rest on a better reason anyway (a plain file survives
compaction, model switches, and the end of a session).

Two things worth keeping. First, changelog evidence is weaker than live
evidence, even when the changelog is right. Second, when a decision's stated
justification collapses, check whether the decision itself was right for another
reason before reversing it. Often the conclusion is fine and only the argument
was wrong.

## 5. Read immediately before you write, not merely at some point

My edit to a settings file was rejected because the file had changed since I
read it. It had: a model setting had moved and changed value, from an unrelated
action elsewhere.

Had the write gone through against my stale copy, it would have silently
reverted someone else's change. The read-before-write check is not bureaucracy,
it is the only thing standing between a config edit and a lost update. Every
merge I made after that read the current file first and preserved what it found.

## 6. Test the branch you would never reach by hand

The gate has five paths. Four are easy to reason about. The fifth is "the check
is failing AND the harness has already forced a continue once", where the
correct behavior is to give up and let the turn end, because otherwise you burn
eight full turns and get overridden anyway.

That branch never occurs while poking at something manually. It only happens
deep in a loop you did not want. I synthesized the payload and piped it in, and
it is the single test I would keep if I could keep only one, because it is the
one protecting against an expensive failure I would not otherwise see until it
happened for real.

**General shape:** for anything with a stdin contract, you can fabricate every
input state in a shell one-liner. The branches worth testing are the ones you
cannot trigger by using the thing normally.

## 7. Close a nit by recording the decision, not by doing nothing

Several findings were judgment calls rather than defects: a model choice, a
deliberately narrow tool grant, an enforcement approach superseded by a simpler
fix.

The instinct is to leave them open because there is nothing to change. That is
how a backlog rots: the next reader cannot tell "considered and kept" from "not
looked at yet", so they re-litigate everything.

They got a "decisions recorded" section instead, each with the reasoning. Where
the reasoning belonged in the system rather than the backlog, it went into the
file itself. The debugger agent can edit files but not create them, which looks
like an oversight until the agent's own prompt says the constraint is deliberate
and explains why.

---

## What actually took the time

Not writing the fixes. Deciding what "fixed" meant for a mechanism that runs
everywhere, and working out which repairs were safe to land separately. The
editing was maybe a fifth of it.
