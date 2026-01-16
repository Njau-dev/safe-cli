"""
Tests for display formatter.
"""

from io import StringIO

import pytest
from rich.console import Console
from safe_cli.core.analyzer import AnalysisResult
from safe_cli.core.parser import ParsedCommand
from safe_cli.ui.display import DisplayFormatter
from safe_cli.utils.constants import DangerLevel


class TestDisplayFormatter:
    """Test suite for DisplayFormatter."""

    @pytest.fixture
    def console(self) -> Console:
        """Create console with string output."""
        return Console(file=StringIO(), width=80)

    @pytest.fixture
    def formatter(self, console: Console) -> DisplayFormatter:
        """Create formatter instance."""
        return DisplayFormatter(console)

    @pytest.fixture
    def safe_result(self) -> AnalysisResult:
        """Create a safe analysis result."""
        cmd = ParsedCommand("echo test", ["echo", "test"], "echo", ["test"], [])
        return AnalysisResult(
            command=cmd,
            danger_level=DangerLevel.SAFE,
            matches=[],
            primary_warning="No issues",
            all_warnings=[],
            suggestions=[],
            safe_alternatives=[],
        )

    @pytest.fixture
    def dangerous_result(self) -> AnalysisResult:
        """Create a dangerous analysis result."""
        cmd = ParsedCommand("rm -rf /", ["rm", "-rf", "/"], "rm", ["/"], ["-rf"])
        return AnalysisResult(
            command=cmd,
            danger_level=DangerLevel.CRITICAL,
            matches=[],
            primary_warning="This will delete everything!",
            all_warnings=["This will delete everything!", "No recovery possible"],
            suggestions=["Don't do this", "Use interactive mode"],
            safe_alternatives=["rm -i -rf /"],
        )

    def test_formatter_initializes(self, formatter: DisplayFormatter) -> None:
        """Test that formatter initializes."""
        assert formatter is not None
        assert formatter.console is not None

    def test_display_safe_analysis(
        self, formatter: DisplayFormatter, safe_result: AnalysisResult
    ) -> None:
        """Test displaying safe command analysis."""
        # Should not raise
        formatter.display_analysis(safe_result)

        output = formatter.console.file.getvalue()
        assert "SAFE" in output or "safe" in output.lower()

    def test_display_dangerous_analysis(
        self, formatter: DisplayFormatter, dangerous_result: AnalysisResult
    ) -> None:
        """Test displaying dangerous command analysis."""
        formatter.display_analysis(dangerous_result)

        output = formatter.console.file.getvalue()
        assert "CRITICAL" in output
        assert dangerous_result.primary_warning in output

    def test_display_with_dry_run_flag(
        self, formatter: DisplayFormatter, safe_result: AnalysisResult
    ) -> None:
        """Test display with dry run flag."""
        formatter.display_analysis(safe_result, dry_run=True)

        output = formatter.console.file.getvalue()
        assert "Dry Run" in output or "dry run" in output.lower()

    def test_display_shows_suggestions(
        self, formatter: DisplayFormatter, dangerous_result: AnalysisResult
    ) -> None:
        """Test that suggestions are displayed."""
        formatter.display_analysis(dangerous_result)

        output = formatter.console.file.getvalue()
        assert "Suggestions" in output or "suggestions" in output.lower()
        assert dangerous_result.suggestions[0] in output

    def test_display_shows_alternatives(
        self, formatter: DisplayFormatter, dangerous_result: AnalysisResult
    ) -> None:
        """Test that safe alternatives are displayed."""
        formatter.display_analysis(dangerous_result)

        output = formatter.console.file.getvalue()
        assert "Alternative" in output or "alternative" in output.lower()
        assert dangerous_result.safe_alternatives[0] in output

    def test_display_comparison(
        self, formatter: DisplayFormatter, console: Console
    ) -> None:
        """Test displaying command comparison."""
        formatter.display_comparison("rm -rf /", "rm -i -rf /")

        output = console.file.getvalue()
        assert "rm -rf /" in output
        assert "rm -i -rf /" in output

    def test_display_execution_start(
        self, formatter: DisplayFormatter, console: Console
    ) -> None:
        """Test displaying execution start."""
        formatter.display_execution_start("echo test")

        output = console.file.getvalue()
        assert "Executing" in output or "executing" in output.lower()
        assert "echo test" in output

    def test_display_execution_complete_success(
        self, formatter: DisplayFormatter, console: Console
    ) -> None:
        """Test displaying successful completion."""
        formatter.display_execution_complete(True)

        output = console.file.getvalue()
        assert "success" in output.lower() or "complete" in output.lower()

    def test_display_execution_complete_failure(
        self, formatter: DisplayFormatter, console: Console
    ) -> None:
        """Test displaying failed completion."""
        formatter.display_execution_complete(False)

        output = console.file.getvalue()
        assert "fail" in output.lower()

    def test_display_execution_aborted(
        self, formatter: DisplayFormatter, console: Console
    ) -> None:
        """Test displaying aborted execution."""
        formatter.display_execution_aborted()

        output = console.file.getvalue()
        assert "abort" in output.lower()

    def test_display_error(self, formatter: DisplayFormatter, console: Console) -> None:
        """Test displaying error message."""
        formatter.display_error("Test error message")

        output = console.file.getvalue()
        assert "Error" in output or "error" in output
        assert "Test error message" in output

    def test_display_info(self, formatter: DisplayFormatter, console: Console) -> None:
        """Test displaying info message."""
        formatter.display_info("Test info message")

        output = console.file.getvalue()
        assert "Test info message" in output

    def test_display_shows_command(
        self, formatter: DisplayFormatter, dangerous_result: AnalysisResult
    ) -> None:
        """Test that command is displayed."""
        formatter.display_analysis(dangerous_result)

        output = formatter.console.file.getvalue()
        assert dangerous_result.command.raw in output

    def test_display_shows_danger_level(
        self, formatter: DisplayFormatter, dangerous_result: AnalysisResult
    ) -> None:
        """Test that danger level is displayed."""
        formatter.display_analysis(dangerous_result)

        output = formatter.console.file.getvalue()
        assert "Danger Level" in output or "danger" in output.lower()
        assert "CRITICAL" in output
