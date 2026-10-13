#!/usr/bin/env python3
"""SmartStandard integration adapter — the single source of truth for every
framework wrapper in this folder. Exposes TOOL_NAME, DESCRIPTION, INPUT_SCHEMA
and run(payload)->dict, plus a CLI:  python adapter.py --root <input>
"""
import argparse
import json
import os
import sys

from smartstandard.core import conformance, standard

TOOL_NAME = "smartstandard_conformance"
DESCRIPTION = "Score a repo against the IAIso baseline (README, .smart.json, LICENSE, tests/) and report drift."
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "root": {
                "type": "string",
                "description": "Repo root to check",
                "default": "."
        }
    },
    "required": [],
}


def _read(p):
    with open(p, encoding="utf-8", errors="ignore") as f:
        return f.read()


def run(payload):
    """Run SmartStandard on a payload dict and return a compact, JSON-safe result."""
    c = conformance(payload.get('root', '.'))
    result = {'score': c.score, 'drift': c.drift, 'standard': standard().hash}
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=DESCRIPTION)
    ap.add_argument("--text")
    ap.add_argument("--file")
    ap.add_argument("--root")
    ap.add_argument("--sources")
    args = ap.parse_args(argv)
    payload = {'root': args.root or '.'}
    print(json.dumps(run(payload)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
