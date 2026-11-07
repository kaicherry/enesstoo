---
description: Execute the next work unit end to end — brief, work, gate, commit, advance state
agent: build
subagent: false
---

Read `.babysteps/config.json` once. Keys used below: `stateFile` (default `docs/STATE.md`),
`workBudgetTokens` (default null — the planned work-unit budget; falls back to the ceiling),
`contextCeilingTokens` (default 150000), `modelContextLimit` (default null),
`costCeilingUSD` (optional; the per-session USD ceiling, unset disables the cost check),
`codeIndexTool` (default `jcodemunch`), `gateCommands`, `runCommand`,
`rebuildBoundaryPath` (single path) or `reboundaryPaths` (array, preferred), `scratchDir` (default
`localTmp/`). Either boundary spelling is accepted; the array exists because a project can be ported
from more than one predecessor.

The **seed** is `docs/slices/NEXT.md`, beside the state file if `stateFile` is configured
elsewhere. It is the only file the brief reads.

**Scratch goes in the project, never the system temp directory.** Every scratch file — a dump,
a capture, a build log, a probe script — is written under the configured `scratchDir`
(`localTmp/` by default), or under `externalTmp/` when it must outlive the project.
`/tmp`, `/private/tmp` and `$TMPDIR` are not scratch: a file there is invisible to the project,
swept by the OS, and outside the tree the next session rebuilds.

**Say each step before you do it.** One line, naming the step and what it waits on. The brief
subagent takes a minute or more and shows nothing; a gate command takes as long as the build.
A run that goes quiet looks like a hung run, and on screen there is no other signal — a live
step and a dead one are the same picture. This is the only progress display there is.

**Publish the steps as todos.** If the `todowrite` tool is in your tool list, call it once with
one todo per step of this command — Flags, Budget, Brief, Title, Index, Work, Gate, Boundary,
Commit, Scratch, Re-index, End — the first `in_progress` and the rest `pending`, and then keep
it current: mark a step `completed` when it is done and the next one `in_progress`. When the
brief comes back, put the slice's own next action in the Work todo, so the list says what the
slice is and not only that it runs. The operator reads that list in the sidebar, so it must not
lie — a step that did not happen is not `completed`, and a step that is running is not
`pending`. If the tool is not in your tool list, skip this: it is a display, not a step.

**0 — Flags.** The flags are the trailing tokens at the very end of this message, after all
the command text. They are **not** the same word appearing inside the command body above — those
occurrences are documentation and must not be read as flags. Read only the tokens at the end:

- `--bigBoy` → set BIGBOY.
- `--auto-chain` or `--chain` → set AUTOCHAIN.

A flag counts only when it is a standalone token at the end of the message. If the message ends
with `--auto-chain`, AUTOCHAIN **is** set even though the word also appears earlier in this
text. Only a message whose trailing tokens contain neither word means neither flag is set. Do
not report a flag absent just because it is not the last token you looked at.

**1 — Budget.** The work-unit budget is `workBudgetTokens` when set, else
`contextCeilingTokens`; `contextCeilingTokens` is also the hard ceiling.
`budget = min(workBudgetTokens ?? contextCeilingTokens, contextCeilingTokens,
modelContextLimit ?? ∞)`. Under `--bigBoy`, drop the work-unit budget and say so.

The token budget and the cost ceiling are separate limits. When `costCeilingUSD` is set, the
binary guard also checks the session's own recorded USD cost; at 95% of the ceiling it stops the
slice. The cost is the session total, including charges not present on individual messages, but
not separate subagent sessions. The `--cost-ceiling` flag overrides the configured amount for one
guard invocation.

**The verdict below is code, and it is settled — do not re-derive it.** It has already run;
treat its output as measured input, not a suggestion:

!`.babysteps/bin/babysteps-budget --enforce --root "$PWD" 2>/dev/null || echo '{"error":"budget check unavailable — the suite binary is not installed; compute the budget from the formula above and treat it as binding"}'`

