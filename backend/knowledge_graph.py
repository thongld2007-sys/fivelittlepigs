"""Small GDPT 2018 mathematics knowledge graph represented as a DAG."""

from __future__ import annotations

from collections import deque

from backend.extended_knowledge_graph import KNOWLEDGE_GRAPH as EXTENDED_KNOWLEDGE_GRAPH


CORE_KNOWLEDGE_GRAPH: dict[str, dict] = {
    "MATH7_ADD_RATIONAL": {
        "name": "Cộng trừ số hữu tỉ (Lớp 7)",
        "grade": 7,
        "prerequisites": ["MATH6_ADD_INTEGER", "MATH5_COMMON_FRACTION"],
    },
    "MATH6_ADD_INTEGER": {
        "name": "Cộng trừ số nguyên (Lớp 6)",
        "grade": 6,
        "prerequisites": [],
    },
    "MATH5_COMMON_FRACTION": {
        "name": "Quy đồng mẫu số phân số (Lớp 5)",
        "grade": 5,
        "prerequisites": [],
    },
}

# Preserve the report-specific canonical skills while extending the application
# with the 55 grade/subject skills synchronized from the frontend repository.
KNOWLEDGE_GRAPH: dict[str, dict] = {
    **EXTENDED_KNOWLEDGE_GRAPH,
    **CORE_KNOWLEDGE_GRAPH,
}


class KnowledgeGraph:
    @staticmethod
    def get_skill_info(skill_id: str) -> dict | None:
        info = KNOWLEDGE_GRAPH.get(skill_id)
        return {"skill_id": skill_id, **info} if info else None

    @staticmethod
    def get_prerequisites(skill_id: str) -> list[str]:
        info = KNOWLEDGE_GRAPH.get(skill_id)
        return list(info.get("prerequisites", [])) if info else []

    @staticmethod
    def is_valid_skill(skill_id: str) -> bool:
        return skill_id in KNOWLEDGE_GRAPH

    @staticmethod
    def all_skills() -> list[dict]:
        return [KnowledgeGraph.get_skill_info(skill_id) for skill_id in KNOWLEDGE_GRAPH]

    @staticmethod
    def descendants(skill_id: str) -> list[str]:
        """Return prerequisites breadth-first and guard against accidental cycles."""
        if skill_id not in KNOWLEDGE_GRAPH:
            return []
        result: list[str] = []
        seen = {skill_id}
        queue = deque(KnowledgeGraph.get_prerequisites(skill_id))
        while queue:
            current = queue.popleft()
            if current in seen:
                continue
            seen.add(current)
            result.append(current)
            queue.extend(KnowledgeGraph.get_prerequisites(current))
        return result

    @staticmethod
    def validate() -> None:
        for skill_id, info in KNOWLEDGE_GRAPH.items():
            for prerequisite in info.get("prerequisites", []):
                if prerequisite not in KNOWLEDGE_GRAPH:
                    raise ValueError(f"Unknown prerequisite {prerequisite!r} for {skill_id!r}")
            if skill_id in KnowledgeGraph.descendants(skill_id):
                raise ValueError(f"Cycle detected at skill {skill_id!r}")
