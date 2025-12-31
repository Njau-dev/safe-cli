"""
CLI entry point for safe-cli.
"""

from typing import List, Optional

import typer
from rich.console import Console

from safe_cli import __version__
from safe_cli.core.parser import CommandParser
from safe_cli.core.analyzer import CommandAnalyzer

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
            f"[bold blue]safe-cli[/bold blue] version [green]{__version__}[/green]")
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

    # Join command parts
    command_str = " ".join(command)

    # Parse and analyze the command
    parser = CommandParser()
    try:
        parsed = parser.parse(command_str)
        analyzer = CommandAnalyzer()
        result = analyzer.analyze(parsed)

        # Show analysis
        if dry_run:
            console.print(
                "[bold cyan]🔍 Dry Run Mode - Analysis Only[/bold cyan]\n")

        # Show danger level with color and emoji
        danger_color = result.danger_level.color
        danger_emoji = result.danger_level.emoji
        console.print(f"[bold]Command:[/bold] {command_str}")
        console.print(
            f"[bold]Danger Level:[/bold] [{danger_color}]{result.danger_level.name} {danger_emoji}[/{danger_color}]\n")

        # Show primary warning
        if result.danger_level != result.danger_level.SAFE:
            console.print(
                f"[{danger_color}]⚠️  {result.primary_warning}[/{danger_color}]\n")

        # Show suggestions if any
        if result.suggestions:
            console.print("[bold cyan]💡 Suggestions:[/bold cyan]")
            for suggestion in result.suggestions:
                console.print(f"  • {suggestion}")
            console.print()

        # Show safe alternatives if any
        if result.safe_alternatives:
            console.print("[bold green]✅ Safe Alternatives:[/bold green]")
            for alt in result.safe_alternatives:
                console.print(f"  → {alt}")
            console.print()

        # TODO: Day 4 - Interactive prompt and execution
        if not dry_run:
            console.print(
                "[yellow]💬 Interactive prompts and execution coming in Day 4[/yellow]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
