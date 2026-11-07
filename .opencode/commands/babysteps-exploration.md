# Code exploration reference

Read this **only when you are about to explore code with jcodemunch** — not on every
`/slice`. The full policy table and the cases where jcodemunch is the wrong tool live in
`~/.config/opencode/AGENTS.md` § Code Exploration Policy.

## MCP servers, not tools

These are MCP servers. They are **not** tools you invoke, and there is no `mcp` path you can
call with a server name:

- duckduckgo-mcp
- jcodemunch
- memory-mcp
- rea
- sequential-thinking

## Call discipline

- One budgeted `get_ranked_context({ repo, query, token_budget })` per behavioural question —
  never a hand-chained `search_symbols` → `get_symbol_source` → `get_context_bundle`.
- Batch independent calls in one `Promise.all`.
- `check_references` for "where is X used". `find_references` is the import graph only and
  reports zero for a single-file target.
- `resolve_repo({ path })` first; take the returned `repo` name. `indexed: false` →
  `index_folder`. An index older than the last commit answers confidently about deleted code.
- Markdown and JSON go through `read`; anything you must run goes through `shell`.
  *Never fall back for code exploration* — that is not *never read anything*.

## When a call errors

**The error text is the correction.** It names the missing key and usually prints a corrected
argument block. Fix the call from it. Do not reach for a workaround — rephrasing the query,
dropping to `grep`, re-reading with `read`, or switching tools — because that discards the
correction and leaves the index wrong.

Corrections seen in practice, as *sent → said → send instead*:

1. `get_symbol_source({ symbol_id, verify: false })` → `repo: Missing key` → add `repo`.
2. `execute` block starting with `#` or a blank line → `Unexpected character ' ' (1:1)` →
   put the call first, no leading comment.
3. `require('fs')` inside Code Mode → `ReferenceError: Unknown identifier 'require'` → use
   the top-level `write` tool.
4. `tools.shell(...)` inside Code Mode → `Unknown tool 'shell'` → `shell` is top-level only.
5. `search_text(...).results[0].matches` on a different result shape →
   `Cannot read properties of undefined` → guard it, or use `get_symbol_source`.
6. Response truncated with `#MUNCH/1 tool=... enc=rc1` → lower `token_budget` and re-query.
   Truncated output that reads like a complete answer is worse than none.
7. Response contradicts visible evidence → re-verify with `resolve_repo` and a fresh
   `index_folder`.

## Not every project uses jcodemunch

`codeIndexTool` in `.babysteps/config.json` names the project's tool. If it is not
`jcodemunch`, use that instead — the guidance above does not apply. The general rule stands
either way: never fall back to ad-hoc search *for code exploration*, while still reading
markdown and JSON normally.