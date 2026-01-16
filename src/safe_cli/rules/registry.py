"""
Rule registry for managing and applying safety rules.
"""

from typing import List, Optional

from safe_cli.core.parser import ParsedCommand
from safe_cli.rules.base import Rule, RuleMatch
from safe_cli.rules.docker import (
    DockerRmiRule,
    DockerRmRule,
    DockerSystemPruneRule,
    DockerVolumePruneRule,
)
from safe_cli.rules.filesystem import (
    ChmodRule,
    ChownRule,
    CpRule,
    MvRule,
    RmRule,
)
from safe_cli.rules.git import (
    GitBranchDeleteRule,
    GitCleanRule,
    GitPushForceRule,
    GitResetRule,
)
from safe_cli.rules.system import (
    DdRule,
    KillRule,
    MkfsRule,
    ShutdownRule,
    SudoRule,
)
from safe_cli.utils.constants import DangerLevel


class RuleRegistry:
    """Registry for managing safety rules."""

    def __init__(self) -> None:
        """Initialize the registry with default rules."""
        self._rules: List[Rule] = []
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """Register all default safety rules."""
        # Filesystem rules
        self.register(RmRule())
        self.register(MvRule())
        self.register(CpRule())
        self.register(ChmodRule())
        self.register(ChownRule())

        # Git rules
        self.register(GitResetRule())
        self.register(GitPushForceRule())
        self.register(GitCleanRule())
        self.register(GitBranchDeleteRule())

        # Docker rules
        self.register(DockerSystemPruneRule())
        self.register(DockerRmRule())
        self.register(DockerRmiRule())
        self.register(DockerVolumePruneRule())

        # System rules
        self.register(SudoRule())
        self.register(DdRule())
        self.register(KillRule())
        self.register(ShutdownRule())
        self.register(MkfsRule())

    def register(self, rule: Rule) -> None:
        """
        Register a new rule.

        Args:
            rule: Rule to register
        """
        if not isinstance(rule, Rule):
            raise TypeError(f"Expected Rule instance, got {type(rule)}")

        # Check for duplicate names
        if any(r.name == rule.name for r in self._rules):
            raise ValueError(f"Rule with name '{rule.name}' already registered")

        self._rules.append(rule)

    def unregister(self, rule_name: str) -> bool:
        """
        Unregister a rule by name.

        Args:
            rule_name: Name of rule to unregister

        Returns:
            True if rule was found and removed, False otherwise
        """
        for i, rule in enumerate(self._rules):
            if rule.name == rule_name:
                self._rules.pop(i)
                return True
        return False

    def get_rule(self, rule_name: str) -> Optional[Rule]:
        """
        Get a rule by name.

        Args:
            rule_name: Name of rule to get

        Returns:
            Rule if found, None otherwise
        """
        for rule in self._rules:
            if rule.name == rule_name:
                return rule
        return None

    def get_all_rules(self) -> List[Rule]:
        """
        Get all registered rules.

        Returns:
            List of all rules
        """
        return self._rules.copy()

    def find_matching_rules(self, command: ParsedCommand) -> List[Rule]:
        """
        Find all rules that match the command.

        Args:
            command: Parsed command to check

        Returns:
            List of matching rules
        """
        return [rule for rule in self._rules if rule.matches(command)]

    def analyze_command(self, command: ParsedCommand) -> List[RuleMatch]:
        """
        Analyze command against all matching rules.

        Args:
            command: Parsed command to analyze

        Returns:
            List of rule matches
        """
        matching_rules = self.find_matching_rules(command)
        return [rule.analyze(command) for rule in matching_rules]

    def get_highest_danger_level(self, command: ParsedCommand) -> DangerLevel:
        """
        Get the highest danger level from all matching rules.

        Args:
            command: Parsed command to analyze

        Returns:
            Highest danger level found, or SAFE if no rules match
        """
        matches = self.analyze_command(command)

        if not matches:
            return DangerLevel.SAFE

        return max(match.danger_level for match in matches)

    def clear(self) -> None:
        """Clear all registered rules."""
        self._rules.clear()

    def __len__(self) -> int:
        """Get number of registered rules."""
        return len(self._rules)

    def __repr__(self) -> str:
        """String representation."""
        return f"<RuleRegistry: {len(self._rules)} rules>"
