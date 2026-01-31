"""
Main dashboard layout component.
"""

from datetime import datetime
from typing import Dict, Optional

from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..collectors.cpu import CPUCollector, CPUMetrics
from ..collectors.disk import DiskCollector, DiskMetrics
from ..collectors.docker import DockerCollector, DockerMetrics
from ..collectors.load import LoadCollector, LoadMetrics
from ..collectors.memory import MemoryCollector, MemoryMetrics
from ..utils.history import HistoryBuffer
from .docker import DockerPanel
from .panels import MetricPanel
from .processes import ProcessTable


class Dashboard:
    """Main dashboard that combines all metric panels."""

    def __init__(self, show_processes: bool = True, show_docker: bool = True):
        """
        Initialize the dashboard.

        Args:
            show_processes: Whether to show the process list
            show_docker: Whether to show Docker container metrics
        """
        self.show_processes = show_processes
        self.show_docker = show_docker

        # Collectors
        self.cpu_collector = CPUCollector()
        self.memory_collector = MemoryCollector()
        self.disk_collector = DiskCollector()
        self.load_collector = LoadCollector()
        self.docker_collector = DockerCollector()

        # Display components
        self.panel_renderer = MetricPanel()
        self.process_table = ProcessTable(max_processes=5)
        self.docker_panel = DockerPanel(max_containers=6)

        # History buffers for sparklines
        self.cpu_history = HistoryBuffer(max_size=60)
        self.memory_history = HistoryBuffer(max_size=60)
        self.load_history = HistoryBuffer(max_size=60)

        # Prime CPU collector
        CPUCollector.prime()

    def collect_metrics(self) -> Dict:
        """
        Collect all system metrics.

        Returns:
            Dictionary containing all metrics
        """
        cpu = self.cpu_collector.collect()
        memory = self.memory_collector.collect()
        disk = self.disk_collector.collect()
        load = self.load_collector.collect()

        # Update history
        self.cpu_history.add(cpu.overall_percent)
        self.memory_history.add(memory.percent)
        self.load_history.add(load.load_1min_normalized)

        metrics = {
            "cpu": cpu,
            "memory": memory,
            "disk": disk,
            "load": load,
        }

        # Collect Docker metrics if enabled
        if self.show_docker:
            metrics["docker"] = self.docker_collector.collect()

        return metrics

    def create_header(self) -> Panel:
        """Create the dashboard header."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        header_table = Table.grid(expand=True)
        header_table.add_column(justify="center", ratio=1)

        header_table.add_row(
            Text("System Monitor", style="bold magenta", justify="center")
        )
        header_table.add_row(Text(now, style="dim", justify="center"))

        return Panel(header_table, style="magenta", padding=(0, 1))

    def create_layout(self, metrics: Dict) -> Layout:
        """
        Create the full dashboard layout.

        Args:
            metrics: Dictionary of collected metrics

        Returns:
            Rich Layout object
        """
        layout = Layout()

        # Build layout sections list
        sections = [Layout(name="header", size=3), Layout(name="main", ratio=2)]

        if self.show_docker:
            sections.append(Layout(name="docker", size=12))

        if self.show_processes:
            sections.append(Layout(name="processes", size=10))

        layout.split_column(*sections)

        # Header
        layout["header"].update(self.create_header())

        # Main area split into 2x2 grid
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right"),
        )

        layout["left"].split_column(
            Layout(name="cpu"),
            Layout(name="load"),
        )

        layout["right"].split_column(
            Layout(name="memory"),
            Layout(name="disk"),
        )

        # Update panels with metrics
        layout["cpu"].update(
            self.panel_renderer.create_cpu_panel(
                metrics["cpu"], self.cpu_history.get_values()
            )
        )
        layout["memory"].update(
            self.panel_renderer.create_memory_panel(
                metrics["memory"], self.memory_history.get_values()
            )
        )
        layout["load"].update(
            self.panel_renderer.create_load_panel(
                metrics["load"], self.load_history.get_values()
            )
        )
        layout["disk"].update(self.panel_renderer.create_disk_panel(metrics["disk"]))

        # Docker containers
        if self.show_docker:
            layout["docker"].update(
                self.docker_panel.create_panel(metrics["docker"])
            )

        # Process table
        if self.show_processes:
            layout["processes"].update(self.process_table.create_panel())

        return layout

    def render(self) -> Layout:
        """
        Collect metrics and render the full dashboard.

        Returns:
            Rich Layout object ready for display
        """
        metrics = self.collect_metrics()
        return self.create_layout(metrics)
