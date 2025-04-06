# -- coding: utf-8
"""Django log analyzer CLI."""

import argparse
import csv
from pathlib import Path
from typing import Dict, Type, Iterator

from log_analyzer.models import HandlersReport as HandlersReportModel
from log_analyzer.parser import parse_log_files
from log_analyzer.reports import HandlersReport, Report


def get_available_reports() -> Dict[str, Type[Report]]:
    """Get all available reports."""
    return {
        HandlersReport.name: HandlersReport
    }


def export_to_csv(log_files: Iterator[Path], csv_file: Path) -> None:
    """Export report data to CSV file."""
    # Generate the report model directly
    report_model = parse_log_files(log_files)
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        # Write header
        writer.writerow(['Handler', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'Total'])
        
        # Write data for each handler
        for stats in report_model.get_sorted_handlers():
            writer.writerow([
                stats.handler,
                stats.debug,
                stats.info,
                stats.warning,
                stats.error,
                stats.critical,
                stats.total
            ])
        
        # Write totals
        total_debug = sum(stats.debug for stats in report_model.handlers.values())
        total_info = sum(stats.info for stats in report_model.handlers.values())
        total_warning = sum(stats.warning for stats in report_model.handlers.values())
        total_error = sum(stats.error for stats in report_model.handlers.values())
        total_critical = sum(stats.critical for stats in report_model.handlers.values())
        total_all = sum(stats.total for stats in report_model.handlers.values())
        
        writer.writerow(['TOTAL', total_debug, total_info, total_warning, 
                        total_error, total_critical, total_all])


def main() -> None:
    """Main entry point."""
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Analyze Django log files and generate reports."
    )
    parser.add_argument(
        "log_files",
        nargs="+",
        type=Path,
        help="Paths to log files to analyze"
    )
    parser.add_argument(
        "--report",
        required=True,
        choices=get_available_reports().keys(),
        help="Type of report to generate"
    )
    parser.add_argument(
        "--csv",
        type=Path,
        help="Path to output CSV file"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Get report class
    reports = get_available_reports()
    report_class = reports[args.report]
    
    # Generate report
    report = report_class()
    log_files = iter(args.log_files)
    
    try:
        # Generate and print report
        result = report.generate(log_files)
        print(result)
        
        # Export to CSV if requested
        if args.csv:
            # Get a fresh iterator for the log files
            csv_log_files = iter(args.log_files)
            export_to_csv(csv_log_files, args.csv)
            print(f"\nReport exported to CSV: {args.csv}")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
