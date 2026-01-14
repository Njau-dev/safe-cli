"""
Docstring for safe_cli.rules.docker
"""
"""
Docker operation safety rules.
"""


from safe_cli.core.parser import ParsedCommand
from typing import Optional
from safe_cli.utils.constants import DangerLevel, FORCE_FLAGS
from safe_cli.rules.base import Rule, RuleMatch


class DockerSystemPruneRule(Rule):
    """Safety rule for docker system prune."""

    name = "docker_system_prune"
    description = "Detects dangerous docker system prune operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is docker system prune."""
        return (
            command.command == "docker"
            and "system" in command.args
            and "prune" in command.args
        )

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze docker system prune for dangers."""
        has_all = "-a" in command.flags or "--all" in command.flags
        has_volumes = "--volumes" in command.flags
        has_force = "-f" in command.flags or "--force" in command.flags

        if has_all and has_volumes:
            danger_level = DangerLevel.CRITICAL
            message = (
                "This will remove ALL unused containers, networks, images (both dangling and unused), "
                "AND volumes. This includes data volumes which could contain important data!"
            )
            suggestion = "Run without --volumes first, then manually clean volumes if needed."
            safe_alternative = command.raw.replace("--volumes", "")

        elif has_all:
            danger_level = DangerLevel.HIGH
            message = (
                "This will remove ALL unused containers, networks, and images "
                "(including non-dangling images). You may lose important images!"
            )
            suggestion = "Run without -a/--all to only remove dangling images."
            safe_alternative = command.raw.replace(
                "-a", "").replace("--all", "")

        elif has_volumes:
            danger_level = DangerLevel.HIGH
            message = (
                "This will remove unused volumes which may contain important data. "
                "Volume data cannot be recovered!"
            )
            suggestion = "List volumes first with 'docker volume ls' and remove specific ones."
            safe_alternative = "docker volume ls"

        else:
            danger_level = DangerLevel.MEDIUM
            message = (
                "This will remove unused containers, networks, and dangling images. "
                "Active resources won't be affected."
            )
            suggestion = "Review what will be removed with 'docker system df' first."
            safe_alternative = None

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alternative,
        )


class DockerRmRule(Rule):
    """Safety rule for docker rm command."""

    name = "docker_rm"
    description = "Detects dangerous docker rm operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is docker rm."""
        return (
            command.command == "docker"
            and "rm" in command.args
        )

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze docker rm for dangers."""
        # Check for force and volume flags (including combined like -fv)
        has_force = command.has_any_flag(["-f", "--force"])
        has_volumes = command.has_any_flag(["-v", "--volumes"])

        # Also check combined flags like -fv
        for flag in command.flags:
            if flag.startswith("-") and not flag.startswith("--"):
                if "f" in flag:
                    has_force = True
                if "v" in flag:
                    has_volumes = True

        # Check if removing multiple containers or using wildcards
        container_args = [arg for arg in command.args if arg != "rm"]
        is_multiple = len(container_args) > 1 or any(
            "*" in arg for arg in container_args)

        if has_force and has_volumes and is_multiple:
            danger_level = DangerLevel.CRITICAL
            message = (
                "This will force remove multiple containers AND their associated volumes. "
                "Data in volumes will be permanently lost!"
            )
            suggestion = "Remove force and volumes flags, stop containers first with 'docker stop'."
            safe_alternative = f"docker stop {' '.join(container_args)}"

        elif has_force and is_multiple:
            danger_level = DangerLevel.HIGH
            message = (
                "Force removing multiple containers will stop and remove them immediately. "
                "Running containers will be killed!"
            )
            suggestion = "Stop containers gracefully first with 'docker stop'."
            safe_alternative = f"docker stop {' '.join(container_args)}"

        elif has_volumes:
            danger_level = DangerLevel.HIGH
            message = (
                "This will remove the container and its associated volumes. "
                "Data in volumes will be permanently lost!"
            )
            suggestion = "Remove the -v/--volumes flag to preserve volume data."
            safe_alternative = command.raw.replace(
                "-v", "").replace("--volumes", "")

        elif has_force:
            danger_level = DangerLevel.MEDIUM
            message = "Force removing will stop and remove the container immediately."
            suggestion = "Stop the container first with 'docker stop' for graceful shutdown."
            safe_alternative = f"docker stop {' '.join(container_args)}"

        else:
            danger_level = DangerLevel.LOW
            message = "This will remove stopped container(s)."
            suggestion = None
            safe_alternative = None

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alternative,
        )


class DockerRmiRule(Rule):
    """Safety rule for docker rmi command."""

    name = "docker_rmi"
    description = "Detects dangerous docker rmi operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is docker rmi."""
        return (
            command.command == "docker"
            and "rmi" in command.args
        )

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze docker rmi for dangers."""
        has_force = "-f" in command.flags or "--force" in command.flags

        # Check if removing multiple images
        image_args = [arg for arg in command.args if arg != "rmi"]
        is_multiple = len(image_args) > 1 or any(
            "*" in arg for arg in image_args)

        if has_force and is_multiple:
            danger_level = DangerLevel.HIGH
            message = (
                "Force removing multiple images will delete them even if containers are using them. "
                "This could break running applications!"
            )
            suggestion = "Remove the -f/--force flag and handle used images manually."
            safe_alternative = command.raw.replace(
                "-f", "").replace("--force", "")

        elif has_force:
            danger_level = DangerLevel.MEDIUM
            message = (
                "Force removing will delete the image even if containers are using it. "
                "This could break running containers!"
            )
            suggestion = "Remove the -f flag to see if image is in use."
            safe_alternative = command.raw.replace(
                "-f", "").replace("--force", "")

        elif is_multiple:
            danger_level = DangerLevel.MEDIUM
            message = "This will remove multiple Docker images. Make sure they're not needed."
            suggestion = "Use 'docker images' to review images before removing."
            safe_alternative = None

        else:
            danger_level = DangerLevel.LOW
            message = "This will remove a Docker image."
            suggestion = None
            safe_alternative = None

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alternative,
        )


class DockerVolumePruneRule(Rule):
    """Safety rule for docker volume prune."""

    name = "docker_volume_prune"
    description = "Detects dangerous docker volume prune operations"

    def matches(self, command: ParsedCommand) -> bool:
        """Check if command is docker volume prune."""
        return (
            command.command == "docker"
            and "volume" in command.args
            and "prune" in command.args
        )

    def analyze(self, command: ParsedCommand) -> RuleMatch:
        """Analyze docker volume prune for dangers."""
        has_force = "-f" in command.flags or "--force" in command.flags

        danger_level = DangerLevel.CRITICAL
        message = (
            "This will permanently delete ALL unused Docker volumes and their data. "
            "Volume data cannot be recovered! This includes volumes that might be needed later."
        )
        suggestion = (
            "List volumes first with 'docker volume ls' and remove specific ones. "
            "Or backup important data before pruning."
        )
        safe_alternative = "docker volume ls"

        return RuleMatch(
            rule_name=self.name,
            danger_level=danger_level,
            message=message,
            suggestion=suggestion,
            safe_alternative=safe_alternative,
        )
