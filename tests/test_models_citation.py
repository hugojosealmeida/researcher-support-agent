"""Tests for citation and bibliography models."""

from researcher_support_agent.models.citation import (
    Bibliography,
    DOIResolutionResult,
    ReferenceFormat,
    ReferenceRecord,
)


class TestReferenceRecord:
    def test_minimal(self):
        r = ReferenceRecord(
            paper_id="paper-1",
            title="Test Paper",
            authors=["Alice Smith"],
        )
        assert r.paper_id == "paper-1"
        assert r.title == "Test Paper"
        assert r.citation_key is None

    def test_get_citation_key_auto_generated(self):
        r = ReferenceRecord(
            paper_id="paper-1",
            title="Test Paper on ML",
            authors=["Alice Smith"],
            year=2023,
        )
        key = r.get_citation_key()
        assert "Smith" in key or "smith" in key
        assert "2023" in key

    def test_explicit_citation_key(self):
        r = ReferenceRecord(
            paper_id="paper-1",
            title="Test",
            authors=["Alice"],
            citation_key="alice2023test",
        )
        assert r.get_citation_key() == "alice2023test"

    def test_to_bibtex(self):
        r = ReferenceRecord(
            paper_id="p1",
            title="Attention Is All You Need",
            authors=["Alice Vaswani", "Bob Shazeer", "Noam Parmar"],
            year=2017,
            journal="Advances in Neural Information Processing Systems",
            doi="10.48550/xxx",
        )
        bibtex = r.to_bibtex("vaswani2017attention")
        assert "@article{vaswani2017attention" in bibtex
        assert "Attention Is All You Need" in bibtex
        assert "2017" in bibtex
        assert "vaswani" in bibtex.lower() or "Alice" in bibtex

    def test_to_csl_json(self):
        r = ReferenceRecord(
            paper_id="p1",
            title="Test Paper",
            authors=["Alice Smith"],
            year=2023,
            journal="Journal of Test",
        )
        csl = r.to_csl_json()
        assert csl["title"] == "Test Paper"
        assert csl["type"] == "article-journal"
        assert len(csl["author"]) == 1
        assert csl["author"][0]["family"] == "Smith"
        assert csl["published"]["literal"] == "2023"

    def test_to_apa(self):
        r = ReferenceRecord(
            paper_id="p1",
            title="Test Paper",
            authors=["Alice Smith", "Bob Jones"],
            year=2023,
            journal="Test Journal",
            volume="10",
            pages="1-20",
        )
        apa = r.to_apa()
        assert "Smith" in apa
        assert "2023" in apa
        assert "Test Paper" in apa
        assert "Test Journal" in apa

    def test_to_mla(self):
        r = ReferenceRecord(
            paper_id="p1",
            title="Test Paper",
            authors=["Alice Smith"],
            year=2023,
            journal="Test Journal",
        )
        mla = r.to_mla()
        assert "Smith" in mla
        assert "Test Paper" in mla

    def test_to_chicago(self):
        r = ReferenceRecord(
            paper_id="p1",
            title="Test Paper",
            authors=["Alice Smith"],
            year=2023,
            journal="Test Journal",
        )
        chicago = r.to_chicago()
        assert "Smith" in chicago
        assert "Test Paper" in chicago

    def test_to_vancouver(self):
        r = ReferenceRecord(
            paper_id="p1",
            title="Test Paper",
            authors=["Alice Smith"],
            year=2023,
            journal="Test Journal",
        )
        vancouver = r.to_vancouver()
        assert "Smith" in vancouver
        assert "Test Paper" in vancouver


