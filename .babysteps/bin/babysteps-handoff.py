#!/usr/bin/env python3
"""Preview a BabySteps handoff update, and write it only on an explicit apply.

The state file and the seed are rewritten whole. The Do-Not list is append-only and is
never rewritten, so the proposal carries only the *new* entries and this tool appends
them: a rewrite of the list is not expressible, not merely discouraged.

  handoff.py preview [--proposal DIR] [--project ROOT]
  handoff.py apply   [--plan PATH]   [--project ROOT]
"""

import argparse
import difflib
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_STATE_FILE = "docs/STATE.md"
DEFAULT_SCRATCH_DIR = "localTmp/"
SEED_LINE_CAP = 120

PROPOSAL_STATE = "STATE.md"
PROPOSAL_SEED = "NEXT.md"
PROPOSAL_DONOT_APPEND = "donot.append.md"

PLAN_VERSION = 1
PLAN_RELATIVE = Path("handoff") / "plan.json"
PROPOSAL_RELATIVE = Path("handoff") / "proposal"

ENTRY_START = re.compile(r"^(\d+)\.\s+")
IDENTIFIER = re.compile(r"[A-Za-z]+[0-9]+(?:\.[0-9]+)*")
DONOT_COUNT_KEYS = ("donotCount", "doNotCount")

STATE_POINTER = "## Where the work is"
STATE_NEXT_ACTION = "## Next action"
STATE_QUEUED = "## Queued"


class HandoffError(Exception):
    """The proposal is not safe to apply."""


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    """Write exactly the given text; no newline translation, so the bytes are the previewed ones."""
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def append_text(path: Path, text: str) -> None:
    with open(path, "a", encoding="utf-8", newline="") as handle:
        handle.write(text)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize(text: str) -> str:
    return " ".join(text.split())


def parse_frontmatter(text: str) -> dict:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return {}
    fields = {}
    for line in lines[1:end]:
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return fields


def section_body(text: str, heading: str):
    """The body of a `## heading` section, or None when the section is absent."""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index + 1
            break
    if start is None:
        return None
    body = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def first_identifier(text: str) -> str:
    match = IDENTIFIER.match(text.strip())
    if match:
        return match.group(0)
    tokens = text.split()
    return tokens[0].strip("—-,.:;()[]") if tokens else ""


def next_action_identifiers(state_text: str) -> dict:
    """The next-action identifier named in each of the three places that must agree."""
    found = {}

    pointer = section_body(state_text, STATE_POINTER)
    if pointer is not None:
        for line in pointer.splitlines():
            if "**The next action** is" in line:
                found["pointer"] = first_identifier(
                    line.split("**The next action** is", 1)[1].strip()
                )
                break

    action = section_body(state_text, STATE_NEXT_ACTION)
    if action is not None:
        for line in action.splitlines():
            if line.strip().startswith("**"):
                found["next-action"] = first_identifier(line.strip().lstrip("*").strip())
                break

    queued = section_body(state_text, STATE_QUEUED)
    if queued is not None:
        for line in queued.splitlines():
            stripped = line.strip()
            if stripped.startswith("- "):
                found["queued"] = first_identifier(stripped[2:].lstrip("*").strip())
                break

    return found


def donot_pointer_count(state_text: str):
    """The entry count the state file's pointer to the Do-Not list claims, or None."""
    for line in state_text.splitlines():
        if "Do-Not list" in line:
            match = re.search(r"(\d+)\s+entr", line)
            if match:
                return int(match.group(1))
    return None


def parse_entries(text: str, source: str) -> list:
    """Numbered entries with their continuation lines; an unindented non-entry is rejected."""
    entries = []
    current = None
    for raw in text.splitlines():
        if not raw.strip():
            continue
        match = ENTRY_START.match(raw)
        if match:
            current = {
                "number": int(match.group(1)),
                "text": raw,
                "body": raw[match.end():],
            }
            entries.append(current)
            continue
        if raw[:1] in (" ", "\t") and current is not None:
            current["text"] += "\n" + raw
            current["body"] += "\n" + raw
            continue
        raise HandoffError(f"{source}: '{raw.strip()[:60]}' is not a numbered entry")
    return entries


def parse_donot(text: str) -> tuple:
    """The framing line and the numbered entries of a Do-Not list."""
    framing = None
    entries = []
    current = None
    for raw in text.splitlines():
        if not raw.strip():
            continue
        match = ENTRY_START.match(raw)
        if match:
            current = {
                "number": int(match.group(1)),
                "text": raw,
                "body": raw[match.end():],
            }
            entries.append(current)
            continue
        if raw[:1] in (" ", "\t") and current is not None:
            current["text"] += "\n" + raw
            current["body"] += "\n" + raw
            continue
        if framing is None and not entries:
            framing = raw
            continue
        raise HandoffError(f"docs/donot.md: '{raw.strip()[:60]}' is not a numbered entry")
    if not entries:
        raise HandoffError("docs/donot.md: no entries")
    return framing, entries


