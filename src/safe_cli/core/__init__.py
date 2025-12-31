"""
Core functionality for safe-cli.
"""

from safe_cli.core.analyzer import AnalysisResult, CommandAnalyzer
from safe_cli.core.parser import CommandParser, ParsedCommand
from safe_cli.core.suggestion import SafeAlternativeGenerator

__all__ = [
    "CommandParser",
    "ParsedCommand",
    "CommandAnalyzer",
    "AnalysisResult",
    "SafeAlternativeGenerator",
]
