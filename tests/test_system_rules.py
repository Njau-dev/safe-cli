"""
Tests for system-level safety rules.
"""

from unittest import result
import pytest
from safe_cli.core.parser import CommandParser
from safe_cli.rules.system import (
    DdRule,
    KillRule,
    MkfsRule,
    ShutdownRule,
    SudoRule,
)
from safe_cli.utils.constants import DangerLevel


class TestSudoRule:
    """Test suite for sudo rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> SudoRule:
        return SudoRule()

    def test_matches_sudo(self, parser: CommandParser, rule: SudoRule) -> None:
        cmd = parser.parse("sudo rm file")
        assert rule.matches(cmd)

    def test_sudo_dangerous_cmd_system_path_critical(self, parser: CommandParser, rule: SudoRule) -> None:
        cmd = parser.parse("sudo rm -rf /usr")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.CRITICAL

    def test_sudo_dangerous_cmd_high(self, parser: CommandParser, rule: SudoRule) -> None:
        cmd = parser.parse("sudo dd if=/dev/zero of=test")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH

    def test_sudo_system_path_high(self, parser: CommandParser, rule: SudoRule) -> None:
        cmd = parser.parse("sudo ls /etc")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH

    def test_sudo_basic_medium(self, parser: CommandParser, rule: SudoRule) -> None:
        cmd = parser.parse("sudo apt-get update")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.MEDIUM


class TestDdRule:
    """Test suite for dd rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> DdRule:
        return DdRule()

    def test_matches_dd(self, parser: CommandParser, rule: DdRule) -> None:
        cmd = parser.parse("dd if=/dev/zero of=test")
        assert rule.matches(cmd)

    def test_dd_to_disk_critical(self, parser: CommandParser, rule: DdRule) -> None:
        cmd = parser.parse("dd if=/dev/zero of=/dev/sda")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.CRITICAL
        assert "DESTROY" in result.message

    def test_dd_to_file_medium(self, parser: CommandParser, rule: DdRule) -> None:
        cmd = parser.parse("dd if=/dev/zero of=test.img")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.MEDIUM

    def test_dd_no_of_low(self, parser: CommandParser, rule: DdRule) -> None:
        cmd = parser.parse("dd if=/dev/zero bs=1M count=10")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.LOW


class TestKillRule:
    """Test suite for kill rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> KillRule:
        return KillRule()

    def test_matches_kill(self, parser: CommandParser, rule: KillRule) -> None:
        cmd = parser.parse("kill 1234")
        assert rule.matches(cmd)

    def test_matches_killall(self, parser: CommandParser, rule: KillRule) -> None:
        cmd = parser.parse("killall firefox")
        assert rule.matches(cmd)

    def test_kill_9_system_process_critical(self, parser: CommandParser, rule: KillRule) -> None:
        cmd = parser.parse("killall -9 systemd")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.CRITICAL

    def test_killall_9_high(self, parser: CommandParser, rule: KillRule) -> None:
        cmd = parser.parse("killall -9 firefox")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH

    def test_kill_9_medium(self, parser: CommandParser, rule: KillRule) -> None:
        cmd = parser.parse("kill -9 1234")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.MEDIUM

    def test_killall_medium(self, parser: CommandParser, rule: KillRule) -> None:
        cmd = parser.parse("killall firefox")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.MEDIUM

    def test_kill_low(self, parser: CommandParser, rule: KillRule) -> None:
        cmd = parser.parse("kill 1234")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.LOW


class TestShutdownRule:
    """Test suite for shutdown rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> ShutdownRule:
        return ShutdownRule()

    def test_matches_shutdown(self, parser: CommandParser, rule: ShutdownRule) -> None:
        cmd = parser.parse("shutdown now")
        assert rule.matches(cmd)

    def test_matches_reboot(self, parser: CommandParser, rule: ShutdownRule) -> None:
        cmd = parser.parse("reboot")
        assert rule.matches(cmd)

    def test_shutdown_now_high(self, parser: CommandParser, rule: ShutdownRule) -> None:
        cmd = parser.parse("shutdown now")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH

    def test_reboot_high(self, parser: CommandParser, rule: ShutdownRule) -> None:
        cmd = parser.parse("reboot")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH

    def test_shutdown_delayed_medium(self, parser: CommandParser, rule: ShutdownRule) -> None:
        cmd = parser.parse("shutdown +10")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.MEDIUM


class TestMkfsRule:
    """Test suite for mkfs rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> MkfsRule:
        return MkfsRule()

    def test_matches_mkfs(self, parser: CommandParser, rule: MkfsRule) -> None:
        cmd = parser.parse("mkfs.ext4 /dev/sdb1")
        assert rule.matches(cmd)

    def test_mkfs_critical(self, parser: CommandParser, rule: MkfsRule) -> None:
        cmd = parser.parse("mkfs.ext4 /dev/sdb1")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.CRITICAL
        assert "FORMAT" in result.message
        assert "DESTROYING ALL DATA" in result.message
