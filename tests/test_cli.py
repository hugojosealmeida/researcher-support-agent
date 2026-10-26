"""Tests for CLI commands."""

import typer.testing

from researcher_support_agent.main import app

runner = typer.testing.CliRunner()


class TestCLI:
    def test_version(self):
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

    def test_list_phases(self):
        result = runner.invoke(app, ["list-phases"])
        assert "Available phases" in result.stdout or result.exit_code == 0

    def test_dry_run(self):
        result = runner.invoke(app, ["run", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.stdout or "dry run" in result.stdout.lower()

    def test_conflicting_options(self):
        result = runner.invoke(app, ["run", "--phase", "a", "--from", "b"])
        # Typer returns 2 for parameter errors (sys.exit(2))
        assert result.exit_code in (1, 2)
