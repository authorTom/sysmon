"""
Memory metrics collector.
"""

from dataclasses import dataclass

import psutil


@dataclass
class MemoryMetrics:
    """Container for memory metrics."""

    # RAM
    total_bytes: int
    available_bytes: int
    used_bytes: int
    percent: float

    # Swap
    swap_total_bytes: int
    swap_used_bytes: int
    swap_free_bytes: int
    swap_percent: float


class MemoryCollector:
    """Collects memory usage metrics using psutil."""

    def collect(self) -> MemoryMetrics:
        """
        Collect current memory metrics.

        Returns:
            MemoryMetrics object with current memory data
        """
        # Get virtual memory (RAM)
        mem = psutil.virtual_memory()

        # Get swap memory
        swap = psutil.swap_memory()

        return MemoryMetrics(
            total_bytes=mem.total,
            available_bytes=mem.available,
            used_bytes=mem.used,
            percent=mem.percent,
            swap_total_bytes=swap.total,
            swap_used_bytes=swap.used,
            swap_free_bytes=swap.free,
            swap_percent=swap.percent,
        )

    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """
        Format bytes to human-readable string.

        Args:
            bytes_value: Number of bytes

        Returns:
            Human-readable string (e.g., "8.5 GB")
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(bytes_value) < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
