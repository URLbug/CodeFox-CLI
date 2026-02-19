
<p align="center">
  <img src="assets/logo.png" alt="CodeFox logo" width="120" />
</p>

<h1 align="center">CodeFox-CLI</h1>
<p align="center">
    Intelligent automated code review system
</p>

---

## 🦊 Overview

**CodeFox-CLI** is an intelligent automated code review system that takes over routine security and code quality checks, allowing senior developers to focus on architecture and complex tasks.

Unlike traditional linters, CodeFox understands the context of the entire project and its business logic, delivering not just review comments but ready-to-apply fixes with **Auto-Fix**.

---

## 📥 Installation

Choose the installation method that fits your workflow.

### 🔹 Install dependencies (local setup)

```bash
pip install -r requirements.txt
```
### 🔹 Development mode (editable install)

Provides the local codefox CLI command and enables live code changes.

```bash
python3 -m pip install -e .
```

### 🔹 Install from GitHub

🐍 Using pip

```bash
python3 -m pip install git+https://github.com/URLbug/CodeFox-CLI.git@main
```

⚡ Using uv (recommended for CLI usage)
```bash
uv tool install git+https://github.com/URLbug/CodeFox-CLI.git@main
```

---

✅ Verify installation
```bash
codefox --command version
```
Or
```bash
python3 -m codefox --command version
```

## 🚀 Quick Start

### Initialize (stores your API key)

```bash
codefox --command init
```

### Run a scan (uses the current git diff)

```bash
codefox --command scan
```

### Show version

```bash
codefox --command version
```

---

## ⚙️ Configuration

**Ignore file:** `./.codefoxignore`
Specifies paths that should not be uploaded to the File Store.

**Model settings:** `./.codefox.yml`
Used for fine-grained configuration of the analysis behavior and model parameters (such as model selection, temperature, review rules, baseline, and prompts).
For detailed configuration options and examples, see [wiki](WIKI.md).

**Token configuration:** `./codefoxenv`
Stores the API token for the model. This file is used by the CLI for authentication and should not be committed to version control.

---

## 🧩 Commands

| Command   | Description                                                                                          |
| --------- | ---------------------------------------------------------------------------------------------------- |
| `init`    | Saves the Gemini API key locally and creates a `.codefoxignore` and `.codefox.yml` file in the current directory.       |
| `scan`    | Collects changes from the `git diff`, uploads files to the File Store, and sends requests to Gemini. |
| `version` | Displays the current CodeFox CLI version.                                                            |
| `--help`  | Shows available flags and usage information.                                                         |

---

## 🧪 Examples

### Run a scan in a project

```bash
codefox --command scan
```

---

## 🛠 Development

Install with dev dependencies:

```bash
pip install -e ".[dev]"
# or: uv pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests -v
```

Lint and format:

```bash
ruff check codefox tests
ruff format codefox tests
```

Static type check:

```bash
mypy codefox
```

---

## 🤝 Contributing

Bug reports, pull requests, and documentation improvements are welcome.
