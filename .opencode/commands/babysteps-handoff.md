---
description: Advance the state file, the Do-Not list and the slice seed — delegated, because the prose is redundancy in the context that has to think
agent: general
subagent: true
---

Three files, in this order. The last one is the point.

**Nothing is written until the operator says apply.** You propose; the helper previews;
the operator applies. Do not edit `docs/STATE.md`, `docs/donot.md` or `docs/slices/NEXT.md`
yourself — write the proposal and let the helper write the files.

## The flow

1. **Draft.** Put the proposed files in the scratch directory, under
   `<scratchDir>/handoff/proposal/`:
   - `STATE.md` — the whole proposed state file.
   - `NEXT.md` — the whole proposed seed.
   - `donot.append.md` — only the **new** Do-Not entries, if this slice paid for any.
     Never a whole replacement list: the list is append-only, and the helper appends
     what you give it. A number that continues from the last entry; no renumbering.

2. **Preview.** From the project root:

   ```sh
   python3 .babysteps/bin/babysteps-handoff.py preview --proposal <scratchDir>/handoff/proposal
   ```

   (In the BabySteps repository itself the helper is the source file: `python3 handoff.py
   preview --proposal <scratchDir>/handoff/proposal`.)

   The preview writes **no project file**. It writes a plan under
   `<scratchDir>/handoff/plan.json` and prints the diff of each file, the Do-Not entry
   count before and after, and the checks it ran. A failed check is a refusal: fix the
   proposal and preview again.

3. **Show.** Report the preview to the operator — the diffs, the counts, the checks — and
   ask for the apply. Do not apply on your own initiative.

4. **Apply.** Only after the operator says so:

   ```sh
   python3 .babysteps/bin/babysteps-handoff.py apply
   ```

   The apply writes exactly the bytes the preview showed. It refuses if the files changed
   since the preview, because a stale preview is not what the operator read.

## 1 — `<stateFile>` (the record)

Default `docs/STATE.md`. A handoff is **not a journal**. It says *pick up here*. Two sections, in
this order:

1. **Where the work is.** What exists now, in one paragraph. Not a list of commits — `git log` has
   that.
2. **The next action.** Exactly one task, with the gate that closes it. One, not a list: a handoff
   describing ten findings and one action reads, to a model with a tight budget, as ten actions. If
   the work genuinely forks, say which branch you took and why.

3. The write-up for this slice goes under "Task / Slice write-ups" as its own
   `### <task> write-up (completed)` heading. That is where the reasoning lives, and where it is
   never re-read unless someone needs it.

**Task-level formatting.** The queue section uses this structure:

```
### Completed
- **Slice 7, Task 7.1 (LPCM)** — description. Commit: `<hash>`. Gate: ...

### In progress
- **Slice 7 — Reduce ffmpeg's role** — full slice gate.
  - **7.2a AT3+ decoder plan** — description. **NEXT.**
  - **7.2b AT3+ VLC builder** — description.
  ...

### Queued
- **Slice 8 — NetMD verification.** ...
```

Each task has a short label, a one-line description, and its position in the queue. Slices are only
complete when all their tasks are done and the full slice gate passes.

**The next action is named in three places, and they must agree:** the pointer line under
"## Where the work is", the "## Next action" section, and the "## Queued" list. The helper checks
this and refuses a proposal that leaves them disagreeing.

**The Do-Not list does not live in the state file.** It is its own file, `docs/donot.md`, append-only
(§ 2). The state file carries a one-line pointer to it with the entry count, and nothing else — a
list living inside a file that is rewritten every slice is a list that can be lost to a rewrite,
and it has been, twice, both times by a session with the never-drop rule directly in front of it.

## 2 — `docs/donot.md` (append-only, never dropped)

**Migrate it if it is not already its own file.** If the state file still holds a Do-Not section,
extract it to `docs/donot.md`, verify, then replace the section in the state file with the pointer.
Verification, in order, before touching the state file:

1. Count the entries in the state file — call it `N`.
2. Write every entry to `docs/donot.md` **verbatim**. Do not reword, merge, dedupe, reorder or
   "tidy". A fault paid for once does not stop being a fault because the code moved.
