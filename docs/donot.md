---
description: Do-Not list — faults already paid for in this project's history
read_if: Working on any slice or task; never drop or trim entries
---

# Do-Not List

Entries are append-only; never dropped, never trimmed.

1. **Do not trust a bare `go build` / `go vet` as a gate — it examines nothing at the module root.** The root package has no `.go` files, so both exit 1 with `no Go files in <root>`, which is a check that ran over nothing and is not a pass. Use `go build ./...` and `go vet ./...`, which is now what `gateCommands` carries.

2. **Do not write or accept a seed without a matching `PLAN.md` row and a `reads:` list.** The first seed arrived with neither, so the budget checker refused it with exit 3 and the slice spent its opening on a re-cut. Every seed names only files its row prices; a file that belongs in the set means a new plan row first.

3. **Do not build a ROM registry, name lookup, or extension filter into bm42 — the frontend owns the ROM-to-emulator mapping.** bm42 is a passthrough: it executes the path it is handed and forwards the exit status. A registry was invented once from the phrase "lookup + execute" and cost a design correction; the contract is `docs/specs/bm42-frontend-contract.md`.
