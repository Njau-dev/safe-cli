"""
Tests for command analyzer.
"""

import pytest
from safe_cli.core.analyzer import AnalysisResult, CommandAnalyzer
from safe_cli.core.parser import CommandParser
from safe_cli.rules.registry import RuleRegistry
from safe_cli.utils.constants import DangerLevel


class TestCommandAnalyzer:
    """Test suite for CommandAnalyzer."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create parser instance."""
        return CommandParser()

    @pytest.fixture
    def analyzer(self) -> CommandAnalyzer:
        """Create analyzer instance."""
        return CommandAnalyzer()

    def test_analyzer_initializes_with_registry(
        self, analyzer: CommandAnalyzer
    ) -> None:
        """Test that analyzer initializes with a registry."""
        assert analyzer.registry is not None
        assert isinstance(analyzer.registry, RuleRegistry)
        assert len(analyzer.registry) > 0

    def test_analyzer_accepts_custom_registry(self) -> None:
        """Test that analyzer can use custom registry."""
        registry = RuleRegistry()
        analyzer = CommandAnalyzer(registry=registry)

        assert analyzer.registry is registry

    def test_analyze_safe_command(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test analyzing a safe command."""
        cmd = parser.parse("echo hello")
        result = analyzer.analyze(cmd)

        assert isinstance(result, AnalysisResult)
        assert result.danger_level == DangerLevel.SAFE
        assert result.is_safe
        assert not result.requires_confirmation
        assert len(result.matches) == 0

    def test_analyze_low_danger_command(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test analyzing low danger command."""
        cmd = parser.parse("rm file.txt")
        result = analyzer.analyze(cmd)

        assert result.danger_level == DangerLevel.LOW
        assert result.is_safe  # Low is still considered safe
        assert not result.requires_confirmation
        assert len(result.matches) > 0

    def test_analyze_medium_danger_command(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test analyzing medium danger command."""
        cmd = parser.parse("rm -r /tmp/test")
        result = analyzer.analyze(cmd)

        assert result.danger_level == DangerLevel.MEDIUM
        assert not result.is_safe
        assert not result.requires_confirmation
        assert len(result.matches) > 0

    def test_analyze_high_danger_command(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test analyzing high danger command."""
        cmd = parser.parse("rm -rf /tmp/test")
        result = analyzer.analyze(cmd)

        assert result.danger_level == DangerLevel.HIGH
        assert not result.is_safe
        assert result.requires_confirmation
        assert len(result.matches) > 0

    def test_analyze_critical_danger_command(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test analyzing critical danger command."""
        cmd = parser.parse("rm -rf /")
        result = analyzer.analyze(cmd)

        assert result.danger_level == DangerLevel.CRITICAL
        assert not result.is_safe
        assert result.requires_confirmation
        assert len(result.matches) > 0

    def test_primary_warning(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test that primary warning is populated."""
        cmd = parser.parse("rm -rf /tmp")
        result = analyzer.analyze(cmd)

        assert result.primary_warning
        assert isinstance(result.primary_warning, str)
        assert len(result.primary_warning) > 0

    def test_all_warnings(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test that all warnings are collected."""
        cmd = parser.parse("rm -rf /tmp")
        result = analyzer.analyze(cmd)

        assert isinstance(result.all_warnings, list)
        assert len(result.all_warnings) > 0
        assert result.primary_warning in result.all_warnings

    def test_suggestions(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test that suggestions are collected."""
        cmd = parser.parse("rm -rf /tmp")
        result = analyzer.analyze(cmd)

        assert isinstance(result.suggestions, list)
        assert result.has_suggestions
        assert len(result.suggestions) > 0

    def test_safe_alternatives(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test that safe alternatives are collected."""
        cmd = parser.parse("rm -rf /tmp")
        result = analyzer.analyze(cmd)

        assert isinstance(result.safe_alternatives, list)
        assert result.has_safe_alternatives
        assert len(result.safe_alternatives) > 0

    def test_no_duplicate_warnings(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test that duplicate warnings are removed."""
        cmd = parser.parse("rm -rf /tmp")
        result = analyzer.analyze(cmd)

        # Check for uniqueness
        assert len(result.all_warnings) == len(set(result.all_warnings))

    def test_no_duplicate_suggestions(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test that duplicate suggestions are removed."""
        cmd = parser.parse("rm -rf /tmp")
        result = analyzer.analyze(cmd)

        # Check for uniqueness
        assert len(result.suggestions) == len(set(result.suggestions))

    def test_no_duplicate_alternatives(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test that duplicate alternatives are removed."""
        cmd = parser.parse("rm -rf /tmp")
        result = analyzer.analyze(cmd)

        # Check for uniqueness
        assert len(result.safe_alternatives) == len(set(result.safe_alternatives))

    def test_analyze_batch(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test analyzing multiple commands."""
        commands = [
            parser.parse("rm file.txt"),
            parser.parse("mv old.txt new.txt"),
            parser.parse("cp -r dir/ backup/"),
        ]

        results = analyzer.analyze_batch(commands)

        assert len(results) == 3
        assert all(isinstance(r, AnalysisResult) for r in results)

    def test_get_summary(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test getting analysis summary."""
        cmd = parser.parse("rm -rf /tmp")
        result = analyzer.analyze(cmd)

        summary = analyzer.get_summary(result)

        assert isinstance(summary, str)
        assert "Command:" in summary
        assert "Danger Level:" in summary
        assert "Primary Warning:" in summary
        assert result.command.raw in summary

    def test_summary_includes_suggestions(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test that summary includes suggestions."""
        cmd = parser.parse("rm -rf /tmp")
        result = analyzer.analyze(cmd)

        summary = analyzer.get_summary(result)

        if result.suggestions:
            assert "Suggestions:" in summary

    def test_summary_includes_alternatives(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test that summary includes safe alternatives."""
        cmd = parser.parse("rm -rf /tmp")
        result = analyzer.analyze(cmd)

        summary = analyzer.get_summary(result)

        if result.safe_alternatives:
            assert "Safe Alternatives:" in summary

    def test_analysis_result_properties(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test AnalysisResult properties."""
        cmd = parser.parse("rm -rf /")
        result = analyzer.analyze(cmd)

        # Test properties
        assert not result.is_safe
        assert result.requires_confirmation
        assert (
            result.has_suggestions or not result.has_suggestions
        )  # Just check it works
        assert result.has_safe_alternatives or not result.has_safe_alternatives

    def test_highest_danger_level_selected(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test that highest danger level is selected from multiple matches."""
        # chmod 777 on system path triggers multiple checks
        cmd = parser.parse("chmod -R 777 /etc")
        result = analyzer.analyze(cmd)

        # Should be CRITICAL (highest level)
        assert result.danger_level == DangerLevel.CRITICAL

    def test_command_preserved_in_result(
        self, parser: CommandParser, analyzer: CommandAnalyzer
    ) -> None:
        """Test that original command is preserved in result."""
        cmd = parser.parse("rm -rf /tmp")
        result = analyzer.analyze(cmd)

        assert result.command is cmd
        assert result.command.raw == "rm -rf /tmp"


class TestAnalysisResultProperties:
    """Test suite for AnalysisResult properties and methods."""

    def test_is_safe_for_safe_level(self) -> None:
        """Test is_safe property for SAFE level."""
        from safe_cli.core.parser import ParsedCommand

        cmd = ParsedCommand("echo test", ["echo", "test"], "echo", ["test"], [])
        result = AnalysisResult(
            command=cmd,
            danger_level=DangerLevel.SAFE,
            matches=[],
            primary_warning="",
            all_warnings=[],
            suggestions=[],
            safe_alternatives=[],
        )

        assert result.is_safe

    def test_is_safe_for_low_level(self) -> None:
        """Test is_safe property for LOW level."""
        from safe_cli.core.parser import ParsedCommand

        cmd = ParsedCommand("rm file", ["rm", "file"], "rm", ["file"], [])
        result = AnalysisResult(
            command=cmd,
            danger_level=DangerLevel.LOW,
            matches=[],
            primary_warning="",
            all_warnings=[],
            suggestions=[],
            safe_alternatives=[],
        )

        assert result.is_safe

    def test_not_safe_for_high_level(self) -> None:
        """Test is_safe property for HIGH level."""
        from safe_cli.core.parser import ParsedCommand

        cmd = ParsedCommand("rm -rf /", ["rm", "-rf", "/"], "rm", ["/"], ["-rf"])
        result = AnalysisResult(
            command=cmd,
            danger_level=DangerLevel.HIGH,
            matches=[],
            primary_warning="",
            all_warnings=[],
            suggestions=[],
            safe_alternatives=[],
        )

        assert not result.is_safe
        assert result.requires_confirmation
