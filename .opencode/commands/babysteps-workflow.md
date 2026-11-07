# BabySteps workflow reference

Everything here is **optional context**. `babysteps-slice.md` is complete on its own. Read the one
section that matches the case in front of you, and nothing more.

## Work

**Sizing.** A task should carry at most one file's worth of context — the brief plus the
files being edited. If it touches more than two source files, split it. The goal is a model
with the ceiling from step 1 finishing the task without running out of room. A task sized
against the wrong ceiling dies mid-edit.

This sizing target is not a runtime cap. The host must enforce the active-context ceiling;
`--auto-chain` resets context between work units, not within one. Its foreground shell call is
the visible progress signal while the fresh child session runs. Keep a separate budget for
cumulative input cost, which can exceed active context as prior prompts are reused.

**One commit per coherent change.** The commit body carries the task number, the fault
history, the numbers, and the reasoning — not a restatement of the diff. State what the gate
proved *and what it did not*.

**Never leave the tree unbuildable between steps.** Finish a half-finished edit or revert it
before anything else.

**New source files.** Some build systems register sources automatically, some do not. Ask
before assuming. *MiniDiscovery example:* a new Swift file is not a file until it is in
`MiniDiscovery.xcodeproj/project.pbxproj`, which is hand-written and holds the same path
twice — once as a file reference, once as its group. If those disagree the build fails with
"Build input files cannot be found" and never says the group is wrong. Put it in both places.

## Gate

A check that examined nothing is not a pass. A build run from the wrong directory compiles
no sources and exits zero; `lipo -info` against a stale binary reports on a tree that is not
the current one. Either way nothing was established — report it as **not run**, not green.

Report each check separately with its real output. End with one line: **all green**, or
**red on `<check>`**.

*MiniDiscovery gate:* Debug and Release arm64 both build clean, then `lipo -info` on the
Debug binary reporting exactly `arm64`. A fat binary is a failure.

## Boundary

Only when `reboundaryPaths` / `rebuildBoundaryPath` is set — the array spelling exists because a
project can be ported from more than one predecessor. The rebuild must not have grown a runtime
dependency on the artifact it was rebuilt from. This is a separate claim from a green build and is
reported separately — green says the code compiles, not that it is free of the thing it came
from.

**The check is scoped to the current slice.** It asks one question: did this slice link, call, or
resolve into anything outside the boundary? Two checks, both over the slice's diff: **linkage**
(does the new or changed code import or call the predecessor, a legacy binary, or a vendored
third-party library — following the slice's calls one hop) and **paths** (does the new or changed
code or build file name a path inside the predecessor, at runtime or at build time).

**A pre-existing finding is not this slice's to re-report.** The inherited set — the vendored
binaries, the artwork, the fixtures — is a standing fact about the tree that lives in the
project's own notes, and re-deriving it on every slice is what made the check cost more than it
was worth. If the slice changed one of them, the diff-scoped checks cover it.

Report each check separately with `file:line`, and state the scope used. A check that examined
nothing is **not run**, not a pass.

*MiniDiscovery example:* boundary is `MiniDiscovery.app/`; the inherited set is the x86_64 CLI
tools, third-party dylibs, and artwork copied from the original, recorded in the project's own
notes rather than re-derived per slice. One `MiniDiscovery.app` hit in `project.pbxproj` is *not*
a finding — it is the product being built, resolved against `BUILT_PRODUCTS_DIR`.

## Running the app

Only when `runCommand` is set and the task is visible. A visual claim is not a claim until
someone observes it. Reading strings out of a Mach-O is not running the app — that is how a
sandboxed iCloud library path was missed entirely.

**Vision-blind models cannot read images.** If the active model cannot see images, describe
images as numbers: `sips -g pixelWidth -g pixelHeight` for dimensions, `ls -l` for bytes,
`diff` for identity against the original. This is coarse — it cannot see a seam or a glyph —
so a claim needing shape is **unverified**, never claimed.

## The slice seed

