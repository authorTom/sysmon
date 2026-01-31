"""
Alert utilities for color-coded threshold warnings.
"""

from rich.style import Style


# Threshold levels (percentage)
THRESHOLD_WARNING = 60
THRESHOLD_CRITICAL = 80

# Color definitions
COLOR_HEALTHY = "green"
COLOR_WARNING = "yellow"
COLOR_CRITICAL = "red"

# Styles for Rich
STYLE_HEALTHY = Style(color="green")
STYLE_WARNING = Style(color="yellow")
STYLE_CRITICAL = Style(color="red", bold=True)


def get_alert_color(percentage: float) -> str:
    """
    Get the appropriate color based on usage percentage.

    Args:
        percentage: Usage percentage (0-100)

    Returns:
        Color name string for Rich
    """
    if percentage >= THRESHOLD_CRITICAL:
        return COLOR_CRITICAL
    elif percentage >= THRESHOLD_WARNING:
        return COLOR_WARNING
    return COLOR_HEALTHY


def get_alert_style(percentage: float) -> Style:
    """
    Get the appropriate Rich Style based on usage percentage.

    Args:
        percentage: Usage percentage (0-100)

    Returns:
        Rich Style object
    """
    if percentage >= THRESHOLD_CRITICAL:
        return STYLE_CRITICAL
    elif percentage >= THRESHOLD_WARNING:
        return STYLE_WARNING
    return STYLE_HEALTHY


def get_status_text(percentage: float) -> str:
    """
    Get a status text label based on usage percentage.

    Args:
        percentage: Usage percentage (0-100)

    Returns:
        Status text string
    """
    if percentage >= THRESHOLD_CRITICAL:
        return "CRITICAL"
    elif percentage >= THRESHOLD_WARNING:
        return "WARNING"
    return "OK"


def format_with_alert(value: str, percentage: float) -> str:
    """
    Format a value string with Rich color markup based on percentage.

    Args:
        value: The string value to format
        percentage: Usage percentage for color selection

    Returns:
        Rich markup formatted string
    """
    color = get_alert_color(percentage)
    return f"[{color}]{value}[/{color}]"