def build_donot(current_text: str, fragment_text: str) -> dict:
    """The appended Do-Not list: the existing file plus the fragment, checked for append-only edits."""
    _, entries = parse_donot(current_text)
    appended = parse_entries(fragment_text, "Do-Not append") if fragment_text.strip() else []

    expected = len(entries) + 1
    for entry in appended:
        if entry["number"] != expected:
            raise HandoffError(
                f"Do-Not append: entry {entry['number']} must be numbered {expected}; the list is never renumbered"
            )
        expected += 1

    # A fault's identity is its first line, so a shortened copy of an entry is still the same fault.
    seen = {normalize(entry["body"].splitlines()[0]) for entry in entries}
    for entry in appended:
        key = normalize(entry["body"].splitlines()[0])
        if key in seen:
            raise HandoffError(
                f"Do-Not append: entry {entry['number']} repeats an entry already in the list"
            )
        seen.add(key)

    if not appended:
        return {
            "text": current_text,
            "append": "",
            "count_before": len(entries),
            "count_after": len(entries),
        }

    body = fragment_text.strip("\n")
    result = current_text if current_text.endswith("\n") else current_text + "\n"
    return {
        "text": result + body + "\n",
        "append": body + "\n",
        "count_before": len(entries),
        "count_after": len(entries) + len(appended),
    }


def check_state(state_text: str, donot_count_after: int, donot_entries: list) -> list:
    """The checks a proposed state file must pass; each returns a (name, ok, detail) line."""
    results = []

    identifiers = next_action_identifiers(state_text)
    missing = [name for name in ("pointer", "next-action", "queued") if name not in identifiers]
    if missing:
        results.append((
            "next action agrees in all three places",
            False,
            "not found: " + ", ".join(missing),
        ))
    else:
        values = set(identifiers.values())
        detail = ", ".join(f"{name}={identifiers[name]}" for name in sorted(identifiers))
        results.append((
            "next action agrees in all three places",
            len(values) == 1,
            detail if len(values) == 1 else detail + " — they disagree",
        ))

    pointer_count = donot_pointer_count(state_text)
    if pointer_count is None:
        results.append((
            "state file points at the Do-Not list with its count",
            True,
            "not run — no pointer line found",
        ))
    else:
        results.append((
            "state file points at the Do-Not list with its count",
            pointer_count == donot_count_after,
            f"pointer says {pointer_count}, list holds {donot_count_after}",
        ))

    inlined = [entry["number"] for entry in donot_entries if entry["text"].splitlines()[0] in state_text]
    results.append((
        "state file does not inline the Do-Not list",
        not inlined,
        "no Do-Not entry appears in the state file"
        if not inlined
        else "entries copied in: " + ", ".join(str(number) for number in inlined),
    ))

    return results


def check_seed_reads(seed_text: str, paths) -> list:
    """The seed's declared reading set must be the one its plan row prices.

    This is what enforces the work-unit budget. Measured on miniD, 2026-10-23: a plan row
    priced 68k while its seed named ~122k, and the session spent `input 180,034 /
    cache_read 17,556,352` against a 170,000 budget because nothing compared the two.

    The plan path is the checker's own business: it reads the project config's `planFile`,
    so this script does not carry a second copy of that path to drift from.
    """
    name = "the seed names only files its plan row prices"
    binary = paths.project / ".babysteps" / "bin" / "babysteps-budget"
    if not binary.is_file():
        return [(name, False, f"no checker at {binary} — an unverified seed is not a passed seed")]

    scratch = paths.scratch
    try:
        scratch.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        return [(name, False, f"cannot use the scratch directory {scratch}: {error}")]

    handle = tempfile.NamedTemporaryFile(
        "w", suffix=".md", prefix="seed-check-", dir=str(scratch), delete=False
    )
    try:
        handle.write(seed_text)
        handle.close()
        proc = subprocess.run(
            [str(binary), "--root", str(paths.project), "--seed", handle.name],
            capture_output=True, text=True,
        )
    finally:
        os.unlink(handle.name)

    detail = (proc.stdout or proc.stderr or "").strip().replace("\n", "; ")
    if proc.returncode == 0:
        return [(name, True, detail)]
    if proc.returncode == 4:
        return [(name, False, "the seed names a file its row does not price — re-cut the seed "
                              f"or the plan row, never widen the seed ({detail})")]
    if proc.returncode == 2:
        return [(name, False, f"the seed cannot be priced, which is the fault this gate refuses ({detail})")]
    return [(name, False, f"the check exited {proc.returncode}: {detail}")]


