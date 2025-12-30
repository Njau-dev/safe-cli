"""
Tests for rule registry.
"""

import pytest
from safe_cli.core.parser import CommandParser
from safe_cli.rules.base import Rule, RuleMatch
from safe_cli.rules.filesystem import RmRule
from safe_cli.rules.registry import RuleRegistry
from safe_cli.utils.constants import DangerLevel


class DummyRule(Rule):
    """Dummy rule for testing."""

    name = "dummy_rule"
    description = "Test rule"

    def matches(self, command):
        return command.command == "dummy"

    def analyze(self, command):
        return RuleMatch(
            rule_name=self.name,
            danger_level=DangerLevel.LOW,
            message="Dummy message",
        )


class TestRuleRegistry:
    """Test suite for RuleRegistry."""

    @pytest.fixture
    def registry(self) -> RuleRegistry:
        """Create a fresh registry."""
        return RuleRegistry()

    @pytest.fixture
    def parser(self) -> CommandParser:
        """Create parser instance."""
        return CommandParser()

    def test_registry_initializes_with_default_rules(
        self, registry: RuleRegistry
    ) -> None:
        """Test that registry starts with default rules."""
        assert len(registry) > 0
        assert len(registry.get_all_rules()) > 0

    def test_registry_has_filesystem_rules(self, registry: RuleRegistry) -> None:
        """Test that filesystem rules are registered."""
        rule_names = [rule.name for rule in registry.get_all_rules()]

        assert "rm_command" in rule_names
        assert "mv_command" in rule_names
        assert "cp_command" in rule_names
        assert "chmod_command" in rule_names
        assert "chown_command" in rule_names

    def test_register_new_rule(self, registry: RuleRegistry) -> None:
        """Test registering a new rule."""
        initial_count = len(registry)
        dummy = DummyRule()

        registry.register(dummy)

        assert len(registry) == initial_count + 1
        assert registry.get_rule("dummy_rule") == dummy

    def test_register_duplicate_raises_error(self, registry: RuleRegistry) -> None:
        """Test that registering duplicate rule raises error."""
        dummy = DummyRule()
        registry.register(dummy)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(DummyRule())

    def test_register_non_rule_raises_error(self, registry: RuleRegistry) -> None:
        """Test that registering non-rule raises error."""
        with pytest.raises(TypeError):
            registry.register("not a rule")  # type: ignore

    def test_unregister_rule(self, registry: RuleRegistry) -> None:
        """Test unregistering a rule."""
        dummy = DummyRule()
        registry.register(dummy)

        result = registry.unregister("dummy_rule")

        assert result is True
        assert registry.get_rule("dummy_rule") is None

    def test_unregister_nonexistent_rule(self, registry: RuleRegistry) -> None:
        """Test unregistering nonexistent rule returns False."""
        result = registry.unregister("nonexistent")
        assert result is False

    def test_get_rule(self, registry: RuleRegistry) -> None:
        """Test getting a rule by name."""
        rule = registry.get_rule("rm_command")

        assert rule is not None
        assert isinstance(rule, RmRule)

    def test_get_nonexistent_rule(self, registry: RuleRegistry) -> None:
        """Test getting nonexistent rule returns None."""
        rule = registry.get_rule("nonexistent")
        assert rule is None

    def test_get_all_rules(self, registry: RuleRegistry) -> None:
        """Test getting all rules."""
        rules = registry.get_all_rules()

        assert isinstance(rules, list)
        assert len(rules) > 0
        assert all(isinstance(r, Rule) for r in rules)

    def test_find_matching_rules(
        self, registry: RuleRegistry, parser: CommandParser
    ) -> None:
        """Test finding rules that match a command."""
        cmd = parser.parse("rm -rf /tmp")
        matches = registry.find_matching_rules(cmd)

        assert len(matches) > 0
        assert any(r.name == "rm_command" for r in matches)

    def test_find_matching_rules_no_match(
        self, registry: RuleRegistry, parser: CommandParser
    ) -> None:
        """Test finding rules when nothing matches."""
        cmd = parser.parse("nonexistent_command")
        matches = registry.find_matching_rules(cmd)

        assert len(matches) == 0

    def test_analyze_command(
        self, registry: RuleRegistry, parser: CommandParser
    ) -> None:
        """Test analyzing a command."""
        cmd = parser.parse("rm -rf /tmp")
        results = registry.analyze_command(cmd)

        assert len(results) > 0
        assert all(isinstance(r, RuleMatch) for r in results)
        assert any(r.rule_name == "rm_command" for r in results)

    def test_analyze_command_no_match(
        self, registry: RuleRegistry, parser: CommandParser
    ) -> None:
        """Test analyzing command with no matches."""
        cmd = parser.parse("nonexistent_command")
        results = registry.analyze_command(cmd)

        assert len(results) == 0

    def test_get_highest_danger_level(
        self, registry: RuleRegistry, parser: CommandParser
    ) -> None:
        """Test getting highest danger level."""
        cmd = parser.parse("rm -rf /")
        danger = registry.get_highest_danger_level(cmd)

        assert danger == DangerLevel.CRITICAL

    def test_get_highest_danger_level_no_match(
        self, registry: RuleRegistry, parser: CommandParser
    ) -> None:
        """Test getting danger level when no rules match."""
        cmd = parser.parse("nonexistent_command")
        danger = registry.get_highest_danger_level(cmd)

        assert danger == DangerLevel.SAFE

    def test_clear_registry(self, registry: RuleRegistry) -> None:
        """Test clearing all rules."""
        assert len(registry) > 0

        registry.clear()

        assert len(registry) == 0
        assert len(registry.get_all_rules()) == 0

    def test_registry_repr(self, registry: RuleRegistry) -> None:
        """Test registry string representation."""
        repr_str = repr(registry)

        assert "RuleRegistry" in repr_str
        assert str(len(registry)) in repr_str

    def test_multiple_matching_rules(
        self, registry: RuleRegistry, parser: CommandParser
    ) -> None:
        """Test command matching multiple rules."""

        # Register a dummy rule that also matches rm
        class AnotherRmRule(Rule):
            name = "another_rm_rule"
            description = "Another rm rule"

            def matches(self, command):
                return command.command == "rm"

            def analyze(self, command):
                return RuleMatch(
                    rule_name=self.name,
                    danger_level=DangerLevel.MEDIUM,
                    message="Another rm warning",
                )

        registry.register(AnotherRmRule())
        cmd = parser.parse("rm file.txt")
        matches = registry.find_matching_rules(cmd)

        assert len(matches) >= 2
        assert any(r.name == "rm_command" for r in matches)
        assert any(r.name == "another_rm_rule" for r in matches)
