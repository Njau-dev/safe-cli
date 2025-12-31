"""
Command analyzer for safety assessment.
"""

from dataclasses import dataclass
from typing import List, Optional

from safe_cli.core.parser import ParsedCommand
from safe_cli.rules.base import RuleMatch
from safe_cli.rules.registry import RuleRegistry
from safe_cli.utils.constants import DangerLevel


@dataclass
class AnalysisResult:
    """Result of command analysis."""

    command: ParsedCommand
    danger_level: DangerLevel
    matches: List[RuleMatch]
    primary_warning: str
    all_warnings: List[str]
    suggestions: List[str]
    safe_alternatives: List[str]

    @property
    def is_safe(self) -> bool:
        """Check if command is considered safe."""
        return self.danger_level in [DangerLevel.SAFE, DangerLevel.LOW]

    @property
    def requires_confirmation(self) -> bool:
        """Check if command requires user confirmation."""
        return self.danger_level.requires_confirmation

    @property
    def has_suggestions(self) -> bool:
        """Check if there are any suggestions."""
        return len(self.suggestions) > 0

    @property
    def has_safe_alternatives(self) -> bool:
        """Check if there are safe alternatives."""
        return len(self.safe_alternatives) > 0


class CommandAnalyzer:
    """Analyzes commands for safety risks."""

    def __init__(self, registry: Optional[RuleRegistry] = None) -> None:
        """
        Initialize analyzer.

        Args:
            registry: Rule registry to use. Creates default if None.
        """
        self.registry = registry if registry else RuleRegistry()

    def analyze(self, command: ParsedCommand) -> AnalysisResult:
        """
        Analyze a command for safety risks.

        Args:
            command: Parsed command to analyze

        Returns:
            AnalysisResult with aggregated warnings and suggestions
        """
        # Get all matching rules
        matches = self.registry.analyze_command(command)

        # If no matches, command is safe
        if not matches:
            return self._create_safe_result(command)

        # Get highest danger level
        danger_level = max(match.danger_level for match in matches)

        # Aggregate warnings, suggestions, and alternatives
        primary_warning = self._get_primary_warning(matches, danger_level)
        all_warnings = self._aggregate_warnings(matches)
        suggestions = self._aggregate_suggestions(matches)
        safe_alternatives = self._aggregate_safe_alternatives(matches)

        return AnalysisResult(
            command=command,
            danger_level=danger_level,
            matches=matches,
            primary_warning=primary_warning,
            all_warnings=all_warnings,
            suggestions=suggestions,
            safe_alternatives=safe_alternatives,
        )

    def _create_safe_result(self, command: ParsedCommand) -> AnalysisResult:
        """Create a safe analysis result."""
        return AnalysisResult(
            command=command,
            danger_level=DangerLevel.SAFE,
            matches=[],
            primary_warning="No safety concerns detected.",
            all_warnings=[],
            suggestions=[],
            safe_alternatives=[],
        )

    def _get_primary_warning(
        self, matches: List[RuleMatch], danger_level: DangerLevel
    ) -> str:
        """
        Get the primary warning message.

        Args:
            matches: List of rule matches
            danger_level: Highest danger level

        Returns:
            Primary warning message
        """
        # Find the match with the highest danger level
        primary_match = max(matches, key=lambda m: m.danger_level)
        return primary_match.message

    def _aggregate_warnings(self, matches: List[RuleMatch]) -> List[str]:
        """
        Aggregate all warning messages.

        Args:
            matches: List of rule matches

        Returns:
            List of unique warning messages
        """
        warnings = [match.message for match in matches]
        # Remove duplicates while preserving order
        seen = set()
        unique_warnings = []
        for warning in warnings:
            if warning not in seen:
                seen.add(warning)
                unique_warnings.append(warning)
        return unique_warnings

    def _aggregate_suggestions(self, matches: List[RuleMatch]) -> List[str]:
        """
        Aggregate all suggestions.

        Args:
            matches: List of rule matches

        Returns:
            List of unique suggestions
        """
        suggestions = [
            match.suggestion
            for match in matches
            if match.suggestion is not None
        ]
        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)
        return unique_suggestions

    def _aggregate_safe_alternatives(self, matches: List[RuleMatch]) -> List[str]:
        """
        Aggregate safe alternative commands.

        Args:
            matches: List of rule matches

        Returns:
            List of unique safe alternatives
        """
        alternatives = [
            match.safe_alternative
            for match in matches
            if match.safe_alternative is not None
        ]
        # Remove duplicates while preserving order
        seen = set()
        unique_alternatives = []
        for alternative in alternatives:
            if alternative not in seen:
                seen.add(alternative)
                unique_alternatives.append(alternative)
        return unique_alternatives

    def analyze_batch(self, commands: List[ParsedCommand]) -> List[AnalysisResult]:
        """
        Analyze multiple commands.

        Args:
            commands: List of parsed commands

        Returns:
            List of analysis results
        """
        return [self.analyze(cmd) for cmd in commands]

    def get_summary(self, result: AnalysisResult) -> str:
        """
        Get a human-readable summary of the analysis.

        Args:
            result: Analysis result

        Returns:
            Summary string
        """
        lines = [
            f"Command: {result.command.raw}",
            f"Danger Level: {result.danger_level.name} {result.danger_level.emoji}",
            "",
            f"Primary Warning: {result.primary_warning}",
        ]

        if len(result.all_warnings) > 1:
            lines.append("")
            lines.append("Additional Warnings:")
            for i, warning in enumerate(result.all_warnings[1:], 1):
                lines.append(f"  {i}. {warning}")

        if result.suggestions:
            lines.append("")
            lines.append("Suggestions:")
            for i, suggestion in enumerate(result.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")

        if result.safe_alternatives:
            lines.append("")
            lines.append("Safe Alternatives:")
            for i, alt in enumerate(result.safe_alternatives, 1):
                lines.append(f"  {i}. {alt}")

        return "\n".join(lines)
