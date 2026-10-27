"""Tests for the screening agent."""

<<<<<<< HEAD
<<<<<<< HEAD
from researcher_support_agent.agents.screening_agent import screen_papers
from researcher_support_agent.models.paper import Author, Paper
from researcher_support_agent.models.research_plan import ResearchPlan, ResearchQuestion
from researcher_support_agent.models.screening import ScreeningDecision


class TestScreening:
    def _make_plan(
        self,
        inclusion: list[str] | None = None,
        exclusion: list[str] | None = None,
    ) -> ResearchPlan:
        inc = inclusion if inclusion is not None else ["machine learning"]
        exc = exclusion if exclusion is not None else ["conference only"]
        return ResearchPlan(
            project_id="p1",
            topic="test",
            research_questions=[
                ResearchQuestion(
                    question="Test?",
                    search_terms=["test"],
                    synonyms={"test": ["test"]},
                    inclusion_criteria=inc,
                    exclusion_criteria=exc,
                )
            ],
        )

    def _make_paper(
        self,
        title: str = "Machine Learning for Healthcare",
        abstract: str | None = "A machine learning approach for healthcare",
    ) -> Paper:
        return Paper(title=title, abstract=abstract, authors=[Author(full_name="Alice")])

    def test_accept_paper_matching_inclusion(self):
        plan = self._make_plan()
        paper = self._make_paper()
        results = screen_papers([paper], plan)
        assert len(results) == 1
        assert results[0].decision == ScreeningDecision.ACCEPT
        assert not results[0].flagged_for_review

    def test_exclude_paper_matching_exclusion(self):
        plan = self._make_plan(
            inclusion=["machine learning"],
            exclusion=["conference only", "workshop"],
        )
        paper = Paper(
            title="Conference Paper on NLP",
            abstract="A workshop presentation on NLP",
            authors=[Author(full_name="Bob")],
        )
        results = screen_papers([paper], plan)
        assert len(results) == 1
        assert results[0].decision == ScreeningDecision.EXCLUDE

    def test_borderline_paper(self):
        plan = self._make_plan(
            inclusion=["machine learning"],
            exclusion=[],
        )
        paper = Paper(
            title="Unrelated Topic",
            abstract="About gardening techniques",
            authors=[Author(full_name="Carol")],
        )
        results = screen_papers([paper], plan)
        assert len(results) == 1
        assert results[0].decision == ScreeningDecision.BORDERLINE
        assert results[0].flagged_for_review is True

    def test_multiple_papers(self):
        plan = self._make_plan()
        papers = [
            self._make_paper("Machine Learning Study", "machine learning results"),
            self._make_paper("Gardening Tips", "gardening techniques"),
        ]
        results = screen_papers(papers, plan)
        assert len(results) == 2

    def test_all_papers_retained_in_log(self):
        """Acceptance: excluded papers are retained in the screening log."""
        plan = self._make_plan(
            inclusion=["machine learning"],
            exclusion=["conference only"],
        )
        papers = [
            self._make_paper("ML Paper", "machine learning"),
            Paper(
                title="Conference Only Paper",
                abstract="A conference-only presentation",
                authors=[Author(full_name="Dave")],
            ),
        ]
        results = screen_papers(papers, plan)
        # Both papers have screening results
        assert len(results) == 2
        # Both are traceable
        for r in results:
            assert r.reason
            assert r.paper_id

    def test_screening_result_has_uncertainty(self):
        plan = self._make_plan(inclusion=[], exclusion=[])
        paper = self._make_paper()
        results = screen_papers([paper], plan)
        assert results[0].uncertainty >= 0.0

    def test_screening_result_has_criteria_matched(self):
        plan = self._make_plan()
        paper = self._make_paper()
        results = screen_papers([paper], plan)
        assert isinstance(results[0].criteria_matched, list)

    def test_paper_status_updated(self):
        plan = self._make_plan()
        paper = self._make_paper()
        screen_papers([paper], plan)
        assert paper.processing_status == "included"

    def test_screening_by_multiple_questions(self):
        """Criteria from multiple research questions are combined."""
        plan = ResearchPlan(
            project_id="p1",
            topic="test",
            research_questions=[
                ResearchQuestion(
                    question="Q1?",
                    search_terms=["ml"],
                    synonyms={},
                    inclusion_criteria=["machine learning"],
                    exclusion_criteria=["preprint"],
                ),
                ResearchQuestion(
                    question="Q2?",
                    search_terms=["deep learning"],
                    synonyms={},
                    inclusion_criteria=["empirical"],
                    exclusion_criteria=["non-english"],
                ),
            ],
        )
        # Paper matching inclusion from both, but not exclusions
        paper = Paper(
            title="Machine Learning Empirical Study",
            abstract="An empirical machine learning study in English",
            authors=[Author(full_name="Eve")],
        )
        results = screen_papers([paper], plan)
        assert results[0].decision == ScreeningDecision.ACCEPT
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))

from researcher_support_agent.agents.screening_agent import ScreeningAgent
from researcher_support_agent.models.paper import Author, Paper
from researcher_support_agent.models.screening import ScreeningDecision


class TestScreeningAgent:
    def test_include_default(self):
        agent = ScreeningAgent()
        paper = Paper(
            title="Test Paper on X",
            authors=[Author(full_name="Alice")],
            year=2023,
        )
        result = agent.screen(paper)
        assert result.decision == ScreeningDecision.INCLUDE

    def test_exclude_with_criteria(self):
        agent = ScreeningAgent(exclusion_criteria="review, meta-analysis")
        paper = Paper(
            title="A Systematic Review of X",
            authors=[Author(full_name="Alice")],
            year=2023,
        )
        result = agent.screen(paper)
        assert result.decision == ScreeningDecision.EXCLUDE
        assert "Excluded" in result.reason

    def test_include_with_exclusion_not_matching(self):
        agent = ScreeningAgent(exclusion_criteria="animal study")
        paper = Paper(
            title="Clinical Trial of X",
            authors=[Author(full_name="Alice")],
            year=2023,
        )
        result = agent.screen(paper)
        assert result.decision == ScreeningDecision.INCLUDE

    def test_screen_batch(self):
        agent = ScreeningAgent()
        papers = [
            Paper(title="Paper A", authors=[Author(full_name="A")]),
            Paper(title="Paper B", authors=[Author(full_name="B")]),
        ]
        results = agent.screen_batch(papers)
        assert len(results) == 2

    def test_include_with_criteria(self):
        agent = ScreeningAgent(inclusion_criteria="randomized")
        paper = Paper(
            title="A Randomized Trial of X",
            authors=[Author(full_name="Alice")],
        )
        result = agent.screen(paper)
        assert result.decision == ScreeningDecision.INCLUDE
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