`bindingBudget` is the number the work is sized to; `rule` is the constraint, and the rule is
the whole point: **the work-unit budget binds regardless of host headroom.** A model or provider
that offers more context does not raise the budget, and headroom above it is not spendable — the
work must still fit if it is later transferred off the cloud model to a smaller one. When
`budgetBinds` is true, size the work to `bindingBudget` and ignore the host window however large
it is; a slice too large for the budget is a **slicing fault** — cut it into smaller work units,
never spend the headroom. State the binding number and the key that set it once, in one line. If
the check could not run, compute `budget` from the formula above and treat it as binding the same
way.

**The seed is the priced reading set, and it is verified before any work starts.** The seed's
frontmatter declares the reading set its plan row prices; the two must agree. Run:

```
.babysteps/bin/babysteps-budget --seed docs/slices/NEXT.md
```

The checker resolves the plan from the project's `planFile` config key, then the tool's default —
a plan it cannot parse is a refusal, not a pass.

- Exit **0** — the seed names only files its row prices and the row fits the budget. Proceed.
- Exit **4** — the seed names a file its row does not price. **Stop here.** Report the unpriced
  paths and re-cut the seed or re-cut the plan row; never widen the seed to fit the file.
- Exit **2** — the seed cannot be priced at all: no budget table, no row for its slice, or no
  `reads:` in its frontmatter. **Stop here.** An unpriced seed is the fault this gate exists to
  refuse, not a cheap slice.

**A seed that does not pass is a slicing fault, and the work is to re-cut it — not to do it.** Do
not begin, do not "make a start while deciding", and do not treat a missing checker as a pass.
Measured on miniD, 2026-10-23: a row priced 68k while its seed named ~122k, and the session spent
`input 180,034 / cache_read 17,556,352` against a 170,000 budget. The budget was a number in a
document and nothing enforced it. This check is the enforcement.

`contextCeilingTokens` is the work-unit budget; it does not configure the model host. The host
limit is separate and may be higher than `ceiling`. Verify the active model's host limit against
`modelContextLimit`, plus its compaction buffer; leave room for fixed prompt/tool context and
closeout. Under `--bigBoy`, the work-unit budget is dropped, but the host limit still applies.
In OpenCode, inspect `opencode api get /api/model --header "x-opencode-directory:$(pwd)"` and
verify `providers.<provider>.models.<model>.limit.context` for the selected model; the directory
header matters when the background service is focused elsewhere. Do not set the host `limit.context`
equal to a smaller work-unit budget merely to enforce slice size: compacting is not a substitute
for splitting the work. For another harness, verify its equivalent native setting. If the host
limit or reserve cannot be verified, **stop and ask before work**. Do not change a project's host
configuration without operator approval.

**2 — Brief.** Do not read the state file yourself.

Say the step first: `Getting the brief — a subagent is reading docs/slices/NEXT.md and the specs it
names. Nothing appears until it returns; it can take a minute or more.` Then call the **subagent
tool** — the one in your own tool list whose job is running another agent.

**It is not in the Code Mode catalog, and its absence there means nothing.** If you are in
Code Mode, the catalog you can see lists *MCP servers only* — not `subagent`, not `read`, not
`shell`, not `write`. Those are top-level tools. Do not conclude a top-level tool is missing
because the catalog omits it.

**It is not a program.** It has no path, it is not in `$PATH`, and `which`, `type`, `find /` and
`compgen` will never find it. If your tool list contains a tool for launching a subagent or task,
that is the one.

Its fields describe the same three things regardless of what the harness calls them: which
agent to use (`general`), a short label (`brief`), and the prompt below. Use the field names
your tool actually documents.

Call it directly as its own tool call — **not from inside `execute`**, which can only reach
the MCP catalog. Call it once and wait for the reply. Do not issue another brief call while it is
running, even if a message is queued or the UI looks idle. If it remains pending for two minutes,
report that it is still pending and stop; do not retry without operator approval.

**A second call is refused, not queued.** While a brief is in flight, a request for another one
is answered `brief in flight — not calling again`, and that is the whole answer: do not issue the
call, do not rephrase the prompt to obtain a different second one. Only the call already in flight produces the brief.