class TestBibliography:
    def test_minimal(self):
        b = Bibliography()
        assert b.references == []

    def test_add_reference(self):
        r1 = ReferenceRecord(paper_id="p1", title="Paper 1", authors=["Alice"])
        b = Bibliography()
        b.add(r1)
        assert len(b.references) == 1
        assert b.references[0].title == "Paper 1"

    def test_add_updates_existing(self):
        r1 = ReferenceRecord(paper_id="p1", title="Paper 1", authors=["Alice"])
        r2 = ReferenceRecord(paper_id="p1", title="Paper 1 Updated", year=2023)
        b = Bibliography()
        b.add(r1)
        b.add(r2)  # Should update, not duplicate
        assert len(b.references) == 1
        assert b.references[0].year == 2023

    def test_get_by_paper_id(self):
        r1 = ReferenceRecord(paper_id="p1", title="Paper 1", authors=["Alice"])
        r2 = ReferenceRecord(paper_id="p2", title="Paper 2", authors=["Bob"])
        b = Bibliography()
        b.add(r1)
        b.add(r2)
        found = b.get_by_paper_id("p2")
        assert found is not None
        assert found.title == "Paper 2"

    def test_get_nonexistent(self):
        b = Bibliography()
        assert b.get_by_paper_id("nonexistent") is None

    def test_citation_key_map(self):
        r1 = ReferenceRecord(paper_id="p1", title="Test", authors=["Alice"], year=2023)
        r2 = ReferenceRecord(paper_id="p2", title="Test2", authors=["Bob"], year=2024)
        b = Bibliography()
        b.add(r1)
        b.add(r2)
        key_map = b.get_citation_key_map()
        assert "p1" in key_map
        assert "p2" in key_map

    def test_find_duplicates(self):
        r1 = ReferenceRecord(paper_id="p1", title="Paper 1", authors=["Alice"])
        r2 = ReferenceRecord(paper_id="p1", title="Paper 1 (dup)", authors=["Alice"])
        b = Bibliography()
        b.add(r1)
        b.add(r2)  # This should update, not create a dup by paper_id
        # Since add() updates by paper_id, there should be no duplicates
        assert len(b.references) == 1

    def test_to_bibtex(self):
        r1 = ReferenceRecord(paper_id="p1", title="Paper 1", authors=["Alice"], year=2023)
        b = Bibliography()
        b.add(r1)
        bibtex = b.to_bibtex()
        assert "@article" in bibtex
        assert "Paper 1" in bibtex

    def test_to_csl_json(self):
        r1 = ReferenceRecord(paper_id="p1", title="Paper 1", authors=["Alice"], year=2023)
        b = Bibliography()
        b.add(r1)
        csl = b.to_csl_json()
        assert len(csl) == 1
        assert csl[0]["title"] == "Paper 1"

    def test_to_format(self):
        r1 = ReferenceRecord(paper_id="p1", title="Test Paper", authors=["Alice"], year=2023)
        b = Bibliography()
        b.add(r1)
        # BibTeX
        assert "@article" in b.to_format(ReferenceFormat.BIBTEX)
        # APA
        assert "Test Paper" in b.to_format(ReferenceFormat.APA)
        # MLA
        assert "Test Paper" in b.to_format(ReferenceFormat.MLA)

    def test_validate_integrity_no_uncited(self):
        r1 = ReferenceRecord(paper_id="p1", title="Paper 1", authors=["Alice"])
        r2 = ReferenceRecord(paper_id="p2", title="Paper 2", authors=["Bob"])
        b = Bibliography()
        b.add(r1)
        b.add(r2)
        # Both are cited
        in_text = {"p1", "p2"}
        issues = b.validate_integrity(in_text)
        assert issues == []

    def test_validate_integrity_uncited(self):
        r1 = ReferenceRecord(paper_id="p1", title="Paper 1", authors=["Alice"])
        b = Bibliography()
        b.add(r1)
        # p1 is not cited in text
        in_text = set()
        issues = b.validate_integrity(in_text)
        assert len(issues) > 0
        assert "Uncited" in issues[0]


class TestDOIResolutionResult:
    def test_minimal(self):
        d = DOIResolutionResult(doi="10.1234/test", resolved=False)
        assert d.doi == "10.1234/test"
        assert d.resolved is False
        assert d.title is None

    def test_resolved(self):
        d = DOIResolutionResult(
            doi="10.1234/test",
            resolved=True,
            title="Test Paper",
            year=2023,
        )
        assert d.resolved is True
        assert d.title == "Test Paper"
        assert d.year == 2023
