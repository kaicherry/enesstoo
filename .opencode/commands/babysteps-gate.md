---
description: Run the project's configured gates and report the real output — whatever they are
agent: general
subagent: true
---

Run the gate on the current tree and report what happened.

Read `.babysteps/config.json` once and take **`gateCommands`** as the whole list. There is no
built-in gate: the suite does not know whether this project builds, tests, lints, or runs a
purpose-built gate binary, and it must not assume. If `gateCommands` is absent or empty, say
**not run** and stop — do not substitute a gate you chose yourself. A gate the project never
asked for passes for reasons that have nothing to do with the change.

`$ARGUMENTS` names the task under test (e.g. "7.2a" or "Slice 7") and carries context — what
changed, what the task expected to prove. If the task is a planning task with no code changes,
run the gate anyway: the gate verifies the tree is clean, which is the whole point. `$ARGUMENTS`
never selects a gate to skip. Run all of them.

Run each in order, each with its own exit status. Report each separately with its actual output,
state plainly which did not run, and end with one line — **all green**, or **red on `<check>`**.

## A gate that examined nothing has certified nothing

A check that runs and succeeds while inspecting an empty set has proved nothing, and its success
is the most dangerous result on the page. Report it as **not run**, never as green.

This is not hypothetical and it is not rare. Four measured shapes:

- **A build run from the wrong directory** finds no project, compiles no sources, and exits zero.
- **An architecture check against a stale binary** reports on the tree from an earlier build.
- **A lint that walks the filesystem instead of the module.** `gofmt -l .` walks scratch
  directories, nested modules and vendored trees, reports about files nobody ships, and goes red
  on arrival — worse than not having the check. Scope the walk to what the project owns:
  `gofmt -l $(go list -f '{{.Dir}}' ./...)`. The same shape appears in any tool with a recursive
  default and a project that has a vendored tree, a second `go.mod`, or a scratch directory.
- **A dependency or boundary check over an empty module.** See `/babysteps-boundary`.

If a gate prints a non-verdict word — `NO-RESULT`, `RECORD-INVALID`, `SKIPPED` — that is **not a
pass**. It means the gate looked and could not conclude, or its own record could not be read.
Report it as what it says and name the reason if the gate gave one.

## A skipped gate is not a gate

Record the skip and its reason. `make test` that would not fit on disk is a skip, not a pass, and
letting it stand in for evidence is the failure this paragraph exists to prevent.

## Do-Not integrity

The Do-Not list is verified by `/babysteps-donot`, which reads `docs/donot.md` back after any
write and confirms every prior entry is present verbatim and the count only went up. If this slice
touched the fault list and you have not run `/babysteps-donot`, the gate is incomplete — say so
plainly. A project that already owns a purpose-built checker for this may list it in
`gateCommands` and run it alongside; it does not replace the read-back.

Do not fix anything. Do not report a gate you did not run.
