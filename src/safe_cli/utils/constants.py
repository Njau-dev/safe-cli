"""
Constants and enums for safe-cli.
"""

from enum import Enum


class DangerLevel(Enum):
    """Danger levels for command operations."""

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def color(self) -> str:
        """Get Rich color for this danger level."""
        colors = {
            DangerLevel.SAFE: "green",
            DangerLevel.LOW: "yellow",
            DangerLevel.MEDIUM: "yellow",
            DangerLevel.HIGH: "red",
            DangerLevel.CRITICAL: "bold red",
        }
        return colors[self]

    @property
    def emoji(self) -> str:
        """Get emoji for this danger level."""
        emojis = {
            DangerLevel.SAFE: "✅",
            DangerLevel.LOW: "⚡",
            DangerLevel.MEDIUM: "⚠️",
            DangerLevel.HIGH: "🔥",
            DangerLevel.CRITICAL: "💀",
        }
        return emojis[self]

    @property
    def requires_confirmation(self) -> bool:
        """Whether this level requires user confirmation."""
        return self in [DangerLevel.HIGH, DangerLevel.CRITICAL]

    def __lt__(self, other: "DangerLevel") -> bool:
        """Compare danger levels."""
        if not isinstance(other, DangerLevel):
            return NotImplemented

        order = [
            DangerLevel.SAFE,
            DangerLevel.LOW,
            DangerLevel.MEDIUM,
            DangerLevel.HIGH,
            DangerLevel.CRITICAL,
        ]
        return order.index(self) < order.index(other)

    def __le__(self, other: "DangerLevel") -> bool:
        """Compare danger levels."""
        return self == other or self < other

    def __gt__(self, other: "DangerLevel") -> bool:
        """Compare danger levels."""
        return not self <= other

    def __ge__(self, other: "DangerLevel") -> bool:
        """Compare danger levels."""
        return not self < other


# Common dangerous flags
RECURSIVE_FLAGS = ["-r", "-R", "--recursive"]
FORCE_FLAGS = ["-f", "-F", "--force"]
ALL_FLAGS = ["-a", "-A", "--all"]
VERBOSE_FLAGS = ["-v", "--verbose"]
INTERACTIVE_FLAGS = ["-i", "-I", "--interactive"]

# Dangerous paths
DANGEROUS_PATHS = [
    "/",
    "/bin",
    "/boot",
    "/dev",
    "/etc",
    "/lib",
    "/proc",
    "/root",
    "/sbin",
    "/sys",
    "/usr",
    "/var",
]

# User paths that need caution
USER_IMPORTANT_PATHS = [
    "~",
    "$HOME",
    "~/Documents",
    "~/Desktop",
    "~/Downloads",
]
