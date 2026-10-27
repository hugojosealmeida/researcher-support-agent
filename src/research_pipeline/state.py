"""Data models that flow through the research pipeline."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar


@dataclass
class SearchItem:
    """One result from the literature search."""

    title: str
    authors: list[str]
    year: int
    venue: str
    doi: str | None = None
    abstract: str = ""
    url: str = ""
    relevance_score: float = 0.0


@dataclass
class Paper:
    """A downloaded paper in structured markdown form."""

    title: str
    authors: list[str]
    year: int
    venue: str
    doi: str | None = None
    md_path: str = ""
    content: str = ""
    sections: dict[str, str] = field(default_factory=dict)


@dataclass
class Summary:
    """Evidence-grounded summary of one paper."""

    title: str
    doi: str | None = None
    key_findings: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    relevance_to_topic: str = ""


@dataclass
class ReviewComment:
    """A single comment from the academic reviewer."""

    section: str
    severity: str  # "critical", "major", "minor"
    comment: str
    suggested_fix: str = ""


@dataclass
class PipelineState:
    """Shared mutable state passed between pipeline phases."""

    # --- Phase 1: Planning ---
    topic: str = ""
    research_questions: list[str] = field(default_factory=list)
    scope: dict[str, Any] = field(default_factory=dict)
    inclusion_criteria: list[str] = field(default_factory=list)
    search_strategy: str = ""

    # --- Phase 2: Literature Search ---
    search_results: list[SearchItem] = field(default_factory=list)
    excluded_papers: list[SearchItem] = field(default_factory=list)

    # --- Phase 3: Paper Ingestion ---
    papers: list[Paper] = field(default_factory=list)

    # --- Phase 4: Summarization ---
    summaries: list[Summary] = field(default_factory=list)

    # --- Phase 5: Synthesis ---
    synthesis: dict[str, Any] = field(default_factory=dict)

    # --- Phase 6: Writing ---
    manuscript: str = ""

    # --- Phase 7: Review ---
    review_comments: list[ReviewComment] = field(default_factory=list)
    review_passed: bool = False

    # --- Phase 8: Revision ---
    final_manuscript: str = ""
    version: str = "1.0"
    published: bool = False

    # --- Metadata ---
    completed_phases: list[str] = field(default_factory=list)
    _phase_order: list[str] = field(
        default_factory=lambda: [
            "planning",
            "literature_search",
            "paper_ingestion",
            "paper_summarization",
            "literature_synthesis",
            "review_paper_writing",
            "academic_review",
            "revision_release",
        ],
        repr=False,
    )

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def save(self, path: str | Path = "pipeline_state.json") -> None:
        """Persist the full state to a JSON file."""
        p = Path(path)
        data: dict[str, Any] = {}
        for key in self.__dataclass_fields__:
            if key.startswith("_"):
                continue
            val = getattr(self, key)
            # Serialize domain objects as dicts
            if isinstance(val, (list, tuple)):
                data[key] = [_serialize(item) if not isinstance(item, dict) else item for item in val]
            elif isinstance(val, dict):
                data[key] = val
            elif not isinstance(val, (str, int, float, bool)) and val is not None:
                data[key] = _serialize(val)
            else:
                data[key] = val
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path = "pipeline_state.json") -> PipelineState:
        """Restore state from a JSON file."""
        p = Path(path)
        if not p.exists():
            return cls()
        data = json.loads(p.read_text(encoding="utf-8"))
        instance = cls()
        for key, val in data.items():
            if key.startswith("_"):
                continue
            setattr(instance, key, _deserialize(key, val))
        return instance

    # Phase-name → attribute mapping
    _PHASE_ATTRIBUTES: ClassVar[dict[str, list[str]]] = {
        "planning": [
            "topic",
            "research_questions",
            "scope",
            "inclusion_criteria",
            "search_strategy",
        ],
        "literature_search": ["search_results", "excluded_papers"],
        "paper_ingestion": ["papers"],
        "paper_summarization": ["summaries"],
        "literature_synthesis": ["synthesis"],
        "review_paper_writing": ["manuscript"],
        "academic_review": ["review_comments", "review_passed"],
        "revision_release": ["final_manuscript", "version", "published"],
    }

    def phase_has_data(self, phase_name: str) -> bool:
        """Return ``True`` if the state already has results for *phase_name*."""
        attrs = self._PHASE_ATTRIBUTES.get(phase_name, [])
        return any(getattr(self, attr) for attr in attrs if isinstance(getattr(self, attr), (list, dict, str)))

    def get_phase_order(self) -> list[str]:
        return list(self._phase_order)


# ---- serialization helpers ---- #


def _serialize(obj: Any) -> Any:
    """Recursively turn a dataclass / object into a JSON-safe dict."""
    if hasattr(obj, "__dataclass_fields__"):
        return {k: _serialize(getattr(obj, k)) for k in obj.__dataclass_fields__}
    if isinstance(obj, (list, tuple)):
        return [_serialize(i) for i in obj]
    return obj


def _deserialize(key: str, val: Any) -> Any:
    """Restore domain objects from a dict loaded from JSON."""
    if key == "search_results" and isinstance(val, list):
        return [_as_dataclass(SearchItem, item) for item in val]
    if key == "papers" and isinstance(val, list):
        return [_as_dataclass(Paper, item) for item in val]
    if key == "summaries" and isinstance(val, list):
        return [_as_dataclass(Summary, item) for item in val]
    if key == "review_comments" and isinstance(val, list):
        return [_as_dataclass(ReviewComment, item) for item in val]
    return val


def _as_dataclass(cls, d: dict) -> Any:
    return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})
