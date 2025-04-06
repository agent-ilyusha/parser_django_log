# -- coding: utf-8
"""Log parser module."""

import json
import re
from pathlib import Path
from typing import Iterator, Dict, Any

from log_analyzer.models import HandlerStats, HandlersReport


def convert_log_line_to_json(line: str) -> Dict[str, Any]:
    """Convert a text log line to JSON format.
    
    Example input:
    2025-03-27 12:13:15,000 INFO django.request: GET /api/v1/products/ 201 OK [192.168.1.72]
    """
    pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) (\w+) ([\w\.]+): (\w+) ([^\s]+) (\d+) (\w+) \[([\d\.]+)\]"
    match = re.match(pattern, line.strip())
    
    if not match:
        return {}
        
    timestamp, level, logger, method, path, status, message, ip = match.groups()
    
    return {
        "timestamp": timestamp,
        "levelname": level,
        "logger": logger,
        "method": method,
        "path": path,
        "status": status,
        "message": message,
        "ip": ip
    }


def parse_log_file(file_path: Path) -> HandlersReport:
    """Parse a single log file and return a report."""
    report = HandlersReport()

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                # First try to parse as JSON
                try:
                    log_entry = json.loads(line)
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to parse as text format
                    log_entry = convert_log_line_to_json(line)

                if 'logger' in log_entry and log_entry['logger'] == 'django.request':
                    handler = log_entry.get('path', '')
                    level = log_entry.get('levelname', '').upper()

                    if not handler:
                        continue

                    if handler not in report.handlers:
                        report.handlers[handler] = HandlerStats(handler=handler)

                    stats = report.handlers[handler]
                    if level == 'DEBUG':
                        stats.debug += 1
                    elif level == 'INFO':
                        stats.info += 1
                    elif level == 'WARNING':
                        stats.warning += 1
                    elif level == 'ERROR':
                        stats.error += 1
                    elif level == 'CRITICAL':
                        stats.critical += 1
            except Exception:
                continue

    return report


def parse_log_files(file_paths: Iterator[Path]) -> HandlersReport:
    """Parse multiple log files and return a combined report."""
    combined_report = HandlersReport()

    for file_path in file_paths:
        if not file_path.exists():
            raise FileNotFoundError(f"Log file not found: {file_path}")

        report = parse_log_file(file_path)
        combined_report.merge(report)

    return combined_report