**You do not know the next task yet — that is what this step is for.** Calling the tool is the
action; the next task is its output. Do not work it out first.

Prompt:

```
You are a subagent. Your only job is to read and report — do not edit anything.

Read <seed path> in full. It is the whole brief. Then read the specs it names under
"Read these first, and only these", and the Do-Not entries it cites by number from
docs/donot.md. Nothing else.

Do NOT read the state file. The seed has already copied the next action out of it.

`read` is a top-level tool: it is NOT inside the Code Mode `execute` catalog, so `tools.read`
and `read({...})` inside execute both fail with "Unknown tool". If `read` appears unavailable,
use `shell` with `cat` instead and carry on — do not spend turns searching for a tool.

Report back tersely, and nothing else:
1. The next action paragraph, verbatim, and the closes-when line.
2. The code-to-touch table, unchanged.
3. The gate commands, and this slice's own close.
4. From the named specs, the path and the section name only — do **not** quote paragraphs; the main session reads them on demand. Quote the numbers.
5. The withdrawn numbers, so they are not re-measured as if new.
6. The Do-Not entries that apply, by number only — do **not** quote the entry body; the main session reads them on demand.

Do not summarise the whole handoff. Do not include history or prior write-ups. Six items is the
whole reply.
```

Substitute the configured seed path (default `docs/slices/NEXT.md`) for `<seed path>` everywhere above.

**Before concluding you have no subagent tool, look at your tool list.** Do not report it
missing without having checked. Claiming a tool is absent when it is not is a failure, not a
shortcut — it stops the run for no reason, and it is the failure this paragraph exists to
stop. If you genuinely have no such tool, stop and say so.

If the seed is missing or empty: stop and say `No docs/slices/NEXT.md — run /babysteps-handoff
first.` Do **not** fall back to the state file: the brief that re-derives the next action from
thousands of lines is the problem the seed exists to remove, and taking the fallback silently
restores it.

**3 — Title.** Rename this session to the task the brief named. Keep the session id the rename
returns — step 11 needs it to name the model this session is running under.

**Renaming your session**

**The correct way to rename the session is via `execute` calling `tools.opencode.session_rename`:**

    tools.opencode.session_rename({ title: "session title here" })

This returns `{ sessionID: "...", title: "..." }`. Take the session ID from the
response — it is needed by later steps (budget guards, auto-chain model pinning).

Not `opencode api …`, not a shell command, not a tool that starts with `opencode.` as a
top-level tool name. The `opencode.` prefix only works inside `execute`.

**4 — Index.** `resolve_repo({ path: <repo root> })`. `indexed: false` → `index_folder`.
Stale versus the last commit → `index_folder({ incremental: true })`. Explore with
`codeIndexTool`; if that is `jcodemunch`, read `babysteps-exploration.md` first.

**5 — Work.** Do the one task. Size it to `bindingBudget` from step 1 — the work-unit budget,
not the host window. One commit per coherent change. Never leave the tree unbuildable between
commits. A task that does not fit `bindingBudget` is mis-sliced: split it into smaller work
units, never exceed the budget by spending host headroom.

`--auto-chain` starts a fresh session and resets context between work units. It does not cap context within a work unit. The host limit checked in step 1 bounds active context during that work unit.

**The budget is re-measured at every commit boundary, because a seed that starts priced can drift.** After each commit, before starting the next change, run:

```
.babysteps/bin/babysteps-budget --guard --session <this session's id>
```

- **within** — carry on.
- **near** (default 80%) — finish the change in hand, commit it green, write the next seed, and
  close the unit. Compacting is insurance, not a licence to carry on.
- **exhausted** (exit **5**) — **stop now.** Commit what is green, write the next seed, stop.
  This means the main-context budget is exhausted or the session's recorded cost reached 95% of
  `costCeilingUSD`. Do not spend the headroom and do not start a change you cannot finish inside
  the unit.
