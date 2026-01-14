"""
Tests for CLI interface.
"""

from unittest import result
import pytest
from typer.testing import CliRunner
from safe_cli.cli import app
from safe_cli import __version__


class TestCLI:
    """Test suite for CLI commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner."""
        return CliRunner()

    def test_version_flag(self, runner: CliRunner) -> None:
        """Test --version flag."""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert __version__ in result.stdout
        assert "safe-cli" in result.stdout

    def test_version_short_flag(self, runner: CliRunner) -> None:
        """Test -v flag."""
        result = runner.invoke(app, ["-v"])

        assert result.exit_code == 0
        assert __version__ in result.stdout

    def test_no_command_shows_help(self, runner: CliRunner) -> None:
        """Test that running without command shows usage info."""
        result = runner.invoke(app, [])

        assert result.exit_code == 1
        assert "No command provided" in result.stdout
        assert "Usage:" in result.stdout

    def test_help_flag(self, runner: CliRunner) -> None:
        """Test --help flag."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Know before you run" in result.stdout
        assert "OPTIONS" in result.stdout

    def test_simple_command(self, runner: CliRunner) -> None:
        """Test running a simple command."""
        result = runner.invoke(app, ["ls", "-la"])

        assert result.exit_code == 0
        assert "ls -la" in result.stdout
        # Should show analysis now
        assert "Danger Level:" in result.stdout

    def test_command_with_flags(self, runner: CliRunner) -> None:
        """Test command with multiple flags."""
        result = runner.invoke(app, ["rm", "-rf", "/tmp/test"])

        assert "rm -rf /tmp/test" in result.stdout
        assert "Danger Level:" in result.stdout

    def test_dry_run_flag(self, runner: CliRunner) -> None:
        """Test --dry-run flag."""
        result = runner.invoke(app, ["--dry-run", "rm", "-rf", "/tmp"])

        assert result.exit_code == 0


        assert "Dry Run Mode" in result.stdout
        assert "rm -rf /tmp" in result.stdout
        assert "no command was executed" in result.stdout.lower()

    def test_dry_run_short_flag(self, runner: CliRunner) -> None:
        """Test -d flag for dry run."""
        result = runner.invoke(app, ["-d", "ls"])

        assert result.exit_code == 0
        assert "Dry Run Mode" in result.stdout

    def test_yes_flag(self, runner: CliRunner) -> None:
        """Test --yes flag (for future use)."""
        result = runner.invoke(app, ["--yes", "echo", "test"])

        assert result.exit_code == 0
        assert "echo test" in result.stdout

    def test_complex_command(self, runner: CliRunner) -> None:
        """Test complex command with multiple arguments."""
        result = runner.invoke(app, ["git", "commit", "-am", "test message"])

        assert "git commit -am" in result.stdout

    def test_quoted_arguments(self, runner: CliRunner) -> None:
        """Test command with quoted arguments."""
        result = runner.invoke(app, ["echo", "hello world"])

        assert result.exit_code == 0
        assert "echo hello world" in result.stdout

    def test_command_with_special_chars(self, runner: CliRunner) -> None:
        """Test command with special characters."""
        result = runner.invoke(app, ["echo", "test*file?.txt"])

        assert result.exit_code == 0
        assert "test*file?.txt" in result.stdout
