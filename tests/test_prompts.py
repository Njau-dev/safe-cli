"""
Tests for user prompts.
"""

from io import StringIO

import pytest
from rich.console import Console

from safe_cli.core.analyzer import AnalysisResult
from safe_cli.core.parser import ParsedCommand
from safe_cli.ui.prompts import PromptResponse, UserPrompt
from safe_cli.utils.constants import DangerLevel


class TestUserPrompt:
    """Test suite for UserPrompt."""

    @pytest.fixture
    def console(self) -> Console:
        """Create console instance."""
        return Console(file=StringIO(), width=80)

    @pytest.fixture
    def prompt(self, console: Console) -> UserPrompt:
        """Create prompt instance."""
        return UserPrompt(console)

    @pytest.fixture
    def safe_result(self) -> AnalysisResult:
        """Create safe analysis result."""
        cmd = ParsedCommand(
            "echo test", ["echo", "test"], "echo", ["test"], [])
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
    def low_result(self) -> AnalysisResult:
        """Create low danger result."""
        cmd = ParsedCommand("rm file", ["rm", "file"], "rm", ["file"], [])
        return AnalysisResult(
            command=cmd,
            danger_level=DangerLevel.LOW,
            matches=[],
            primary_warning="Will delete file",
            all_warnings=["Will delete file"],
            suggestions=[],
            safe_alternatives=[],
        )

    @pytest.fixture
    def medium_result(self) -> AnalysisResult:
        """Create medium danger result."""
        cmd = ParsedCommand(
            "rm -r /tmp", ["rm", "-r", "/tmp"], "rm", ["/tmp"], ["-r"])
        return AnalysisResult(
            command=cmd,
            danger_level=DangerLevel.MEDIUM,
            matches=[],
            primary_warning="Will delete recursively",
            all_warnings=["Will delete recursively"],
            suggestions=["Use -i flag"],
            safe_alternatives=["rm -i -r /tmp"],
        )

    @pytest.fixture
    def high_result(self) -> AnalysisResult:
        """Create high danger result."""
        cmd = ParsedCommand(
            "rm -rf /tmp", ["rm", "-rf", "/tmp"], "rm", ["/tmp"], ["-rf"])
        return AnalysisResult(
            command=cmd,
            danger_level=DangerLevel.HIGH,
            matches=[],
            primary_warning="Dangerous operation",
            all_warnings=["Dangerous operation"],
            suggestions=["Be careful"],
            safe_alternatives=["rm -i -rf /tmp"],
        )

    @pytest.fixture
    def critical_result(self) -> AnalysisResult:
        """Create critical danger result."""
        cmd = ParsedCommand(
            "rm -rf /", ["rm", "-rf", "/"], "rm", ["/"], ["-rf"])
        return AnalysisResult(
            command=cmd,
            danger_level=DangerLevel.CRITICAL,
            matches=[],
            primary_warning="Will destroy system!",
            all_warnings=["Will destroy system!"],
            suggestions=["Don't do this"],
            safe_alternatives=["rm -i -rf /"],
        )

    def test_prompt_initializes(self, prompt: UserPrompt) -> None:
        """Test that prompt initializes."""
        assert prompt is not None
        assert prompt.console is not None

    def test_safe_command_auto_continues(
        self, prompt: UserPrompt, safe_result: AnalysisResult
    ) -> None:
        """Test that safe commands auto-continue."""
        response = prompt.confirm_execution(safe_result)
        assert response == PromptResponse.CONTINUE

    def test_low_danger_auto_continues(
        self, prompt: UserPrompt, low_result: AnalysisResult
    ) -> None:
        """Test that low danger commands auto-continue."""
        response = prompt.confirm_execution(low_result)
        assert response == PromptResponse.CONTINUE

    def test_skip_prompt_auto_continues(
        self, prompt: UserPrompt, critical_result: AnalysisResult
    ) -> None:
        """Test that --yes flag skips prompts."""
        response = prompt.confirm_execution(critical_result, skip_prompt=True)
        assert response == PromptResponse.CONTINUE

    def test_prompt_response_enum_values(self) -> None:
        """Test PromptResponse enum values."""
        assert PromptResponse.ABORT
        assert PromptResponse.CONTINUE
        assert PromptResponse.VIEW_ALTERNATIVE
        assert PromptResponse.USE_ALTERNATIVE

    def test_choose_alternative_with_alternatives(
        self, prompt: UserPrompt
    ) -> None:
        """Test choosing from alternatives."""
        alternatives = ["alt1", "alt2", "alt3"]

        # Can't easily test interactive input, but verify method exists
        assert hasattr(prompt, "choose_alternative")
        assert callable(prompt.choose_alternative)


class TestPromptResponse:
    """Test suite for PromptResponse enum."""

    def test_prompt_response_values(self) -> None:
        """Test that all response values exist."""
        assert PromptResponse.ABORT.value == "abort"
        assert PromptResponse.CONTINUE.value == "continue"
        assert PromptResponse.VIEW_ALTERNATIVE.value == "view_alternative"
        assert PromptResponse.USE_ALTERNATIVE.value == "use_alternative"

    def test_prompt_response_comparison(self) -> None:
        """Test comparing prompt responses."""
        assert PromptResponse.ABORT == PromptResponse.ABORT
        assert PromptResponse.ABORT != PromptResponse.CONTINUE

    def test_prompt_response_in_collection(self) -> None:
        """Test using prompt responses in collections."""
        responses = [PromptResponse.ABORT, PromptResponse.CONTINUE]

        assert PromptResponse.ABORT in responses
        assert PromptResponse.VIEW_ALTERNATIVE not in responses
