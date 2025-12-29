"""
Tests for command parser.
"""

import pytest
from safe_cli.core.parser import CommandParser, ParsedCommand


class TestCommandParser:
    """Test suite for CommandParser."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create a parser instance."""
        return CommandParser()

    def test_simple_command(self, parser: CommandParser) -> None:
        """Test parsing a simple command."""
        result = parser.parse("ls")

        assert result.command == "ls"
        assert result.args == []
        assert result.flags == []
        assert result.tokens == ["ls"]
        assert result.raw == "ls"

    def test_command_with_args(self, parser: CommandParser) -> None:
        """Test parsing command with arguments."""
        result = parser.parse("rm file.txt")

        assert result.command == "rm"
        assert result.args == ["file.txt"]
        assert result.flags == []
        assert result.tokens == ["rm", "file.txt"]

    def test_command_with_flags(self, parser: CommandParser) -> None:
        """Test parsing command with flags."""
        result = parser.parse("ls -la")

        assert result.command == "ls"
        assert result.flags == ["-la"]
        assert result.args == []

    def test_command_with_flags_and_args(self, parser: CommandParser) -> None:
        """Test parsing command with both flags and arguments."""
        result = parser.parse("rm -rf /tmp/test")

        assert result.command == "rm"
        assert result.flags == ["-rf"]
        assert result.args == ["/tmp/test"]
        assert len(result.tokens) == 3

    def test_command_with_multiple_flags(self, parser: CommandParser) -> None:
        """Test parsing command with multiple flags."""
        result = parser.parse("docker rm -f --volumes container_name")

        assert result.command == "docker"
        assert "-f" in result.flags
        assert "--volumes" in result.flags
        assert "container_name" in result.args

    def test_command_with_quoted_args(self, parser: CommandParser) -> None:
        """Test parsing command with quoted arguments."""
        result = parser.parse('echo "hello world"')

        assert result.command == "echo"
        assert result.args == ["hello world"]
        assert len(result.tokens) == 2

    def test_command_with_escaped_spaces(self, parser: CommandParser) -> None:
        """Test parsing command with escaped spaces."""
        result = parser.parse(r"rm my\ file.txt")

        assert result.command == "rm"
        assert result.args == ["my file.txt"]

    def test_empty_command_raises_error(self, parser: CommandParser) -> None:
        """Test that empty command raises ValueError."""
        with pytest.raises(ValueError, match="Command cannot be empty"):
            parser.parse("")

    def test_whitespace_only_command_raises_error(self, parser: CommandParser) -> None:
        """Test that whitespace-only command raises ValueError."""
        with pytest.raises(ValueError, match="Command cannot be empty"):
            parser.parse("   ")

    def test_invalid_syntax_raises_error(self, parser: CommandParser) -> None:
        """Test that invalid syntax raises ValueError."""
        with pytest.raises(ValueError, match="Invalid command syntax"):
            parser.parse('echo "unclosed quote')

    def test_has_flag(self, parser: CommandParser) -> None:
        """Test has_flag method."""
        result = parser.parse("rm -rf /tmp")

        assert result.has_flag("-rf")
        assert not result.has_flag("-i")

    def test_has_any_flag(self, parser: CommandParser) -> None:
        """Test has_any_flag method."""
        result = parser.parse("rm -rf /tmp")

        assert result.has_any_flag(["-rf", "-i"])
        assert result.has_any_flag(["-r", "-rf"])
        assert not result.has_any_flag(["-i", "-v"])

    def test_get_flag_value_with_equals(self, parser: CommandParser) -> None:
        """Test getting flag value with = syntax."""
        result = parser.parse("command --output=file.txt")

        assert result.get_flag_value("--output") == "file.txt"

    def test_is_compound_command(self, parser: CommandParser) -> None:
        """Test compound command detection."""
        assert parser.is_compound_command("ls | grep test")
        assert parser.is_compound_command("command1 && command2")
        assert parser.is_compound_command("cat file > output.txt")
        assert not parser.is_compound_command("ls -la")

    def test_split_compound_command(self, parser: CommandParser) -> None:
        """Test splitting compound commands."""
        parts = parser.split_compound_command("ls | grep test")

        assert len(parts) == 2
        assert "ls" in parts[0]
        assert "grep test" in parts[1]

    def test_complex_command(self, parser: CommandParser) -> None:
        """Test parsing complex real-world command."""
        result = parser.parse("git commit -am 'Initial commit'")

        assert result.command == "git"
        assert "commit" in result.args
        assert "-am" in result.flags
        assert "Initial commit" in result.args


class TestParsedCommand:
    """Test suite for ParsedCommand methods."""

    def test_parsed_command_representation(self) -> None:
        """Test ParsedCommand data structure."""
        cmd = ParsedCommand(
            raw="rm -rf /tmp",
            tokens=["rm", "-rf", "/tmp"],
            command="rm",
            args=["/tmp"],
            flags=["-rf"],
        )

        assert cmd.command == "rm"
        assert cmd.has_flag("-rf")
        assert len(cmd.tokens) == 3
