<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
"""Tests for CLI commands."""

import typer.testing

from researcher_support_agent.main import app

runner = typer.testing.CliRunner()
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
"""Tests for the CLI."""

import os

import pytest
=======
"""Tests for the CLI."""


>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
"""Tests for the CLI."""


>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
from typer.testing import CliRunner

from researcher_support_agent.main import app

runner = CliRunner()
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))


class TestCLI:
    def test_version(self):
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.stdout

    def test_help(self):
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "research" in result.stdout.lower() or "Researcher" in result.stdout

    def test_doctor_help(self):
        result = runner.invoke(app, ["doctor", "--help"])
        assert result.exit_code == 0

    def test_run_help(self):
        result = runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0

    def test_run_list_phases(self):
        # "run" is a group; "list-phases" is a subcommand
        result = runner.invoke(app, ["run", "list-phases"])
        assert "Available phases" in result.stdout or result.exit_code == 0

    def test_dry_run(self):
        # "run" is a group; "run" is the subcommand for the pipeline
        result = runner.invoke(app, ["run", "run", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.stdout or "dry run" in result.stdout.lower()

    def test_conflicting_options(self):
        result = runner.invoke(app, ["run", "run", "--phase", "a", "--from", "b"])
        # Typer returns 2 for parameter errors (sys.exit(2))
        assert result.exit_code in (1, 2)
=======
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "researcher-support-agent" in result.output

    def test_list_phases(self):
        result = runner.invoke(app, ["run", "list-phases"])
        assert result.exit_code == 0
        assert "plan" in result.output
        assert "search" in result.output
        assert "screen" in result.output

    def test_run_dry_run(self, tmp_dir):
        sf = os.path.join(tmp_dir, "state.json")
        result = runner.invoke(
            app,
            ["run", "run", "--topic", "Test topic", "--state", sf, "--dry-run"],
        )
        assert result.exit_code == 0
        assert "plan: pending" in result.output

    def test_run_phase(self, tmp_dir):
        sf = os.path.join(tmp_dir, "state.json")
        result = runner.invoke(
            app,
            [
                "run",
                "run",
                "--topic",
                "Machine Learning",
                "--phase",
                "plan",
                "--state",
                sf,
            ],
        )
        assert result.exit_code == 0
        assert "Research plan built" in result.output

    def test_doctor(self):
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "Environment check passed" in result.output
<<<<<<< HEAD
>>>>>>> e45cda7 (fix: Phase B — Literature discovery and ingestion (#3))
=======
>>>>>>> 1123db3 (fix: Phase C — Evidence extraction and synthesis (#4))
=======
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "researcher-support-agent" in result.output

    def test_doctor(self):
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "Health check passed" in result.output
<<<<<<< HEAD
>>>>>>> 10d6757 (fix: Phase D — Manuscript production and quality control (#5))
=======
>>>>>>> 3eda405 (fix: Phase E — Reliability, Git integration and release (#6))
