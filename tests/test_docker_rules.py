"""
Tests for Docker safety rules.
"""

import pytest
from safe_cli.core.parser import CommandParser
from safe_cli.rules.docker import (
    DockerRmiRule,
    DockerRmRule,
    DockerSystemPruneRule,
    DockerVolumePruneRule,
)
from safe_cli.utils.constants import DangerLevel


class TestDockerSystemPruneRule:
    """Test suite for docker system prune rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> DockerSystemPruneRule:
        return DockerSystemPruneRule()

    def test_matches_system_prune(self, parser: CommandParser, rule: DockerSystemPruneRule) -> None:
        cmd = parser.parse("docker system prune")
        assert rule.matches(cmd)

    def test_prune_all_volumes_critical(self, parser: CommandParser, rule: DockerSystemPruneRule) -> None:
        cmd = parser.parse("docker system prune -a --volumes")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.CRITICAL

    def test_prune_all_high(self, parser: CommandParser, rule: DockerSystemPruneRule) -> None:
        cmd = parser.parse("docker system prune -a")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH

    def test_prune_volumes_high(self, parser: CommandParser, rule: DockerSystemPruneRule) -> None:
        cmd = parser.parse("docker system prune --volumes")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH

    def test_prune_basic_medium(self, parser: CommandParser, rule: DockerSystemPruneRule) -> None:
        cmd = parser.parse("docker system prune")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.MEDIUM


class TestDockerRmRule:
    """Test suite for docker rm rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> DockerRmRule:
        return DockerRmRule()

    def test_matches_docker_rm(self, parser: CommandParser, rule: DockerRmRule) -> None:
        cmd = parser.parse("docker rm container")
        assert rule.matches(cmd)

    def test_rm_force_volumes_multiple_critical(self, parser: CommandParser, rule: DockerRmRule) -> None:
        cmd = parser.parse("docker rm -fv container1 container2")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.CRITICAL

    def test_rm_force_multiple_high(self, parser: CommandParser, rule: DockerRmRule) -> None:
        cmd = parser.parse("docker rm -f container1 container2")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH

    def test_rm_volumes_high(self, parser: CommandParser, rule: DockerRmRule) -> None:
        cmd = parser.parse("docker rm -v container")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH

    def test_rm_force_medium(self, parser: CommandParser, rule: DockerRmRule) -> None:
        cmd = parser.parse("docker rm -f container")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.MEDIUM

    def test_rm_basic_low(self, parser: CommandParser, rule: DockerRmRule) -> None:
        cmd = parser.parse("docker rm container")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.LOW


class TestDockerRmiRule:
    """Test suite for docker rmi rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> DockerRmiRule:
        return DockerRmiRule()

    def test_matches_docker_rmi(self, parser: CommandParser, rule: DockerRmiRule) -> None:
        cmd = parser.parse("docker rmi image")
        assert rule.matches(cmd)

    def test_rmi_force_multiple_high(self, parser: CommandParser, rule: DockerRmiRule) -> None:
        cmd = parser.parse("docker rmi -f image1 image2")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH

    def test_rmi_force_medium(self, parser: CommandParser, rule: DockerRmiRule) -> None:
        cmd = parser.parse("docker rmi -f image")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.MEDIUM

    def test_rmi_multiple_medium(self, parser: CommandParser, rule: DockerRmiRule) -> None:
        cmd = parser.parse("docker rmi image1 image2 image3")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.MEDIUM

    def test_rmi_basic_low(self, parser: CommandParser, rule: DockerRmiRule) -> None:
        cmd = parser.parse("docker rmi image")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.LOW


class TestDockerVolumePruneRule:
    """Test suite for docker volume prune rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> DockerVolumePruneRule:
        return DockerVolumePruneRule()

    def test_matches_volume_prune(self, parser: CommandParser, rule: DockerVolumePruneRule) -> None:
        cmd = parser.parse("docker volume prune")
        assert rule.matches(cmd)

    def test_volume_prune_critical(self, parser: CommandParser, rule: DockerVolumePruneRule) -> None:
        cmd = parser.parse("docker volume prune -f")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.CRITICAL
        assert "permanently" in result.message.lower()
