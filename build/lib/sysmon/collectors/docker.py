"""
Docker container metrics collector.
"""

from dataclasses import dataclass
from typing import List, Optional

try:
    import docker
    from docker.errors import DockerException

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False


@dataclass
class ContainerMetrics:
    """Container for a single Docker container's metrics."""

    container_id: str
    name: str
    status: str
    image: str

    # CPU metrics
    cpu_percent: float

    # Memory metrics
    memory_used_bytes: int
    memory_limit_bytes: int
    memory_percent: float

    # Network I/O
    network_rx_bytes: int
    network_tx_bytes: int

    # Block I/O
    block_read_bytes: int
    block_write_bytes: int


@dataclass
class DockerMetrics:
    """Container for all Docker metrics."""

    available: bool
    error: Optional[str]
    containers: List[ContainerMetrics]
    total_containers: int
    running_containers: int


class DockerCollector:
    """Collects Docker container metrics using the Docker SDK."""

    def __init__(self):
        """Initialize the Docker collector."""
        self._client = None
        self._available = DOCKER_AVAILABLE
        self._error: Optional[str] = None

        if self._available:
            try:
                self._client = docker.from_env()
                # Test connection
                self._client.ping()
            except Exception as e:
                self._available = False
                self._error = str(e)

    @property
    def is_available(self) -> bool:
        """Check if Docker is available and accessible."""
        return self._available and self._client is not None

    def collect(self) -> DockerMetrics:
        """
        Collect metrics from all running Docker containers.

        Returns:
            DockerMetrics object with container data
        """
        if not self.is_available:
            return DockerMetrics(
                available=False,
                error=self._error or "Docker not available",
                containers=[],
                total_containers=0,
                running_containers=0,
            )

        try:
            containers = self._client.containers.list(all=True)
            running_containers = [c for c in containers if c.status == "running"]

            container_metrics = []
            for container in running_containers:
                metrics = self._get_container_metrics(container)
                if metrics:
                    container_metrics.append(metrics)

            return DockerMetrics(
                available=True,
                error=None,
                containers=container_metrics,
                total_containers=len(containers),
                running_containers=len(running_containers),
            )

        except Exception as e:
            return DockerMetrics(
                available=False,
                error=str(e),
                containers=[],
                total_containers=0,
                running_containers=0,
            )

    def _get_container_metrics(self, container) -> Optional[ContainerMetrics]:
        """
        Get metrics for a single container.

        Args:
            container: Docker container object

        Returns:
            ContainerMetrics or None if unable to get stats
        """
        try:
            # Get container stats (non-streaming for single snapshot)
            stats = container.stats(stream=False)

            # Calculate CPU percentage
            cpu_percent = self._calculate_cpu_percent(stats)

            # Memory metrics
            memory_stats = stats.get("memory_stats", {})
            memory_used = memory_stats.get("usage", 0)
            memory_limit = memory_stats.get("limit", 1)

            # Subtract cache from memory usage if available
            cache = memory_stats.get("stats", {}).get("cache", 0)
            memory_used = max(0, memory_used - cache)

            memory_percent = (memory_used / memory_limit * 100) if memory_limit > 0 else 0

            # Network I/O
            networks = stats.get("networks", {})
            net_rx = sum(net.get("rx_bytes", 0) for net in networks.values())
            net_tx = sum(net.get("tx_bytes", 0) for net in networks.values())

            # Block I/O
            blkio_stats = stats.get("blkio_stats", {})
            io_service_bytes = blkio_stats.get("io_service_bytes_recursive", []) or []
            block_read = sum(
                entry.get("value", 0)
                for entry in io_service_bytes
                if entry.get("op") == "read"
            )
            block_write = sum(
                entry.get("value", 0)
                for entry in io_service_bytes
                if entry.get("op") == "write"
            )

            # Get container name (remove leading slash)
            name = container.name
            if name.startswith("/"):
                name = name[1:]

            # Get image name
            image = container.image.tags[0] if container.image.tags else container.image.short_id

            return ContainerMetrics(
                container_id=container.short_id,
                name=name,
                status=container.status,
                image=image,
                cpu_percent=cpu_percent,
                memory_used_bytes=memory_used,
                memory_limit_bytes=memory_limit,
                memory_percent=memory_percent,
                network_rx_bytes=net_rx,
                network_tx_bytes=net_tx,
                block_read_bytes=block_read,
                block_write_bytes=block_write,
            )

        except Exception:
            return None

    def _calculate_cpu_percent(self, stats: dict) -> float:
        """
        Calculate CPU percentage from container stats.

        Args:
            stats: Container stats dictionary

        Returns:
            CPU usage percentage
        """
        try:
            cpu_stats = stats.get("cpu_stats", {})
            precpu_stats = stats.get("precpu_stats", {})

            cpu_usage = cpu_stats.get("cpu_usage", {})
            precpu_usage = precpu_stats.get("cpu_usage", {})

            cpu_total = cpu_usage.get("total_usage", 0)
            precpu_total = precpu_usage.get("total_usage", 0)

            system_cpu = cpu_stats.get("system_cpu_usage", 0)
            presystem_cpu = precpu_stats.get("system_cpu_usage", 0)

            cpu_delta = cpu_total - precpu_total
            system_delta = system_cpu - presystem_cpu

            if system_delta > 0 and cpu_delta > 0:
                online_cpus = cpu_stats.get("online_cpus", 1)
                if online_cpus == 0:
                    online_cpus = len(cpu_usage.get("percpu_usage", [1]))
                return (cpu_delta / system_delta) * online_cpus * 100

            return 0.0

        except (KeyError, ZeroDivisionError):
            return 0.0

    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """
        Format bytes to human-readable string.

        Args:
            bytes_value: Number of bytes

        Returns:
            Human-readable string (e.g., "500 MB")
        """
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(bytes_value) < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
