"""
CPU metrics collector.
"""

from dataclasses import dataclass
from typing import List, Optional

import psutil


@dataclass
class CPUMetrics:
    """Container for CPU metrics."""

    overall_percent: float
    per_core_percent: List[float]
    frequency_current: Optional[float]
    frequency_max: Optional[float]
    core_count: int
    thread_count: int


class CPUCollector:
    """Collects CPU usage metrics using psutil."""

    def __init__(self):
        """Initialize the CPU collector."""
        self._core_count = psutil.cpu_count(logical=False) or 1
        self._thread_count = psutil.cpu_count(logical=True) or 1

    def collect(self) -> CPUMetrics:
        """
        Collect current CPU metrics.

        Returns:
            CPUMetrics object with current CPU data
        """
        # Get overall CPU percentage (non-blocking with interval=None uses cached value)
        overall = psutil.cpu_percent(interval=None)

        # Get per-core percentages
        per_core = psutil.cpu_percent(interval=None, percpu=True)

        # Get CPU frequency (may not be available on all systems)
        freq_current = None
        freq_max = None
        try:
            freq = psutil.cpu_freq()
            if freq:
                freq_current = freq.current
                freq_max = freq.max
        except (AttributeError, NotImplementedError):
            pass

        return CPUMetrics(
            overall_percent=overall,
            per_core_percent=per_core,
            frequency_current=freq_current,
            frequency_max=freq_max,
            core_count=self._core_count,
            thread_count=self._thread_count,
        )

    @staticmethod
    def prime():
        """
        Prime the CPU percentage calculation.
        Call this once at startup to initialize the baseline.
        """
        psutil.cpu_percent(interval=None)
        psutil.cpu_percent(interval=None, percpu=True)
