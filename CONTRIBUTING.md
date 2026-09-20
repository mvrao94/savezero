# Contributing to SaveZero

Thank you for your interest in contributing to SaveZero! This document provides guidelines for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce** the behavior
- **Expected vs actual behavior**
- **Screenshots or logs** if applicable
- **Environment details**: OS, Python version, Chrome version
- **SaveZero version** you're using

Use the bug report template when creating issues.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful** to most SaveZero users
- **List any alternative solutions** you've considered

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Add tests** if applicable
4. **Update documentation** if you're changing functionality
5. **Ensure tests pass** before submitting
6. **Write clear commit messages** describing your changes
7. **Submit a pull request** with a clear description of the changes

#### Pull Request Guidelines

- Keep pull requests focused on a single feature or bug fix
- Include tests for new functionality
- Update README.md if adding user-facing features
- Follow the existing code style and conventions
- Reference any related issues in your PR description

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Google Chrome
- Git

### Setting Up Your Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/savezero.git
cd savezero

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Running Tests

```bash
# Run tests (when available)
python -m pytest

# Run with coverage
python -m pytest --cov=savezero
```

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and reasonably sized
- Use meaningful variable and function names

### Testing Your Changes

Before submitting a PR:

1. Test on a small collection first (10-20 saved posts)
2. Verify both API and UI modes work
3. Check that error handling works correctly
4. Test the authentication flow
5. Verify the self-healing recovery mechanism

## Project Structure

```
savezero/
├── cleaner.py          # Main automation logic
├── config.py           # Configuration and selectors
├── run.bat            # Windows launcher
├── run.sh             # Unix launcher
├── requirements.txt   # Python dependencies
├── pyproject.toml    # Package configuration
└── README.md         # User documentation
```

## Commit Message Guidelines

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

Example:
```
Add support for multiple Instagram accounts

- Implement account switching logic
- Update configuration to support account list
- Add CLI flag for account selection

Fixes #123
```

## Documentation

- Update README.md for user-facing changes
- Add docstrings for new functions/classes
- Update CHANGELOG.md following [Keep a Changelog](https://keepachangelog.com/) format
- Include code comments for complex logic

## Questions?

Feel free to open an issue with the "question" label if you have questions about contributing.

## Recognition

Contributors will be recognized in the project README and release notes.

---

Thank you for contributing to SaveZero! 🚀
