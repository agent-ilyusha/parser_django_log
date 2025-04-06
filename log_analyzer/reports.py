# -- coding: utf-8
"""Report generation module."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, Protocol

from log_analyzer.models import HandlersReport
from log_analyzer.parser import parse_log_files


class ReportFormatter(Protocol):
    """Protocol for report formatters."""

    def format(self, report: HandlersReport) -> str:
        """Format the report as a string."""
        ...


class Report(ABC):
    """Base class for all reports."""

    name: str

    @abstractmethod
    def generate(self, log_files: Iterator[Path]) -> str:
        """Generate the report."""
        pass


class HandlersReportFormatter:
    """Formatter for handlers report."""

    def format(self, report: HandlersReport) -> str:
        """Format the handlers report as a string."""
        lines = []

        # Add total requests
        lines.append(f"Total requests: {report.total_requests}\n")

        lines.append("HANDLER               \tDEBUG  \tINFO   \tWARNING\tERROR  \tCRITICAL")

        total_debug = total_info = total_warning = total_error = total_critical = 0
        
        for stats in report.get_sorted_handlers():
            lines.append(
                f"{stats.handler:<20}\t{stats.debug:<7}\t{stats.info:<7}\t"
                f"{stats.warning:<7}\t{stats.error:<7}\t{stats.critical:<7}"
            )
            total_debug += stats.debug
            total_info += stats.info
            total_warning += stats.warning
            total_error += stats.error
            total_critical += stats.critical

        lines.append(
            f"{'':20}\t{total_debug:<7}\t{total_info:<7}\t"
            f"{total_warning:<7}\t{total_error:<7}\t{total_critical:<7}"
        )

        return "\n".join(lines)


class HandlersReport(Report):
    """Handlers report implementation."""

    name = "handlers"

    def __init__(self, formatter: ReportFormatter = None):
        """Initialize the report with an optional formatter."""
        self.formatter = formatter or HandlersReportFormatter()

    def generate(self, log_files: Iterator[Path]) -> str:
        """Generate the handlers report."""
        report = parse_log_files(log_files)
        return self.formatter.format(report)
