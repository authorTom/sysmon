"""
Individual metric panel components.
"""

from typing import List, Optional

from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn
from rich.table import Table
from rich.text import Text

from ..collectors.cpu import CPUMetrics
from ..collectors.disk import DiskMetrics
from ..collectors.load import LoadMetrics
from ..collectors.memory import MemoryCollector, MemoryMetrics
from ..utils.alerts import get_alert_color
from .graphs import SparklineGraph


class MetricPanel:
    """Creates Rich panels for displaying metrics."""

    def __init__(self):
        """Initialize the metric panel renderer."""
        self.sparkline = SparklineGraph(width=20)

    def create_cpu_panel(
        self, metrics: CPUMetrics, history: Optional[List[float]] = None
    ) -> Panel:
        """
        Create a panel displaying CPU metrics.

        Args:
            metrics: CPUMetrics data
            history: Optional list of historical CPU percentages

        Returns:
            Rich Panel object
        """
        color = get_alert_color(metrics.overall_percent)

        # Build content
        content = Table.grid(padding=(0, 1))
        content.add_column(justify="left")
        content.add_column(justify="right")

        # Sparkline graph
        if history:
            graph = self.sparkline.render_with_color(history)
            content.add_row("History:", graph)

        # Progress bar for overall CPU
        bar = self._create_progress_bar(metrics.overall_percent, color)
        content.add_row("Overall:", bar)

        # Per-core display (show up to 8 cores in 2 columns)
        cores = metrics.per_core_percent[:8]
        for i in range(0, len(cores), 2):
            left = f"Core {i}: {cores[i]:.0f}%"
            right = f"Core {i+1}: {cores[i+1]:.0f}%" if i + 1 < len(cores) else ""
            content.add_row(
                Text(left, style=get_alert_color(cores[i])),
                Text(right, style=get_alert_color(cores[i + 1]) if right else ""),
            )

        # Frequency if available
        if metrics.frequency_current:
            freq_text = f"{metrics.frequency_current:.0f} MHz"
            if metrics.frequency_max:
                freq_text += f" / {metrics.frequency_max:.0f} MHz"
            content.add_row("Frequency:", freq_text)

        return Panel(
            content,
            title=f"[bold]CPU Usage[/bold] [{color}]{metrics.overall_percent:.1f}%[/{color}]",
            border_style=color,
        )

    def create_memory_panel(
        self, metrics: MemoryMetrics, history: Optional[List[float]] = None
    ) -> Panel:
        """
        Create a panel displaying memory metrics.

        Args:
            metrics: MemoryMetrics data
            history: Optional list of historical memory percentages

        Returns:
            Rich Panel object
        """
        color = get_alert_color(metrics.percent)

        content = Table.grid(padding=(0, 1))
        content.add_column(justify="left")
        content.add_column(justify="right")

        # Sparkline graph
        if history:
            graph = self.sparkline.render_with_color(history)
            content.add_row("History:", graph)

        # Progress bar for RAM
        bar = self._create_progress_bar(metrics.percent, color)
        content.add_row("RAM:", bar)

        # Used / Total
        used = MemoryCollector.format_bytes(metrics.used_bytes)
        total = MemoryCollector.format_bytes(metrics.total_bytes)
        content.add_row("Used:", f"{used} / {total}")

        # Available
        available = MemoryCollector.format_bytes(metrics.available_bytes)
        content.add_row("Available:", available)

        # Swap
        if metrics.swap_total_bytes > 0:
            swap_color = get_alert_color(metrics.swap_percent)
            swap_used = MemoryCollector.format_bytes(metrics.swap_used_bytes)
            swap_total = MemoryCollector.format_bytes(metrics.swap_total_bytes)
            content.add_row(
                "Swap:",
                Text(
                    f"{swap_used} / {swap_total} ({metrics.swap_percent:.1f}%)",
                    style=swap_color,
                ),
            )

        return Panel(
            content,
            title=f"[bold]Memory Usage[/bold] [{color}]{metrics.percent:.1f}%[/{color}]",
            border_style=color,
        )

    def create_load_panel(
        self, metrics: LoadMetrics, history: Optional[List[float]] = None
    ) -> Panel:
        """
        Create a panel displaying system load metrics.

        Args:
            metrics: LoadMetrics data
            history: Optional list of historical load values (normalized)

        Returns:
            Rich Panel object
        """
        # Use normalized 1-min load for color
        normalized = metrics.load_1min_normalized
        color = get_alert_color(min(normalized, 100))

        content = Table.grid(padding=(0, 1))
        content.add_column(justify="left")
        content.add_column(justify="right")

        # Sparkline graph
        if history:
            graph = self.sparkline.render_with_color(history, min_val=0, max_val=100)
            content.add_row("History:", graph)

        # Load averages
        content.add_row(
            "1 min:",
            Text(f"{metrics.load_1min:.2f}", style=get_alert_color(metrics.load_1min_normalized)),
        )
        content.add_row(
            "5 min:",
            Text(f"{metrics.load_5min:.2f}", style=get_alert_color(metrics.load_5min_normalized)),
        )
        content.add_row(
            "15 min:",
            Text(f"{metrics.load_15min:.2f}", style=get_alert_color(metrics.load_15min_normalized)),
        )

        # CPU count reference
        content.add_row("CPUs:", f"{metrics.cpu_count}")

        return Panel(
            content,
            title=f"[bold]System Load[/bold]",
            border_style=color,
        )

    def create_disk_panel(self, metrics: DiskMetrics) -> Panel:
        """
        Create a panel displaying disk metrics.

        Args:
            metrics: DiskMetrics data

        Returns:
            Rich Panel object
        """
        content = Table.grid(padding=(0, 1))
        content.add_column(justify="left", width=12)
        content.add_column(justify="left")
        content.add_column(justify="right", width=20)

        # Show each partition
        for partition in metrics.partitions[:5]:  # Limit to 5 partitions
            color = get_alert_color(partition.percent)

            # Truncate long mount points
            mount = partition.mountpoint
            if len(mount) > 10:
                mount = mount[:9] + "…"

            # Create mini progress bar
            bar = self._create_mini_bar(partition.percent, color)

            # Size info
            from ..collectors.disk import DiskCollector

            used = DiskCollector.format_bytes(partition.used_bytes)
            total = DiskCollector.format_bytes(partition.total_bytes)

            content.add_row(
                Text(mount, style="bold"),
                bar,
                Text(f"{used}/{total}", style=color),
            )

        return Panel(
            content,
            title="[bold]Disk Usage[/bold]",
            border_style="blue",
        )

    def _create_progress_bar(self, percentage: float, color: str) -> Text:
        """Create a text-based progress bar."""
        width = 20
        filled = int((percentage / 100) * width)
        empty = width - filled

        bar = "█" * filled + "░" * empty
        return Text(f"{bar} {percentage:.1f}%", style=color)

    def _create_mini_bar(self, percentage: float, color: str) -> Text:
        """Create a smaller progress bar for disk usage."""
        width = 10
        filled = int((percentage / 100) * width)
        empty = width - filled

        bar = "█" * filled + "░" * empty
        return Text(f"{bar} {percentage:.0f}%", style=color)
