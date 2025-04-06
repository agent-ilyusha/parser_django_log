# -- coding: utf-8
"""Models for log analyzer."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class HandlerStats:
    """Statistics for a single handler."""
    handler: str
    debug: int = 0
    info: int = 0
    warning: int = 0
    error: int = 0
    critical: int = 0

    @property
    def total(self) -> int:
        """Get total number of requests."""
        return self.debug + self.info + self.warning + self.error + self.critical


@dataclass
class HandlersReport:
    """Report containing statistics for all handlers."""
    handlers: Dict[str, HandlerStats] = field(default_factory=dict)

    @property
    def total_requests(self) -> int:
        """Get total number of requests across all handlers."""
        return sum(handler.total for handler in self.handlers.values())

    def merge(self, other: 'HandlersReport') -> None:
        """Merge another report into this one."""
        for handler_name, stats in other.handlers.items():
            if handler_name not in self.handlers:
                self.handlers[handler_name] = HandlerStats(handler=handler_name)

            current = self.handlers[handler_name]
            current.debug += stats.debug
            current.info += stats.info
            current.warning += stats.warning
            current.error += stats.error
            current.critical += stats.critical

    def get_sorted_handlers(self) -> List[HandlerStats]:
        """Get handlers sorted by name."""
        return sorted(self.handlers.values(), key=lambda x: x.handler)
