"""
System-level command safety rules.
"""

from safe_cli.core.parser import ParsedCommand
from safe_cli.rules.base import Rule, RuleMatch
from safe_cli.utils.constants import DANGEROUS_PATHS, DangerLevel


class SudoRule(Rule):
    """Safety rule for sudo commands."""

    name = "sudo_command"
    description = "Detects sudo usage with potentially dangerous commands"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command uses sudo."""
        return command.command == "sudo"

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze sudo command for dangers."""
        # Get the actual command being run with sudo
        actual_cmd = command.args[0] if command.args else ""

        # Check for dangerous command combinations
        dangerous_commands = ["rm", "dd", "mkfs", "fdisk", "parted", "chmod", "chown"]
        is_dangerous_cmd = actual_cmd in dangerous_commands

        # Check if modifying system paths (exclude /dev/zero, /dev/null which are safe sources)
        safe_dev_paths = ["/dev/zero", "/dev/null", "/dev/random", "/dev/urandom"]
        has_system_path = any(
            any(path in arg for path in DANGEROUS_PATHS)
            and not any(safe in arg for safe in safe_dev_paths)
            for arg in command.args
        )

        if is_dangerous_cmd and has_system_path:
            danger_level = DangerLevel.CRITICAL
            message = (
                f"Running '{actual_cmd}' with sudo on system paths can destroy your system! "
                "Root privileges allow unrestricted access to critical files."
            )
            suggestion = "Double-check the command and paths. Consider if sudo is really necessary."

        elif is_dangerous_cmd:
            danger_level = DangerLevel.HIGH
            message = (
                f"Running '{actual_cmd}' with sudo is dangerous. "
                "Root privileges can cause irreversible damage."
            )
            suggestion = "Verify the command is correct and necessary."

        elif has_system_path:
            danger_level = DangerLevel.HIGH
            message = (
                "Using sudo to modify system paths can break your system. "
                "Be very careful with root access."
            )
            suggestion = "Make sure you know what you're doing."

        else:
            danger_level = DangerLevel.MEDIUM
            message = (
                "Running commands with sudo gives them root privileges. "
                "Only use sudo when necessary."
            )
            suggestion = "Check if the command really needs root access."

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=None,
        )


