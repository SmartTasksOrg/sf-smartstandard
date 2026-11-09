"""SmartStandard CLI.

    sf-smartstandard --demo
    sf-smartstandard PATH [--standard iaiso-baseline|iaiso-strict|FILE.json] [--json]

Exit code 0 when PATH conforms fully, 1 when any rule drifts.
"""
import argparse
import json
import os
import sys
from dataclasses import asdict

from . import core
from ._version import __version__

BANNER = f"\n🦔 SmartStandard {__version__}  ·  IAIso §7 · Standards"
FOOTER = "\nBacked by IAIso §7 · Standards · part of the Smart* family · https://smarttasks.cloud\n"


def _demo_dir():
    return os.path.join(os.path.dirname(__file__), "..", "..", "demo")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--version" in argv:
        print(f"SmartStandard {__version__}"); return 0
    if not argv or "--demo" in argv:
        print(BANNER); print(core_demo()); print(FOOTER); return 0

    ap = argparse.ArgumentParser(prog="sf-smartstandard")
    ap.add_argument("path", help="folder to check")
    ap.add_argument("--standard", default="iaiso-baseline",
                    help="iaiso-baseline, iaiso-strict, or a JSON standard file")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    std = core.load_standard(a.standard) if a.standard.endswith(".json") else core.standard(a.standard)
    c = core.conformance(a.path, std)
    if a.json:
        print(json.dumps({"standard": std.id, "hash": std.hash, **asdict(c)}, indent=2))
    else:
        print(f"{std.id} {std.hash}: {c.score}/100")
        desc = {r.id: r.desc for r in std.rules}
        for d in c.drift:
            print(f"  ✗ {d}: {desc.get(d, '')}")
    return 0 if not c.drift else 1


def core_demo() -> str:
    return _DEMO()


def _DEMO():
    root = os.path.join(os.path.dirname(__file__), "..", "..")
    s = core.standard()
    c = core.conformance(root)
    out = [f"standard {s.id}  ({len(s.rules)} rules)  {s.hash}",
           f"conformance of this repo: {c.score}/100"]
    for d in c.drift:
        out.append(f"  ✗ drift: {d}")
    if not c.drift:
        out.append("  ✓ fully conformant")
    return "\n".join(out)

if __name__ == "__main__":
    sys.exit(main())
