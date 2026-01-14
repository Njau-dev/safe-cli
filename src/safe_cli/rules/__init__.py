"""
Safety rules for command analysis.
"""

from safe_cli.rules.base import CompositeRule, Rule, RuleMatch
from safe_cli.rules.docker import (
    DockerRmiRule,
    DockerRmRule,
    DockerSystemPruneRule,
    DockerVolumePruneRule,
)
from safe_cli.rules.filesystem import (
    ChmodRule,
    ChownRule,
    CpRule,
    MvRule,
    RmRule,
)
from safe_cli.rules.git import (
    GitBranchDeleteRule,
    GitCleanRule,
    GitPushForceRule,
    GitResetRule,
)
from safe_cli.rules.system import (
    DdRule,
    KillRule,
    MkfsRule,
    ShutdownRule,
    SudoRule,
)

__all__ = [
    "Rule",
    "RuleMatch",
    "CompositeRule",
    # Filesystem
    "RmRule",
    "MvRule",
    "CpRule",
    "ChmodRule",
    "ChownRule",
    # Git
    "GitResetRule",
    "GitPushForceRule",
    "GitCleanRule",
    "GitBranchDeleteRule",
    # Docker
    "DockerSystemPruneRule",
    "DockerRmRule",
    "DockerRmiRule",
    "DockerVolumePruneRule",
    # System
    "SudoRule",
    "DdRule",
    "KillRule",
    "ShutdownRule",
    "MkfsRule",
]