def check_seed(seed_text: str, donot_count_after: int, paths) -> list:
    """The checks a proposed seed must pass."""
    results = []

    lines = seed_text.splitlines()
    results.append((
        "seed fits the line cap",
        len(lines) <= SEED_LINE_CAP,
        f"{len(lines)} lines (cap {SEED_LINE_CAP})",
    ))

    fields = parse_frontmatter(seed_text)
    missing = [key for key in ("slice", "stateFile", "seededFrom", "reads") if key not in fields]
    if not any(key in fields for key in DONOT_COUNT_KEYS):
        missing.append("donotCount")
    if missing:
        results.append((
            "seed frontmatter names the slice, the state file, the Do-Not count and the reading set",
            False,
            "missing: " + ", ".join(missing),
        ))
    else:
        claimed = None
        for key in DONOT_COUNT_KEYS:
            if key in fields:
                claimed = fields[key]
                break
        try:
            claimed_count = int(claimed)
        except (TypeError, ValueError):
            claimed_count = None
        results.append((
            "seed frontmatter names the slice, the state file, the Do-Not count and the reading set",
            claimed_count == donot_count_after,
            f"seed claims {claimed}, list holds {donot_count_after}",
        ))

    results += check_seed_reads(seed_text, paths)

    return results


def unified(path: str, current_text: str, proposed_text: str) -> str:
    return "".join(difflib.unified_diff(
        current_text.splitlines(keepends=True),
        proposed_text.splitlines(keepends=True),
        fromfile=path,
        tofile=path + " (proposed)",
    ))


class Paths:
    """Where the handoff's files live in one project."""

    def __init__(self, project: Path):
        self.project = project
        config = {}
        config_path = project / ".babysteps" / "config.json"
        if config_path.is_file():
            try:
                config = json.loads(read_text(config_path))
            except json.JSONDecodeError as error:
                raise HandoffError(f"{config_path}: {error}")
        self.state = project / config.get("stateFile", DEFAULT_STATE_FILE)
        self.donot = self.state.parent / "donot.md"
        self.seed = self.state.parent / "slices" / "NEXT.md"
        self.scratch = project / config.get("scratchDir", DEFAULT_SCRATCH_DIR)
        self.plan = self.scratch / PLAN_RELATIVE
        self.proposal = self.scratch / PROPOSAL_RELATIVE


def build_proposal(paths: Paths, proposal_dir: Path) -> dict:
    """Read the proposal and build the three resulting files, or refuse."""
    state_proposal = proposal_dir / PROPOSAL_STATE
    seed_proposal = proposal_dir / PROPOSAL_SEED
    append_proposal = proposal_dir / PROPOSAL_DONOT_APPEND

    for path in (paths.state, paths.donot, paths.seed):
        if not path.is_file():
            raise HandoffError(f"missing {path}")
    for path in (state_proposal, seed_proposal):
        if not path.is_file():
            raise HandoffError(f"missing proposal {path}")

    state_current = read_text(paths.state)
    donot_current = read_text(paths.donot)
    seed_current = read_text(paths.seed)
    state_proposed = read_text(state_proposal)
    seed_proposed = read_text(seed_proposal)
    fragment = read_text(append_proposal) if append_proposal.is_file() else ""

    donot = build_donot(donot_current, fragment)
    _, donot_entries = parse_donot(donot["text"])

    results = check_state(state_proposed, donot["count_after"], donot_entries)
    results += check_seed(seed_proposed, donot["count_after"], paths)

    return {
        "state": {
            "path": str(paths.state.relative_to(paths.project)),
            "current_sha256": digest(state_current),
            "proposed": state_proposed,
        },
        "seed": {
            "path": str(paths.seed.relative_to(paths.project)),
            "current_sha256": digest(seed_current),
            "proposed": seed_proposed,
        },
        "donot": {
            "path": str(paths.donot.relative_to(paths.project)),
            "current_sha256": digest(donot_current),
            "append": donot["append"],
            "text": donot["text"],
        },
        "donot_count_before": donot["count_before"],
        "donot_count_after": donot["count_after"],
        "checks": results,
    }


