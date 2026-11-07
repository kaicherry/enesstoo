---
description: Slice budget table — the priced reading set and allowance for each work unit
read_if: Cutting a slice, writing a seed, or checking whether a seed's reading set is priced
---

# Slice Plan

Each row prices one work unit: the files its brief reads, plus the working allowance.
A seed may name only the files its row prices. A file that belongs in the set means a new
row here first, never a wider seed.

| Slice | Reads | Allowance |
|---|---|---|
| 1 | docs/slices/NEXT.md, docs/donot.md | 6000 |
| 2 | docs/slices/NEXT.md, docs/donot.md, cmd/bm42/main.go, go.mod, docs/specs/bm42-frontend-contract.md | 12000 |

Later slices get their own row when they are cut. A row is priced against files that exist,
so the row for slice 3 lands after slice 2 settles the ROM mapping.
