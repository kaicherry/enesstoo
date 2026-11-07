---
description: Read the slice seed, only the specs it names, and the Do-Not entries it cites by number; report the working set. The state file is never opened.
agent: general
subagent: true
---

# /brief

**Do not read the state file.** The slice seed has already copied the next action out of it.

## Why

The state file grows every slice, and the brief used to read all of it. Measured on one installed
project: it reached **4,500 lines / 312 KB**, the next action sat at line 291 competing against
**eleven other "next action" mentions** of which most were `DONE` or `Superseded`, and the Do-Not
list occupied **930 lines / 77 KB** — the largest single section. `/brief` read all of it to
extract about 100 lines of signal. **A ~30× bloat, and the prep ran an hour.**

The seed is the fix, and the filtering happens in exactly one place: at handoff time, while the
context that knows the answer is still warm. The brief checks that the named specs were read.

## Read exactly these, and nothing more

1. **`docs/slices/NEXT.md`** — in full. It is the whole brief: the next action verbatim, what is
   settled, what is withdrawn, the code to touch, the specs to read, the Do-Not subset and the
   gate. The seed sits beside the state file if `stateFile` is configured elsewhere.
2. **The specs the seed names** under "Read these first, and only these" — those files, and no
   others. Read the section it names, not the whole spec.
3. **The Do-Not entries it cites by number**, pulled individually from `docs/donot.md`. Do not read
   the whole list.

`read` is a top-level tool: it is NOT inside the Code Mode `execute` catalog, so `tools.read` and
`read({...})` inside `execute` both fail. If `read` appears unavailable, use `shell` with `cat`
instead and carry on — do not spend turns searching for a tool.

## Report back, tersely, and nothing else

- **The task** — the "next action" paragraph verbatim, and the closes-when line.
- **Code to touch** — the table, unchanged.
- **The gate** — the gate commands, and this slice's own close.
- **From the named specs** — the path and the section name only. Do **not** quote paragraphs; the main session reads them on demand. Quote the numbers (spec + Do-Not).
- **Withdrawn numbers** — so they are not re-measured as if new.
- **The Do-Not entries that apply** — by number only. Do **not** quote the entry body; the main session reads them on demand.

No history, no prior write-ups, no summary of the seed itself. Six items is the whole reply.

## If the seed is missing

**Stop and say so.** Do not fall back to reading the state file: a brief that hunts the next action
out of thousands of lines is the problem the seed exists to remove, and running the fallback
silently restores it. A stale seed is fixed by `/babysteps-handoff`.

If the seed names no spec, read no spec. If it cites no Do-Not entry, read no fault. An empty
section is an answer, not an invitation to look further.