3. Count the entries in `docs/donot.md` — it must be `N`, and the **last entry's text must match
   the original's last entry, verbatim**.
4. If either check fails, **stop and say so. Restore the state file and do not migrate.** An
   aborted migration is recoverable; a silently shortened list reads as a healthy one, because
   presence is the check everyone runs.

Entry format, numbered throughout:

```
1. **Do not assert where user data lives from a remembered path — run the app and look.** The library
   was reported absent and the folder empty, twice, while it sat in an iCloud ubiquity container.
   ...
```

Append anything this slice paid for. Number continues from the last entry; never renumber.

The file opens with one line of framing — these are this project's own paid-for faults, appended as
they are met, a fault listed here that repeats is a defect in whatever repeated it — and **nothing
else**. No section headings mid-file, no dates, no status.

**You never hand the helper a whole list.** You hand it the new entries in
`donot.append.md`; it appends them to the existing file. The helper refuses a fragment that
renumbers, that repeats an entry, or that carries anything but numbered entries.

## 3 — `docs/slices/NEXT.md` (the seed)

The seed is the whole point. It is the only file the next brief reads. **Under 120 lines.** If it
will not fit, the task is too big — split it. A seed over the cap is not a seed; it is the state
file's problem in a new location.

Frontmatter first:

```markdown
---
slice: <the next task's label>
stateFile: docs/STATE.md
donotCount: <the count you just confirmed>
seededFrom: <the commit that closes this slice>
reads:
  - <the plan row's reading set, copied verbatim>
allowanceTokens: <the plan row's allowance>
---
```

**`reads:` is the plan row's reading set copied verbatim — it is not your judgement.** The plan
prices that set and the seed names it, and a seed naming a file the row does not price is work
nobody budgeted. That is the fault the check exists for: on miniD a row priced 68k while its seed
named ~122k, and the files added on top were the whole over-run. If a file genuinely belongs in the
set, **re-cut the plan row first** — never widen the seed.

Then, in this order:

| section | comes from |
|---|---|
| **The next action — verbatim** | the "The next action" paragraph from § 1, and the closes-when line |
| **What is settled — do not re-derive** | the measured facts the next task would otherwise re-derive. Only what was proven this slice or last. |
| **Withdrawn — proven wrong, do not use** | every number withdrawn during the work just done, with why. Each was measured wrong and each closed under arithmetic. |
| **Code to touch** | the files, one row each, with what changes in each |
| **Read these first, and only these** | spec paths and scratch paths. **Paths only — do not quote a spec's contents.** If a spec is large, name the section. |
| **Do-Not entries that apply here** | the filtered subset, cited **by number**, each with the one-line reason it bites, copied verbatim from `docs/donot.md`. State the total count so a reader knows the list was filtered. |
| **The gate** | the gate commands, plus this slice's own close |
| **When this slice closes** | the instruction to write the next seed and re-verify the Do-Not count |

The Do-Not subset is the only judgement call. **Err toward one extra over omitting a relevant one** —
an omitted entry is a paid-for fault being paid for twice, and one extra line costs 20 tokens.

**Then check the seed, and do not apply one that fails.** Write it, then run:

```
.babysteps/bin/babysteps-budget --seed docs/slices/NEXT.md
```

The checker resolves the plan from the project's `planFile` config key, then the tool's default.

Exit **0** is the pass. Exit **4** means the seed names a file its row does not price: fix the seed,
or re-cut the plan row if the file belongs there. Exit **2** means the check could not be made at
all — no budget table, no row for this slice, or no `reads:` in the seed — and an unpriced seed is
the fault this gate exists to refuse, not a cheap slice. **A seed that does not pass is not
applied.** If the check cannot run because the suite binary is missing, say so in the report and
treat the seed as unverified rather than as passed.

## What must not be touched

No tracked file other than the state file, `docs/donot.md` and `docs/slices/NEXT.md`, and no tracked
file at all until the apply. No `git commit` / `checkout` / `reset`. No path outside this
repository. Scratch in `<scratchDir>/`, never the system temp directory.

## Before replying

Report, on separate lines:

- the Do-Not entry count **before** and **after**, and the last entry's text unchanged
- the line count of the seed you wrote
- what the seed left out
- whether the update was previewed and is waiting for an apply, or was applied
