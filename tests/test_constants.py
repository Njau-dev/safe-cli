"""
Tests for safety rules.
"""

import pytest
from safe_cli.core.parser import CommandParser
from safe_cli.rules.base import RuleMatch
from safe_cli.rules.filesystem import (
    ChmodRule,
    ChownRule,
    CpRule,
    MvRule,
    RmRule,
)
from safe_cli.utils.constants import DangerLevel


class TestRmRule:
    """Test suite for rm command rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create parser instance."""
        return CommandParser()

    @pytest.fixture
    def rule(self) -> RmRule:
        """Create rm rule instance."""
        return RmRule()

    def test_matches_rm_command(self, parser: CommandParser, rule: RmRule) -> None:
        """Test that rule matches rm command."""
        cmd = parser.parse("rm file.txt")
        assert rule.matches(cmd)

    def test_does_not_match_other_commands(
        self, parser: CommandParser, rule: RmRule
    ) -> None:
        """Test that rule doesn't match non-rm commands."""
        cmd = parser.parse("ls -la")
        assert not rule.matches(cmd)

    def test_simple_rm_low_danger(self, parser: CommandParser, rule: RmRule) -> None:
        """Test simple rm is low danger."""
        cmd = parser.parse("rm file.txt")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.LOW
        assert "permanently delete" in result.message.lower()

    def test_rm_recursive_medium_danger(
        self, parser: CommandParser, rule: RmRule
    ) -> None:
        """Test rm -r is medium danger."""
        cmd = parser.parse("rm -r /tmp/test")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.MEDIUM
        assert "recursively" in result.message.lower()

    def test_rm_force_medium_danger(self, parser: CommandParser, rule: RmRule) -> None:
        """Test rm -f is medium danger."""
        cmd = parser.parse("rm -f file.txt")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.MEDIUM

    def test_rm_rf_high_danger(self, parser: CommandParser, rule: RmRule) -> None:
        """Test rm -rf is high danger."""
        cmd = parser.parse("rm -rf /tmp/test")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.HIGH
        assert "cannot be undone" in result.message.lower()

    def test_rm_rf_root_critical(self, parser: CommandParser, rule: RmRule) -> None:
        """Test rm -rf on root is critical."""
        cmd = parser.parse("rm -rf /")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.CRITICAL

    def test_rm_rf_system_path_critical(
        self, parser: CommandParser, rule: RmRule
    ) -> None:
        """Test rm -rf on system paths is critical."""
        cmd = parser.parse("rm -rf /usr")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.CRITICAL

    def test_rm_rf_wildcard_critical(self, parser: CommandParser, rule: RmRule) -> None:
        """Test rm -rf with wildcard is critical."""
        cmd = parser.parse("rm -rf /*")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.CRITICAL

    def test_rm_suggests_interactive(self, parser: CommandParser, rule: RmRule) -> None:
        """Test that rm suggests interactive flag."""
        cmd = parser.parse("rm -rf /tmp/test")
        result = rule.analyze(cmd)

        assert result.suggestion is not None
        assert "interactive" in result.suggestion.lower()

    def test_rm_safe_alternative(self, parser: CommandParser, rule: RmRule) -> None:
        """Test that rm provides safe alternative."""
        cmd = parser.parse("rm -rf /tmp/test")
        result = rule.analyze(cmd)

        assert result.safe_alternative is not None
        assert "-i" in result.safe_alternative


class TestMvRule:
    """Test suite for mv command rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create parser instance."""
        return CommandParser()

    @pytest.fixture
    def rule(self) -> MvRule:
        """Create mv rule instance."""
        return MvRule()

    def test_matches_mv_command(self, parser: CommandParser, rule: MvRule) -> None:
        """Test that rule matches mv command."""
        cmd = parser.parse("mv old.txt new.txt")
        assert rule.matches(cmd)

    def test_simple_mv_low_danger(self, parser: CommandParser, rule: MvRule) -> None:
        """Test simple mv is low danger."""
        cmd = parser.parse("mv old.txt new.txt")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.LOW

    def test_mv_force_medium_danger(self, parser: CommandParser, rule: MvRule) -> None:
        """Test mv -f is medium danger."""
        cmd = parser.parse("mv -f old.txt new.txt")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.MEDIUM
        assert "overwrite" in result.message.lower()

    def test_mv_system_path_high_danger(
        self, parser: CommandParser, rule: MvRule
    ) -> None:
        """Test mv on system paths is high danger."""
        cmd = parser.parse("mv -f /etc/config /tmp/")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.HIGH
        assert "system" in result.message.lower()


