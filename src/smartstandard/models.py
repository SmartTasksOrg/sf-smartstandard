"""UML data objects for SmartStandard — the diagram in the README is these classes."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class Rule:
    id: str
    desc: str

@dataclass
class Standard:
    id: str
    rules: list[Rule]
    hash: str

@dataclass
class Conformance:
    score: int
    drift: list[str]
