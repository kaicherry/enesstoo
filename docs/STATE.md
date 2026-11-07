---
description: Work-unit state for EnessToo — Bambleweeny-42 emulator proxy
read_if: Working on any slice or task
---

# EnessToo — Work State

## Where the work is

EnessToo is a greenfield Go CLI utility that acts as an emulator proxy / passthrough launcher. It treats real applications and binaries as "ROMs" in a virtual console called **Bambleweeny-42** (bm42). The Go service executes the ROM path it is handed — it does not manage ROM registries, metadata, or displays; those are handled by frontends.

## The next action

**Unknown.** The queue ended at task 2, which is complete and committed (`84050f4`). bm42 now satisfies the three frontend facts in `docs/specs/bm42-frontend-contract.md`: identity from `-v` / `--version`, no required extension, and `bm42 <path-to-rom>` executing the path verbatim and forwarding its exit status. Task 3 was dropped as a contract violation, so defining the next task is the operator's decision — do not invent one from the passthrough contract.

**The Do-Not list is `docs/donot.md`** — 3 entries, append-only. Never dropped, never trimmed.

## Task queue

### Completed
| ID | Task | Gate | Notes |
|---|---|---|---|
| 1 | Go module initialization + binary skeleton | `go build ./...` + `go vet ./...` | `go.mod` (github.com/kaicherry/enesstoo, go 1.22) and `cmd/bm42/main.go`; version `dev`, overridable with `-ldflags "-X main.version=<tag>"` |
| 2 | ROM passthrough (execute) | `go build ./...` + `go vet ./...` | `run` takes the first positional as the ROM path, `launch` execs it verbatim with inherited stdio, and the child's exit status becomes bm42's; no ROM, a second positional, and an unknown flag exit 2, an unexecutable path exits 1. Commit `84050f4` |

### In progress
*(none)*

### Queued
*(none — the next task is undefined)*

Task 3 (ROM registry config file reading) is **dropped** — it contradicts the passthrough
contract. The queue ends at task 2; the next task is unknown until the operator defines it.
