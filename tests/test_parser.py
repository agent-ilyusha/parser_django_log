# -- coding: utf-8
"""Tests for parser module."""

import csv
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Iterator

import pytest

from log_analyzer.parser import parse_log_file, parse_log_files, convert_log_line_to_json
from main import export_to_csv


@pytest.fixture
def sample_log_file() -> Iterator[Path]:
    """Create a temporary log file with sample data."""

    log_entries = [
        {
            "logger": "django.request",
            "path": "/api/v1/test/",
            "levelname": "DEBUG"
        },
        {
            "logger": "django.request",
            "path": "/api/v1/test/",
            "levelname": "INFO"
        },
        {
            "logger": "django.request",
            "path": "/api/v1/test/",
            "levelname": "WARNING"
        },
        {
            "logger": "django.request",
            "path": "/api/v1/test/",
            "levelname": "ERROR"
        },
        {
            "logger": "django.request",
            "path": "/api/v1/test/",
            "levelname": "CRITICAL"
        },
        {
            "logger": "django.other",  # Should be ignored
            "path": "/api/v1/test/",
            "levelname": "INFO"
        },
        "invalid json"  # Should be ignored
    ]

    with NamedTemporaryFile(mode='w', delete=False) as f:
        for entry in log_entries:
            if isinstance(entry, dict):
                f.write(json.dumps(entry) + "\n")
            else:
                f.write(entry + "\n")
        temp_path = Path(f.name)

    yield temp_path
    temp_path.unlink()


def test_parse_log_file(sample_log_file: Path):
    """Test parse_log_file function."""

    report = parse_log_file(sample_log_file)

    assert len(report.handlers) == 1
    stats = report.handlers["/api/v1/test/"]
    assert stats.debug == 1
    assert stats.info == 1
    assert stats.warning == 1
    assert stats.error == 1
    assert stats.critical == 1


def test_parse_log_files(sample_log_file: Path):
    """Test parse_log_files function."""

    report = parse_log_files([sample_log_file, sample_log_file])

    assert len(report.handlers) == 1
    stats = report.handlers["/api/v1/test/"]
    assert stats.debug == 2
    assert stats.info == 2
    assert stats.warning == 2
    assert stats.error == 2
    assert stats.critical == 2


def test_parse_log_files_missing_file():
    """Test parse_log_files with missing file."""
    with pytest.raises(FileNotFoundError):
        parse_log_files([Path("non_existent_file.log")])


def test_convert_log_line_to_json_valid():
    """Test converting valid log line to JSON."""
    log_line = "2025-03-27 12:13:15,000 INFO django.request: GET /api/v1/products/ 201 OK [192.168.1.72]"
    result = convert_log_line_to_json(log_line)
    
    assert result == {
        "timestamp": "2025-03-27 12:13:15,000",
        "levelname": "INFO",
        "logger": "django.request",
        "method": "GET",
        "path": "/api/v1/products/",
        "status": "201",
        "message": "OK",
        "ip": "192.168.1.72"
    }


def test_convert_log_line_to_json_invalid():
    """Test converting invalid log line to JSON."""
    # Test with invalid format
    invalid_line = "This is not a valid log line"
    result = convert_log_line_to_json(invalid_line)
    assert result == {}
    
    # Test with empty line
    empty_line = ""
    result = convert_log_line_to_json(empty_line)
    assert result == {}


def test_convert_log_line_to_json_different_levels():
    """Test converting log lines with different log levels."""
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    for level in log_levels:
        log_line = f"2025-03-27 12:13:15,000 {level} django.request: GET /api/v1/products/ 201 OK [192.168.1.72]"
        result = convert_log_line_to_json(log_line)
        assert result["levelname"] == level


def test_convert_log_line_to_json_different_paths():
    """Test converting log lines with different paths."""
    paths = [
        "/api/v1/products/",
        "/api/v1/users/123",
        "/api/v2/orders/create/",
        "/admin/login/"
    ]
    
    for path in paths:
        log_line = f"2025-03-27 12:13:15,000 INFO django.request: GET {path} 201 OK [192.168.1.72]"
        result = convert_log_line_to_json(log_line)
        assert result["path"] == path


def test_export_to_csv(sample_log_file: Path):
    """Test exporting report to CSV."""
    # Create temporary CSV file
    with NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        csv_path = Path(f.name)
    
    try:
        # Export to CSV
        export_to_csv([sample_log_file], csv_path)
        
        # Read and verify CSV contents
        with open(csv_path, 'r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # Check header
            assert rows[0] == ['Handler', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'Total']
            
            # Check data row
            assert rows[1][0] == '/api/v1/test/'  # Handler path
            assert rows[1][1:] == ['1', '1', '1', '1', '1', '5']  # Stats
            
            # Check totals row
            assert rows[2][0] == 'TOTAL'
            assert rows[2][1:] == ['1', '1', '1', '1', '1', '5']  # Total stats
            
    finally:
        # Cleanup
        csv_path.unlink()
