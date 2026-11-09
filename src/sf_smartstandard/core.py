"""SmartStandard core — one shared convention + conformance check.

Three ways to pick a standard:

* `standard()` / `"iaiso-baseline"`: the four files every Smart* repo has
  (README, .smart.json, LICENSE, tests/). Presence only.
* `standard("iaiso-strict")`: the same four, checked for content: the README
  has a heading and a runnable line, .smart.json is valid JSON naming its
  family and IAIso section, the LICENSE names a license, and tests/ holds at
  least one test file.
* `load_standard("team.json")`: your own rules, each one of these checks:
  `exists`, `dir`, `nonempty`, `contains` (arg: text), `json_keys`
  (arg: list of keys) or `glob` (arg: pattern under path).
"""
from __future__ import annotations

import glob as _glob
import hashlib
import json
import os
import re

from .models import Conformance, Rule, Standard

DEFAULT_RULES = [
    Rule("STD-README", "A README.md exists with a hook + a 10s try-it line."),
    Rule("STD-SMARTJSON", "A .smart.json declares the family + IAIso section."),
    Rule("STD-LICENSE", "A LICENSE is present."),
    Rule("STD-TESTS", "A tests/ directory exists."),
]

STRICT_RULES = [
    Rule("STD-README", "README.md has a heading and a runnable line (a code block or $ command).",
         "readme_strict", "README.md"),
    Rule("STD-SMARTJSON", ".smart.json is valid JSON with non-empty family and iaiso_section.",
         "json_keys", ".smart.json", ["family", "iaiso_section"]),
    Rule("STD-LICENSE", "LICENSE names a license.", "license_strict", "LICENSE"),
    Rule("STD-TESTS", "tests/ holds at least one test_*.py or *_test.py.", "tests_strict", "tests"),
]

CHECKS = ("exists", "dir", "nonempty", "contains", "json_keys", "glob")
_LICENSE_WORDS = re.compile(r"\b(license|licence|SPDX-License-Identifier|copyright)\b", re.I)


def _hash(s_id: str, rules: list[Rule]) -> str:
    if all(not r.check for r in rules):
        key = ",".join(r.id for r in rules)          # baseline: unchanged since version 3.0
    else:
        key = json.dumps([s_id] + [[r.id, r.check, r.path, r.arg] for r in rules], sort_keys=True)
    return "sha256:" + hashlib.sha256(key.encode()).hexdigest()[:12]


def standard(name: str = "iaiso-baseline") -> Standard:
    if name == "iaiso-baseline":
        rules = DEFAULT_RULES
    elif name == "iaiso-strict":
        rules = STRICT_RULES
    else:
        raise ValueError("built-in standards are 'iaiso-baseline' and 'iaiso-strict'")
    return Standard(name, list(rules), _hash(name, rules))


def load_standard(path: str) -> Standard:
    """Read {"id": "...", "rules": [{"id", "desc", "check", "path", "arg"?}, ...]}."""
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict) or not isinstance(data.get("rules"), list) or not data["rules"]:
        raise ValueError('expected {"id": "...", "rules": [...]}')
    rules, seen = [], set()
    for i, r in enumerate(data["rules"]):
        if not isinstance(r, dict) or not r.get("id") or r.get("check") not in CHECKS or not r.get("path"):
            raise ValueError(f"rule {i + 1}: needs id, path and check (one of {', '.join(CHECKS)})")
        if r["id"] in seen:
            raise ValueError(f"rule id {r['id']!r} appears twice")
        if os.path.isabs(r["path"]) or ".." in r["path"].replace("\\", "/").split("/"):
            raise ValueError(f"rule {r['id']!r}: path must stay inside the folder being checked")
        if r["check"] in ("contains", "glob") and not isinstance(r.get("arg"), str):
            raise ValueError(f"rule {r['id']!r}: {r['check']} needs a text 'arg'")
        if r["check"] == "json_keys" and not (isinstance(r.get("arg"), list) and r["arg"]):
            raise ValueError(f"rule {r['id']!r}: json_keys needs a list of keys in 'arg'")
        seen.add(r["id"])
        rules.append(Rule(r["id"], r.get("desc", ""), r["check"], r["path"], r.get("arg")))
    s_id = str(data.get("id") or os.path.splitext(os.path.basename(path))[0])
    return Standard(s_id, rules, _hash(s_id, rules))


def _read(p: str) -> str:
    try:
        with open(p, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return ""


def _passes(root: str, rule: Rule) -> bool:
    p = os.path.join(root, rule.path)
    c = rule.check
    if c == "exists":
        return os.path.exists(p)
    if c == "dir":
        return os.path.isdir(p)
    if c == "nonempty":
        return os.path.isfile(p) and bool(_read(p).strip())
    if c == "contains":
        return rule.arg in _read(p)
    if c == "json_keys":
        try:
            data = json.loads(_read(p))
        except ValueError:
            return False
        return isinstance(data, dict) and all(data.get(k) not in (None, "", [], {}) for k in rule.arg)
    if c == "glob":
        return bool(_glob.glob(os.path.join(p, rule.arg), recursive=True))
    if c == "readme_strict":
        text = _read(p)
        return bool(re.search(r"^#\s+\S|<h1[\s>]", text, re.M | re.I)) and bool(re.search(r"```|^\s*\$\s+\S", text, re.M))
    if c == "license_strict":
        return bool(_LICENSE_WORDS.search(_read(p)))
    if c == "tests_strict":
        return bool(_glob.glob(os.path.join(p, "**", "test_*.py"), recursive=True)
                    or _glob.glob(os.path.join(p, "**", "*_test.py"), recursive=True))
    raise ValueError(f"unknown check {c!r}")


_BASELINE = {
    "STD-README": lambda root: os.path.exists(os.path.join(root, "README.md")),
    "STD-SMARTJSON": lambda root: os.path.exists(os.path.join(root, ".smart.json")),
    "STD-LICENSE": lambda root: os.path.exists(os.path.join(root, "LICENSE")),
    "STD-TESTS": lambda root: os.path.isdir(os.path.join(root, "tests")),
}


def conformance(root: str, std: Standard | str | None = None) -> Conformance:
    """Check `root` against a standard (default: iaiso-baseline)."""
    s = standard() if std is None else (standard(std) if isinstance(std, str) else std)
    checks = {}
    for r in s.rules:
        checks[r.id] = _BASELINE[r.id](root) if not r.check else _passes(root, r)
    drift = [k for k, ok in checks.items() if not ok]
    score = round(100 * sum(checks.values()) / len(checks)) if checks else 100
    return Conformance(score, drift)
