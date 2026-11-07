---
slice: 2
stateFile: docs/STATE.md
donotCount: 3
seededFrom: 40cc398
reads:
  - docs/slices/NEXT.md
  - docs/donot.md
  - cmd/bm42/main.go
  - go.mod
  - docs/specs/bm42-frontend-contract.md
allowanceTokens: 12000
description: Seed for EnessToo slice 2 — ROM passthrough
read_if: Running /babysteps-slice for task 2
---

# Task 2: ROM passthrough (execute)

## The next action

**Task 2: ROM passthrough (execute)** — `bm42 <path-to-rom>` executes the path it is
handed as a child process and forwards its exit status. There is no registry and no
extension filter: the frontend owns the ROM-to-emulator mapping. The frontend-facing
facts are identity (`-v` / `--version`), extensions (none required), and launch syntax
(`bm42 <path-to-rom>`); see `docs/specs/bm42-frontend-contract.md`. Gate:
`go build ./...` + `go vet ./...`.

**Closes when:** `go build ./...` and `go vet ./...` are green, task 2 is marked complete
in `docs/STATE.md`, and the next seed is written and passes
`babysteps-budget --seed docs/slices/NEXT.md`. The queue ends at task 2, so if no new
task has been defined, the next seed records the next action as **unknown**.

## What is settled — do not re-derive

- bm42 is a **passthrough**. The frontend maps ROMs to bm42; bm42 runs the path it is given.
  There is no internal registry, no name lookup, and no extension filter.
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

- The first state/seed tables listed tasks 2 and 3 as "slice 1". They are separate work units.
- "The ROM mapping source is undecided" was wrong: the frontend owns the mapping. Do not
  build a registry, a name-to-binary lookup, or a config reader for one.

## Code to touch

| File | Change |
|---|---|
| `cmd/bm42/main.go` | Take the ROM path positionally, execute it as a child process, forward its exit status; update `usageText` to `bm42 [flags] <path-to-rom>` |
| `go.mod` | Unchanged unless a dependency is genuinely required; the slice starts with none |

## Read these first, and only these

- `docs/specs/bm42-frontend-contract.md` — the three frontend facts and the invariants.

## Do-Not entries that apply here

Total count: 3. All apply.

- **1** — a bare `go build` / `go vet` examines nothing at the module root; use `./...`.
- **2** — a seed without a `PLAN.md` row and `reads:` is refused; price the row before writing the seed.
- **3** — do not build a ROM registry, name lookup, or extension filter; the frontend owns the mapping.

## The gate

```
go build ./...
go vet ./...
```

## When this slice closes

Complete task 2 in `docs/STATE.md`, advance the next action, append any new fault to
`docs/donot.md` after the last entry, write the next seed, and re-verify the Do-Not count
only went up. The queue ends at task 2: if no new task is defined, the next seed must say
the next action is unknown rather than inventing one.
