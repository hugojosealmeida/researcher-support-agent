"""Tests for structured logging configuration."""

import logging
from pathlib import Path

import pytest

from researcher_support_agent import logging_config


@pytest.fixture
def log_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tmp_path / "logs"
    monkeypatch.setattr(logging_config, "_LOG_DIR", d)
    monkeypatch.setattr(logging_config, "_LOG_FILE", d / "research.log")
    return d


class TestLogging:
    def test_console_and_file_output(self, log_dir: Path):
        logging_config.setup_logging(level="INFO", enable_file=True)
        log = logging_config.get_logger("test")
        log.info("hello logging", key="value")
        for h in logging.getLogger().handlers:
            h.flush()
        log_file = log_dir / "research.log"
        assert log_file.exists()
        content = log_file.read_text()
        assert "hello logging" in content

    def test_file_logging_disabled(self, log_dir: Path):
        logging_config.setup_logging(level="INFO", enable_file=False)
        log = logging_config.get_logger("test")
        log.info("no file")
        for h in logging.getLogger().handlers:
            h.flush()
        assert not (log_dir / "research.log").exists()

    def test_idempotent_handlers(self, log_dir: Path):
        logging_config.setup_logging(level="INFO", enable_file=True)
        logging_config.setup_logging(level="DEBUG", enable_file=True)
        logging_config.setup_logging(level="INFO", enable_file=True)
        # Only our own handlers remain tracked (no duplicates accumulated).
        assert len(logging_config._HANDLERS) == 2

    def test_level_respected(self, log_dir: Path, capsys):
        logging_config.setup_logging(level="WARNING", enable_file=False)
        log = logging_config.get_logger("test")
        log.info("should not appear")
        log.warning("should appear")
        captured = capsys.readouterr()
        assert "should appear" in captured.out
        assert "should not appear" not in captured.out
