---
description: Check that the current slice did not link the rebuild to the artifact it was rebuilt from
agent: general
subagent: true
---

Check the rebuild boundary **for the current slice**. Read `.babysteps/config.json` once and take
the boundary from **`reboundaryPaths`** (an array) or **`rebuildBoundaryPath`** (a single path) —
either spelling is accepted, the array is preferred because a project can be ported from more
than one predecessor. If neither is set, the boundary is empty and this command reports **not
run**.

## The question

One question: **did this slice link, call, or resolve into anything outside the boundary?**

The boundary is the artifact the rebuild replaced — an original app bundle kept for
reverse-engineering, an upstream repository a port was taken from, a vendored implementation
being replaced. The rebuild must not have grown a dependency on it.

## The scope is the slice's diff

Take the diff of the working tree against `HEAD` (staged, unstaged, and untracked source
files); if the tree is clean, take the last commit's diff. Say which scope you used.

**Nothing outside that diff is this check's business.** A pre-existing finding is not this
slice's to re-report, and the whole tree is not a fresh audit every slice. If the slice changed
nothing, report the check **not run** — an empty diff is not a pass.

## 1. Linkage

Does the slice's new or changed code **import, call, or invoke** something outside the project —
the predecessor, a legacy CLI binary, a vendored third-party library?

Follow the slice's calls **one hop**. A new call to a helper that was already in the tree still
counts when that helper resolves into the boundary: the slice has added the linkage in effect,
and that is the one case where a file the slice did not author is in scope.

Report the line that does it, and name the predecessor's artefact exactly.

## 2. Paths

Does the slice's new or changed code, script, or build file **name a path inside the
predecessor**? Runtime and build-time reaches both count; say which it is.

**One hit is not a hit.** A path can be there because the project is naming *its own* output
resolved against the build directory — the product reference in a project file, the bundle
layout in a helper. Report the paths that resolve into the predecessor as it sits in this
repository, and say which of the two you found.

## Reporting

Report the two checks separately, with `file:line` for every finding, and state the scope used.
A check you could not run is **not run**, never a pass.

**What the tree still inherits is not this command's business.** The vendored binaries, the
artwork, the fixtures and the rest are a standing fact about the tree, recorded in the project's
own notes. Re-deriving them on every slice costs a great deal and adds nothing. If the slice
*changed* one of them, the diff-scoped checks above cover it.

Do not fix anything.
