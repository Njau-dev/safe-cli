"""
Tests for command executor.
"""

import pytest
from safe_cli.core.executor import CommandExecutor, ExecutionResult


class TestCommandExecutor:
    """Test suite for CommandExecutor."""

    @pytest.fixture
    def executor(self) -> CommandExecutor:
        """Create executor instance."""
        return CommandExecutor()

    def test_executor_initializes(self, executor: CommandExecutor) -> None:
        """Test that executor initializes correctly."""
        assert executor is not None
        assert executor.shell is True

    def test_execute_simple_command(self, executor: CommandExecutor) -> None:
        """Test executing a simple command."""
        result = executor.execute("echo 'test'")

        assert isinstance(result, ExecutionResult)
        assert result.success
        assert result.return_code == 0
        assert "test" in result.stdout

    def test_execute_command_with_args(self, executor: CommandExecutor) -> None:
        """Test executing command with arguments."""
        result = executor.execute("echo hello world")

        assert result.success
        assert "hello world" in result.stdout

    def test_execute_failing_command(self, executor: CommandExecutor) -> None:
        """Test executing a command that fails."""
        result = executor.execute("exit 1")

        assert not result.success
        assert result.return_code == 1

    def test_execute_nonexistent_command(self, executor: CommandExecutor) -> None:
        """Test executing a nonexistent command."""
        result = executor.execute("nonexistent_command_xyz")

        assert not result.success
        assert result.return_code != 0

    def test_execution_result_command_preserved(
        self, executor: CommandExecutor
    ) -> None:
        """Test that executed command is preserved in result."""
        cmd = "echo test"
        result = executor.execute(cmd)

        assert result.command == cmd

    def test_execution_result_has_stdout(self, executor: CommandExecutor) -> None:
        """Test that stdout is captured."""
        result = executor.execute("echo hello")

        assert result.stdout
        assert "hello" in result.stdout

    def test_execution_result_has_stderr(self, executor: CommandExecutor) -> None:
        """Test that stderr is captured."""
        result = executor.execute("echo error >&2")

        assert result.stderr or "error" in result.stdout  # Shell dependent

    def test_execution_result_output_property(self, executor: CommandExecutor) -> None:
        """Test that output property combines stdout and stderr."""
        result = executor.execute("echo test")

        assert result.output
        assert isinstance(result.output, str)

    def test_dry_run_mode(self, executor: CommandExecutor) -> None:
        """Test dry run mode doesn't execute."""
        result = executor.dry_run("rm -rf /")

        assert result.success
        assert "DRY RUN" in result.stdout
        assert "rm -rf /" in result.stdout

    def test_dry_run_preserves_command(self, executor: CommandExecutor) -> None:
        """Test that dry run preserves the command."""
        cmd = "dangerous_command"
        result = executor.dry_run(cmd)

        assert result.command == cmd

    def test_execute_with_timeout(self, executor: CommandExecutor) -> None:
        """Test executing with timeout."""
        # Quick command should complete
        result = executor.execute("echo fast", timeout=5)

        assert result.success

    def test_execute_timeout_expires(self, executor: CommandExecutor) -> None:
        """Test that timeout is enforced."""
        # Sleep longer than timeout
        result = executor.execute("sleep 10", timeout=1)

        assert not result.success
        assert result.error
        assert "timed out" in result.error.lower()

    def test_multiple_executions(self, executor: CommandExecutor) -> None:
        """Test multiple sequential executions."""
        results = [
            executor.execute("echo first"),
            executor.execute("echo second"),
            executor.execute("echo third"),
        ]

        assert all(r.success for r in results)
        assert "first" in results[0].stdout
        assert "second" in results[1].stdout
        assert "third" in results[2].stdout


class TestExecutionResult:
    """Test suite for ExecutionResult."""

    def test_execution_result_creation(self) -> None:
        """Test creating an execution result."""
        result = ExecutionResult(
            command="test",
            success=True,
            return_code=0,
            stdout="output",
            stderr="",
        )

        assert result.command == "test"
        assert result.success is True
        assert result.return_code == 0
        assert result.stdout == "output"
        assert result.stderr == ""

    def test_execution_result_with_error(self) -> None:
        """Test execution result with error."""
        result = ExecutionResult(
            command="test",
            success=False,
            return_code=1,
            stdout="",
            stderr="error message",
            error="Something went wrong",
        )

        assert not result.success
        assert result.error == "Something went wrong"

    def test_output_property_combines_streams(self) -> None:
        """Test that output property combines stdout and stderr."""
        result = ExecutionResult(
            command="test",
            success=True,
            return_code=0,
            stdout="out",
            stderr="err",
        )

        output = result.output
        assert "out" in output
        assert "err" in output

    def test_output_property_handles_empty_streams(self) -> None:
        """Test output property with empty streams."""
        result = ExecutionResult(
            command="test",
            success=True,
            return_code=0,
            stdout="",
            stderr="",
        )

        assert result.output == ""

    def test_output_property_with_only_stdout(self) -> None:
        """Test output with only stdout."""
        result = ExecutionResult(
            command="test",
            success=True,
            return_code=0,
            stdout="only stdout",
            stderr="",
        )

        assert result.output == "only stdout"

    def test_output_property_with_only_stderr(self) -> None:
        """Test output with only stderr."""
        result = ExecutionResult(
            command="test",
            success=False,
            return_code=1,
            stdout="",
            stderr="only stderr",
        )

        assert result.output == "only stderr"


class TestCommandExecutorRealtime:
    """Test suite for realtime execution."""

    @pytest.fixture
    def executor(self) -> CommandExecutor:
        """Create executor instance."""
        return CommandExecutor()

    def test_realtime_execution(self, executor: CommandExecutor) -> None:
        """Test realtime execution."""
        result = executor.execute_with_realtime_output("echo test")

        assert result.success
        assert "test" in result.stdout

    def test_realtime_execution_with_timeout(self, executor: CommandExecutor) -> None:
        """Test realtime execution with timeout."""
        result = executor.execute_with_realtime_output("echo fast", timeout=5)

        assert result.success

    def test_realtime_timeout_expires(self, executor: CommandExecutor) -> None:
        """Test realtime execution timeout."""
        result = executor.execute_with_realtime_output("sleep 10", timeout=1)

        assert not result.success
        assert result.error