class TestCpRule:
    """Test suite for cp command rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create parser instance."""
        return CommandParser()

    @pytest.fixture
    def rule(self) -> CpRule:
        """Create cp rule instance."""
        return CpRule()

    def test_matches_cp_command(self, parser: CommandParser, rule: CpRule) -> None:
        """Test that rule matches cp command."""
        cmd = parser.parse("cp file.txt backup.txt")
        assert rule.matches(cmd)

    def test_simple_cp_safe(self, parser: CommandParser, rule: CpRule) -> None:
        """Test simple cp is safe."""
        cmd = parser.parse("cp file.txt backup.txt")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.SAFE

    def test_cp_recursive_low_danger(self, parser: CommandParser, rule: CpRule) -> None:
        """Test cp -r is low danger."""
        cmd = parser.parse("cp -r dir/ backup/")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.LOW

    def test_cp_force_low_danger(self, parser: CommandParser, rule: CpRule) -> None:
        """Test cp -f is low danger."""
        cmd = parser.parse("cp -f file.txt backup.txt")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.LOW

    def test_cp_rf_medium_danger(self, parser: CommandParser, rule: CpRule) -> None:
        """Test cp -rf is medium danger."""
        cmd = parser.parse("cp -rf dir/ backup/")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.MEDIUM


class TestChmodRule:
    """Test suite for chmod command rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create parser instance."""
        return CommandParser()

    @pytest.fixture
    def rule(self) -> ChmodRule:
        """Create chmod rule instance."""
        return ChmodRule()

    def test_matches_chmod_command(
        self, parser: CommandParser, rule: ChmodRule
    ) -> None:
        """Test that rule matches chmod command."""
        cmd = parser.parse("chmod 755 file.sh")
        assert rule.matches(cmd)

    def test_simple_chmod_low_danger(
        self, parser: CommandParser, rule: ChmodRule
    ) -> None:
        """Test simple chmod is low danger."""
        cmd = parser.parse("chmod 755 file.sh")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.LOW

    def test_chmod_777_medium_danger(
        self, parser: CommandParser, rule: ChmodRule
    ) -> None:
        """Test chmod 777 is medium danger."""
        cmd = parser.parse("chmod 777 file.sh")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.MEDIUM
        assert "security" in result.message.lower()

    def test_chmod_777_recursive_high_danger(
        self, parser: CommandParser, rule: ChmodRule
    ) -> None:
        """Test chmod -R 777 is high danger."""
        cmd = parser.parse("chmod -R 777 /tmp/")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.HIGH

    def test_chmod_777_recursive_system_critical(
        self, parser: CommandParser, rule: ChmodRule
    ) -> None:
        """Test chmod -R 777 on system paths is critical."""
        cmd = parser.parse("chmod -R 777 /etc")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.CRITICAL
        assert "system" in result.message.lower()

    def test_chmod_suggests_safer_permissions(
        self, parser: CommandParser, rule: ChmodRule
    ) -> None:
        """Test that chmod 777 suggests safer alternatives."""
        cmd = parser.parse("chmod 777 file.sh")
        result = rule.analyze(cmd)

        assert result.suggestion is not None
        assert "755" in result.suggestion or "644" in result.suggestion


class TestChownRule:
    """Test suite for chown command rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create parser instance."""
        return CommandParser()

    @pytest.fixture
    def rule(self) -> ChownRule:
        """Create chown rule instance."""
        return ChownRule()

    def test_matches_chown_command(
        self, parser: CommandParser, rule: ChownRule
    ) -> None:
        """Test that rule matches chown command."""
        cmd = parser.parse("chown user:group file.txt")
        assert rule.matches(cmd)

    def test_simple_chown_low_danger(
        self, parser: CommandParser, rule: ChownRule
    ) -> None:
        """Test simple chown is low danger."""
        cmd = parser.parse("chown user file.txt")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.LOW

    def test_chown_recursive_medium_danger(
        self, parser: CommandParser, rule: ChownRule
    ) -> None:
        """Test chown -R is medium danger."""
        cmd = parser.parse("chown -R user /tmp/dir")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.MEDIUM

    def test_chown_system_path_high_danger(
        self, parser: CommandParser, rule: ChownRule
    ) -> None:
        """Test chown on system paths is high danger."""
        cmd = parser.parse("chown user /etc/config")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.HIGH

    def test_chown_recursive_system_critical(
        self, parser: CommandParser, rule: ChownRule
    ) -> None:
        """Test chown -R on system paths is critical."""
        cmd = parser.parse("chown -R user /usr")
        result = rule.analyze(cmd)

        assert result.danger_level == DangerLevel.CRITICAL


class TestRuleMatch:
    """Test suite for RuleMatch data class."""

    def test_rule_match_creation(self) -> None:
        """Test creating a rule match."""
        match = RuleMatch(
            rule_name="test_rule",
            danger_level=DangerLevel.HIGH,
            message="Test message",
            suggestion="Test suggestion",
            safe_alternative="safe command",
        )

        assert match.rule_name == "test_rule"
        assert match.danger_level == DangerLevel.HIGH
        assert match.message == "Test message"
        assert match.suggestion == "Test suggestion"
        assert match.safe_alternative == "safe command"

    def test_rule_match_requires_name(self) -> None:
        """Test that rule match requires name."""
        with pytest.raises(ValueError):
            RuleMatch(
                rule_name="",
                danger_level=DangerLevel.LOW,
                message="Test",
            )

    def test_rule_match_requires_message(self) -> None:
        """Test that rule match requires message."""
        with pytest.raises(ValueError):
            RuleMatch(
                rule_name="test",
                danger_level=DangerLevel.LOW,
                message="",
            )