- **unmeasured** (exit **2**) — the session store could not be read or no session was named.
  **Stop and report.** An unmeasured guard is not a pass, and a guard that passes when it cannot
  see is the same defect as a budget nothing enforces.

The session id is the one the rename in step 3 returned. It gates on peak main context, not cumulative cache reads:
`input + cacheRead` for one turn, including compaction turns. Cache reads never sum across turns.
The cost check uses the session's recorded total and runs at this same commit boundary; it does
not interrupt a turn already in progress.

**Do not wait for the guard to fire.** A unit that is going to need more than its budget is a
slicing fault: stop at the next commit boundary and cut the remainder into a new unit. Session-wide
input and cache-read totals measure repeated traffic, not main context; they do not drive this gate.

**6 — Gate.** Name the check and that it is running, then run it: `Gate 1 of 3 — <command>.`
Each of these is as slow as the thing it builds. Run every `gateCommands` entry, each with its
own exit status. A check that examined nothing is not a pass. Report each separately with real
output; end with `all green` or `red on <check>`.

**7 — Boundary.** Only when `reboundaryPaths` / `rebuildBoundaryPath` is non-empty. It is scoped to
**this slice's diff** and asks one thing: did the slice link, call, or resolve into anything
outside the boundary? Report the two checks — linkage, paths — separately, with `file:line`, and
state any check you could not run as **not run** rather than as a pass. A pre-existing finding is
not this slice's to re-report. See `babysteps-boundary.md`.

**8 — Commit,** then advance the three files from the brief: complete the task and advance "next
action" in the state file, append any new fault to `docs/donot.md` **after the last existing
entry**, and verify the count only went up and the last entry before it is unchanged.

**Then write the next seed.** `docs/slices/NEXT.md` is rewritten from what this slice left behind —
the next action verbatim, what is now settled, what is withdrawn, the code it touches, the specs it
needs, and the Do-Not subset cited by number. **Under 120 lines.** A seed left stale is worse than
none: the next session reads it and believes it. If the next task is not yet known, write that it is
unknown rather than leaving the previous slice's seed in place.

The seed is a *filtered copy*: it never becomes the source of truth for anything. The write-ups stay
in the state file and the faults stay in `docs/donot.md`.

**A slice is not closed until the seed for the one after it exists.**

**9 — Scratch.** Produce the removal list per `babysteps-workflow.md` § Scratch. Do not delete
anything.

**10 — Re-index** incrementally. After the last commit, never before.

