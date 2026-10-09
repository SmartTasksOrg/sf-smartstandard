"""SmartStandard core — one shared convention + conformance check."""
import hashlib, json, os
from .models import Rule, Standard, Conformance

DEFAULT_RULES = [
    Rule("STD-README", "A README.md exists with a hook + a 10s try-it line."),
    Rule("STD-SMARTJSON", "A .smart.json declares the family + IAIso section."),
    Rule("STD-LICENSE", "A LICENSE is present."),
    Rule("STD-TESTS", "A tests/ directory exists."),
]

def standard() -> Standard:
    # deterministic, real SHA-256 over the rule ids (stable across processes)
    key = ",".join(r.id for r in DEFAULT_RULES)
    h = hashlib.sha256(key.encode()).hexdigest()[:12]
    return Standard("iaiso-baseline", DEFAULT_RULES, "sha256:" + h)

def conformance(root: str) -> Conformance:
    checks = {
        "STD-README": os.path.exists(os.path.join(root, "README.md")),
        "STD-SMARTJSON": os.path.exists(os.path.join(root, ".smart.json")),
        "STD-LICENSE": os.path.exists(os.path.join(root, "LICENSE")),
        "STD-TESTS": os.path.isdir(os.path.join(root, "tests")),
    }
    drift = [k for k, ok in checks.items() if not ok]
    score = round(100 * sum(checks.values()) / len(checks))
    return Conformance(score, drift)
