# -- coding: utf-8
"""Tests for reports module."""

from pathlib import Path
from typing import Iterator

import pytest

from log_analyzer.models import HandlerStats, HandlersReport
from log_analyzer.reports import HandlersReport as HandlersReportImpl
from log_analyzer.reports import HandlersReportFormatter


@pytest.fixture
def sample_report() -> HandlersReport:
    """Create a sample report."""

    report = HandlersReport()
    report.handlers["/api/v1/test1/"] = HandlerStats(
        handler="/api/v1/test1/",
        debug=1,
        info=2,
        warning=3,
        error=4,
        critical=5
    )
    report.handlers["/api/v1/test2/"] = HandlerStats(
        handler="/api/v1/test2/",
        debug=5,
        info=4,
        warning=3,
        error=2,
        critical=1
    )
    return report


def test_handlers_report_formatter(sample_report: HandlersReport):
    """Test HandlersReportFormatter.format method."""

    formatter = HandlersReportFormatter()
    output = formatter.format(sample_report)

    # Check that output contains all the necessary information
    assert "Total requests: 30" in output
    assert "HANDLER" in output
    assert "DEBUG" in output
    assert "INFO" in output
    assert "WARNING" in output
    assert "ERROR" in output
    assert "CRITICAL" in output
    assert "/api/v1/test1/" in output
    assert "/api/v1/test2/" in output

    # Check that handlers are sorted
    lines = output.split("\n")
    data_lines = [line for line in lines if "/api/v1/" in line]
    assert data_lines[0].startswith("/api/v1/test1/")
    assert data_lines[1].startswith("/api/v1/test2/")


class MockFormatter:
    """Mock formatter for testing."""

    def format(self, report: HandlersReport) -> str:
        """Mock format method."""
        return "mock output"


def test_handlers_report_custom_formatter():
    """Test HandlersReport with custom formatter."""
    report = HandlersReportImpl(formatter=MockFormatter())
    output = report.generate([])
    assert output == "mock output"


def test_handlers_report_default_formatter():
    """Test HandlersReport with default formatter."""
    report = HandlersReportImpl()
    assert isinstance(report.formatter, HandlersReportFormatter)
