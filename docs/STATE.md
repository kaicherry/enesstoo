---
description: Work-unit state for EnessToo — Bambleweeny-42 emulator proxy
read_if: Working on any slice or task
---

# EnessToo — Work State

## Where the work is

EnessToo is a greenfield Go CLI utility that acts as an emulator proxy / passthrough launcher. It treats real applications and binaries as "ROMs" in a virtual console called **Bambleweeny-42** (**SubMeson**, formerly `bm42`). The Go service executes the ROM path it is handed — it does not manage ROM registries, metadata, or displays; those are handled by frontends. The darwin distributable is `dist/SubMeson.app` (`dist/SubMeson.dmg`).

## The next action

**SubMeson `.app` + DMG test bundle (this change).** Renamed `bm42` → `SubMeson` (`cmd/bm42/main.go` → `cmd/SubMeson/main.go`, launch syntax `SubMeson <path-to-rom>`) and added `packaging/darwin/Info.plist` + `scripts/build-darwin-app.sh` producing `dist/SubMeson.app` / `dist/SubMeson.dmg` that run as-is (unsigned test bundle; sign/notarize/staple next, then an optional `Open…` dialog). The queue ended at task 2, which is complete and committed (`84050f4`). SubMeson satisfies the three frontend facts in `docs/specs/submeson-frontend-contract.md`: identity from `-v` / `--version`, no required extension, and `SubMeson <path-to-rom>` executing the path and forwarding its exit status. Task 3 was dropped as a contract violation, so defining the next task is the operator's decision — do not invent one from the passthrough contract.

**The Do-Not list is `docs/donot.md`** — 3 entries, append-only. Never dropped, never trimmed.

## Task queue

### Completed
| ID | Task | Gate | Notes |
|---|---|---|---|
| 1 | Go module initialization + binary skeleton | `go build ./...` + `go vet ./...` | `go.mod` (github.com/kaicherry/enesstoo, go 1.22) and `cmd/SubMeson/main.go` (was `cmd/bm42/main.go` before rename); version `dev`, overridable with `-ldflags "-X main.version=<tag>"` |
| 2 | ROM passthrough (execute) | `go build ./...` + `go vet ./...` | `run` takes the first positional as the ROM path, `launch` execs it verbatim with inherited stdio (`.app` bundles via `open -W`), and the child's exit status becomes SubMeson's; no ROM, a second positional, and an unknown flag exit 2, an unexecutable path exits 1. Commit `84050f4` |

### In progress
*(none)*

### Queued
*(none — the next task is undefined)*

Task 3 (ROM registry config file reading) is **dropped** — it contradicts the passthrough
contract. The queue ends at task 2; the next task is unknown until the operator defines it.