**One file carries the brief, and it is not the state file.** `docs/slices/NEXT.md` holds the next
action verbatim, what is settled, what is withdrawn, the code to touch, the specs to read and the
Do-Not subset — capped at **120 lines**.

The state file grows every slice, and it is where the next action goes to be hunted for. Measured
on one installed project: 4,500 lines / 312 KB, the next action at line 291 against eleven other
"next action" mentions of which most were `DONE` or `Superseded`, and 930 lines / 77 KB of Do-Not
list. The brief read all of it to extract about 100 lines of signal — a ~30× bloat that ran an hour
of prep. The seed moves the filtering to handoff time, while the context that knows the answer is
warm, so the brief reads a small file and checks that the specs were read.

Three rules, and all three are the difference between a fix and a slower version of the problem:

- **The brief never opens the state file, and never falls back to it.** If the seed is missing, the
  brief stops and says so. The fallback is what silently restores the bloat.
- **A slice is not closed until the seed for the next one exists.** A stale seed is worse than
  none: the next session reads it, believes it, and works on the wrong thing.
- **The seed is a filtered copy, never a source of truth.** Write-ups stay in the state file and
  faults stay in `docs/donot.md`. The cap is what keeps it a seed.

Err toward one extra Do-Not entry over omitting a relevant one. An omitted entry is a paid-for
fault being paid for twice, and one extra line costs 20 tokens.

## Do-Not list

**`docs/donot.md`, never dropped, never trimmed.** It has been destroyed by a rewrite before, twice,
each time by a session that had the rule in front of it — which is why it no longer lives inside
the file that gets rewritten every slice.

The brief reads the entries the seed cites **by number**, not the whole list. That is what keeps a
long fault history from costing a read of the entire file in every slice's prep.

After any change, read the list back out of the file. Confirm every prior entry is present verbatim,
the count only went up, and the last entry before it is unchanged. If one is lost, restore it and
say which and how — do not quietly repair the count. A present-but-short list is worse than an
absent one, because presence is the check everyone runs and a truncated list reads as healthy.

## Scratch

Scratch goes in `scratchDir`, never the system temp directory. Produce the removal list; do
**not** delete — the agent does not run its own sweep. A person who has looked at the tree
outranks a list assembled from memory.

Three lists, one path per line, in code blocks, nothing else — no tiers, no tables, no sizes, no
rationale. A flat list of paths cannot be misread, and annotation is what makes one misread.
Prose explaining a deletion belongs in the commit, not beside the list.

```
KEEP
<scratchDir>/<whatever the state file's own inventory names>

REMOVE
everything else under <scratchDir>/

NOT SCRATCH — operator's call
<anything outside <scratchDir>/, named on its own evidence>
```

**Two things a sweep must never take, and the second one fails somewhere else entirely.** What
must survive inside the scratch directory is whatever keeps a stray file from joining the thing
under judgement — a second `go.mod` in a Go tree, a manifest in a build tree, a manifest keeping
scratch out of a recursive lint. And a nested git repository under scratch blocks `git add -A`
outright, so a sweep that takes one surfaces as an unrelated failure in a later step. Name it.

Only the scratch directory is disposable by definition. Anything outside it is the operator's
call, named on its own evidence.

*MiniDiscovery example of what must survive:* `MiniDiscovery/Tools/`,
`MiniDiscovery/Frameworks/` and artwork under `MiniDiscovery/Resources/` are gitignored and
the original bundle they came from is the reverse-engineering source. A sweep that takes
them destroys work git cannot restore.

## Standing rules

- **An unnamed number in code is a defect.** Name it before writing it. One quantity, one
  name — two names for one value look like two facts and drift apart while staying green.
- **Comments are the invariant and the trap**, in one or two lines. No argument, no history.
  A comment that argues passes every length gate there is.
- **A check that examined nothing has certified nothing.**

Project doctrine — data formats, hardware, build quirks — belongs in that project's
own documentation or specs, not here. This file is the workflow, not the project.
