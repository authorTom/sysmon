"""
Circular buffer for storing metric history data.
"""

from collections import deque
from typing import List, Optional


class HistoryBuffer:
    """A circular buffer that stores historical metric values for sparkline graphs."""

    def __init__(self, max_size: int = 60):
        """
        Initialize the history buffer.

        Args:
            max_size: Maximum number of values to store (default 60 = 2 min at 2s refresh)
        """
        self._buffer: deque = deque(maxlen=max_size)
        self._max_size = max_size

    def add(self, value: float) -> None:
        """Add a new value to the buffer."""
        self._buffer.append(value)

    def get_values(self) -> List[float]:
        """Get all values in the buffer as a list."""
        return list(self._buffer)

    def get_latest(self) -> Optional[float]:
        """Get the most recent value, or None if empty."""
        return self._buffer[-1] if self._buffer else None

    def get_average(self) -> float:
        """Get the average of all values in the buffer."""
        if not self._buffer:
            return 0.0
        return sum(self._buffer) / len(self._buffer)

    def get_min(self) -> float:
        """Get the minimum value in the buffer."""
        return min(self._buffer) if self._buffer else 0.0

    def get_max(self) -> float:
        """Get the maximum value in the buffer."""
        return max(self._buffer) if self._buffer else 0.0

    def clear(self) -> None:
        """Clear all values from the buffer."""
        self._buffer.clear()

    def __len__(self) -> int:
        """Return the current number of values in the buffer."""
        return len(self._buffer)

    @property
    def is_full(self) -> bool:
        """Check if the buffer is at maximum capacity."""
        return len(self._buffer) >= self._max_size
