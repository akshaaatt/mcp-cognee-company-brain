from dataclasses import dataclass, field
from typing import Any

@dataclass
class SourceDocument:
    id: str
    source_type: str
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class Relationship:
    source: str
    predicate: str
    target: str

@dataclass
class Answer:
    text: str
    evidence: list[SourceDocument]
    chain: list[str] = field(default_factory=list)
