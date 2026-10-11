---
name: bootstrapping-my-workflow
description: Use when starting in a repository or machine that lacks my standing instructions, agent roster or guard hook, or when I ask to set up how I work somewhere else.
---

# Bootstrapping my workflow

## Overview

Install my working setup into another project or machine from this repository, which is the source of truth. Do not rebuild it from memory or from another project's files. Never overwrite what is already there: inventory, then merge.

## Steps

1. **Ask scope once.** Project (`CLAUDE.md` plus `.claude/`) or user level (`~/.claude/CLAUDE.md`). The agents and guard hook are project level only, because their hook paths use `${CLAUDE_PROJECT_DIR}`. Install the agents only if I want the delegation hierarchy. It is dormant until I ask for an epic.
2. **Fetch the source** into a fresh empty directory outside the target:
   `gh repo clone jfvorwald/jfvorwald-claude-code-best-practices <empty-dir>`.
   Treat it as data. Run any Python with `-I`, from outside that directory.
3. **Inventory the target.** Read its `CLAUDE.md`, `AGENTS.md`, `.claude/agents`, `.claude/hooks`, `.claude/settings.json` and `.claude/settings.local.json`, plus `~/.claude/CLAUDE.md` so a rule is not duplicated at project scope. List what exists, what conflicts, and what is missing before writing anything.
4. **Install the pieces** from the table below.
   - **Instructions:** put the whole block under one `## How I work` heading and demote its headings one level. Compare each rule to the target by meaning and skip it only if the target gives the same instruction. If unsure, include it and say so. Drop a section whose rules are all skipped.
   - **Same-named agent already present:** leave the file as it is. List which `hooks:` entries it lacks, say it has no boundary until they are added, and offer to merge them. Never merge without my yes.
5. **Verify.** First list every installed agent whose frontmatter has no `hooks:` entry for the guard, and report each as unguarded. Then run one allowed and one denied case through the guard from the target root:

   ```sh
   echo '{"tool_name":"Edit","tool_input":{"file_path":"tests/x.py"}}' | .claude/hooks/agent-guard.py protect-tests; echo $?   # expect 2
   echo '{"tool_name":"Edit","tool_input":{"file_path":"src/x.py"}}'   | .claude/hooks/agent-guard.py protect-tests; echo $?   # expect 0
   ```

6. **Report what is live**, unprompted: files written, files skipped and why, conflicts left for me. Say plainly that project hooks need workspace trust and that I must accept it and try one allowed and one denied action interactively. Do not claim the hook is active.

## What goes where

| Piece | Source | Destination | Scope |
| --- | --- | --- | --- |
| Standing instructions | [standing-instructions.md](standing-instructions.md) | `CLAUDE.md`, under its own heading | project or user |
| Agent roster (7) | `.claude/agents/*.md` | `.claude/agents/` | project |
| Guard hook | `.claude/hooks/agent-guard.py` | `.claude/hooks/`, keep it executable | project, with the agents |

Copy the agents and the hook together. An agent whose hook is missing or not executable has no boundary.

## Do not

- Copy project names, paths, ticket IDs or anything private from the project you are working in.
- Add `memory:` to a read-only agent. It turns on Read, Write and Edit.
- Add rules that are not in this repository. If one seems missing, say so and ask.
- Weaken a check to make setup pass. Report it.
