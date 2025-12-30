"""
Command parser for tokenizing and analyzing shell commands.
"""

import shlex
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ParsedCommand:
    """Represents a parsed shell command."""

    raw: str
    tokens: List[str]
    command: str
    args: List[str]
    flags: List[str]

    def has_flag(self, flag: str) -> bool:
        """Check if command has a specific flag."""
        # Direct match or startswith handles flags like '--output=file'
        if flag in self.flags or any(f.startswith(flag) for f in self.flags):
            return True

        # Support combined short flags (e.g., '-rf' should match '-r' and '-f')
        # Only apply this logic for single-dash short flags like '-f'
        if flag.startswith("-") and not flag.startswith("--") and len(flag) == 2:
            short = flag[1]
            for f in self.flags:
                if f.startswith("-") and not f.startswith("--"):
                    # skip lone '-' and negative numbers
                    if len(f) > 1 and short in f[1:]:
                        return True

        return False

    def has_any_flag(self, flags: List[str]) -> bool:
        """Check if command has any of the specified flags."""
        return any(self.has_flag(f) for f in flags)

    def get_flag_value(self, flag: str) -> Optional[str]:
        """Get value for a flag like --output=file.txt or -o file.txt."""
        # Check --flag=value format
        for f in self.flags:
            if f.startswith(f"{flag}="):
                return f.split("=", 1)[1]

        # Check --flag value format
        try:
            idx = self.flags.index(flag)
            if idx + 1 < len(self.args):
                return self.args[idx + 1]
        except ValueError:
            pass

        return None


class CommandParser:
    """Parser for shell commands."""

    def parse(self, command: str) -> ParsedCommand:
        """
        Parse a shell command into structured components.

        Args:
            command: Raw command string

        Returns:
            ParsedCommand object with parsed components

        Raises:
            ValueError: If command is empty or invalid
        """
        if not command or not command.strip():
            raise ValueError("Command cannot be empty")

        # Tokenize using shlex (handles quotes, escapes, etc.)
        try:
            tokens = shlex.split(command)
        except ValueError as e:
            raise ValueError(f"Invalid command syntax: {e}") from e

        if not tokens:
            raise ValueError("Command produced no tokens")

        # First token is always the command
        cmd = tokens[0]
        remaining = tokens[1:]

        # Separate flags from arguments
        flags = []
        args = []

        for token in remaining:
            if token.startswith("-"):
                flags.append(token)
            else:
                args.append(token)

        return ParsedCommand(
            raw=command,
            tokens=tokens,
            command=cmd,
            args=args,
            flags=flags,
        )

    def is_compound_command(self, command: str) -> bool:
        """
        Check if command contains pipes, redirects, or logical operators.

        Args:
            command: Raw command string

        Returns:
            True if command is compound
        """
        compound_operators = ["|", "&&", "||", ";", ">", ">>", "<"]
        return any(op in command for op in compound_operators)

    def split_compound_command(self, command: str) -> List[str]:
        """
        Split compound command into individual commands.

        Args:
            command: Raw command string with pipes/operators

        Returns:
            List of individual command strings

        Note:
            This is a simple split for MVP. Day 2+ will handle complex cases.
        """
        # For MVP, just split on common operators
        # TODO: Properly handle quotes and escapes
        import re

        # Split on pipes, semicolons, and logical operators
        parts = re.split(r"[|;&]|&&|\|\|", command)
        return [p.strip() for p in parts if p.strip()]
