# Contributing to CodeFox-CLI

Thank you for your interest in contributing. This document explains how to set up the project, run checks, and submit changes.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.

## How to Contribute

- **Bug reports and feature ideas** — open a [GitHub Issue](https://github.com/URLbug/CodeFox-CLI/issues). Describe the problem or proposal and your environment (OS, Python version, provider).
- **Security issues** — do not open a public issue. See [SECURITY.md](SECURITY.md) for responsible disclosure.
- **Code and docs** — open a Pull Request (see below).

## Development Setup

**Requirements:** Python 3.11+

1. Clone the repository:

   ```bash
   git clone https://github.com/URLbug/CodeFox-CLI.git
   cd CodeFox-CLI
   ```

2. Install in editable mode with dev dependencies:

   **pip:**
   ```bash
   pip install -e ".[dev]"
   ```

   **uv:**
   ```bash
   uv pip install -e ".[dev]"
   ```

3. Verify:

   ```bash
   codefox --command version
   ```

## Running Checks

Before submitting a PR, run the following from the project root.

**Tests:**
```bash
pytest tests -v --tb=short
```

**Lint (Ruff):**
```bash
ruff check codefox tests
ruff format codefox tests
```

**Type check (mypy):**
```bash
mypy codefox
```

**All at once (recommended):**
```bash
ruff check codefox tests && ruff format --check codefox tests && mypy codefox && pytest tests -v --tb=short
```

CI runs the same checks on push/PR; your branch should pass before merge.

## Pull Request Process

1. **Branch** — create a branch from `main` (or `dev`, if that’s the default). Use a short prefix, e.g. `fix/`, `feat/`, `docs/`.
2. **Changes** — keep the diff focused. One logical change per PR is easier to review.
3. **Tests** — add or update tests for bug fixes and new behavior.
4. **Docs** — update README, [WIKI.md](WIKI.md), or docstrings if you change behavior or config.
5. **Open PR** — describe what you changed and why. Link any related issues.
6. **Review** — address feedback. Once CI is green and a maintainer approves, your PR can be merged.

## Project Structure (quick reference)

| Path | Purpose |
|------|--------|
| `codefox/main.py` | CLI entry point (Typer) |
| `codefox/cli_manager.py` | Command routing (init, scan, list, version) |
| `codefox/scan.py` | Scan workflow (diff → upload → model → output) |
| `codefox/init.py` | Init workflow (API key, .codefoxignore, .codefox.yml) |
| `codefox/api/base_api.py` | Abstract base for providers |
| `codefox/api/*.py` | Provider implementations (Gemini, Ollama, OpenRouter) |
| `codefox/api/model_enum.py` | Provider registry |
| `codefox/prompts/` | System prompts and template |
| `codefox/utils/` | Helpers (YAML, git diff, RAG, etc.) |
| `tests/` | Pytest tests |

Adding a new provider: implement `BaseAPI` in `codefox/api/`, register in `ModelEnum`, and add a default model name. See existing providers for patterns.

## Code Style

- **Formatting:** Ruff (line length 79). Run `ruff format codefox tests` before committing.
- **Linting:** Ruff rules E, F, I, N, W, UP. No new warnings in `codefox` or `tests`.
- **Types:** mypy with the options in `pyproject.toml`. Type hints encouraged for new code.
- **Tests:** Pytest. Use `tests/conftest.py` fixtures where useful. Avoid `S101` in tests (assert with plain strings allowed).

## Questions

- **Usage and config** — see [README.md](README.md) and [WIKI.md](WIKI.md).
- **Bugs and features** — open an [Issue](https://github.com/URLbug/CodeFox-CLI/issues).

Thanks for contributing.
