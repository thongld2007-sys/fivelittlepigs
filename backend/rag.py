"""Auditable local retrieval over curated, GDPT-aligned pedagogical notes."""

from __future__ import annotations

import json
import re
from pathlib import Path


class RAGRetriever:
    def __init__(self, path: str | Path | None = None):
        source = Path(path) if path else Path(__file__).resolve().parents[1] / "data" / "rag_knowledge.json"
        self.documents = json.loads(source.read_text(encoding="utf-8"))

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return set(re.findall(r"[\wÀ-ỹ]+", text.lower()))

    def retrieve(self, query: str, *, skill_id: str | None = None, limit: int = 3) -> list[dict]:
        query_tokens = self._tokens(query)
        ranked = []
        for document in self.documents:
            content_tokens = self._tokens(" ".join([document["title"], document["content"], " ".join(document.get("keywords", []))]))
            lexical = len(query_tokens & content_tokens)
            skill_bonus = 8 if skill_id and skill_id in document.get("skill_ids", []) else 0
            ranked.append((lexical + skill_bonus, document))
        return [{**document, "retrieval_score": score} for score, document in sorted(ranked, key=lambda item: item[0], reverse=True)[:limit] if score > 0]


rag_retriever = RAGRetriever()
