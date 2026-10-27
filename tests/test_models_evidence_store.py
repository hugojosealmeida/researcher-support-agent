"""Tests for the evidence repository."""

from pathlib import Path

import pytest

from researcher_support_agent.models.evidence import (
    CitationRecord,
    Evidence,
    EvidencePointer,
    ExtractedClaim,
    ResearchNote,
    ReviewFinding,
)
from researcher_support_agent.models.evidence_store import EvidenceRepository


class TestEvidenceRepository:
    @pytest.fixture()
    def repo(self, tmp_path):
        """Create a temporary evidence repository."""
        db_path = str(tmp_path / "evidence.db")
        artifacts_dir = str(tmp_path / "artifacts")
        with EvidenceRepository(db_path=db_path, artifacts_dir=artifacts_dir) as repo:
            yield repo

    def test_create_repository(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        with EvidenceRepository(db_path=db_path) as repo:
            assert repo.db_path == db_path
            tables = repo._conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [t["name"] for t in tables]
            assert "papers" in table_names
            assert "research_notes" in table_names
            assert "claims" in table_names
            assert "evidence" in table_names

    def test_store_and_get_paper(self, repo):
        paper_data = {
            "id": "paper-1",
            "title": "Test Paper",
            "year": 2023,
            "doi": "10.1234/test",
            "authors": [{"full_name": "Alice"}],
            "metadata": {"source": "test"},
        }
        repo.store_paper(paper_data)
        result = repo.get_paper("paper-1")
        assert result is not None
        assert result["title"] == "Test Paper"
        assert result["year"] == 2023

    def test_get_nonexistent_paper(self, repo):
        assert repo.get_paper("nonexistent") is None

    def test_list_papers(self, repo):
        repo.store_paper({"id": "p1", "title": "Paper 1", "year": 2020})
        repo.store_paper({"id": "p2", "title": "Paper 2", "year": 2021})
        papers = repo.list_papers()
        assert len(papers) == 2

    def test_store_and_get_research_note(self, repo):
        note = ResearchNote(
            paper_id="paper-1",
            title="Test Paper",
            year=2023,
            research_question="What is X?",
            methodology="Survey with 100 participants.",
            main_results="X has a positive effect.",
            agent_interpretation="This paper provides foundational evidence.",
        )
        repo.store_research_note(note)
        result = repo.get_research_note("paper-1")
        assert result is not None
        assert result.main_results == "X has a positive effect."

    def test_research_note_markdown_artifact(self, repo):
        note = ResearchNote(
            paper_id="paper-1",
            title="Markdown Test",
            year=2023,
            research_question="What is X?",
            main_results="X improves Y.",
            agent_interpretation="Important finding.",
        )
        repo.store_research_note(note)
        artifacts_dir = repo.artifacts_dir
        assert artifacts_dir is not None
        md_path = Path(artifacts_dir) / "note_paper-1.md"
        assert md_path.exists()
        content = md_path.read_text(encoding="utf-8")
        assert "Markdown Test" in content
        assert "Author-reported" in content

    def test_store_and_get_claims_from_paper(self, repo):
        claim = ExtractedClaim(
            claim_text="X improves Y.",
            paper_id="paper-1",
            supporting_evidence=["Page 5: 'We observed a 20% improvement.'"],
            confidence=0.8,
        )
        repo.store_claim(claim)
        claims = repo.get_claims_from_paper("paper-1")
        assert len(claims) == 1

    def test_get_papers_supporting_claim(self, repo):
        claim = ExtractedClaim(
            claim_text="X improves Y.",
            paper_id="paper-1",
            confidence=0.8,
        )
        repo.store_paper({"id": "paper-1", "title": "Paper 1"})
        repo.store_claim(claim)
        claims = repo.get_papers_supporting_claim("X improves Y.")
        assert "paper-1" in claims

    def test_claim_to_source_mapping(self, repo):
        claim = ExtractedClaim(
            claim_text="X improves Y.",
            paper_id="paper-1",
            supporting_evidence=["Table 2: X vs Y"],
            confidence=0.85,
        )
        repo.store_paper({"id": "paper-1", "title": "Paper 1"})
        repo.store_claim(claim)
        papers = repo.get_papers_supporting_claim("X improves Y.")
        assert "paper-1" in papers

    def test_store_evidence(self, repo):
        evidence = Evidence(
            claim="X improves Y.",
            supporting_paper_ids=["paper-1", "paper-2"],
            strength="strong",
            confidence=0.85,
        )
        repo.store_evidence(evidence)
        results = repo.get_evidence_for_claim("X improves Y.")
        assert len(results) == 1

    def test_store_and_get_evidence_pointers(self, repo):
        ptr = EvidencePointer(
            paper_id="paper-1",
            section="Results",
            page=5,
            table="Table 1",
            description="Table 1 shows the main results.",
        )
        repo.store_evidence_pointer(ptr)
        pointers = repo.get_evidence_pointers("paper-1")
        assert len(pointers) == 1

    def test_store_evidence_pointer_idempotent(self, repo):
        ptr = EvidencePointer(
            paper_id="paper-1",
            section="Results",
            page=5,
            table="Table 1",
            description="Table 1 shows the main results.",
        )
        repo.store_evidence_pointer(ptr)
        repo.store_evidence_pointer(ptr)
        rows = repo._conn.execute("SELECT COUNT(*) FROM evidence_pointers").fetchone()[
            0
        ]
        assert rows == 1
        pointers = repo.get_evidence_pointers("paper-1")
        assert len(pointers) == 1

    def test_store_and_get_citations(self, repo):
        repo.store_paper({"id": "p1", "title": "Paper 1"})
        repo.store_paper({"id": "p2", "title": "Paper 2"})
        citation = CitationRecord(
            citing_paper_id="p1",
            cited_paper_id="p2",
            context="Section 2 discusses this work.",
        )
        repo.store_citation(citation)
        out = repo.get_citations_from("p1")
        assert len(out) == 1

    def test_store_review_finding(self, repo):
        finding = ReviewFinding(
            category="selection_bias",
            severity="medium",
            description="Participants were self-selected.",
            paper_id="paper-1",
        )
        repo.store_review_finding(finding)
        findings = repo.get_review_findings("paper-1")
        assert len(findings) == 1

    def test_context_manager(self, tmp_path):
        db_path = str(tmp_path / "cm.db")
        with EvidenceRepository(db_path=db_path) as repo:
            assert repo._conn is not None
