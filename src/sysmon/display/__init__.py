"""
Display module - Terminal UI components.
"""

from .dashboard import Dashboard
from .panels import MetricPanel
from .graphs import SparklineGraph
from .processes import ProcessTable
from .docker import DockerPanel

__all__ = ["Dashboard", "MetricPanel", "SparklineGraph", "ProcessTable", "DockerPanel"]
