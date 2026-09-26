# What transferred across the other repositories

**2026-09-26. Patterns collected from a browser game, a private records repo,
a Discord bot, an agent-session viewer, and the shared staging workflow.**

Rally taught the mechanics of coordinating parallel implementation. The other
repositories supplied a different category of lesson: how an agent decides
which facts to trust, how it knows the system is current, and which boundaries
must remain deterministic even when the model is behaving well.

---

## 1. Give each kind of fact an owner

"Source of truth" is often too broad to be useful.

In one records workflow, a contemporaneous event log was authoritative for
quantities while a professional visit note was authoritative for instructions.
Neither source won globally because each failed in a different direction. In
Rally, the founder note owned intent, the playback specification owned timing,
and the storage specification owned media custody. In a browser game, the
current agent instructions identified the TypeScript application as live while
an older design document still described a historical prototype.

The reusable rule is to assign authority by field or question:

- what happened
- what somebody intended or instructed
- what the current product is
- what a contract guarantees
- what remains proposed

When two sources disagree, say so. Do not average them into a third story that
appears consistent and is supported by neither source.

## 2. Corrections should preserve the reasoning trail

Quietly rewriting an old decision makes the current document cleaner and the
history less useful.

The stronger pattern is append-only decisions with explicit supersession or
factual correction. Preserve the old reasoning that still holds, name the exact
claim that changed, and record what new evidence caused the revision. This
distinguishes "the decision was wrong" from "one sentence describing its
outcome was wrong."

That distinction matters to agents because they otherwise over-correct. When
one premise falls, a model is tempted to reverse the whole conclusion. A
durable correction says precisely how much should move.

## 3. Put arithmetic and state reduction in code

Models are useful for explaining evidence and poor choices for being the only
calculator or state store.

A private records repo paired each LLM-facing workflow with a small script that
performed date math, aggregation, threshold checks, and merge rules. Rally's
research cards did the same with deterministic fixture matrices and saved
result files. The model interpreted the outputs; it did not recreate the math
from memory in every session.

The boundary is simple:

- code computes dates, totals, limits, hashes, diffs, and pass/fail conditions
- durable files store decisions, evidence, and state transitions
- the model explains, proposes, reviews, and identifies gaps

If a number controls safety, acceptance, money, access, or scheduling, make the
calculation reproducible outside the conversation.

## 4. Staleness is a data-quality failure

Several apparently unrelated failures had the same shape.

- A manual export was accurate but old, so a check against it could still miss
  the current problem.
- A deployed browser game had the correct files on the server while an existing
  client remained on an obsolete service-worker bundle.
- An edited agent definition still ran a hook path captured from another
  machine.
- Documentation described a prototype that was no longer the active product.

The content can be valid and the answer still be wrong because freshness was
not part of the evidence.

Record timestamps, source versions, release identities, cache or refresh state,
and the path by which data arrived. A manual source should report when it was
last refreshed. A deploy is not live until the intended client loads the new
artifact. A config edit is not active until a new session or process proves it
loaded.

## 5. Privacy starts before data enters durable history

Prompts are not a privacy boundary and deletion from the current tree does not
erase Git history.

The useful patterns were structural:

- raw sensitive exports stayed ignored while minimized daily aggregates were
  committed
- personal context lived outside the code repository
- generated summaries were not treated as direct quotations from a person
- public fixtures, logs, docs, commits, and pull requests were scrubbed for
  private paths, identities, hostnames, and content
- output guards checked material leaving the process even when the prompt had
  already told the model not to leak it

Data minimization should happen at ingestion. Decide what the system needs to
retain before a model, log, commit, cache, or third-party service sees the raw
input.

## 6. Bind privilege to durable identity, not presentation

One bot had an owner-only command. A display-name fallback would have let a new
account inherit the privilege by renaming itself. The correct boundary used the
platform's immutable user ID, with the friendly name only for display.

The same rule applies to rooms, staging allowlists, deployment accounts, and
agent ownership. Names, handles, branch labels, and window titles are context.
Authorization needs an identity that the caller cannot claim by editing text.

## 7. Route instructions instead of building one giant prompt

The larger repositories worked better when a short root instruction file routed
the agent to focused guides for storage, testing, background work, frontend,
deployment, or design. Project maps and command catalogues stayed in their
owning README or build files instead of being copied into every instruction
surface.

This reduces two failures at once:

- irrelevant context does not consume every session
- one fact does not drift across several duplicated instruction files

The root file should answer "what do I read for this task?" The focused file
should answer "what rules apply here?" The source file itself should answer
"what is the current command, schema, or product fact?"

## 8. "Live" is an end-to-end statement

One bot made restart output part of every code change because edits and the
running process had drifted before. The browser game went further: server files
matched the release, but the user's existing tab remained stale until the
client update path was fixed and verified without clearing user data.

Operational completion therefore has layers:

1. source changed
2. checks passed
3. artifact built
4. service loaded that artifact
5. real client fetched and used it
6. persisted user state survived the transition

Report the deepest layer actually observed. Never use "deployed," "running,"
or "live" as synonyms when only one of them was verified.

## What I would keep

- authority assigned per field, with contradictions left visible
- append-only decisions and precise corrections
- deterministic arithmetic and state reduction
- freshness metadata on every manual or cached input
- data minimization before Git, logs, prompts, or third parties
- immutable identity for privilege
- short root instructions that route to focused guides
- live verification through the user's real path, including caches and saved
  state

The common thread is provenance. A useful agent should be able to say where a
fact came from, how current it is, what transformed it, who can change it, and
what evidence would overturn it.
