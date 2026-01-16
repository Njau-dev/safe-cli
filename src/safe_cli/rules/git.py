"""
Git operation safety rules.
"""

from safe_cli.core.parser import ParsedCommand
from safe_cli.rules.base import Rule, RuleMatch
from safe_cli.utils.constants import DangerLevel


class GitResetRule(Rule):
    """Safety rule for git reset command."""

    name = "git_reset"
    description = "Detects dangerous git reset operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is git reset."""
        return command.command == "git" and "reset" in command.args

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze git reset command for dangers."""
        has_hard = "--hard" in command.flags
        has_soft = "--soft" in command.flags
        has_mixed = "--mixed" in command.flags or (not has_hard and not has_soft)

        # Check how far back we're resetting
        has_head_ref = any("HEAD~" in arg or "HEAD^" in arg for arg in command.args)

        if has_hard:
            if has_head_ref:
                danger_level = DangerLevel.CRITICAL
                message = (
                    "This will permanently discard all uncommitted changes "
                    "and reset to a previous commit. All work will be lost!"
                )
            else:
                danger_level = DangerLevel.HIGH
                message = (
                    "This will permanently discard all uncommitted changes. "
                    "Staged and unstaged changes will be lost!"
                )

            suggestion = "Use 'git stash' to save your changes first, or 'git reset --soft' to keep changes."
            safe_alternative = command.raw.replace("--hard", "--soft")

        elif has_mixed:
            danger_level = DangerLevel.MEDIUM
            message = (
                "This will unstage changes but keep them in your working directory."
            )
            suggestion = "Use 'git reset --soft' if you want to keep changes staged."
            safe_alternative = command.raw.replace("reset", "reset --soft")

        else:  # --soft
            danger_level = DangerLevel.LOW
            message = "This will move HEAD but keep all changes staged."
            suggestion = None
            safe_alternative = None

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alternative,
        )


class GitPushForceRule(Rule):
    """Safety rule for git push --force."""

    name = "git_push_force"
    description = "Detects dangerous force push operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is git push with force."""
        return (
            command.command == "git"
            and "push" in command.args
            and (
                "--force" in command.flags
                or "-f" in command.flags
                or "--force-with-lease" in command.flags
            )
        )

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze git push --force for dangers."""
        has_force_with_lease = "--force-with-lease" in command.flags

        # Check if pushing to main/master
        is_main_branch = any(
            arg in ["main", "master", "origin/main", "origin/master"]
            for arg in command.args
        )

        if is_main_branch and not has_force_with_lease:
            danger_level = DangerLevel.CRITICAL
            message = (
                "Force pushing to main/master branch will rewrite history "
                "and could break the repository for all team members!"
            )
            suggestion = (
                "Use --force-with-lease instead of --force for safer forced pushes. "
                "Or better yet, avoid force pushing to main branches."
            )
            safe_alternative = command.raw.replace(
                "--force", "--force-with-lease"
            ).replace("-f", "--force-with-lease")

        elif has_force_with_lease:
            danger_level = DangerLevel.MEDIUM
            message = (
                "Force pushing will rewrite history. --force-with-lease provides "
                "some safety by checking remote hasn't changed."
            )
            suggestion = "Make sure no one else is working on this branch."
            safe_alternative = None

        else:
            danger_level = DangerLevel.HIGH
            message = (
                "Force pushing will rewrite remote history and could lose commits "
                "from other team members."
            )
            suggestion = "Use --force-with-lease instead for safer forced pushes."
            safe_alternative = command.raw.replace(
                "--force", "--force-with-lease"
            ).replace("-f", "--force-with-lease")

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alternative,
        )


class GitCleanRule(Rule):
    """Safety rule for git clean command."""

    name = "git_clean"
    description = "Detects dangerous git clean operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is git clean."""
        return command.command == "git" and "clean" in command.args

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze git clean for dangers."""
        has_force = "-f" in command.flags or "--force" in command.flags
        has_d = "-d" in command.flags
        has_x = "-x" in command.flags or "-X" in command.flags

        # Combined flags like -fd, -fdx
        combined_flags = "".join(
            [f for f in command.flags if f.startswith("-") and not f.startswith("--")]
        )
        if "f" in combined_flags:
            has_force = True
        if "d" in combined_flags:
            has_d = True
        if "x" in combined_flags or "X" in combined_flags:
            has_x = True

        if has_force and has_d and has_x:
            danger_level = DangerLevel.CRITICAL
            message = (
                "This will permanently delete ALL untracked files and directories, "
                "including ignored files. This cannot be undone!"
            )
            suggestion = "Run 'git clean -fdxn' first to see what would be deleted."
            safe_alternative = "git clean -fdxn"

        elif has_force and has_d:
            danger_level = DangerLevel.HIGH
            message = (
                "This will permanently delete all untracked files and directories. "
                "This cannot be undone!"
            )
            suggestion = "Run 'git clean -fdn' first to preview what will be deleted."
            safe_alternative = "git clean -fdn"

        elif has_force:
            danger_level = DangerLevel.MEDIUM
            message = "This will permanently delete untracked files."
            suggestion = "Run 'git clean -fn' first to see what would be deleted."
            safe_alternative = "git clean -fn"

        else:
            danger_level = DangerLevel.LOW
            message = "Use -f flag to actually delete files (dry run mode)."
            suggestion = None
            safe_alternative = None

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alternative,
        )


class GitBranchDeleteRule(Rule):
    """Safety rule for git branch -D (force delete)."""

    name = "git_branch_delete"
    description = "Detects force deletion of git branches"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is git branch -D."""
        return (
            command.command == "git"
            and "branch" in command.args
            and ("-D" in command.flags or "--delete --force" in " ".join(command.flags))
        )

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze git branch delete for dangers."""
        danger_level = DangerLevel.HIGH
        message = (
            "Force deleting a branch will remove it even if it contains unmerged changes. "
            "This could result in lost commits!"
        )
        suggestion = (
            "Use 'git branch -d' (lowercase) to safely delete only merged branches."
        )
        safe_alternative = command.raw.replace("-D", "-d")

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alternative,
        )
