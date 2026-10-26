"""Tests for the CLI."""

import os

import pytest
from typer.testing import CliRunner

from researcher_support_agent.main import app

runner = CliRunner()


class TestCLI:
    def test_version(self):
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
