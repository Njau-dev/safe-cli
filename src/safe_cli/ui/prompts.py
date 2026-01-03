"""
Interactive prompts for user decisions.
"""

from enum import Enum

from rich.console import Console
from rich.prompt import Confirm
import questionary

from safe_cli.core.analyzer import AnalysisResult
from safe_cli.utils.constants import DangerLevel


class PromptResponse(Enum):
    """User response to safety prompt."""

    ABORT = "abort"
    CONTINUE = "continue"
    VIEW_ALTERNATIVE = "view_alternative"
    USE_ALTERNATIVE = "use_alternative"


class UserPrompt:
    """Handles interactive user prompts."""

    def __init__(self, console: Console) -> None:
        """
        Initialize user prompt handler.
        
        Args:
            console: Rich console for output
        """
        self.console = console

    def _prompt_choice(self, question: str, choices: list[str], default: int = 0) -> str:
        """
        Prompt user with arrow key selection.
        
        Args:
            question: Question to ask
            choices: List of choices
            default: Default choice index
            
        Returns:
            Selected choice
        """
        return questionary.select(
            question,
            choices=choices,
            default=choices[default]
        ).ask()

    def confirm_execution(
        self, result: AnalysisResult, skip_prompt: bool = False
    ) -> PromptResponse:
        """
        Prompt user to confirm command execution.
        
        Args:
            result: Analysis result
            skip_prompt: Skip prompt if True (--yes flag)
            
        Returns:
            User's response
        """
        # If --yes flag, auto-continue
        if skip_prompt:
            return PromptResponse.CONTINUE

        # Safe commands don't need confirmation
        if result.is_safe:
            return PromptResponse.CONTINUE

        # Different prompt styles based on danger level
        if result.danger_level == DangerLevel.CRITICAL:
            return self._critical_prompt(result)
        elif result.danger_level == DangerLevel.HIGH:
            return self._high_prompt(result)
        elif result.danger_level == DangerLevel.MEDIUM:
            return self._medium_prompt(result)
        else:
            return PromptResponse.CONTINUE

    def _critical_prompt(self, result: AnalysisResult) -> PromptResponse:
        """
        Prompt for critical danger commands.
        Uses arrow key selection.
        """
        self.console.print(
            "\n[bold red]⚠️  CRITICAL DANGER - This action could cause severe damage![/bold red]"
        )

        if result.has_safe_alternatives:
            self.console.print(
                "[yellow]Consider using a safe alternative instead.[/yellow]"
            )

            choice = self._prompt_choice(
                "How would you like to proceed?",
                ["Abort", "View safe alternative", "Continue anyway"],
                default=0
            )

            if choice == "Abort":
                return PromptResponse.ABORT
            elif choice == "View safe alternative":
                return PromptResponse.VIEW_ALTERNATIVE
            else:  # Continue anyway
                return PromptResponse.CONTINUE
        else:
            choice = self._prompt_choice(
                "How would you like to proceed?",
                ["Abort", "Continue anyway"],
                default=0
            )

            if choice == "Abort":
                return PromptResponse.ABORT
            else:
                return PromptResponse.CONTINUE

    def _high_prompt(self, result: AnalysisResult) -> PromptResponse:
        """Prompt for high danger commands."""
        self.console.print(
            "\n[bold red]⚠️  HIGH RISK - Proceed with caution![/bold red]")

        if result.has_safe_alternatives:
            choice = self._prompt_choice(
                "How would you like to proceed?",
                ["Abort", "Continue anyway", "View safe alternative"],
                default=0
            )

            if choice == "Abort":
                return PromptResponse.ABORT
            elif choice == "View safe alternative":
                return PromptResponse.VIEW_ALTERNATIVE
            else:
                # Confirm once more
                if Confirm.ask("\n[yellow]Are you sure you want to continue?[/yellow]", default=False):
                    return PromptResponse.CONTINUE
                else:
                    return PromptResponse.ABORT
        else:
            if Confirm.ask("\n[yellow]Continue anyway?[/yellow]", default=False):
                return PromptResponse.CONTINUE
            else:
                return PromptResponse.ABORT

    def _medium_prompt(self, result: AnalysisResult) -> PromptResponse:
        """Prompt for medium danger commands."""
        if result.has_safe_alternatives:
            choice = self._prompt_choice(
                "[yellow]⚠️  How would you like to proceed?[/yellow]",
                ["Continue", "View safe alternative", "Abort"],
                default=0
            )

            if choice == "Abort":
                return PromptResponse.ABORT
            elif choice == "View safe alternative":
                return PromptResponse.VIEW_ALTERNATIVE
            else:
                return PromptResponse.CONTINUE
        else:
            if Confirm.ask("\n[yellow]Continue with execution?[/yellow]", default=True):
                return PromptResponse.CONTINUE
            else:
                return PromptResponse.ABORT

    def choose_alternative(self, alternatives: list[str]) -> tuple[bool, str | None]:
        """
        Let user choose from safe alternatives.
        
        Args:
            alternatives: List of safe alternative commands
            
        Returns:
            Tuple of (should_use_alternative, chosen_alternative)
        """
        choices = alternatives + ["Use original command", "Abort"]

        choice = self._prompt_choice(
            "[bold green]Available Safe Alternatives:[/bold green]",
            choices,
            default=0
        )

        if choice == "Abort":
            return False, None
        elif choice == "Use original command":
            return False, None
        else:
            return True, choice
