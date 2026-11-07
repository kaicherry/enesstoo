#!/usr/bin/env python3
"""Render a chain child's event stream, bounded.

The chain step runs the child with `opencode run --format json`, which writes raw JSON
events rather than readable output, and points this renderer at the file that stream is
written to. The child is silent through the phases that take longest — a brief subagent, a
gate run — so silence is the normal state, and a renderer that says nothing leaves a live
child and a dead one looking the same.

The pending policy is bounded on purpose. A stall of `--pending-after` seconds is reported,
at most `--max-pending` times per stall; after the last report the renderer says it has
stopped asking and stays quiet until an event arrives. A monitor that keeps asking turns a
silent child into noise, and noise is ignored.

  chain_watch.py --follow <events.jsonl> [--pending-after 90] [--max-pending 2]
  chain_watch.py < events.jsonl
"""

import argparse
import json
import sys
import time
from pathlib import Path

DEFAULT_PENDING_AFTER = 90.0
DEFAULT_MAX_PENDING = 2
DEFAULT_POLL = 0.5

TEXT_KEYS = ("text", "content")


def parse(line):
    """The event a line carries, or None when the line is not a JSON object."""
    try:
        event = json.loads(line)
    except ValueError:
        return None
    return event if isinstance(event, dict) else None


def part_of(event):
    """The part an event carries, or an empty dict.

    `opencode run --format json` writes one envelope per line — `type`, `timestamp`,
    `sessionID` and `part` — and the payload lives in the part.
    """
    part = event.get("part")
    return part if isinstance(part, dict) else {}


def status_of(part):
    state = part.get("state")
    if isinstance(state, dict) and state.get("status"):
        return str(state["status"])
    return ""


def text_of(part):
    for key in TEXT_KEYS:
        value = part.get(key)
        if isinstance(value, str) and value:
            return value
    return ""


def session_of(event):
    """The session an event belongs to, or the empty string.

    Every envelope carries it, so the id is named once, when it first appears.
    """
    if not isinstance(event, dict):
        return ""
    identifier = event.get("sessionID")
    return str(identifier) if identifier else ""


def render(line, event):
    """The lines to print for one event.

    A line this renderer does not recognise is printed unchanged. Dropping it would hide
    the child's own output behind the renderer's opinion of it, and the child is the thing
    being watched.
    """
    if event is None:
        return [line] if line.strip() else []
    kind = str(event.get("type", ""))
    part = part_of(event)
    if kind == "tool_use":
        name = part.get("tool") or part.get("name") or "tool"
        status = status_of(part)
        return [f"[chain] tool {name} — {status}" if status else f"[chain] tool {name}"]
    if kind == "text":
        text = text_of(part)
        return text.splitlines() or []
    if kind == "error":
        error = event.get("error")
        message = error.get("message") if isinstance(error, dict) else error
        return [f"[chain] error: {message or 'unknown'}"]
    if kind in ("step_start", "reasoning"):
        return []
    if kind == "step_finish":
        return ["[chain] step finished"]
    return [line]


class Monitor:
    """The bounded pending policy over one event stream.

    `observe` takes an event and ends the current stall; `tick` is what a follower calls on
    its poll interval, and is the only place a pending report is made. Reports are counted
    against the stall, so a child that keeps stalling keeps being reported while a child
    that is merely slow cannot make the monitor repeat itself indefinitely.
    """

    def __init__(self, pending_after=DEFAULT_PENDING_AFTER, max_pending=DEFAULT_MAX_PENDING, clock=time.monotonic):
        self.pending_after = float(pending_after)
        self.max_pending = int(max_pending)
        self.clock = clock
        self.events = 0
        self.reported = 0
        self.reports = 0
        self.session = ""
        self._last = clock()

    def observe(self, line, now=None):
        if not line.strip():
            return []
        now = self.clock() if now is None else now
        self.events += 1
        self._last = now
        self.reports = 0
        event = parse(line)
        lines = []
        identifier = session_of(event)
        if identifier and identifier != self.session:
            self.session = identifier
            lines.append(f"[chain] session {identifier}")
        lines.extend(render(line.rstrip("\n"), event))
        return lines

    def tick(self, now=None):
        now = self.clock() if now is None else now
        if self.reports >= self.max_pending:
            return []
        silence = now - self._last
        if silence < self.pending_after:
            return []
        self.reports += 1
        self.reported += 1
        label = f"report {self.reports} of {self.max_pending}"
        if self.reports >= self.max_pending:
            return [f"[chain] pending — no event for {int(silence)}s since event {self.events} "
                    f"({label}); not asking again until an event arrives"]
        return [f"[chain] pending — no event for {int(silence)}s since event {self.events} ({label})"]

    def summary(self):
        return (f"[chain] stream closed — {self.events} events, "
                f"{self.reported} pending report{'s' if self.reported != 1 else ''}")


def emit(lines, out):
    for rendered in lines:
        print(rendered, file=out, flush=True)


def drain(path, offset, buffer):
    """Read what has been appended since offset; return the complete lines and the new state.

    The read is binary and the decoding happens after, because a text-mode offset is an
    opaque cookie that a second handle cannot rely on once a multi-byte character straddles
    the boundary.
    """
    try:
        with open(path, "rb") as handle:
            handle.seek(offset)
            chunk = handle.read()
            offset = handle.tell()
    except FileNotFoundError:
        return [], offset, buffer
    buffer += chunk.decode("utf-8", "replace")
    lines = []
    while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        lines.append(line)
    return lines, offset, buffer


def follow(path, monitor, out, poll=DEFAULT_POLL, done=None):
    """Follow a stream until `done` exists and the file has been read to its end."""
    offset, buffer = 0, ""
    while True:
        lines, offset, buffer = drain(path, offset, buffer)
        for line in lines:
            emit(monitor.observe(line), out)
        emit(monitor.tick(), out)
        if done is not None and done.exists():
            if buffer:
                emit(monitor.observe(buffer), out)
                buffer = ""
                continue
            return
        time.sleep(poll)


def watch_stdin(monitor, out):
    for line in sys.stdin:
        emit(monitor.observe(line), out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--follow", type=Path, default=None,
                        help="event file to follow; without it the stream is read from stdin")
    parser.add_argument("--done-file", type=Path, default=None,
                        help="appear when the child has exited (default: <events>.done)")
    parser.add_argument("--pending-after", type=float, default=DEFAULT_PENDING_AFTER,
                        help="seconds of silence before a child is reported pending")
    parser.add_argument("--max-pending", type=int, default=DEFAULT_MAX_PENDING,
                        help="pending reports per stall before the monitor stops asking")
    parser.add_argument("--poll", type=float, default=DEFAULT_POLL, help="seconds between reads")
    args = parser.parse_args(argv)

    monitor = Monitor(args.pending_after, args.max_pending)
    out = sys.stdout
    if args.follow:
        done = args.done_file or Path(str(args.follow) + ".done")
        follow(args.follow, monitor, out, args.poll, done)
    else:
        watch_stdin(monitor, out)
    emit([monitor.summary()], out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
