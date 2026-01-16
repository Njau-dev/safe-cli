"""
CLI entry point for safe-cli.
"""

from typing import List, Optional

import typer
from rich.console import Console

from safe_cli import __version__
from safe_cli.core.analyzer import CommandAnalyzer
from safe_cli.core.executor import CommandExecutor
from safe_cli.core.parser import CommandParser
from safe_cli.ui.display import DisplayFormatter
from safe_cli.ui.prompts import PromptResponse, UserPrompt

app = typer.Typer(
    name="safe",
    help="Know before you run - A safety wrapper for dangerous shell commands",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        console.print(
            f"[bold blue]safe-cli[/bold blue] version [green]{__version__}[/green]"
        )
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    command: Optional[List[str]] = typer.Argument(
        None,
        help="Command to analyze and run safely",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-d",
        help="Show what would happen without executing",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompts (use with caution)",
    ),
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    ),
) -> None:
    """
    Analyze and safely execute shell commands.

    Examples:
        safe rm -rf /tmp/test
        safe --dry-run git reset --hard
        safe --yes mv file.txt backup/
    """
    # If no command provided, show help
    if not command:
        console.print("[yellow]No command provided.[/yellow]")
        console.print("\nUsage: [bold]safe [OPTIONS] COMMAND[/bold]")
        console.print("\nExamples:")
        console.print("  safe rm -rf /tmp/test")
        console.print("  safe --dry-run docker system prune")
        console.print("  safe --yes git push --force")
        console.print("\nRun [bold]safe --help[/bold] for more information.")
        raise typer.Exit(1)

    # Initialize components
    command_str = " ".join(command)
    parser = CommandParser()
    analyzer = CommandAnalyzer()
    display = DisplayFormatter(console)
    prompt = UserPrompt(console)
    executor = CommandExecutor()

    try:
        # Parse command
        parsed = parser.parse(command_str)

        # Analyze for risks
        result = analyzer.analyze(parsed)

        # Display analysis
        display.display_analysis(result, dry_run=dry_run)

        # If dry run, stop here
        if dry_run:
            display.display_info("Dry run complete - no command was executed.")
            raise typer.Exit(0)

        # Get user decision
        response = prompt.confirm_execution(result, skip_prompt=yes)

        # Handle user response
        if response == PromptResponse.ABORT:
            display.display_execution_aborted()
            raise typer.Exit(0)

        elif response == PromptResponse.VIEW_ALTERNATIVE:
            # Show alternatives and let user choose
            if result.safe_alternatives:
                use_alt, chosen = prompt.choose_alternative(result.safe_alternatives)

                if chosen:
                    # User chose an alternative
                    console.print()
                    display.display_comparison(command_str, chosen)
                    display.display_execution_start(chosen)
                    exec_result = executor.execute(chosen)
                elif use_alt is False and chosen is None:
                    # User chose to abort
                    display.display_execution_aborted()
                    raise typer.Exit(0)
                else:
                    # User chose original (shouldn't happen, but handle it)
                    display.display_execution_start(command_str)
                    exec_result = executor.execute(command_str)
            else:
                # No alternatives available (shouldn't reach here)
                display.display_execution_start(command_str)
                exec_result = executor.execute(command_str)

        else:  # PromptResponse.CONTINUE
            # Execute original command
            display.display_execution_start(command_str)
            exec_result = executor.execute(command_str)

        # Display execution results
        if exec_result.stdout:
            console.print(exec_result.stdout, end="")
        if exec_result.stderr:
            console.print(f"[red]{exec_result.stderr}[/red]", end="")

        # Show completion status
        display.display_execution_complete(exec_result.success)

        # Exit with command's return code
        raise typer.Exit(exec_result.return_code)

    except ValueError as e:
        display.display_error(str(e))
        raise typer.Exit(1) from e
    except KeyboardInterrupt as e:
        console.print("\n[yellow]⚠️  Interrupted by user[/yellow]")
        raise typer.Exit(130) from e
    except typer.Exit:
        # Re-raise typer exits (normal flow)
        raise
    except Exception as e:
        # Only show unexpected errors that aren't normal exits
        display.display_error(f"Unexpected error: {e}")
        raise typer.Exit(1) from e


if __name__ == "__main__":
    app()
