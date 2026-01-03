"""
Display formatting for analysis results.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from safe_cli.core.analyzer import AnalysisResult
from safe_cli.utils.constants import DangerLevel


class DisplayFormatter:
    """Formats analysis results for display."""

    def __init__(self, console: Console) -> None:
        """
        Initialize display formatter.
        
        Args:
            console: Rich console for output
        """
        self.console = console

    def display_analysis(self, result: AnalysisResult, dry_run: bool = False) -> None:
        """
        Display complete analysis results.
        
        Args:
            result: Analysis result to display
            dry_run: Whether this is a dry run
        """
        if dry_run:
            self.console.print(
                "\n[bold cyan]🔍 Dry Run Mode - Analysis Only[/bold cyan]\n")

        # Command and danger level
        self._display_header(result)

        # Warnings
        self._display_warnings(result)

        # Suggestions
        if result.suggestions:
            self._display_suggestions(result)

        # Safe alternatives
        if result.safe_alternatives:
            self._display_alternatives(result)

    def _display_header(self, result: AnalysisResult) -> None:
        """Display command and danger level."""
        danger_color = result.danger_level.color
        danger_emoji = result.danger_level.emoji

        self.console.print(f"[bold]Command:[/bold] {result.command.raw}")
        self.console.print(
            f"[bold]Danger Level:[/bold] [{danger_color}]"
            f"{result.danger_level.name} {danger_emoji}[/{danger_color}]\n"
        )

    def _display_warnings(self, result: AnalysisResult) -> None:
        """Display warning messages."""
        if result.danger_level == DangerLevel.SAFE:
            self.console.print(
                "[green]✅ No safety concerns detected.[/green]\n")
            return

        danger_color = result.danger_level.color

        # Primary warning in panel for emphasis
        if result.danger_level.requires_confirmation:
            panel = Panel(
                result.primary_warning,
                title="⚠️  Warning",
                border_style=danger_color,
                title_align="left",
            )
            self.console.print(panel)
        else:
            self.console.print(
                f"[{danger_color}]⚠️  {result.primary_warning}[/{danger_color}]")

        # Additional warnings if any
        if len(result.all_warnings) > 1:
            self.console.print(
                f"\n[bold {danger_color}]Additional Concerns:[/bold {danger_color}]")
            for warning in result.all_warnings[1:]:
                self.console.print(f"  • {warning}")

        self.console.print()

    def _display_suggestions(self, result: AnalysisResult) -> None:
        """Display suggestions."""
        self.console.print("[bold cyan]💡 Suggestions:[/bold cyan]")
        for suggestion in result.suggestions:
            self.console.print(f"  • {suggestion}")
        self.console.print()

    def _display_alternatives(self, result: AnalysisResult) -> None:
        """Display safe alternatives."""
        self.console.print("[bold green]✅ Safe Alternatives:[/bold green]")
        for alt in result.safe_alternatives:
            self.console.print(f"  → [green]{alt}[/green]")
        self.console.print()

    def display_comparison(self, original: str, alternative: str) -> None:
        """
        Display side-by-side comparison of original and alternative.
        
        Args:
            original: Original command
            alternative: Safe alternative
        """
        table = Table(show_header=True, header_style="bold")
        table.add_column("Original", style="red")
        table.add_column("Safe Alternative", style="green")

        table.add_row(original, alternative)

        self.console.print(table)
        self.console.print()

    def display_execution_start(self, command: str) -> None:
        """Display that execution is starting."""
        self.console.print(f"\n[cyan]▶️  Executing:[/cyan] {command}")

    def display_execution_complete(self, success: bool) -> None:
        """Display execution completion status."""
        if success:
            self.console.print(
                "[green]✅ Command completed successfully.[/green]\n")
        else:
            self.console.print("[red]❌ Command failed.[/red]\n")

    def display_execution_aborted(self) -> None:
        """Display that execution was aborted."""
        self.console.print("[yellow]🛑 Execution aborted by user.[/yellow]\n")

    def display_error(self, message: str) -> None:
        """Display an error message."""
        self.console.print(f"[red]❌ Error:[/red] {message}\n")

    def display_info(self, message: str) -> None:
        """Display an info message."""
        self.console.print(f"[cyan]ℹ️  {message}[/cyan]\n")
