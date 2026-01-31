"""
Sparkline graph renderer for historical metrics.
"""

from typing import List


class SparklineGraph:
    """Renders sparkline graphs using Unicode block characters."""

    # Unicode block characters for vertical bars (8 levels)
    BLOCKS = " ▁▂▃▄▅▆▇█"

    def __init__(self, width: int = 20):
        """
        Initialize the sparkline graph.

        Args:
            width: Maximum width of the sparkline in characters
        """
        self.width = width

    def render(self, values: List[float], min_val: float = 0, max_val: float = 100) -> str:
        """
        Render a sparkline graph from a list of values.

        Args:
            values: List of numeric values to graph
            min_val: Minimum value for scaling (default 0)
            max_val: Maximum value for scaling (default 100)

        Returns:
            String containing the sparkline graph
        """
        if not values:
            return " " * self.width

        # Take the last `width` values if we have more
        display_values = values[-self.width :]

        # Build the sparkline
        sparkline = ""
        value_range = max_val - min_val

        for value in display_values:
            if value_range == 0:
                index = 4  # Middle block if no range
            else:
                # Normalize to 0-1 range and map to block index (0-8)
                normalized = (value - min_val) / value_range
                normalized = max(0, min(1, normalized))  # Clamp to 0-1
                index = int(normalized * 8)

            sparkline += self.BLOCKS[index]

        # Pad with spaces if needed
        if len(sparkline) < self.width:
            sparkline = " " * (self.width - len(sparkline)) + sparkline

        return sparkline

    def render_with_color(
        self, values: List[float], min_val: float = 0, max_val: float = 100
    ) -> str:
        """
        Render a sparkline graph with color gradient based on values.

        Args:
            values: List of numeric values to graph
            min_val: Minimum value for scaling (default 0)
            max_val: Maximum value for scaling (default 100)

        Returns:
            Rich markup string with colored sparkline
        """
        if not values:
            return " " * self.width

        display_values = values[-self.width :]
        sparkline_parts = []
        value_range = max_val - min_val

        for value in display_values:
            if value_range == 0:
                index = 4
                color = "green"
            else:
                normalized = (value - min_val) / value_range
                normalized = max(0, min(1, normalized))
                index = int(normalized * 8)

                # Color based on value
                if value >= 80:
                    color = "red"
                elif value >= 60:
                    color = "yellow"
                else:
                    color = "green"

            block = self.BLOCKS[index]
            sparkline_parts.append(f"[{color}]{block}[/{color}]")

        result = "".join(sparkline_parts)

        # Pad with spaces if needed
        if len(display_values) < self.width:
            padding = " " * (self.width - len(display_values))
            result = padding + result

        return result
