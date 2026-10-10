# The machine and the person are shared surfaces

**2026-10-09. Claude Code 2.1.293 at the time of writing. Drawn from the same
two weeks of Rally coordination, plus one earlier note from the first
end-to-end run of the agent roster.**

The September lessons said every shared surface needs one owner: the board,
contracts, manifests, migrations, decision numbering. Two surfaces were missing
from that list. The machine every agent runs on is shared, and so is the person
they all report to. Both failed in ways that worktrees and ownership tables do
not prevent.

---

## 1. The machine is a shared surface

Worktrees isolate files. They do not isolate processes, disk, CPU, scratch
directories, or API quotas.

- **Processes.** A worker stopped its dev server with `pkill -f` on the dev
  command. The pattern matched every worktree's server, so it also stopped the
  coordinator's and another worker's. Stop only what you started: the recorded
  PID or task handle, or listeners on your own assigned ports. Killing a
  recorded process tree can still leave child servers listening, reparented
  away from the tree. Check your ports afterwards, and kill a listener only if
  its command line shows your own worktree.
- **Scratch space.** Every agent in a team session gets the same scratchpad and
  task-output directory. Two workers logged to the same `dev.log` and
  overwrote each other's evidence. Prefix scratch files with the ticket ID and
  keep your own list of background task IDs.
- **Ports.** Each worker gets a named port set, and the coordinator keeps its
  own.
- **Disk.** One reproduction script imported a 173 MB file over and over
  against a local storage emulator that never deletes uploaded bytes. The
  worktree's emulator state reached 86 GB and filled the disk. Then every shell
  call from every session failed, because the tool could not write its own
  output file, so no agent could clean up. Any repeated import or export now
  wipes its local state between batches and stops below 30 GB free. When the
  shell is dead, file reads may still work, and the agent can send the person
  the exact cleanup commands.
- **API quotas.** Moving 18 issues on a GitHub Project, by listing every
  project item once per issue, exhausted the GraphQL budget. That budget is per
  user and shared by every session on the machine. Every GraphQL call was
  refused while the REST `rate_limit` endpoint reported thousands of calls
  remaining, and the block outlasted the hourly reset. Look items up through
  the issue instead of listing the project, use REST for issues and pull
  requests, and never retry a secondary limit in a loop.
- **CPU.** With up to three workers and a coordinator, machine load decides
  whether a long run is evidence. The companion lesson,
  [When review stops converging](2026-10-09-when-review-stops-converging.md),
  covers how that played out.

Each item is the same failure: an agent acting correctly inside its worktree
and wrongly on the machine.

## 2. Messages between agents arrive late

Three mechanics cost the most time.

- **Messages cross.** A message is read only at the receiver's next tool round.
  Workers regularly handed off "done" before reading the coordinator's latest
  findings, or committed a fix the coordinator had just said it would make.
  Before resending or fixing, check the worker's branch for the commits the
  message asked for. Batch a round's findings into one message.
- **An idle agent may not wake for its own background job.** A worker started a
  measurement in the background and ended its turn. The job finished at 15:40.
  The completion notice reached the worker at 18:41, after the coordinator sent
  a status check, so the card stalled for three hours. For anything that runs
  for minutes, run it in the foreground with a long timeout, or start it in the
  background and block in the same turn on a foreground wait. End a turn only
  when waiting on a person or another agent.
- **A background subagent cannot wait for approval.** A worker told to "stop
  and wait for approval" cannot block on a message. It ends its turn, and its
  plan arrives as a hand-back. The coordinator approves by messaging the
  worker's agent ID, which resumes it with its context intact. Write "stop and
  send me the plan; I will resume you", not "wait". A completion notice from a
  worker that just handed back a plan is not a finished ticket.

## 3. The person needs one inbox

One night I told the coordinator to keep going while I slept, because I wanted
to wake up to real, verified progress. Later, mid-wave, after several updates
that ended in "Waiting for you" lists, I said "stop asking and keep going", then
"do not ask me again."

The coordinator complied by parking decisions in the status file. That list
grew to 74 items, mostly veto notes, buried under current work. A decision page
published separately was never answered and went stale. I asked "what do I
need to decide on, I am not finding it", then "we need a better way for me to
see what's waiting for me."

