CodeFox-CLI
===========

Overview
------------
CodeFox-CLI is an intelligent automated code review system that takes over routine security and code quality checks, allowing senior developers to focus on architecture and complex tasks.
Unlike traditional linters, CodeFox understands the context of the entire project and the business logic, providing not just comments but ready-to-apply fixes (Auto-Fix).

Installation
------------
Install dependencies locally
pip install -r requirements.txt

Install in development mode (provides local codefox command)
python3 -m pip install -e .

Install directly from the repository
python3 -m pip install git+https://github.com/URLbug/CodeFox-CLI.git

Quick Start
------------
Initialize (stores your API key)
python -m codefox --command init

Run a scan (uses the current git diff)
python -m codefox --command scan

Show version
python -m codefox --command version

Configuration
------------
Ignore file: ./.codefoxignore
Specifies paths that should not be uploaded to the File Store.

Commands
------------
init - saves the Gemini API key locally and creates a .codefoxignore file in the current directory.ы
scan - collects changes from the git diff, uploads files to the File Store, and sends requests to Gemini.
version - displays the current CodeFox CLI version.
--help - shows available flags and usage information.

Examples
------------
Run a scan in a project
python -m codefox --command scan

Install locally and use the codefox command
python -m pip install -e .
codefox --command version

Contributing
------------
Bug reports, pull requests, and documentation improvements are welcome.
