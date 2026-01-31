"""
CLI entry point for the system monitor.
"""

import argparse
import sys

from . import __version__
from .monitor import Monitor


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="sysmon",
        description="A modern CLI tool for real-time Linux system performance monitoring",
        epilog="Press Ctrl+C to exit the monitor.",
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "-r", "--refresh",
        type=float,
        default=2.0,
        metavar="SECONDS",
        help="Refresh interval in seconds (default: 2.0)",
    )

    parser.add_argument(
        "--no-processes",
        action="store_true",
        help="Hide the process list",
    )

    parser.add_argument(
        "--no-docker",
        action="store_true",
        help="Hide Docker container metrics",
    )

    parser.add_argument(
        "--docker-only",
        action="store_true",
        help="Show only Docker metrics (hide processes)",
    )

    parser.add_argument(
        "--once",
        action="store_true",
        help="Display metrics once and exit (no live updates)",
    )

    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    # Validate refresh rate
    if args.refresh < 0.5:
        print("Error: Refresh rate must be at least 0.5 seconds", file=sys.stderr)
        sys.exit(1)

    if args.refresh > 60:
        print("Error: Refresh rate must not exceed 60 seconds", file=sys.stderr)
        sys.exit(1)

    # Handle docker-only mode
    show_processes = not args.no_processes
    show_docker = not args.no_docker

    if args.docker_only:
        show_processes = False
        show_docker = True

    # Create and run the monitor
    monitor = Monitor(
        refresh_rate=args.refresh,
        show_processes=show_processes,
        show_docker=show_docker,
    )

    if args.once:
        monitor.run_once()
    else:
        monitor.run()


if __name__ == "__main__":
    main()
