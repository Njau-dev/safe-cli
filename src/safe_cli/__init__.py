"""
safe-cli: Know before you run

A safety wrapper for dangerous shell commands.
"""

__version__ = "0.1.0"
__author__ = "Jefferson Njau"
__license__ = "MIT"

from safe_cli.cli import app

__all__ = ["app", "__version__"]
