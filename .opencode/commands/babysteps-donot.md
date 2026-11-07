---
description: Work on the Do-Not list in its own file — append, verify it survived, migrate it out of the state file once. It fails rather than let a written rule be lost again.
agent: build
subagent: false
---

The Do-Not list is **`docs/donot.md`**, not the state file. One reason: a list that lives inside a
file rewritten every slice is a list that can be lost to a rewrite, and this one has been, twice,
both times by a session with the never-drop rule directly in front of it. Splitting it makes the
invariant cheaper to hold and cheaper to check, and makes the brief cheap — it reads the entries the
seed cites by number instead of the whole file.

## Migrate, once

If `docs/donot.md` does not exist and the state file has a Do-Not section:

1. Count the entries in the state file — call it `N`.
2. Write every entry to `docs/donot.md` **verbatim**. Do not reword, merge, dedupe, reorder or
   "tidy". A fault paid for once does not stop being a fault because the code moved.
3. Count the entries in `docs/donot.md` — it must be `N` — and the **last entry's text must match
   the state file's last entry, verbatim**.
4. Only then replace the section in the state file with a pointer:

   `**The Do-Not list is `docs/donot.md`** — N entries, append-only. Never dropped, never trimmed.`

If either check fails, **stop, restore the state file, and do not migrate.** An aborted migration is
recoverable; a silently shortened list reads as a healthy one, because presence is the check
everyone runs. Say which check failed and what you restored.

## Append

Append anything in `$ARGUMENTS`. If no arguments were given, read the list and report its entry
count and whether any entry looks truncated.

New entries continue the numbering from the last one — never renumber. Format:

```
N. **Do not <the thing> — <the one-line tell>.** <What it presented as, what it cost, and the fix,
   in two or three sentences.>
```

The first sentence of each entry is load-bearing: it is the part the brief copies, and it is what a
session reads at 2am. Make it a rule that can be followed without the paragraph under it.

## Then verify it is still there

1. Read the list back out of the file **after** writing. Confirm every pre-existing entry is
   present, verbatim, and that the count has only gone up.
2. Confirm the last entry before the append is unchanged.
3. If a single entry has been lost, **restore it and say which one and how it went**, rather than
   quietly repairing the count.

## Do not

- Trim, reword, merge or reorder entries.
- Decide an entry is now obsolete because the code moved.
- Put a date or a status on an entry — the file is append-only, not a changelog.
- Add section headings mid-file. One flat numbered list, opening with one line of framing.

Finish by stating the entry count **before** and **after**. If they are not equal or higher, that is
a failure — say so plainly and do not report success.
