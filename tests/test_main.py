# -- coding: utf-8
"""Tests for main module."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from main import get_available_reports, main


def test_get_available_reports():
    """Test get_available_reports function."""
    reports = get_available_reports()
    assert "handlers" in reports


def test_main_missing_file(capsys):
    """Test main function with missing file."""
    test_args = ["main.py", "non_existent.log", "--report", "handlers"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Error: Log file not found" in captured.out


def test_main_invalid_report(capsys):
    """Test main function with invalid report type."""
    test_args = ["main.py", "test.log", "--report", "invalid"]
    with patch.object(sys, "argv", test_args):
        with pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "invalid choice: 'invalid'" in captured.err
