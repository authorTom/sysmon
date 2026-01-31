"""
Process list table component.
"""

from dataclasses import dataclass
from typing import List

import psutil
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..utils.alerts import get_alert_color


@dataclass
class ProcessInfo:
    """Container for process information."""

    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    status: str


class ProcessTable:
    """Collects and displays top processes by resource usage."""

    def __init__(self, max_processes: int = 5):
        """
        Initialize the process table.

        Args:
            max_processes: Maximum number of processes to display
        """
        self.max_processes = max_processes

    def get_top_processes(self, sort_by: str = "cpu") -> List[ProcessInfo]:
        """
        Get top processes sorted by CPU or memory usage.

        Args:
            sort_by: Sort criteria ("cpu" or "memory")

        Returns:
            List of ProcessInfo objects
        """
        processes = []

        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
            try:
                info = proc.info
                processes.append(
                    ProcessInfo(
                        pid=info["pid"],
                        name=info["name"] or "Unknown",
                        cpu_percent=info["cpu_percent"] or 0.0,
                        memory_percent=info["memory_percent"] or 0.0,
                        status=info["status"] or "unknown",
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Sort by CPU or memory
        if sort_by == "memory":
            processes.sort(key=lambda p: p.memory_percent, reverse=True)
        else:
            processes.sort(key=lambda p: p.cpu_percent, reverse=True)

        return processes[: self.max_processes]

    def create_panel(self, sort_by: str = "cpu") -> Panel:
        """
        Create a panel displaying top processes.

        Args:
            sort_by: Sort criteria ("cpu" or "memory")

        Returns:
            Rich Panel object
        """
        processes = self.get_top_processes(sort_by)

        table = Table(
            show_header=True,
            header_style="bold cyan",
            box=None,
            padding=(0, 1),
            expand=True,
        )

        table.add_column("PID", justify="right", width=8)
        table.add_column("Name", justify="left", width=20)
        table.add_column("CPU%", justify="right", width=8)
        table.add_column("MEM%", justify="right", width=8)
        table.add_column("Status", justify="left", width=10)

        for proc in processes:
            # Truncate long names
            name = proc.name
            if len(name) > 18:
                name = name[:17] + "…"

            # Color-code CPU percentage
            cpu_color = get_alert_color(proc.cpu_percent)
            mem_color = get_alert_color(proc.memory_percent)

            # Status styling
            status_style = "green" if proc.status == "running" else "dim"

            table.add_row(
                str(proc.pid),
                name,
                Text(f"{proc.cpu_percent:.1f}", style=cpu_color),
                Text(f"{proc.memory_percent:.1f}", style=mem_color),
                Text(proc.status, style=status_style),
            )

        title = "Top Processes by CPU" if sort_by == "cpu" else "Top Processes by Memory"

        return Panel(
            table,
            title=f"[bold]{title}[/bold]",
            border_style="cyan",
        )
