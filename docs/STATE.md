---
description: Work-unit state for EnessToo — Bambleweeny-42 emulator proxy
read_if: Working on any slice or task
---

# EnessToo — Work State

## Where the work is

EnessToo is a greenfield Go CLI utility that acts as an emulator proxy / passthrough launcher. It treats real applications and binaries as "ROMs" in a virtual console called **Bambleweeny-42** (bm42). The Go service accepts a ROM name and executes the mapped binary — it does not manage ROM registries, metadata, or displays; those are handled by frontends.

## The next action

**Task 2: ROM passthrough (lookup + execute)** — take a ROM name as a positional argument, resolve it to the binary it maps to, and execute that binary, forwarding its exit status. Gate: `go build ./...` + `go vet ./...`. **Open decision:** the mapping source is not yet specified — Task 3 is registry config reading, so slice 2 must either define the mapping here or wait for Task 3; confirm with the operator before inventing a registry format.

**The Do-Not list is `docs/donot.md`** — 2 entries, append-only. Never dropped, never trimmed.

## Task queue

### Completed
| ID | Task | Gate | Notes |
|---|---|---|---|
| 1 | Go module initialization + binary skeleton | `go build ./...` + `go vet ./...` | `go.mod` (github.com/kaicherry/enesstoo, go 1.22) and `cmd/bm42/main.go`; version `dev`, overridable with `-ldflags "-X main.version=<tag>"` |

### In progress
*(none)*

### Queued
| ID | Task | Slice | Gate | Notes |
|---|---|---|---|---|
| 2 | ROM passthrough (lookup + execute) | 2 | `go build ./...` + `go vet ./...` | mapping source undecided; see next action |
| 3 | ROM registry config file reading | 3 | `go build ./...` + `go vet ./...` | |
