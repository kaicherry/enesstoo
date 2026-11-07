---
description: Interview the user, then set up or extend slices and sub-tasks as work units in docs/STATE.md — the handoff for the next /babysteps-slice
agent: build
subagent: false
---

Interview the user and establish the work units BabySteps will execute. **Do not implement
anything.** The output is a `docs/STATE.md` (and, optionally, `.babysteps/config.json`)
that the next `/babysteps-slice` can pick up.

$ARGUMENTS may name a project or a topic to seed the interview; otherwise start from
nothing.

## Context ceiling

Read `.babysteps/config.json` if it exists; otherwise default to 150000 tokens and offer to
save that value. The ceiling sizes one work unit's brief + touched files; it is not a lifetime
or runtime host limit. Every slice/task planned here must plausibly fit inside it unless the
user opts into `--bigBoy` later.

Ask for the active provider/model and its **context window** (the maximum prompt size the model
accepts). If unknown, offer a conservative default (e.g. 90000) and record it as
`modelContextLimit`. The effective work-unit budget is `min(workBudgetTokens ??
contextCeilingTokens, contextCeilingTokens, modelContextLimit)` — the smaller of the three,
because a budget above the host window cannot be spent. This calculation does not configure or
enforce a host limit.

Ask separately whether the user wants a per-session USD cost ceiling. If they choose one, record it
as `costCeilingUSD`; it is not part of the token-budget calculation. The guard stops at 95% of that
amount at a commit boundary, using the OpenCode main session's recorded cost (not separate subagent
sessions). Other harnesses do not currently provide this cost guard.

**The work-unit budget is the constraint, and it binds regardless of the host window.** A model or
provider that offers more context does not raise the budget: the work must still fit if it is later
transferred off the cloud model to a smaller one, so size every slice to the budget and never to the
host headroom. A slice too large for the budget is a slicing fault — split it.

Ask for the host's usable context limit and compaction reserve separately from the work-unit
ceiling. Record the effective host limit as `modelContextLimit`. For OpenCode, verify the selected
provider/model's `providers.<provider>.models.<model>.limit.context` and `compaction.buffer`.
Keep the work-unit budget lower to leave room for fixed prompt/tool context, tool results and
closeout; do not set the host limit equal to a smaller work-unit budget to force slices to fit. If
there is no verifiable host limit/reserve, say so and ask whether to proceed advisory-only.

## Interview

Use the `question` tool. Group related questions; do not overwhelm. Cover, in this order:

1. **What we are building.** One paragraph — what exists now, what the goal is.
2. **Work breakdown.** Slices (phases) and, within each, tasks/sub-tasks with one-line
   descriptions. Use the vocabulary the user uses; "slice" and "task" are fine defaults.
3. **Gates.** What proves a task is done (build, test, run-app, measurement). Record the
   exact commands. Do not assume xcodebuild or any tool not stated.
4. **Do-Not seed.** Faults already paid for in this project's history. Ask; an empty list
   is acceptable on a green field. These go in `docs/donot.md`, not the state file.

5. **Project-specific tools and paths.** Ask for equivalents; do not assume the built-in
   defaults, and record the answers in `.babysteps/config.json`:
   - Code exploration / indexing tool (default: jcodemunch; may be ripgrep, sourcegraph,
     or none).
   - Build / test / gate commands and the verifier (e.g. `make test`, `go test ./...`,
     `xcodebuild ...`, `lipo -info ...`).
   - State file path (default: `docs/STATE.md`).
   - Where specs live (default: `docs/`). Use only locations the user names.
   - Scratch / temporary directory (default: `localTmp/`).
   - App-run / behavioural verification command, if any.
   - Whether the work includes a rebuild boundary (an original bundle or artifact the
     rebuilt thing must not depend on) and, if so, its path. **Ask for every predecessor** — a
     port can be taken from more than one tree, and a single path silently un-checks the rest.
     Record them as `reboundaryPaths` (an array); `rebuildBoundaryPath` is the single-path
     spelling and is still accepted.
   - Registration steps for a new source file (e.g. none, or a hand-edited project file
     such as `project.pbxproj`).

## Output

1. Write `<stateFile>` (default `docs/STATE.md`) using the structure from `<name>handoff`:
   - **Where the work is** — one paragraph.
   - **The next action** — exactly one task, named, with its gate.
   - A pointer line to the Do-Not list: `**The Do-Not list is `docs/donot.md`** — N entries,
     append-only. Never dropped, never trimmed.`
   - Task-level queue (Completed / In progress / Queued) with the formats documented there.
2. Write the seed, `docs/slices/NEXT.md`, from the **first** task — this is what the next
   `/babysteps-slice` reads, so a project that starts without one starts by hunting the state
   file. Same section structure as `<name>handoff` § 3. Under 120 lines.
3. Write `docs/donot.md` with every entry carried in from the interview, verbatim, numbered from 1.
   Append-only thereafter; never dropped, never trimmed.
4. Write or update `.babysteps/config.json` with at least:
   ```json
   {
      "contextCeilingTokens": <number>,
      "modelContextLimit": <number or null>,
      "costCeilingUSD": <USD ceiling, only if the user chose one>,
      "stateFile": "docs/STATE.md",
      "specsLocations": ["docs/"],
     "scratchDir": "localTmp/",
     "codeIndexTool": "jcodemunch",
     "gateCommands": [ "<command>", ... ],
     "runCommand": "<command or empty>",
     "reboundaryPaths": [ "<path>", ... ],
     "rebuildBoundaryPath": "<single path or empty — legacy spelling, still read>",
     "newFileRegistration": "<description or empty>"
   }
   ```
5. If no slice directory exists and the user wants notes, suggest `docs/` for plans;
   do not create speculative files.

## Guardrails

- Never overwrite an existing `<stateFile>` without confirmation; append or advance it if
  it already exists.
- **Never overwrite an existing `docs/donot.md`.** If one exists, verify its count and carry every
  entry forward verbatim. If the state file still holds a Do-Not section, migrate it per
  `<name>donot` and verify the count and the last entry before replacing it with the pointer.
- Do not remove or migrate the user's existing files. `--bigBoy` is a runtime flag, not a
  setup choice; do not bake it into config.
- Do not scan for or infer spec locations; use only the locations the user named.
