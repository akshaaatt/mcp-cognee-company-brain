"""Cognee-backed knowledge facade with a deterministic, no-key graph fallback.

The explicit graph is retained so that structured relationships can be explained
reliably even when a deployment cannot download local model assets.
"""
import asyncio
from collections import defaultdict, deque
from typing import Optional
from .models import Relationship, SourceDocument

class KnowledgeBase:
    def __init__(self):
        self.documents: list[SourceDocument] = []
        self.relationships: list[Relationship] = []
        self._cognee_available = False
        self._cognee_error = None

    @property
    def cognee_status(self):
        if self._cognee_error:
            return self._cognee_error
        return "synced" if self._cognee_available else "not initialized"

    @property
    def knowledge_mode(self):
        """Human-facing deployment status without surfacing raw import errors."""
        if self._cognee_available and not self._cognee_error:
            return "Cognee semantic graph synced"
        if self.documents:
            return "Grounded relationship graph active (Cognee optional on hosted demo)"
        return "Ready for grounded knowledge"

    def initialize(self):
        try:
            import cognee  # noqa: F401 - optional runtime integration
            self._cognee_available = True
        except Exception as exc:
            self._cognee_error = f"Cognee unavailable: {type(exc).__name__}"

    def clear(self):
        self.documents.clear()
        self.relationships.clear()

    def ingest(self, documents: list[SourceDocument], relationships: Optional[list[Relationship]] = None):
        self.documents.extend(documents)
        if relationships:
            self.relationships.extend(relationships)

    def build(self):
        """Synchronize normalized text to Cognee, without making it a prerequisite.

        Cognee's pipeline may need locally installed model assets. A failure is
        deliberately non-fatal: explicit source relationships still provide the
        zero-key, evidence-preserving baseline.
        """
        self.initialize()
        if not self._cognee_available:
            return
        try:
            import cognee
            payload = [f"Title: {doc.title}\nType: {doc.source_type}\n{doc.content}" for doc in self.documents]
            asyncio.run(self._sync_cognee(cognee, payload))
            self._cognee_error = None
        except Exception as exc:
            self._cognee_error = f"Cognee sync deferred: {type(exc).__name__}"

    async def _sync_cognee(self, cognee, payload):
        if payload:
            await cognee.add(payload, dataset_name="mini_company_brain")
            await cognee.cognify(["mini_company_brain"])

    def recall(self, query: str) -> list[SourceDocument]:
        words = {word.lower().strip("?.,!") for word in query.split() if len(word) > 2}
        ranked = []
        for doc in self.documents:
            score = sum(word in f"{doc.title} {doc.content}".lower() for word in words)
            if score:
                ranked.append((score, doc))
        return [doc for _, doc in sorted(ranked, key=lambda item: item[0], reverse=True)[:8]]

    def path(self, start: str, end: str) -> list[str]:
        graph = defaultdict(list)
        for rel in self.relationships:
            graph[rel.source].append((rel.target, rel.predicate))
        queue = deque([(start, [start])])
        seen = {start}
        while queue:
            node, path = queue.popleft()
            if node == end:
                return path
            for neighbor, _ in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    def evidence_for(self, names: list[str]) -> list[SourceDocument]:
        return [doc for doc in self.documents if any(name.lower() == doc.title.lower() for name in names)]
