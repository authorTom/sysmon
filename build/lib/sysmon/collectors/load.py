"""
System load metrics collector.
"""

from dataclasses import dataclass
from typing import Tuple

import psutil


@dataclass
class LoadMetrics:
    """Container for system load metrics."""

    load_1min: float
    load_5min: float
    load_15min: float
    cpu_count: int

    @property
    def load_1min_normalized(self) -> float:
        """Get 1-minute load as percentage of CPU count."""
        return (self.load_1min / self.cpu_count) * 100 if self.cpu_count > 0 else 0

    @property
    def load_5min_normalized(self) -> float:
        """Get 5-minute load as percentage of CPU count."""
        return (self.load_5min / self.cpu_count) * 100 if self.cpu_count > 0 else 0

    @property
    def load_15min_normalized(self) -> float:
        """Get 15-minute load as percentage of CPU count."""
        return (self.load_15min / self.cpu_count) * 100 if self.cpu_count > 0 else 0


class LoadCollector:
    """Collects system load average metrics using psutil."""

    def __init__(self):
        """Initialize the load collector."""
        self._cpu_count = psutil.cpu_count(logical=True) or 1

    def collect(self) -> LoadMetrics:
        """
        Collect current system load metrics.

        Returns:
            LoadMetrics object with current load data
        """
        try:
            load_avg: Tuple[float, float, float] = psutil.getloadavg()
        except (AttributeError, OSError):
            # getloadavg() not available on Windows
            load_avg = (0.0, 0.0, 0.0)

        return LoadMetrics(
            load_1min=load_avg[0],
            load_5min=load_avg[1],
            load_15min=load_avg[2],
            cpu_count=self._cpu_count,
        )

    def get_load_status(self, metrics: LoadMetrics) -> str:
        """
        Get a status description based on load average.

        Args:
            metrics: LoadMetrics to evaluate

        Returns:
            Status string ("Low", "Normal", "High", "Critical")
        """
        # Normalized load (load / cpu_count) thresholds
        normalized = metrics.load_1min_normalized

        if normalized < 50:
            return "Low"
        elif normalized < 80:
            return "Normal"
        elif normalized < 100:
            return "High"
        return "Critical"
