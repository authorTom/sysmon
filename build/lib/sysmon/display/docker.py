"""
Docker container display panel.
"""

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..collectors.docker import DockerCollector, DockerMetrics
from ..utils.alerts import get_alert_color


class DockerPanel:
    """Displays Docker container metrics in a Rich panel."""

    def __init__(self, max_containers: int = 8):
        """
        Initialize the Docker panel.

        Args:
            max_containers: Maximum number of containers to display
        """
        self.max_containers = max_containers

    def create_panel(self, metrics: DockerMetrics) -> Panel:
        """
        Create a panel displaying Docker container metrics.

        Args:
            metrics: DockerMetrics data

        Returns:
            Rich Panel object
        """
        if not metrics.available:
            return self._create_unavailable_panel(metrics.error)

        if not metrics.containers:
            return self._create_no_containers_panel(metrics)

        return self._create_containers_panel(metrics)

    def _create_unavailable_panel(self, error: str) -> Panel:
        """Create a panel when Docker is not available."""
        content = Table.grid(padding=(0, 1))
        content.add_column(justify="center")

        content.add_row(Text("Docker not available", style="dim"))
        if error:
            # Truncate long error messages
            error_short = error[:50] + "..." if len(error) > 50 else error
            content.add_row(Text(error_short, style="dim italic"))

        return Panel(
            content,
            title="[bold]Docker Containers[/bold]",
            border_style="dim",
        )

    def _create_no_containers_panel(self, metrics: DockerMetrics) -> Panel:
        """Create a panel when no containers are running."""
        content = Table.grid(padding=(0, 1))
        content.add_column(justify="center")

        content.add_row(Text("No running containers", style="dim"))
        content.add_row(
            Text(f"Total: {metrics.total_containers} containers", style="dim")
        )

        return Panel(
            content,
            title="[bold]Docker Containers[/bold]",
            border_style="blue",
        )

    def _create_containers_panel(self, metrics: DockerMetrics) -> Panel:
        """Create a panel with container metrics table."""
        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=None,
            padding=(0, 1),
            expand=True,
        )

        table.add_column("Container", justify="left", width=15)
        table.add_column("Image", justify="left", width=18)
        table.add_column("CPU%", justify="right", width=7)
        table.add_column("Memory", justify="right", width=12)
        table.add_column("MEM%", justify="right", width=7)
        table.add_column("Net I/O", justify="right", width=14)

        for container in metrics.containers[: self.max_containers]:
            # Truncate long names
            name = container.name
            if len(name) > 13:
                name = name[:12] + "…"

            image = container.image
            if len(image) > 16:
                image = image[:15] + "…"

            # Color coding
            cpu_color = get_alert_color(container.cpu_percent)
            mem_color = get_alert_color(container.memory_percent)

            # Format memory
            mem_used = DockerCollector.format_bytes(container.memory_used_bytes)
            mem_limit = DockerCollector.format_bytes(container.memory_limit_bytes)
            memory_str = f"{mem_used}"

            # Format network I/O
            net_rx = DockerCollector.format_bytes(container.network_rx_bytes)
            net_tx = DockerCollector.format_bytes(container.network_tx_bytes)
            net_io = f"↓{net_rx}/↑{net_tx}"

            table.add_row(
                name,
                Text(image, style="dim"),
                Text(f"{container.cpu_percent:.1f}", style=cpu_color),
                memory_str,
                Text(f"{container.memory_percent:.1f}", style=mem_color),
                Text(net_io, style="dim"),
            )

        # Title with container count
        title = f"[bold]Docker Containers[/bold] [dim]({metrics.running_containers}/{metrics.total_containers})[/dim]"

        return Panel(
            table,
            title=title,
            border_style="blue",
        )
