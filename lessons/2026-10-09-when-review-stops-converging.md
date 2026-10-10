# When review stops converging

**2026-10-09. Claude Code 2.1.293 at the time of writing. Drawn from two weeks
of coordinating Rally: 59 tagged releases, up to three concurrent workers, and
an automated pre-merge review panel on every branch.**

The September lessons were about getting parallel work to start safely. The
next two weeks were about getting it to finish. Most of the lost time came from
two places: review loops that never converged, and runs that looked like
evidence but were not.

---

## 1. A review loop is a design signal

Rally's merge gate is an automated review panel, a bug reviewer and a security
reviewer run through roborev, that every branch must pass. Over two days, six
cards each ran 9 to 16 rounds. Every round found a narrower edge of the same
problem, the worker patched it, and the next round found the next edge. At 40
to 60 minutes a round, that does not converge.

The loops ended only when the coordinator stopped approving point fixes and
changed the design. The class fixes that worked:

- **One source of truth.** A waiter that kept its own list of sources became a
  reader of the existing registry, so there was nothing left to fall out of
  sync.
- **Decide by evidence or ordering, never by a timer.** Timer windows and clock
  thresholds both failed. Each new threshold created a new boundary to probe.
- **Count against intent.** A drop counts the files it expected. A step reports
  whether it actually submitted.
- **Confirm instead of acting automatically.** Replacing a silent automatic
  action with "Everything is saved" plus an Export button removed a whole
  category of omission tracking.
- **Make a product decision when nothing is lost.** A pause the browser undoes
  before the page sees it is a glitch, not a stop. Once that was decided, its
  edge cases stopped being defects.
- **Write the whole state machine down.** A table of states by events in the
  module header, with one named test per cell, closed the last open class on
  one card in a single round.

The rule I now give the coordinator: after two or three rounds in the same
class, stop patching instances. Ask for a class fix, a mechanical sweep of every
call site (grep each entry point rather than reading the flows), or a product
decision.

## 2. Check whether the looping feature is yours

The most expensive loop was self-inflicted. One card ran 13 rounds, and 11 of
them were edge cases of a button that closed other open dialogs. I had asked
for "a warning dialog". The coordinator had added the button on top. Removing
it, plus an ordering rule and an explicit state table, ended the loop.

The same thing happened on an audio card. A global cap the coordinator had
added caused a cross-track eviction class that review kept finding. Cutting the
cap ended it.

Before approving another fix, trace the looping feature to the requester's
words. If it is the agent's own addition, the cheapest fix is deletion.

## 3. Cap every session up front

One worker ran 11 panel rounds. Another ran about 30 review jobs before
passing. Several sessions errored out before handing anything back, and one
stalled with no process for about six hours until a fresh worker finished the
card. I told the coordinator: "make sure these two sessions finish up. we need
to start capping them."

The cap now goes into every dispatch prompt from the start, not after someone
notices:

- a scope freeze, with any wiring into another ticket cut into its own
  follow-up ticket
- at most two or three review rounds, fixing real Medium-or-higher findings and
  one-line Lows, and recording the rest with their job IDs
- one final full check run, rerunning only a flaky suite rather than the whole
  chain
- the report, stopping the worker's own processes, and handing back

What happens past the cap is the coordinator's decision. Coordinator fix rounds
count toward it too. On one measurement harness the worker used its three
rounds, then the coordinator ran seven more, and each found two or three new
edge cases in the same 560-line script.

## 4. The reviewer is a noisy instrument

Treat an automated reviewer like any other measurement.

- **It is not deterministic.** One job passed, and the next found a new High on
  almost the same code. A single pass is a sample.
- **Check what it reviewed.** A bare branch review diffed against
  `origin/main`. When pushes were paused and origin lagged, the panel reviewed
  about 70 already-accepted commits along with the card. A fast pass over the
  wrong range means nothing. Every dispatch prompt now names the base.
- **Narrow reviews catch what broad ones miss.** Per-commit reviews, with
  smaller ranges, found three real defects that a passing pre-merge panel had
  missed. Before merging, read every failed job whose range lies on the branch,
  not only the last panel.
- **Status words are not verdicts.** Queued is not passed. A job that failed to
  run is not a failing review. A Pass is not task acceptance. Closed means
  handled, not correct.
- **Context the reviewer cannot see gets raised forever.** A schema finding kept
  returning while the worker argued that the old schema was unreleased. The
  reviewer could not see release history. Bumping the schema version ended the
  finding.
