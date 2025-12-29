# Contributing to safe-cli

Thank you for your interest in contributing to safe-cli! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)
- Git

### Setup Steps

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/safe-cli.git
   cd safe-cli
   ```

2. **Install dependencies**
   ```bash
   poetry install
   ```

3. **Activate the virtual environment**
   ```bash
   poetry shell
   ```

4. **Run tests to verify setup**
   ```bash
   pytest
   ```

## Development Workflow

### Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing

Format your code before committing:
```bash
# Format code
poetry run black src tests

# Lint code
poetry run ruff check src tests

# Type check
poetry run mypy src
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/test_parser.py

# Run specific test
poetry run pytest tests/test_parser.py::TestCommandParser::test_simple_command

# Run with verbose output
poetry run pytest -v
```

### Project Structure

```
safe-cli/
├── src/safe_cli/         # Source code
│   ├── cli.py           # CLI entry point
│   ├── core/            # Core functionality
│   ├── rules/           # Safety rules (Day 2+)
│   ├── ui/              # User interface (Day 4+)
│   └── utils/           # Utilities
├── tests/               # Test suite
├── pyproject.toml       # Project configuration
└── README.md
```

## Making Changes

### Branch Naming

- Feature: `feature/description`
- Bug fix: `fix/description`
- Documentation: `docs/description`

Example:
```bash
git checkout -b feature/add-docker-rules
```

### Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Detailed description (if needed)

- Change 1
- Change 2
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test changes
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Maintenance tasks

Example:
```
feat(rules): add docker system prune detection

- Detects docker system prune commands
- Warns about potential data loss
- Suggests safer alternatives
```

## Adding New Features

### Adding a New Rule (Day 2+)

1. Create rule class in `src/safe_cli/rules/`
2. Implement `matches()` and `explain()` methods
3. Register rule in `RuleRegistry`
4. Add tests in `tests/test_rules.py`

Example:
```python
from safe_cli.rules.base import Rule

class DockerPruneRule(Rule):
    name = "docker_prune"
    danger_level = "high"
    
    def matches(self, parsed_command):
        return (
            parsed_command.command == "docker" 
            and "prune" in parsed_command.args
        )
    
    def explain(self):
        return "This will remove unused Docker resources"
```

### Adding Tests

- Every new feature must have tests
- Aim for >80% test coverage
- Test both happy path and edge cases

Example:
```python
def test_docker_prune_detection():
    parser = CommandParser()
    rule = DockerPruneRule()
    
    cmd = parser.parse("docker system prune")
    assert rule.matches(cmd)
```

## Pull Request Process

1. **Ensure tests pass**
   ```bash
   pytest
   ```

2. **Format and lint code**
   ```bash
   black src tests
   ruff check src tests
   ```

3. **Update documentation** if needed

4. **Create pull request** with:
   - Clear title describing the change
   - Description of what changed and why
   - Reference to any related issues

5. **Wait for review**
   - Address feedback promptly
   - Keep discussions focused and professional

## Code Review Guidelines

### For Reviewers

- Be constructive and specific
- Suggest improvements, don't just criticize
- Approve when code meets standards

### For Contributors

- Respond to feedback professionally
- Ask questions if feedback is unclear
- Make requested changes promptly

## Reporting Issues

### Bug Reports

Include:
- Python version
- safe-cli version
- Command that caused the issue
- Expected behavior
- Actual behavior
- Error messages (if any)

Example:
```
**Environment:**
- Python: 3.11.5
- safe-cli: 0.1.0
- OS: macOS 14.0

**Command:**
safe rm -rf /tmp

**Expected:**
Should show warning and prompt

**Actual:**
Crashes with error: ...

**Error:**
[paste error message]
```

### Feature Requests

Include:
- Clear description of the feature
- Use cases
- Why it would be valuable
- Suggested implementation (optional)

## Development Principles

### Safety First
- Never execute commands without user confirmation
- Err on the side of caution
- Provide clear warnings

### User Experience
- Keep interfaces simple and intuitive
- Use clear, helpful error messages
- Provide educational feedback

### Code Quality
- Write clean, readable code
- Follow DRY principles
- Comment complex logic
- Type hint everything

### Testing
- Test edge cases
- Mock external dependencies
- Keep tests fast and focused

## Questions?

- Open an issue for questions
- Start discussions in GitHub Discussions
- Check existing issues before creating new ones

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to safe-cli! 🛡️