"""SmartStandard CLI — run `smartstandard --demo`."""
import os, sys, json
from . import core
from ._version import __version__


def _demo_dir():
    return os.path.join(os.path.dirname(__file__), "..", "..", "demo")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--version" in argv:
        print(f"SmartStandard {__version__}"); return 0
    demo = "--demo" in argv or not argv
    print(f"\n🦔 SmartStandard {__version__}  ·  IAIso §7 · Standards")
    result = core_demo()
    print(result)
    print(f"\nBacked by IAIso §7 · Standards · part of the Smart* family · https://smarttasks.cloud\n")
    return 0


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
