---
slice: 2
stateFile: docs/STATE.md
donotCount: 2
seededFrom: 40cc398
reads:
  - docs/slices/NEXT.md
  - docs/donot.md
  - cmd/bm42/main.go
  - go.mod
allowanceTokens: 12000
description: Seed for EnessToo slice 2 — ROM passthrough
read_if: Running /babysteps-slice for task 2
---

# Task 2: ROM passthrough (lookup + execute)

## The next action

**Task 2: ROM passthrough (lookup + execute)** — take a ROM name as a positional
argument, resolve it to the binary it maps to, and execute that binary, forwarding its
exit status. Gate: `go build ./...` + `go vet ./...`.

**Open decision:** the mapping source is not yet specified — Task 3 is registry config
reading, so slice 2 must either define the mapping here or wait for Task 3; confirm with
the operator before inventing a registry format.

**Closes when:** `go build ./...` and `go vet ./...` are green, task 2 is marked complete
in `docs/STATE.md`, and the seed for task 3 is written and passes
`babysteps-budget --seed docs/slices/NEXT.md`.

## What is settled — do not re-derive

- Module path is `github.com/kaicherry/enesstoo`; `go.mod` declares `go 1.22`.
- `cmd/bm42/main.go` is the only product file. It has `main()` → `run(args, stdout, stderr) int`,
  a `version` var (`dev`, replaced with `-ldflags "-X main.version=<tag>"`), and a `usageText` const.
- Flags today: `-v` / `--version` print `bm42 <version>`; `-h` / `--help` print usage; no args
  prints usage; an unknown `-`-prefixed flag prints an error plus usage to stderr and exits 2.
- A bare positional argument currently falls through to usage and exits 0 — that is the hole
  this slice fills.
- The gate is module-wide (`./...`), not bare `go build` (Do-Not 1).
- The repository is initialized on `main`; slice 1 is commit `40cc398`.

## Withdrawn — proven wrong, do not use

- The first state/seed tables listed tasks 2 and 3 as "slice 1". They are separate work units:
  task 2 is slice 2, task 3 is slice 3.

## Code to touch

| File | Change |
|---|---|
| `cmd/bm42/main.go` | Accept a ROM name positionally, resolve it to a binary, exec it, forward its exit status |
| `go.mod` | Unchanged unless a dependency is genuinely required; the slice starts with none |

## Read these first, and only these

- No specs exist yet. `docs/donot.md` is the only standing reference.

## Do-Not entries that apply here

Total count: 2. Both apply.

- **1** — a bare `go build` / `go vet` examines nothing at the module root; use `./...`.
- **2** — a seed without a `PLAN.md` row and `reads:` is refused; price the row before writing the seed.

## The gate

```
go build ./...
go vet ./...
```

## When this slice closes

Complete task 2 in `docs/STATE.md`, advance the next action to task 3, append any new fault
to `docs/donot.md` after the last entry, write the seed for task 3, and re-verify the Do-Not
count only went up.
