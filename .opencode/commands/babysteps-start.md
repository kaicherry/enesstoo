---
description: Start BabySteps with a deterministic session-cost preflight and setup interview
agent: build
subagent: false
---

BabySteps setup has already run its deterministic budget preflight below. Treat that output as
measured input, not as a suggestion. Do not start implementation work in this command.

## Preflight

!`python3 .babysteps/bin/babysteps-start.py --root "$PWD" --arguments "$ARGUMENTS"`

## Setup contract

- Parse the invocation arguments from the final `Invocation arguments` line and preserve them.
- If `--budget N` was supplied, use N as the planned work-unit budget and write it into the
  project config as `workBudgetTokens` only after checking the existing project state; do not
  silently lower a larger configured ceiling. Do not write it into `contextCeilingTokens`: the
  slice reads `workBudgetTokens` first, and the ceiling still clamps it.
- If `--bigBoy` was supplied, say that the planned work-unit ceiling is dropped for this setup;
  the host context limit still applies.
- Read the project state, existing docs and current Git status before writing setup files.
- Create or update the BabySteps state and seed through the normal interview contract. Do not
  inspect game binaries, keys, secrets or product source unless the resulting seed explicitly
  calls for that later.
- End by reporting the preflight's measured session cost, model, token totals and any
  reconciliation gap. The session ledger is the spend record; a forecast is informational.

The next work unit is not started by this command. When setup closes, use `/babysteps-slice` in a
new turn.

**Invocation arguments:** $ARGUMENTS
