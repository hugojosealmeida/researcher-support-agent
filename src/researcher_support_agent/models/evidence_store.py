"""SQLite-backed structured evidence repository.

Stores normalized paper metadata, summaries, extracted claims,
supporting evidence, and citation records with Markdown files as
readable artifacts.

Acceptance criteria:
- Retrieve all papers supporting a claim and all claims derived from a given paper.
- Maintain claim-to-source mapping so every statement can be traced back.
"""

from __future__ import annotations

import json
import sqlite3
<<<<<<< HEAD
<<<<<<< HEAD
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
=======
from datetime import UTC, datetime
from pathlib import Path
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
from datetime import UTC, datetime
from pathlib import Path
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

from pydantic import BaseModel

from ..models.evidence import (
    CitationRecord,
    ClaimType,
    Evidence,
<<<<<<< HEAD
<<<<<<< HEAD
    ExtractedClaim,
    EvidencePointer,
=======
    EvidencePointer,
    ExtractedClaim,
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
    EvidencePointer,
    ExtractedClaim,
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
    ResearchNote,
    ReviewFinding,
)

SCHEMA_VERSION = 1


class _DBRow(BaseModel):
    """Generic row helper."""

    _model_dump = "row"


class EvidenceRepository:
    """SQLite-backed evidence store with file-based Markdown artifacts.

    Tables:
    - papers: normalized paper metadata
    - research_notes: paper summaries
    - claims: extracted claims with claim-to-source mapping
    - evidence: evidence linking claims to papers
    - citations: citation records
    - evidence_pointers: pointers to sections/pages/tables/figures
    - review_findings: quality/bias review findings
    """