class DdRule(Rule):
    """Safety rule for dd command."""

    name = "dd_command"
    description = "Detects dangerous dd operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is dd."""
        return command.command == "dd"

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze dd command for dangers."""
        # Check for dangerous output targets
        dangerous_of = ["/dev/sda", "/dev/sdb", "/dev/nvme", "/dev/disk"]

        of_arg = None
        for arg in command.args:
            if arg.startswith("of="):
                of_arg = arg.split("=", 1)[1]
                break

        if of_arg:
            is_dangerous_target = any(
                of_arg.startswith(dangerous) for dangerous in dangerous_of
            )

            if is_dangerous_target:
                danger_level = DangerLevel.CRITICAL
                message = (
                    "Writing to a disk device with dd will DESTROY all data on that disk! "
                    "This is one of the most dangerous commands in Linux."
                )
                suggestion = (
                    "Triple-check the device name. Use 'lsblk' to verify. "
                    "Make sure you have backups of any important data."
                )
                safe_alternative = "lsblk"
            else:
                danger_level = DangerLevel.MEDIUM
                message = "dd will overwrite the specified file or device."
                suggestion = "Make sure the output path is correct."
                safe_alternative = None
        else:
            danger_level = DangerLevel.LOW
            message = (
                "dd command detected. Make sure input/output parameters are correct."
            )
            suggestion = None
            safe_alternative = None

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alternative,
        )


class KillRule(Rule):
    """Safety rule for kill command."""

    name = "kill_command"
    description = "Detects dangerous process kill operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is kill or killall."""
        return command.command in ["kill", "killall"]

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze kill command for dangers."""
        has_9 = (
            "-9" in command.flags
            or "-KILL" in command.flags
            or "-SIGKILL" in command.flags
        )
        is_killall = command.command == "killall"

        # Check for dangerous process names
        dangerous_processes = ["init", "systemd", "launchd", "ssh", "sshd"]
        targets = command.args if is_killall else []
        has_dangerous_target = any(proc in dangerous_processes for proc in targets)

        if has_9 and has_dangerous_target:
            danger_level = DangerLevel.CRITICAL
            message = (
                f"Force killing critical system processes like {targets} can crash your system! "
                "This will immediately terminate the process without cleanup."
            )
            suggestion = "Don't kill critical system processes. If you must, try without -9 first."
            safe_alternative = (
                command.raw.replace("-9", "")
                .replace("-KILL", "")
                .replace("-SIGKILL", "")
            )

        elif has_9 and is_killall:
            danger_level = DangerLevel.HIGH
            message = (
                "killall -9 will force kill ALL processes with that name immediately. "
                "They won't have a chance to clean up or save state."
            )
            suggestion = "Try without -9 first to allow graceful termination."
            safe_alternative = (
                command.raw.replace("-9", "")
                .replace("-KILL", "")
                .replace("-SIGKILL", "")
            )

        elif has_9:
            danger_level = DangerLevel.MEDIUM
            message = (
                "kill -9 sends SIGKILL which cannot be caught or ignored. "
                "The process will be terminated immediately without cleanup."
            )
            suggestion = "Try regular kill first (SIGTERM) to allow graceful shutdown."
            safe_alternative = (
                command.raw.replace("-9", "")
                .replace("-KILL", "")
                .replace("-SIGKILL", "")
            )

        elif is_killall:
            danger_level = DangerLevel.MEDIUM
            message = "killall will terminate ALL processes with the specified name."
            suggestion = "Use 'kill' with specific PIDs for more control."
            safe_alternative = None

        else:
            danger_level = DangerLevel.LOW
            message = (
                "This will send SIGTERM to the process, allowing graceful shutdown."
            )
            suggestion = None
            safe_alternative = None

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alternative,
        )


class ShutdownRule(Rule):
    """Safety rule for shutdown/reboot commands."""

    name = "shutdown_command"
    description = "Detects system shutdown/reboot operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is shutdown or reboot."""
        return command.command in ["shutdown", "reboot", "halt", "poweroff"]

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze shutdown command for dangers."""
        is_immediate = (
            "now" in command.args
            or "-h" in command.flags
            or command.command in ["reboot", "halt", "poweroff"]
        )

        if is_immediate:
            danger_level = DangerLevel.HIGH
            message = (
                "This will immediately shutdown/reboot the system. "
                "All running processes will be terminated, work may be lost."
            )
            suggestion = (
                "Make sure all work is saved and other users are notified. "
                "Consider scheduling shutdown with a delay (e.g., 'shutdown +5')."
            )
            safe_alternative = "shutdown +5" if command.command == "shutdown" else None
        else:
            danger_level = DangerLevel.MEDIUM
            message = "This will schedule a system shutdown/reboot."
            suggestion = "Notify other users if this is a shared system."
            safe_alternative = None

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alternative,
        )


class MkfsRule(Rule):
    """Safety rule for mkfs (format filesystem) command."""

    name = "mkfs_command"
    description = "Detects filesystem formatting operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is mkfs or variants."""
        return command.command.startswith("mkfs") or command.command in [
            "mkfs.ext4",
            "mkfs.ext3",
            "mkfs.ntfs",
            "mkfs.vfat",
        ]

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze mkfs command for dangers."""
        danger_level = DangerLevel.CRITICAL
        message = (
            "This will FORMAT the specified device, DESTROYING ALL DATA on it! "
            "Formatting cannot be undone and all files will be permanently lost."
        )
        suggestion = (
            "Triple-check you have the correct device. Use 'lsblk' or 'fdisk -l' to verify. "
            "Make absolutely sure you have backups of any important data."
        )
        safe_alternative = "lsblk"

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alternative,
        )
