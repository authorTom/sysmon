"""
Disk/storage metrics collector.
"""

from dataclasses import dataclass
from typing import List, Optional

import psutil


@dataclass
class DiskPartitionMetrics:
    """Container for a single disk partition's metrics."""

    mountpoint: str
    device: str
    fstype: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    percent: float


@dataclass
class DiskIOMetrics:
    """Container for disk I/O metrics."""

    read_bytes: int
    write_bytes: int
    read_count: int
    write_count: int


@dataclass
class DiskMetrics:
    """Container for all disk metrics."""

    partitions: List[DiskPartitionMetrics]
    io: Optional[DiskIOMetrics]


class DiskCollector:
    """Collects disk usage and I/O metrics using psutil."""

    # Filesystem types to exclude (virtual filesystems)
    EXCLUDED_FSTYPES = {
        "squashfs",
        "tmpfs",
        "devtmpfs",
        "devfs",
        "overlay",
        "aufs",
        "none",
    }

    # Mount points to exclude
    EXCLUDED_MOUNTPOINTS = {"/boot", "/boot/efi", "/snap"}

    def __init__(self):
        """Initialize the disk collector."""
        self._last_io: Optional[DiskIOMetrics] = None

    def collect(self) -> DiskMetrics:
        """
        Collect current disk metrics.

        Returns:
            DiskMetrics object with current disk data
        """
        partitions = []

        # Get disk partitions
        for partition in psutil.disk_partitions(all=False):
            # Skip excluded filesystem types
            if partition.fstype.lower() in self.EXCLUDED_FSTYPES:
                continue

            # Skip excluded mount points
            if any(
                partition.mountpoint.startswith(excl)
                for excl in self.EXCLUDED_MOUNTPOINTS
            ):
                continue

            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append(
                    DiskPartitionMetrics(
                        mountpoint=partition.mountpoint,
                        device=partition.device,
                        fstype=partition.fstype,
                        total_bytes=usage.total,
                        used_bytes=usage.used,
                        free_bytes=usage.free,
                        percent=usage.percent,
                    )
                )
            except (PermissionError, OSError):
                # Skip partitions we can't access
                continue

        # Get disk I/O counters
        io_metrics = None
        try:
            io_counters = psutil.disk_io_counters()
            if io_counters:
                io_metrics = DiskIOMetrics(
                    read_bytes=io_counters.read_bytes,
                    write_bytes=io_counters.write_bytes,
                    read_count=io_counters.read_count,
                    write_count=io_counters.write_count,
                )
        except (AttributeError, NotImplementedError):
            pass

        return DiskMetrics(partitions=partitions, io=io_metrics)

    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """
        Format bytes to human-readable string.

        Args:
            bytes_value: Number of bytes

        Returns:
            Human-readable string (e.g., "500 GB")
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(bytes_value) < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
