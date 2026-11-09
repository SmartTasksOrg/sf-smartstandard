"""UML data objects for SmartStandard — the diagram in the README is these classes."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Rule:
    id: str
    desc: str
    check: str = ""        # "" = the baseline check for this id; else exists | dir | nonempty | contains | json_keys | glob
    path: str = ""
    arg: object = None     # text for contains, keys for json_keys, pattern for glob

@dataclass
class Standard:
    id: str
    rules: list[Rule]
    hash: str

@dataclass
class Conformance:
    score: int
    drift: list[str]
