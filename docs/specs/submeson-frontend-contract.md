---
description: How a frontend registers and launches SubMeson — the passthrough contract
read_if: Working on SubMeson's CLI surface, ROM execution, or frontend integration
---

# SubMeson frontend contract

SubMeson is a passthrough, not an emulator with a ROM registry. The frontend owns the
ROM-to-emulator mapping; SubMeson is the emulator it maps to.

Three facts are all a frontend needs to register SubMeson:

| Fact | Answer |
|---|---|
| What the emulator is | `SubMeson` — Bambleweeny-42; version from `-v` / `--version` |
| Extensions it requires | none — it accepts any path it is handed |
| Launch syntax | `SubMeson <path-to-rom>` |

SubMeson executes the path it is given and forwards the exit status. The distributable
macOS bundle is `dist/SubMeson.app` (`dist/SubMeson.dmg`); launch the binary
(`SubMeson <path-to-rom>`, e.g. `dist/SubMeson.app/Contents/MacOS/SubMeson`) for exact
exit-status forwarding. The bundle form (`open -W SubMeson.app --args <path-to-rom>`) waits
for GUI apps but cannot reliably capture instant-exit CLI children.

## Invariants

- No internal ROM registry and no name lookup. The frontend decides which ROMs map to SubMeson.
- No extension filter. The suffix is the frontend's concern, not SubMeson's.
- The ROM is a positional path argument; SubMeson does not rewrite it before execution.
- The exit status of the executed process is SubMeson's exit status.
- Bundle paths (`.app` directories) are launched via `open -W`, because `exec` cannot run a bundle directory; the path itself is not rewritten.

How a frontend obtains the three facts — its own config, a manifest, or a person reading
the usage text — is the frontend's integration choice. SubMeson's surface is the three facts.