<<<<<<< HEAD
<<<<<<< HEAD
    def __init__(self, db_path: str, artifacts_dir: Optional[str] = None) -> None:
        self.db_path = db_path
        self.artifacts_dir = artifacts_dir
        self._conn: Optional[sqlite3.Connection] = None
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
    def __init__(self, db_path: str, artifacts_dir: str | None = None) -> None:
        self.db_path = db_path
        self.artifacts_dir = artifacts_dir
        self._conn: sqlite3.Connection | None = None
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
        self._connect()
        self._ensure_schema()

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    def _connect(self) -> None:
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")

    def _ensure_schema(self) -> None:
        """Create tables if they do not exist."""
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_version (
                version INTEGER PRIMARY KEY,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS papers (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                year INTEGER,
                authors TEXT,  -- JSON array
                doi TEXT,
                pmid TEXT,
                arxiv_id TEXT,
                venue TEXT,
                abstract TEXT,
                source_id TEXT,
                url TEXT,
                metadata TEXT,  -- JSON blob
                retrieved_at TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS research_notes (
                id TEXT PRIMARY KEY,
                paper_id TEXT NOT NULL UNIQUE,
                research_question TEXT,
                motivation TEXT,
                methodology TEXT,
                data_and_sample TEXT,
                main_results TEXT,
                quantitative_findings TEXT,
                contributions TEXT,
                limitations TEXT,
                open_questions TEXT,
                relevance_to_review TEXT,
                agent_interpretation TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS claims (
                id TEXT PRIMARY KEY,
                claim_text TEXT NOT NULL,
                claim_type TEXT NOT NULL DEFAULT 'empirical',
                paper_id TEXT NOT NULL,
                confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS claim_supporting_evidence (
                claim_id TEXT NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
                evidence_text TEXT NOT NULL,
                PRIMARY KEY (claim_id, evidence_text)
            );

            CREATE TABLE IF NOT EXISTS evidence (
                id TEXT PRIMARY KEY,
                claim TEXT NOT NULL,
                supporting_paper_ids TEXT,  -- JSON array
                strength TEXT NOT NULL DEFAULT 'weak',
                confidence REAL CHECK(confidence >= 0 AND confidence <= 1),
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS evidence_pointers (
                id TEXT PRIMARY KEY,
                paper_id TEXT NOT NULL,
                section TEXT,
                page INTEGER,
                table_ref TEXT,
                figure_ref TEXT,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS citations (
                id TEXT PRIMARY KEY,
                citing_paper_id TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
                cited_paper_id TEXT NOT NULL REFERENCES papers(id) ON DELETE CASCADE,
                context TEXT,
                UNIQUE(citing_paper_id, cited_paper_id)
            );

            CREATE TABLE IF NOT EXISTS review_findings (
                id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                severity TEXT NOT NULL DEFAULT 'low',
                description TEXT NOT NULL,
                resolution TEXT,
                paper_id TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            INSERT OR IGNORE INTO schema_version (version, updated_at)
                VALUES (1, datetime('now'));
            """
        )
        self._conn.commit()

    # ------------------------------------------------------------------
    # Paper operations
    # ------------------------------------------------------------------

    def store_paper(self, paper_data: dict) -> None:
        """Store or update a paper's metadata."""
        self._conn.execute(
            """
            INSERT OR REPLACE INTO papers
                (id, title, year, authors, doi, pmid, arxiv_id, venue,
                 abstract, source_id, url, metadata, retrieved_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                paper_data["id"],
                paper_data.get("title", ""),
                paper_data.get("year"),
                json.dumps(paper_data.get("authors", [])),
                paper_data.get("doi"),
                paper_data.get("pmid"),
                paper_data.get("arxiv_id"),
                paper_data.get("venue"),
                paper_data.get("abstract"),
                paper_data.get("source_id"),
                paper_data.get("url"),
                json.dumps(paper_data.get("metadata", {})),
<<<<<<< HEAD
<<<<<<< HEAD
                paper_data.get("retrieved_at") or datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
=======
                paper_data.get("retrieved_at") or datetime.now(UTC).isoformat(),
                datetime.now(UTC).isoformat(),
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
                paper_data.get("retrieved_at") or datetime.now(UTC).isoformat(),
                datetime.now(UTC).isoformat(),
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
            ),
        )
        self._conn.commit()

<<<<<<< HEAD
<<<<<<< HEAD
    def get_paper(self, paper_id: str) -> Optional[dict]:
=======
    def get_paper(self, paper_id: str) -> dict | None:
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
    def get_paper(self, paper_id: str) -> dict | None:
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
        """Retrieve a paper by ID."""
        row = self._conn.execute(
            "SELECT * FROM papers WHERE id = ?", (paper_id,)
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        d["authors"] = json.loads(d["authors"]) if d.get("authors") else []
        d["metadata"] = json.loads(d["metadata"]) if d.get("metadata") else {}
        return d

    def list_papers(self) -> list[dict]:
        """List all stored papers."""
        rows = self._conn.execute("SELECT * FROM papers ORDER BY created_at DESC").fetchall()
        papers = []
        for row in rows:
            d = dict(row)
            d["authors"] = json.loads(d["authors"]) if d.get("authors") else []
            d["metadata"] = json.loads(d["metadata"]) if d.get("metadata") else {}
            papers.append(d)
        return papers

    # ------------------------------------------------------------------
    # Research note operations
    # ------------------------------------------------------------------

    def store_research_note(self, note: ResearchNote) -> None:
        """Store a research note and optionally write a Markdown artifact."""
        self._conn.execute(
            """
            INSERT OR REPLACE INTO research_notes
                (id, paper_id, research_question, motivation, methodology,
                 data_and_sample, main_results, quantitative_findings,
                 contributions, limitations, open_questions, relevance_to_review,
                 agent_interpretation, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                note.paper_id,
                note.paper_id,
                note.research_question,
                note.motivation,
                note.methodology,
                note.data_and_sample,
                note.main_results,
                note.quantitative_findings,
                note.contributions,
                note.limitations,
                note.open_questions,
                note.relevance_to_review,
                note.agent_interpretation,
                note.created_at.isoformat(),
            ),
        )

        # Write Markdown artifact if artifacts_dir is configured
        if self.artifacts_dir:
            Path(self.artifacts_dir).mkdir(parents=True, exist_ok=True)
            md_path = Path(self.artifacts_dir) / f"note_{note.paper_id}.md"
            md_path.write_text(note.to_markdown(), encoding="utf-8")

        self._conn.commit()

<<<<<<< HEAD
<<<<<<< HEAD
    def get_research_note(self, paper_id: str) -> Optional[ResearchNote]:
=======
    def get_research_note(self, paper_id: str) -> ResearchNote | None:
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
    def get_research_note(self, paper_id: str) -> ResearchNote | None:
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
        """Retrieve a research note by paper ID."""
        row = self._conn.execute(
            """
            SELECT rn.*, p.title as paper_title
            FROM research_notes rn
            LEFT JOIN papers p ON p.id = rn.paper_id
            WHERE rn.paper_id = ?
            """,
            (paper_id,),
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        title = d.get("paper_title") or "Unknown"
        return ResearchNote(
            paper_id=d["paper_id"],
            title=title,
            year=None,
            research_question=d.get("research_question", "Unknown"),
            motivation=d.get("motivation", "Unknown"),
            methodology=d.get("methodology", "Unknown"),
            data_and_sample=d.get("data_and_sample", "Unknown"),
            main_results=d.get("main_results", "Unknown"),
            quantitative_findings=d.get("quantitative_findings", "Unknown"),
            contributions=d.get("contributions", "Unknown"),
            limitations=d.get("limitations", "Unknown"),
            open_questions=d.get("open_questions", "Unknown"),
            relevance_to_review=d.get("relevance_to_review", "Unknown"),
            agent_interpretation=d.get("agent_interpretation", "Unknown"),
            created_at=datetime.fromisoformat(d["created_at"]),
        )

    # ------------------------------------------------------------------
    # Claim operations (Phase C acceptance criteria)
    # ------------------------------------------------------------------

    def store_claim(self, claim: ExtractedClaim) -> None:
        """Store an extracted claim and its supporting evidence."""
        self._conn.execute(
            """
            INSERT INTO claims
                (id, claim_text, claim_type, paper_id, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                f"{claim.paper_id}_{claim.claim_text[:40].replace(' ', '_')}",
                claim.claim_text,
                claim.claim_type.value if hasattr(claim.claim_type, "value") else str(claim.claim_type),
                claim.paper_id,
                claim.confidence,
<<<<<<< HEAD
<<<<<<< HEAD
                datetime.now(timezone.utc).isoformat(),
=======
                datetime.now(UTC).isoformat(),
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
                datetime.now(UTC).isoformat(),
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
            ),
        )
        for ev in claim.supporting_evidence:
            self._conn.execute(
                "INSERT OR IGNORE INTO claim_supporting_evidence (claim_id, evidence_text) VALUES (?, ?)",
                (f"{claim.paper_id}_{claim.claim_text[:40].replace(' ', '_')}", ev),
            )
        self._conn.commit()

    def get_papers_supporting_claim(self, claim_text: str) -> list[str]:
        """Retrieve all paper IDs that support a given claim.

        Acceptance criterion: retrieve all papers supporting a claim.
        """
        rows = self._conn.execute(
            """
            SELECT DISTINCT p.id FROM papers p
            JOIN claims c ON c.paper_id = p.id
            WHERE c.claim_text = ?
            ORDER BY p.id
            """,
            (claim_text,),
        ).fetchall()
        return [row["id"] for row in rows]

    def get_claims_from_paper(self, paper_id: str) -> list[ExtractedClaim]:
        """Retrieve all claims extracted from a given paper.

        Acceptance criterion: retrieve all claims derived from a given paper.
        """
        rows = self._conn.execute(
            """
            SELECT c.*, cs.evidence_text
            FROM claims c
            LEFT JOIN claim_supporting_evidence cs ON cs.claim_id = c.id
            WHERE c.paper_id = ?
            ORDER BY c.id
            """,
            (paper_id,),
        ).fetchall()

        claims_dict: dict[str, ExtractedClaim] = {}
        for row in rows:
            key = row["id"]
            if key not in claims_dict:
                ct = row["claim_type"]
                try:
                    claim_type = ClaimType(ct)
                except ValueError:
                    claim_type = ClaimType.EMPIRICAL
                claims_dict[key] = ExtractedClaim(
                    claim_text=row["claim_text"],
                    claim_type=claim_type,
                    paper_id=row["paper_id"],
                    supporting_evidence=[],
                    confidence=row["confidence"] or 0.0,
                )
            if row["evidence_text"]:
                claims_dict[key].supporting_evidence.append(row["evidence_text"])

        return list(claims_dict.values())

    # ------------------------------------------------------------------
    # Evidence operations
    # ------------------------------------------------------------------

    def store_evidence(self, evidence: Evidence) -> None:
        """Store an evidence record linking a claim to supporting papers."""
        self._conn.execute(
            """
            INSERT INTO evidence
                (id, claim, supporting_paper_ids, strength, confidence, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                evidence.claim,
                evidence.claim,
                json.dumps(evidence.supporting_paper_ids),
                evidence.strength,
                evidence.confidence,
<<<<<<< HEAD
<<<<<<< HEAD
                datetime.now(timezone.utc).isoformat(),
=======
                datetime.now(UTC).isoformat(),
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
                datetime.now(UTC).isoformat(),
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
            ),
        )
        self._conn.commit()

    def get_evidence_for_claim(self, claim: str) -> list[Evidence]:
        """Retrieve all evidence records for a given claim."""
        rows = self._conn.execute(
            "SELECT * FROM evidence WHERE claim = ?", (claim,)
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            d["supporting_paper_ids"] = json.loads(d["supporting_paper_ids"]) if d.get("supporting_paper_ids") else []
            result.append(Evidence(**d))
        return result

    # ------------------------------------------------------------------
    # Evidence pointers
    # ------------------------------------------------------------------

    def store_evidence_pointer(self, pointer: EvidencePointer) -> None:
        """Store an evidence pointer to a specific location in a paper."""
        self._conn.execute(
            """
            INSERT INTO evidence_pointers
                (id, paper_id, section, page, table_ref, figure_ref, description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"{pointer.paper_id}_{pointer.section or 'default'}_{pointer.description[:30].replace(' ', '_')}",
                pointer.paper_id,
                pointer.section,
                pointer.page,
                pointer.table,
                pointer.figure,
                pointer.description,
<<<<<<< HEAD
<<<<<<< HEAD
                datetime.now(timezone.utc).isoformat(),
=======
                datetime.now(UTC).isoformat(),
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
                datetime.now(UTC).isoformat(),
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
            ),
        )
        self._conn.commit()

    def get_evidence_pointers(self, paper_id: str) -> list[EvidencePointer]:
        """Retrieve all evidence pointers for a paper."""
        rows = self._conn.execute(
            "SELECT * FROM evidence_pointers WHERE paper_id = ?", (paper_id,)
        ).fetchall()
        result = []
        for row in rows:
            d = dict(row)
            result.append(EvidencePointer(
                paper_id=d["paper_id"],
                section=d.get("section"),
                page=d.get("page"),
                table=d.get("table_ref"),
                figure=d.get("figure_ref"),
                description=d["description"],
            ))
        return result

    # ------------------------------------------------------------------
    # Citation operations
    # ------------------------------------------------------------------

    def store_citation(self, citation: CitationRecord) -> None:
        """Store a citation relationship."""
        self._conn.execute(
            """
            INSERT OR IGNORE INTO citations (id, citing_paper_id, cited_paper_id, context)
            VALUES (?, ?, ?, ?)
            """,
            (
                f"{citation.citing_paper_id}_{citation.cited_paper_id}",
                citation.citing_paper_id,
                citation.cited_paper_id,
                citation.context,
            ),
        )
        self._conn.commit()

    def get_citations_from(self, paper_id: str) -> list[CitationRecord]:
        """Get all papers cited by a given paper."""
        rows = self._conn.execute(
            "SELECT * FROM citations WHERE citing_paper_id = ?", (paper_id,)
        ).fetchall()
        return [
            CitationRecord(
                citing_paper_id=row["citing_paper_id"],
                cited_paper_id=row["cited_paper_id"],
                context=dict(row).get("context", ""),
            )
            for row in rows
        ]

    def get_citations_to(self, paper_id: str) -> list[CitationRecord]:
        """Get all papers that cite a given paper."""
        rows = self._conn.execute(
            "SELECT * FROM citations WHERE cited_paper_id = ?", (paper_id,)
        ).fetchall()
        return [
            CitationRecord(
                citing_paper_id=row["citing_paper_id"],
                cited_paper_id=row["cited_paper_id"],
                context=dict(row).get("context", ""),
            )
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Review findings
    # ------------------------------------------------------------------

    def store_review_finding(self, finding: ReviewFinding) -> None:
        """Store a review finding."""
        import uuid
        self._conn.execute(
            """
            INSERT INTO review_findings (id, category, severity, description, resolution, paper_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                finding.category,
                finding.severity,
                finding.description,
                finding.resolution,
                finding.paper_id,
<<<<<<< HEAD
<<<<<<< HEAD
                datetime.now(timezone.utc).isoformat(),
=======
                datetime.now(UTC).isoformat(),
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
                datetime.now(UTC).isoformat(),
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
            ),
        )
        self._conn.commit()

    def get_review_findings(self, paper_id: str) -> list[ReviewFinding]:
        """Get review findings for a paper."""
        rows = self._conn.execute(
            "SELECT * FROM review_findings WHERE paper_id = ?", (paper_id,)
        ).fetchall()
        return [
            ReviewFinding(
                category=row["category"],
                severity=row["severity"],
                description=row["description"],
                resolution=dict(row).get("resolution"),
                paper_id=paper_id,
            )
            for row in rows
        ]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, *args) -> None:
        self.close()
