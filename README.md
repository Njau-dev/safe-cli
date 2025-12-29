# safe-cli

**Know before you run** - A safety wrapper for dangerous shell commands

## Overview

`safe` analyzes shell commands before execution, warns you about potential dangers, and helps you avoid costly mistakes.

Part of a developer safety ecosystem:
- `scaffold` → create projects safely
- `safe` → run commands safely
- `cleaner` → clean projects safely
- `uterm` → undo mistakes safely
- `envdoctor` → fix broken environments

## Features

- 🛡️ **Danger Detection**: Identifies risky command patterns before execution
- ⚠️ **Smart Warnings**: Context-aware risk assessment
- 🎯 **Interactive Prompts**: Beautiful CLI prompts powered by Rich
- 🔍 **Dry Run Mode**: See what would happen without executing
- 📚 **Educational**: Learn why commands are dangerous

## Installation

```bash
pip install safe-cli
```

Or with Poetry:

```bash
poetry add safe-cli
```

## Quick Start

```bash
# Analyze and run a command safely
safe rm -rf /tmp/test

# Dry run mode - see what would happen
safe --dry-run rm -rf /tmp/test

# Skip confirmations (useful for scripts)
safe --yes rm file.txt

# Get help
safe --help
```

## Examples

### Dangerous File Operations
```bash
$ safe rm -rf /
⚠️  CRITICAL DANGER DETECTED
This command will permanently delete files recursively from root directory.
→ Abort / Continue / View Safe Alternative?
```

### Git Operations
```bash
$ safe git reset --hard HEAD~5
⚠️  HIGH RISK OPERATION
This will permanently discard uncommitted changes and reset 5 commits.
→ Continue? (y/N)
```

### System Commands
```bash
$ safe sudo dd if=/dev/zero of=/dev/sda
⚠️  CRITICAL DANGER DETECTED
This will overwrite disk with root privileges - DATA LOSS IMMINENT
→ Abort / Continue / View Safe Alternative?
```

## Command Coverage (MVP v0.1.0)

- File operations: `rm`, `mv`, `cp`, `chmod`, `chown`
- System commands: `sudo`, `dd`, `kill`, `killall`
- Git operations: `git reset`, `git push --force`
- Docker operations: `docker system prune`, `docker rm`

## Development

```bash
# Clone the repository
git clone https://github.com/Njau-dev/safe-cli.git
cd safe-cli

# Install dependencies
poetry install

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Format code
poetry run black src tests

# Lint
poetry run ruff check src tests
```

## Architecture

```
safe-cli/
├── src/safe_cli/
│   ├── cli.py           # Entry point
│   ├── core/            # Core functionality
│   │   ├── parser.py    # Command parsing
│   │   ├── analyzer.py  # Risk analysis
│   │   └── executor.py  # Command execution
│   ├── rules/           # Risk detection rules
│   ├── ui/              # User interface
│   └── utils/           # Utilities
└── tests/               # Test suite
```

## Roadmap

- **v0.1.0** (Current): MVP with core safety features
- **v0.2.0**: Command history and pattern learning
- **v0.3.0**: Team-wide safety policies
- **v0.4.0**: Integration with UTerm, Cleaner, EnvDoctor
- **v0.5.0**: Advanced simulation and dry-run
- **v1.0.0**: Shell integration and plugin system

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Ecosystem

Part of the developer safety toolkit:
- [scaffold-cli](https://github.com/Njau-dev/scaffold-cli) - Project scaffolding
- [safe-cli](https://github.com/Njau-dev/safe-cli) - Command safety (you are here)
- Coming soon: `cleaner`, `uterm`, `envdoctor`

---

**Safety first, always.** 🛡️