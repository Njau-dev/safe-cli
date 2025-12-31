"""
Safe alternative suggestion generator.
"""

from typing import List, Optional

from safe_cli.core.parser import ParsedCommand
from safe_cli.utils.constants import (
    FORCE_FLAGS,
    INTERACTIVE_FLAGS,
    RECURSIVE_FLAGS,
)


class SafeAlternativeGenerator:
    """Generates safer alternatives for dangerous commands."""

    def generate(self, command: ParsedCommand) -> Optional[str]:
        """
        Generate a safer alternative for a command.

        Args:
            command: Parsed command

        Returns:
            Safer alternative command or None
        """
        cmd = command.command

        if cmd == "rm":
            return self._safe_rm(command)
        elif cmd == "mv":
            return self._safe_mv(command)
        elif cmd == "cp":
            return self._safe_cp(command)
        elif cmd == "chmod":
            return self._safe_chmod(command)
        elif cmd == "chown":
            return self._safe_chown(command)

        return None

    def _safe_rm(self, command: ParsedCommand) -> Optional[str]:
        """Generate safer rm alternative."""
        # If already has interactive flag, no alternative needed
        if command.has_any_flag(INTERACTIVE_FLAGS):
            return None

        # Add -i flag
        flags = ["-i"] + command.flags
        args = command.args

        parts = [command.command] + flags + args
        return " ".join(parts)

    def _safe_mv(self, command: ParsedCommand) -> Optional[str]:
        """Generate safer mv alternative."""
        # If already has interactive flag, no alternative needed
        if command.has_any_flag(INTERACTIVE_FLAGS):
            return None

        # Add -i flag, remove -f if present
        flags = [f for f in command.flags if f not in FORCE_FLAGS]
        flags = ["-i"] + flags
        args = command.args

        parts = [command.command] + flags + args
        return " ".join(parts)

    def _safe_cp(self, command: ParsedCommand) -> Optional[str]:
        """Generate safer cp alternative."""
        # If already has interactive flag, no alternative needed
        if command.has_any_flag(INTERACTIVE_FLAGS):
            return None

        # Only suggest if has force flag
        if not command.has_any_flag(FORCE_FLAGS):
            return None

        # Add -i flag, remove -f if present
        flags = [f for f in command.flags if f not in FORCE_FLAGS]
        flags = ["-i"] + flags
        args = command.args

        parts = [command.command] + flags + args
        return " ".join(parts)

    def _safe_chmod(self, command: ParsedCommand) -> Optional[str]:
        """Generate safer chmod alternative."""
        # Check for dangerous permissions
        dangerous_perms = ["777", "666", "a+rwx", "ugo+rwx"]

        # Find if any dangerous permission is in args
        new_args = []
        changed = False

        for arg in command.args:
            if arg in dangerous_perms:
                # Suggest 755 instead of 777, 644 instead of 666
                if arg in ["777", "a+rwx", "ugo+rwx"]:
                    new_args.append("755")
                    changed = True
                elif arg == "666":
                    new_args.append("644")
                    changed = True
                else:
                    new_args.append(arg)
            else:
                new_args.append(arg)

        if not changed:
            return None

        parts = [command.command] + command.flags + new_args
        return " ".join(parts)

    def _safe_chown(self, command: ParsedCommand) -> Optional[str]:
        """Generate safer chown alternative."""
        # For chown, main suggestion is to avoid recursive on system paths
        # Hard to generate alternative without knowing intent
        # Return None - suggestions will guide user
        return None

    def generate_multiple(
        self, command: ParsedCommand, count: int = 3
    ) -> List[str]:
        """
        Generate multiple safer alternatives.

        Args:
            command: Parsed command
            count: Number of alternatives to generate

        Returns:
            List of alternative commands
        """
        alternatives = []

        # Primary alternative
        primary = self.generate(command)
        if primary:
            alternatives.append(primary)

        # Additional alternatives based on command type
        if command.command == "rm" and len(alternatives) < count:
            # Suggest using trash instead
            alternatives.append(
                f"# Move to trash instead: mv {' '.join(command.args)} ~/.Trash/")

        if command.command == "chmod" and len(alternatives) < count:
            # Suggest more specific permissions
            alternatives.append(
                "# Use more specific permissions: 644 for files, 755 for executables")

        return alternatives[:count]