- **A measurement harness gives review unlimited surface.** Window-boundary
  accounting, exit and interrupt paths, setup interruption, workload
  completeness: there is always another edge. After one coordinator round,
  write a single consolidated rule list (one boundary definition, every
  operation failure fails the run, every exit path drains), run one panel, and
  if it fails, park the card with its evidence.

For findings about test validity, prove the test can fail. Delaying one input
by a single gain ramp made all 36 checks fail, which settled whether the test
measured anything.

## 5. Test the review gate's fallback

The review gate had single points of failure that nobody had exercised. Both
reviewers ran on one provider and inherited that same provider as their backup,
so a provider failure had no fallback. After that was fixed, the synthesis step
that combines the panel's findings still had no backup. When the provider's CLI
was missing from the machine, a panel with any finding, even a Low, failed with
"no configured agent available". A panel with no findings passed, because
synthesis had nothing to do. Forcing the fallback agent failed too: it
inherited the primary provider's model name.

This is working-agreement rule 9 again, applied to review tooling instead of
hooks. A gate that only works when its primary path works has not been tested.
Run it once with the primary missing.

## 6. A run is evidence only for the code it ran

- **Never edit code a test run is serving.** The dev servers hot-reload. An
  edit in the middle of a combined end-to-end run means later suites test
  different code from earlier ones, so neither a failure nor a pass is evidence
  for either commit. This invalidated three long runs. Finish the fixes,
  restart the server on the final commit, then run.
- **Triage flakes before rerunning.** The release suites are `&&`-chained, take
  about 40 minutes, and share an 8-core machine with up to three workers. A
  failure under a load average near 10 is often load. Check the load and what
  changed, rerun from the failing suite onward, and record the run as segments
  with counts. A check that fails twice in a row with nothing relevant changed
  is a real race. Twice, a suspected flake turned out to be a product defect,
  and fixing the product ended it. A CPU stress harness pushed the load average
  to about 95; never schedule one alongside a release run.
- **Measure the system, not the harness.** Room CPU per message looked like 13
  to 17 ms with process CPU time, over a 10 ms budget. Per-thread CPU time gave
  4 to 8 ms; the rest was the test runner's other threads. The fake socket also
  parsed every outgoing frame, which production never does.
- **Copy numbers from the log with a command.** One release note said 2,157
  tests where the log said 2,187, and the tag was already pushed. Counts are now
  summed by a one-line pipeline. Counting failures needs the same care: some
  suites print "19 PASS, 0 FAIL", so a naive search for FAIL matches every
  summary line, and an exit 1 with no FAIL line is a crashed suite.

## 7. A model of the system hides what the system does

Rally's audio engine has a specification model that replays automation and
checks values. In one wave, every check against a real browser engine found a
defect the model had missed. An offline render harness found one, a Chrome
output recorder found two more, and a harness around the real player reached
one of the same defects through ordinary timing.

The usual cause was engine behavior the model did not encode. A fresh gain node
plays its default value of 1 for a source that starts a hair after a frame
boundary. The model replays from the source start, so a one-sample spike is
invisible to it.

Two consequences:

- A fix proven only on the model needs a real-engine check before acceptance.
- Acceptance lists are per area. One change to the audio engine, which added
  content-hash verification, was accepted on the unit and end-to-end chains
  alone. The real-engine harness was never run, and it had gone red: 86 of 176
  scenarios. Its fixture page had no WebCrypto and served empty digests, so
  nothing was scheduled. A later card found it.

A sampled browser suite is also weak proof for a rare defect, here about 1 in
300 edits. A deterministic scenario that places events 1e-9 s after a frame
boundary is the proof.

## What I would keep

- after two or three review rounds in one class, a class fix, a state table, or
  a product decision
- every looping feature traced to the requester's words, with the agent's own
  additions cut first
- a cap in every dispatch prompt: scope freeze, bounded rounds, one final run,
  hand back
- reviewer output treated as a noisy measurement: check its range, read the
  narrow jobs, and do not trust one pass
- every gate, including review tooling, run once with its primary path missing
- no edits while a run is serving the code
- counts copied by command, never by hand
- a real-system check for every change proven only on a model

The common thread is that a verdict is only as good as its inputs. A review
over the wrong range, a run over mixed code, and a model without the system's
quirks all produce confident answers to a question nobody asked.
