#!/usr/bin/env python3
"""Tail-block protocol for orchestrator <-> worker handoff.

Workers (planner / executor / verifier subagents) emit a single structured
line as their final output:

    <<orchestrate-result>>{"status":"ok","path":"...","sha":"..."}<<end>>

The orchestrator parses that line out of the worker's full output to extract
machine-readable fields without having to read the entire human-readable
narrative the worker produced. Everything before the tail is the worker's
own context that closes when the worker exits.

This script is dual-use:
- Workers can call `emit` to format the tail line correctly.
- The orchestrator can call `parse` to pull JSON out of captured stdout.

Schema (always present):
    status   one of: ok | fail | blocked

Common fields by role:
    planner   -> path     (str)  relative path to the written PLAN.md
                 summary  (str)  one-line description of the plan
    executor  -> sha      (str)  HEAD commit SHA after execution
                 files    (int)  number of files changed
                 tests    (str)  pass | fail | not-run
    verifier  -> verdict  (str)  pass | fail
                 reasons  (list) failure reasons (only when verdict=fail)

Always allowed:
    reason     (str)  why the worker emitted fail or blocked
    suggestion (str)  concrete next step for the orchestrator
    summary    (str)  one-line summary
"""

import argparse
import json
import re
import sys

TAIL_RE = re.compile(r"<<orchestrate-result>>(.*?)<<end>>", re.DOTALL)


def emit(payload):
    return "<<orchestrate-result>>" + json.dumps(payload, separators=(",", ":")) + "<<end>>"


def parse(text):
    matches = TAIL_RE.findall(text)
    if not matches:
        return None
    try:
        return json.loads(matches[-1])
    except json.JSONDecodeError:
        return None


def main():
    p = argparse.ArgumentParser(description="Orchestrator <-> worker tail-block protocol.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("schema", help="print the field reference")

    pe = sub.add_parser("emit", help="print a tail-block to stdout")
    pe.add_argument("--status", required=True, choices=["ok", "fail", "blocked"])
    pe.add_argument(
        "--field",
        action="append",
        default=[],
        metavar="key=value",
        help="extra field (repeatable). value is parsed as JSON if possible, else string.",
    )

    sub.add_parser("parse", help="read stdin, print parsed tail-block JSON, exit 1 if absent")

    args = p.parse_args()

    if args.cmd == "schema":
        print(__doc__.strip())
        return

    if args.cmd == "emit":
        payload = {"status": args.status}
        for kv in args.field:
            k, _, v = kv.partition("=")
            try:
                payload[k] = json.loads(v)
            except json.JSONDecodeError:
                payload[k] = v
        print(emit(payload))
        return

    if args.cmd == "parse":
        text = sys.stdin.read()
        result = parse(text)
        if result is None:
            sys.stderr.write("no orchestrate-result tail found\n")
            sys.exit(1)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