**11 — End.**
- `--auto-chain` and work remains → run the continuation in the foreground, then stop when it
  returns. This creates a fresh OpenCode session, but the visible shell call stays active while it
  runs. `opencode run` must run in the foreground through the shell tool; the shell tool remains
  active and its output is visible until the chain completes. **Do not use `nohup`, detach it, or
  redirect it to a log file.** The child stays attached to the same stdout; running it as a job of
  the foreground shell is fine, because the shell call still waits for it and still shows its output.

  Pin the model with `--model`, to **the model this session is running under**, as
  `provider/model#variant`. Left unpinned, `opencode run` picks its own default, which can be
  a model that cannot call a top-level tool — and then the chain fails at the only point
  where the chain matters. The **session record** names that model; the config does not. The
  global config names the harness default, which is frequently a different model, and a chain
  that inherits it silently changes model mid-run. Read the model from the session record
  (`opencode api get /api/session/<id>` → `model.providerID`, `model.id`, `model.variant`);
  step 3's rename response carries the session id. Fall back to OpenCode's own config only
  when the session record does not answer.

  **The visible signal must not depend on what the child chooses to print.** The child is
  silent through the phases that take longest — a brief subagent, a gate run — so a child that
  prints only when it has something to say leaves the screen identical to a dead one. The parent
  renders the child's JSON event stream, reports bounded pending states, and prints its own
  heartbeat while the child lives. The monitor says it has stopped asking and waits for an event
  after the last bounded pending report. The child runs one slice only; the parent owns
  continuation.

  **Interrupting the chain call is not a stop.** The child survives an interrupted parent and
  keeps working. An interrupted chain call means the chain may still be running: report that
  first, and check the commits and the session list before calling the work stopped.

  **A chain worker looks idle in the session list, and it is not.** OpenCode's TUI does not mark
  a session with an in-flight turn, so a running session renders exactly like a finished one.
  That invites the operator to type into a worker mid-turn, and the message lands inside the
  running turn instead of starting a new one. The server knows: `opencode api get
  /api/session/active` lists every running session as `{"type": "running"}`. Never type into a
  session that looks idle — check that list first, and treat a session in it as untouchable.

  **Send the command body, not the command name.** `opencode run` does not expand a slash
  command — it hands the string to the model as an ordinary prompt. A spawn that passes
  `/babysteps-slice --auto-chain` therefore opens a session containing *no steps at all*, and
  the model invents its own. Verified on miniD: the typed run's first user message is the
  7.4KB body of this file, the chained run's is the 33-byte string `"/babysteps-slice
  --auto-chaine"`. Everything downstream of that — a brief that never returns, a model that
  wanders — is the chain running with no instructions in it. The launcher below sends this
  file's body, not the command name, and does not append `--auto-chain` to the child: the parent
  loop owns the next spawn.

  Read this command's own installed file, strip its frontmatter, and send the rest:

  ```
  root=$(pwd)
  cmd=$root/.opencode/commands/babysteps-slice.md     # this command's installed file
  [ -r "$cmd" ] || cmd=$root/.claude/commands/babysteps-slice.md
  [ -r "$cmd" ] || cmd=$root/.codex/prompts/babysteps-slice.md
  body=$(awk 'NR==1&&/^---$/{f=1;next} f&&/^---$/{f=0;next} !f' "$cmd")
  # Name this session's model from the session record, not from the config. The config names
  # the harness default, which is often a different model from the one running this session.
  session=${BABYSTEPS_SESSION_ID:-}
  if [ -z "$session" ]; then
    session=$(opencode api get /api/session --header "x-opencode-directory:$(pwd)" 2>/dev/null | python3 -c '
import sys, json, os
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
here = os.getcwd()
rows = [r for r in (data.get("data") or data.get("sessions") or [])
        if (r.get("time") or {}).get("created")
        and not r.get("parentID")
        and (r.get("location") or {}).get("directory") == here]
rows.sort(key=lambda r: r["time"]["created"])
print(rows[-1]["id"] if rows else "")
')
  fi
  model=$(opencode api get "/api/session/$session" --header "x-opencode-directory:$(pwd)" 2>/dev/null | python3 -c '
import sys, json
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
m = (data.get("data") or data).get("model") or {}
provider, model_id, variant = m.get("providerID"), m.get("id"), m.get("variant")
if provider and model_id:
    print(f"{provider}/{model_id}" + (f"#{variant}" if variant else ""))
')
  # OpenCode's own config is the fallback, never .babysteps/config.json.
  [ -z "$model" ] && model=$(printf '%s' "${OPENCODE_CONFIG_CONTENT:-}" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("model",""))' 2>/dev/null)
  [ -z "$model" ] && model=$(python3 -c 'import json,os;print(json.load(open(os.path.join(os.environ.get("PWD","."), ".opencode", "opencode.json"))).get("model",""))' 2>/dev/null)
  [ -z "$model" ] && model=$(python3 -c 'import json,os; print(json.load(open(os.path.expanduser("~/.config/opencode/opencode.json"))).get("model",""))' 2>/dev/null)
  watcher=$root/.opencode/commands/babysteps-chain-watch.py
  [ -r "$watcher" ] || watcher=$root/.babysteps/bin/babysteps-chain-watch.py
  if [ -n "$model" ]; then
    echo "Auto-chain running in foreground — parent owns continuation; model $model."
    echo "A running session looks idle in the session list — check 'opencode api get /api/session/active' before typing into any session."
    stop_after=${BABYSTEPS_STOP_AFTER_SLICE:-0}
    while :; do
      slice=$(awk '$1 == "slice:" {print $2; exit}' "$root/docs/slices/NEXT.md")
      [ -n "$slice" ] || { echo "cannot name the current slice — not spawning"; exit 4; }
      events=$root/localTmp/chain-events-$slice.jsonl
      before=$root/localTmp/chain-seed-before-$slice.sha256
      shasum "$root/docs/slices/NEXT.md" > "$before"
      rm -f "$events" "$events.done"
      echo "[chain] starting $slice; events: $events"
      if [ -r "$watcher" ]; then
        opencode run --auto --agent build --model "$model" --format json \
          --title "$slice" "$body" > "$events" 2>&1 &
        child=$!
        python3 "$watcher" --follow "$events" &
        renderer=$!
      else
        echo "No chain watcher at $watcher — child output stays on this terminal"
        opencode run --auto --agent build --model "$model" --title "$slice" "$body" &
        child=$!
        renderer=
      fi
      start=$(date +%s)
      while kill -0 "$child" 2>/dev/null; do
        sleep 30
        kill -0 "$child" 2>/dev/null && echo "[chain] still running — $(( $(date +%s) - start ))s elapsed"
      done
      wait "$child"; exit_code=$?
      if [ -n "$renderer" ]; then
        touch "$events.done"
        wait "$renderer" 2>/dev/null
      fi
      echo "[chain] $slice exited with status $exit_code."
      [ "$exit_code" -eq 0 ] || exit "$exit_code"
      after=$root/localTmp/chain-seed-after-$slice.sha256
      shasum "$root/docs/slices/NEXT.md" > "$after"
      if cmp -s "$before" "$after"; then
        echo "[chain] $slice did not advance the seed — stopping before a duplicate slice"
        exit 5
      fi
      [ "$stop_after" = "1" ] && { echo "[chain] stop-after-slice requested — not spawning the next slice"; exit 0; }
      echo "[chain] $slice closed — starting the next seeded slice"
    done
  else
    echo "cannot name this session's model — not spawning"
  fi
  ```

  The flag goes on its own line at the end because step 0 reads flags from the trailing
  tokens of the message. Putting it on its own line keeps it a distinct token, separate
  from the prose above that also contains the word. `BABYSTEPS_STOP_AFTER_SLICE=1` stops the
  parent after the current child closes; it is checked only after the commit, seed advance and
  clean child exit, so it cannot interrupt a slice mid-turn.

  This is inherited, not configured: the model that just did the work is the model that
  continues, and the user is asked nothing. Do not read a model out of `.babysteps/config.json`
  — there is no model setting there, and there must not become one. The session record is the
  source, because it names the model this session is actually running under; OpenCode's own
  config names the harness default, which is frequently a different model.

  If this session's model cannot be named, **stop and say so and do not spawn**. An unpinned
  process picks a model you did not choose and fails silently, which is indistinguishable
  from not chaining at all.

  The parent shell call remains active while the child and its later continuations run. When it
  returns, report the final exit status; do not report the chain as finished earlier. If the
  call is interrupted rather than returning, the child may still be running: say so, and check
  the commits and the session list before reporting the work stopped.
- `--bigBoy` → repeat from step 1.
- Otherwise → `The handoff is ready — type /clear to start a new session, and /babysteps-slice in the new one to resume working.`

On `--auto-chain`, the command *name* the user typed is not what gets spawned. The name says
which file to send; that file's contents are the message. Copy the user's form only to
identify the file — never to hand the next session a string it cannot act on.

**Stop and report only when:** the task is genuinely gated (needs a decision only a person can
make), the queue is exhausted, or something is truly blocking after a two-minute timer during
which you keep working. A finished task is not a stop condition — it is the next iteration.

  Rationale, worked examples, and per-case detail: `babysteps-workflow.md`. It sits in the
  same directory as this file — that is where every reference file is. If one is not there,
  carry on without it. Do not search the filesystem for a missing reference file: a bare name
  that no longer matches its installed filename turns one `ls` into four turns of `find /`,
  and the run dies before step 2.

**Invocation arguments:** $ARGUMENTS
