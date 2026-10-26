"""Test conftest — shared fixtures."""

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest


@pytest.fixture()
def tmp_dir() -> Path:
    """A temporary directory that is cleaned up after the test."""
    with TemporaryDirectory() as td:
        yield Path(td)
