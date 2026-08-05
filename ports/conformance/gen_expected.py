#!/usr/bin/env python3
"""Regenerate expected.json from the Python reference (smartstandard.core).
Fixture roots are resolved relative to this file so results are location-stable."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "src")))
from smartstandard.core import standard, conformance  # noqa: E402

v = json.load(open(os.path.join(HERE, "vectors.json"), encoding="utf-8"))
res = []
for c in v["cases"]:
    if c.get("op", "standard") == "standard":
        s = standard()
        res.append({"name": c["name"], "id": s.id, "hash": s.hash, "rules": [r.id for r in s.rules]})
    else:
        cf = conformance(os.path.join(HERE, c["root"]))
        res.append({"name": c["name"], "score": cf.score, "drift": cf.drift})
out = {"results": res}
with open(os.path.join(HERE, "expected.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2); f.write("\n")
print(f"wrote expected.json ({len(res)} cases)")
