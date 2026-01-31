"""
Main monitor class with live display.
"""

import signal
import sys
import time
from typing import Optional

from rich.console import Console
from rich.live import Live

from .display.dashboard import Dashboard


class Monitor:
    """Main system monitor with real-time updating display."""

    def __init__(
        self,
        refresh_rate: float = 2.0,
        show_processes: bool = True,
        show_docker: bool = True,
    ):
        """
        Initialize the system monitor.

        Args:
            refresh_rate: Refresh interval in seconds (default 2.0)
            show_processes: Whether to show the process list
            show_docker: Whether to show Docker container metrics
        """
        self.refresh_rate = refresh_rate
        self.show_processes = show_processes
        self.show_docker = show_docker
        self.console = Console()
        self.dashboard = Dashboard(show_processes=show_processes, show_docker=show_docker)
        self._running = False

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully."""
        self._running = False

    def run(self) -> None:
        """
        Start the monitor with live updating display.

        Runs until Ctrl+C is pressed.
        """
        # Set up signal handlers for graceful exit
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self._running = True

        try:
            with Live(
                self.dashboard.render(),
                console=self.console,
                refresh_per_second=1,
                screen=True,
            ) as live:
                while self._running:
                    try:
                        live.update(self.dashboard.render())
                        time.sleep(self.refresh_rate)
                    except KeyboardInterrupt:
                        break
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            sys.exit(1)
        finally:
            self.console.print("\n[dim]Monitor stopped.[/dim]")

    def run_once(self) -> None:
        """
        Run a single collection and display cycle.

        Useful for testing or one-shot display.
        """
        self.console.print(self.dashboard.render())