What replaced both:

- one GitHub issue per decision, with a dedicated label, filed from a template
- one plain-language question, lettered options with the recommended default
  first, what it blocks, and links to anything to review
- vetoes for defaults already built, batched into one issue per release with a
  7-day window, after which they count as accepted
- chat kept short: what landed, what is running, nothing else

Two mechanics made the inbox reliable:

- I answer by commenting and closing in one action, so a query for open issues
  misses fresh answers. Several answers I gave mid-session went unapplied until
  the handoff. The coordinator now reads recently closed issues too, and checks
  again during long sessions.
- Every agent's `gh` posts as my account, so the account alone does not prove I
  wrote a comment. A bare "sounds good to me, proceed" on one issue could not be
  told apart from an agent's comment, and the auto-mode classifier refused to
  record it as approval of ten decisions. Short or ambiguous answers get
  confirmed. A detailed answer in my voice to the specific question is fine.
  This is the September identity lesson again: bind authority to something the
  caller cannot claim by writing text.

Authorization also has scope. Permission to push and deploy given for one night
applied to that night. A standing "unless I ask to stop, keep going" applied to
that session, not to the next one.

## 4. The person's context lives outside the repository

I asked for "an updated UX as we discussed last night". The discussion was not
in the repository, on the board, or in any local session. It was a design
canvas I had made in claude.ai. Before saying something cannot be found, an
agent should search every surface the person works in, including their
published artifacts.

The reverse failure is worse. A research card recommended reading the founder
note's "proprietary LLM" as "any AI model, no proprietary training", and the
coordinator wrote "no proprietary model training is proposed" into the
architecture document. I said: "remember we're training an LLM." An agent's
reinterpretation of the owner's intent is a proposal, not a specification
change. The founder note owned intent, and the architecture document did not
get to narrow it.

## 5. Credentials and approvals stay with the person

The repository's SSH key is passphrase-protected and the SSH agent held no
identity, so batch pushes failed. The auto-mode classifier refused to load the
key from the keychain because that is credential access, which is correct. The
working pattern was to hand me the exact command to run with `!` in the prompt,
then push. Agents should not route around a credential refusal.

The classifier also refused to let the coordinator add its own permission
allow rules. Approval prompts can therefore still reach the person during an
autonomous run, and simple, single-purpose commands draw fewer of them than
long compound pipelines.

## 6. A migration ends the rollback window

Once a staging room loads a newer arrangement schema, deploying the previous
release over it is unsafe. Each release that bumped the schema therefore became
an explicit decision for me, and its record names the release staging can no
longer roll back below. Deploy guards check history; they cannot know that
persisted state moved forward. Say so before deploying, not after.

## 7. Two notes about Claude Code itself

- **`.claude/` is a protected path.** Claude Code refuses agent writes there
  regardless of the permission allowlist, because hook and settings files there
  execute code. A coordinator told to keep its ticket ledger in `.claude/` could
  not create it. It stopped and escalated instead of routing around the refusal,
  which was the right behavior. Keep agent-written ledgers at the repository
  root. This was observed on 2026-09-04, on the first end-to-end run of the
  roster.
- **A published fix is not an installed fix.** The September lesson replaced
  machine-specific hook paths with `${CLAUDE_PROJECT_DIR}` in this repository.
  On 2026-10-09 the user-level agents installed on my machine still pointed at
  the missing path from another machine. The repository was right and the
  installation was not. After publishing a fix, update every installed copy
  and run the denied-path check against the installed copy.

## What I would keep

- processes stopped by PID or owned port, never by pattern
- scratch files, ports, and background tasks named by ticket
- disk and API budgets treated as shared, with guards in every long-running
  brief
- the worker's branch checked before resending a message, and one batched
  message per review round
- long jobs awaited in the turn, not left to a notice
- plan gates written as hand-backs that the coordinator resumes
- one inbox for the person, one decision per item, recommended option first
- answers confirmed when authorship cannot be proven
- changes to intent routed to the owner, never written into a spec by an agent
- schema-moving releases treated as rollback decisions
- installed copies updated and tested, not only the published source

Ownership tables answer "who may write this file". These failures needed a
wider question: what else does this action touch that nobody assigned to me?