def print_preview(paths: Paths, proposal: dict) -> None:
    print("BabySteps handoff preview")
    print(f"  state  {proposal['state']['path']}")
    print(f"  seed   {proposal['seed']['path']}")
    print(
        f"  donot  {proposal['donot']['path']} "
        f"({proposal['donot_count_before']} → {proposal['donot_count_after']} entries, append-only)"
    )
    print()

    failures = 0
    print("checks:")
    for name, ok, detail in proposal["checks"]:
        if not ok:
            failures += 1
        print(f"  {'ok  ' if ok else 'FAIL'} {name}: {detail}")
    print()

    print(f"--- {proposal['state']['path']}")
    print(unified(proposal["state"]["path"], read_text(paths.state), proposal["state"]["proposed"]), end="")
    print(f"--- {proposal['seed']['path']}")
    print(unified(proposal["seed"]["path"], read_text(paths.seed), proposal["seed"]["proposed"]), end="")
    print(f"--- {proposal['donot']['path']}")
    print(unified(proposal["donot"]["path"], read_text(paths.donot), proposal["donot"]["text"]), end="")
    print()

    if failures:
        print(f"preview refused: {failures} check(s) failed. Nothing written.")
        return

    print(f"preview only — no project file written. plan: {paths.plan}")
    print(f"apply with: python3 handoff.py apply --plan {paths.plan}")


def write_plan(paths: Paths, proposal: dict) -> None:
    plan = {
        "version": PLAN_VERSION,
        "state": proposal["state"],
        "seed": proposal["seed"],
        "donot": proposal["donot"],
        "donot_count_before": proposal["donot_count_before"],
        "donot_count_after": proposal["donot_count_after"],
    }
    paths.plan.parent.mkdir(parents=True, exist_ok=True)
    with open(paths.plan, "w", encoding="utf-8", newline="") as handle:
        json.dump(plan, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def read_plan(paths: Paths) -> dict:
    if not paths.plan.is_file():
        raise HandoffError(
            f"no plan at {paths.plan} — run `handoff.py preview` first; there is nothing to apply"
        )
    try:
        plan = json.loads(read_text(paths.plan))
    except json.JSONDecodeError as error:
        raise HandoffError(f"{paths.plan}: {error}")
    if plan.get("version") != PLAN_VERSION:
        raise HandoffError(f"{paths.plan}: unsupported plan version {plan.get('version')}")
    return plan


def apply_plan(paths: Paths, plan: dict) -> None:
    """Write the three files exactly as the preview showed them."""
    for key in ("state", "seed", "donot"):
        entry = plan[key]
        path = paths.project / entry["path"]
        if not path.is_file():
            raise HandoffError(f"missing {path}")
        if digest(read_text(path)) != entry["current_sha256"]:
            raise HandoffError(
                f"the preview is stale: {entry['path']} changed since it was previewed"
            )

    donot_current = read_text(paths.donot)
    donot_result = build_donot(donot_current, plan["donot"]["append"])
    if not donot_result["text"].startswith(donot_current):
        raise HandoffError("the Do-Not list would not carry every existing entry through unchanged")

    write_text(paths.state, plan["state"]["proposed"])
    write_text(paths.seed, plan["seed"]["proposed"])
    if plan["donot"]["append"]:
        append_text(paths.donot, plan["donot"]["append"])

    print(f"wrote {plan['state']['path']}")
    print(f"wrote {plan['seed']['path']}")
    if plan["donot"]["append"]:
        print(
            f"appended {plan['donot_count_after'] - plan['donot_count_before']} entry/entries "
            f"to {plan['donot']['path']} "
            f"({plan['donot_count_before']} → {plan['donot_count_after']} entries)"
        )
    else:
        print(f"{plan['donot']['path']} unchanged ({plan['donot_count_after']} entries)")


def command_preview(args) -> int:
    paths = Paths(Path(args.project).resolve())
    proposal_dir = Path(args.proposal).resolve() if args.proposal else paths.proposal
    proposal = build_proposal(paths, proposal_dir)
    print_preview(paths, proposal)
    failures = [name for name, ok, _ in proposal["checks"] if not ok]
    if failures:
        return 1
    write_plan(paths, proposal)
    return 0


def command_apply(args) -> int:
    paths = Paths(Path(args.project).resolve())
    if args.plan:
        paths.plan = Path(args.plan).resolve()
    plan = read_plan(paths)
    apply_plan(paths, plan)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--project", default=".", help="the project root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    preview = subparsers.add_parser("preview", help="show the proposed update and write nothing")
    preview.add_argument(
        "--project", default=argparse.SUPPRESS, help="the project root",
    )
    preview.add_argument("--proposal", default=None, help="directory holding the proposed files")
    preview.set_defaults(handler=command_preview)

    apply = subparsers.add_parser("apply", help="write the update the preview showed")
    apply.add_argument(
        "--project", default=argparse.SUPPRESS, help="the project root",
    )
    apply.add_argument("--plan", default=None, help="the plan the preview wrote")
    apply.set_defaults(handler=command_apply)

    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except HandoffError as error:
        print(f"handoff: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
