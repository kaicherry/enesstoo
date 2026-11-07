---
description: Convert installed BabySteps commands/state to another harness or to Operator-compatible artifacts — formats, harness layout, and nomenclature
agent: build
subagent: false
---

Convert BabySteps artifacts for $ARGUMENTS. Preferred flags: `--to claude`,
`--to codex`, `--to opencode`, or `--to operator` (optionally `--dry-run`).
CLI equivalent: `python3 convert.py --target . --to <target> [--dry-run]`.

**This is a file-transformation task, not an implementation task.** Confirm each
overwrite before writing.

## Sources of truth

- Installed BabySteps commands: `.opencode/commands/babysteps-<name>.md`, **flat** (or the
  repository's top-level `*.md` files when no installation exists). The namespace is in the
  filename, never a directory: OpenCode does not walk nested command directories
  (sst/opencode#2532).
- State: the path in `.babysteps/config.json` -> `stateFile` (default `docs/STATE.md`).
- Slice seed: `<stateFile>`'s directory, `slices/NEXT.md` — the only file `/babysteps-brief`
  reads.
- Do-Not list: `docs/donot.md`, append-only, never dropped.
- Config: `.babysteps/config.json`.

## Harness conversion

For each target harness, copy the command files into that harness's command directory with the
`babysteps-` filename prefix, adjusting frontmatter only:

| Harness | Command directory | Filename form |
|---|---|---|
| OpenCode (source) | `.opencode/commands/` | `babysteps-<name>.md` (flat) |
| Claude Code | `.claude/commands/` | `babysteps-<name>.md` (flat) |
| Codex | `.codex/prompts/` | `babysteps-<name>.md` (flat) |

Adjust frontmatter:
- Drop OpenCode-only keys (`agent`, `subagent`) for Claude Code; keep `description`.
- Keep the command body byte-identical unless the target requires placeholders.

## Nomenclature conversion

- BabySteps vocabulary stays in the BabySteps-owned files: "work unit", "slice",
  "sub-task", "Do-Not", "context ceiling", "--bigBoy".

## Operator conversion

This conversion runs only when the user explicitly selects `--to operator`; the ordinary
BabySteps workflow never discovers or reads Operator.

When `.operator-shared/` exists:
1. Create `.operator-shared/specs/babysteps-workflow.md` (shared, publishable) holding a
   **pointer**, not a copy: the state file, the slice seed, and the Do-Not list, each as a path.
   Do not duplicate the queue, the active task or any task body — Operator specs link to files,
   they do not mirror them. `convert.py` writes exactly this and no more.
2. Add an entry to `.operator-shared/catalog.md` pointing at it.

If `.operator-shared/` is absent, report that no files were changed. Do not modify
`.babysteps/config.json`.

**`convert` is harness and theme translation only.** It copies BabySteps' own root commands
outward — it cannot convert a project's pre-existing command set, adopt an older incarnation,
or retire one. A target whose `.opencode/commands/` already holds commands under other names
gets a *second* suite beside the first, which is a defect and not a conversion.

## Guardrails

- Do not remove source commands or `docs/STATE.md`.
- Do not overwrite without confirmation; show the planned file list first.
- Leave `.babysteps/config.json` values stable unless the user asks otherwise.
