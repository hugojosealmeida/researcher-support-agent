"""Test fixtures and conftest."""

import tempfile
from pathlib import Path

import pytest

from research_pipeline.state import Paper, SearchItem, Summary


@pytest.fixture()
def tmp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as td:
        yield td


@pytest.fixture()
def sample_pdf(tmp_path: Path) -> Path:
    """Create a minimal valid PDF for testing."""
    pdf_path = tmp_path / "sample.pdf"
    # Minimal valid PDF (1x1 pixel white page)
    pdf_content = b"""%PDF-1.0
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj
xref
0 4
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
trailer<</Size 4/Root 1 0 R>>
startxref
190
%%EOF"""
    pdf_path.write_bytes(pdf_content)
    return pdf_path


@pytest.fixture()
def openalex_fixture(tmp_path: Path) -> Path:
    """Create a mock OpenAlex fixture file."""
    fixture_path = tmp_path / "openalex_fixture.json"
    data = {
        "results": [
            {
                "id": "W1234567",
                "title": "Deep Learning for Natural Language Processing",
                "authorships": [
                    {
                        "author": {
                            "display_name": "Alice Smith",
                            "orcid": "https://orcid.org/0000-0001-2345-6789",
                            "affiliations": [
                                {
                                    "institution": {
                                        "display_name": "University of Example"
                                    }
                                }
                            ],
                        }
                    },
                    {"author": {"display_name": "Bob Jones"}},
                ],
                "doi": "https://doi.org/10.1234/example",
                "publication_date": "2023-06-15",
                "primary_location": {"source": {"display_name": "Journal of ML"}},
                "abstract_inverted_index": {
                    "deep": [0],
                    "learning": [1],
                    "nlp": [2],
                },
            },
            {
                "id": "W7654321",
                "title": "Transformer Models in Healthcare",
                "authorships": [{"author": {"display_name": "Carol White"}}],
                "doi": "https://doi.org/10.5678/health",
                "publication_date": "2024-01-10",
                "primary_location": {"source": {"display_name": "Health AI Journal"}},
                "abstract_inverted_index": None,
            },
        ]
    }
    import json

    fixture_path.write_text(json.dumps(data))
    return fixture_path


@pytest.fixture()
def crossref_fixture(tmp_path: Path) -> Path:
    """Create a mock Crossref fixture file."""
    fixture_path = tmp_path / "crossref_fixture.json"
    data = {
        "message": {
            "total-results": 2,
            "items": [
                {
                    "ID": 1001,
                    "title": ["Bayesian Methods in Clinical Trials"],
                    "author": [
                        {
                            "given": "David",
                            "family": "Brown",
                            "ORCID": "https://orcid.org/0000-0002-3456-7890",
                        }
                    ],
                    "DOI": "10.9999/clinical",
                    "published-print": {"date-parts": [[2022]]},
                    "container-title": ["Clinical Statistics Review"],
                    "abstract": "This paper reviews Bayesian approaches...",
                },
                {
                    "ID": 1002,
                    "title": ["Meta-analysis of Randomized Trials"],
                    "author": [
                        {"given": "Eve", "family": "Green"},
                        {"given": "Frank", "family": "Blue"},
                    ],
                    "DOI": "10.9999/meta",
                    "published-print": {"date-parts": [[2023]]},
                    "container-title": ["Evidence-Based Medicine"],
                    "abstract": None,
                },
            ],
        }
    }
    import json

    fixture_path.write_text(json.dumps(data))
    return fixture_path


@pytest.fixture()
def europe_pmc_fixture(tmp_path: Path) -> Path:
    """Create a mock Europe PMC fixture file."""
    fixture_path = tmp_path / "europe_pmc_fixture.json"
    data = {
        "hit": 5,
        "resultList": {
            "result": [
                {
                    "pmid": "36000001",
                    "pmcid": "PMC1234567",
                    "doi": "10.1186/example1",
                    "title": ["Protein Structure Prediction"],
                    "authorList": {
                        "author": [
                            {"forename": "Grace", "surname": "Lee"},
                            {"forename": "Henry", "surname": "Kim"},
                        ]
                    },
                    "publishDate": "2023-03-20",
                    "journalTitle": "Bioinformatics",
                    "abstractText": "We present a novel method...",
                },
                {
                    "pmid": "36000002",
                    "pmcid": "PMC1234568",
                    "doi": "10.1186/example2",
                    "title": ["Gene Expression Analysis"],
                    "authorList": {"author": [{"forename": "Iris", "surname": "Wang"}]},
                    "publishDate": "2024-02-15",
                    "journalTitle": "Genome Research",
                    "abstractText": "",
                },
            ]
        },
    }
    import json

    fixture_path.write_text(json.dumps(data))
    return fixture_path


@pytest.fixture()
def arxiv_fixture(tmp_path: Path) -> Path:
    """Create a mock arXiv fixture file."""
    fixture_path = tmp_path / "arxiv_fixture.json"
    data = {
        "entries": [
            {
                "id": "http://arxiv.org/abs/2301.12345",
                "title": "Attention Is All You Need Revisited",
                "summary": "We revisit the attention mechanism...",
                "published": "2023-01-25",
                "authors": [
                    {"name": "Jack Chen"},
                    {"name": "Kate Park"},
                ],
            },
            {
                "id": "http://arxiv.org/abs/2402.67890",
                "title": "Large Language Models for Science",
                "summary": "We explore LLM applications in...",
                "published": "2024-02-10",
                "authors": [{"name": "Leo Zhang"}],
            },
        ]
    }
    import json

    fixture_path.write_text(json.dumps(data))
    return fixture_path


@pytest.fixture()
def state_file(tmp_path: Path) -> Path:
    """Return a path to a temp JSON file for state persistence tests."""
    return tmp_path / "pipeline_state.json"


@pytest.fixture()
def sample_search_item() -> SearchItem:
    return SearchItem(
        title="Sample Paper",
        authors=["A. Author"],
        year=2024,
        venue="Test Journal",
        doi="10.1234/sample",
        abstract="A test abstract.",
    )


@pytest.fixture()
def sample_paper() -> Paper:
    return Paper(
        title="Sample Paper",
        authors=["A. Author"],
        year=2024,
        venue="Test Journal",
        doi="10.1234/sample",
        md_path="/tmp/sample.md",
        content="# Sample\n\nContent.",
    )


@pytest.fixture()
def sample_summary() -> Summary:
    return Summary(
        title="Sample Paper",
        doi="10.1234/sample",
        key_findings=["Finding A"],
        methods=["Method B"],
        limitations=["Limit C"],
    )
