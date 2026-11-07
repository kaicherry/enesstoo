---
slice: 3
stateFile: docs/STATE.md
donotCount: 3
seededFrom: 84050f4
reads:
  - docs/slices/NEXT.md
  - docs/donot.md
allowanceTokens: 3000
description: Seed for EnessToo slice 3 — next action undefined; the queue is exhausted
read_if: Running /babysteps-slice after slice 2; there is no task to run
---

# Task 3: undefined — the queue is exhausted

## The next action

**Unknown.** Task 2 is complete and committed (`84050f4`), and task 3 was dropped because a
ROM registry contradicts the passthrough contract. No next task has been defined, so there is
nothing to run. This seed exists so the next session reads a true statement instead of slice
2's finished brief.

**Closes when:** the operator defines the next task. A defined task gets its own `PLAN.md`
row first, then a seed that names only the files that row prices.

## What is settled — do not re-derive

- bm42 is a **passthrough**. The frontend maps ROMs to bm42; bm42 executes the path it is
  handed and exits with that process's status. No registry, no name lookup, no extension
  filter, no rewrite of the path.
- The frontend contract is `docs/specs/bm42-frontend-contract.md`: identity (`-v` /
  `--version`), extensions (none required), launch syntax (`bm42 <path-to-rom>`).
- `cmd/bm42/main.go` is the only product file: `main()` → `run(args, stdout, stderr) int`,
  `launch(rom, stdout, stderr) int` doing the `exec.Command` call, a `version` var (`dev`,
  replaced with `-ldflags "-X main.version=<tag>"`), and `usageText`.
- Exit shapes are settled and probed: child status forwarded verbatim; no ROM, a second
  positional, and an unknown `-`-prefixed flag exit 2; an unexecutable path exits 1;
  `-v` / `--version` and `-h` / `--help` exit 0.
- The gate is module-wide (`./...`), not bare `go build` — see Do-Not 1.
- Module path is `github.com/kaicherry/enesstoo`; `go.mod` declares `go 1.22` and no
  third-party dependency.

## Withdrawn — proven wrong, do not use

- The first state/seed tables listed tasks 2 and 3 as "slice 1". They are separate work units.
- "The ROM mapping source is undecided" was wrong: the frontend owns the mapping.
- Task 3 (ROM registry config file reading) is **dropped**, not deferred. Do not revive it.

## Code to touch

None. There is no task, so a code-to-touch table would be invented.

## Read these first, and only these

- Nothing beyond this seed until a task exists. When one does, it will name its spec here.

## Do-Not entries that apply here

Total count: 3. All apply, because a new task must respect all three.

- **1** — a bare `go build` / `go vet` examines nothing at the module root; use `./...`.
- **2** — a seed without a `PLAN.md` row and `reads:` is refused; price the row first.
- **3** — do not build a ROM registry, name lookup, or extension filter into bm42.

## The gate

Nothing to gate until a task is defined. The commands that gate a code slice are:

```
go build ./...
go vet ./...
```

## When this slice closes

It has nothing to do. Report that the queue is exhausted and ask the operator what the next
task is; do not cut a slice from the passthrough contract to keep the queue moving.
