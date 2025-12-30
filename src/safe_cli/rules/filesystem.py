"""
Filesystem safety rules (rm, mv, cp, chmod, chown).
"""

from typing import Optional

from safe_cli.core.parser import ParsedCommand
from safe_cli.rules.base import Rule, RuleMatch
from safe_cli.utils.constants import (
    DANGEROUS_PATHS,
    FORCE_FLAGS,
    INTERACTIVE_FLAGS,
    RECURSIVE_FLAGS,
    DangerLevel,
)


def _path_is_dangerous(path: str) -> bool:
    """Determine if a target path matches one of the dangerous paths.

    Only match when the path is exactly the dangerous path or when it
    is a sub-path (i.e. startswith(dangerous + '/')). Special-case '/' so
    that ordinary absolute paths like '/tmp' are not considered system-critical.
    """
    for dangerous in DANGEROUS_PATHS:
        if dangerous == "/":
            if path == "/" or path.startswith("/*"):
                return True
            continue

        if path == dangerous or path.startswith(dangerous + "/"):
            return True

    return False


class RmRule(Rule):
    """Safety rule for rm command."""

    name = "rm_command"
    description = "Detects dangerous rm operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is rm."""
        return command.command == "rm"

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze rm command for dangers."""
        danger_level = self._calculate_danger(command)
        message = self._get_message(command)
        suggestion = self._get_suggestion(command)
        safe_alt = self._get_safe_alternative(command)

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alt,
        )

    def _calculate_danger(self, command: ParsedCommand) -> DangerLevel:
        """Calculate danger level for rm command."""
        has_recursive = command.has_any_flag(RECURSIVE_FLAGS)
        has_force = command.has_any_flag(FORCE_FLAGS)
        has_interactive = command.has_any_flag(INTERACTIVE_FLAGS)

        # Check paths
        targets = command.args
        has_dangerous_path = any(_path_is_dangerous(path) for path in targets)
        has_wildcard = any("*" in path for path in targets)

        # Critical: recursive + force on dangerous paths
        if has_recursive and has_force and has_dangerous_path:
            return DangerLevel.CRITICAL

        # Critical: recursive + force + wildcard
        if has_recursive and has_force and has_wildcard:
            return DangerLevel.CRITICAL

        # High: recursive + force
        if has_recursive and has_force:
            return DangerLevel.HIGH

        # High: dangerous paths without interactive
        if has_dangerous_path and not has_interactive:
            return DangerLevel.HIGH

        # Medium: recursive or force alone
        if has_recursive or has_force:
            return DangerLevel.MEDIUM

        # Low: normal rm
        return DangerLevel.LOW

    def _get_message(self, command: ParsedCommand) -> str:
        """Get warning message."""
        has_recursive = command.has_any_flag(RECURSIVE_FLAGS)
        has_force = command.has_any_flag(FORCE_FLAGS)
        targets = command.args

        if has_recursive and has_force:
            return (
                "This will permanently delete files recursively without prompting. "
                "This operation cannot be undone!"
            )
        elif has_recursive:
            return "This will delete directories and all their contents recursively."
        elif has_force:
            return "This will force delete files without prompting for confirmation."
        elif any(_path_is_dangerous(t) for t in targets):
            return "This targets system-critical directories. Deletion could break your system!"
        else:
            return "This will permanently delete files."

    def _get_suggestion(self, command: ParsedCommand) -> Optional[str]:
        """Get safety suggestion."""
        has_interactive = command.has_any_flag(INTERACTIVE_FLAGS)

        if not has_interactive:
            return "Consider using -i or --interactive flag to confirm each deletion."
        return None

    def _get_safe_alternative(self, command: ParsedCommand) -> Optional[str]:
        """Generate safer alternative command."""
        has_interactive = command.has_any_flag(INTERACTIVE_FLAGS)

        if not has_interactive:
            # Add -i flag
            flags = " ".join(command.flags)
            args = " ".join(command.args)
            return f"rm -i {flags} {args}".strip()

        return None


class MvRule(Rule):
    """Safety rule for mv command."""

    name = "mv_command"
    description = "Detects dangerous mv operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is mv."""
        return command.command == "mv"

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze mv command for dangers."""
        has_force = command.has_any_flag(FORCE_FLAGS)
        has_interactive = command.has_any_flag(INTERACTIVE_FLAGS)

        targets = command.args
        has_dangerous_path = any(_path_is_dangerous(path) for path in targets)

        # Determine danger level
        if has_force and has_dangerous_path:
            danger_level = DangerLevel.HIGH
            message = (
                "Moving system-critical files with force flag could break your system!"
            )
        elif has_force:
            danger_level = DangerLevel.MEDIUM
            message = "This will overwrite existing files without prompting."
        elif has_dangerous_path:
            danger_level = DangerLevel.MEDIUM
            message = "Moving system-critical files could cause issues."
        else:
            danger_level = DangerLevel.LOW
            message = "This will move or rename files."

        suggestion = None
        safe_alt = None

        if not has_interactive and (has_force or has_dangerous_path):
            suggestion = "Consider using -i flag to confirm overwrites."
            flags = " ".join(command.flags)
            args = " ".join(command.args)
            safe_alt = f"mv -i {flags} {args}".strip()

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alt,
        )


class CpRule(Rule):
    """Safety rule for cp command."""

    name = "cp_command"
    description = "Detects dangerous cp operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is cp."""
        return command.command == "cp"

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze cp command for dangers."""
        has_recursive = command.has_any_flag(RECURSIVE_FLAGS)
        has_force = command.has_any_flag(FORCE_FLAGS)

        if has_recursive and has_force:
            danger_level = DangerLevel.MEDIUM
            message = (
                "This will recursively copy and overwrite files without prompting."
            )
            suggestion = "Consider using -i flag to confirm overwrites."
        elif has_force:
            danger_level = DangerLevel.LOW
            message = "This will overwrite existing files without prompting."
            suggestion = "Consider using -i flag to confirm overwrites."
        elif has_recursive:
            danger_level = DangerLevel.LOW
            message = "This will recursively copy directories."
            suggestion = None
        else:
            danger_level = DangerLevel.SAFE
            message = "Standard file copy operation."
            suggestion = None

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
        )


class ChmodRule(Rule):
    """Safety rule for chmod command."""

    name = "chmod_command"
    description = "Detects dangerous chmod operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is chmod."""
        return command.command == "chmod"

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze chmod command for dangers."""
        has_recursive = command.has_any_flag(RECURSIVE_FLAGS)
        args = command.args

        # Check for dangerous permissions
        dangerous_perms = ["777", "666", "a+rwx", "ugo+rwx"]
        has_dangerous_perm = any(perm in args for perm in dangerous_perms)

        # Check for system paths
        targets = [arg for arg in args if not arg.startswith("-") and arg not in dangerous_perms]
        has_dangerous_path = any(_path_is_dangerous(path) for path in targets)

        if has_dangerous_perm and has_recursive and has_dangerous_path:
            danger_level = DangerLevel.CRITICAL
            message = "Setting world-writable permissions recursively on system paths is extremely dangerous!"
        elif has_dangerous_perm and has_recursive:
            danger_level = DangerLevel.HIGH
            message = "Setting world-writable permissions recursively can create security vulnerabilities."
        elif has_dangerous_perm:
            danger_level = DangerLevel.MEDIUM
            message = "Setting world-writable permissions can create security vulnerabilities."
        elif has_recursive and has_dangerous_path:
            danger_level = DangerLevel.HIGH
            message = "Recursively changing permissions on system paths could break your system."
        else:
            danger_level = DangerLevel.LOW
            message = "This will change file permissions."

        suggestion = None
        if has_dangerous_perm:
            suggestion = "Avoid 777 or 666 permissions. Use minimal necessary permissions (e.g., 755, 644)."

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
        )


class ChownRule(Rule):
    """Safety rule for chown command."""

    name = "chown_command"
    description = "Detects dangerous chown operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is chown."""
        return command.command == "chown"

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze chown command for dangers."""
        has_recursive = command.has_any_flag(RECURSIVE_FLAGS)

        targets = command.args
        has_dangerous_path = any(_path_is_dangerous(path) for path in targets)

        if has_recursive and has_dangerous_path:
            danger_level = DangerLevel.CRITICAL
            message = (
                "Recursively changing ownership on system paths can break your system!"
            )
        elif has_dangerous_path:
            danger_level = DangerLevel.HIGH
            message = "Changing ownership of system files can cause serious issues."
        elif has_recursive:
            danger_level = DangerLevel.MEDIUM
            message = "Recursively changing ownership affects all files in the directory tree."
        else:
            danger_level = DangerLevel.LOW
            message = "This will change file ownership."

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
        )
