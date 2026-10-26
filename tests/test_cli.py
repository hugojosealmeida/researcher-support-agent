"""Tests for the CLI."""


from typer.testing import CliRunner

from researcher_support_agent.main import app

runner = CliRunner()


class TestCLI:
    def test_version(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "researcher-support-agent" in result.output

    def test_doctor(self):
        result = runner.invoke(app, ["doctor"])
        assert result.exit_code == 0
        assert "Health check passed" in result.output
