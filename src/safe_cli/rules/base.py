"""
Base classes for safety rules.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

from safe_cli.core.parser import ParsedCommand
from safe_cli.utils.constants import DangerLevel


@dataclass
class RuleMatch:
    """Represents a rule match with details."""

    rule_name: str
    danger_level: DangerLevel
    message: str
    suggestion: Optional[str] = None
    safe_alternative: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate rule match data."""
        if not self.rule_name:
            raise ValueError("rule_name cannot be empty")
        if not self.message:
            raise ValueError("message cannot be empty")


class Rule(ABC):
    """Base class for all safety rules."""

    # Subclasses should override these
    name: str = "base_rule"
    description: str = "Base rule"

    @abstractmethod
    def matches(self, command: ParsedCommand) -> bool:
        """
        Check if this rule matches the command.

        Args:
            command: Parsed command to check

        Returns:
            True if rule matches, False otherwise
        """
        pass

    @abstractmethod
    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """
        Analyze the command and return match details.

        Args:
            command: Parsed command to analyze

        Returns:
            RuleMatch with danger level, message, and suggestions
        """
        pass

    def get_danger_level(self, command: ParsedCommand) -> DangerLevel:
        """
        Calculate danger level for the command.
        Override this for custom danger calculation.

        Args:
            command: Parsed command

        Returns:
            Danger level
        """
        return DangerLevel.MEDIUM

    def get_message(self, command: ParsedCommand) -> str:
        """
        Get warning message for the command.
        Override this for custom messages.

        Args:
            command: Parsed command

        Returns:
            Warning message
        """
        return f"Command '{command.command}' detected by {self.name} rule"

    def get_suggestion(self, command: ParsedCommand) -> Optional[str]:
        """
        Get safety suggestion for the command.
        Override this for custom suggestions.

        Args:
            command: Parsed command

        Returns:
            Safety suggestion or None
        """
        return None

    def get_safe_alternative(self, command: ParsedCommand) -> Optional[str]:
        """
        Get a safer alternative command.
        Override this for custom alternatives.

        Args:
            command: Parsed command

        Returns:
            Safe alternative command or None
        """
        return None

    def __repr__(self) -> str:
        """String representation."""
        return f"<Rule: {self.name}>"


class CompositeRule(Rule):
    """
    A rule that combines multiple sub-rules.
    Useful for complex checks that need multiple conditions.
    """

    def __init__(self, rules: List[Rule]) -> None:
        """
        Initialize composite rule.

        Args:
            rules: List of sub-rules to check
        """
        self.rules = rules
        self.name = "composite_rule"
        self.description = "Composite rule"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if any sub-rule matches."""
        return any(rule.matches(command) for rule in self.rules)

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze using all matching sub-rules."""
        matches = [
            rule.analyze(command) for rule in self.rules if rule.matches(command)
        ]

        if not matches:
            return RuleMatch(
                rule_name=self.name,
                danger_level=DangerLevel.SAFE,
                message="No risks detected",
            )

        # Return the highest danger level match
        highest = max(matches, key=lambda m: m.danger_level)
        return highest
