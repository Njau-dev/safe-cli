"""
Safe command execution.
"""

import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExecutionResult:
    """Result of command execution."""

    command: str
    success: bool
    return_code: int
    stdout: str
    stderr: str
    error: Optional[str] = None

    @property
    def output(self) -> str:
        """Get combined output."""
        parts = []
        if self.stdout:
            parts.append(self.stdout)
        if self.stderr:
            parts.append(self.stderr)
        return "\n".join(parts)


class CommandExecutor:
    """Safely executes shell commands."""

    def __init__(self, shell: bool = True) -> None:
        """
        Initialize command executor.

        Args:
            shell: Whether to execute via shell
        """
        self.shell = shell

    def execute(self, command: str, timeout: Optional[int] = None) -> ExecutionResult:
        """
        Execute a command safely.

        Args:
            command: Command string to execute
            timeout: Timeout in seconds (None for no timeout)

        Returns:
            ExecutionResult with command output and status
        """
        try:
            # Execute command
            result = subprocess.run(
                command,
                shell=self.shell,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            return ExecutionResult(
                command=command,
                success=result.returncode == 0,
                return_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
            )

        except subprocess.TimeoutExpired as e:
            return ExecutionResult(
                command=command,
                success=False,
                return_code=-1,
                stdout=e.stdout.decode() if e.stdout else "",
                stderr=e.stderr.decode() if e.stderr else "",
                error=f"Command timed out after {timeout} seconds",
            )

        except Exception as e:
            return ExecutionResult(
                command=command,
                success=False,
                return_code=-1,
                stdout="",
                stderr="",
                error=str(e),
            )

    def execute_with_realtime_output(
        self, command: str, timeout: Optional[int] = None
    ) -> ExecutionResult:
        """
        Execute command with real-time output streaming.

        Args:
            command: Command to execute
            timeout: Timeout in seconds

        Returns:
            ExecutionResult with final status
        """
        try:
            # Execute with stdout/stderr streaming
            process = subprocess.Popen(
                command,
                shell=self.shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Wait for completion
            stdout, stderr = process.communicate(timeout=timeout)

            return ExecutionResult(
                command=command,
                success=process.returncode == 0,
                return_code=process.returncode,
                stdout=stdout,
                stderr=stderr,
            )

        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            return ExecutionResult(
                command=command,
                success=False,
                return_code=-1,
                stdout=stdout,
                stderr=stderr,
                error=f"Command timed out after {timeout} seconds",
            )

        except Exception as e:
            return ExecutionResult(
                command=command,
                success=False,
                return_code=-1,
                stdout="",
                stderr="",
                error=str(e),
            )

    def dry_run(self, command: str) -> ExecutionResult:
        """
        Simulate command execution without actually running it.

        Args:
            command: Command to simulate

        Returns:
            ExecutionResult indicating dry run
        """
        return ExecutionResult(
            command=command,
            success=True,
            return_code=0,
            stdout=f"[DRY RUN] Would execute: {command}",
            stderr="",
        )
