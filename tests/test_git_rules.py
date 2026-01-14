"""
Tests for Git safety rules.
"""

import pytest
from safe_cli.core.parser import CommandParser
from safe_cli.rules.git import (
    GitBranchDeleteRule,
    GitCleanRule,
    GitPushForceRule,
    GitResetRule,
)
from safe_cli.utils.constants import DangerLevel


class TestGitResetRule:
    """Test suite for git reset rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> GitResetRule:
        return GitResetRule()

    def test_matches_git_reset(self, parser: CommandParser, rule: GitResetRule) -> None:
        cmd = parser.parse("git reset --hard")
        assert rule.matches(cmd)

    def test_no_match_other_git(self, parser: CommandParser, rule: GitResetRule) -> None:
        cmd = parser.parse("git commit -m 'test'")
        assert not rule.matches(cmd)

    def test_git_reset_hard_high_danger(self, parser: CommandParser, rule: GitResetRule) -> None:
        cmd = parser.parse("git reset --hard")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH

    def test_git_reset_hard_head_critical(self, parser: CommandParser, rule: GitResetRule) -> None:
        cmd = parser.parse("git reset --hard HEAD~5")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.CRITICAL

    def test_git_reset_soft_low(self, parser: CommandParser, rule: GitResetRule) -> None:
        cmd = parser.parse("git reset --soft HEAD~1")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.LOW

    def test_git_reset_mixed_medium(self, parser: CommandParser, rule: GitResetRule) -> None:
        cmd = parser.parse("git reset HEAD~1")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.MEDIUM


class TestGitPushForceRule:
    """Test suite for git push --force rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> GitPushForceRule:
        return GitPushForceRule()

    def test_matches_push_force(self, parser: CommandParser, rule: GitPushForceRule) -> None:
        cmd = parser.parse("git push --force")
        assert rule.matches(cmd)

    def test_matches_push_f(self, parser: CommandParser, rule: GitPushForceRule) -> None:
        cmd = parser.parse("git push -f")
        assert rule.matches(cmd)

    def test_no_match_regular_push(self, parser: CommandParser, rule: GitPushForceRule) -> None:
        cmd = parser.parse("git push origin main")
        assert not rule.matches(cmd)

    def test_force_push_to_main_critical(self, parser: CommandParser, rule: GitPushForceRule) -> None:
        cmd = parser.parse("git push --force origin main")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.CRITICAL

    def test_force_push_with_lease_medium(self, parser: CommandParser, rule: GitPushForceRule) -> None:
        cmd = parser.parse("git push --force-with-lease")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.MEDIUM

    def test_force_push_feature_high(self, parser: CommandParser, rule: GitPushForceRule) -> None:
        cmd = parser.parse("git push --force origin feature-branch")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH


class TestGitCleanRule:
    """Test suite for git clean rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> GitCleanRule:
        return GitCleanRule()

    def test_matches_git_clean(self, parser: CommandParser, rule: GitCleanRule) -> None:
        cmd = parser.parse("git clean -fd")
        assert rule.matches(cmd)

    def test_git_clean_fdx_critical(self, parser: CommandParser, rule: GitCleanRule) -> None:
        cmd = parser.parse("git clean -fdx")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.CRITICAL

    def test_git_clean_fd_high(self, parser: CommandParser, rule: GitCleanRule) -> None:
        cmd = parser.parse("git clean -fd")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH

    def test_git_clean_f_medium(self, parser: CommandParser, rule: GitCleanRule) -> None:
        cmd = parser.parse("git clean -f")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.MEDIUM

    def test_git_clean_n_low(self, parser: CommandParser, rule: GitCleanRule) -> None:
        cmd = parser.parse("git clean -n")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.LOW


class TestGitBranchDeleteRule:
    """Test suite for git branch -D rule."""

    @pytest.fixture
    def parser(self) -> CommandParser:
        return CommandParser()

    @pytest.fixture
    def rule(self) -> GitBranchDeleteRule:
        return GitBranchDeleteRule()

    def test_matches_branch_D(self, parser: CommandParser, rule: GitBranchDeleteRule) -> None:
        cmd = parser.parse("git branch -D feature")
        assert rule.matches(cmd)

    def test_no_match_lowercase_d(self, parser: CommandParser, rule: GitBranchDeleteRule) -> None:
        cmd = parser.parse("git branch -d feature")
        assert not rule.matches(cmd)

    def test_force_delete_high(self, parser: CommandParser, rule: GitBranchDeleteRule) -> None:
        cmd = parser.parse("git branch -D old-feature")
        result = rule.analyze(cmd)
        assert result.danger_level == DangerLevel.HIGH
        assert "unmerged" in result.message.lower()
