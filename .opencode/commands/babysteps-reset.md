---
description: Clear this session's accumulated context and start fresh with the next task — runs /brief to establish what to load
agent: general
subagent: true
---

Clear the session and establish a fresh context for the next task.

Run `/brief` to get the next task summary (next task, Do-Not entries, code to touch). Then produce a **reset session document** — a single output that contains ONLY:

1. **The next task** — verbatim, from /brief
2. **The relevant spec excerpt** — the section of a spec under `docs/` or a project-specific
   location explicitly listed in `specsLocations` that this task needs (not the whole file)
3. **The plan excerpt** — if a plan document exists (e.g. `AT3PlusDecoderPlan.md`), only the sections relevant to this task
4. **The Do-Not entries that apply** — filtered from the full list
5. **What code to touch** — files to create/edit, and the registration each new file needs. That
   is whatever `newFileRegistration` says in `.babysteps/config.json`: none at all in most
   languages (Go compiles from the filesystem), or a hand-edited manifest where it does not.
6. **Gate instructions** — the `gateCommands` from config, in order.

This document is the ENTIRE context for the next agent invocation. Nothing else is needed. If the brief says "plan only," include the plan read instructions. If it says "implement," include the source file outlines.

**Do NOT include:** previous task write-ups, historical context, session history, or any information not needed to execute the next task.

**Do NOT commit, edit, or run anything.** This is a context-loading step only. The output is a document, not an execution.

After producing the document, report: "Session reset complete. Next task: [task label]. [Brief summary]. Use this output to start a fresh session."
