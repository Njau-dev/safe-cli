"""
Tests for safe alternative generator.
"""

import pytest
from safe_cli.core.parser import CommandParser
from safe_cli.core.suggestion import SafeAlternativeGenerator


class TestSafeAlternativeGenerator:
    """Test suite for SafeAlternativeGenerator."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create parser instance."""
        return CommandParser()

    @pytest.fixture
    def generator(self) -> SafeAlternativeGenerator:
        """Create generator instance."""
        return SafeAlternativeGenerator()

    def test_safe_rm_alternative(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test generating safe rm alternative."""
        cmd = parser.parse("rm -rf /tmp/test")
        alternative = generator.generate(cmd)

        assert alternative is not None
        assert "-i" in alternative
        assert "rm" in alternative

    def test_safe_rm_no_alternative_if_interactive(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test that no alternative is generated if already interactive."""
        cmd = parser.parse("rm -i file.txt")
        alternative = generator.generate(cmd)

        assert alternative is None

    def test_safe_mv_alternative(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test generating safe mv alternative."""
        cmd = parser.parse("mv -f old.txt new.txt")
        alternative = generator.generate(cmd)

        assert alternative is not None
        assert "-i" in alternative
        assert "-f" not in alternative
        assert "mv" in alternative

    def test_safe_mv_no_alternative_if_interactive(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test that mv doesn't generate alternative if interactive."""
        cmd = parser.parse("mv -i old.txt new.txt")
        alternative = generator.generate(cmd)

        assert alternative is None

    def test_safe_cp_alternative(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test generating safe cp alternative."""
        cmd = parser.parse("cp -f file.txt backup.txt")
        alternative = generator.generate(cmd)

        assert alternative is not None
        assert "-i" in alternative
        assert "-f" not in alternative

    def test_safe_cp_no_alternative_if_no_force(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test that cp doesn't generate alternative without force flag."""
        cmd = parser.parse("cp file.txt backup.txt")
        alternative = generator.generate(cmd)

        assert alternative is None

    def test_safe_chmod_777_alternative(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test generating safe chmod alternative for 777."""
        cmd = parser.parse("chmod 777 file.sh")
        alternative = generator.generate(cmd)

        assert alternative is not None
        assert "755" in alternative
        assert "777" not in alternative

    def test_safe_chmod_666_alternative(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test generating safe chmod alternative for 666."""
        cmd = parser.parse("chmod 666 file.txt")
        alternative = generator.generate(cmd)

        assert alternative is not None
        assert "644" in alternative
        assert "666" not in alternative

    def test_safe_chmod_no_alternative_for_safe_perms(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test that chmod doesn't generate alternative for safe permissions."""
        cmd = parser.parse("chmod 755 file.sh")
        alternative = generator.generate(cmd)

        assert alternative is None

    def test_safe_chown_no_alternative(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test that chown doesn't generate automatic alternative."""
        cmd = parser.parse("chown -R user /tmp")
        alternative = generator.generate(cmd)

        # chown is complex, we rely on suggestions instead
        assert alternative is None

    def test_unknown_command_no_alternative(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test that unknown commands return None."""
        cmd = parser.parse("unknown_command arg")
        alternative = generator.generate(cmd)

        assert alternative is None

    def test_generate_multiple_alternatives(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test generating multiple alternatives."""
        cmd = parser.parse("rm -rf /tmp/test")
        alternatives = generator.generate_multiple(cmd, count=3)

        assert isinstance(alternatives, list)
        assert len(alternatives) > 0
        assert len(alternatives) <= 3

    def test_multiple_alternatives_unique(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test that multiple alternatives are unique."""
        cmd = parser.parse("rm -rf /tmp/test")
        alternatives = generator.generate_multiple(cmd, count=5)

        # Check for uniqueness
        assert len(alternatives) == len(set(alternatives))

    def test_rm_alternative_preserves_args(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test that rm alternative preserves arguments."""
        cmd = parser.parse("rm -rf file1.txt file2.txt")
        alternative = generator.generate(cmd)

        assert alternative is not None
        assert "file1.txt" in alternative
        assert "file2.txt" in alternative

    def test_mv_alternative_removes_force(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test that mv alternative removes force flag."""
        cmd = parser.parse("mv -f old.txt new.txt")
        alternative = generator.generate(cmd)

        assert alternative is not None
        assert "-f" not in alternative
        assert "-i" in alternative

    def test_cp_alternative_removes_force(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test that cp alternative removes force flag."""
        cmd = parser.parse("cp -rf dir/ backup/")
        alternative = generator.generate(cmd)

        assert alternative is not None
        assert "-f" not in alternative
        assert "-i" in alternative
        assert "-r" in alternative  # Keep recursive

    def test_chmod_multiple_files(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test chmod alternative with multiple files."""
        cmd = parser.parse("chmod 777 file1.sh file2.sh")
        alternative = generator.generate(cmd)

        assert alternative is not None
        assert "755" in alternative
        assert "file1.sh" in alternative
        assert "file2.sh" in alternative


class TestAlternativeFormats:
    """Test alternative command formatting."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create parser instance."""
        return CommandParser()

    @pytest.fixture
    def generator(self) -> SafeAlternativeGenerator:
        """Create generator instance."""
        return SafeAlternativeGenerator()

    def test_alternative_is_valid_command(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test that generated alternative is a valid command."""
        cmd = parser.parse("rm -rf /tmp/test")
        alternative = generator.generate(cmd)

        assert alternative is not None

        # Should be parseable
        alt_cmd = parser.parse(alternative)
        assert alt_cmd.command == "rm"
        assert alt_cmd.has_flag("-i")

    def test_alternative_preserves_command_structure(
        self, parser: CommandParser, generator: SafeAlternativeGenerator
    ) -> None:
        """Test that alternative preserves command structure."""
        cmd = parser.parse("mv -f old.txt new.txt")
        alternative = generator.generate(cmd)

        assert alternative is not None

        alt_cmd = parser.parse(alternative)
        assert alt_cmd.command == "mv"
        assert "old.txt" in alt_cmd.args
        assert "new.txt" in alt_cmd.args
