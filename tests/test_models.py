"""Tests for models module."""
from log_analyzer.models import HandlerStats, HandlersReport


def test_handler_stats_total():
    """Test HandlerStats.total property."""
    stats = HandlerStats(
        handler="/api/v1/test/",
        debug=1,
        info=2,
        warning=3,
        error=4,
        critical=5
    )
    assert stats.total == 15


def test_handlers_report_total_requests():
    """Test HandlersReport.total_requests property."""
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
    assert report.total_requests == 30


def test_handlers_report_merge():
    """Test HandlersReport.merge method."""
    report1 = HandlersReport()
    report1.handlers["/api/v1/test/"] = HandlerStats(
        handler="/api/v1/test/",
        debug=1,
        info=2,
        warning=3,
        error=4,
        critical=5
    )

    report2 = HandlersReport()
    report2.handlers["/api/v1/test/"] = HandlerStats(
        handler="/api/v1/test/",
        debug=5,
        info=4,
        warning=3,
        error=2,
        critical=1
    )

    report1.merge(report2)
    stats = report1.handlers["/api/v1/test/"]
    assert stats.debug == 6
    assert stats.info == 6
    assert stats.warning == 6
    assert stats.error == 6
    assert stats.critical == 6


def test_handlers_report_get_sorted_handlers():
    """Test HandlersReport.get_sorted_handlers method."""
    report = HandlersReport()
    report.handlers["/api/v1/test2/"] = HandlerStats(handler="/api/v1/test2/")
    report.handlers["/api/v1/test1/"] = HandlerStats(handler="/api/v1/test1/")
    report.handlers["/api/v1/test3/"] = HandlerStats(handler="/api/v1/test3/")

    sorted_handlers = report.get_sorted_handlers()
    assert len(sorted_handlers) == 3
    assert sorted_handlers[0].handler == "/api/v1/test1/"
    assert sorted_handlers[1].handler == "/api/v1/test2/"
    assert sorted_handlers[2].handler == "/api/v1/test3/"
