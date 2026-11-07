---
description: How a frontend registers and launches bm42 — the passthrough contract
read_if: Working on bm42's CLI surface, ROM execution, or frontend integration
---

# bm42 frontend contract

bm42 is a passthrough, not an emulator with a ROM registry. The frontend owns the
ROM-to-emulator mapping; bm42 is the emulator it maps to.

Three facts are all a frontend needs to register bm42:

| Fact | Answer |
|---|---|
| What the emulator is | `bm42` — Bambleweeny-42; version from `-v` / `--version` |
| Extensions it requires | none — it accepts any path it is handed |
| Launch syntax | `bm42 <path-to-rom>` |

bm42 executes the path it is given and forwards the exit status.

## Invariants

- No internal ROM registry and no name lookup. The frontend decides which ROMs map to bm42.
- No extension filter. The suffix is the frontend's concern, not bm42's.
- The ROM is a positional path argument; bm42 does not rewrite it before execution.
- The exit status of the executed process is bm42's exit status.

How a frontend obtains the three facts — its own config, a manifest, or a person reading
the usage text — is the frontend's integration choice. bm42's surface is the three facts.
