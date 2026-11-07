#!/usr/bin/env python3
"""Run the deterministic BabySteps session-cost preflight for /babysteps-start."""

from __future__ import annotations

import argparse
import json
import os
import shlex
import subprocess
import sys
from pathlib import Path


def current_session(root: Path) -> str:
    explicit = os.environ.get("BABYSTEPS_SESSION_ID", "").strip()
    if explicit:
        return explicit
    result = subprocess.run(
        [
            "opencode",
            "api",
            "get",
            "/api/session",
            "--header",
            f"x-opencode-directory:{root}",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "could not read OpenCode sessions")
    data = json.loads(result.stdout)
    rows = data.get("data") or data.get("sessions") or []
    rows = [
        row
        for row in rows
        if (row.get("location") or {}).get("directory") == str(root)
        and (row.get("time") or {}).get("created")
        and not row.get("parentID")
    ]
    rows.sort(key=lambda row: row["time"]["created"])
    if not rows:
        raise RuntimeError(f"no current OpenCode session found for {root}")
    return rows[-1]["id"]


def requested_budget(arguments: str) -> tuple[int | None, bool]:
    tokens = shlex.split(arguments)
    budget = None
    big_boy = False
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == "--bigBoy":
            big_boy = True
        elif token == "--budget":
            index += 1
            if index >= len(tokens):
                raise ValueError("--budget needs a token count")
            budget = int(tokens[index])
            if budget <= 0:
                raise ValueError("--budget must be positive")
        elif token.startswith("--budget="):
            budget = int(token.split("=", 1)[1])
            if budget <= 0:
                raise ValueError("--budget must be positive")
        elif token not in ("--auto-chain", "--chain"):
            raise ValueError(f"unsupported /babysteps-start argument: {token}")
        index += 1
    return budget, big_boy


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--arguments", default="")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        budget, big_boy = requested_budget(args.arguments)
        session = current_session(root)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"BabySteps preflight failed: {error}", file=sys.stderr)
        return 2

    binary = root / ".babysteps" / "bin" / "babysteps-budget"
    if not binary.is_file():
        print(f"BabySteps preflight failed: missing {binary}", file=sys.stderr)
        return 2
    command = [
        str(binary),
        "--root",
        str(root),
        "--config",
        str(root / ".babysteps" / "config.json"),
        "--session",
        session,
        "--session-only",
        "--json",
    ]
    if budget is not None and not big_boy:
        command.extend(["--work-budget", str(budget)])
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    print(f"BabySteps preflight session: {session}")
    print(f"BabySteps preflight budget: {'unbounded' if big_boy else budget or 'project config'}")
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode != 0 and result.stderr:
        print(result.stderr, file=sys.stderr, end="")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
